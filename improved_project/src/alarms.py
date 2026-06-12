from enum import Enum


class AlarmLevel(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlarmSystem:

    def __init__(self):

        self.message = "SYSTEM READY"
        self.level = AlarmLevel.NORMAL

    #################################

    def evaluate(self, device, patient):

        self.message = "SYSTEM READY"
        self.level = AlarmLevel.NORMAL

        # Battery

        if device.battery <= 10:

            self.message = "LOW BATTERY"
            self.level = AlarmLevel.WARNING

        # Device State

        if device.state.value == "Charging":

            self.message = "CHARGING"
            self.level = AlarmLevel.WARNING

        if device.state.value == "Ready":

            self.message = "READY TO SHOCK"
            self.level = AlarmLevel.WARNING

        # Patient Rhythm

        rhythm = patient.rhythm.value

        if rhythm == "Ventricular Fibrillation":

            self.message = "VF DETECTED"
            self.level = AlarmLevel.CRITICAL

        elif rhythm == "Ventricular Tachycardia":

            self.message = "VT DETECTED"
            self.level = AlarmLevel.CRITICAL

        elif rhythm == "Asystole":

            self.message = "ASYSTOLE"
            self.level = AlarmLevel.CRITICAL

    #################################

    def get_alarm(self):

        return self.message

    #################################

    def get_level(self):

        return self.level.value

    #################################

    def status(self):

        return {

            "alarm": self.message,

            "level": self.level.value

        }