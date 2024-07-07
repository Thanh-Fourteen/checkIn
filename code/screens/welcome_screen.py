from PyQt6.QtWidgets import QDockWidget
from PyQt6.uic import loadUi
import os

class WelcomeScreen(QDockWidget):
    def __init__(self, folder, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        ui_path = os.path.join(folder, "UI", 'welcome.ui')
        loadUi(ui_path, self)
        
        self.backButton.clicked.connect(self.goBack)

    def update_text(self, name, acc):
        self.TEXT.setText(f"Welcome, {name} (Accuracy: {acc:.2f})!")
    
    def goBack(self):
        self.parent().setCurrentIndex(0)