from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget,QAbstractItemView,QHeaderView
from UI.ui_frmFrequency2 import Ui_frmFrequency2
from ..dataModel.frequency import Frequency
from ..icons import sysIcons
from .baseStyle import baseStyle
class frmFrequency2(Ui_frmFrequency2,QtWidgets.QMainWindow):
    sigModify=QtCore.pyqtSignal(Frequency)
    def __init__(self,parent=None,freqObj:Frequency=None):
        super(frmFrequency2,self).__init__(parent)
       
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnCancel.clicked.connect(self.close)
        self.btnOK.clicked.connect(self.btnOKClick)

        self.txtStart.textChanged.connect(self.setFreqNum)
        self.txtEnd.textChanged.connect(self.setFreqNum)
        self.txtIncrement.textChanged.connect(self.setFreqNum)
        self.cbxFreqType.currentIndexChanged.connect(self.setFreqType)
        self.btnAdd.clicked.connect(lambda:self.addRow(self.tbFreqList))
        self.btnRemove.clicked.connect(lambda:self.removeRow(self.tbFreqList))
      
        self.frequency=freqObj

        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        self.tabWidget.tabBar().setVisible(False)
        self.onLoad()
    def onLoad(self):
        self.cbxFreqType.setCurrentIndex(0)
        self.setFreqType()
        self.initFreqTable(self.tbFreqList)
        if(self.frequency!=None):
            if(not hasattr(self.frequency,"reflection")):
                self.frequency.reflection="1"
            self.txtStart.setText(str(self.frequency.start))
            self.txtEnd.setText(str(self.frequency.end))
            self.txtIncrement.setText(str(self.frequency.increment))
            self.txtReflection.setText(str(self.frequency.reflection))
            self.txtTransmission.setText(str(self.frequency.transmission))
            self.txtDiffraction.setText(str(self.frequency.diffraction))
            self.checkBox.setChecked(self.frequency.store_current)
            self.setFreqNum()
            if(hasattr(self.frequency,"freqType")):
                self.cbxFreqType.setCurrentIndex(self.frequency.freqType)
                self.setFreqType()
            if(hasattr(self.frequency,"discreteList")):
                self.fillFreqList(self.frequency.discreteList)
        self.txtStart.setFocus()
        
    def setFreqType(self):
        freqType=self.cbxFreqType.currentIndex()
        for i in range(self.tabWidget.count()):
            if i != freqType:
                self.tabWidget.setTabVisible(i, False)
            else:
                self.tabWidget.setTabVisible(i, True)
    def initFreqTable(self,tableWidget:QTableWidget):
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
        tableWidget.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        tableWidget.setFont(self._font)
        pass
    def addRow(self,tableWidget:QTableWidget):
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
        pass
    def fillFreqList(self,freqList:list=[]):
        for freq in freqList:
            row_index=self.tbFreqList.rowCount()
            self.tbFreqList.insertRow(row_index)
            self.tbFreqList.setRowHeight(row_index,baseStyle.rowHeight)
            item=QtWidgets.QTableWidgetItem(freq)
            self.tbFreqList.setItem(row_index,0,item)
    def getFreqList(self):
        try:
            freqList=[]
            f_list=[]
            for i in range(self.tbFreqList.rowCount()):
                freq=self.tbFreqList.item(i,0).text()
                t_freq=float(freq)
                f_list.append(t_freq)
                freqList.append(freq)
            #检查是否有重复的频率
            f_list.sort()
            for i in range(len(f_list)-1):
                if(f_list[i]==f_list[i+1]):
                    return (-1,"离散频率列表中有重复的频率，请检查数据",[])
            return (1,"success",freqList)
        except Exception as e:
            return (-1,"频率必须是数字类型，请检查数据"+str(e),[])
        pass
         
            
    def btnOKClick(self):
        freqObj=self.getFrequency()
        if(freqObj!=None):
            self.sigModify.emit(freqObj)
            self.close()
    def getFrequency(self):
        freqObj=self.frequency
        if(freqObj==None):
            freqObj=Frequency()
        freqObj.freqType=self.cbxFreqType.currentIndex()

        if(freqObj.freqType==0):
            str_start=self.txtStart.text()
            str_end=self.txtEnd.text()
            str_increment=self.txtIncrement.text()
            str_reflection=self.txtReflection.text()
            str_transmission=self.txtTransmission.text()
            str_diffraction=self.txtDiffraction.text()
            
            if(str_start==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入起始频率")
                return None
            if(str_end==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入截止频率")
                return None
            if(str_increment==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入频率步进值")
                return None
            if(str_reflection==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入反射次数")
                return None
            if(str_transmission==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入透射次数")
                return None
            if(str_diffraction==""):
                QtWidgets.QMessageBox.warning(self,"频率","请输入绕射次数")
                return None
            try:
                start=float(str_start)
                end=float(str_end)
                fincrement=float(str_increment)
                reflection=int(str_reflection)
                transmission=int(str_transmission)
                diffraction=int(str_diffraction)
                freqObj.start=str_start
                freqObj.end=str_end
                freqObj.increment=str_increment
                freqObj.reflection=reflection
                freqObj.transmission=transmission
                freqObj.diffraction=diffraction
                freqObj.store_current=self.checkBox.isChecked()
                return freqObj
            except Exception as e:
                QtWidgets.QMessageBox.warning(self,"频率","起始频率/截止频率/步进值必须是有效数字"+str(e))
                return None
        else:
            code,message,freqList=self.getFreqList()
            if(code!=1):
                QtWidgets.QMessageBox.warning(self,"频率",message)
                return None
            freqObj.discreteList=freqList
            return freqObj
    def setFreqNum(self):
        #根据频率起始和步进计算频率个数
        try:
            f_tolerance=1e-6
            fStart=float(self.txtStart.text())
            fEnd=float(self.txtEnd.text())
            fIncrement=float(self.txtIncrement.text())
       
            fNum=1
            if(abs(fStart-fEnd)>f_tolerance):
                fNum=2
                if(abs(fIncrement)>f_tolerance):#终点与起点不同
                    fNum=int((fEnd-fStart)/fIncrement)+1
        
            self.txtFreqNum.setText(str(fNum))
            pass
        except Exception as e:
            pass

        


            


    