import traceback
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtWidgets import QTableWidget,QAbstractItemView,QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmTime import Ui_frmTime
from ..icons import sysIcons
from .frmBase import frmBase
from ..dataModel.requestParam import RequestParam_time

class frmTime(Ui_frmTime,frmBase):
    sigTimeSet=QtCore.pyqtSignal(RequestParam_time)
  
    def __init__(self,parent=None,timeObj:RequestParam_time=None):
        super(frmTime,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

        # self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)

        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)
        self.btnAddRow.clicked.connect(lambda :self.addRow(self.tbPoints))
        self.btnRemoveRow.clicked.connect(lambda :self.removeRow(self.tbPoints))
        self._timeObj=timeObj
        if timeObj is not None:
            try:
                self.txtTimeTotal_g.setText(str(timeObj.timeTotal_g))
                self.txtTimeStep_g.setText(str(timeObj.timeStep_g))
                self.fillPointList(self._timeObj.timePoints_g)
            except:
                pass

        
        self.onLoad() 
        self.initPointsTable(self.tbPoints)
    def onLoad(self):
        super().onLoad()
        gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.groupBox.setStyleSheet(gbxStyle)
        
   
        
        pass
    def actionApply(self):
        try:
            timeObj=RequestParam_time()
            float(self.txtTimeTotal_g.text())
      
            float(self.txtTimeStep_g.text())
           
            timeObj.timeTotal_g=self.txtTimeTotal_g.text()
            timeObj.timeStep_g=self.txtTimeStep_g.text()
            timeObj.timePoints_g=self.getPointList()

     
            self.sigTimeSet.emit(timeObj)
            return (1,"suceess")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","时间设置数据不合法，请重新输入"+str(e))
            traceback.print_exc()
            return(-1,"error")
        pass
    def actionOK(self):
        code,message=self.actionApply()
        if(code!=1):
            return
        self.close()
        pass

    def initPointsTable(self,tableWidget:QTableWidget):
        tableWidget.setColumnWidth(0,200)
        
        
        tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        tableWidget.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px; }
                                      QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px; }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);
                                 }

                                      """)
        tableWidget.horizontalHeader().setHighlightSections(False)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        tableWidget.setFont(self._font)
        pass
    def addRow(self,tableWidget:QTableWidget):
        
        row_index=tableWidget.rowCount()
        tableWidget.insertRow(row_index)
        tableWidget.setRowHeight(row_index,25)
        tableWidget.setCurrentCell(row_index,0)
        pass
    def removeRow(self,tableWidget:QTableWidget):
        #删除选中行
        row_index=tableWidget.currentRow()
        if(row_index>=0):
            tableWidget.removeRow(row_index)
     
        pass
    def fillPointList(self,pointList:list=[]):
        for p in pointList:
            row_index=self.tbPoints.rowCount()
            self.tbPoints.insertRow(row_index)
            self.tbPoints.setRowHeight(row_index,25)
            item=QtWidgets.QTableWidgetItem(str(p))
            self.tbPoints.setItem(row_index,0,item)
           
    def getPointList(self):
        try:
            pointList=[]
            for i in range(self.tbPoints.rowCount()):
                x=self.tbPoints.item(i,0).text()
                float(x)
               
                pointList.append(x)
            return pointList
        except Exception as e:
            raise TypeError ("时刻必须是数字类型，请检查"+str(e))
