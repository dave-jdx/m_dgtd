from PyQt5 import QtCore,QtWidgets
from UI.ui_frmCreateLoad import Ui_frmLoad
from ..dataModel.load import Load
from ..dataModel.port import Port
from ..icons import sysIcons
class frmLoad(Ui_frmLoad,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(Load)
    sigModify=QtCore.pyqtSignal(Load)
    def __init__(self,parent=None,mode:int=0,loadObj:Load=None,portList=None):
        self.parent=parent
        super(frmLoad,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.mode=mode
        self.portList:list[Port]=portList

        
        self.btnCreate.clicked.connect(self.btnCreateClick)
        self.btnAdd.clicked.connect(self.btnAddClick)
        self.btnClose.clicked.connect(self.close)

        self.onLoad(loadObj)

    def onLoad(self,loadObj:Load=None):
        self.cbxPort.clear()
        baseTitle=" load"
        titleMode="Create"
        str_btnCreate="Create"
        str_btnAdd="Add"
        str_btnClose="Close"
        if(self.mode==1):
            titleMode="Modify"
            str_btnCreate="OK"
            str_btnAdd="Apply"
            str_btnClose="Cancel"

        if(self.portList!=None and len(self.portList)>0):
            for port in self.portList:
                self.cbxPort.addItem(port.title,port)

        self.setWindowTitle(titleMode+baseTitle)
        self.btnCreate.setText(str_btnCreate)
        self.btnAdd.setText(str_btnAdd)
        self.btnClose.setText(str_btnClose)
        
        self.txtReceive.setText(None)
        self.txtReal.setText(None)
        self.txtImag.setText(None)
        self.txtLoadName.setText(Load.titlePrefix+str(Load.currentIndex))
            
        if(loadObj!=None):
            self.txtReceive.setText(str(loadObj.receive))
            self.txtReal.setText(str(loadObj.real))
            self.txtImag.setText(str(loadObj.imaginary))
            self.txtLoadName.setText(str(loadObj.title))
            for port in self.portList:
                if port.name==loadObj.port.name:
                    self.cbxPort.setCurrentIndex(self.portList.index(port))
                    break
            
        pass
    def btnCreateClick(self):
        try:
            if(self.mode==0):
                self.actionCreate()
            else:
                self.actionOK()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Load settings","请输入正确参数         ")
        pass
    def btnAddClick(self):
        try:
            if(self.mode==0):
                self.actionAdd()
            else:
                self.actionApply()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Load settings","请输入正确参数         ")
        pass
    def actionCreate(self):
        loadObj=self.getLoad()
        self.sigCreate.emit(loadObj)
        pass
    def actionOK(self):
        loadObj=self.getLoad()
        self.sigModify.emit(loadObj)
        pass
    def actionAdd(self):
        loadObj=self.getLoad()
        self.sigCreate.emit(loadObj)
        self.onLoad()
        pass
    def actionApply(self):
        loadObj=self.getLoad()
        self.sigModify.emit(loadObj)
        pass
    def getLoad(self):
        loadObj=Load()
        loadObj.name=self.txtLoadName.text()
        loadObj.title=self.txtLoadName.text()
        loadObj.receive=int(self.txtReceive.text())
        loadObj.real=int(self.txtReal.text())
        loadObj.imaginary=int(self.txtImag.text())
        loadObj.port=self.cbxPort.itemData(self.cbxPort.currentIndex())
        return loadObj
        pass