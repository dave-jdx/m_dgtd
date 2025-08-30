from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import QComboBox,QTableWidget,QTableWidgetItem,QAbstractItemView,QHeaderView
from PyQt5.QtGui import QColor
from UI.ui_frmModelMedia import Ui_frmModelMedia
from ..dataModel.mediaN import MediaBase,Isotropic
from ..icons import sysIcons
FACE_MEDIUM_COLUMNS=["体编号","材料名称"]
FACE_TIP="Solid"
ROW_HEIGHT=30
class frmModelMedia(Ui_frmModelMedia,QtWidgets.QMainWindow):
    # sigModifyPower=QtCore.pyqtSignal(Power)
    sigMedialLibrary=QtCore.pyqtSignal()
    sigSolidClicked=QtCore.pyqtSignal(int)
    sigClosed=QtCore.pyqtSignal()
    sigMediumApply=QtCore.pyqtSignal(tuple)
    def __init__(self,parent=None,mediaList=None,medium=-1,mediumFaces={}):
        super(frmModelMedia,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent

     
        self._mediaList:list[Isotropic]=mediaList  
        # self._faceNum=faceNum 
        self._medium=medium
        self._mediumFaces=mediumFaces
        self._face_dic={}#面材质设置,{faceId,(mediaId,coatId,coatThickness,rowIndex)}
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnMore.clicked.connect(self.actionMore)
        self.tbFaces.itemClicked.connect(self.rowClicked)
        self.btnClear.clicked.connect(self.actionClearFaces)
        self.btnRemove.clicked.connect(self.actionRemoveFace)
        self.btnClose.clicked.connect(self.close)

        self._font=self.font()
        self._font.setPixelSize(14)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)
     
        self.onLoad()
       

    def onLoad(self):
        self.tbFaces.setFont(self._font)
        self.initFaceTable()
        self.fillCombobox(self.cbxMedia,self._mediaList,self._medium)
        # self.fillFaceList(self._faceNum)
        self.initFaceList(self._mediumFaces)

        self.groupBox_2.setStyleSheet("QGroupBox:title{left:5px}")
        pass
    def rowClicked(self):
        row=self.tbFaces.currentRow()
        faceId=int(self.tbFaces.item(row,0).text().replace(FACE_TIP,""))
        self.sigSolidClicked.emit(faceId-1)

        pass
    def selectSolid(self,faceId):
        '''
        模型选中一个面，没有选中的面则添加一行，有则选中
        '''
        if(self._face_dic.get(faceId) is None):#没有选中的面，则添加一行
            
            row_position=self.tbFaces.rowCount()
            self.tbFaces.insertRow(row_position)
            self.tbFaces.setRowHeight(row_position, ROW_HEIGHT)
            self.tbFaces.setCurrentCell(row_position,0)
             
            item0 = QTableWidgetItem(FACE_TIP+str(faceId+1))
            self.tbFaces.setItem(row_position, 0, item0)
            cbx=QComboBox()
            cbx.setFont(self._font)
            self.fillCombobox(cbx,self._mediaList)
            self.tbFaces.setCellWidget(row_position,1,cbx)
            
            
            # cbxT=QComboBox()
            # cbxT.setFont(self._font)
            # self.fillCombobox(cbxT,self._mediaList)
            # self.tbFaces.setCellWidget(row_position,2,cbxT)

            # txtEdit=QtWidgets.QLineEdit()
            # txtEdit.setFont(self._font)
            # self.tbFaces.setCellWidget(row_position,3,txtEdit)

            self._face_dic[faceId]=(row_position,-1)
            
        
        
        self.tbFaces.setFocus()
        rowIndex=self._face_dic[faceId][0] #行号 当前字典的第一个元素存放行号
        # self.tbFaces.item(faceId,0).setBackground(QColor(0,120,215))
        # self.tbFaces.item(faceId,1).setForeground(QColor(255,255,255))
        item=self.tbFaces.item(rowIndex,0)
        self.tbFaces.setCurrentItem(item)
        # self.tbFaces.setStyleSheet(f"QTableWidget::item:selected {{ background-color: rgb(0,120,215); color:white}}")
        self.tbFaces.selectRow(rowIndex)
        # self.tb
        pass
    def refreshMedialList(self,mList):
        '''
        更新材料库之后，刷新下拉列表，包含顶部的和行内的
        '''
    
        # self._mediaList=mList
        # self.fillCombobox(self.cbxMedia,self._mediaList,self._medium)
        # self.updateFaceList()
        pass
    def initFaceTable(self):

        self.tbFaces.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbFaces.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbFaces.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # self.tbLibrary.setVerticalHeaderLabels(["Type","Media name","From"])
        self.tbFaces.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        # self.tbLibrary.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tbFaces.setAlternatingRowColors(True)
        self.tbFaces.horizontalHeader().setHighlightSections(False)
        self.tbFaces.setRowCount(0)
        self.tbFaces.setColumnCount(2)
        self.tbFaces.setHorizontalHeaderLabels(FACE_MEDIUM_COLUMNS)
        self.tbFaces.setColumnWidth(0,100)
        self.tbFaces.setColumnWidth(1,160)
        # self.tbFaces.setColumnWidth(2,90)
        # self.tbFaces.setColumnWidth(3,90)
        pass
    def fillCombobox(self,box:QComboBox,mediaList:list,mediumIndex=-1):
        mList:list[Isotropic]=mediaList
        box.clear()
        for item in mList:
            box.addItem(item.name,item)
        box.setCurrentIndex(mediumIndex)
        pass
    def addFace(self):
        pass
    def updateFaceList(self):
        '''
        更新材料库之后，更新面列表的下拉列表内容
        '''
        for i in range(self.tbFaces.rowCount()):
            item=self.tbFaces.cellWidget(i,1)
            self.fillCombobox(item,self._mediaList,item.currentIndex())

            item2=self.tbFaces.cellWidget(i,2)
            self.fillCombobox(item2,self._mediaList,item2.currentIndex())
    def initFaceList(self,mediumFaces):
        '''
        初始化面材质设置
        '''
        self._face_dic.clear()
        self.tbFaces.setRowCount(0)
        # self.tbFaces.setRowCount(len(mediumFaces))
        for faceId in mediumFaces:
            v=mediumFaces[faceId]
            row_position=self.tbFaces.rowCount()
            self.tbFaces.insertRow(row_position)
            self.tbFaces.setRowHeight(row_position, ROW_HEIGHT)
            # self.tbFaces.setCurrentCell(row_position,0)
             
            item0 = QTableWidgetItem(FACE_TIP+str(faceId+1))
            self.tbFaces.setItem(row_position, 0, item0)

            cbx=QComboBox()
            self.fillCombobox(cbx,self._mediaList,v)
            self.tbFaces.setCellWidget(row_position,1,cbx)

            # cbxT=QComboBox()
            # self.fillCombobox(cbxT,self._mediaList,v[1])
            # self.tbFaces.setCellWidget(row_position,2,cbxT)


            # txtEdit=QtWidgets.QLineEdit()
            # txtEdit.setText(str(v[2]))
            # self.tbFaces.setCellWidget(row_position,3,txtEdit)
            self._face_dic[faceId]=(row_position,-1)


    
    def actionClearFaces(self):
        self._face_dic.clear()
        self.tbFaces.setRowCount(0)
        pass
    def actionRemoveFace(self):
        row=self.tbFaces.currentRow()
        if(row<0):
            return
        faceId=int(self.tbFaces.item(row,0).text().replace(FACE_TIP,""))-1
        if(faceId in self._face_dic):
            del self._face_dic[faceId]
        # self._face_dic.pop(faceId)
        self.tbFaces.removeRow(row)
        pass
    def actionApply(self):
        code,message,data=self.getFaceMedium()
        if(code<0):
            QtWidgets.QMessageBox.about(self,"Error",message)
            return
        self.sigMediumApply.emit(data)
    
        pass
    def actionOK(self):
        code,message,data=self.getFaceMedium()
        if(code<0):
            QtWidgets.QMessageBox.about(self,"Error",message)
            return
        self.sigMediumApply.emit(data)
        self.close()
        pass
    def actionMore(self):
        self.sigMedialLibrary.emit()
        pass
    def closeEvent(self,event):
        self.sigClosed.emit()
        return super().closeEvent(event)
    def getFaceMedium(self):
        '''
        获取面材质设置
        '''
        try:
            mediumFaces={}
            for i in range(self.tbFaces.rowCount()):
                faceId=int(self.tbFaces.item(i,0).text().replace(FACE_TIP,""))-1
                medium_f=self.tbFaces.cellWidget(i,1).currentIndex()
                # medium_coat=self.tbFaces.cellWidget(i,2).currentIndex()
                # thickness=self.tbFaces.cellWidget(i,3).text()
                # if(thickness!=""):
                #     thickness=float(thickness)
                mediumFaces[faceId]=(medium_f)
            medium=self.cbxMedia.currentIndex()
            return (1,"success",(medium,mediumFaces))
        except Exception as e:
            return (-1,str(e),None)

