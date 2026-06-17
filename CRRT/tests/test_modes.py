from models.patient import Patient
from models.fluid_balance import FluidBalance
from engines.therapy_engine import TherapyEngine

import time

# Create objects
patient = Patient()
fluid = FluidBalance()
therapy = TherapyEngine()

# Select therapy mode
therapy.set_mode("CVVHDF")

# Start therapy
therapy.start_therapy()

print("\nCRRT Mode Test Started\n")

for i in range(20):

    therapy.update(patient, fluid)

    print(
        f"Step {i+1} | "
        f"Mode={therapy.mode} | "
        f"BUN={patient.bun:.2f} | "
        f"Creatinine={patient.creatinine:.2f} | "
        f"Potassium={patient.potassium:.2f} | "
        f"Net Fluid={fluid.get_net_balance():.2f}"
    )
    
    time.sleep(1)

print("\nTest Complete")