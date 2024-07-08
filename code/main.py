import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from screens.main_screen import MainScreen
from screens.welcome_screen import WelcomeScreen

if __name__ == "__main__":
    folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
    app = QApplication(sys.argv)
    
    # Create stacked widget and add screens
    stacked_widget = QStackedWidget()
    main_screen = MainScreen(folder=folder)
    welcome_screen = WelcomeScreen(folder=folder)
    stacked_widget.addWidget(main_screen)
    stacked_widget.addWidget(welcome_screen)
    
    # stacked_widget.show()
    stacked_widget.showMaximized()
    # stacked_widget.showFullScreen()

    # Store stacked widget reference in main screen
    main_screen.stacked_widget = stacked_widget
    main_screen.welcome_screen = welcome_screen

    welcome_screen.setParent(stacked_widget)

    stacked_widget.closeEvent = main_screen.closeEvent  

    app.exec()
    # sys.exit(app.exec())