class AlarmManager:

    def __init__(self):

        self.active_alarms = []

    def trigger_alarm(self, alarm):

        if alarm not in self.active_alarms:

            self.active_alarms.append(
                alarm
            )

            print(
                f"ALARM: {alarm.value}"
            )

    def clear_alarm(self, alarm):

        if alarm in self.active_alarms:

            self.active_alarms.remove(
                alarm
            )

    def get_alarms(self):

        return self.active_alarms