from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmPostParam import Ui_frmPostParam
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.requestParam import RequestParam_domain

class frmPostParam(Ui_frmPostParam,frmBase):
    sigShowParam=QtCore.pyqtSignal(bool,bool)
  
    def __init__(self,parent=None):
        super(frmPostParam,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)

        self.chk1.stateChanged.connect(self.actionApply)
        self.chk2.stateChanged.connect(self.actionApply)
       

        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.gbxDomain.setStyleSheet(gbxStyle)
        
        pass
    def actionApply(self):
        try:
            showModel=self.chk1.isChecked()
            showPost=self.chk2.isChecked()
            self.sigShowParam.emit(showModel,showPost)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","参数设置错误"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        pass
