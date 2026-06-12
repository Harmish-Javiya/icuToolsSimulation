from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Callable, DefaultDict, List


class EventBus:

    def __init__(self):

        self._lock = Lock()
        self._listeners: DefaultDict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable):

        with self._lock:
            self._listeners[event_name].append(callback)

    def publish(self, event_name: str, payload=None):

        with self._lock:
            callbacks = list(self._listeners.get(event_name, []))

        for callback in callbacks:
            callback(payload)