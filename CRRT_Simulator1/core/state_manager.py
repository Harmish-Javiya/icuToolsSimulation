from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from threading import Lock

from network import shared_state


class StateManager:

    def __init__(self):

        self._lock = Lock()
        self._state = {
            "patient": {},
            "pressure": {},
            "filter": {},
            "fluid": {},
            "machine": {},
            "alarms": [],
            "events": [],
            "waveforms": {
                "ecg_phase": 0.0,
                "resp_phase": 0.0,
                "pleth_phase": 0.0,
            },
            "samples": [],
            "updated_at": datetime.now().strftime("%H:%M:%S"),
        }

    def update_snapshot(self, snapshot):

        with self._lock:
            self._state.update(snapshot)
            self._state["updated_at"] = datetime.now().strftime("%H:%M:%S")
            state_copy = deepcopy(self._state)

        shared_state.sync_from_snapshot(state_copy)
        return state_copy

    def get_snapshot(self):

        with self._lock:
            return deepcopy(self._state)

    def append_event(self, message, level="INFO"):

        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
        }

        with self._lock:
            events = self._state.setdefault("events", [])
            events.append(entry)
            self._state["events"] = events[-300:]
            snapshot = deepcopy(self._state)

        shared_state.sync_from_snapshot(snapshot)
        return entry

    def append_sample(self, sample):

        with self._lock:
            samples = self._state.setdefault("samples", [])
            samples.append(sample)
            self._state["samples"] = samples[-300:]
            snapshot = deepcopy(self._state)

        shared_state.sync_from_snapshot(snapshot)
        return snapshot