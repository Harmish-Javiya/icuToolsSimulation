class TherapyEngine:
    """
    Manages active therapies. Each therapy has a dose counter that
    decays over time, producing a visible, sustained effect on vitals.

    Dose scaling:
      - Each button press adds one "unit" of dose.
      - Per-tick effect is proportional to remaining dose.
      - Dose decays each tick so the effect tapers off naturally.
    """

    # How much effect is applied per unit of dose per tick
    FLUID_SBP   = 2.0
    FLUID_DBP   = 1.2
    FLUID_CVP   = 0.8
    FLUID_DECAY = 0.04   # dose drains over ~25 ticks per unit (~1.25 s)

    BLOOD_SBP   = 1.8
    BLOOD_DBP   = 1.0
    BLOOD_SV    = 0.8
    BLOOD_DECAY = 0.04

    NORAD_SBP   = 3.0
    NORAD_DBP   = 2.0
    NORAD_DECAY = 0.02   # slower decay — drug infusion lingers longer

    def __init__(self):

        self.fluid = 0.0
        self.blood = 0.0
        self.norad = 0.0
        self.cpr   = False

    # ------------------------------------------------------------------
    # Dose administration — each press adds one bolus/dose unit
    # ------------------------------------------------------------------

    def give_fluid(self):
        self.fluid += 1.0

    def give_blood(self):
        self.blood += 1.0

    def start_norad(self):
        self.norad += 1.0

    def start_cpr(self):
        self.cpr = True

    def stop_cpr(self):
        self.cpr = False

    # ------------------------------------------------------------------
    # Apply effects each tick — called from app.py before patient.update()
    # ------------------------------------------------------------------

    def apply(self, patient):

        if self.fluid > 0:
            # Proportional effect — stronger at peak dose, tapers off
            factor = min(self.fluid, 1.0)
            patient.sbp += self.FLUID_SBP * factor
            patient.dbp += self.FLUID_DBP * factor
            patient.cvp += self.FLUID_CVP * factor
            self.fluid = max(0.0, self.fluid - self.FLUID_DECAY)

        if self.blood > 0:
            factor = min(self.blood, 1.0)
            patient.sbp += self.BLOOD_SBP * factor
            patient.dbp += self.BLOOD_DBP * factor
            patient.sv  += self.BLOOD_SV  * factor
            self.blood = max(0.0, self.blood - self.BLOOD_DECAY)

        if self.norad > 0:
            factor = min(self.norad, 1.0)
            patient.sbp += self.NORAD_SBP * factor
            patient.dbp += self.NORAD_DBP * factor
            self.norad = max(0.0, self.norad - self.NORAD_DECAY)

        if self.cpr and patient.currentScenario == "Arrest":
            # CPR mechanically pumps — sets vitals directly each tick
            patient.hr  = 40
            patient.sbp = 60
            patient.dbp = 30

    # ------------------------------------------------------------------
    # Status — passed to UI so buttons can show active state
    # ------------------------------------------------------------------

    def status(self):
        return {
            "fluid": round(self.fluid, 2),
            "blood": round(self.blood, 2),
            "norad": round(self.norad, 2),
            "cpr":   self.cpr,
        }
