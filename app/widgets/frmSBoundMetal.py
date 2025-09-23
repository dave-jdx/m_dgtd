from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmSBoundMetal import Ui_frmSBoundMetal
from ..icons import sysIcons
from .baseStyle import baseStyle
from .frmBase import frmBase
from ..dataModel.pf import PF_SBound_Metal_Contact

class frmSBoundMetal(Ui_frmSBoundMetal,frmBase):
    sigApplySBoundMetal=QtCore.pyqtSignal(PF_SBound_Metal_Contact,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)    
  
    def __init__(self,parent=None,boundObj:PF_SBound_Metal_Contact=None):
        super(frmSBoundMetal,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent   

     
        self._isManual=False

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtFaceId.textChanged.connect(self.selectIdChanged)
 
        self._boundObj=boundObj
        if(boundObj!=None):
            self.txtFaceId.setText(str(boundObj.faceId+1))
            
            self.cbxBoundType.setCurrentIndex(boundObj.contact_type)
            self.txtVoltage.setText(str(boundObj.voltage))

        self.onLoad()  
    def onLoad(self):
  
        super().onLoad()
        self._isManual=True
        pass
    def actionApply(self):
        try:
            faceId_old=-1
            if(self._boundObj!=None):
                faceId_old=self._boundObj.faceId
            faceId=int(self.txtFaceId.text())-1
            boundType=self.cbxBoundType.currentIndex()
            voltage=float(self.txtVoltage.text())
            boundObj=PF_SBound_Metal_Contact()   
            boundObj.faceId=faceId
            boundObj.contact_type=boundType                                                                                                                                                                                                                                          
            boundObj.voltage=voltage
            self.sigApplySBoundMetal.emit(boundObj,faceId_old)
            
            return (1,"suceess")                                                                                                             
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","数据不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
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
        super(frmSBoundMetal, self).closeEvent(event)
        
        pass
