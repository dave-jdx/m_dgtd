from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmEMPEC import Ui_frmEMPEC
from ..icons import sysIcons
from .frmBase import frmBase


class frmEMPEC(Ui_frmEMPEC,frmBase):
    sigFaceSelected=QtCore.pyqtSignal(int)
    sigSelectFace=QtCore.pyqtSignal(int)
  
    def __init__(self,parent=None,title="电磁-PEC"):
        super(frmEMPEC,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(title)
 
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtFaceId.textChanged.connect(self.faceIdChanged)

        print("frmPEC",self.font().pixelSize())

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        
        pass
    def actionApply(self):
        try:
            faceId=int(self.txtFaceId.text())-1
            self.sigFaceSelected.emit(faceId)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入")
        pass
    def actionOK(self):
        try:
            faceId=int(self.txtFaceId.text())-1
            self.sigFaceSelected.emit(faceId)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入")
            return
        self.close()
        pass
    def sig_chooseFace(self,faceId:int):
        self.txtFaceId.setText(str(faceId+1))
        pass
    def faceIdChanged(self):
        try:
            faceId=int(self.txtFaceId.text())-1
            self.sigSelectFace.emit(faceId)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入(1~N)")