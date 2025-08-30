from PyQt5 import QtCore,QtWidgets
from UI.ui_frmRequestFFR import Ui_frmFFR
from ..dataModel.ffr import FFR
from ..icons import sysIcons
class frmRequestFFR(Ui_frmFFR,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(FFR)
    sigModify=QtCore.pyqtSignal(FFR)
    def __init__(self,parent=None,mode:int=0,ffrObj:FFR=None):
        super(frmRequestFFR,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.mode=mode

        
        self.btnCreate.clicked.connect(self.btnCreateClick)
        self.btnAdd.clicked.connect(self.btnAddClick)
        self.btnClose.clicked.connect(self.close)
        
        
        self.onLoad(ffrObj)
        self.txtThe_start.textChanged.connect(self.setNum)
        self.txtThe_end.textChanged.connect(self.setNum)
        self.txtThe_inc.textChanged.connect(self.setNum)
        self.txtPhi_start.textChanged.connect(self.setNum)
        self.txtPhi_end.textChanged.connect(self.setNum)
        self.txtPhi_inc.textChanged.connect(self.setNum)

    def onLoad(self,ffrObj:FFR=None):
        baseTitle="FarField Radiation"
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
        self.txtThe_n.setText(defaultV)
        self.txtPhi_n.setText(defaultV)
        self.txtName.setText(FFR.titlePrefix+str(FFR.currentIndex))

        if(ffrObj!=None):
            self.txtPhi_start.setText(str(ffrObj.phiStart))
            self.txtPhi_end.setText(str(ffrObj.phiEnd))
            self.txtPhi_inc.setText(str(ffrObj.phiIncrement))
            self.txtThe_start.setText(str(ffrObj.theStart))
            self.txtThe_end.setText(str(ffrObj.theEnd))
            self.txtThe_inc.setText(str(ffrObj.theIncrement))
            
            self.txtName.setText(ffrObj.title)
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
            QtWidgets.QMessageBox.warning(self,"FarField Radiation","请输入正确参数"+str(e))
        pass

    def btnAddClick(self):
        try:
            if(self.mode==0):
                self.actionAdd()
            else:
                self.actionApply()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"FarField Radiation","请输入正确参数         ")
        pass

    def actionCreate(self):
        ffrObj=self.getFFR()
        self.sigCreate.emit(ffrObj)
        
        pass
    def actionOK(self):
        ffrObj=self.getFFR()
        self.sigModify.emit(ffrObj)
        pass
    def actionAdd(self):
        ffrObj=self.getFFR()
        self.sigCreate.emit(ffrObj)
        self.onLoad()#加载下一个添加界面
        pass
    def actionApply(self):
        ffrObj=self.getFFR()
        self.sigModify.emit(ffrObj)
        pass
    def getFFR(self):
        ffrObj=FFR()
        ffrObj.title=self.txtName.text()
        ffrObj.name=self.txtName.text()
        ffrObj.theStart=float(self.txtThe_start.text())
        ffrObj.theEnd=float(self.txtThe_end.text())
        ffrObj.theIncrement=float(self.txtThe_inc.text())
        ffrObj.phiStart=float(self.txtPhi_start.text())
        ffrObj.phiEnd=float(self.txtPhi_end.text())
        ffrObj.phiIncrement=float(self.txtPhi_inc.text())
        return ffrObj
    def setNum(self):
        try:
            ffrObj=self.getFFR()
            self.txtThe_n.setText(str(int((ffrObj.theEnd-ffrObj.theStart)/ffrObj.theIncrement)+1))
            self.txtPhi_n.setText(str(int((ffrObj.phiEnd-ffrObj.phiStart)/ffrObj.phiIncrement)+1))
        except Exception as e:
            pass
