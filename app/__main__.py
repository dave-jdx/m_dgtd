import sys,os,signal
# import argparse
# import subprocess

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtGui import QFont
NAME = 'CAE1.0'
# from .widgets.mySplashScreen import MovieSplashScreen
#need to initialize QApp here, otherewise svg icons do not work on windows




def main():

    # try:
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
    app = QtWidgets.QApplication.instance()  # checks if QApplication already exists
    if not app:  # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)
    # font=app.font()
    # font.setPixelSize(14)
    # font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
    # app.setFont(font)
 
    args=app.arguments()
    argString=":".join(args)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, False)
    # print(argString)
  
    from .main_window import MainWindow
    defaultFile=""
    if(len(args)>=3):
        defaultFile=args[2]#加载工程文件，如果有的话
    win = MainWindow(projectFile=defaultFile)


    # print(len(args))
    if(len(args)>=2):
        try:
            start_pid=int(args[1])
            os.kill(start_pid, signal.SIGTERM)
            print("kill success",start_pid)
        except Exception as e:
            print("Error",e)
   
    win.show()
   
    sys.exit(app.exec_())


    
   
if __name__ == "__main__":

    main()
