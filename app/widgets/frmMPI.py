from PyQt5 import QtCore,QtWidgets
from UI.ui_frmMPI import Ui_frmMPI
from ..icons import sysIcons
from .frmBase import frmBase
class frmMPI(Ui_frmMPI,frmBase):
    sigMPISet=QtCore.pyqtSignal(int,str)
    sigMPIRegister=QtCore.pyqtSignal()
    sigMPITest=QtCore.pyqtSignal()
    def __init__(self,parent=None,mpiNum:int=2,installPath=None):
        super(frmMPI,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.btnOKClick)
        # self.btnRegister.clicked.connect(self.btnRegisterClick)
        # self.btnTest.clicked.connect(self.btnTestClick)
        # self.btnBrowse.clicked.connect(self.btnBrowsePathClick)
        self.mpiNum=mpiNum
        self.installPath=installPath
        self.onLoad()
        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)

    def onLoad(self):
        super().onLoad()
        self.txtMPINum.setText(str(self.mpiNum))
        # self.txtInstallPath.setText(str(self.installPath))
        # if(self.power!=None):
        #     self.txtPower.setText(str(self.power.sourcePower))
        pass
    def btnOKClick(self):
        str_mpi=self.txtMPINum.text()
        # str_installPath=self.txtInstallPath.text()
        if(str_mpi==""):
            QtWidgets.QMessageBox.warning(self,"mpi process number","请输入进程数（正整数)")
            return
        try:
            mpiNum=int(str_mpi)
            self.sigMPISet.emit(mpiNum,"")
            self.close()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self,"并行进程数","请输正整数")
    def btnRegisterClick(self):
        self.sigMPIRegister.emit()
        pass
    def btnTestClick(self):
        self.sigMPITest.emit()
        pass
    def btnBrowsePathClick(self):
        installPath = QtWidgets.QFileDialog.getExistingDirectory(self,"选择MPI安装路径")
        if(installPath=="" or installPath is None):
            return
        self.txtInstallPath.setText(installPath)
        self.installPath=installPath
        pass

        
