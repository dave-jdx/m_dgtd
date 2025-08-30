from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmTemperature import Ui_frmTemperature
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.requestParam import RequestParam_temperature

class frmTemperature(Ui_frmTemperature,frmBase):
    sigTemperatureSet=QtCore.pyqtSignal(RequestParam_temperature)
  
    def __init__(self,parent=None,temperatureObj:RequestParam_temperature=None):
        super(frmTemperature,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)

        self._temperatureObj=temperatureObj
        if temperatureObj is not None:
            self.txtTemperatureStart.setText(str(temperatureObj.temperatureStart))
            self.txtTemperatureEnv.setText(str(temperatureObj.temperatureEnv))
        self.onLoad() 
    def onLoad(self):
        super().onLoad()
        
        pass
    def actionApply(self):
        try:
            temperatureObj=RequestParam_temperature()
            temperatureObj.temperatureStart=float(self.txtTemperatureStart.text())
            temperatureObj.temperatureEnv=float(self.txtTemperatureEnv.text())
            self.sigTemperatureSet.emit(temperatureObj)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","时间设置数据不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
