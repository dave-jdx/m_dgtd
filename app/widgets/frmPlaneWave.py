from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmPlaneWave import Ui_frmPlaneWave
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_Plane_Wave

#电路-源设置，增加端口类型 0-线端口（默认） 1-面端口
class frmPlaneWave(Ui_frmPlaneWave,frmBase):
    sigApplyPlaneWave=QtCore.pyqtSignal(PF_Plane_Wave)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)
  
    def __init__(self,parent=None,waveObj:PF_Plane_Wave=None):
        super(frmPlaneWave,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
       
      
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.cbxWaveType.currentIndexChanged.connect(self.showHide)
      
        self._waveObj=waveObj
        if(waveObj!=None):
        
            self.cbxWaveType.setCurrentIndex(waveObj.waveType)
            self.txtAmplitude.setText(str(waveObj.amplitude))
            if(type(waveObj.frequency)!=str):
                self.txtFrequency.setText(str(waveObj.frequency))
            else:
                self.txtFrequency.setText(waveObj.frequency)
            self.txtPluseWidth.setText(str(waveObj.pulseWidth))
            self.txtDelay.setText(str(waveObj.delay))
            self.txtTheta.setText(str(waveObj.theta))
            self.txtPhi.setText(str(waveObj.phi))
            self.txtEAngle.setText(str(waveObj.eAngle))
           
          

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
      
       
        pass
    def showHide(self):
        if(self.cbxWaveType.currentIndex()==0):
            self.txtPluseWidth.setEnabled(False)
            self.txtDelay.setEnabled(False)
            self.txtPluseWidth.setText("0")
            self.txtDelay.setText("0")
        else:
            self.txtPluseWidth.setEnabled(True)
            self.txtDelay.setEnabled(True)
        pass
    def actionApply(self):
        try:
         
          
           
            waveObj=PF_Plane_Wave()
            
            waveObj.waveType=self.cbxWaveType.currentIndex()
            waveObj.amplitude=self.txtAmplitude.text()
            float(self.txtFrequency.text())
            float(self.txtAmplitude.text())
            waveObj.frequency=self.txtFrequency.text()
            waveObj.pulseWidth=float(self.txtPluseWidth.text())
            waveObj.delay=float(self.txtDelay.text())
            waveObj.theta=float(self.txtTheta.text())
            waveObj.phi=float(self.txtPhi.text())
            waveObj.eAngle=float(self.txtEAngle.text())
            self.sigApplyPlaneWave.emit(waveObj)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","参数不合法，请重新输入"+str(e))
            return(-1,"error")

        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass

    def closeEvent(self, event):
        self.sigClosed.emit()
        super(frmPlaneWave, self).closeEvent(event)
        
        pass
