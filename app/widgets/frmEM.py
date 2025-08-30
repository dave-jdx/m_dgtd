from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmEM import Ui_frmEM
from ..icons import sysIcons
from .baseStyle import baseStyle

class frmEM(Ui_frmEM,QtWidgets.QMainWindow):
    sigMidiaModify=QtCore.pyqtSignal(tuple)
  
    def __init__(self,parent=None,mediaData:tuple=None):
        super(frmEM,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnClose.clicked.connect(self.close)

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)

        self.onLoad()  
    def onLoad(self):
        self.groupBox_2.setStyleSheet("QGroupBox:title{left:10px;height:50px;}")
        
        pass
    def actionApply(self):
        pass
    def actionOK(self):
        pass