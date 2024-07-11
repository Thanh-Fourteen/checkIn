# import cv2
# import os
# import threading
# from PyQt6 import QtCore, QtGui
# from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool, QRectF
# from PyQt6.QtGui import QImage, QPixmap, QColor, QPixmap, QPainter, QPainterPath
# from PyQt6.QtWidgets import QDialog, QInputDialog, QMainWindow
# from PyQt6.uic import loadUi
# from detection import faceDetection
# from tasks.warmup_task import WarmupTask
# from threads.recognition_thread import ThreadClass
# from threads.registration_thread import RegistrationThread

# class MainScreen(QMainWindow):
#     signal_update_buttons = QtCore.pyqtSignal(bool)
#     def __init__(self, folder, parent=None, skip_frame_first=30, frame_skip=30, threshold=0.5):
#         super(MainScreen, self).__init__(parent)
#         ui_path = os.path.join(folder,"UI", 'form.ui')
#         loadUi(ui_path, self)
#         self.folder = folder
#         self.detect = faceDetection(self.folder)

#         # self.label.setGeometry(0, 0, self.width(), self.height())

#         self.SHOW.clicked.connect(self.onClicked)
#         self.TEXT.setReadOnly(True)
#         self.TEXT.setText('Ready')
#         self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
#         self.Break.clicked.connect(self.breakClicked)
#         self.warmup.clicked.connect(self.WarmUp)
#         self.inputButton.clicked.connect(self.getInputName)
#         self.signin.clicked.connect(self.onSignInClicked)

#         self.cap = None
#         self.thread_pool = QThreadPool()
#         self.signal_update_buttons.connect(self.update_buttons)
#         self.warmup_active = False
#         self.original_pixmap = self.imgLabel.pixmap()
        
#         self.running = True
#         self.mutex = threading.Lock()
#         self.thread = ThreadClass(self.folder, self.detect, self.mutex, parent, skip_frame_first, frame_skip, threshold)

#         self.registration_thread = None
#         self.thread.signal_update_text.connect(self.update_text)
#         self.thread.signal_update_button.connect(self.update_button_state)
#         self.thread.signal_recognized.connect(self.onRecognized)
#         self.predicting = False
#         # self.WarmUp()

#     def WarmUp(self):
#         if not self.warmup_active:
#             self.signal_update_buttons.emit(False)
#             self.TEXT.setText("Warming up...")
#             self.warmup_active = True

#             def warmup_finished():
#                 self.signal_update_buttons.emit(True)
#                 self.TEXT.setText("Warmup complete!")
#                 self.warmup_active = False

#             warmup_task = WarmupTask(self.detect)
#             warmup_task.signals.finished.connect(warmup_finished)  # Kết nối tín hiệu finished với khe cắm warmup_finished
#             self.thread_pool.start(warmup_task)
         

#     @pyqtSlot()
#     def onClicked(self):
#         if not self.predicting:
#             print("Button show click!")
#             self.TEXT.setText("Camera starting...")
#             self.warmup.setEnabled(False)
#             self.SHOW.setEnabled(False)
#             self.inputButton.setEnabled(False)
#             self.signin.setEnabled(False)
#             self.cap = cv2.VideoCapture(0)

#             # Tạo và kết nối luồng xử lý nhận diện
#             self.thread.cap = self.cap
#             self.thread.signal_update_text.connect(self.update_text)
#             self.thread.start()

#             # Bắt đầu vòng lặp hiển thị camera trong luồng chính
#             while (self.cap != None):
#                 ret, frame = self.cap.read()
#                 frame = cv2.flip(frame, 1)

#                 if not ret:
#                     break
#                 self.displayImage(frame)
#                 cv2.waitKey(1)


#     def breakClicked(self):
#         if not self.predicting:
#             self.TEXT.setText("Don't Click any button!")
#             if self.cap != None:
#                 self.thread.running = False
#                 self.thread.wait() # Đợi luồng kết thúc

