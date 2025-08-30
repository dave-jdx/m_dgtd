import os
from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmCreateMesh import Ui_frmCreateMesh
from ..icons import sysIcons
SPEED=3e+8
class frmCreateMesh(Ui_frmCreateMesh,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(float)
    def __init__(self,parent=None,maxF:float=10e+9):
        self.parent=parent
        super(frmCreateMesh,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.cbxSizeType.currentIndexChanged.connect(self.selectChange)
        self.btnMesh.clicked.connect(self.btnMeshClicked)
        self.txtMaxSize.setText("20")
        self.txtMinSize.setText("0")
        self.txtGrading.setText("0.3")
        self.txtMaxSize.textChanged.connect(self.setMaxSize)

        self.maxh=3
        self.maxF=maxF #设置的最大频率值
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
    def selectChange(self):
        self.setMaxh()
        if(self.cbxSizeType.currentIndex()==self.cbxSizeType.count()-1):
            self.txtMaxSize.setEnabled(True)
            # self.txtMinSize.setEnabled(True)
            # self.txtGrading.setEnabled(True)
            self.txtMaxSize.setFocus()
        else:
            self.txtMaxSize.setEnabled(False)
            # self.txtMinSize.setEnabled(False)
            # self.txtGrading.setEnabled(False)  
        pass
    def setMaxh(self):
        '''根据频率设置网格尺寸
        '''
        sizeType=self.cbxSizeType.currentIndex()
        maxh=3
        w= 1000*(SPEED/self.maxF) #计算波长
        if(sizeType==0):#1/16波长-最大频率
            maxh=round(w/16,1)
            # maxh=2.3
        if(sizeType==1):#1/12波长
            maxh=round(w/12,1)
            # maxh=2.9
        if(sizeType==2):#1/8波长
            maxh=round(w/8,1)
            # maxh=3.8
        if(sizeType==3):
            maxh=float(self.txtMaxSize.text())
        self.maxh=maxh

    def btnMeshClicked(self):
        self.setMaxh()
        self.sigCreate.emit(self.maxh)
        self.close()
        pass

