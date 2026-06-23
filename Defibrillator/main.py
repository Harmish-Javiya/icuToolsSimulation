import sys
import argparse
from pathlib import Path

# ==========================================
# 1. CRITICAL PATH INJECTION
# This MUST happen before any local imports!
# ==========================================
# __file__       -> main.py
# .parent        -> Defibrillator folder
# .parent.parent -> ICU_Tools_Simulation (Root)
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ==========================================
# 2. STANDARD IMPORTS
# ==========================================
# FIX: Import the helper function 'run_app' instead of the raw class
from ui import run_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the defibrillator simulator UI and API")
    parser.add_argument("--port", type=int, default=8000, help="Port for the simulator HTTP API")
    args = parser.parse_args()

    # FIX: Run the helper function which creates the Tkinter root window!
    run_app(port=args.port)