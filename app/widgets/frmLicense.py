import sys
from PyQt5 import QtCore, QtGui,QtWidgets
from UI.ui_frmLicense import Ui_frmLicense
from ..dataModel.project import Project
from ..api import api_license
from ..icons import sysIcons
class frmLicense(Ui_frmLicense,QtWidgets.QMainWindow,):
    def __init__(self,parent=None,):
        super(frmLicense,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnRegister.clicked.connect(self.btnRegisterClick)
        self.btnBrowser.clicked.connect(self.btnBrowseClick)
        self.onLoad()

    def onLoad(self):
        hardId=api_license.get_hardId()
        self.txtPower.setText(hardId)
    def btnRegisterClick(self):
        licenseCode=api_license.readLicenseCode(self.txtLicense.text())
        code,message=api_license.validate_license(licenseCode)
        if(code==1):
            code,message=api_license.register(licenseCode)
            if(code==1):
                QtWidgets.QMessageBox.information(self,"license","license register success")
                self.close()
            else:
                QtWidgets.QMessageBox.warning(self,"license",message)
        else:
            QtWidgets.QMessageBox.warning(self,"license",message)
        pass
        # str_power=self.txtPower.text()
        # if(str_power==""):
        #     QtWidgets.QMessageBox.warning(self,"power","请输入功率值（正整数)")
        #     return
        # try:
        #     powerObj=Power()
        #     powerObj.sourcePower=int(str_power)
        #     if(powerObj.sourcePower)<=0:
        #         raise TypeError
        #     self.sigModifyPower.emit(powerObj)
        #     self.close()
        # except Exception as ex:
        #     QtWidgets.QMessageBox.warning(self,"频率","请输正整数")

    def btnBrowseClick(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(filter=Project.licenseExtension)
        if(fname=="" or fname is None):
            return
        self.txtLicense.setText(fname)
    def closeEvent(self, event) -> None:
        code,message=api_license.license_validated()
        if(code!=1):
            self.parent.close()
            sys.exit(0)
        return super().closeEvent(event)
