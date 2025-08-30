import os
from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmMeshSize import Ui_frmMeshSize
from ..icons import sysIcons
from .frmBase import frmBase
SPEED=3e+8
class frmMeshSize(Ui_frmMeshSize,frmBase):
    # sigCreate=QtCore.pyqtSignal(float)
    sigMeshLocalSize=QtCore.pyqtSignal(int,float,bool)
    def __init__(self,parent=None,solidId=-1,maxh=0.1,used=False):
        self.parent=parent
        super(frmMeshSize,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.actionOK)
        self._solidId=solidId
        self.maxh=maxh
        self.txtMaxSize.setText(str(maxh))
        self.chk_used.setChecked(used)  
        self.onLoad()

    def onLoad(self):
        super().onLoad()
        pass
    def setMaxSize(self):
        txt=self.txtMaxSize.text()
        if(txt==""):
            return
        maxh=0
        try:
            maxh=float(txt)
            self.maxh=maxh
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"网格参数","请输入正确的浮点数")
            self.txtMaxSize.setText("0")
        pass

    def setMaxh(self):
        '''根据频率设置网格尺寸
        '''
        sizeType=3
        maxh=3
    
        maxh=float(self.txtMaxSize.text())
        self.maxh=maxh


    def actionOK(self):
        self.setMaxh()
        self.sigMeshLocalSize.emit(self._solidId,self.maxh,self.chk_used.isChecked())
        self.close()
        pass

