import os
from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmCreateMesh import Ui_frmCreateMesh
from ..dataModel.mesh import Mesh
from ..icons import sysIcons
from .frmBase import frmBase
SPEED=3e+8
class frmCreateMesh(Ui_frmCreateMesh,frmBase):
    sigCreate=QtCore.pyqtSignal(dict)
    sigOptions=QtCore.pyqtSignal(dict)
    def __init__(self,parent=None,options:dict={"maxh":0.1,
                                                "minh":0,
                                                "3dAlogrithm":0,
                                                "smoothing_steps":1,
                                                "optimize_tetrahedra":1,
                                                "hex_x":0.01,
                                                "hex_y":0.01,
                                                "hex_z":0.01,},
                 localSize:dict={}):
        self.parent=parent
        super(frmCreateMesh,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnMesh.clicked.connect(self.actionCreate)
        self.btnSave.clicked.connect(self.actionSave)
        self._options=options
        self._localSize=localSize


        # self.maxh=maxh
        self.txt_size_min.setText(str(options[Mesh.k_minh]))
        self.txt_size_max.setText(str(options[Mesh.k_maxh]))
        self.txt_smoothind_steps.setText(str(options[Mesh.k_smoothing_steps]))
        self.chk_optimize_tet.setChecked(options[Mesh.k_optimize_tetrahedra])
        self.cbx3dAlogrithm.setCurrentIndex(options[Mesh.k_3dAlogrithm])

        self.txtHex_x.setText(str(options.get("hex_x",0.01)))
        self.txtHex_y.setText(str(options.get("hex_y",0.01)))
        self.txtHex_z.setText(str(options.get("hex_z",0.01)))
        
        self.onLoad()

    def onLoad(self):
        super().onLoad()
        # self.tabWidget.setTabVisible(1,False)
        pass



    def actionSave(self):
        try:
            options=self.getOptions()
            self.sigOptions.emit(options)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"网格参数","请输入正确格式的数据"+str(e))
        pass
    def actionCreate(self):
        try:
            options=self.getOptions()
            self.sigCreate.emit(options)
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"网格参数","请输入正确格式的数据"+str(e))
            
    
    def getOptions(self):
        options={}
        minh=float(self.txt_size_min.text())
        maxh=float(self.txt_size_max.text())
        smoothing_steps=int(self.txt_smoothind_steps.text())
        optimize_tetrahedra=self.chk_optimize_tet.isChecked()
        alogrithm=self.cbx3dAlogrithm.currentIndex()

        options[Mesh.k_maxh]=maxh
        options[Mesh.k_minh]=minh
        options[Mesh.k_smoothing_steps]=smoothing_steps
        options[Mesh.k_optimize_tetrahedra]=optimize_tetrahedra
        options[Mesh.k_3dAlogrithm]=alogrithm

        options["hex_x"]=float(self.txtHex_x.text())
        options["hex_y"]=float(self.txtHex_y.text())
        options["hex_z"]=float(self.txtHex_z.text())

        return options

        