#                 self.cap.release()
#                 cv2.destroyAllWindows()
#             self.TEXT.setText("Camera stopped")
#             self.cap = None
#             self.warmup.setEnabled(True)
#             self.inputButton.setEnabled(True)
#             self.SHOW.setEnabled(True)
#             self.signin.setEnabled(True)
#             self.predicting = False

#             self.imgLabel.setPixmap(self.original_pixmap)

#     # def onSignInClicked(self):
#     #     try:
#     #         self.TEXT.setText("Capturing images...")
#     #         for frame in self.detect.register():  # Lặp qua từng frame từ camera
#     #             self.displayImage(frame)         # Hiển thị frame bằng displayImage
#     #             cv2.waitKey(1) 

#     #         self.TEXT.setText("Enter name:") 
#     #         person_name, ok = QInputDialog.getText(self, "Registration", "Enter the name of the person:")
#     #         if ok and person_name:
#     #             self.detect.process_registration(self.detect.captured_images, person_name)  # Xử lý ảnh và lưu vào database
#     #             self.TEXT.setText("Registration completed!")
#     #         else:
#     #             self.TEXT.setText("Tên không hợp lệ")

#     #     except Exception as e:
#     #         self.TEXT.append(f"Đã xảy ra lỗi: {e}")
            
#     #     self.imgLabel.setPixmap(self.original_pixmap)
#     def onSignInClicked(self):
#         if not self.predicting:
#             # Nhập tên trước khi mở camera
#             self.toggle_buttons(False)
#             person_name, ok = QInputDialog.getText(self, "Registration", "Enter the name of the person:")
#             if not ok or not person_name:
#                 self.TEXT.setText("Tên không hợp lệ")
#                 self.toggle_buttons(True)
#                 return

#             self.TEXT.setText("Starting registration...")
#             # self.warmup.setEnabled(False)
#             # self.SHOW.setEnabled(False)
#             # self.inputButton.setEnabled(False)
#             # self.signin.setEnabled(False)
#             self.cap = cv2.VideoCapture(0)

#             if not self.cap.isOpened():
#                 self.TEXT.setText("Error: Could not open camera.")
#                 self.toggle_buttons(True)
#                 return

#             # Truyền tên người dùng cho RegistrationThread
#             self.registration_thread = RegistrationThread(folder=self.folder, detect=self.detect, cap=self.cap, person_name=person_name)
#             self.registration_thread.signal_update_text.connect(self.update_text)
#             self.registration_thread.signal_registration_finished.connect(self.onRegistrationFinished)
#             self.registration_thread.start()

#             # Bắt đầu vòng lặp hiển thị camera trong luồng chính
#             while (self.cap != None):
#                 ret, frame = self.cap.read()
#                 frame = cv2.flip(frame, 1)

#                 if not ret:
#                     break
#                 self.displayImage(frame)
#                 cv2.waitKey(1)

#     def get_person_name(self):
#         """Hiển thị QInputDialog và gửi tên trở lại thread đăng ký."""
#         person_name, ok = QInputDialog.getText(self, "Registration", "Enter the name of the person:")
#         if ok:
#             self.registration_thread.set_person_name(person_name)
#         else:
#             print("Error") 

#     def onRegistrationFinished(self):
#         self.cap.release()
#         self.cap = None
#         self.TEXT.setText("Registration completed!")
#         self.toggle_buttons(True)
#         # self.warmup.setEnabled(True)
#         # self.SHOW.setEnabled(True)
#         # self.inputButton.setEnabled(True)
#         # self.signin.setEnabled(True)

#         self.imgLabel.setPixmap(self.original_pixmap)

#     def toggle_buttons(self, enabled):
#         """Hàm để bật/tắt các nút."""
#         self.warmup.setEnabled(enabled)
#         self.SHOW.setEnabled(enabled)
#         self.Break.setEnabled(enabled)
#         self.inputButton.setEnabled(enabled)
#         self.signin.setEnabled(enabled)

#     def update_button_state(self, enabled):
#         self.Break.setEnabled(enabled)
#         self.predicting = not enabled

