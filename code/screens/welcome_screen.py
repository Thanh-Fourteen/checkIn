from PyQt6.QtWidgets import QDockWidget, QMainWindow
from PyQt6.uic import loadUi
from PyQt6 import QtCore
import os

class WelcomeScreen(QMainWindow):
    def __init__(self, folder, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        ui_path = os.path.join(folder, "UI", 'back.ui')
        loadUi(ui_path, self)
        
        self.backButton.clicked.connect(self.goBack)
        self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def update_text(self, name, acc):
        # self.TEXT.setText(f"Welcome, {name} (Accuracy: {acc:.2f})!")
        self.TEXT.setText(f"{name}, your presence is highly valued.")
    
    def goBack(self):
        self.parent().setCurrentIndex(0)