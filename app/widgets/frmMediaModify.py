from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmMediaModify import Ui_frmMediaModify
from ..icons import sysIcons

from ..dataModel.media import Media,Dielectric,Metal,MediaItem
from ..api import api_writer
import uuid
ROW_HEIGHT=30
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmMediaModify(Ui_frmMediaModify,QtWidgets.QMainWindow):
    sigMidiaModify=QtCore.pyqtSignal(tuple)
  
    def __init__(self,parent=None,mediaData:tuple=None):
        super(frmMediaModify,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._mediaData=mediaData
        
       
        

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.btnCancel.clicked.connect(self.close)
        # self.btnOK.clicked.connect(self.btnOKClick)
        
        self.btnAddFreq.clicked.connect(self.addRow)
        self.btnRemoveFreq.clicked.connect(self.removeRow)

        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnClose.clicked.connect(self.close)

        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)

        self.onLoad()  
        
        

    def onLoad(self):
        
        self.groupBox.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupBox.setFont(self._font)

        self.initFreqListTable()
        # self.tbFreqList.setFont(self._font)
        
        if(self._mediaData!=None):
            mItem:MediaItem=self._mediaData[1]
            if(mItem.media.type==Media.dielectric):
                self.initDielectric(mItem)
            elif(mItem.media.type==Media.metal):
                self.initMetal(mItem)
                self.btnAddFreq.setVisible(False)
                self.btnRemoveFreq.setVisible(False)

        pass
    
 


    def initFreqListTable(self):
        # self.tbFreqList.setColumnCount(5)
        # self.tbFreqList.setHorizontalHeaderLabels(Media.columnsDielectric)
        self.setDielectricColumns()
        self.tbFreqList.setFont(self._font)
    
        self.tbFreqList.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        
    
        self.tbFreqList.setStyleSheet("""
                                      QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);}

                                      """)
     
        #   QTableWidget::item:selected { border: 2px solid rgb(188,220,220); }
        # self.tbFreqList.horizontalHeader().setSectionsClickable(False)
        self.tbFreqList.horizontalHeader().setHighlightSections(False)
        self.tbFreqList.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        # self.tbFreqList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.tbFreqList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbFreqList.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.tbFreqList.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
      
        pass
    def addRow(self):
        row_position=self.tbFreqList.rowCount()
        self.tbFreqList.insertRow(row_position)
        self.tbFreqList.setRowHeight(row_position, ROW_HEIGHT)
        self.tbFreqList.setCurrentCell(row_position,0)
        
        # item = QTableWidgetItem(str(""))
        # self.tbFreqList.setInputMethodHints
        
        # self.tbFreqList.setItem(row_position, 0, item)

        # self.tbFreqList.setItemDelegate(EditDelegate())
    def removeRow(self):
        row_position=self.tbFreqList.currentRow()
        self.tbFreqList.removeRow(row_position)
    def setDielectricColumns(self):
        self.tbFreqList.setColumnCount(len(Dielectric.columns))
        self.tbFreqList.setHorizontalHeaderLabels(Dielectric.columns)
        self.tbFreqList.setColumnWidth(0,60)
        self.tbFreqList.setColumnWidth(1,85)
        self.tbFreqList.setColumnWidth(2,50)
        self.tbFreqList.setColumnWidth(3,85)
        self.tbFreqList.setColumnWidth(4,50)
    def setMetalColumns(self):
        self.tbFreqList.setColumnCount(len(Metal.columns))
        self.tbFreqList.setHorizontalHeaderLabels(Metal.columns)
        self.tbFreqList.setColumnWidth(0,110)
        self.tbFreqList.setColumnWidth(1,200)
        self.tbFreqList.setColumnHidden(0,True)


    def initDielectric(self,mediaItem:MediaItem):
        media_base:Media=mediaItem.media
        self.txtMediaName.setText(media_base.name)
        # self.groupModel.setTitle(Dielectric.title)
        self._currentMediaType=Dielectric.type

        self.setDielectricColumns()
        self.tbFreqList.setRowCount(0)

        freqList:list[Dielectric]=mediaItem.freqList
        rowNum=len(freqList)
        
        self.tbFreqList.setRowCount(rowNum)
        for i in range(rowNum):
            media:Dielectric=freqList[i]
            self.tbFreqList.setRowHeight(i, ROW_HEIGHT)
            item = QTableWidgetItem(media.frequency)
            self.tbFreqList.setItem(i, 0, item)
            item = QTableWidgetItem(str(media.permittivity_real))
            self.tbFreqList.setItem(i, 1, item)
            item = QTableWidgetItem(str(media.permittivity_imag))
            self.tbFreqList.setItem(i, 2, item)
            item = QTableWidgetItem(str(media.permeability_real))
            self.tbFreqList.setItem(i, 3, item)
            item = QTableWidgetItem(str(media.permeability_imag))
            self.tbFreqList.setItem(i, 4, item)

        

        pass
    def initMetal(self,mediaItem:MediaItem):    
        media_base=mediaItem.media
        self.txtMediaName.setText(media_base.name)
        # self.groupModel.setTitle(Metal.title)
        self._currentMediaType=Metal.type
        self.setMetalColumns()
        self.tbFreqList.setRowCount(0)

        rowNum=len(mediaItem.freqList)
        self.tbFreqList.setRowCount(rowNum)
        for i in range(rowNum):
            media:Metal=mediaItem.freqList[i]
            self.tbFreqList.setRowHeight(i, ROW_HEIGHT)
            item = QTableWidgetItem("{:.2e}".format(media.frequency))
            self.tbFreqList.setItem(i, 0, item)
            item = QTableWidgetItem(str(media.conductivity))
            self.tbFreqList.setItem(i, 1, item)
        
        pass
    def freqListSelectionChanged(self):
        row=self.tbFreqList.currentRow()
        col=self.tbFreqList.currentColumn()
        item=self.tbFreqList.item(row,col)
        # print("selected",row,col)
        # if(item!=None):
        #     self.tbFreqList.editItem(item)
        # pass

    def getMediaItem(self):
        try:
            mItem:MediaItem=self._mediaData[1]
            media=Media()
            # media.id=str(uuid.uuid4())
            media.name=self.txtMediaName.text()
            media.type=Media.dielectric
            media.owner="user"
            mItem.media=media
            if(media.name==""):
                return(-1,"Media name can not be empty",None)
            if(self._currentMediaType==Metal.type):
                mItem.media.type=Media.metal
            mItem.freqList=[]
            for row in range(self.tbFreqList.rowCount()):
                media=None
                if(mItem.media.type==Media.dielectric):
                    media=Dielectric()
                    media.name=mItem.media.name
                    media.frequency=self.tbFreqList.item(row,0).text()
                    media.permittivity_real=self.tbFreqList.item(row,1).text()
                    media.permittivity_imag=self.tbFreqList.item(row,2).text()
                    media.permeability_real=self.tbFreqList.item(row,3).text()
                    media.permeability_imag=self.tbFreqList.item(row,4).text()
                elif(mItem.media.type==Media.metal):
                    media=Metal()
                    media.name=mItem.media.name
                    # media.frequency=float(self.tbFreqList.item(row,0).text())
                    media.frequency=-1
                    media.conductivity=self.tbFreqList.item(row,1).text()
                mItem.freqList.append(media)
            # print("get media item",mItem)
            if(len(mItem.freqList)==0):
                return(-1,"Please add frequency and attribute value",None)
            return (1,"success",mItem)
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"media input error","please input float value"+str(e))
            return(-1,"Frequency and attribute value should be float\n"+str(e),None)

    def actionOK(self):
        self.actionApply()
        self.close()
    def actionApply(self):
        code,msg,mItem=self.getMediaItem()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"media input error",msg)
            return
        mData=(self._mediaData[0],mItem)
        self.sigMidiaModify.emit(mData)
        pass
    def closeEvent(self, event):
        return super().closeEvent(event)
