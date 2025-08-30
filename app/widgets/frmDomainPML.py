from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmDomainPML import Ui_frmDomainPML
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_EBase

class frmDomainPML(Ui_frmDomainPML,frmBase):
    sigModify=QtCore.pyqtSignal(tuple,tuple,tuple)
    sigClosed=QtCore.pyqtSignal()
    sigShowPML=QtCore.pyqtSignal(bool)
    sigShowEXF=QtCore.pyqtSignal(bool)
  
    def __init__(self,parent=None,pml:tuple=(1,1,True,False,0.01,False),exf=(0.5,True,False,0.01,False),freq=(1e9,True)):
        super(frmDomainPML,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
      

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.btnApply.clicked.connect(self.actionApply)

        self.txtDistancePML.setText(str(pml[0]))
        self.txtThickness.setText(str(pml[1]))
        self.chkPMLVisible.setChecked(pml[2])
        self.chkUsed_pml.setChecked(pml[3])
        self.txtFreq.setText(str(freq[0]))
        self.chkFreq.setChecked(freq[1])
        self.chkPMLVisible.clicked.connect(lambda:self.sigShowPML.emit(self.chkPMLVisible.isChecked()))

        self.txt_pml_mesh_size.setText(str(pml[4]))
        self.chk_pml_mesh_size.setChecked(pml[5])
        

        self.txtDistanceEXF.setText(str(exf[0]))
        self.chkEXFVisible.setChecked(exf[1])
        self.chkUsed_exf.setChecked(exf[2])
        self.chk_exf_mesh_size.setChecked(exf[4])
        self.txt_exf_mesh_size.setText(str(exf[3]))

        self.chkEXFVisible.clicked.connect(lambda:self.sigShowEXF.emit(self.chkEXFVisible.isChecked()))
        self.txtFreq.textChanged.connect(self.freqChanged)
        self.chkFreq.stateChanged.connect(self.freqChanged)

        

        


        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.gbxPML.setStyleSheet(gbxStyle)
        # self.gbxEXF.setStyleSheet(gbxStyle)
        self.gbxAir.setStyleSheet(gbxStyle)
        
        pass
    def freqChanged(self):
        try:
            if(self.chkFreq.isChecked()==False):
                return
            c=3e8
            freq=float(self.txtFreq.text())
            if(freq<=0):
                raise Exception("频率应大于0")
            #计算波长
            wl=c/freq
            #设置为1/8波长并保留6位小数
            self.txtDistanceEXF.setText(str(round(wl/8,6)))
            self.txtDistancePML.setText(str(round(wl/4,6)))
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"Error","频率设置不合法，请重新输入"+str(e))
            print("Error",e)
            return
        
    def actionApply(self):
        try:
            pml=(float(self.txtDistancePML.text()),
                 float(self.txtThickness.text()),
                 self.chkPMLVisible.isChecked(),
                 self.chkUsed_pml.isChecked(),
                 float(self.txt_pml_mesh_size.text()),
                self.chk_pml_mesh_size.isChecked()
                 )
            exf=(float(self.txtDistanceEXF.text()),
                 self.chkEXFVisible.isChecked(),
                 self.chkUsed_exf.isChecked(),
                    float(self.txt_exf_mesh_size.text()),
                    self.chk_exf_mesh_size.isChecked()
                 )
            
            freq=(self.txtFreq.text(),
                  self.chkFreq.isChecked())
            if(exf[0]<=0 or pml[0]<=0 or pml[1]<=0 or pml[0]<=exf[0]):
                raise Exception("设置数据不合法,空气域模型距离应大于外推面模型距离，且两者均大于0")

            self.sigModify.emit(pml,exf,freq)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","设置数据不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
    def closeEvent(self, event):
        self.sigShowPML.emit(self.chkPMLVisible.isChecked())
        self.sigShowEXF.emit(self.chkEXFVisible.isChecked())
        super(frmDomainPML, self).closeEvent(event)
        
        pass
