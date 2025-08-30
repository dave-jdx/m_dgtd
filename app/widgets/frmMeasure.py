from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmMeasure import Ui_frmMeasure
from ..icons import sysIcons
class frmMeasure(Ui_frmMeasure,QtWidgets.QMainWindow):
    sigShowLine=QtCore.pyqtSignal(tuple,tuple)
    sigHideLine=QtCore.pyqtSignal()
    def __init__(self,parent=None):
        super(frmMeasure,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.onLoad()
        self.btnClose.clicked.connect(self.close)
        self.txtPoint1_x.textChanged.connect(self.pointChanged)
        self.txtPoint1_y.textChanged.connect(self.pointChanged)
        self.txtPoint1_z.textChanged.connect(self.pointChanged)
        self.txtPoint2_x.textChanged.connect(self.pointChanged)
        self.txtPoint2_y.textChanged.connect(self.pointChanged)
        self.txtPoint2_z.textChanged.connect(self.pointChanged)
        
    def onLoad(self):
        self.txtPoint1_x.setText("0.0")
        self.txtPoint1_y.setText("0.0")
        self.txtPoint1_z.setText("0.0")
        self.txtPoint2_x.setText("0.0")
        self.txtPoint2_y.setText("0.0")
        self.txtPoint2_z.setText("0.0")

        pass
    def pointChanged(self):
        try:
            p1_x=float(self.txtPoint1_x.text())
            p1_y=float(self.txtPoint1_y.text())
            p1_z=float(self.txtPoint1_z.text())
            p2_x=float(self.txtPoint2_x.text())
            p2_y=float(self.txtPoint2_y.text())
            p2_z=float(self.txtPoint2_z.text())
            self.sigShowLine.emit((p1_x,p1_y,p1_z),(p2_x,p2_y,p2_z))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"点测量","x/y/z坐标必须是数字类型"+str(e))
        pass
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.sigHideLine.emit()
        return super().closeEvent(a0)

            