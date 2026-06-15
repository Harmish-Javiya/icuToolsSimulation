from enum import Enum


class Mode(Enum):
    MANUAL = "Manual"
    AED = "AED"
    SYNC = "Sync"
    PACING = "Pacing"


class DeviceState(Enum):
    IDLE = "Idle"
    CHARGING = "Charging"
    READY = "Ready"
    SHOCK_DELIVERED = "Shock Delivered"
    DISARMED = "Disarmed"


class Defibrillator:

    ENERGY_LEVELS = [
        50,
        100,
        150,
        200,
        300,
        360
    ]

    def __init__(self):

        self.mode = Mode.MANUAL

        self.state = DeviceState.IDLE

        self.energy = 200

        self.battery = 100

        self.sync = False

        self.pacing = False

        self.shocks = 0

    ############################

    def set_mode(self, mode):

        self.mode = mode

    ############################

    def set_energy(self, energy):

        if energy in self.ENERGY_LEVELS:

            self.energy = energy

    ############################

    def charge(self):

        if self.battery <= 5:

            return False

        self.state = DeviceState.CHARGING

        return True

    ############################

    def ready(self):

        if self.state == DeviceState.CHARGING:

            self.state = DeviceState.READY

    ############################

    def shock(self):

        if self.state != DeviceState.READY:

            return False

        self.state = DeviceState.SHOCK_DELIVERED

        self.shocks += 1

        self.battery -= 1

        if self.battery < 0:

            self.battery = 0

        return True

    ############################

    def disarm(self):

        self.state = DeviceState.DISARMED

    ############################

    def recharge(self):

        self.battery = 100

    ############################

    def toggle_sync(self):

        self.sync = not self.sync

    ############################

    def toggle_pacing(self):

        self.pacing = not self.pacing

    ############################

    def status(self):

        return {

            "mode": self.mode.value,

            "state": self.state.value,

            "energy": self.energy,

            "battery": self.battery,

            "sync": self.sync,

            "pacing": self.pacing,

            "shocks": self.shocks

        }