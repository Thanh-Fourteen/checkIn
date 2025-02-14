import os
import sys
from PyQt6.QtWidgets import QApplication
from screens.main_screen import MainScreen
from screens.welcome_screen import WelcomeScreen

if __name__ == "__main__":
    folder = os.getcwd()
    csv_path = os.path.join(folder,"data", "top100.csv")
    app = QApplication(sys.argv)

    main_screen = MainScreen(folder=folder)
    welcome_screen = WelcomeScreen(folder=folder, csv_path=csv_path)

    main_screen.welcome_screen = welcome_screen 
    main_screen.welcome_screen.signal_no_match_found.connect(main_screen.update_text)

    main_screen.showMaximized()
    welcome_screen.show() 

    app.exec()