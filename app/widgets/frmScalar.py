from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem,QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal,QSize,QStringListModel,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem,QFont,QIcon,QPixmap
from UI.ui_frmScalar import Ui_frmScalar
from typing import List,Tuple
from ..icons import sysIcons
class frmScalar(Ui_frmScalar,QtWidgets.QMainWindow):
    # sigShowLine=QtCore.pyqtSignal(tuple,tuple)
    # sigHideLine=QtCore.pyqtSignal()
    sigSetRange=QtCore.pyqtSignal(float,float,int)#根据设置的range显示颜色范围
    sigRangeAuto=QtCore.pyqtSignal(int)#自动根据数值范围显示
    def __init__(self,parent=None,minV=0,maxV=0,numberOfColors:int=256):
        super(frmScalar,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)

        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._minV=minV
        self._maxV=maxV
        self._numberOfColors=numberOfColors
        
        self.onLoad()
        self.btnCancel.clicked.connect(self.close)
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.rdbFixed.toggled.connect(self.onFixedChanged)
        
    def onLoad(self):
        self.txtMax.setText(str(self._maxV))
        self.txtMin.setText(str(self._minV))
        self.txtNumOfColors.setText(str(self._numberOfColors))
        self.rdbAuto.setChecked(True)
        self.groupBox.setStyleSheet("QGroupBox:title{left:5px}")
        pass
    def onFixedChanged(self):
        if(self.rdbFixed.isChecked()):
            self.txtMax.setEnabled(True)
            self.txtMin.setEnabled(True)
        else:
            self.txtMax.setEnabled(False)
            self.txtMin.setEnabled(False)

    def actionApply(self):
        try:
           nColors=int(self.txtNumOfColors.text())
           if(self.rdbFixed.isChecked()):
                min=float(self.txtMin.text())
                max=float(self.txtMax.text())
                if(min>=max):
                    QtWidgets.QMessageBox.warning(self,"值范围","最大值必须大于最小值")
                    return False
                self.sigSetRange.emit(min,max,nColors)
           else:
               self.sigRangeAuto.emit(nColors)
           return True
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Range","值需要是浮点数，请核对"+str(e))
            return False
            # QtWidgets.QMessageBox.warning(self,"Mesh size","设置尺寸错误，尺寸必须是正数"+str(e))
        pass
    def actionOK(self):
        if(self.actionApply()):
            self.close()
        pass



            