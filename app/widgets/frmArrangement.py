from PyQt5 import QtCore,QtWidgets
from UI.ui_frmArrangement import Ui_frmArrangement
from ..dataModel.antenna import Antenna
from ..icons import sysIcons
from ..api import api_model

class frmArrange(Ui_frmArrangement,QtWidgets.QMainWindow):
    # sigModifyPower=QtCore.pyqtSignal(Power)
    sigOffset=QtCore.pyqtSignal(tuple)
    sigRotate=QtCore.pyqtSignal(float)
    sigDirChange=QtCore.pyqtSignal(tuple)
    sigAxisChange=QtCore.pyqtSignal(float)
    sigPixelChange=QtCore.pyqtSignal(float)
    sigClosed=QtCore.pyqtSignal()
    sigImport=QtCore.pyqtSignal()
    sigPoints=QtCore.pyqtSignal()
    def __init__(self,parent=None,antennaObj:Antenna=None):
        super(frmArrange,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._antenna=antennaObj
        self._is_axis_changed=False
        self._is_pixel_changed=False
        self._is_dir_changed=False
        self._is_offset_changed=False
        self._is_rotate_changed=False
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.onLoad()
        self.btnOK.clicked.connect(self.actionOK)
        self.btnApply.clicked.connect(self.actionApply)
        # self.btnBrowse.clicked.connect(self.actionImport)
        self.txtAxisLength.textChanged.connect(self.axisChanged)
        self.txtDisplayPixel.textChanged.connect(self.pixelChanged)
        self.txtRotatebyZ.textChanged.connect(self.rotateChanged)
        self.txtDirection.textChanged.connect(self.dirChanged)
        self.txtDistance_X.textChanged.connect(self.offsetChanged)
        self.txtDistance_Y.textChanged.connect(self.offsetChanged)
        self.txtDistance_Z.textChanged.connect(self.offsetChanged)
    


    def onLoad(self):
        if(self._antenna!=None):
            self.txtAxisLength.setText(str(self._antenna.axis_length_array))
            self.txtRotatebyZ.setText(str(self._antenna.offset_rotate_z))
            
            self.txtDisplayPixel.setText(str(self._antenna.display_size))
            self.txtDistance_X.setText(str(self._antenna.offset_x))
            self.txtDistance_Y.setText(str(self._antenna.offset_y))
            self.txtDistance_Z.setText(str(self._antenna.offset_z))

            center=tuple(value / 1000 for value in self._antenna.center)
            self.txtOrigin.setText(str(center))
            self.txtDirection.setText(str(self._antenna.normal_dir))
            
            self.txtAntennaFile.setText(self._antenna.file_antenna)
            if(self._antenna.mode==Antenna.mode_points):
                self.txtAntennaFile.setText(f"points:{len(self._antenna.itemList_global)}")
                self.disableArrange()
            self.updateAngel(self._antenna.center,self._antenna.normal_dir)
            
        self.txtOrigin.setReadOnly(True)
        self.txtOrigin.setDisabled(True)
        self.initAntennaMenu()
        # self.txtAngel.setReadOnly(True)
        pass
    def axisChanged(self):
        self._is_axis_changed=True
        # axis_length=float(self.txtAxisLength.text())
        # print("axis changed",axis_length)
    def pixelChanged(self):
        self._is_pixel_changed=True
        pass
    def dirChanged(self):
        self._is_dir_changed=True
        pass
    def offsetChanged(self):
        self._is_offset_changed=True
        pass
    def rotateChanged(self):
        self._is_rotate_changed=True
        pass
    def sig_updateChoose(self,center,direction):
        center=tuple(value / 1000 for value in center)
        self.txtOrigin.setText(str(center))
        self.txtDirection.setText(str(direction))
        self.updateAngel(center,direction)
        
        # self.txtAngel.setText(str(angel))
        pass
    def updateAngel(self,center,direction):
        v=api_model.get_angel_xyz(center,direction)

        self.txtAngel.setText(str(v))
        self.txtAngel.setReadOnly(True)

    def updateAntennaFile(self,fileName):
        self.txtAntennaFile.setText(fileName)
        pass

    def actionApply(self):
        try:
            axis_length=float(self.txtAxisLength.text())
            display_size=float(self.txtDisplayPixel.text())

            normal_dir=tuple(float(value) for value in self.txtDirection.text()[1:-1].split(","))

            offset_x=float(self.txtDistance_X.text())
            offset_y=float(self.txtDistance_Y.text())
            offset_z=float(self.txtDistance_Z.text())

            offset_rotate_z=float(self.txtRotatebyZ.text())

            axis_orgin=self._antenna.axis_length_array
            display_origin=self._antenna.display_size
            offset_rotate_z_origin=self._antenna.offset_rotate_z

            tolerance=1e-6
            if(self._is_axis_changed and abs(axis_orgin-axis_length)>tolerance):
                self.sigAxisChange.emit(axis_length)
                self._antenna.axis_length_array=axis_length
            if(self._is_pixel_changed and abs(display_origin-display_size)>tolerance):
                self.sigPixelChange.emit(display_size)
                self._antenna.display_size=display_size
            if(self._is_dir_changed):
                self.sigDirChange.emit(normal_dir)
                self._antenna.normal_dir=normal_dir
            if(self._is_offset_changed):
                self.sigOffset.emit((offset_x,offset_y,offset_z))
            if(self._is_rotate_changed and abs(offset_rotate_z_origin-offset_rotate_z)>tolerance):
                self.sigRotate.emit(offset_rotate_z)
                self._antenna.offset_rotate_z=offset_rotate_z
            self._is_axis_changed=False
            self._is_pixel_changed=False
            self._is_dir_changed=False
            self._is_offset_changed=False
            self._is_rotate_changed=False
            return(1,"success")
           
            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","Invalid input,Please Check"+str(e))
            return (-1,str(e))
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass
    # def actionImport(self):
    #     self.sigImport.emit()
    #     pass
    def closeEvent(self, event):
        self.sigClosed.emit()
        return super().closeEvent(event)
    def initAntennaMenu(self):
        '''
        创建天线操作下拉菜单，点击按钮显示下拉菜单
        '''
        self.menuAntenna=QtWidgets.QMenu(self)
        self.menuAntenna.addAction("Import",self.actionImport)
        self.menuAntenna.addAction("Points",self.actionPoints)
        # self.menuAntenna.addAction("Delete",self.actionDelete)
        # self.menuAntenna.addAction("Copy",self.actionCopy)
        self.btnAntenna.setMenu(self.menuAntenna)
        pass
    def actionImport(self):
        if(self._antenna.mode!=Antenna.mode_array and len(self._antenna.itemList_global)>0):
            #询问是否切换模式
            ret=QtWidgets.QMessageBox.question(self,"Switch Mode","Switch to array mode will clear all data,Continue?",QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            if(ret==QtWidgets.QMessageBox.No):
                return
        self.sigImport.emit()
        self.enableArrange()
        pass
    def actionPoints(self):
        if(self._antenna.mode!=Antenna.mode_points and len(self._antenna.itemList_global)>0):
            #询问是否切换模式
            ret=QtWidgets.QMessageBox.question(self,"Switch Mode","Switch to points mode will clear all data,Continue?",QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            if(ret==QtWidgets.QMessageBox.No):
                return
        # self._antenna.mode=Antenna.mode_points
        self.sigPoints.emit()
        self.disableArrange()
        pass
    def enableArrange(self):
        self.groupWorkplane.setEnabled(True)
        self.txtDistance_X.setEnabled(True)
        self.txtDistance_Y.setEnabled(True)
        self.txtDistance_Z.setEnabled(True)
    def disableArrange(self):
        self.groupWorkplane.setEnabled(False)
        self.txtDistance_X.setEnabled(False)
        self.txtDistance_Y.setEnabled(False)
        self.txtDistance_Z.setEnabled(False)
        

        
