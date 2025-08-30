from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmRotate import Ui_frmRotate
from ..dataModel.antenna import Antenna
from ..icons import sysIcons
from ..api import api_model
class frmAntennaSet(Ui_frmRotate,QtWidgets.QMainWindow):
    sigRotate=QtCore.pyqtSignal(tuple)
    sigScale=QtCore.pyqtSignal(float)
    sigAxisChange=QtCore.pyqtSignal(float,float)
    sigImport=QtCore.pyqtSignal()
    sigShowAxis=QtCore.pyqtSignal(bool)
    def __init__(self,parent=None,antennaObj:Antenna=None):
        super(frmAntennaSet,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self._antenna=antennaObj
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.onLoad()
        self.btnOK.clicked.connect(self.actionOK)
        self.btnApply.clicked.connect(self.actionApply)
        self.btnBrowse.clicked.connect(self.actionImport)
        self.chkShowAxis.clicked.connect(self.actionShowAxis)

        # self.txtPoint1_x.textChanged.connect(self.pointChanged)
        # self.txtPoint1_y.textChanged.connect(self.pointChanged)
        # self.txtPoint1_z.textChanged.connect(self.pointChanged)
        
    def onLoad(self):
        self.txtOrigin.setDisabled(True)
        self.txtAngel.setDisabled(True)

        if(self._antenna!=None):
            center=tuple(value / 1000 for value in self._antenna.center)
            self.txtOrigin.setText(str(center))

            angel=api_model.get_angel_xyz(self._antenna.center,
                                          self._antenna.normal_dir)
            self.txtAngel.setText(str(angel))
            self.txtRotate_x.setText(str(self._antenna.rotate_x))
            self.txtRotate_y.setText(str(self._antenna.rotate_y))
            self.txtRotate_z.setText(str(self._antenna.rotate_z))
            self.txtScale.setText(str(self._antenna.radio_scale))
            self.txtAxisLength.setText(str(self._antenna.axis_length_antenna))
            self.txtRadioFile.setText(self._antenna.file_antenna)
            if(hasattr(self._antenna,"axis_thickness_antenna")==False):
                self._antenna.axis_thickness_antenna=1
            self.txtThickness.setText(str(self._antenna.axis_thickness_antenna))
        
        
        pass
    def updateRadioFile(self,fname):
        self.txtRadioFile.setText(fname)
        pass
    def actionApply(self):
        try:
            p1_x=float(self.txtRotate_x.text())
            p1_y=float(self.txtRotate_y.text())
            p1_z=float(self.txtRotate_z.text())
            scale=float(self.txtScale.text())
            axis_length=float(self.txtAxisLength.text())
            axis_thickness=float(self.txtThickness.text())

            self.sigRotate.emit((p1_x,p1_y,p1_z))
            self.sigScale.emit(scale)
            self.sigAxisChange.emit(axis_length,axis_thickness)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"方向图旋转","x/y/z旋转角度必须是数字类型"+str(e))

        pass
    def pointChanged(self):
        return
        try:
            p1_x=float(self.txtPoint1_x.text())
            p1_y=float(self.txtPoint1_y.text())
            p1_z=float(self.txtPoint1_z.text())
            self.sigRotate.emit((p1_x,p1_y,p1_z))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"方向图旋转","x/y/z坐标必须是数字类型"+str(e))
        pass
    def actionOK(self):
        # self.actionApply()
        self.close()
        pass
    def actionImport(self):
        self.sigImport.emit()
        pass
    def actionShowAxis(self):
        showAxis=self.chkShowAxis.isChecked()
        self.sigShowAxis.emit(showAxis)
        pass
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # self.sigHideLine.emit()
        return super().closeEvent(a0)

            