from models.patient import Patient
from engines.scenario_engine import ScenarioEngine

patient = Patient()

scenario = ScenarioEngine()

print("Before Scenario")
print(patient.get_patient_data())

scenario.apply(patient, "Hyperkalemia")

print("\nAfter Hyperkalemia Scenario")
print(patient.get_patient_data())