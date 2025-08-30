from PyQt5 import QtCore,QtWidgets
from UI.ui_frmPower import Ui_frmPower
from ..dataModel.power import Power
from ..icons import sysIcons
class frmPower(QtWidgets.QMainWindow,Ui_frmPower):
    sigModifyPower=QtCore.pyqtSignal(Power)
    def __init__(self,parent=None,powerObj:Power=None):
        super(frmPower,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.btnOKClick)
        self.power=powerObj
        self.onLoad()

    def onLoad(self):
        if(self.power!=None):
            self.txtPower.setText(str(self.power.sourcePower))
    def btnOKClick(self):
        str_power=self.txtPower.text()
        if(str_power==""):
            QtWidgets.QMessageBox.warning(self,"power","请输入功率值（正整数)")
            return
        try:
            powerObj=Power()
            powerObj.sourcePower=int(str_power)
            if(powerObj.sourcePower)<=0:
                raise TypeError
            self.sigModifyPower.emit(powerObj)
            self.close()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self,"频率","请输正整数")

        
