from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmStructDirichlet import Ui_frmStructDirichlet
from ..icons import sysIcons
from .frmBase import frmBase


class frmStructDirichlet(Ui_frmStructDirichlet,frmBase):
    sigFaceSelected=QtCore.pyqtSignal(int,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)
  
    def __init__(self,parent=None,faceId:int=-1):
        super(frmStructDirichlet,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._isManual=False
        self._faceId=faceId

        
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)

 
        

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtFaceId.textChanged.connect(self.selectIdChanged)
        if faceId>=0:
            self.txtFaceId.setText(str(faceId+1))

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        self._isManual=True
 
        pass
    def actionApply(self):
        try:
            faceId_old=self._faceId
            faceId=int(self.txtFaceId.text())-1
            self.sigFaceSelected.emit(faceId,faceId_old)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入")
        pass
    def actionOK(self):
        try:
            faceId_old=self._faceId
            faceId=int(self.txtFaceId.text())-1
            self.sigFaceSelected.emit(faceId,faceId_old)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入")
            return
        self.close()
        pass
    def sig_chooseFace(self,faceId:int):
        self._isManual=False
        self.txtFaceId.setText(str(faceId+1))
        self._isManual=True
        pass
    def selectIdChanged(self):
        try:
            if(not self._isManual):
                return
            if(self.txtFaceId.text()==""):
                return
            selectId=int(self.txtFaceId.text())-1
            self.sigSelectFace.emit(selectId)
   
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","编号不合法，请重新输入(1~N)")
    def closeEvent(self, event):
        self.sigClosed.emit()
        super(frmStructDirichlet, self).closeEvent(event)
        
        pass