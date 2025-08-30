from PyQt5 import QtCore,QtWidgets
from UI.ui_frmVoltageSource import Ui_frmVoltageSource
from ..dataModel.source import Source
from ..dataModel.port import Port
from ..icons import sysIcons
class frmVoltageSource(Ui_frmVoltageSource,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(Source)
    sigModify=QtCore.pyqtSignal(Source)
    def __init__(self,parent=None,mode:int=0,sourceObj:Source=None,portList=None):
        super(frmVoltageSource,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.mode=mode
        self.portList:list[Port]=portList

        self.btnCreate.clicked.connect(self.btnCreateClick)
        self.btnAdd.clicked.connect(self.btnAddClick)
        self.btnClose.clicked.connect(self.close)
        self.onLoad(sourceObj)

    def onLoad(self,sourceObj:Source=None):#加载时初始化参数
        self.cbxPort.clear()
        baseTitle=" voltage source"
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

        self.txtSourceName.setText(Source.titlePrefix+str(Source.currentIndex))

        self.txtMagnitude.setText(None)
        self.txtPhase.setText(None)
        self.txtImpedence.setText(None)

        if(sourceObj!=None):
            self.txtMagnitude.setText(str(sourceObj.magnitude))
            self.txtPhase.setText(str(sourceObj.phase))
            self.txtImpedence.setText(str(sourceObj.impedence))
            self.txtSourceName.setText(str(sourceObj.title))
            #port索引值匹配
            for port in self.portList:
                if port.name==sourceObj.port.name:
                    self.cbxPort.setCurrentIndex(self.portList.index(port))
                    break
        

    def btnCreateClick(self):
        try:
            if(self.mode==0):
                self.actionCreate()
            else:
                self.actionOK()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"source","请输入正确参数")
    def btnAddClick(self):
        try:
            if(self.mode==0):
                self.actionAdd()
            else:
                self.actionApply()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"source","请输入正确参数")
        
        pass
    def actionCreate(self):
        sourceObj=self.getSource()
        self.sigCreate.emit(sourceObj)
        # print("click create")
        pass
    def actionOK(self):
        sourceObj=self.getSource()
        self.sigModify.emit(sourceObj)
        pass
    def actionAdd(self):
        sourceObj=self.getSource()
        self.sigCreate.emit(sourceObj)
        self.onLoad()
        # print("click add")
    def actionApply(self):
        sourceObj=self.getSource()
        self.sigModify.emit(sourceObj)
        # print("click apply")
    def getSource(self):
        sourceObj=Source()
        sourceObj.title=self.txtSourceName.text()
        sourceObj.name=self.txtSourceName.text()
        sourceObj.port=self.cbxPort.itemData(self.cbxPort.currentIndex())
        sourceObj.magnitude=int(self.txtMagnitude.text())
        sourceObj.phase=int(self.txtPhase.text())
        sourceObj.impedence=int(self.txtImpedence.text())
        return sourceObj



