from __future__ import annotations

import threading
import time

from database.database import Database
from engines.scenario_engine import ScenarioEngine
from hardware import HardwareInterface
from models.crrt_machine import CRRTMachine
from models.fluid_balance import FluidBalance
from network.shared_state import get_simulator_state
from simulation.alarm_engine import AlarmEngine
from simulation.filter_model import FilterModel
from simulation.patient_model import PatientModel
from simulation.pressure_model import PressureModel
from core.state_manager import StateManager
from ui.dashboard import MedicalDashboard

# --- IMPORT THE CENTRAL SERVER CLIENT ---
from core.central_patient_engine import CentralPatientEngine


class SimulatorController:

    def __init__(self):
        self.state_manager = StateManager()
        self.patient = PatientModel()
        self.machine = CRRTMachine()
        self.pressure = PressureModel()
        self.filter_model = FilterModel()
        self.fluid = FluidBalance()
        self.scenario = ScenarioEngine()
        self.alarm_engine = AlarmEngine()
        self.hardware = HardwareInterface(
            mode="Ethernet UDP",
            serial_port="/tmp/ttyV7",
            ip="127.0.0.1",
            net_port=8000
        )
        self.db = Database()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.step = 0

        self.scenario.apply(self.patient, "AKI")
        self.state_manager.append_event("AKI scenario loaded")
        self.start_machine()
        self.publish_snapshot([])

    def start_machine(self):
        with self.lock:
            if self.machine.running:
                return
            self.machine.start()
            self.state_manager.append_event("CRRT machine started")
            self.publish_snapshot([])

    def update_parameter(self, name, value):
        with self.lock:
            if hasattr(self.patient, name):
                setattr(self.patient, name, float(value))
                self.patient.clamp()
                self.state_manager.append_event(f"Updated patient {name} to {float(value):g}")
                return

            if hasattr(self.machine, name):
                setattr(self.machine, name, float(value) if name != "mode" else value)
                self.state_manager.append_event(f"Updated machine {name} to {value}")
                return

            if hasattr(self.fluid, name):
                setattr(self.fluid, name, float(value))
                self.state_manager.append_event(f"Updated fluid {name} to {float(value):g}")
                return

    def replace_filter(self):
        with self.lock:
            self.filter_model.replace_filter()
            self.state_manager.append_event("Filter replaced successfully")

    def set_hardware_mode(self, mode):
        with self.lock:
            self.hardware.configure(mode=mode)
            self.state_manager.append_event(f"Telemetry output set to {mode}")

    def _build_snapshot(self, alarms):
        # --- THIN PAYLOAD ---
        # Note: **self.patient.get_snapshot() is removed to save bandwidth.
        # The Aggregator gets those global vitals from the Central Server instead!
        return {
            "device_id": "CRRT-RENAL-01",
            "pressure": self.pressure.get_snapshot(),
            "filter": self.filter_model.get_snapshot(),
            "fluid_balance": round(self.fluid.get_net_balance(), 2),
            "fluid_intake": round(self.fluid.intake, 2),
            "fluid_output": round(self.fluid.output, 2),
            "therapy_mode": self.machine.mode,
            "blood_flow_rate": self.machine.blood_flow_rate,
            "dialysate_flow_rate": self.machine.dialysate_flow_rate,
            "ultrafiltration_rate": self.machine.ultrafiltration_rate,
            "machine_status": "Running" if self.machine.running else "Stopped",
            "alarms": alarms,
            "simulation_step": self.step,
        }

    def publish_snapshot(self, alarms):
        snapshot = self._build_snapshot(alarms)
        # We merge patient vitals *only* for the local UI Dashboard (state_manager)
        local_ui_snapshot = {**snapshot, **self.patient.get_snapshot()}

        self.state_manager.update_snapshot(local_ui_snapshot)
        self.hardware.send_data(snapshot)  # Send the Thin Payload over UDP

        self.state_manager.append_sample(
            {
                "step": self.step,
                "heart_rate": self.patient.hr,
                "tmp": self.pressure.tmp,
                "potassium": self.patient.potassium,
                "filter_health": self.filter_model.health,
                "fluid_balance": self.fluid.get_net_balance(),
            }
        )
        return snapshot

    def loop(self):
        # 1. Initialize the network client
        net_engine = CentralPatientEngine()

        while not self.stop_event.is_set():
            with self.lock:
                # ==========================================
                # PHASE 1: LISTEN TO GLOBAL SERVER
                # ==========================================
                global_hr = net_engine.get("hr")
                global_spo2 = net_engine.get("spo2")
                global_bp_sys = net_engine.get("bp_sys")
                global_bp_dia = net_engine.get("bp_dia")
                global_rr = net_engine.get("rr")
                global_temp = net_engine.get("temperature")

                # Apply network truth to local patient model
                if global_hr is not None: self.patient.hr = float(global_hr)
                if global_spo2 is not None: self.patient.spo2 = float(global_spo2)
                if global_bp_sys is not None: self.patient.bp_sys = float(global_bp_sys)
                if global_bp_dia is not None: self.patient.bp_dia = float(global_bp_dia)
                if global_rr is not None: self.patient.respiratory_rate = float(global_rr)
                if global_temp is not None: self.patient.temperature = float(global_temp)

                # ==========================================
                # PHASE 2: RUN INTERNAL RENAL PHYSICS
                # ==========================================
                self.patient.step(self.machine, self.fluid, self.pressure, self.filter_model)
                self.pressure.update(self.patient, self.machine, self.filter_model)
                self.filter_model.update(self.patient, self.pressure, self.machine)

                alarms = self.alarm_engine.evaluate(self.patient, self.pressure, self.filter_model)
                if alarms:
                    for alarm in alarms:
                        self.state_manager.append_event(alarm["message"], alarm["priority"])
                        self.db.save_alarm(alarm)

                self.publish_snapshot(alarms)
                self.db.save_patient(self.patient)
                self.step += 1

                # ==========================================
                # PHASE 3: BROADCAST TO GLOBAL SERVER
                # ==========================================
                # CRRT owns "fluid_balance", so we push the net balance back to the server
                net_balance = round(self.fluid.get_net_balance(), 2)
                net_engine.update(source="CRRT", vital="fluid_balance", value=net_balance)

            time.sleep(1)

        self.machine.stop()
        self.hardware.close()
        self.db.close()


def main():
    controller = SimulatorController()
    dashboard = MedicalDashboard(
        state_provider=get_simulator_state,
        on_control_change=controller.update_parameter,
        on_replace_filter=controller.replace_filter,
        on_start=controller.start_machine,
        on_hardware_change=controller.set_hardware_mode,
        on_close=controller.stop_event.set,
    )

    simulation_thread = threading.Thread(target=controller.loop, daemon=True)
    simulation_thread.start()

    try:
        dashboard.run()
    except KeyboardInterrupt:
        controller.stop_event.set()
    finally:
        controller.stop_event.set()
        simulation_thread.join(timeout=3)


if __name__ == "__main__":
    main()