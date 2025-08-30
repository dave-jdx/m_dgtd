from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QTableWidget,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmMediaDispersive import Ui_frmMediaDispersive
from ..icons import sysIcons

from ..dataModel.mediaN import DispersiveProp,Dispersive
from ..api import api_writer
import uuid
from .baseStyle import baseStyle
ROW_HEIGHT=30
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmMediaDispersive(Ui_frmMediaDispersive,QtWidgets.QMainWindow):
    sigApplyDispersive=QtCore.pyqtSignal(Dispersive,int)
  
    def __init__(self,parent=None,media:Dispersive=None,rowIndex:int=-1):
        super(frmMediaDispersive,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._isotropic=media
        self._rowIndex=rowIndex
        
       
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnAddRow.clicked.connect(self.addRow)
        self.btnRemoveRow.clicked.connect(self.removeRow)
        self.btnClose.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.actionOK)

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)

        self.onLoad()  
        
        

    def onLoad(self):
        self.initTableColumns(self.tableWidget,DispersiveProp.columns)
        if(self._isotropic is not None):
            self.txtMediaName.setText(self._isotropic.name)
            rowNum=len(self._isotropic.itemList)
            for i in range(rowNum):
                self.tableWidget.insertRow(i)
                item=self._isotropic.itemList[i]
                self.tableWidget.setItem(i,0,QTableWidgetItem(item.frequency))
                self.tableWidget.setItem(i,1,QTableWidgetItem(item.permittivity_real))
                self.tableWidget.setItem(i,2,QTableWidgetItem(item.permittivity_imag))
                self.tableWidget.setItem(i,3,QTableWidgetItem(item.permeability_real))
                self.tableWidget.setItem(i,4,QTableWidgetItem(item.permeability_imag))
                self.tableWidget.setItem(i,5,QTableWidgetItem(item.eConductivity))
          
            pass
        
        pass
    def initTableColumns(self,tableWidget:QTableWidget,colums:list):
         
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(0)
        tableWidget.setColumnCount(len(colums))
        tableWidget.setHorizontalHeaderLabels(colums)
        # tableWidget.setMinimumWidth(600)
        tableWidget.resizeColumnsToContents()
    
       
        tableWidget.horizontalHeader().setMinimumSectionSize(50)

        tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        tableWidget.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px;border:1px solid rgb(216,216,216); }
                                 QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);}

                                      """)
    def addRow(self):
        row_position=self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setRowHeight(row_position, ROW_HEIGHT)
        self.tableWidget.setCurrentCell(row_position,0)
        self.tableWidget.setFocus()
        
    def removeRow(self):
        if(self.tableWidget.rowCount()<=0):
            return
        row_position=self.tableWidget.currentRow()
        if(row_position<0):
            return
        self.tableWidget.removeRow(row_position)

    def getMediaItem(self):
        try:
            media_dispersive=Dispersive()
            media_dispersive.name=self.txtMediaName.text()
            rowNum=self.tableWidget.rowCount()
            for i in range(rowNum):

                item=DispersiveProp()
                item.frequency=self.tableWidget.item(i,0).text()
                item.permittivity_real=self.tableWidget.item(i,1).text()
                item.permittivity_imag=self.tableWidget.item(i,2).text()
                item.permeability_real=self.tableWidget.item(i,3).text()
                item.permeability_imag=self.tableWidget.item(i,4).text()
                item.eConductivity=self.tableWidget.item(i,5).text()
                media_dispersive.itemList.append(item)
    

            if(media_dispersive.name==""):
                return(-1,"材料名称不能为空",None)
            return (1,"success",media_dispersive)
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"media input error","please input float value"+str(e))
            return(-1,"参数值必须是数字，请检查并修改\n"+str(e),None)

    def actionOK(self):
        code,message,mediaData=self.getMediaItem()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"材料数据错误",message)
            return
        self.sigApplyDispersive.emit(mediaData,self._rowIndex)
        self.close()

    def closeEvent(self, event):
        return super().closeEvent(event)
