# This Python file uses the following encoding: utf-8
import sys
import os
import cv2
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6.uic import loadUi
from detection import faceDetection
import imageio
import threading

class ThreadClass(QtCore.QThread):
    """
    A worker thread class responsible for capturing video frames, performing face detection, 
    and emitting signals to update the user interface.

    Attributes:
        signal_update_text (QtCore.pyqtSignal): Signal to emit updated text to the UI.

    Args:
        folder (str): Path to the application folder.
        detect (faceDetection): An instance of the faceDetection class for face recognition.
        parent (QObject, optional): Parent object. Defaults to None.
        skip_frame_first (int, optional): Number of initial frames to skip. Defaults to 30.
        frame_skip (int, optional): Number of frames to skip between detections. Defaults to 30.
        threshold (float, optional): Confidence threshold for face recognition. Defaults to 0.5.
    """
    signal_update_text = QtCore.pyqtSignal(str)

    def __init__(self, folder, detect, parent=None, skip_frame_first = 30, frame_skip = 30, threshold = 0.5):
        super(ThreadClass, self).__init__(parent)
        self.folder = folder
        self.detect = detect
        self.running = True
        self.img_path = os.path.join(self.folder, "my_image.png")

        self.skip_frame_first = skip_frame_first
        self.frame_skip = frame_skip
        self.threshold = threshold

        self.mutex = threading.Lock() 
        

    def run(self):
        """
        Starts the thread execution.

        This method captures video frames from the camera, performs face detection at specified intervals,
        and emits signals with recognized names and confidence levels or "No match found." messages.
        """
        self.running = True
        frame_count = 0
        while self.running:
            with self.mutex:
                if self.cap is not None:  # Kiểm tra self.cap khác None trước khi sử dụng
                    ret, frame = self.cap.read()
                else:
                    ret = False
                    frame = None
            
            if not ret:
                break
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_count += 1
            if (frame_count < self.skip_frame_first) or (frame_count % self.frame_skip != 0):
                continue

            imageio.imwrite(self.img_path, frame)
            name, acc = self.detect.predict_name(self.img_path)
            if acc >= self.threshold:
                self.signal_update_text.emit(f"Name: {name} with acc {acc:.2f}")
            else:
                self.signal_update_text.emit("No match found.")
            print(f"frame count: {frame_count}")
    


class tehSeencode(QDialog):
    """
    Main GUI class responsible for handling user interactions, displaying camera feed,
    and managing the face detection thread.

    Args:
        folder (str): Path to the application folder.
        parent (QObject, optional): Parent object. Defaults to None.
        skip_frame_first (int, optional): Number of initial frames to skip. Defaults to 30.
        frame_skip (int, optional): Number of frames to skip between detections. Defaults to 30.
        threshold (float, optional): Confidence threshold for face recognition. Defaults to 0.5.
    """
    def __init__(self, folder, parent=None, skip_frame_first=30, frame_skip=30, threshold=0.5):
        super(tehSeencode, self).__init__(parent)
        ui_path = os.path.join(folder, 'form.ui')
        loadUi(ui_path, self)
        self.folder = folder
        self.detect = faceDetection(self.folder)

        self.SHOW.clicked.connect(self.onClicked)
        self.TEXT.setText('Findly Press')
        self.Break.clicked.connect(self.breakClicked)
        self.warmup.clicked.connect(self.WarmUp)

        self.cap = None
        self.WarmUp()
        self.running = True
        self.thread = ThreadClass(self.folder, self.detect, parent, skip_frame_first, frame_skip, threshold)

    def WarmUp(self):
        """
        Warms up the face detection model.

        This method is called to prepare the face detection model for use.
        """
        if (self.cap == None):
            self.detect.warmup()

    @pyqtSlot()
    def onClicked(self):
        """
        Handles the 'Show' button click event.

        Starts capturing video from the camera, creates and connects the face detection thread,
        and initiates the camera display loop.
        """
        print("Button show click!")
        self.TEXT.setText("Camera starting...")

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
        """
        Handles the 'Break' button click event.

        Stops the camera, terminates the face detection thread, and releases resources.
        """
        self.TEXT.setText("Don't Click any button!")
        if self.cap != None:
            with self.thread.mutex:
                self.thread.running = False
            self.thread.wait() # Đợi luồng kết thúc

            self.cap.release()
            cv2.destroyAllWindows()
        self.TEXT.setText("Camera stopped")
        self.cap = None

    def update_text(self, text):
        """
        Updates the text displayed in the UI.

        Args:
            text (str): The text to display.
        """
        self.TEXT.setText(text)

    def displayImage(self, img):
        """
        Displays an image in the UI's image label.

        Args:
            img (numpy.ndarray): The image to display.
        """
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

if __name__ == "__main__":
    folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
    app = QApplication(sys.argv)
    widget = tehSeencode(folder=folder)
    widget.show()
    sys.exit(app.exec())