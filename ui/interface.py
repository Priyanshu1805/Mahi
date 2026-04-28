from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import sys

class UIBridge(QObject):
    status_changed = pyqtSignal(str)

ui_bridge = UIBridge()

class IronManUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        ui_bridge.status_changed.connect(self.update_status)

    def initUI(self):
        self.setWindowTitle("MAHI AI HUD")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout()

        self.label = QLabel("MAHI ONLINE", self)
        self.label.setStyleSheet("color: #00ffff; font-size: 32px; font-weight: bold; font-family: 'Courier';")
        self.label.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("SYSTEM READY", self)
        self.status_label.setStyleSheet("color: #008888; font-size: 18px; font-family: 'Courier';")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        # Pulse animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(800)

    def animate(self):
        if "ONLINE" in self.label.text():
            self.label.setStyleSheet("color: #008888; font-size: 32px; font-weight: bold; font-family: 'Courier';")
            self.label.setText("SYSTEM ACTIVE")
        else:
            self.label.setStyleSheet("color: #00ffff; font-size: 32px; font-weight: bold; font-family: 'Courier';")
            self.label.setText("MAHI ONLINE")

    def update_status(self, text):
        self.status_label.setText(text.upper())
        if "LISTENING" in text.upper():
            self.status_label.setStyleSheet("color: #ff3333; font-size: 18px; font-family: 'Courier';")
        else:
            self.status_label.setStyleSheet("color: #008888; font-size: 18px; font-family: 'Courier';")

def start_ui():
    """
    Initializes and starts the PyQt5 application loop.
    """
    app = QApplication(sys.argv)
    window = IronManUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_ui()
