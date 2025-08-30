from PyQt5 import QtWidgets, QtGui, QtCore
# or from PySide2 import QtWidgets, QtGui, QtCore
import sys
import time


class MovieSplashScreen(QtWidgets.QSplashScreen):

	def __init__(self, pathToGIF):
		self.movie = QtGui.QMovie(pathToGIF)
		self.movie.jumpToFrame(0)
		self.mytimer = QtCore.QTimer()
		pixmap = QtGui.QPixmap(self.movie.frameRect().size())
		QtWidgets.QSplashScreen.__init__(self, pixmap)
		self.movie.frameChanged.connect(self.repaint)
		self.mytimer.timeout.connect(self.onTimer)
		self.mytimer.start(1)

	def showEvent(self, event):
		self.movie.start()

	def hideEvent(self, event):
		self.movie.stop()

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		pixmap = self.movie.currentPixmap()
		self.setMask(pixmap.mask())
		painter.drawPixmap(0, 0, pixmap)
	def onTimer(self):
		s=self.movie.speed()
		for n in range(1,3000,s):
			QtWidgets.QApplication.instance().processEvents()
			time.sleep(0.1)
		pass


class MainWindowx(QtWidgets.QMainWindow):

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self, None)
		self.setCentralWidget(QtWidgets.QLabel("Hello world!"))

def main():

	app = QtWidgets.QApplication(sys.argv)

	pathToGIF = "icons/loading.gif"
	splash = MovieSplashScreen(pathToGIF)
	splash.show()

	def showWindow():
		splash.close()
		form.show()
    # from .main_window import MainWindow
	QtCore.QTimer.singleShot(3500, showWindow)
	form = MainWindowx()
	app.exec_()
# main()