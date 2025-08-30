from ..theme import theme_ui
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmMediaLibrary import Ui_frmMediaLIbrary
from ..icons import sysIcons

from ..dataModel.media import Media,Dielectric,Metal,MediaItem
from ..api import api_writer
import uuid
ROW_HEIGHT=20
screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

class frmMediaLibrary(Ui_frmMediaLIbrary,QtWidgets.QMainWindow):
    sigClosed=QtCore.pyqtSignal(list)
  
    def __init__(self,parent=None,mediaItemList:list=None,media2Modify:MediaItem=None):
        super(frmMediaLibrary,self).__init__(parent)
        # self.setStyleSheet(theme_ui.baseWidgetStyle)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)

    
        
        self._currentMediaType:str=None
        self._currentItemIndex:int=-1#选中行时，赋值，并且使用这个mediaItem
        self._mediaItemlList:list[MediaItem]=mediaItemList
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.btnCancel.clicked.connect(self.close)
        # self.btnOK.clicked.connect(self.btnOKClick)
        
        self.btnAddFreq.clicked.connect(self.addRow)
        self.btnRemoveFreq.clicked.connect(self.removeRow)
        # self.tbLibrary.itemSelectionChanged.connect(self.librarySelectionChanged)
        self.tbLibrary.itemClicked.connect(self.rowClicked)
        # self.tbFreqList.itemSelectionChanged.connect(self.freqListSelectionChanged)
        # self.tbFreqList.clicked.connect(self.freqListSelectionChanged)
        self.btnAddMedia.clicked.connect(self.addMediaItem)
        self.btnDeleteMedia.clicked.connect(self.deleteMediaItem)
        self.btnOK.clicked.connect(self.actionOK)

        self.onLoad()
        self.txtFilter.textChanged.connect(self.filterChanged) 
        self.rdbSimple.clicked.connect(self.hideGroupMode)
        self.rdbAdvanced.clicked.connect(self.showGroupMode)    

    def onLoad(self):
        self.initToolButton()
        self.initLibraryTable()
        self.initFreqListTable()
        self.fillLibrary(self._mediaItemlList)
        # self.tbLibrary.selectRow(0)
        # self.rowClicked()
        self.hideGroupMode()
        # self._font.setPixelSize(16)
        # self.setFont(self._font)
        # self.groupBox_2.font().setPointSize(12)
        # print("frmMediaLibrary",self.font().pointSize())
        # print("groupbox2",self.groupBox_2.font().pointSize())


        self.tbFreqList.setFont(self._font)
        self.tbLibrary.setFont(self._font)
        # self.groupBox_2.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupMediaList.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupModel.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupFreq.setStyleSheet("QGroupBox:title{left:5px}")
        

        pass
 
    def hideGroupMode(self):
        self.groupModel.setVisible(False)
        self.rdbSimple.setChecked(True)
        self.setMinimumSize(0,0)
        self.setMaximumSize(1000,1000)
        # self.tbLibrary.resize(self.tbLibrary.width(),self.tbLibrary.height()-100)
        # self.btnNew.move(self.btnNew.x(),self.tbLibrary.geometry().y()+self.tbLibrary.height()+10)
        # self.btnOK.move(self.btnOK.x(),self.btnNew.y())
        # self.btnDeleteMedia.move(self.btnDeleteMedia.x(),self.btnNew.y())
     
        self.resize(self.width()-self.groupModel.width(),self.height())
        self.setFixedSize(self.width(), self.height())
        
        pass
    def showGroupMode(self):
        if(self.groupModel.isVisible()):
            return
        self.setMinimumSize(0,0)
        self.setMaximumSize(1000,1000)
        self.groupModel.setVisible(True)
        self.rdbAdvanced.setChecked(True)
        # self.tbLibrary.resize(self.tbLibrary.width(),self.tbLibrary.height()+100)
        # self.btnNew.move(self.btnNew.x(),self.tbLibrary.geometry().y()+self.tbLibrary.height()+10)
        # self.btnOK.move(self.btnOK.x(),self.btnNew.y())
        # self.btnDeleteMedia.move(self.btnDeleteMedia.x(),self.btnNew.y())
        # print("before",self.height())
        
        self.resize(self.width()+self.groupModel.width(),self.height())
        self.setFixedSize(self.width(), self.height())
        # print("after",self.height())
        # print("x,y",SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_WIDTH-self.width(),SCREEN_HEIGHT-self.height())
        # self.move((SCREEN_WIDTH-self.width())/2
        #           ,(SCREEN_HEIGHT-self.height()-60)/2)
        
        pass
    def disableEdit(self):
        self.btnDeleteMedia.setEnabled(False)
        self.groupModel.setEnabled(False)
        pass
    def enableEdit(self):
        self.btnDeleteMedia.setEnabled(True)
        self.groupModel.setEnabled(True)
        pass
    def fillLibrary(self,mediaItemList:list):
        mList:list[MediaItem]=mediaItemList
        self.tbLibrary.setRowCount(0)
        if(mList!=None and len(mList)>0):
            rowNum=len(mList)
            self.tbLibrary.setRowCount(rowNum)
            for i in range(rowNum):
                media:Media=mList[i].media
                item = QTableWidgetItem(str(media.type))
                self.tbLibrary.setItem(i, 0, item)
                item = QTableWidgetItem(str(media.name))
                self.tbLibrary.setItem(i, 1, item)
                item = QTableWidgetItem(str(media.owner))
                self.tbLibrary.setItem(i, 2, item)
        pass

    def initFreqListTable(self):
        # self.tbFreqList.setColumnCount(5)
        # self.tbFreqList.setHorizontalHeaderLabels(Media.columnsDielectric)
        self.setDielectricColumns()
        self.tbFreqList.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
    
        self.tbFreqList.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px; }
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
        
        # self.tbFreqList.horizontalHeader().setStyleSheet("QHeaderView::section {border-bottom: 1px solid rgb(200,200,200);}")

    def initLibraryTable(self):
        
        self.tbLibrary.setColumnCount(3)

        self.tbLibrary.setColumnWidth(0,80)
        self.tbLibrary.setColumnWidth(1,80)
        self.tbLibrary.setColumnWidth(2,80)
        
        self.tbLibrary.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbLibrary.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbLibrary.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # self.tbLibrary.setVerticalHeaderLabels(["Type","Media name","From"])
        self.tbLibrary.setHorizontalHeaderLabels(Media.columns)
        self.tbLibrary.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        # self.tbLibrary.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tbLibrary.setAlternatingRowColors(True)
        self.tbLibrary.horizontalHeader().setHighlightSections(False)

        self.tbLibrary.setStyleSheet("""
                                    QHeaderView::section { font-size: 14px; }

                                    
                                    QTableWidget::item:selected { 
                                     background-color: rgb(188,220,244);
                                     color: rgb(0,0,0);
                                     border:0px;
                                     }
                                    selection-color: rgb(0,0,0);

                                     """
                                     )
        # self.tbLibrary.setFont(self._font)


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
        
        
    def initToolButton(self):
       
        self.btnNew.setPopupMode(QToolButton.InstantPopup)
        font=self.btnNew.font()
        font.setPixelSize(14)
        font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.btnNew.setFont(font)
       
        self.btnNew.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btnNew.setText("创建")
        # self.btnNew.setFont(font)
        # self.dropdown_button.setStyleSheet("QToolButton::menu-indicator:image{subcontrol-position: right center;}")
        self.btnNew.setStyleSheet(
            '''
             QToolButton {
                padding: 5px;
                font-size: 14px;
            }
            QToolButton::menu-indicator{
                
                color:red;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                min-width: 20px;
                min-height: 20px;
                margin-right: 50px;
                padding-right: 50px;
                
                
            }
           

            '''
        )

        # 创建一个下拉菜单
        self.dropdown_menu = QMenu(self.btnNew)
        self.dropdown_menu.setFont(self._font)

        # 添加一些菜单项
        action1 = QAction(Media.dielectric_zh, self,triggered=self.newDielectric)
        action2 = QAction(Media.metal_zh, self,triggered=self.newMetal)

        self.dropdown_menu.addAction(action1)
        self.dropdown_menu.addAction(action2)

        # 将下拉菜单与按钮关联
        self.btnNew.setMenu(self.dropdown_menu)
   
    def rowClicked(self):
        row=self.tbLibrary.currentRow()
        mediaItem=self._mediaItemlList[row]
        self._currentItemIndex=row
        self.enableEdit()
        if(mediaItem.media.owner==Media.sysOwner):
            self.disableEdit()
        if(mediaItem.media.type==Media.dielectric):
            self.initDielectric(mediaItem)
        elif(mediaItem.media.type==Media.metal):
            self.initMetal(mediaItem)
        self.txtMediaName.setFocus()
        self.showGroupMode()
        pass
    def setDielectricColumns(self):
        self.tbFreqList.setColumnCount(len(Dielectric.columns))
        self.tbFreqList.setHorizontalHeaderLabels(Dielectric.columns)
        self.tbFreqList.setColumnWidth(0,80)
        self.tbFreqList.setColumnWidth(1,80)
        self.tbFreqList.setColumnWidth(2,50)
        self.tbFreqList.setColumnWidth(3,75)
        self.tbFreqList.setColumnWidth(4,50)
        self.tbFreqList.setColumnHidden(0,False)#当是介质时，显示频率列
    def setMetalColumns(self):
        self.tbFreqList.setColumnCount(len(Metal.columns))
        self.tbFreqList.setHorizontalHeaderLabels(Metal.columns)
        self.tbFreqList.setColumnWidth(0,110)
        self.tbFreqList.setColumnWidth(1,200)
        self.tbFreqList.setColumnHidden(0,True)#当是金属时，隐藏频率列

    def newDielectric(self):
        self._currentMediaType=Dielectric.type
        self._currentItemIndex=-1
        self.txtMediaName.setText("")
        self.groupModel.setTitle(Dielectric.title)
        
        self.tbFreqList.setRowCount(0)
        self.tbFreqList.setRowCount(1)
        self.tbFreqList.setRowHeight(0, ROW_HEIGHT)
        self.setDielectricColumns()
        
        self.showGroupMode()
        self.enableEdit()
        self.txtMediaName.setFocus()
        self.tbLibrary.clearSelection()
        self.btnAddFreq.setVisible(True)
        self.btnRemoveFreq.setVisible(True) 
       
        pass
    def newMetal(self):
        self._currentMediaType=Metal.type
        self._currentItemIndex=-1
        self.txtMediaName.setText("")
        self.groupModel.setTitle(Metal.title)
        self.groupFreq.setTitle("")
        self.tbFreqList.setRowCount(0)
        self.tbFreqList.setRowCount(1)
        self.tbFreqList.setRowHeight(0, ROW_HEIGHT)
        self.setMetalColumns()
        
        self.showGroupMode()
        self.enableEdit()
        self.txtMediaName.setFocus()
        self.tbLibrary.clearSelection()
        self.btnAddFreq.setVisible(False)
        self.btnRemoveFreq.setVisible(False)
        pass
    def initDielectric(self,mediaItem:MediaItem):
        media_base:Media=mediaItem.media
        self.txtMediaName.setText(media_base.name)
        self.groupModel.setTitle(Dielectric.title)
        self._currentMediaType=Dielectric.type
        self.btnAddFreq.setVisible(True)
        self.btnRemoveFreq.setVisible(True)

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
            item = QTableWidgetItem(media.permittivity_real)
            self.tbFreqList.setItem(i, 1, item)
            item = QTableWidgetItem(media.permittivity_imag)
            self.tbFreqList.setItem(i, 2, item)
            item = QTableWidgetItem(media.permeability_real)
            self.tbFreqList.setItem(i, 3, item)
            item = QTableWidgetItem(media.permeability_imag)
            self.tbFreqList.setItem(i, 4, item)

        

        pass
    def initMetal(self,mediaItem:MediaItem):    
        media_base=mediaItem.media
        self.txtMediaName.setText(media_base.name)
        self.groupModel.setTitle(Metal.title)
        self.btnAddFreq.setVisible(False)
        self.btnRemoveFreq.setVisible(False)
        self._currentMediaType=Metal.type
        self.setMetalColumns()
        self.tbFreqList.setRowCount(0)


        rowNum=len(mediaItem.freqList)
        self.tbFreqList.setRowCount(rowNum)
        for i in range(rowNum):
            media:Metal=mediaItem.freqList[i]
            self.tbFreqList.setRowHeight(i, ROW_HEIGHT)
            item = QTableWidgetItem(media.frequency)
            self.tbFreqList.setItem(i, 0, item)
            item = QTableWidgetItem(media.conductivity)
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
    def addMediaItem(self):
        '''
        添加介质
        '''
        code,message,mItem=self.getMediaItem()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"media input error",message)
            return
        if(self._currentItemIndex>=0):
            self._mediaItemlList[self._currentItemIndex]=mItem
        else:
            self._mediaItemlList.append(mItem)
        self._currentItemIndex=-1
        self.fillLibrary(self._mediaItemlList)
        self.tbLibrary.selectRow(self.tbLibrary.rowCount()-1)
        if(self._currentMediaType==Dielectric.type):
            self.newDielectric()
        elif(self._currentMediaType==Metal.type):
            self.newMetal()
        pass
    def getMediaItem(self):
        try:
            mItem=None
            if(self._currentItemIndex>0):
                mItem=self._mediaItemlList[self._currentItemIndex]
            else:
                mItem=MediaItem()
            media=Media()
            # media.id=str(uuid.uuid4())
            media.name=self.txtMediaName.text()
            media.type=Media.dielectric
            media.owner="user"
            mItem.media=media
            if(media.name==""):
                return(-1,"Media name can not be empty",None)
            if(self.groupModel.title()==Metal.title):
                mItem.media.type=Media.metal
            mItem.freqList=[]
            for row in range(self.tbFreqList.rowCount()):
                media=None
                if(mItem.media.type==Media.dielectric):
                    media=Dielectric()
                    media.name=mItem.media.name
                    m_freq=self.tbFreqList.item(row,0).text()
                    m_permittivity_real=self.tbFreqList.item(row,1).text()
                    m_permittivity_imag=self.tbFreqList.item(row,2).text()
                    m_permeability_real=self.tbFreqList.item(row,3).text()
                    m_permeability_imag=self.tbFreqList.item(row,4).text()

                    f_freq=float(m_freq)
                    f_permittivity_real=float(m_permittivity_real)
                    f_permittivity_imag=float(m_permittivity_imag)
                    f_permeability_real=float(m_permeability_real)
                    f_permeability_imag=float(m_permeability_imag)


                    media.frequency=m_freq
                    media.permittivity_real=m_permittivity_real
                    media.permittivity_imag=m_permittivity_imag
                    media.permeability_real=m_permeability_real
                    media.permeability_imag=m_permeability_imag
                elif(mItem.media.type==Media.metal):
                    media=Metal()
                    media.name=mItem.media.name
                    # media.frequency=float(self.tbFreqList.item(row,0).text())
                    media.frequency=-1
                    m_conductivity=self.tbFreqList.item(row,1).text()
                    f_conductivity=float(m_conductivity)
                    media.conductivity=m_conductivity   
                mItem.freqList.append(media)
            # print("get media item",mItem)
            if(len(mItem.freqList)==0):
                return(-1,"Please add frequency and attribute value",None)
            return (1,"success",mItem)
        except Exception as e:
            # QtWidgets.QMessageBox.about(self,"media input error","please input float value"+str(e))
            return(-1,"Frequency and attribute value should be float\n"+str(e),None)

    def filterChanged(self):
        filter=self.txtFilter.text()
        if(filter==""):
            self.fillLibrary(self._mediaItemlList)
        else:
            filter=filter.lower()
            mList:list[MediaItem]=[]
            for item in self._mediaItemlList:
                if(filter in item.media.name.lower()):
                    mList.append(item)
            self.fillLibrary(mList)
        pass
    def deleteMediaItem(self):
        row=self.tbLibrary.currentRow()
        if(row<0):#没有选中行
            return
        self._mediaItemlList.pop(row)
        self.fillLibrary(self._mediaItemlList)
        rowNum=self.tbLibrary.rowCount()
        if(rowNum>0):
            row_select=0
            if(row==rowNum):
                row_select=row-1
            else:
                row_select=row
            self.tbLibrary.selectRow(row_select)
            self.rowClicked()
        else:
            if(self._currentMediaType==Dielectric.type):
                self.newDielectric()
            elif(self._currentMediaType==Metal.type):
                self.newMetal()
        # self.tbLibrary.selectRow(0)
        # self.rowClicked()
        pass
    def actionOK(self):
        self.close()
    def closeEvent(self, event):
        # print("media closed")
        self.sigClosed.emit(self._mediaItemlList)
        # api_writer.write_mediaLibrary("D:/m.txt",self._mediaItemlList)
        return super().closeEvent(event)