#     @pyqtSlot(bool)
#     def update_buttons(self, enabled):
#         self.SHOW.setEnabled(enabled)
#         self.Break.setEnabled(enabled)
#         self.inputButton.setEnabled(enabled) 
#         self.warmup.setEnabled(enabled)

#     def update_text(self, text):
#         self.TEXT.setText(text)
import cv2
import os
import threading
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool, QRectF
from PyQt6.QtGui import QImage, QPixmap, QColor, QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import QDialog, QInputDialog, QMainWindow
from PyQt6.uic import loadUi
from detection import faceDetection
from tasks.warmup_task import WarmupTask
from threads.recognition_thread import ThreadClass
from threads.registration_thread import RegistrationThread

class MainScreen(QMainWindow):
    signal_update_buttons = QtCore.pyqtSignal(bool)
    def __init__(self, folder, parent=None, skip_frame_first=30, frame_skip=30, threshold=0.5):
        super(MainScreen, self).__init__(parent)
        ui_path = os.path.join(folder,"UI", 'form.ui')
        loadUi(ui_path, self)
        self.folder = folder
        self.detect = faceDetection(self.folder)

        self.SHOW.clicked.connect(self.onClicked)
        self.TEXT.setReadOnly(True)
        self.TEXT.setText('Ready')
        self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.Break.clicked.connect(self.breakClicked)
        self.warmup.clicked.connect(self.WarmUp)
        self.inputButton.clicked.connect(self.getInputName)
        self.signin.clicked.connect(self.onSignInClicked)

        self.cap = None
        self.thread_pool = QThreadPool()
        self.signal_update_buttons.connect(self.update_buttons)

        # Biến trạng thái
        self.warmup_active = False
        self.showing_camera = False 
        self.registering = False 

        self.original_pixmap = self.imgLabel.pixmap()
        
        self.running = True
        self.mutex = threading.Lock()
        self.thread = ThreadClass(self.folder, self.detect, self.mutex, parent, skip_frame_first, frame_skip, threshold)

        self.registration_thread = None
        self.thread.signal_update_text.connect(self.update_text)
        self.thread.signal_update_button.connect(self.update_button_state)
        self.thread.signal_recognized.connect(self.onRecognized)
        self.predicting = False

    def WarmUp(self):
        if not self.warmup_active and not self.showing_camera and not self.registering:
            self.toggle_buttons(False)
            self.TEXT.setText("Warming up...")
            self.warmup_active = True

            def warmup_finished():
                self.TEXT.setText("Warmup complete!")
                self.warmup_active = False
                self.toggle_buttons(True)

            warmup_task = WarmupTask(self.detect)
            warmup_task.signals.finished.connect(warmup_finished) 
            self.thread_pool.start(warmup_task)

    @pyqtSlot()
    def onClicked(self):
        if not self.showing_camera and not self.warmup_active and not self.registering:
            self.TEXT.setText("Camera starting...")
            self.toggle_buttons(False)
            self.showing_camera = True
            self.cap = cv2.VideoCapture(0)

            self.thread.cap = self.cap
            self.thread.signal_update_text.connect(self.update_text)
            self.thread.start()

            while self.cap is not None:
                ret, frame = self.cap.read()
                frame = cv2.flip(frame, 1)

                if not ret:
                    break
                self.displayImage(frame)
                cv2.waitKey(1)

    def breakClicked(self):
        if self.showing_camera:
            self.TEXT.setText("Don't Click any button!")
            self.thread.running = False
            self.thread.wait()

            self.cap.release()
            cv2.destroyAllWindows()
            self.TEXT.setText("Camera stopped")
            self.cap = None
            self.showing_camera = False
            self.predicting = False
            self.toggle_buttons(True)
            self.imgLabel.setPixmap(self.original_pixmap)

    def onSignInClicked(self):
        if not self.registering and not self.warmup_active and not self.showing_camera:
            self.toggle_buttons(False)
            person_name, ok = QInputDialog.getText(self, "Registration", "Enter the name of the person:")
            if not ok or not person_name:
                self.TEXT.setText("Tên không hợp lệ")
                self.toggle_buttons(True)
                return

            self.TEXT.setText("Starting registration...")
            self.registering = True 
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.TEXT.setText("Error: Could not open camera.")
                self.toggle_buttons(True)
                self.registering = False 
                return

            self.registration_thread = RegistrationThread(folder=self.folder, detect=self.detect, cap=self.cap, person_name=person_name)
            self.registration_thread.signal_update_text.connect(self.update_text)
            self.registration_thread.signal_registration_finished.connect(self.onRegistrationFinished)
            self.registration_thread.start()

            while self.cap is not None:
                ret, frame = self.cap.read()
                frame = cv2.flip(frame, 1)

                if not ret:
                    break
                self.displayImage(frame)
                cv2.waitKey(1)

    def onRegistrationFinished(self):
        self.cap.release()
        self.cap = None
        self.TEXT.setText("Registration completed!")
        self.registering = False
        self.toggle_buttons(True)
        self.imgLabel.setPixmap(self.original_pixmap)

    def toggle_buttons(self, enabled):
        self.warmup.setEnabled(enabled and not self.warmup_active)
        self.SHOW.setEnabled(enabled and not self.showing_camera)
        self.inputButton.setEnabled(enabled)
        self.signin.setEnabled(enabled and not self.registering)
        self.Break.setEnabled(self.showing_camera or self.registering)

    def update_button_state(self, enabled):
        self.Break.setEnabled(enabled)
        self.predicting = not enabled

    @pyqtSlot(bool)
    def update_buttons(self, enabled):
        self.SHOW.setEnabled(enabled)
        self.Break.setEnabled(enabled)
        self.inputButton.setEnabled(enabled) 
        self.warmup.setEnabled(enabled)

    def update_text(self, text):
        self.TEXT.setText(text)
    
    def displayImage(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Tạo QImage từ ảnh
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        # Tạo QPixmap từ QImage
        pixmap = QPixmap.fromImage(qimg)

        # Thay đổi kích thước pixmap để vừa với imgLabel, giữ nguyên tỷ lệ khung hình
        scaled_pixmap = pixmap.scaled(self.imgLabel.size(), Qt.AspectRatioMode.KeepAspectRatio)

        # Tạo mask bo tròn và vẽ pixmap lên
        mask_pixmap = QPixmap(scaled_pixmap.size())
        mask_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask_pixmap)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        radius = 45 # Điều chỉnh bán kính bo tròn (giống trong file .ui)
        rect = QRectF(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()

        # Hiển thị pixmap trên imgLabel
        self.imgLabel.setPixmap(mask_pixmap)
        self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # qformat = QImage.Format.Format_Indexed8
        # if len(img.shape) == 3:
        #     if img.shape[2] == 4:
        #         qformat = QImage.Format.Format_RGB888
        #     else:
        #         qformat = QImage.Format.Format_RGB888
        
        # img = QImage(img, img.shape[1], img.shape[0], qformat)
        # img = img.rgbSwapped()
        # self.imgLabel.setPixmap(QPixmap.fromImage(img))
        # self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def onRecognized(self, name, acc):
        self.predicting = False
        self.breakClicked() 
        self.stacked_widget.setCurrentIndex(1)  
        self.welcome_screen.update_text(name, acc) 
    
    def getInputName(self):
        name, ok = QInputDialog.getText(self, "Input your name", "Enter name:")
        if ok and name:
            self.goToWelcomeScreen(name)

    def goToWelcomeScreen(self, name):
        self.stacked_widget.setCurrentIndex(1)
        self.welcome_screen.update_text(name, 100)
    
    def closeEvent(self, event):
        if (self.cap != None) or self.warmup_active:
            # Nếu predict_name đang chạy, chặn sự kiện đóng và thông báo cho người dùng
            event.ignore()
            self.TEXT.setText("Still processing, try again soon.")
        else:
            # Nếu predict_name đã hoàn thành, cho phép đóng ứng dụng
            self.breakClicked()
            event.accept()