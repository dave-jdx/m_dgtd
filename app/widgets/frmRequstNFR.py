from PyQt5 import QtCore,QtWidgets
from UI.ui_frmRequestNFR import Ui_frmNFR
from ..dataModel.nfr import NFR
from ..icons import sysIcons
class frmRequestNFR(Ui_frmNFR,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(NFR)
    sigModify=QtCore.pyqtSignal(NFR)
    def __init__(self,parent=None,mode:int=0,nfrObj:NFR=None):
        super(frmRequestNFR,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.mode=mode

        
        self.btnCreate.clicked.connect(self.btnCreateClick)
        self.btnAdd.clicked.connect(self.btnAddClick)
        self.btnClose.clicked.connect(self.close)
        
        self.onLoad(nfrObj)
        
        self.txtThe_start.textChanged.connect(self.setNum)
        self.txtThe_end.textChanged.connect(self.setNum)
        self.txtThe_inc.textChanged.connect(self.setNum)
        self.txtPhi_start.textChanged.connect(self.setNum)
        self.txtPhi_end.textChanged.connect(self.setNum)
        self.txtPhi_inc.textChanged.connect(self.setNum)


    def onLoad(self,nfrObj:NFR=None):
        baseTitle="NearField Radiation"
        titleMode="Request "
        str_btnCreate="Create"
        str_btnAdd="Add"
        str_btnClose="Close"
        if(self.mode==1):
            titleMode="Modify "
            str_btnCreate="OK"
            str_btnAdd="Apply"
            str_btnClose="Cancel"

        self.setWindowTitle(titleMode+baseTitle)

        self.btnCreate.setText(str_btnCreate)
        self.btnAdd.setText(str_btnAdd)
        self.btnClose.setText(str_btnClose)

        defaultV="0.0"

        self.txtPhi_start.setText(defaultV)
        self.txtPhi_end.setText(defaultV)
        self.txtPhi_inc.setText(defaultV)
        self.txtThe_start.setText(defaultV)
        self.txtThe_end.setText(defaultV)
        self.txtThe_inc.setText(defaultV)
        self.txtRadius.setText(defaultV)
        self.txtName.setText(NFR.titlePrefix+str(NFR.currentIndex))

        if(nfrObj!=None):
            self.txtPhi_start.setText(str(nfrObj.phiStart))
            self.txtPhi_end.setText(str(nfrObj.phiEnd))
            self.txtPhi_inc.setText(str(nfrObj.phiIncrement))
            self.txtThe_start.setText(str(nfrObj.theStart))
            self.txtThe_end.setText(str(nfrObj.theEnd))
            self.txtThe_inc.setText(str(nfrObj.theIncrement))
            self.txtRadius.setText(str(nfrObj.radius))
            self.txtName.setText(nfrObj.title)
            self.setNum()
        pass

    def btnCreateClick(self):
        try:
            if(self.mode==0):
                self.actionCreate()
            else:
                self.actionOK()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"NearField Radiation","请输入正确参数"+str(e))
        pass
    def btnAddClick(self):
        try:
            if(self.mode==0):
                self.actionAdd()
            else:
                self.actionApply()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"NearField Radiation","保存参数错误"+str(e))
        
        pass
    def actionCreate(self):
        nfrObj=self.getNFR()
        self.sigCreate.emit(nfrObj)
        pass
    def actionOK(self):
        nfrObj=self.getNFR()
        self.sigModify.emit(nfrObj)
        pass
    def actionAdd(self):
        nfrObj=self.getNFR()
        self.sigCreate.emit(nfrObj)
        self.onLoad()
        pass
    def actionApply(self):
        nfrObj=self.getNFR()
        self.sigModify.emit(nfrObj)
        pass
    def getNFR(self):
        nfrObj=NFR()
        nfrObj.phiStart=float(self.txtPhi_start.text())
        nfrObj.phiEnd=float(self.txtPhi_end.text())
        nfrObj.phiIncrement=float(self.txtPhi_inc.text())
        nfrObj.theStart=float(self.txtThe_start.text())
        nfrObj.theEnd=float(self.txtThe_end.text())
        nfrObj.theIncrement=float(self.txtThe_inc.text())
        nfrObj.radius=float(self.txtRadius.text())
        nfrObj.name=self.txtName.text()
        nfrObj.title=self.txtName.text()
        return nfrObj
        pass
    def setNum(self):
        try:
            obj=self.getNFR()
            self.txtThe_n.setText(str(int((obj.theEnd-obj.theStart)/obj.theIncrement)+1))
            self.txtPhi_n.setText(str(int((obj.phiEnd-obj.phiStart)/obj.phiIncrement)+1))
        except Exception as e:
            pass