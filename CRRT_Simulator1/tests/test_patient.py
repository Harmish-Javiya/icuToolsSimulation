from models.patient import Patient

patient = Patient()

print("Initial Values")
print(patient.get_patient_data())

print("\nUpdating Vitals...\n")

for _ in range(5):

    patient.update_vitals()

    print(patient.get_patient_data())