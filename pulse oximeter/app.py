import sys
from pathlib import Path

# ==========================================
# 1. CRITICAL PATH INJECTION
# This MUST happen before any local imports!
# ==========================================
# __file__       -> app.py
# .parent        -> pulse oximeter folder
# .parent.parent -> ICU_Tools_Simulation (Root)
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ==========================================
# 2. STANDARD IMPORTS
# Now Python knows to look in the Root folder!
# ==========================================
from PySide6.QtWidgets import QApplication
from ui.mainWindow_v2 import MainWindow

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())