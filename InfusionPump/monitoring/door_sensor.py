class DoorSensor:

    def __init__(self):
        self.is_open = False

    def open_door(self):
        self.is_open = True

    def close_door(self):
        self.is_open = False