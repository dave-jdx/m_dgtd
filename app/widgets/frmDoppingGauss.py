from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmDoppingGauss import Ui_frmDoppingGauss
from ..icons import sysIcons
from .baseStyle import baseStyle
from .frmBase import frmBase
from ..dataModel.pf import PF_Dopping_Gaussian

class frmDoppingGauss(Ui_frmDoppingGauss,frmBase):
    sigApplyDoppingGauss=QtCore.pyqtSignal(PF_Dopping_Gaussian,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int) 
 
  
    def __init__(self,parent=None,doppingObj:PF_Dopping_Gaussian=None):
        super(frmDoppingGauss,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent   

     
        self._isManual=False

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtBodyId.textChanged.connect(self.selectIdChanged)
 
        self._doppingObj=doppingObj
        if(doppingObj!=None):
            self.txtBodyId.setText(str(doppingObj.dopping_bodyId+1))
            self.txtFaceId.setText(str(doppingObj.dopping_faceId+1))
            self.cbxDoppingType.setCurrentIndex(doppingObj.dopping_type)
            self.txtConc.setText(str(doppingObj.dopping_concentration))
            self.txtDepth.setText(str(doppingObj.dopping_depth))

        self.onLoad()  
    def onLoad(self):
  
        super().onLoad()
        self._isManual=True
        self.txtBodyId.setEnabled(False)
        self.txtFaceId.setFocus()
        pass
    def actionApply(self):
        try:
    
            faceId_old=-1
            if(self._doppingObj!=None):

                faceId_old=self._doppingObj.dopping_faceId
            bodyId=int(self.txtBodyId.text())-1
            faceId=int(self.txtFaceId.text())-1
            doppingType=self.cbxDoppingType.currentIndex()
            concentration=float(self.txtConc.text())
            doppingObj=PF_Dopping_Gaussian()
            doppingObj.dopping_bodyId=bodyId
            doppingObj.dopping_faceId=faceId
            doppingObj.dopping_type=doppingType
            doppingObj.dopping_concentration=concentration
            doppingObj.dopping_depth=float(self.txtDepth.text())
            self.sigApplyDoppingGauss.emit(doppingObj,faceId_old)
            
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号/电阻不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
    def sig_chooseFace(self,faceId:int,isSelected:bool,shape,shapeId:int):
        self._isManual=False
        self.txtFaceId.setText(str(faceId+1))
        self.txtBodyId.setText(str(shapeId+1))
        self._isManual=True
        pass

    def selectIdChanged(self):
        try:
            if(not self._isManual):
                return
            if(self.txtBodyId.text()==""):
                return
            selectId=int(self.txtBodyId.text())-1
            self.sigSelectFace.emit(selectId)
   
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","编号不合法，请重新输入(1~N)")
    def closeEvent(self, event):
        self.sigClosed.emit()
        super(frmDoppingGauss, self).closeEvent(event)
        
        pass
