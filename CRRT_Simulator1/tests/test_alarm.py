from models.patient import Patient
from models.pressure_monitor import PressureMonitor
from models.filter import Filter
from database.database import Database

from engines.alarm_engine import AlarmEngine


patient = Patient()

pressure = PressureMonitor()

db = Database()

filter_obj = Filter()

alarm_engine = AlarmEngine()


# Force abnormal conditions

patient.potassium = 7.5

patient.spo2 = 88

patient.bp_sys = 85

pressure.tmp = 300

filter_obj.health = 15


alarms = alarm_engine.check(
    patient,
    pressure,
    filter_obj
)
db.save_patient(patient)
print("\nACTIVE ALARMS\n")

for alarm in alarms:
    print(alarm)

for alarm in alarms:
    db.save_alarm(alarm)