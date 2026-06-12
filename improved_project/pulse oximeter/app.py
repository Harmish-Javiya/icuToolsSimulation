import sys
from PySide6.QtWidgets import QApplication
from ui.mainWindow_v2 import MainWindow

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())