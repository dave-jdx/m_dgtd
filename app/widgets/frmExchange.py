from PyQt5 import QtCore,QtWidgets
from UI.ui_frmExchange import Ui_frmExchange
from ..dataModel.model import Model
from ..icons import sysIcons

class frmExchange(Ui_frmExchange,QtWidgets.QMainWindow):
    sigFormatExchange=QtCore.pyqtSignal(str,str)#自动根据数值范围显示
    def __init__(self,parent=None):
        super(frmExchange,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnClose.clicked.connect(self.close)
        self.btnBrowseSource.clicked.connect(self.browseSource)
        self.btnBrowseTarget.clicked.connect(self.browseTarget)
        self.btnOK.clicked.connect(self.btnOKClick)
        # self.power=powerObj
        self.onLoad()

    def onLoad(self):
        pass
    def btnOKClick(self):
        source=self.txtSourceFile.text()
        target=self.txtTargetFile.text()
        if(source!=None and target!=None):
            self.sigFormatExchange.emit(source,target)
        else:
            QtWidgets.QMessageBox.warning(self,"Exchange","请选择源文件并输入目标文件名")
            pass
        pass
    def browseSource(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(filter=Model.exchangeExtension)
        if(fname=="" or fname is None):
            return
        self.txtSourceFile.setText(fname)
        pass
    def browseTarget(self):
        fname,_ = QtWidgets.QFileDialog.getSaveFileName(filter=Model.exchangeExtension)
        if(fname=="" or fname is None):
            return
        self.txtTargetFile.setText(fname)
        pass

        
