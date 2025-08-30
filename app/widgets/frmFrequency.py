from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmFrequency import Ui_frmFrequency
from ..dataModel.frequency import Frequency
from ..icons import sysIcons
class frmFrequency(Ui_frmFrequency,QtWidgets.QMainWindow):
    sigModify=QtCore.pyqtSignal(Frequency)
    def __init__(self,parent=None,freqObj:Frequency=None):
        super(frmFrequency,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.btnOKClick)
        self.start=None
        self.end=None
        self.increment=None
        self.frequency=freqObj
        self.onLoad()
    def onLoad(self):
        if(self.frequency!=None):
            self.txtStart.setText(str(self.frequency.start))
            self.txtEnd.setText(str(self.frequency.end))
            self.txtIncrement.setText(str(self.frequency.increment))
        self.txtStart.setFocus()
            
    def btnOKClick(self):
        freqObj=self.getFrequency()
        if(freqObj!=None):
            self.sigModify.emit(freqObj)
            self.close()
    def getFrequency(self):
        freqObj=Frequency()
        str_start=self.txtStart.text()
        str_end=self.txtEnd.text()
        str_increment=self.txtIncrement.text()
        if(str_start==""):
            QtWidgets.QMessageBox.warning(self,"频率","请输入起始频率")
            return None
        if(str_end==""):
            QtWidgets.QMessageBox.warning(self,"频率","请输入截止频率")
            return None
        if(str_increment==""):
            QtWidgets.QMessageBox.warning(self,"频率","请输入频率步进值")
            return None
        try:
            start=float(str_start)
            end=float(str_end)
            fincrement=float(str_increment)
            freqObj.start=str_start
            freqObj.end=str_end
            freqObj.increment=str_increment
            return freqObj
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"频率","起始频率/截止频率/步进值必须是有效数字"+str(e))
            return None

        


            


    