from enum import Enum


class PumpState(Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPED = "Stopped"
    COMPLETED = "Completed"


class StateMachine:

    def __init__(self):
        self.state = PumpState.IDLE

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state