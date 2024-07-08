import sys
from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'D:\FPT\AI\9.5 AI\Check In\Final1\UI\form.ui', self)

        self.pixmap = QPixmap(r"D:\FPT\AI\9.5 AI\Check In\Final1\UI\background.jpg")

        # Đặt hình nền với tỷ lệ khung hình được giữ nguyên
        self.set_background_image()

    def resizeEvent(self, event):
        # Cập nhật lại hình nền khi thay đổi kích thước cửa sổ
        self.set_background_image()
        super().resizeEvent(event)

    def set_background_image(self):
        # Tạo QPixmap mới với kích thước được điều chỉnh
        scaled_pixmap = self.pixmap.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
        )

        # Tạo QBrush từ QPixmap đã được điều chỉnh
        brush = QBrush(scaled_pixmap)
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())