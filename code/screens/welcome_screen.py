from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi
from PyQt6 import QtCore
import os

class WelcomeScreen(QMainWindow):
    def __init__(self, folder, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        ui_path = os.path.join(folder, "UI", 'back.ui')
        loadUi(ui_path, self)
        
        self.backButton.clicked.connect(self.goBack)
        self.TEXT = self.findChild(QtCore.QObject, "TEXT")
        self.TEXT.setReadOnly(True)
        self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def update_text(self, name, acc):
        # self.TEXT.setText(f"Welcome, {name} (Accuracy: {acc:.2f})!")
        self.TEXT.setText(f"Have a productive day, {name}!")
    
    def goBack(self):
        pass
        # self.parent().setCurrentIndex(0)