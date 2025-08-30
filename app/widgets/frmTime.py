from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmTime import Ui_frmTime
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.requestParam import RequestParam_time

class frmTime(Ui_frmTime,frmBase):
    sigTimeSet=QtCore.pyqtSignal(RequestParam_time)
  
    def __init__(self,parent=None,timeObj:RequestParam_time=None):
        super(frmTime,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)

        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self._timeObj=timeObj
        if timeObj is not None:
            try:
                self.txtTimeStep.setText(timeObj.timeStep)
            except:
                self.txtTimeStep.setText(str(timeObj.timeStep))
            self.txtTimeStepNum.setText(str(timeObj.timeStepNum))
            # self.txtTimeStepFactor.setText(str(timeObj.timeStepFactor))

            if(not hasattr(timeObj,"timeStep_heat")):
                timeObj.timeStep_heat="1"
                timeObj.timeStepNum_heat=1
                timeObj.timeStepFactor_heat=1
            self.txtTimeStep_heat.setText(timeObj.timeStep_heat)
            self.txtTimeStepNum_heat.setText(str(timeObj.timeStepNum_heat))
            # self.txtTimeStepFactor_heat.setText(str(timeObj.timeStepFactor_heat))
        # print("frmTime",self.font().pixelSize())
        
        self.onLoad() 
    def onLoad(self):
        super().onLoad()
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.groupBox.setStyleSheet(gbxStyle)
        self.groupBox_2.setStyleSheet(gbxStyle)
        
        pass
    def actionApply(self):
        try:
            timeObj=RequestParam_time()
            float(self.txtTimeStep.text())
            float(self.txtTimeStep_heat.text())

            int(self.txtTimeStepNum.text())
            int(self.txtTimeStepNum_heat.text())
            # float(self.txtTimeStepFactor.text())
            # float(self.txtTimeStepFactor_heat.text())

            timeObj.timeStep=self.txtTimeStep.text()
            timeObj.timeStepNum=int(self.txtTimeStepNum.text())
            # timeObj.timeStepFactor=float(self.txtTimeStepFactor.text())

            timeObj.timeStep_heat=self.txtTimeStep_heat.text()
            timeObj.timeStepNum_heat=int(self.txtTimeStepNum_heat.text())
            # timeObj.timeStepFactor_heat=float(self.txtTimeStepFactor_heat.text())
            self.sigTimeSet.emit(timeObj)
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
