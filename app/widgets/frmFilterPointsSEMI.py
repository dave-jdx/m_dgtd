from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmFilterPointsSEMI import Ui_frmFilterPointsSEMI
from ..icons import sysIcons
from .frmBase import frmBase


class frmFilterPointsSEMI(Ui_frmFilterPointsSEMI,frmBase):
    sigApply=QtCore.pyqtSignal(dict)
    sigClosed=QtCore.pyqtSignal()
  
    def __init__(self,parent=None):
        super(frmFilterPointsSEMI,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._values=["电子浓度","空穴浓度","电势值"]
    
        
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        for v in self._values:
            self.cbxValues.addItem(v)
      
        self.cbxValues.currentIndexChanged.connect(self.actionValueChanged)

        self.onLoad()  
    def onLoad(self):
        
        super().onLoad()
        pass
    
    def actionValueChanged(self):
        self.actionApply(tips=False)
    def actionFilter(self):
        try:
           
            self.actionApply(tips=False)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.about(self,"Error","数据设置错误,请重新选择"+str(e))
    def actionApply(self, tips=True):
        try:
            filterValue = self.cbxValues.currentIndex()
            if filterValue < 0:
                if(tips):
                    QtWidgets.QMessageBox.about(self,"Error","请选择物理量")
                return 
           
            self.sigApply.emit({
       
            'filterValue': filterValue,
           })

            pass 
        except Exception as e:
            print(e)
            if tips:
                # 显示错误信息
                QtWidgets.QMessageBox.about(self,"Error","数据设置错误,请重新选择"+str(e))
            else:
                # 仅打印错误信息
                print("数据设置错误,请重新选择", e)
          
        pass
    def actionOK(self):
        self.actionApply()
        pass
    def closeEvent(self, a0):
        self.sigClosed.emit()
        return super().closeEvent(a0)   