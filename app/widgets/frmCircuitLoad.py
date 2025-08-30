from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmCircuitLoad import Ui_frmCIrcuitLoad
from ..icons import sysIcons
from .baseStyle import baseStyle
from .frmBase import frmBase

class frmCircuitLoad(Ui_frmCIrcuitLoad,frmBase):
    sigFaceSelected=QtCore.pyqtSignal(int,float,tuple,int)
    sigClosed=QtCore.pyqtSignal()
    sigSelectFace=QtCore.pyqtSignal(int)    
  
    def __init__(self,parent=None,loadObj:tuple=None):
        super(frmCircuitLoad,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent   
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self._u_length=0
        self._v_length=0
        self._isManual=False
        # self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.txtFaceId.textChanged.connect(self.selectIdChanged)
        self.btnExchange.clicked.connect(self.actionExcgange)
        self._loadObj=loadObj
        if(loadObj!=None):
            self.txtFaceId.setText(str(loadObj[0]+1))
            v_load=loadObj[1][0]
            v_uv=loadObj[1][1]
            self._u_length=v_uv[0]
            self._v_length=v_uv[1]
        
            # self.txtLengthUV.setText(f"({v_uv[0]/1000},{v_uv[1]/1000})")
            self.setUVText(v_uv[0],v_uv[1])
            self.txtLoad.setText(str(v_load))

        self.onLoad()  
    def onLoad(self):
        self.txtLengthUV.setEnabled(False)
        super().onLoad()
        self._isManual=True
        pass
    def actionApply(self):
        try:
            faceId_old=-1
            if(self._loadObj!=None):
                faceId_old=self._loadObj[0]
            faceId=int(self.txtFaceId.text())-1
            loadValue=float(self.txtLoad.text())
            self.sigFaceSelected.emit(faceId,loadValue,(self._u_length,self._v_length),faceId_old)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号/电阻不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
    def sig_chooseFace(self,faceId:int):
        self._isManual=False
        self.txtFaceId.setText(str(faceId+1))
        self._isManual=True
        pass
    def sig_chooseFaceLength(self,u_length:float,v_length:float):
        self._u_length=u_length
        self._v_length=v_length
        # self.txtLengthUV.setText(f"({u_length/1000},{v_length/1000})")
        self.setUVText(u_length,v_length)
        
        pass
    def selectIdChanged(self):
        try:
            if(not self._isManual):
                return
            if(self.txtFaceId.text()==""):
                return
            selectId=int(self.txtFaceId.text())-1
            self.sigSelectFace.emit(selectId)
   
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","编号不合法，请重新输入(1~N)")
    def closeEvent(self, event):
        self.sigClosed.emit()
        super(frmCircuitLoad, self).closeEvent(event)
        
        pass
    def setUVText(self,u,v):
        u_text="{:.6e}".format(u/1000)
       
        v_text="{:.6e}".format(v/1000)
        
        self.txtLengthUV.setText(f"({u_text},{v_text})")
    def actionExcgange(self):
        u=self._u_length
        v=self._v_length
        self._u_length=v
        self._v_length=u
        self.setUVText(v,u)
        pass