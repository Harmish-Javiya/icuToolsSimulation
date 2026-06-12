from models.pressure_monitor import PressureMonitor
import time

pressure = PressureMonitor()

for i in range(10):

    pressure.update()

    print("\nPressure Readings")

    print(
        pressure.get_pressure_data()
    )
    time.sleep(1)