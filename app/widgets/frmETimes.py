from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmETimes import Ui_frmETimes
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_E_Times


class frmETimes(Ui_frmETimes,frmBase):
    sigApplyETimes=QtCore.pyqtSignal(PF_E_Times)

  
    def __init__(self,parent=None,eTimesObj:PF_E_Times=None,title="迭代电势设置"):
        super(frmETimes,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(title)
 
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self._eTimesObj=eTimesObj
        if(eTimesObj!=None):
            self.txtETimes.setText(str(eTimesObj.value))
      
       

        # print("frmETimes",self.font().pixelSize())

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        
        
        pass
    def actionApply(self):
        try:
            timeS=int(self.txtETimes.text())
            eTimesObj=PF_E_Times()
            eTimesObj.value=timeS
            self.sigApplyETimes.emit(eTimesObj)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","次数需要为正整数，请重新输入")
        pass
    def actionOK(self):
        try:
            timeS=int(self.txtETimes.text())
            eTimesObj=PF_E_Times()
            eTimesObj.value=timeS
            self.sigApplyETimes.emit(eTimesObj)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号不合法，请重新输入")
            return
        self.close()
        pass
  