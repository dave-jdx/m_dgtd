from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmMediaIsotropic import Ui_frmMediaIsotropic
from ..icons import sysIcons

from ..dataModel.mediaN import Isotropic
from ..api import api_writer
import uuid
from .baseStyle import baseStyle
ROW_HEIGHT=30
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmMediaIsotropic(Ui_frmMediaIsotropic,QtWidgets.QMainWindow):
    sigApplyIsotropic=QtCore.pyqtSignal(Isotropic,int)
  
    def __init__(self,parent=None,media:Isotropic=None,rowIndex:int=-1):
        super(frmMediaIsotropic,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._isotropic=media  
        self._rowIndex=rowIndex

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnClose.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.actionOK)

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)

        self.onLoad()  
        
        

    def onLoad(self):
        if(self._isotropic is not None):
            self.txtMediaName.setText(self._isotropic.name)
            self.txtPermittivity.setText(str(self._isotropic.permittivity))
            self.txtPermeability.setText(str(self._isotropic.permeability))
            self.txtEConductivity.setText(str(self._isotropic.eConductivity))
            self.txtTConductivity.setText(str(self._isotropic.tConductivity))
            self.txtDensity.setText(str(self._isotropic.density))
            self.txtSpecificHeat.setText(str(self._isotropic.specificHeat))
            self.txtYoungModulus.setText(str(self._isotropic.youngModulus))
            self.txtPoissonRatio.setText(str(self._isotropic.poissonRatio))
            self.txtThermalExpansion.setText(str(self._isotropic.thermalExpansion))

        pass
    
 


    def getMediaItem(self):
        try:
            media_isotropic=Isotropic()
            media_isotropic.name=self.txtMediaName.text()
            v1=float(self.txtPermittivity.text())
            v2=float(self.txtPermeability.text())
            v3=float(self.txtEConductivity.text())
            v4=float(self.txtTConductivity.text())
            v5=float(self.txtDensity.text())
            v6=float(self.txtSpecificHeat.text())
            v7=float(self.txtYoungModulus.text())
            v8=float(self.txtPoissonRatio.text())
            v9=float(self.txtThermalExpansion.text())

            media_isotropic.permittivity=self.txtPermittivity.text()
            media_isotropic.permeability=self.txtPermeability.text()
            media_isotropic.eConductivity=self.txtEConductivity.text()
            media_isotropic.tConductivity=self.txtTConductivity.text()
            media_isotropic.density=self.txtDensity.text()
            media_isotropic.specificHeat=self.txtSpecificHeat.text()
            media_isotropic.youngModulus=self.txtYoungModulus.text()
            media_isotropic.poissonRatio=self.txtPoissonRatio.text()
            media_isotropic.thermalExpansion=self.txtThermalExpansion.text()
            

            if(media_isotropic.name==""):
                return(-1,"材料名称不能为空",None)
            return (1,"success",media_isotropic)
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"media input error","please input float value"+str(e))
            return(-1,"参数值必须是数字，请检查并修改\n"+str(e),None)

    def actionOK(self):
        code,message,mediaData=self.getMediaItem()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"材料数据错误",message)
            return
        self.sigApplyIsotropic.emit(mediaData,self._rowIndex)
        self.close()

    def closeEvent(self, event):
        return super().closeEvent(event)
