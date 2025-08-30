from PyQt5 import QtCore,QtWidgets
from UI.ui_frmNFFilter import Ui_frmNFFilter
from ..dataModel.power import Power
from ..icons import sysIcons
class frmFilter(Ui_frmNFFilter,QtWidgets.QMainWindow):
    sigFilter=QtCore.pyqtSignal(list,int)#pointList,面索引，分量索引
    def __init__(self,parent=None,nfList=None):
        super(frmFilter,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnClose.clicked.connect(self.close)
        self.btnApply.clicked.connect(self.btnApplyClick)
        self._nfList=nfList


        self.onLoad()
        self.cbxFreq.currentIndexChanged.connect(self.freqChanged)
        self.cbxPlotType.currentIndexChanged.connect(self.plotTypeChanged)
        self.cbxVType.currentIndexChanged.connect(self.vTypeChanged)

    def onLoad(self):
        self.data2fill()
        self.fillValueType()
        pass
    def data2fill(self):
        sbr_nfList=self._nfList
        freqList=[]
        plotList=[]
        
        pointList=sbr_nfList[0][1]
        xNum=len(list(set(t[0] for t in pointList)))
        yNum=len(list(set(t[1] for t in pointList)))
        zNum=len(list(set(t[2] for t in pointList)))
        dim=0 #维度数据，观察点是一个点，一条线，还是一个面
        if(xNum>1):
            dim+=1
        if(yNum>1):
            dim+=1
        if(zNum>1):
            dim+=1
        if(dim==2):
            if(xNum==1):
                plotList.append("yz")
            elif(yNum==1):
                plotList.append("xz")
            elif(zNum==1):
                plotList.append("xy")
        elif(dim==3):
            plotList.append("xy")
            plotList.append("xz")
            plotList.append("yz")
        for item in sbr_nfList:
            freqList.append("{:g}".format(item[0]))
        self.fillFreq(freqList)
        self.fillPlot(plotList)
        pass
    def fillPlot(self,plotList):
        self.cbxPlotType.clear()
        self.cbxPlotType.addItems(plotList)
    def fillFreq(self,freqList):
        self.cbxFreq.clear()
        self.cbxFreq.addItems([str(i) for i in freqList])
    def fillValueType(self):
        v_List=["Abs(Ex)","Phase(Ex)","Abs(Ey)","Phase(Ey)","Abs(Ez)","Phase(Ez)",
                "Abs(Hx)","Phase(Hx)","Abs(Hy)","Phase(Hy)","Abs(Hz)","Phase(Hz)",
                "Abs(E_Total)","Abs(H_Total)"]
        self.cbxVType.clear()
        self.cbxVType.addItems(v_List)
                
               
               

    def btnApplyClick(self):
        self.sigFilter.emit(0,0,0)
        pass
    def freqChanged(self):
        # freq=self.cbxFreq.currentText()
        # print(freq)
        pointList=self.getPointList()
        pass
    def plotTypeChanged(self):
        # plotType=self.cbxPlotType.currentText()
        # print(plotType)
        self.getPointList()
        pass
    def vTypeChanged(self):
        # vType=self.cbxVType.currentText()
        # print(vType)
        self.getPointList()
        pass
    def getPointList(self):
        freqIndex=self.cbxFreq.currentIndex()
        valueIndex=self.cbxVType.currentIndex()
        plotType=self.cbxPlotType.currentIndex()
        pointList=self._nfList[freqIndex][1]
        pointList_n= [(item[0], item[1],item[2], item[valueIndex+3]) for item in pointList]
        self.sigFilter.emit(pointList_n,plotType)

        
        pass

        
