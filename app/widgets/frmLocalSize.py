from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem,QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal,QSize,QStringListModel,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem,QFont,QIcon,QPixmap
from UI.ui_frmLocalSize import Ui_frmLocalSize
from typing import List,Tuple
from ..icons import sysIcons
class frmLocalSize(Ui_frmLocalSize,QtWidgets.QMainWindow):
    sigLocalSize=QtCore.pyqtSignal(dict)
    def __init__(self,parent=None,faceIdList:List[int]=None):
        super(frmLocalSize,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self._faceIdList:List[int]=faceIdList
        self._faceSizeDic={}#尺寸设置字典 key-value:faceId-size
        self.dataIndex=Qt.UserRole+1
        self.faceModel=QStandardItemModel()
        self.onLoad()
        self.btnCancel.clicked.connect(self.close)
        self.chxLocal.stateChanged.connect(self.setLocalEnable)
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.treeView.clicked.connect(self.itemClick)

        
       
    def sig_selectFace(self,faceId:int):
        if(faceId in self._faceIdList):
            self._faceIdList.remove(faceId)
        else:
            self._faceIdList.append(faceId)
        self.faceModel.removeRows(0,self.faceModel.rowCount())
        self.initTreeView(self._faceIdList)
        pass
    def initTreeView(self,faceIdList:List[int]):
        self.treeView.setModel(self.faceModel)
        self.treeView.setHeaderHidden(True)
        self.treeView.setIndentation(5)
        # self.treeView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.treeView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        if(faceIdList is not None):
            for f in faceIdList:
                item=QStandardItem("Face:"+str(f))
                item.setData(f,self.dataIndex)
                # item.setFont(QFont("Arial",12))
                item.setCheckable(True)
                
                item.setEditable(False)
            
                # item.setData(f,self.dataIndex)
                self.faceModel.appendRow(item)
                # self.treeView.setIndexWidget(self.faceModel.indexFromItem(item),QCheckBox())
            
            pass
        pass
    def onLoad(self):
        self.txtLocalSize.setDisabled(True)
        self.initTreeView(self._faceIdList)
        self.treeView.setStyleSheet("{ padding-top: 20px; }")
        
        pass
    def setLocalEnable(self):
        if(self.chxLocal.isChecked()):
            self.txtLocalSize.setDisabled(False)
        else:
            self.txtLocalSize.setDisabled(True)

    def actionApply(self):
        try:
            msgBox=QtWidgets.QMessageBox(self)
            msgBox.setIconPixmap(QPixmap())
            msgBox.setWindowTitle("Mesh size")
            if(not self.chxLocal.isChecked()):
                msgBox.setText("请先启用设置尺寸\n[选中Local mesh size]")
                msgBox.exec_()
                return False
            maxh=float(self.txtLocalSize.text())
            if(maxh>0):
                for item in self.treeView.selectedIndexes():
                    self._faceSizeDic[item.data(self.dataIndex)]=maxh
                self.sigLocalSize.emit(self._faceSizeDic)
                msgBox.setText("设置尺寸成功          ")
                msgBox.exec_()
                return True
                # msgBox.setWindowTitle("Mesh size")
                # msgBox.about(self,"Mesh size","设置尺寸成功")
            else:
                msgBox.setText("设置尺寸错误，尺寸必须是正数")
                msgBox.exec_()
                return False
                # QtWidgets.QMessageBox.warning(self,"Mesh size","设置尺寸错误，尺寸必须是正数")

        except Exception as e:
            msgBox.setText("设置尺寸错误，尺寸必须是正数"+str(e))
            msgBox.exec_()
            return False
            # QtWidgets.QMessageBox.warning(self,"Mesh size","设置尺寸错误，尺寸必须是正数"+str(e))
        pass
    def actionOK(self):
        if(self.actionApply()):
            self.close()
        pass
    def itemClick(self,index): 
        # checked = (index.data(Qt.CheckStateRole) == Qt.Checked)
        # item = self.faceModel.itemFromIndex(index)
        
        # if item is not None:
        #     item.setData(checked, Qt.UserRole)
        smodel=self.treeView.selectionModel()
        smodel.select(index,QtCore.QItemSelectionModel.SelectionFlag.Toggle)

        # selected_indexes = self.treeView.selectionModel().selectedIndexes()
        # selected_items = []

        # for index in selected_indexes:
        #     item = self.faceModel.itemFromIndex(index)

        #     if item is not None:
        #         selected_items.append(item.text())

        # print("Selected Items:", selected_items)



            