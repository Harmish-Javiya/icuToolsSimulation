# import sqlite3


# class DatabaseManager:

#     def __init__(self):

#         self.conn = sqlite3.connect(
#             "pump.db"
#         )

#         self.cursor = self.conn.cursor()

#         self.create_tables()

#     def create_tables(self):

#         self.cursor.execute("""
#         CREATE TABLE IF NOT EXISTS event_logs(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             event TEXT
#         )
#         """)

#         self.cursor.execute("""
#         CREATE TABLE IF NOT EXISTS alarms(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             alarm TEXT
#         )
#         """)

#         self.conn.commit()

#     def insert_event(
#             self,
#             timestamp,
#             event):

#         self.cursor.execute(
#             """
#             INSERT INTO event_logs
#             (timestamp, event)
#             VALUES (?, ?)
#             """,
#             (timestamp, event)
#         )

#         self.conn.commit()

#     def insert_alarm(
#             self,
#             timestamp,
#             alarm):

#         self.cursor.execute(
#             """
#             INSERT INTO alarms
#             (timestamp, alarm)
#             VALUES (?, ?)
#             """,
#             (timestamp, alarm)
#         )

#         self.conn.commit()