from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmAntennaPoints import Ui_frmAntennaPoints
from ..icons import sysIcons

from ..dataModel.antenna import Antenna
from ..api import api_writer
import uuid
ROW_HEIGHT=30
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmAntennaPoints(Ui_frmAntennaPoints,QtWidgets.QMainWindow):
    sigPointsChanged=QtCore.pyqtSignal(list)
  
    def __init__(self,parent=None,antennaObj=None):
        super(frmAntennaPoints,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._antenna:Antenna=antennaObj
        self._font=QFont()
        

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.btnCancel.clicked.connect(self.close)
        # self.btnOK.clicked.connect(self.btnOKClick)
        
        self.btnAddFreq.clicked.connect(self.addRow)
        self.btnRemoveFreq.clicked.connect(self.removeRow)

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)

        self.onLoad()  

    def onLoad(self):

        self.initPointsTable()
        self._font.setPointSize(9)
        self.setFont(self._font)
        if(self._antenna!=None):
            pList=self._antenna.itemList_global
            self.initPoints(pList)

        pass
 


    def initPointsTable(self):
        # self.tbFreqList.setColumnCount(5)
        # self.tbFreqList.setHorizontalHeaderLabels(Media.columnsDielectric)
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

    def actionOK(self):
        self.actionApply()
        self.close()
    def actionApply(self):
        code,msg,points=self.getPoints()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"point input error",msg)
            return
        self.sigPointsChanged.emit(points)
        pass
    def closeEvent(self, event):
        return super().closeEvent(event)
