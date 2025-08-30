from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmSimSelect import Ui_frmSimSelect
from ..icons import sysIcons
from .frmBase import frmBase

SIM_EXE_LIST=[
    "EM.exe",
    "Thermal.exe",
    "Mechanical.exe",
    "Thermal_Mechanical.exe",
    "Thermal_Mechanical_EM.exe",
    "Mechanical_EM.exe",
    "EM_Thermal.exe",
    "EM_Thermal_Mechanical.exe",
]


class frmSimSelect(Ui_frmSimSelect,frmBase):
    sigApplySimExe=QtCore.pyqtSignal(str)
  
    def __init__(self,parent=None):
        super(frmSimSelect,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
       

        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.gbxDomainPF.setStyleSheet(gbxStyle)
        
        pass

    def actionOK(self):
        pfDic,exeFileName=self.getSelect()
        if exeFileName=="":
            QtWidgets.QMessageBox.about(self,"Error","请选择计算类型")
            return
        self.sigApplySimExe.emit(exeFileName)
        self.close()
        pass
    def getSelect(self):
        exeFileName=""
        if(self.rdb1.isChecked()):
            exeFileName=SIM_EXE_LIST[0]
        elif(self.rdb2.isChecked()):
            exeFileName=SIM_EXE_LIST[1]
        elif(self.rdb3.isChecked()):
            exeFileName=SIM_EXE_LIST[2]
        elif(self.rdb4.isChecked()):
            exeFileName=SIM_EXE_LIST[3]
        elif(self.rdb5.isChecked()):
            exeFileName=SIM_EXE_LIST[4]
        elif(self.rdb6.isChecked()):
            exeFileName=SIM_EXE_LIST[5]
        elif(self.rdb7.isChecked()):
            exeFileName=SIM_EXE_LIST[6]
        elif(self.rdb8.isChecked()):
            exeFileName=SIM_EXE_LIST[7]
        return exeFileName
