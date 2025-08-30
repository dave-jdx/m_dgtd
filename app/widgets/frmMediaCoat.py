from PyQt5 import QtCore,QtWidgets
from UI.ui_frmMediaCoat import Ui_frmMediaCoat
from ..dataModel.mediaN import MediaBase
from ..icons import sysIcons
from .baseStyle import baseStyle
class frmMediaCoat(Ui_frmMediaCoat,QtWidgets.QMainWindow):
    sigApplyMediaCoat=QtCore.pyqtSignal(object,float)
    sigChooseMeidaCoat=QtCore.pyqtSignal()
    def __init__(self,parent=None,mediaName:str="",thickness:float=0):
        super(frmMediaCoat,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        
        self._medaiName=mediaName
        self._thickness=thickness
        self._media=None
        self.onLoad()
        self.btnClose.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnClear.clicked.connect(self.actionClear)
        self.btnChoose.clicked.connect(self.actionChooseMediaCoat)

    def onLoad(self):
        self.txtMediaName.setText(self._medaiName)
        self.txtThickness.setText(str(self._thickness))
    def actionOK(self):

        try:
            self.sigApplyMediaCoat.emit(self._media,float(self.txtThickness.text()))
            self.close()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self,"涂覆材料","请检查数据"+str(ex))
    def actionClear(self):
        self.txtMediaName.setText("")
        self.txtThickness.setText("0")
        self._media=None
    def actionChooseMediaCoat(self):
        self.sigChooseMeidaCoat.emit()
    def setMedia(self,media:MediaBase):
        self._media=media
        self.txtMediaName.setText(media.name)


        
