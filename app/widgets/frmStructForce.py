from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmStructForce import Ui_frmStructForce
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.pf import PF_Struct_Force


class frmStructSource(Ui_frmStructForce,frmBase):
    sigFaceSelected=QtCore.pyqtSignal(int,PF_Struct_Force,int)
    sigClosed=QtCore.pyqtSignal()
  
    def __init__(self,parent=None,forceObj:PF_Struct_Force=None):
        super(frmStructSource,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self._forceObj=forceObj
        if forceObj is not None:
            self.txtPointId.setText(str(forceObj.pointId+1))
            self.txtPoint_xyz.setText(str(forceObj.point_xyz))
            self.txtForce_x.setText(str(forceObj.force_xyz[0]))
            self.txtForce_y.setText(str(forceObj.force_xyz[1]))
            self.txtForce_z.setText(str(forceObj.force_xyz[2]))

        self.onLoad()  
    def onLoad(self):
        self.txtPointId.setEnabled(False)
        super().onLoad()
        pass
    def actionApply(self):
        try:
            pointId_old=-1
            if(self._forceObj is not None):
                pointId_old=self._forceObj.pointId
            forceObj=PF_Struct_Force()
            pointId=int(self.txtPointId.text())-1
            forceObj.pointId=pointId
            forceObj.point_xyz=eval(self.txtPoint_xyz.text())
            forceObj.force_xyz=(float(self.txtForce_x.text()),float(self.txtForce_y.text()),float(self.txtForce_z.text()))
            self.sigFaceSelected.emit(pointId,forceObj,pointId_old)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","面编号/坐标/力不合法，请重新输入"+str(e))
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass

    def sig_choosePoint(self,pointId:int,point:tuple):
        self.setFocus()
        m_unit=1000
        self.txtPointId.setText(str(pointId+1))  
        point=(float(f"{point[0]/m_unit:.4f}"),float(f"{point[1]/m_unit:.4f}"),float(f"{point[2]/m_unit:.4f}"))
        self.txtPoint_xyz.setText(str(point))
        self.txtForce_x.setFocus()
        pass

    def closeEvent(self, event):
        self.sigClosed.emit()
        super().closeEvent(event)
        pass