from core.state_machine import PumpState
from alarms.alarm_types import AlarmType


class InfusionEngine:

    def __init__(self, controller):
        self.controller = controller

    def update(self, global_map=90.0):
        # 1. Flow Physics
        # Only add to the infused volume if the pump is actually running
        if self.controller.get_state() == PumpState.RUNNING:
            delta = self.controller.flow_rate / 3600
            self.controller.infused += delta

        # 2. Monitoring (Now influenced by global patient blood pressure)
        # We pass the global MAP down into the pressure monitor so line resistance reacts to the patient.
        pressure = self.controller.pressure_monitor.get_pressure(
            global_map=global_map,
            flow_rate=self.controller.flow_rate if self.controller.get_state() == PumpState.RUNNING else 0
        )
        battery = self.controller.battery_monitor.update()

        # 3. Alarms
        # Trigger standard hardware alarms based on the monitored state
        if pressure > 250:
            self.controller.alarm_manager.trigger_alarm(AlarmType.HIGH_PRESSURE)

        if battery < 20:
            self.controller.alarm_manager.trigger_alarm(AlarmType.LOW_BATTERY)

        # 4. Completion logic
        # Check if the target volume (VTBI) has been reached
        if (self.controller.infused >= self.controller.vtbi
                and not self.controller.completed):

            self.controller.completed = True
            self.controller.infused = self.controller.vtbi
            self.controller.logger.add_event("Infusion Complete")

            if self.controller.kvo_enabled:
                self.controller.enter_kvo()
            else:
                self.controller.state_machine.set_state(PumpState.COMPLETED)

        # 5. ---> BROADCAST TELEMETRY TO AGGREGATOR <---
        # This sends the "Thin Payload" JSON packet to your local network
        self.controller.publish_snapshot()