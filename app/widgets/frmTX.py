from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu,QTableWidgetItem,QAbstractItemView,
                                QHeaderView)
from PyQt5.QtGui import QFont
from UI.ui_frmTX import Ui_frmTX
from ..dataModel.antenna import Antenna
from ..icons import sysIcons
from ..api import api_model
from .baseStyle import baseStyle
ROW_HEIGHT=30

class frmTX(Ui_frmTX,QtWidgets.QMainWindow):
    # sigModifyPower=QtCore.pyqtSignal(Power)
    sigOffset=QtCore.pyqtSignal(tuple)
    sigRotate=QtCore.pyqtSignal(float)
    sigDirChange=QtCore.pyqtSignal(tuple,bool)
    sigAxisChange=QtCore.pyqtSignal(float)
    sigPixelChange=QtCore.pyqtSignal(float)
    sigClosed=QtCore.pyqtSignal()
    sigImport=QtCore.pyqtSignal()
    sigPoints=QtCore.pyqtSignal()
    sigPointsApply=QtCore.pyqtSignal(list,float,bool)#点阵元数据，显示像素，是否显示阵列
    sigShowAxis=QtCore.pyqtSignal(bool)

    sigRotate_radio=QtCore.pyqtSignal(tuple)
    sigScale_radio=QtCore.pyqtSignal(float)
    sigAxisChange_radio=QtCore.pyqtSignal(float,float)
    sigImport_radio=QtCore.pyqtSignal()
    sigShowAxis_radio=QtCore.pyqtSignal(bool)
    sigShowAntenna_radio=QtCore.pyqtSignal(bool)#是否显示方向图

    sigTabActivated=QtCore.pyqtSignal(int)
    sigFaceChanged=QtCore.pyqtSignal(int) #面选择变化下拉列表选择

    sigPower=QtCore.pyqtSignal(str)
    sigShowArray=QtCore.pyqtSignal(bool)
    sigAntennaTypeApply=QtCore.pyqtSignal(int) #应用天线类型
    def __init__(self,parent=None,antennaObj:Antenna=None,faceNum=0):
        super(frmTX,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
      

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)

        self._antenna=antennaObj
        self._is_axis_changed=False
        self._is_pixel_changed=False
        self._is_dir_changed=False
        self._is_offset_changed=False
        self._is_rotate_changed=False
        self._faceNum=faceNum
       
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(antennaObj.typeName)
        
        self.onLoad()
        self.btnOK.clicked.connect(self.actionOK)
        self.btnApply.clicked.connect(self.actionApply)

        self.btnCancel.clicked.connect(self.close)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.cbxFaces.currentIndexChanged.connect(self.faceChanged)

        #workplane操作
        self.txtAxisLength.textChanged.connect(self.axisChanged)
        self.txtRotatebyZ.textChanged.connect(self.rotateChanged)
        self.txtDirection.textChanged.connect(self.dirChanged)

        #天线操作 
        self.btnBrowse.clicked.connect(self.actionImport)
        self.txtDisplayPixel.textChanged.connect(self.pixelChanged)
        self.txtDistance_X.textChanged.connect(self.offsetChanged)
        self.txtDistance_Y.textChanged.connect(self.offsetChanged)
        self.txtDistance_Z.textChanged.connect(self.offsetChanged)
        
        self.chkShowAxis.clicked.connect(self.actionShowAxis)

        #方向图操作
        self.btnBrowse_radio.clicked.connect(self.actionImport_radio)
        self.chkShowAxis_radio.clicked.connect(self.actionShowAxis_radio)
        self.chkShowAntenna_radio.clicked.connect(self.actionShoeAntenna_radio)

        self.chkShowArray.clicked.connect(self.actionShowArray)
        self.cbxAntennaType.currentIndexChanged.connect(self.setAntenntType)
        self.btnAddPoint.clicked.connect(self.addRow)
        self.btnRemovePoint.clicked.connect(self.removeRow)
        self.chkShowArray_discrete.clicked.connect(self.actionShowArray)
        self.chkReverseN.clicked.connect(self.actionReversN)

    
    


    def onLoad(self):
          
        
        self.initPointsTable()
        if(not hasattr(self._antenna,"antennaType")):
            self._antenna.antennaType=self._antenna.mode_array
        if(not hasattr(self._antenna,"itemList_discrete")):
            self._antenna.itemList_discrete=[]
        
        #都需要加载
        self.loadProperties_array(self._antenna)
        self.loadProperties_points(self._antenna)
        # self.txtDisplayPixel_2.setText(str(self._antenna.display_size))
        self.txtDisplayPixel.setText(str(self._antenna.display_size))
        self.chkReverseN.setChecked(self._antenna.reverseN)
  
      
        self.loadProperties_radio()
        self.initFaces(self._faceNum)
        self.txtName.setText(self._antenna.name)
        if(self._antenna.typeName=="RX"):
            self.lblPower.setVisible(False)
            self.txtPower.setVisible(False)
            self.lblWaveform.setVisible(False)
            self.cbxWaveform.setVisible(False)
            height_hide=60
            
            self.groupPower.setFixedHeight(self.groupPower.height()-height_hide)
            self.lblTitle.move(self.lblTitle.x(),self.lblTitle.y()-height_hide)
            self.txtName.move(self.txtName.x(),self.txtName.y()-height_hide)
            self.setFixedHeight(self.height()-height_hide)
            

            self.btnApply.move(self.btnApply.x(),self.btnApply.y()-height_hide)
            self.btnOK.move(self.btnOK.x(),self.btnOK.y()-height_hide)
            self.btnCancel.move(self.btnCancel.x(),self.btnCancel.y()-height_hide)
           
    
            
        self.cbxAntennaType.setCurrentIndex(self._antenna.antennaType)
        self.setAntenntType()
            
 
        pass
    def setAntenntType(self):
        antennaType=self.cbxAntennaType.currentIndex()

        if(antennaType==0):
            self.tabWidget.setTabVisible(0,True)
            self.tabWidget.setTabVisible(1,True)
            self.tabWidget.setTabVisible(2,False)
            self.tabWidget.setCurrentIndex(0)

        else:
            self.tabWidget.setTabVisible(0,False)
            self.tabWidget.setTabVisible(1,False)
            self.tabWidget.setTabVisible(2,True)
            self.tabWidget.setCurrentIndex(2)


    def initFaces(self,faceNum):
        self.cbxFaces.clear()
        for i in range(faceNum):
            self.cbxFaces.addItem("face-"+str(i+1),i)
        self.cbxFaces.setCurrentIndex(-1)
        if(self._antenna._face_id>=0):
            self.cbxFaces.setCurrentIndex(self._antenna._face_id)
        
        pass
    def loadProperties_radio(self):
        if(self._antenna!=None):
            center=tuple(value / 1000 for value in self._antenna.center)
            self.txtOrigin_radio.setText(str(center))

            angel=api_model.get_angel_xyz(self._antenna.center,
                                          self._antenna.normal_dir)
            self.txtAngel_radio.setText(str(angel))
            self.txtRotate_x.setText(str(self._antenna.rotate_x))
            self.txtRotate_y.setText(str(self._antenna.rotate_y))
            self.txtRotate_z.setText(str(self._antenna.rotate_z))
            self.txtScale.setText(str(self._antenna.radio_scale))
            self.txtAxisLength_radio.setText(str(self._antenna.axis_length_antenna))
            self.txtRadioFile.setText(self._antenna.file_antenna)
            self.chkShowAntenna_radio.setChecked(self._antenna._show_antenna)
            self.chkShowAxis_radio.setChecked(self._antenna._show_axis_radio)
            if(hasattr(self._antenna,"axis_thickness_antenna")==False):
                self._antenna.axis_thickness_antenna=1
            self.txtThickness.setText(str(self._antenna.axis_thickness_antenna))
    def loadProperties_array(self,antennaObj:Antenna):
        if(antennaObj!=None):
            self.txtAxisLength.setText(str(antennaObj.axis_length_array))
            self.txtRotatebyZ.setText(str(antennaObj.offset_rotate_z))
            
            self.txtDisplayPixel.setText(str(antennaObj.display_size))
            self.txtDistance_X.setText(str(antennaObj.offset_x))
            self.txtDistance_Y.setText(str(antennaObj.offset_y))
            self.txtDistance_Z.setText(str(antennaObj.offset_z))

            center=tuple(value / antennaObj.m_unit for value in antennaObj.center)
            self.txtOrigin.setText(str(center))
            self.txtDirection.setText(str(antennaObj.normal_dir))
            
            self.txtAntennaFile.setText(antennaObj.file_array)
            
            self.updateAngel(antennaObj.center,antennaObj.normal_dir)

            self.txtPower.setText(str(antennaObj.power))
            self.chkShowArray.setChecked(antennaObj._show_array)
            self.chkShowAxis.setChecked(antennaObj._show_axis_array)
            self.chkReverseN.setChecked(antennaObj.reverseN)

            self.txtElementNum.setText(str(len(antennaObj.itemList_local))) #显示阵元数
    def loadProperties_points(self,antennaObj:Antenna):
        if(antennaObj!=None):
            self.fillPointList(antennaObj.itemList_discrete)
            self.txtDisplayPixel_discrete.setText(str(antennaObj.display_size))
            self.chkShowArray_discrete.setChecked(antennaObj._show_array)
            

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
    def sig_updateChoose(self,center,direction,faceId):
        center=tuple(value / 1000 for value in center)
        self.txtOrigin.setText(str(center))
        self.txtDirection.setText(str(direction))
        self.txtOrigin_radio.setText(str(center))
        self.updateAngel(center,direction)
        self.cbxFaces.setCurrentIndex(faceId)
        self.chkReverseN.setChecked(False)
        
        # self.txtAngel.setText(str(angel))
        pass
    def updateAngel(self,center,direction):
        v=api_model.get_angel_xyz(center,direction)

        self.txtAngel.setText(str(v))
        self.txtAngel.setReadOnly(True)
        self.txtAngel_radio.setText(str(v)) 

    def updateAntennaFile(self,fileName,elmemtNum:int=0):
        self.txtAntennaFile.setText(fileName)
        self.txtElementNum.setText(str(elmemtNum))
        pass

    def actionApply_array(self,needClose=False):
        try:
            axis_length=float(self.txtAxisLength.text())
            offset_rotate_z_origin=self._antenna.offset_rotate_z
            axis_orgin=self._antenna.axis_length_array

            display_size=float(self.txtDisplayPixel.text())
            normal_dir=tuple(float(value) for value in self.txtDirection.text()[1:-1].split(","))

            offset_x=float(self.txtDistance_X.text())
            offset_y=float(self.txtDistance_Y.text())
            offset_z=float(self.txtDistance_Z.text())

            offset_rotate_z=float(self.txtRotatebyZ.text())
            
            power=float(self.txtPower.text())

            
            display_origin=self._antenna.display_size
            

            tolerance=1e-6
            if(self._is_axis_changed and abs(axis_orgin-axis_length)>tolerance):
                self.sigAxisChange.emit(axis_length)
                self._antenna.axis_length_array=axis_length

            if(self._is_rotate_changed and abs(offset_rotate_z_origin-offset_rotate_z)>tolerance):
                self.sigRotate.emit(offset_rotate_z)
                self._antenna.offset_rotate_z=offset_rotate_z

            if(self._is_pixel_changed and abs(display_origin-display_size)>tolerance):
                self.sigPixelChange.emit(display_size)
                self._antenna.display_size=display_size
            
            if(self._is_offset_changed):
                self.sigOffset.emit((offset_x,offset_y,offset_z))

            if(self._is_dir_changed):
                self.sigDirChange.emit(normal_dir,self.chkReverseN.isChecked())
                self._antenna.normal_dir=normal_dir
                self._antenna.reverseN=self.chkReverseN.isChecked()

            self.sigPower.emit(self.txtPower.text())

            self._is_axis_changed=False
            self._is_pixel_changed=False
            self._is_dir_changed=False
            self._is_offset_changed=False
            self._is_rotate_changed=False

            self.actionApply_radio()
            if(needClose):
                self.close()
           
           
            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","数据校验错误，请检查."+str(e))
        pass
      

    def closeEvent(self, event):
        self.sigClosed.emit()
        return super().closeEvent(event)

    def actionImport(self):
   
        self.sigImport.emit() #在外层界面中弹出对话框导入数据
        pass

    def initPointsTable(self):
        self.tbPoints.setFont(self._font)
        self.setPointColumns()
        self.tbPoints.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
    
        self.tbPoints.setStyleSheet("""
                                      QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);}

                                      """)
        self.tbPoints.horizontalHeader().setHighlightSections(False)
        self.tbPoints.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        
        self.tbPoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbPoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.tbPoints.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        # self.tbFreqList.horizontalHeader().setStyleSheet("QHeaderView::section {border-bottom: 1px solid rgb(200,200,200);}")

        pass
    def addRow(self):
        row_position=self.tbPoints.rowCount()
        self.tbPoints.insertRow(row_position)
        self.tbPoints.setRowHeight(row_position, ROW_HEIGHT)
        self.tbPoints.setCurrentCell(row_position,0)
    
    def removeRow(self):
        row_position=self.tbPoints.currentRow()
        self.tbPoints.removeRow(row_position)
    def setPointColumns(self):
        self.tbPoints.setColumnCount(3)
        self.tbPoints.setHorizontalHeaderLabels(["X(m)","Y(m)","Z(m)"])
        self.tbPoints.setColumnWidth(0,100)
        self.tbPoints.setColumnWidth(1,100)
        self.tbPoints.setColumnWidth(2,100)

    def fillPointList(self,pointList:list=[]):
        for p in pointList:
            row_index=self.tbPoints.rowCount()
            self.tbPoints.insertRow(row_index)
            self.tbPoints.setRowHeight(row_index,baseStyle.rowHeight)
            item=QtWidgets.QTableWidgetItem(str(p[0]))
            self.tbPoints.setItem(row_index,0,item)
            item=QtWidgets.QTableWidgetItem(str(p[1]))
            self.tbPoints.setItem(row_index,1,item)
            item=QtWidgets.QTableWidgetItem(str(p[2]))
            self.tbPoints.setItem(row_index,2,item)
    def getPointList(self):
        try:
            pointList=[]
            for i in range(self.tbPoints.rowCount()):
                x=float(self.tbPoints.item(i,0).text())
                y=float(self.tbPoints.item(i,1).text())
                z=float(self.tbPoints.item(i,2).text())
                pointList.append((x,y,z))
            return (1,"success",pointList)
        except Exception as e:
            return (-1,"坐标必须是数字类型，请检查"+str(e),None)



    def initPoints(self,points):
       
        pointList:list=points
        rowNum=len(pointList)
        unit=self._antenna.m_unit
        
        self.tbPoints.setRowCount(rowNum)
        for i in range(rowNum):
            v=pointList[i]
            self.tbPoints.setRowHeight(i, ROW_HEIGHT)
            item = QTableWidgetItem(str(v[0]/unit))
            self.tbPoints.setItem(i, 0, item)
            item = QTableWidgetItem(str(v[1]/unit))
            self.tbPoints.setItem(i, 1, item)
            item = QTableWidgetItem(str(v[2]/unit))
            self.tbPoints.setItem(i, 2, item)

        pass

    def actionApply_points(self,needClose=False):
        try:
            code,msg,points=self.getPointList()
            if(code!=1):
                QtWidgets.QMessageBox.about(self,"提示",msg)
                return
            display_size=float(self.txtDisplayPixel_discrete.text())
            showArray=self.chkShowArray_discrete.isChecked()
            self.sigPointsApply.emit(points,display_size,showArray)
            self.actionApply_radio()
            if(needClose):
                self.close()
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","数据数据错误，请检查."+str(e))

        pass
    def actionApply(self):
        if(self.cbxAntennaType.currentIndex()==Antenna.mode_array):
            self.actionApply_array()
        else:
            self.actionApply_points()
        self.sigAntennaTypeApply.emit(self.cbxAntennaType.currentIndex())
        pass
    def actionOK(self):
        if(self.cbxAntennaType.currentIndex()==Antenna.mode_array):
            self.actionApply_array(needClose=True)
        else:
            self.actionApply_points(needClose=True)
        self.sigAntennaTypeApply.emit(self.cbxAntennaType.currentIndex())
        pass
    def actionShowAxis(self):
        self.sigShowAxis.emit(self.chkShowAxis.isChecked())
        pass
    def actionImport_radio(self):
        self.sigImport_radio.emit()
        pass
    def actionShowAxis_radio(self):
        showAxis=self.chkShowAxis_radio.isChecked()
        self.sigShowAxis_radio.emit(showAxis)
        pass
    def actionShoeAntenna_radio(self):
        showAntenna=self.chkShowAntenna_radio.isChecked()
        self.sigShowAntenna_radio.emit(showAntenna)
        pass
    def updateRadioFile(self,fname):
        self.txtRadioFile.setText(fname)
        pass

    def actionApply_radio(self):
        try:
            p1_x=float(self.txtRotate_x.text())
            p1_y=float(self.txtRotate_y.text())
            p1_z=float(self.txtRotate_z.text())
            scale=float(self.txtScale.text())
            axis_length=float(self.txtAxisLength_radio.text())
            axis_thickness=float(self.txtThickness.text())

            self.sigRotate_radio.emit((p1_x,p1_y,p1_z))
            self.sigScale_radio.emit(scale)
            self.sigAxisChange_radio.emit(axis_length,axis_thickness)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"方向图旋转","x/y/z旋转角度必须是数字类型"+str(e))

        pass
    def tabChanged(self,index):
        self.sigTabActivated.emit(index)
        pass
    def faceChanged(self):
        faceId=self.cbxFaces.currentIndex()
        self.sigFaceChanged.emit(faceId)
        pass
    def actionShowArray(self):
        if(self.cbxAntennaType.currentIndex()==Antenna.mode_array):
            self.sigShowArray.emit(self.chkShowArray.isChecked())
        else:
            self.sigShowArray.emit(self.chkShowArray_discrete.isChecked())
        pass
    def actionReversN(self):
        '''
        反转N轴
        '''
        self._is_dir_changed=True
        normal_dir=tuple(float(value) for value in self.txtDirection.text()[1:-1].split(","))
        normal_dir=(-normal_dir[0],-normal_dir[1],-normal_dir[2])
        self.txtDirection.setText(str(normal_dir))
        self.sigDirChange.emit(normal_dir,self.chkReverseN.isChecked())
        self._is_dir_changed=False
        pass

        
