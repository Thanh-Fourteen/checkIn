import cv2
import os
import threading
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtWidgets import QDialog, QInputDialog
from PyQt6.uic import loadUi
from detection import faceDetection
from tasks.warmup_task import WarmupTask
from threads.recognition_thread import ThreadClass

class MainScreen(QDialog):
    signal_update_buttons = QtCore.pyqtSignal(bool)
    
    def __init__(self, folder, parent=None, skip_frame_first=30, frame_skip=30, threshold=0.5):
        super(MainScreen, self).__init__(parent)
        ui_path = os.path.join(folder,"UI", 'form.ui')
        loadUi(ui_path, self)
        self.folder = folder
        self.detect = faceDetection(self.folder)

        self.SHOW.clicked.connect(self.onClicked)
        self.TEXT.setText('Findly Press')
        self.Break.clicked.connect(self.breakClicked)
        self.warmup.clicked.connect(self.WarmUp)
        self.inputButton.clicked.connect(self.getInputName)

        self.cap = None
        self.thread_pool = QThreadPool()
        self.signal_update_buttons.connect(self.update_buttons)
        self.warmup_active = False
        
        self.running = True
        self.mutex = threading.Lock()
        self.thread = ThreadClass(self.folder, self.detect, self.mutex, parent, skip_frame_first, frame_skip, threshold)

        self.thread.signal_update_text.connect(self.update_text)
        self.thread.signal_update_button.connect(self.update_button_state)
        self.thread.signal_recognized.connect(self.onRecognized)
        self.predicting = False
        self.WarmUp()

    def WarmUp(self):
        if not self.warmup_active:
            self.signal_update_buttons.emit(False)
            self.TEXT.setText("Warming up...")
            self.warmup_active = True

            def warmup_finished():
                self.signal_update_buttons.emit(True)
                self.TEXT.setText("Warmup complete!")
                self.warmup_active = False

            warmup_task = WarmupTask(self.detect)
            warmup_task.signals.finished.connect(warmup_finished)  # Kết nối tín hiệu finished với khe cắm warmup_finished
            self.thread_pool.start(warmup_task)
         

    @pyqtSlot()
    def onClicked(self):
        if not self.predicting:
            print("Button show click!")
            self.TEXT.setText("Camera starting...")
            self.warmup.setEnabled(False)
            self.SHOW.setEnabled(False)
            self.inputButton.setEnabled(False)
            self.cap = cv2.VideoCapture(0)

            # Tạo và kết nối luồng xử lý nhận diện
            self.thread.cap = self.cap
            self.thread.signal_update_text.connect(self.update_text)
            self.thread.start()

            # Bắt đầu vòng lặp hiển thị camera trong luồng chính
            while (self.cap != None):
                ret, frame = self.cap.read()
                frame = cv2.flip(frame, 1)

                if not ret:
                    break
                self.displayImage(frame)
                cv2.waitKey(1)


    def breakClicked(self):
        if not self.predicting:
            self.TEXT.setText("Don't Click any button!")
            if self.cap != None:
                self.thread.running = False
                self.thread.wait() # Đợi luồng kết thúc

                self.cap.release()
                cv2.destroyAllWindows()
            self.TEXT.setText("Camera stopped")
            self.cap = None
            self.warmup.setEnabled(True)
            self.inputButton.setEnabled(True)
            self.SHOW.setEnabled(True)
            self.predicting = False

            # Tạo QPixmap trắng trơn
            white_pixmap = QPixmap(self.imgLabel.size())
            white_pixmap.fill(QColor("white"))

            # Đặt QPixmap trắng vào imgLabel
            self.imgLabel.setPixmap(white_pixmap)

    def update_button_state(self, enabled):
        self.Break.setEnabled(enabled)
        self.predicting = not enabled

    @pyqtSlot(bool)
    def update_buttons(self, enabled):
        self.SHOW.setEnabled(enabled)
        self.Break.setEnabled(enabled)

    def update_text(self, text):
        self.TEXT.setText(text)
    
    def displayImage(self, img):
        qformat = QImage.Format.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format.Format_RGB888
            else:
                qformat = QImage.Format.Format_RGB888
        
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def onRecognized(self, name, acc):
        self.predicting = False
        self.breakClicked() 
        self.stacked_widget.setCurrentIndex(1)  
        self.welcome_screen.update_text(name, acc) 
    
    def getInputName(self):
        name, ok = QInputDialog.getText(self, "Nhập tên", "Nhập tên:")
        if ok and name:
            self.goToWelcomeScreen(name)

    def goToWelcomeScreen(self, name):
        self.stacked_widget.setCurrentIndex(1)
        self.welcome_screen.update_text(name, 100)
    
    def closeEvent(self, event):
        if self.predicting or self.warmup_active:
            # Nếu predict_name đang chạy, chặn sự kiện đóng và thông báo cho người dùng
            event.ignore()
            self.TEXT.setText("Chương trình đang xử lý, hãy thử lại sau...")
        else:
            # Nếu predict_name đã hoàn thành, cho phép đóng ứng dụng
            self.breakClicked()
            event.accept()