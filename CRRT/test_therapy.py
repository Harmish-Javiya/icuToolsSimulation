from models.patient import Patient

from engines.therapy_engine import TherapyEngine

import time


patient = Patient()

therapy = TherapyEngine()

therapy.start_therapy()

for i in range(20):

    therapy.update(patient)

    print(
        f"BUN={patient.bun:.2f} "
        f"Creatinine={patient.creatinine:.2f} "
        f"K={patient.potassium:.2f}"
    )

    time.sleep(1)