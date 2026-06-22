from enum import Enum


class AlarmType(Enum):

    HIGH_PRESSURE = "High Pressure"

    LOW_BATTERY = "Low Battery"

    AIR_IN_LINE = "Air In Line"

    DOOR_OPEN = "Door Open"

    OCCLUSION = "Occlusion"

    INFUSION_COMPLETE = "Infusion Complete"