from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
import sys

class SScreenWindow:
    def __init__(self, title='SScreen App', width=800, height=600, bg='#fff', icon_path=None):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        self.window.resize(width, height)
        self.window.setStyleSheet(f'background-color: {bg};')
        if icon_path:
            self.window.setWindowIcon(QIcon(icon_path))
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())
