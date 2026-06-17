from models.patient import Patient
from models.pressure_monitor import PressureMonitor
from models.filter import Filter

from visualization.realtime_graphs import RealtimeGraphs

import time


patient = Patient()

pressure = PressureMonitor()

filter_obj = Filter()

graphs = RealtimeGraphs()

step = 0

while True:

    patient.update_vitals()

    pressure.update()

    filter_obj.update()

    graphs.update(
        step,
        patient,
        pressure,
        filter_obj
    )

    step += 1

    time.sleep(1)