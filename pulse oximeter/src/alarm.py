"""
alarm.py  –  Alarm checker with audio beep alerts.

Beep behaviour:
  • Rising-edge beep: plays only when an alarm is newly triggered.
  • Persistent-alarm repeat: critical alarms (low SpO2, shock, sensor/finger
    loss) beep on every update tick so they cannot be silently ignored.
  • Mute: pass muted=True to suppress all audio (UI mute button).

Platform support:
  • Windows  → winsound.Beep (no extra dependencies)
  • Linux/Mac → pyaudio if installed, otherwise terminal bell (\a)
"""

import sys
import math
import struct
import threading


# ─────────────────────────────────────────────────────────────
# Low-level beep helpers
# ─────────────────────────────────────────────────────────────

def _do_beep(frequency: int, duration_ms: int):
    """Synchronously play a beep tone."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.Beep(int(frequency), int(duration_ms))
        else:
            try:
                import pyaudio
                pa = pyaudio.PyAudio()
                stream = pa.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True
                )
                n = int(44100 * duration_ms / 1000)
                samples = [
                    int(32767 * math.sin(2 * math.pi * frequency * i / 44100))
                    for i in range(n)
                ]
                stream.write(struct.pack('<' + 'h' * n, *samples))
                stream.stop_stream()
                stream.close()
                pa.terminate()
            except Exception:
                print('\a', end='', flush=True)   # terminal bell fallback
    except Exception:
        print('\a', end='', flush=True)


def _play_profile(freq, dur_ms, count):
    """Play a beep profile (frequency, duration, repeat count) synchronously."""
    import time
    for i in range(count):
        _do_beep(freq, dur_ms)
        if i < count - 1:
            time.sleep(0.08)   # gap between repeats


def _beep_async(freq, dur_ms, count):
    """Launch beep playback in a background daemon thread."""
    threading.Thread(
        target=_play_profile,
        args=(freq, dur_ms, count),
        daemon=True
    ).start()


# ─────────────────────────────────────────────────────────────
# Beep profiles  (frequency_hz, duration_ms, repeat_count)
# ─────────────────────────────────────────────────────────────
# Higher frequency = more urgent sound.
BEEP_PROFILES = {
    "SHOCK":           (960, 120, 4),   # rapid quad-beep – most critical
    "LOW SPO2":        (880, 150, 3),   # triple high beep – hypoxia
    "HIGH PULSE":      (800, 200, 2),   # double – tachycardia
    "LOW PULSE":       (700, 200, 2),   # double – bradycardia
    "HIGH TEMP":       (620, 300, 2),   # double mid – fever
    "LOW TEMP":        (520, 300, 2),   # double low – hypothermia
    "CHECK SENSOR":    (440, 450, 1),   # single long – sensor off
    "FINGER REMOVED":  (440, 450, 1),   # single long – finger off
    "MOTION DETECTED": (360, 250, 2),   # double soft – motion artefact
}

# Alarms that keep beeping every update tick while they remain active
PERSISTENT_ALARMS = {
    "SHOCK",
    "LOW SPO2",
    "CHECK SENSOR",
    "FINGER REMOVED",
}


# ─────────────────────────────────────────────────────────────
# Alarm class
# ─────────────────────────────────────────────────────────────

class Alarm:

    def __init__(self):
        self._previous_alarms: set = set()
        self.muted: bool = False   # can be set directly by UI

    def check(self, data: dict, muted: bool = False) -> list:
        """
        Evaluate patient data, trigger beeps, and return list of alarm strings.

        Parameters
        ----------
        data   : dict returned by PulseOximeter.read()
        muted  : if True, suppress all audio (overrides self.muted)
        """
        silence = muted or self.muted

        alarms = []

        # ── Sensor / device alarms ──────────────────────────────────
        if not data["sensor_connected"]:
            alarms.append("CHECK SENSOR")

        if not data["finger_present"]:
            alarms.append("FINGER REMOVED")

        if data["motion"]:
            alarms.append("MOTION DETECTED")

        # ── Clinical alarms (only when readings are valid) ──────────
        if data["spo2"] != "--":

            spo2 = data["spo2"]
            hr   = data["heart_rate"]
            temp = data["temperature"]

            if spo2 < 90:
                alarms.append("LOW SPO2")       # Hypoxia

            if hr < 40:
                alarms.append("LOW PULSE")

            if hr > 140:
                alarms.append("HIGH PULSE")

            if temp > 39:
                alarms.append("HIGH TEMP")      # Fever

            if temp < 35:
                alarms.append("LOW TEMP")       # Hypothermia

            # Shock: low SpO2 + tachycardia + low temperature
            if spo2 < 90 and hr > 110 and temp < 36:
                alarms.append("SHOCK")

        # ── Beep logic ───────────────────────────────────────────────
        if not silence:
            current = set(alarms)
            new_alarms = current - self._previous_alarms

            # Beep for every newly triggered alarm
            for name in new_alarms:
                if name in BEEP_PROFILES:
                    _beep_async(*BEEP_PROFILES[name])

            # Persistent alarms beep on every tick while still active
            for name in current & PERSISTENT_ALARMS:
                if name not in new_alarms:    # already active
                    if name in BEEP_PROFILES:
                        _beep_async(*BEEP_PROFILES[name])

        self._previous_alarms = set(alarms)
        return alarms
