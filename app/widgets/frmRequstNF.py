from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import QTableWidget,QAbstractItemView,QHeaderView
from UI.ui_frmRequestNF import Ui_frmNF
from ..dataModel.nf import NF
from ..icons import sysIcons
from ..api import api_model
from .baseStyle import baseStyle
import traceback
class frmRequestNF(Ui_frmNF,QtWidgets.QMainWindow):
    sigCreate=QtCore.pyqtSignal(NF)
    sigModify=QtCore.pyqtSignal(NF)
    sigShowNF=QtCore.pyqtSignal(NF,tuple)
    sigClosed=QtCore.pyqtSignal()
    def __init__(self,parent=None,mode:int=0,nfObj:NF=None):
        super(frmRequestNF,self).__init__(parent)

        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.mode=mode
        self._nfObj=nfObj
       
        self.btnCreate.clicked.connect(self.btnCreateClick)
        self.btnAdd.clicked.connect(self.btnAddClick)
        self.btnClose.clicked.connect(self.close)
        self.btnAddRow.clicked.connect(lambda:self.addRow(self.tbPoints))
        self.btnRemoveRow.clicked.connect(lambda:self.removeRow(self.tbPoints))

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        self.tabWidget.tabBar().setVisible(False)

        # self.groupBox.setStyleSheet("QGroupBox:title{left:5px}")

        self.onLoad(nfObj)
        self.initPointsTable(self.tbPoints)

        self.txtU_start.textChanged.connect(self.setNum)
        self.txtU_end.textChanged.connect(self.setNum)
        self.txtU_inc.textChanged.connect(self.setNum)
        self.txtV_start.textChanged.connect(self.setNum)
        self.txtV_end.textChanged.connect(self.setNum)
        self.txtV_inc.textChanged.connect(self.setNum)
        self.txtN_start.textChanged.connect(self.setNum)
        self.txtN_end.textChanged.connect(self.setNum)
        self.txtN_inc.textChanged.connect(self.setNum)
        # self.chkShowNF.stateChanged.connect(self.setNum)
        # self.cbxAxisType.currentIndexChanged.connect(self.setAxisType)
        self.cbxPointType.currentIndexChanged.connect(self.setPointType)
        

    def onLoad(self,nfObj:NF=None):
        self.groupBox.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupBox_2.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupBox_3.setStyleSheet("QGroupBox:title{left:5px}")
        self.groupBox_4.setStyleSheet("QGroupBox:title{left:5px}")
        # self.groupBox_5.setStyleSheet("QGroupBox:title{left:0px}")
        self.setPointType()#切换为正确的点类型界面
        baseTitle=""
        titleMode="观察点 "
        str_btnCreate="创建"
        str_btnAdd="新增"
        str_btnClose="退出"
        if(self.mode==1):
            titleMode="观察点 "
            str_btnCreate="确定"
            str_btnAdd="应用"
            str_btnClose="取消"
        self.setWindowTitle(titleMode+baseTitle)
        self.btnCreate.setText(str_btnCreate)
        self.btnAdd.setText(str_btnAdd)
        self.btnClose.setText(str_btnClose)

        defaultV="0.0"

        self.txtU_start.setText(defaultV)
        self.txtU_end.setText(defaultV)
        self.txtU_inc.setText(defaultV)

        self.txtV_start.setText(defaultV)
        self.txtV_end.setText(defaultV)
        self.txtV_inc.setText(defaultV)

        self.txtN_start.setText(defaultV)
        self.txtN_end.setText(defaultV)
        self.txtN_inc.setText(defaultV)

        self.txtName.setText(NF.titlePrefix+str(NF.currentIndex))
        if(nfObj!=None):
            self.txtU_start.setText(str(nfObj.uStart))
            self.txtU_end.setText(str(nfObj.uEnd))
            self.txtU_inc.setText(str(nfObj.uIncrement))

            self.txtV_start.setText(str(nfObj.vStart))
            self.txtV_end.setText(str(nfObj.vEnd))
            self.txtV_inc.setText(str(nfObj.vIncrement))

            self.txtN_start.setText(str(nfObj.nStart))
            self.txtN_end.setText(str(nfObj.nEnd))
            self.txtN_inc.setText(str(nfObj.nIncrement))

            
            self.txtName.setText(nfObj.title)
            
            # if(hasattr(nfObj,"show")):
            #     self.chkShowNF.setChecked(nfObj.show)
            # else:
            #     self.chkShowNF.setChecked(True) 
            
            # if(hasattr(nfObj,"axisType")):
            #     self.cbxAxisType.setCurrentIndex(nfObj.axisType)
            if(hasattr(nfObj,"pointType")):
                self.cbxPointType.setCurrentIndex(nfObj.pointType)
                self.setPointType()
            if(hasattr(nfObj,"pointList")):
                self.fillPointList(nfObj.pointList)
            self.setNum()
            if(nfObj is not None):
                self.sigShowNF.emit(nfObj,NF.color_highlight)
            
        pass
    def setAxisType(self):
        try:
            # axisType=self.cbxAxisType.currentIndex()
            nfObj=self.getNF()
            self.sigShowNF.emit(nfObj,NF.color_highlight)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"电磁环境","请输入正确的参数"+str(e))

        
        pass
    def setPointType(self):
        pointType=self.cbxPointType.currentIndex()
        for i in range(self.tabWidget.count()):
            if i != pointType:
                self.tabWidget.setTabVisible(i, False)
            else:
                self.tabWidget.setTabVisible(i, True)

    def initPointsTable(self,tableWidget:QTableWidget):
        tableWidget.setColumnWidth(0,100)
        tableWidget.setColumnWidth(1,100)
        tableWidget.setColumnWidth(2,100)
        
        tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        tableWidget.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px; }
                                      QTableWidget::item { border: 1px solid rgb(100,100,100);margin:1px; }
                                      QTableWidget::item:selected { border: 2px solid rgb(78,201,176); 
                                      selection-color: rgb(0,0,0);
                                 }

                                      """)
        tableWidget.horizontalHeader().setHighlightSections(False)
        tableWidget.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        tableWidget.setFont(self._font)
        pass
    def addRow(self,tableWidget:QTableWidget):
        try:
            nfObj=self.getNF()
            self.sigShowNF.emit(nfObj,NF.color_highlight)
        except Exception as e:
            pass
        row_index=tableWidget.rowCount()
        tableWidget.insertRow(row_index)
        tableWidget.setRowHeight(row_index,baseStyle.rowHeight)
        tableWidget.setCurrentCell(row_index,0)
        pass
    def removeRow(self,tableWidget:QTableWidget):
        #删除选中行
        row_index=tableWidget.currentRow()
        if(row_index>=0):
            tableWidget.removeRow(row_index)
        try:
            nfObj=self.getNF()
            self.sigShowNF.emit(nfObj,NF.color_highlight)
        except Exception as e:
            pass
        pass
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

    
    def btnCreateClick(self):
        try:
            if(self.mode==0):
                self.actionCreate()
            else:
                self.actionOK()
            self.close()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self,"电磁环境","请输入正确的参数"+str(ex))
       
        pass
    def btnAddClick(self):
        try:
            if(self.mode==0):
                self.actionAdd()
            else:
                self.actionApply()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self,"电磁环境","请输入正确的参数"+str(ex))
        pass
    def actionCreate(self):
        nfObj=self.getNF()
        self.sigCreate.emit(nfObj)
        pass
    def actionOK(self):
        nfObj=self.getNF()
        self.sigModify.emit(nfObj)
        pass
    def actionAdd(self):
        nfObj=self.getNF()
        self.sigCreate.emit(nfObj)
        self.onLoad()
        pass
    def actionApply(self):
        nfObj=self.getNF()
        self.sigModify.emit(nfObj)
        self.sigShowNF.emit(nfObj,NF.color_highlight)
        pass
    def getNF(self):
        nfObj=self._nfObj
        if(nfObj==None):
            nfObj=NF()
        nfObj.name=self.txtName.text()
        nfObj.title=self.txtName.text()
        nfObj.axisType=0
        nfObj.pointType=self.cbxPointType.currentIndex()
        nfObj.show=False
        if(nfObj.pointType==0):
            nfObj.uStart=float(self.txtU_start.text())
            nfObj.uEnd=float(self.txtU_end.text())
            nfObj.uIncrement=float(self.txtU_inc.text())

            nfObj.vStart=float(self.txtV_start.text())
            nfObj.vEnd=float(self.txtV_end.text())
            nfObj.vIncrement=float(self.txtV_inc.text())

            nfObj.nStart=float(self.txtN_start.text())
            nfObj.nEnd=float(self.txtN_end.text())
            nfObj.nIncrement=float(self.txtN_inc.text())
        else:
            code,message,data=self.getPointList()
            if(code!=1):
                raise Exception(message)
            nfObj.pointList=data

        self._nfObj=nfObj
        return nfObj
    def setNum(self):
        try:
            obj=self.getNF()
            self.sigShowNF.emit(obj,NF.color_highlight)
                    

            self.txtU_n.setText(str(self.getNum(obj.uStart,obj.uEnd,obj.uIncrement)))
            self.txtV_n.setText(str(self.getNum(obj.vStart,obj.vEnd,obj.vIncrement)))
            self.txtN_n.setText(str(self.getNum(obj.nStart,obj.nEnd,obj.nIncrement)))
            
        except Exception as e:
            traceback.print_exc()
            pass
    def getNum(self,start:float,end:float,inc:float):
        threshold=1e-6
        if(abs(start-end)<threshold):
            return 1
        else:
            if(inc==0):
                return 2
            else:
                return int((end-start)/inc)+1
    def closeEvent(self, event):
        if(self._nfObj!=None):
            self.sigShowNF.emit(self._nfObj,NF.color_default)
        super(frmRequestNF, self).closeEvent(event)
    
  