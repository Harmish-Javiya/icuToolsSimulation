from __future__ import annotations

from datetime import datetime

try:
    import winsound
except ImportError:  # pragma: no cover - platform fallback
    winsound = None


class AlarmEngine:

    def __init__(self):

        self.history = []
        self._active_keys = set()

    def evaluate(self, patient, pressure, filter_model):

        checks = [
            ("HIGH_K", patient.potassium > 6.0, "HIGH POTASSIUM", "HIGH", f"K {patient.potassium:.1f} mmol/L"),
            ("LOW_SPO2", patient.spo2 < 92, "LOW SpO2", "HIGH", f"SpO2 {patient.spo2:.0f}%"),
            ("HIGH_TEMP", patient.temperature > 38.2, "HIGH TEMPERATURE", "MEDIUM", f"Temp {patient.temperature:.1f} C"),
            ("LOW_BP", patient.bp_sys < 90 or patient.bp_dia < 55, "LOW BLOOD PRESSURE", "HIGH", f"BP {int(patient.bp_sys)}/{int(patient.bp_dia)}"),
            ("HIGH_TMP", pressure.tmp > 250, "HIGH TMP", "HIGH", f"TMP {pressure.tmp:.0f} mmHg"),
            ("FILTER_CLOT", filter_model.health < 20, "FILTER CLOTTING", "CRITICAL", f"Health {filter_model.health:.0f}%"),
        ]

        alarms = []
        new_active = set()

        for key, active, label, priority, details in checks:
            if active:
                new_active.add(key)
                if key not in self._active_keys:
                    alarm = {
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "priority": priority,
                        "label": label,
                        "details": details,
                        "message": f"{label} | {details}",
                    }
                    self.history.append(alarm)
                    self.history = self.history[-300:]
                    alarms.append(alarm)

        if new_active and winsound is not None:
            try:
                winsound.Beep(880, 120)
            except RuntimeError:
                pass

        self._active_keys = new_active
        return alarms
