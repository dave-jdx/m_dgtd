from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmDomain import Ui_frmDomain
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.requestParam import RequestParam_domain

class frmDomain(Ui_frmDomain,frmBase):
    sigDomainSet=QtCore.pyqtSignal(RequestParam_domain)
  
    def __init__(self,parent=None,domainObj:RequestParam_domain=None):
        super(frmDomain,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self._domainObj=domainObj
        if domainObj is not None:
            self.chk1.setChecked(domainObj.domain1[0])
            self.txtTimeStepNum.setText(str(domainObj.domain1[1]))
            self.chk2.setChecked(domainObj.domain2[0])
            self.txtTimeStepNum2.setText(str(domainObj.domain2[1]))
            # self.cbxDomainType.setCurrentIndex(domainObj.domainType)
            # self.txtTimeStepNum.setText(str(domainObj.domainTimeStepNum))
            
            pass

        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.gbxDomain.setStyleSheet(gbxStyle)
        
        pass
    def actionApply(self):
        try:
            domainObj=RequestParam_domain()
            domainObj.domain1=(self.chk1.isChecked(),int(self.txtTimeStepNum.text()))
            domainObj.domain2=(self.chk2.isChecked(),int(self.txtTimeStepNum2.text()))
            self.sigDomainSet.emit(domainObj)
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
