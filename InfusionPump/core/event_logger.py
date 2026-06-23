from datetime import datetime

# from database import db_manager


class EventLogger:

    def __init__(self, db=None):
        self.logs = []
        self.db = db

    def add_event(self, message):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        log = f"{timestamp} - {message}"

        self.logs.append(log)

        print(log)

        # if self.db:
        #     self.db.insert_event(timestamp, message)

    def get_logs(self):
        return self.logs
    