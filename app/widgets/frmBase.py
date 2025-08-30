from PyQt5 import QtCore,QtWidgets
from ..icons import sysIcons
from .baseStyle import baseStyle
class frmBase(QtWidgets.QMainWindow):
    def __init__(self,parent=None,):
        super(frmBase,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
    
       
    def onLoad(self):
        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)


        
        

   
        
