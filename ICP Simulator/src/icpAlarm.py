class ICPAlarmSystem:
    def __init__(self):
        self.alarms = []

    def evaluate(self, current_icp: float, simulated_hr: float) -> list:
        self.alarms.clear()

        if current_icp >= 20.0:
            self.alarms.append("CRITICAL: HIGH ICP (BRAIN SWELLING)")
        elif current_icp >= 15.0:
            self.alarms.append("WARNING: ELEVATED ICP")

        if current_icp >= 20.0 and simulated_hr <= 50.0:
            self.alarms.append("EMERGENCY: CUSHING'S TRIAD DETECTED")

        return self.alarms