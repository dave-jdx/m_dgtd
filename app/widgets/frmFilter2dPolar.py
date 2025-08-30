from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmFilter2dPolar import Ui_frmFilter2dPolar
from ..icons import sysIcons
from .frmBase import frmBase


class frmFilter2dPolar(Ui_frmFilter2dPolar,frmBase):
    sigApply=QtCore.pyqtSignal(dict)
    sigClosed=QtCore.pyqtSignal()
  
    def __init__(self,parent=None,pointList:list=None):
        super(frmFilter2dPolar,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._pointList=pointList
        self._thetaValues=[]
        self._phiValues=[]
 
        
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.rdbTheta.clicked.connect(self.actionFilter)
        self.rdbPhi.clicked.connect(self.actionFilter)
        self.cbxValues.currentIndexChanged.connect(self.actionValueChanged)

        self.onLoad()  
    def onLoad(self):
        self.thetaPhiUnique()
        super().onLoad()
        pass
    def thetaPhiUnique(self):
        if not self._pointList:
            return
        self._thetaValues = sorted(set([p[0] for p in self._pointList]))
        self._phiValues = sorted(set([p[1] for p in self._pointList]))
        return self._thetaValues,self._phiValues
    def actionValueChanged(self):
        self.actionApply(tips=False)
    def actionFilter(self):
        try:
            if self.rdbTheta.isChecked():
                self.cbxValues.addItems([str(v) for v in self._thetaValues])
            elif self.rdbPhi.isChecked():
                self.cbxValues.addItems([str(v) for v in self._phiValues])
            else:
                QtWidgets.QMessageBox.about(self,"Error","请选择过滤类型")
            self.actionApply(tips=False)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.about(self,"Error","2dpolar数据设置错误,请重新选择"+str(e))
    def actionApply(self, tips=True):
        try:
            filterValue = self.cbxValues.currentText()
            if not filterValue:
                if(tips):
                    QtWidgets.QMessageBox.about(self,"Error","请选择切面值")
                return 
            filterType = 'theta' if self.rdbTheta.isChecked() else 'phi'
            if filterType == 'theta':
                filteredPoints = [p for p in self._pointList if str(p[0]) == filterValue]
            else:
                filteredPoints = [p for p in self._pointList if str(p[1]) == filterValue]
            if not filteredPoints:
                if tips:
                    QtWidgets.QMessageBox.about(self,"Error","没有找到符合条件的点")
    
                return
            self.sigApply.emit({
            'filterType': filterType,
            'filterValue': filterValue,
            'filteredPoints': filteredPoints})

            pass 
        except Exception as e:
            print(e)
            if tips:
                # 显示错误信息
                QtWidgets.QMessageBox.about(self,"Error","2dpolar数据设置错误,请重新选择"+str(e))
            else:
                # 仅打印错误信息
                print("2dpolar数据设置错误,请重新选择", e)
          
        pass
    def actionOK(self):
        self.actionApply()
        pass
    def closeEvent(self, a0):
        self.sigClosed.emit()
        return super().closeEvent(a0)   