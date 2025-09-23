from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmThermalConvection import Ui_frmThermalConvection
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_Thermal_Base


class frmThermalConvection(Ui_frmThermalConvection,frmBase):
    sigSelected=QtCore.pyqtSignal(int,PF_Thermal_Base,int)
    sigSelectSolid=QtCore.pyqtSignal(int)
    sigSelectFace=QtCore.pyqtSignal(int)
    sigClosed=QtCore.pyqtSignal()
  
    def __init__(self,parent=None,thermalObj:PF_Thermal_Base=None,selectType:int=2):
        super(frmThermalConvection,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
 

        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
 
        self._thermalObj=thermalObj
        self._selectType=selectType
        self._isManual=True

        if thermalObj is not None:
            self.setWindowTitle(thermalObj.title)
          
 
            if(thermalObj.value is not None):
                self.txtValue.setText(str(thermalObj.value))
   
        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        pass
    def actionApply(self):
        try:
            selectId_old=self._thermalObj.selectId
            thermalObj=PF_Thermal_Base()
            selectId=-1
            thermalObj.selectId=selectId
            thermalObj.value=float(self.txtValue.text())
            thermalObj.title=self._thermalObj.title
            thermalObj.lblTitle=self._thermalObj.lblTitle
            self.sigSelected.emit(selectId,thermalObj,selectId_old)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号/值不合法，请重新输入"+str(e))
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
        super(frmThermalConvection, self).closeEvent(event)
        
        pass