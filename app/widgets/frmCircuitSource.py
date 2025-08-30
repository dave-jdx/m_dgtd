from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmCircuitSource import Ui_frmCIrcuitSource
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_Circuit_Source

#电路-源设置，增加端口类型 0-线端口（默认） 1-面端口
class frmCircuitSource(Ui_frmCIrcuitSource,frmBase):
    sigFaceSelected=QtCore.pyqtSignal(int,PF_Circuit_Source,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)
  
    def __init__(self,parent=None,sourceObj:PF_Circuit_Source=None):
        super(frmCircuitSource,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._isManual=False
        self._u_length=0
        self._v_length=0
        self._is_loading=True
   
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
      
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.cbxWaveType.currentIndexChanged.connect(self.showHide)
        self.txtFaceId.textChanged.connect(self.selectIdChanged)
        self.btnExchange.clicked.connect(self.actionExcgange)
        self._sourceObj=sourceObj
        if(sourceObj!=None):
            self.txtFaceId.setText(str(sourceObj.faceId+1))
            self.cbxWaveType.setCurrentIndex(sourceObj.waveType)
            self.txtAmplitude.setText(str(sourceObj.amplitude))
            if(type(sourceObj.frequency)!=str):
                self.txtFrequency.setText(str(sourceObj.frequency))
            else:
                self.txtFrequency.setText(sourceObj.frequency)
            self.txtPluseWidth.setText(str(sourceObj.pulseWidth))
            self.txtDelay.setText(str(sourceObj.delay))
            if(hasattr(sourceObj,"uv")):
                v_uv=sourceObj.uv
                self._u_length=v_uv[0]
                self._v_length=v_uv[1]
                self.setUVText(v_uv[0],v_uv[1])
            if(not hasattr(sourceObj,"source_type")):
                sourceObj.source_type=0
            if(sourceObj.source_type==0):
                self.rdbPortLine.setChecked(True)
            else:
                self.rdbPortFace.setChecked(True)

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        self.txtLengthUV.setEnabled(False)
        self.showHide()
        self._isManual=True
        self._is_loading=False
        

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
            faceId_old=-1
            if(self._sourceObj!=None):
                faceId_old=self._sourceObj.faceId
            faceId=int(self.txtFaceId.text())-1
            sourceObj=PF_Circuit_Source()
            sourceObj.faceId=faceId
            sourceObj.waveType=self.cbxWaveType.currentIndex()
            sourceObj.amplitude=float(self.txtAmplitude.text())
            freq=float(self.txtFrequency.text())
            sourceObj.frequency=self.txtFrequency.text()
            sourceObj.pulseWidth=float(self.txtPluseWidth.text())
            sourceObj.delay=float(self.txtDelay.text())
            sourceObj.uv=(self._u_length,self._v_length)
            sourceObj.source_type=0 if self.rdbPortLine.isChecked() else 1
            self.sigFaceSelected.emit(faceId,sourceObj,faceId_old)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号/参数不合法，请重新输入"+str(e))
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
        super(frmCircuitSource, self).closeEvent(event)
        
        pass
    def sig_chooseFaceLength(self,u_length:float,v_length:float):
        self._u_length=u_length
        self._v_length=v_length
        self.setUVText(u_length,v_length)
        
        pass
    def setUVText(self,u,v):
        u_text="{:.6e}".format(u/1000)
        v_text="{:.6e}".format(v/1000)
        self.txtLengthUV.setText(f"({u_text},{v_text})")
    def actionExcgange(self):
        u=self._u_length
        v=self._v_length
        self._u_length=v
        self._v_length=u
        self.setUVText(v,u)
        pass