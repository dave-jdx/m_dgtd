from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmPostFilter import Ui_frmPostFilter
from ..icons import sysIcons
from .frmBase import frmBase

class frmPostFilter(Ui_frmPostFilter,frmBase):
    sigShowParamFilter=QtCore.pyqtSignal(int,int)
  
    def __init__(self,parent=None,timeList=[],tetera_num=1000000):
        super(frmPostFilter,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        # self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        for t in timeList:
            self.cbxTime.addItem(t)
        self.txtMaxNum.setText(str(tetera_num))

        self.cbxTime.currentIndexChanged.connect(self.actionApply)

        
       

        self.onLoad() 
    def onLoad(self):
        super().onLoad()    
        
        
        pass
    def actionApply(self):
        try:
            timeIndex=self.cbxTime.currentIndex()
            teteraNum=int(self.txtMaxNum.text())
            self.sigShowParamFilter.emit(timeIndex,teteraNum)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","参数设置错误"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        pass
