from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmSBoundGate import Ui_frmSBoundGate
from ..icons import sysIcons
from .baseStyle import baseStyle
from .frmBase import frmBase
from ..dataModel.pf import PF_SBound_Insulate_Gate

class frmSBoundGate(Ui_frmSBoundGate,frmBase):
    sigApplySBoundGate=QtCore.pyqtSignal(PF_SBound_Insulate_Gate,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)    
  
    def __init__(self,parent=None,boundObj:PF_SBound_Insulate_Gate=None):
        super(frmSBoundGate,self).__init__(parent)
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
            self.txtPerm.setText(str(boundObj.permittivity))
            self.txtThickness.setText(str(boundObj.thickness))
            self.txtFunc.setText(str(boundObj.metal_work_function))
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
     
         
            boundObj=PF_SBound_Insulate_Gate()   
            boundObj.faceId=faceId
            boundObj.permittivity=float(self.txtPerm.text())
            boundObj.thickness=float(self.txtThickness.text())
            boundObj.metal_work_function=float(self.txtFunc.text())
            boundObj.voltage=float(self.txtVoltage.text())
                                                                                                                                                                                                                                            

            self.sigApplySBoundGate.emit(boundObj,faceId_old)
            
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
        super(frmSBoundGate, self).closeEvent(event)
        
        pass
