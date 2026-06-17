from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_hardware_engine import UnifiedHardwareEngine


class HardwareInterface(UnifiedHardwareEngine):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("device_name", "Hemodynamics")
        super().__init__(*args, **kwargs)
