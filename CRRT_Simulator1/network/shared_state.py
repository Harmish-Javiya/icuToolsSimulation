import threading
from datetime import datetime


def _default_state():

    return {
        "heart_rate": 0,
        "blood_pressure": "0/0",
        "spo2": 0,
        "temperature": 0,
        "respiratory_rate": 0,
        "bun": 0,
        "creatinine": 0,
        "potassium": 0,
        "sodium": 0,
        "hemoglobin": 0,
        "pressure": {
            "access": 0,
            "return": 0,
            "filter": 0,
            "tmp": 0,
            "pressure_drop": 0,
            "clotting_risk": 0,
        },
        "filter": {
            "health": 0,
            "status": "Unknown",
            "pressure_drop": 0,
            "clotting_risk": 0,
        },
        "fluid_balance": 0,
        "fluid_intake": 0,
        "fluid_output": 0,
        "therapy_mode": "Unknown",
        "blood_flow_rate": 0,
        "dialysate_flow_rate": 0,
        "ultrafiltration_rate": 0,
        "machine_status": "Stopped",
        "alarms": [],
        "events": [],
        "simulation_step": 0,
        "updated_at": "",
        "samples": [],
    }


state_lock = threading.Lock()


simulator_data = _default_state()


def get_simulator_state():
    with state_lock:
        return {
            **simulator_data,
            "pressure": dict(simulator_data.get("pressure", {})),
            "filter": dict(simulator_data.get("filter", {})),
            "alarms": list(simulator_data.get("alarms", [])),
            "events": list(simulator_data.get("events", [])),
            "samples": list(simulator_data.get("samples", [])),
        }


def sync_from_snapshot(snapshot):

    with state_lock:
        simulator_data.update(snapshot)


def update_from_simulation(
    patient,
    machine,
    pressure,
    filter_obj,
    fluid,
    alarms,
    step=0,
):
    sync_from_snapshot(
        {
            "heart_rate": patient.hr,
            "blood_pressure": f"{patient.bp_sys}/{patient.bp_dia}",
            "spo2": patient.spo2,
            "temperature": patient.temperature,
            "respiratory_rate": getattr(patient, "respiratory_rate", 0),
            "bun": round(patient.bun, 2),
            "creatinine": round(patient.creatinine, 2),
            "potassium": round(patient.potassium, 2),
            "sodium": round(getattr(patient, "sodium", 0), 2),
            "hemoglobin": round(getattr(patient, "hemoglobin", 0), 2),
            "pressure": {
                "access": pressure.access_pressure,
                "return": pressure.return_pressure,
                "filter": pressure.filter_pressure,
                "tmp": pressure.tmp,
                "pressure_drop": getattr(pressure, "pressure_drop", pressure.filter_pressure - pressure.return_pressure),
                "clotting_risk": getattr(pressure, "clotting_risk", 0),
            },
            "filter": {
                "health": round(filter_obj.health, 2),
                "status": filter_obj.status,
                "pressure_drop": getattr(filter_obj, "pressure_drop", 0),
                "clotting_risk": getattr(filter_obj, "clotting_risk", 0),
            },
            "fluid_balance": round(fluid.get_net_balance(), 2),
            "fluid_intake": round(fluid.intake, 2),
            "fluid_output": round(fluid.output, 2),
            "therapy_mode": machine.mode,
            "blood_flow_rate": machine.blood_flow_rate,
            "dialysate_flow_rate": machine.dialysate_flow_rate,
            "ultrafiltration_rate": machine.ultrafiltration_rate,
            "machine_status": "Running" if machine.running else "Stopped",
            "alarms": list(alarms),
            "simulation_step": step,
            "updated_at": datetime.now().strftime("%H:%M:%S"),
        }
    )