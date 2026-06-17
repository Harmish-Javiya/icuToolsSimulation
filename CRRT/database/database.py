import sqlite3
import os
import threading


class Database:

    def __init__(self):

        os.makedirs("data", exist_ok=True)

        self.conn = sqlite3.connect(
            "data/crrt.db",
            check_same_thread=False,
        )

        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

        self.create_tables()

    def create_tables(self):

        with self.lock:
            self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp DATETIME
            DEFAULT CURRENT_TIMESTAMP,

            hr INTEGER,

            bp_sys INTEGER,

            bp_dia INTEGER,

            spo2 INTEGER,

            temperature REAL,

            bun REAL,

            creatinine REAL,

            potassium REAL
        )
        """)

            self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarm_logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp DATETIME
            DEFAULT CURRENT_TIMESTAMP,

            alarm TEXT
        )
        """)

            self.conn.commit()

    def save_patient(self, patient):

        with self.lock:
            self.cursor.execute("""
        INSERT INTO patient_logs(

            hr,
            bp_sys,
            bp_dia,
            spo2,
            temperature,
            bun,
            creatinine,
            potassium

        )

        VALUES(?,?,?,?,?,?,?,?)
        """,
        (
            patient.hr,
            patient.bp_sys,
            patient.bp_dia,
            patient.spo2,
            patient.temperature,
            patient.bun,
            patient.creatinine,
            patient.potassium
        ))

            self.conn.commit()

    def save_alarm(self, alarm):

        if isinstance(alarm, dict):
            alarm = alarm.get("message", str(alarm))

        with self.lock:
            self.cursor.execute("""
        INSERT INTO alarm_logs(alarm)

        VALUES(?)
        """, (alarm,))

            self.conn.commit()

    def close(self):

        with self.lock:
            self.conn.close()