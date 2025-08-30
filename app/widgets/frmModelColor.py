
from PyQt5 import QtCore, QtWidgets
from UI.ui_frmModelColor import Ui_frmModelColor
from ..dataModel.model import Model
from ..dataModel.modelColor import ModelColor
from ..icons import sysIcons
from PyQt5.QtGui import QColor
from .baseStyle import baseStyle


class frmModelColor(Ui_frmModelColor, QtWidgets.QMainWindow):
    sigSetModelColor=QtCore.pyqtSignal(ModelColor)#颜色对象
    def __init__(self, parent=None,modelColor:ModelColor=None):
        super(frmModelColor, self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent = parent
        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self._modelColor=modelColor
        self.onLoad()

        self.btnClose.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnApply.clicked.connect(self.actionApply)
        self.btnColorBackground.clicked.connect(self.colorBackground)
        self.btnColorModel.clicked.connect(self.colorModel)
        self.cbxColorType.currentIndexChanged.connect(self.colorTypeChanged)
        # self.btnOK.clicked.connect(self.btnOKClick)
        # self.power=powerObj
        

    def onLoad(self):

        self.groupBox1.setFont(self._font)
        self.groupBox2.setFont(self._font) 
        self.groupBox1.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupBox2.setStyleSheet("QGroupBox:title{left:5px}")
        self.initModelColor()

        pass
    def initModelColor(self):
        self.cbxColorType.setCurrentIndex(self._modelColor.colorType)
        if(self._modelColor.colorType==0):
            self.initColor(self._modelColor.color_model_background,self._modelColor.color_model_foreground)
            self.groupBox1.setTitle("背景颜色")
            self.groupBox2.setTitle("模型颜色")
        elif(self._modelColor.colorType==1):
            self.initColor(self._modelColor.color_normal_outside,self._modelColor.color_normal_inside)
            self.groupBox1.setTitle("法线向外颜色")
            self.groupBox2.setTitle("法线向内颜色")
    def initColor(self,color1:tuple,color2:tuple):
        backColor=QColor()
        backColor.setRed(color1[0])
        backColor.setGreen(color1[1])
        backColor.setBlue(color1[2])
        self.lblColorBack.setStyleSheet("background-color: {};".format(backColor.name()))
        self.txtRed_background.setText(str(backColor.red()))
        self.txtGreen_background.setText(str(backColor.green()))
        self.txtBlue_background.setText(str(backColor.blue()))

        modelColor=QColor()
        modelColor.setRed(color2[0])
        modelColor.setGreen(color2[1])
        modelColor.setBlue(color2[2])
        self.lblColorModel.setStyleSheet("background-color: {};".format(modelColor.name()))
        self.txtRed_model.setText(str(modelColor.red()))
        self.txtGreen_model.setText(str(modelColor.green()))
        self.txtBlue_model.setText(str(modelColor.blue()))
        pass

    def actionOK(self):
        self.actionApply()
        self.close()
        pass

    def actionApply(self):
        try:
            self.sigSetModelColor.emit(self._modelColor)
            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "错误", "颜色设置错误："+str(e))
            pass
        pass

    def colorBackground(self):
        color_dialog = QtWidgets.QColorDialog(self)
        
        # color_dialog.show()
       
        color: QColor = color_dialog.getColor()
        if(not color.isValid()):
            return
        self.txtRed_background.setText(str(color.red()))
        self.txtGreen_background.setText(str(color.green()))
        self.txtBlue_background.setText(str(color.blue()))
        self.lblColorBack.setStyleSheet("background-color: {};".format(color.name()))
        if(self._modelColor.colorType==0):
            self._modelColor.color_model_background=(color.red(),color.green(),color.blue())
        else:
            self._modelColor.color_normal_outside=(color.red(),color.green(),color.blue())
        pass

    def colorModel(self):
        color_dialog = QtWidgets.QColorDialog(self)
    
        # color_dialog.show()
        color: QColor = color_dialog.getColor()
        if(not color.isValid()):
            return
        
        self.txtRed_model.setText(str(color.red()))
        self.txtGreen_model.setText(str(color.green()))
        self.txtBlue_model.setText(str(color.blue()))
        self.lblColorModel.setStyleSheet("background-color: {};".format(color.name()))
        if(self._modelColor.colorType==0):
            self._modelColor.color_model_foreground=(color.red(),color.green(),color.blue())
        else:
            self._modelColor.color_normal_inside=(color.red(),color.green(),color.blue())
        pass
    def colorTypeChanged(self):
        self._modelColor.colorType=self.cbxColorType.currentIndex() 
        self.initModelColor()
