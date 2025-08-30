from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmCircuit import Ui_frmCircuit
from ..icons import sysIcons
from .baseStyle import baseStyle

from .frmCircuitCreate import frmCircuitCreate

class frmCircuit(Ui_frmCircuit,QtWidgets.QMainWindow):
    sigMidiaModify=QtCore.pyqtSignal(tuple)
  
    def __init__(self,parent=None,mediaData:tuple=None):
        super(frmCircuit,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnClose.clicked.connect(self.close)
        self.btnAdd.clicked.connect(self.actionAdd)

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)

        self.onLoad()  
    def onLoad(self):
        self.tbFaces.setFont(self._font)
        self.groupBox_2.setStyleSheet("QGroupBox:title{left:10px;height:50px;}")
        
        
        pass
    def actionApply(self):
        pass
    def actionOK(self):
        pass
    def actionAdd(self):
        self.frmCircuitCreate=frmCircuitCreate(self)
        self.frmCircuitCreate.show()
        pass