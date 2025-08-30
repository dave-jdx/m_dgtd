from ..theme import theme_ui
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate,QTableWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmMediaLibraryN import Ui_frmMediaLIbraryN
from ..icons import sysIcons

from ..dataModel.mediaN import MediaBase,Isotropic
from ..api import api_writer
import uuid
from .baseStyle import baseStyle
from .frmMediaIsotropic import frmMediaIsotropic

ROW_HEIGHT=20
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmMediaLibraryN(Ui_frmMediaLIbraryN,QtWidgets.QMainWindow):
    sigApplyMedia=QtCore.pyqtSignal(list)
    sigClosed=QtCore.pyqtSignal()
    sigMedialSelected=QtCore.pyqtSignal(MediaBase)
  
    def __init__(self,parent=None,
                 isotropicList:list=[]):
        super(frmMediaLibraryN,self).__init__(parent)
        # self.setStyleSheet(theme_ui.baseWidgetStyle)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        self._mediaSelected:MediaBase=None

    
        self._isotropicList:list[Isotropic]=isotropicList


    
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.btnOK.clicked.connect(self.actionOK)
        self.btnApply.clicked.connect(self.actionApply)
        self.btnCancel.clicked.connect(self.actionCancel)
        self.btnAdd.clicked.connect(self.actionAdd)
        self.btnDelete.clicked.connect(self.actionRemove)
        self.tbIsotropic.itemDoubleClicked.connect(self.modifyIsotropicItem)

        self.tbIsotropic.clicked.connect(self.rowClicked)

        

        self.onLoad()
 

    def onLoad(self):
    
        self.initTableIsotropic()


        
        pass
    def initTableIsotropic(self):
        colums=Isotropic.columns
        self.initTableColumns(self.tbIsotropic,colums)
        for isotropic in self._isotropicList:
            rowIndex=self.tbIsotropic.rowCount()
            self.tbIsotropic.insertRow(rowIndex)
            self.fillRow_isotropic(isotropic,rowIndex)
        pass

    def initTableColumns(self,tableWidget:QTableWidget,colums:list):
        tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tableWidget.horizontalHeader().setMinimumSectionSize(80)
        tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        tableWidget.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px;border:1px solid rgb(216,216,216); }
                                      """)
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(0)
        tableWidget.setColumnCount(len(colums))
        tableWidget.setHorizontalHeaderLabels(colums)
       
        # tableWidget.setMinimumWidth(600)
        tableWidget.resizeColumnsToContents()
        tableWidget.setFont(self._font)
        
        
        pass
    def actionAdd(self):
        tabIndex=self.tabMedia.currentIndex()
        self.addIsotropic()

    def actionRemove(self):
        tabIndex=self.tabMedia.currentIndex()

        self.removeRow(self.tbIsotropic)

    def actionApply(self):
        try:
            self.sigApplyMedia.emit(self._isotropicList)
            #当前选中的medium，通知其他窗口用来作为设置当天的选项
            if(self._mediaSelected!=None):
                self.sigMedialSelected.emit(self._mediaSelected)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"保存数据失败"+str(e))
        pass
    def actionOK(self):
        self.actionApply()
        self.close()
    def actionCancel(self):
        self.close()
    def modifyIsotropicItem(self):
        rowIndex=self.tbIsotropic.currentRow()
        isotropic=self._isotropicList[rowIndex]
        frm=frmMediaIsotropic(self,isotropic,rowIndex)
        frm.show()
        frm.sigApplyIsotropic.connect(self.applyIsotropicItem)
        pass


    def addIsotropic(self):
        frm=frmMediaIsotropic(self)
        frm.show()
        frm.sigApplyIsotropic.connect(self.applyIsotropicItem)
        pass
    def applyIsotropicItem(self,isotropic:Isotropic,rowIndex):
        if(rowIndex<0):
            #添加新行
            rowIndex=self.tbIsotropic.rowCount()
            self.tbIsotropic.insertRow(rowIndex)
            self._isotropicList.append(isotropic)
        else:
            #更新数据行
            self._isotropicList[rowIndex]=isotropic
        #更新表格值
        self.fillRow_isotropic(isotropic,rowIndex)

    
        pass
    def fillRow_isotropic(self,isotropic:Isotropic,rowIndex):
        self.tbIsotropic.setRowHeight(rowIndex, ROW_HEIGHT)
        item = QTableWidgetItem(isotropic.name)
        self.tbIsotropic.setItem(rowIndex, 0, item)
        item = QTableWidgetItem(isotropic.permittivity)
        self.tbIsotropic.setItem(rowIndex, 1, item)
        item = QTableWidgetItem(isotropic.permeability)
        self.tbIsotropic.setItem(rowIndex, 2, item)
        item = QTableWidgetItem(isotropic.eConductivity)
        self.tbIsotropic.setItem(rowIndex, 3, item)
        item = QTableWidgetItem(isotropic.tConductivity)
        self.tbIsotropic.setItem(rowIndex, 4, item)
        item = QTableWidgetItem(isotropic.density)
        self.tbIsotropic.setItem(rowIndex, 5, item)
        item = QTableWidgetItem(isotropic.specificHeat)
        self.tbIsotropic.setItem(rowIndex, 6, item)
        item = QTableWidgetItem(isotropic.youngModulus)
        self.tbIsotropic.setItem(rowIndex, 7, item)
        item = QTableWidgetItem(isotropic.poissonRatio)
        self.tbIsotropic.setItem(rowIndex, 8, item)
        item = QTableWidgetItem(isotropic.thermalExpansion)
        self.tbIsotropic.setItem(rowIndex, 9, item)
        item = QTableWidgetItem(isotropic.owner)
        self.tbIsotropic.setItem(rowIndex, 10, item)



    def removeRow(self,tableWidget:QTableWidget):
        if(tableWidget.rowCount()==0):
            return
        if(tableWidget.currentRow()<0):
            return
        row_position=tableWidget.currentRow()
        tableWidget.removeRow(row_position)
        pass

    def applyIsotropicTable(self):
        #若当前值已存在则更新，否则添加
        rowNum=self.tbIsotropic.rowCount()
        for i in range(rowNum):
            isotropicData=Isotropic()
            isotropicData.name=self.tbIsotropic.item(i,0).text()
            isotropicData.permittivity=self.tbIsotropic.item(i,1).text()
            isotropicData.permeability=self.tbIsotropic.item(i,2).text()
            isotropicData.eConductivity=self.tbIsotropic.item(i,3).text()
            isotropicData.DF=self.tbIsotropic.item(i,4).text()
            isotropicData.MF=self.tbIsotropic.item(i,5).text()
            isotropicData.owner=self.tbAnisotropic.item(i,6).text()
            self._isotropicList.append(isotropicData)
            pass
        pass

    def rowClicked(self):
        tabIndex=self.tabMedia.currentIndex()

        rowIndex=self.tbIsotropic.currentRow()
        if(rowIndex>=0):
            isotropic=self._isotropicList[rowIndex]
            self._mediaSelected=isotropic

        pass

   
    def closeEvent(self, event):
        self.sigClosed.emit()

        return super().closeEvent(event)
