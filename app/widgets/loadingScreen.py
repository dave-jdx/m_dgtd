import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QProgressBar, QMainWindow
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtCore import Qt, QTimer

class loadingScreen(QSplashScreen):
    def __init__(self, movie:QMovie):
        super().__init__(QPixmap())
        self.movie = movie
        self.movie.frameChanged.connect(self.updateFrame)
        self.movie.start()

        # 设置窗口无边框和置顶
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # # 创建进度条
        self.progress = QProgressBar(self)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setGeometry(0, self.movie.currentPixmap().height() - 30, 
                                  self.movie.currentPixmap().width(), 20)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

    def updateFrame(self):
        pixmap = self.movie.currentPixmap()
        self.setPixmap(pixmap)

    def setProgress(self, value):
        self.progress.setValue(value)