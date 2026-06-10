import logging

logger = logging.getLogger(__name__)

class CardiacAlarmSystem:
    """Evaluates heart rate and rhythm to trigger clinical alarms."""

    def __init__(self):
        self.limits = {
            "high_hr": 130.0,
            "low_hr": 45.0,
            "asystole_time": 4.0  # Seconds without a heartbeat before alarming
        }
        self.active_alarms = set()
        self.flatline_timer = 0.0

    def evaluate(self, dt: float, current_hr: float, rhythm_status: str) -> list:
        current_alarms = set()

        # 1. Heart Rate Thresholds
        if current_hr >= self.limits["high_hr"]:
            current_alarms.add("HIGH HR (TACHYCARDIA)")
        elif 0 < current_hr <= self.limits["low_hr"]:
            current_alarms.add("LOW HR (BRADYCARDIA)")

        # 2. Asystole (Flatline) Detection
        if rhythm_status == "ASYSTOLE":
            self.flatline_timer += dt
        else:
            self.flatline_timer = 0.0

        if self.flatline_timer >= self.limits["asystole_time"]:
            current_alarms.add("ASYSTOLE (CARDIAC ARREST)")

        # Logging changes
        new_alarms = current_alarms - self.active_alarms
        resolved_alarms = self.active_alarms - current_alarms

        for alarm in new_alarms:
            logger.error(f"CARDIAC ALARM: {alarm} !!!")
        for alarm in resolved_alarms:
            logger.info(f"Cardiac Alarm Cleared: {alarm}")

        self.active_alarms = current_alarms
        return list(self.active_alarms)