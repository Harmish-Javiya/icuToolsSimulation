# test_crosstalk.py
from core.central_patient_engine import CentralPatientEngine
from ECG.src.ecgEngine import ECGEngine
from Ventilator.src.patientEngine import PatientEngine

# 1. Initialize both engines in the SAME process
vent = PatientEngine("Adult")
ecg = ECGEngine()

print(f"START -> SpO2: {vent.spo2}% | HR: {ecg.current_hr} bpm")

# 2. Trigger lung failure in the Ventilator
vent.apply_intervention("ards")

# 3. Step forward in time by 30 seconds
for _ in range(300):
    # Ventilator physics run (drops SpO2, writes to Central Engine)
    vent.update_physics(applied_flow=0.5, dt=0.1, ventilator_peep=5.0)

    # ECG physics run (reads Central Engine SpO2, adjusts HR)
    ecg.step(dt=0.1, active_leads=["Lead II"])

print(f"END   -> SpO2: {vent.spo2:.1f}% | HR: {ecg.current_hr:.1f} bpm")