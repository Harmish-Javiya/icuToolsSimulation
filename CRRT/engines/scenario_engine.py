class ScenarioEngine:

    def apply(self, patient, scenario):

        if scenario == "Healthy":

            patient.bun = 20
            patient.creatinine = 1.0
            patient.potassium = 4.0
            patient.sodium = 140
            patient.hemoglobin = 12.0

        elif scenario == "AKI":

            patient.bun = 120
            patient.creatinine = 8.0
            patient.potassium = 6.8
            patient.sodium = 136
            patient.hemoglobin = 10.5

        elif scenario == "Hyperkalemia":

            patient.potassium = 7.5
            patient.sodium = 138

        elif scenario == "FluidOverload":

            patient.fluid_overload = 10
            patient.sodium = 134