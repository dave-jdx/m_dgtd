from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmThermalDirichlet import Ui_frmThermalDirichlet
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_Thermal_Base


class frmThermalBase(Ui_frmThermalDirichlet,frmBase):
    sigSelected=QtCore.pyqtSignal(int,PF_Thermal_Base,int)
    sigSelectSolid=QtCore.pyqtSignal(int)
    sigSelectFace=QtCore.pyqtSignal(int)
    sigClosed=QtCore.pyqtSignal()
  
    def __init__(self,parent=None,thermalObj:PF_Thermal_Base=None,selectType:int=2):
        super(frmThermalBase,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
 
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtSelectId.textChanged.connect(self.selectIdChanged)
        self._thermalObj=thermalObj
        self._selectType=selectType
        self._isManual=True

        if thermalObj is not None:
            self.setWindowTitle(thermalObj.title)
            self.lblValue.setText(thermalObj.lblTitle)
            if(thermalObj.selectId is not None):
                self.txtSelectId.setText(str(thermalObj.selectId+1))
            if(thermalObj.value is not None):
                self.txtValue.setText(str(thermalObj.value))
        if(selectType==3):
            self.lblSelect.setText("体编号")
        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        pass
    def actionApply(self):
        try:
            selectId_old=self._thermalObj.selectId
            thermalObj=PF_Thermal_Base()
            selectId=int(self.txtSelectId.text())-1
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
    def sig_chooseFace(self,faceId:int):
        self._isManual=False
        self.txtSelectId.setText(str(faceId+1))
        self._isManual=True
        pass
    def sig_chooseSolid(self,solidId:int):
        self._isManual=False
        self.txtSelectId.setText(str(solidId+1))
        self._isManual=True
        pass
    def selectIdChanged(self):
        try:
            if(not self._isManual):
                return
            if(self.txtSelectId.text()==""):
                return
            selectId=int(self.txtSelectId.text())-1
            if(self._selectType==2):
                self.sigSelectFace.emit(selectId)
            else:
                self.sigSelectSolid.emit(selectId)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","编号不合法，请重新输入(1~N)")
    def closeEvent(self, event):
        self.sigClosed.emit()
        super(frmThermalBase, self).closeEvent(event)
        
        pass