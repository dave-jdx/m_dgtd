from PyQt5 import QtCore,QtWidgets
from UI.ui_widgetFilter import Ui_filterWidget
from ..dataModel.power import Power
from ..icons import sysIcons
class wFilter(Ui_filterWidget,QtWidgets.QMainWindow):
    sigFilter=QtCore.pyqtSignal(list,int)#pointList,面索引，分量索引
    def __init__(self,parent=None,nfList=None):
        super(wFilter,self).__init__(parent)
        self.setupUi(self)
        self.parent=parent
        #隐藏标题栏
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.onLoad()
  
    def onLoad(self):

        pass

               

        
