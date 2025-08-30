from PyQt5 import QtCore,QtWidgets
from UI.ui_frmModelMedia import Ui_frmModelMedia
from ..dataModel.media import Media
from ..icons import sysIcons
class frmModelMedia(QtWidgets.QMainWindow,Ui_frmModelMedia):
    # sigModifyPower=QtCore.pyqtSignal(Power)
    def __init__(self,parent=None):
        super(frmModelMedia,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
     
        self.onLoad()

    def onLoad(self):
        pass

