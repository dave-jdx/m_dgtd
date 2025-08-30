import sys,os,signal
# import argparse
# import subprocess

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtCore import QTimer
from app.api import api_mesh
app = QtWidgets.QApplication.instance()  # checks if QApplication already exists
if not app:  # create QApplication if it doesnt exist
    app = QtWidgets.QApplication(sys.argv)
api_mesh.mesh_import()