from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu,QTableWidgetItem,QAbstractItemView,
                                QHeaderView)
from PyQt5.QtGui import QFont
from UI.ui_frmArrangement2 import Ui_frmArrangement2
from ..dataModel.antenna import Antenna
from ..icons import sysIcons
from ..api import api_model
ROW_HEIGHT=30

class frmArrange2(Ui_frmArrangement2,QtWidgets.QMainWindow):
    # sigModifyPower=QtCore.pyqtSignal(Power)
    sigOffset=QtCore.pyqtSignal(tuple)
    sigRotate=QtCore.pyqtSignal(float)
    sigDirChange=QtCore.pyqtSignal(tuple)
    sigAxisChange=QtCore.pyqtSignal(float)
    sigPixelChange=QtCore.pyqtSignal(float)
    sigClosed=QtCore.pyqtSignal()
    sigImport=QtCore.pyqtSignal()
    sigPoints=QtCore.pyqtSignal()
    sigPointsChanged=QtCore.pyqtSignal(list,float)
    sigShowAxis=QtCore.pyqtSignal(bool)
    sigShowAntenna=QtCore.pyqtSignal(bool)
    def __init__(self,parent=None,antennaObj:Antenna=None):
        super(frmArrange2,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._font=QFont()
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
        self.btnBrowse.clicked.connect(self.actionImport)
        self.txtAxisLength.textChanged.connect(self.axisChanged)
        self.txtDisplayPixel.textChanged.connect(self.pixelChanged)
        self.txtRotatebyZ.textChanged.connect(self.rotateChanged)
        self.txtDirection.textChanged.connect(self.dirChanged)
        self.txtDistance_X.textChanged.connect(self.offsetChanged)
        self.txtDistance_Y.textChanged.connect(self.offsetChanged)
        self.txtDistance_Z.textChanged.connect(self.offsetChanged)
        self.cbxAntennaType.currentIndexChanged.connect(self.actionCreateAntenna)
        self.btnAddPoint.clicked.connect(self.addRow)
        self.btnRemovePoint.clicked.connect(self.removeRow)
        self.chkShowAxis.clicked.connect(self.actionShowAxis)
    
    


    def onLoad(self):
        self.tabWidget.tabBar().hide()            
        self.txtOrigin.setDisabled(True)
        
        self.initPointsTable()
        self.cbxAntennaType.setCurrentIndex(self._antenna.mode)
        if(self._antenna.mode==Antenna.mode_array):
            self.showArrayTab()
            self.loadProperties_array(self._antenna)
        else:
            self.showPointsTab()
            self.loadProperties_points(self._antenna)
        self.txtDisplayPixel_2.setText(str(self._antenna.display_size))
        self.txtDisplayPixel.setText(str(self._antenna.display_size))
  
        self._font.setPointSize(9)
        self.setFont(self._font)
 
        pass
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
    def loadProperties_points(self,antennaObj:Antenna):
        if(antennaObj!=None):
            self.initPoints(antennaObj.itemList_global)
            

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

    def actionApply_array(self):
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
    def actionOK_array(self):
        code,message=self.actionApply_array()
        if(code!=1):
            return
        self.close()
        pass

    def closeEvent(self, event):
        self.sigClosed.emit()
        return super().closeEvent(event)

    def actionImport(self):
        if(self._antenna.mode!=Antenna.mode_array and len(self._antenna.itemList_global)>0):
            #询问是否切换模式
            ret=QtWidgets.QMessageBox.question(self,"Switch Mode","Switch to array mode will clear all data,Continue?",QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            if(ret==QtWidgets.QMessageBox.No):
                return
        
        
        self.showArrayTab()
        self.loadProperties_array(Antenna())
        self.sigImport.emit()
        # self.enableArrange()
        pass
    def actionPoints(self):
        if(self._antenna.mode!=Antenna.mode_points and len(self._antenna.itemList_global)>0):
            #询问是否切换模式
            ret=QtWidgets.QMessageBox.question(self,"Switch Mode","Switch to points mode will clear all data,Continue?",QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            if(ret==QtWidgets.QMessageBox.No):
                return
        self.showPointsTab()
        
        self.loadProperties_points(Antenna())
        self.sigPoints.emit()
        pass


    def actionCreateAntenna(self):
        '''
        创建天线
        '''
        antennaIndex=self.cbxAntennaType.currentIndex()
        if(antennaIndex==0):
            self.actionImport()

        else:
            self.actionPoints()

        
        pass
    def showArrayTab(self):
        self.tabWidget.setTabVisible(0,True)
        self.tabWidget.setTabVisible(1,False)
        pass
    def showPointsTab(self):
        self.tabWidget.setTabVisible(0,False)
        self.tabWidget.setTabVisible(1,True)
        pass
    def initPointsTable(self):
        self.setPointColumns()
        self.tbPoints.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
    
        self.tbPoints.setStyleSheet("""
                                      QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);}

                                      """)
        #   QTableWidget::item:selected { border: 2px solid rgb(188,220,220); }
        # self.tbFreqList.horizontalHeader().setSectionsClickable(False)
        self.tbPoints.horizontalHeader().setHighlightSections(False)
        self.tbPoints.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        # self.tbFreqList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
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
        
        # item = QTableWidgetItem(str(""))
        # self.tbFreqList.setInputMethodHints
        
        # self.tbFreqList.setItem(row_position, 0, item)

        # self.tbFreqList.setItemDelegate(EditDelegate())
    def removeRow(self):
        row_position=self.tbPoints.currentRow()
        self.tbPoints.removeRow(row_position)
    def setPointColumns(self):
        self.tbPoints.setColumnCount(3)
        self.tbPoints.setHorizontalHeaderLabels(["X(m)","Y(m)","Z(m)"])
        self.tbPoints.setColumnWidth(0,116)
        self.tbPoints.setColumnWidth(1,116)
        self.tbPoints.setColumnWidth(2,116)


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


    def getPoints(self):
        try:
            points=[]
            unit=self._antenna.m_unit
            for row in range(self.tbPoints.rowCount()):
                x=float(self.tbPoints.item(row,0).text())*unit
                y=float(self.tbPoints.item(row,1).text())*unit
                z=float(self.tbPoints.item(row,2).text())*unit
                
                points.append((x,y,z,1,0))
            # print("get media item",mItem)
            if(len(points)==0):
                return(-1,"Please add point and attribute value",None)
            return (1,"success",points)
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"media input error","please input float value"+str(e))
            return(-1,"point attribute value should be float\n"+str(e),None)

    def actionOK_points(self):
        self.actionApply_points()
        self.close()
    def actionApply_points(self):
        try:
            code,msg,points=self.getPoints()
            if(code!=1):
                QtWidgets.QMessageBox.about(self,"point input error",msg)
                return
            display_size=float(self.txtDisplayPixel_2.text())
            self.sigPointsChanged.emit(points,display_size)
            
            
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","Invalid input,Please Check"+str(e))

        pass
    def actionApply(self):
        if(self.cbxAntennaType.currentIndex()==Antenna.mode_array):
            self.actionApply_array()
        else:
            self.actionApply_points()
        pass
    def actionOK(self):
        if(self.cbxAntennaType.currentIndex()==Antenna.mode_array):
            self.actionOK_array()
        else:
            self.actionOK_points()
        pass
    def actionShowAxis(self):
        self.sigShowAxis.emit(self.chkShowAxis.isChecked())
        pass

        
