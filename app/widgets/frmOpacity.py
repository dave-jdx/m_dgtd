import os
from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmOpacity import Ui_frmOpacity
from ..icons import sysIcons
from .frmBase import frmBase
SPEED=3e+8
class frmOpacity(Ui_frmOpacity,frmBase):
    sigModify=QtCore.pyqtSignal(float,float)
    def __init__(self,parent=None,opacity=0,opacityMap=0):
        self.parent=parent
        super(frmOpacity,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.btnOKClicked)
        self.btnApply.clicked.connect(self.actionApply)
        self.txtMaxSize.setText(str(opacity))
        self.txtOpacityMap.setText(str(opacityMap))
        self.onLoad()

    def onLoad(self):
        super().onLoad()
        self.gbxOpacity.setStyleSheet("QGroupBox:title{left:5px;height:25px}")
        pass
    def actionApply(self):
        try:
            opacity=float(self.txtMaxSize.text())
            if(opacity<0 or opacity>1):
                raise Exception("请输入正确的浮点数0-1")
            opacityMap=float(self.txtOpacityMap.text())
            if(opacityMap<0 or opacityMap>1):
                raise Exception("请输入正确的浮点数0-1")
            self.sigModify.emit(opacity,opacityMap)
            return(1,"sucess")
    
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"设置","请输入正确的浮点数0-1")
            self.txtMaxSize.setText("0")
            self.txtOpacityMap.setText("0")
            return(-1,"failed")


    def btnOKClicked(self):
        code,message=self.actionApply()
        if(code==1):
            self.close()
        pass

