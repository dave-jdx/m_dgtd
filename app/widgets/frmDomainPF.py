from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmDomainPF import Ui_frmDomainPF
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_EBase

class frmDomainPF(Ui_frmDomainPF,frmBase):
    sigModify=QtCore.pyqtSignal(PF_EBase)
  
    def __init__(self,parent=None,eObj:PF_EBase=None):
        super(frmDomainPF,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self._eObj=eObj
        if eObj is not None:
            self.chkModel.setChecked(eObj.cal_dic[0])
            self.chkAir.setChecked(eObj.cal_dic[1])
            self.chkPML.setChecked(eObj.cal_dic[2])
            self.setWindowTitle(eObj.title)
            pass

        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.gbxDomainPF.setStyleSheet(gbxStyle)
        
        pass
    def actionApply(self):
        try:
            eObj=self._eObj
            modelChecked=self.chkModel.isChecked()
            airChecked=self.chkAir.isChecked()
            pmlChecked=self.chkPML.isChecked()
            eObj.cal_dic=[modelChecked,airChecked,pmlChecked]

            self.sigModify.emit(eObj)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","观察域设置数据不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
