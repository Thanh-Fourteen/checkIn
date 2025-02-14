from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.uic import loadUi
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
import os
import cv2
import pandas as pd
import soundfile as sf
import sounddevice as sd

class WelcomeScreen(QMainWindow):
    signal_no_match_found = pyqtSignal(str)
    def __init__(self, folder, csv_path, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        self.folder = folder
        ui_path = os.path.join(folder, "UI", 'wellcome.ui')
        loadUi(ui_path, self)
        
        self.name = self.findChild(QtCore.QObject, "name")
        self.name.setReadOnly(True)
        self.name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.posi = self.findChild(QtCore.QObject, "posi")
        self.posi.setReadOnly(True)
        self.posi.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.imgLabel = self.findChild(QLabel, "img")
        self.radius = 43  

        self.csv_path = csv_path
        self.load_csv()

    def name2idx(self, name, is_parent):
        idx = -1

        self.df['id'] = self.df['id'].astype(str).str.lower()

        condition1 = self.df['id'].str.contains(str(name).lower(), na=False) 
        condition2 = self.df['isparent'] == is_parent  

        match = self.df[condition1 & condition2]

        if not match.empty:
            idx = int(match.iloc[0]['idx'])
            self.signal_no_match_found.emit("Success found")
            self.update_text(idx, 100)
        else:
            self.signal_no_match_found.emit("Find name error")
            print("Find name error")


    def load_csv(self):
        self.df = pd.read_csv(self.csv_path)

    def update_text(self, idx, acc):
        name = self.df.loc[idx, 'names']
        id = self.df.loc[idx, 'id']
        pos = self.df.loc[idx, 'position']
        img_path = self.df.loc[idx, 'path']
        voice_path = self.df.loc[idx, 'voice']
        
        img_path = os.path.join(self.folder, "img_database", img_path)
        audio_path = os.path.join(self.folder, "voice", voice_path)
        self.df.loc[idx, 'checkin'] = True

        self.df.to_csv(self.csv_path, index=False)  

        self.default_image_path = img_path
        self.load_image(self.default_image_path)

        textName = f"Chào mừng {name} {id} đến với buổi vinh danh."
        textPos = f"Vị trí ghế là {pos}"

        self.name.setText(textName)
        self.posi.setText(textPos)

        self.load_audio(audio_path)
    
    def load_audio(self, audio_path):
        audio, sample_rate = sf.read(audio_path)
        sd.play(audio, sample_rate)

    def load_image(self, image_path):
        if os.path.exists(image_path):
            # Use OpenCV to load the image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not load image with OpenCV from {image_path}")
                self.load_default_image() # Load a default image
                return

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img.shape

            bytes_per_line = ch * w
            qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(self.imgLabel.size(), Qt.AspectRatioMode.KeepAspectRatio)
            rounded_pixmap = self.round_corners(scaled_pixmap, self.radius)

            self.imgLabel.setPixmap(rounded_pixmap)
            self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            print(f"Image not found: {image_path}")
            self.load_default_image()

    def round_corners(self, pixmap, radius):
        """Applies rounded corners to the given QPixmap."""
        mask_pixmap = QPixmap(pixmap.size())
        mask_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask_pixmap)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform, True)  # More hints
        path = QPainterPath()
        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return mask_pixmap

    def load_default_image(self):
        """Loads and displays the default image with rounded corners."""
        if os.path.exists(self.default_image_path):
            self.load_image(self.default_image_path)
        else:
            print(f"Default image not found: {self.default_image_path}")