class filter_base():
    vTypeList=[]
    valueKeys={}
    checkedKeys={}
    checkedKeys_multi={}
    checkedKeys_convert={}
    checkedSurfaces={} #云图切面使用
    singleChecked=True
    headers={}
    surfaceList=[]
    positionList=[]
    surfaceIndex=0 #选中的面，选中哪一个面
    positionIndex=0 #选中的位置，选中哪一个位置
    db_Convert=False #转换为db值
    db_ConvertKeys={
            "Total(l)":1
        }
    

    barKeys={} #value物理量映射到颜色条上的title
    dbMin=-250 #数据为0是的最小db值
    typeName=""
    dataObject=None#存储当前节点关联的数据对象

    
class filter_currents(filter_base):

    def __init__(self):

        self.vTypeList=["云图"]
        self.valueKeys={
            "Re(lx)":4,
            "Re(ly)":5,
            "Re(lz)":6,
            "Imag(lx)":7,
            "Imag(ly)":8,
            "Imag(lz)":9,
            "Real(l)":10,
            "Imag(l)":11,
            "Total(l)":12
            }
        self.checkedKeys={
            "Re(lx)":False,
            "Re(ly)":False,
            "Re(lz)":False,
            "Imag(lx)":False,
            "Imag(ly)":False,
            "Imag(lz)":False,
            "Real(l)":False,
            "Imag(l)":False,
            "Total(l)":True #默认选中的物理量
    }
        self.barKeys={
            "Re(lx)":"lx Real(A)",
            "Re(ly)": "ly Real(A)",
            "Re(lz)":  "lz Real(A)",
            "Imag(lx)": "Ix Imag(A)",
            "Imag(ly)": "ly Imag(A)",
            "Imag(lz)": "lz Imag(A)",
            "Real(l)": "l Real(A)",
            "Imag(l)": "l Imag(A)",
            "Total(l)":"l Total(A)",
            "Total(l)dB":"l Total(dBA)"
        }
        self.db_Convert=False #转换为db值
        self.db_ConvertKeys={
            "Total(l)":1
        } #哪些物理量允许转换为db值
        self.singleChecked=True
        self.typeName=PostFilter.dataKey_currents

        pass
class filter_nf_E(filter_base):
    
    

    def __init__(self):

        self.vTypeList=["表格","曲线","云图"]
        self.valueKeys={
            "Abs(Ex)":4,
            "Abs(Ey)":6,
            "Abs(Ez)":8,
            "Phase(Ex)":5,
            "Phase(Ey)":7,
            "Phase(Ez)":9,
            "Abs(E_total)":10,
        }
        self.checkedKeys={
            "Abs(Ex)":False,
            "Abs(Ey)":False,
            "Abs(Ez)":False,
            "Phase(Ex)":False,
            "Phase(Ey)":False,
            "Phase(Ez)":False,
            "Abs(E_total)":True
        }
        self.checkedKeys_multi={
            "Abs(Ex)":True,
            "Abs(Ey)":True,
            "Abs(Ez)":True,
            "Phase(Ex)":True,
            "Phase(Ey)":True,
            "Phase(Ez)":True,
            "Abs(E_total)":True
        }
        self.headers={ "No.":True,"X/m":True,"Y/m":True,"Z/m":True,
                "Abs(Ex)":True,"Phase(Ex)":True,
                "Abs(Ey)":True,"Phase(Ey)":True,
                "Abs(Ez)":True,"Phase(Ez)":True,
                "Abs(E_total)":True}
        self.singleChecked=False
        self.checkedDefault="Abs(E_total)"
        self.checkedSurfaces={
            "XY":True,
            "YZ":False,
            "XZ":False
        }
        self.barKeys={
            "Abs(Ex)":"Ex Abs(V/m)",
            "Abs(Ex)dB":"Ex Abs(dBV/m)",
            "Abs(Ey)": "Ey Abs(V/m)",
            "Abs(Ey)dB":"Ey Abs(dBV/m)",
            "Abs(Ez)":  "Ez Abs(V/m)",
            "Abs(Ez)dB":"Ez Abs(dBV/m)",
            "Phase(Ex)": "Ex Phase(deg)",
            "Phase(Ey)": "Ey Phase(deg)",
            "Phase(Ez)": "Ez Phase(deg)",
            "Abs(E_total)":"E_Total Abs(V/m)",
            "Abs(E_total)dB":"E_Total(dBV/m)"
        }
        self.db_Convert=False
        self.db_ConvertKeys={
            "Abs(Ex)":1,
            "Abs(Ey)":1,
            "Abs(Ez)":1,
            "Abs(E_total)":1
        }
        self.typeName=PostFilter.dataKey_nf_E
        
        pass
class filter_nf_H(filter_base):
    
    
    def __init__(self):
        self.vTypeList=["表格","曲线","云图"]
        self.valueKeys={
            "Abs(Hx)":4,
            "Abs(Hy)":6,
            "Abs(Hz)":8,
            "Phase(Hx)":5,
            "Phase(Hy)":7,
            "Phase(Hz)":9,
            "Abs(H_total)":10,
        }
        self.checkedKeys={
            "Abs(Hx)":False,
            "Abs(Hy)":False,
            "Abs(Hz)":False,
            "Phase(Hx)":False,
            "Phase(Hy)":False,
            "Phase(Hz)":False,
            "Abs(H_total)":True
        }
        self.checkedKeys_multi={
            "Abs(Hx)":True,
            "Abs(Hy)":True,
            "Abs(Hz)":True,
            "Phase(Hx)":True,
            "Phase(Hy)":True,
            "Phase(Hz)":True,
            "Abs(H_total)":True
        }
        self.headers={ "No.":True,"X/m":True,"Y/m":True,"Z/m":True,
                "Abs(Hx)":True,"Phase(Hx)":True,
                "Abs(Hy)":True,"Phase(Hy)":True,
                "Abs(Hz)":True,"Phase(Hz)":True,
                "Abs(H_total)":True}
        self.checkedDefault="Abs(H_total)"
        self.singleChecked=False

        self.checkedSurfaces={
            "XY":True,
            "YZ":False,
            "XZ":False
        }
        self.barKeys={
            "Abs(Hx)":"Hx Abs(A/m)",
            "Abs(Hx)dB":"Hx Abs(dBA/m)",
            "Abs(Hy)": "Hy Abs(A/m)",
            "Abs(Hy)dB":"Hy Abs(dBA/m)",
            "Abs(Hz)":  "Hz Abs(A/m)",
            "Abs(Hz)dB":"Hz Abs(dBA/m)",
            "Phase(Hx)": "Hx Phase(deg)",
            "Phase(Hy)": "Hy Phase(deg)",
            "Phase(Hz)": "Hz Phase(deg)",
            "Abs(H_total)":"H_Total Abs(A/m)",
            "Abs(H_total)dB":"H_Total(dBA/m)"
        }
        self.db_Convert=False
        self.db_ConvertKeys={
            "Abs(Hx)":1,
            "Abs(Hy)":1,
            "Abs(Hz)":1,
            "Abs(H_total)":1
        }
        self.typeName=PostFilter.dataKey_nf_H
        pass
class filter_emi(filter_base):
   
    def __init__(self):
        self.vTypeList=["表格","云图"]
        self.valueKeys={
            "Abs(Voltage)":4,
            "Abs(Current)":6,
            "Abs(Power)":8,
            "Phase(Voltage)":5,
            "Phase(Current)":7,
            "Phase(Power)":9,
        }
        self.checkedKeys={
            "Abs(Voltage)":False,
            "Abs(Current)":False,
            "Abs(Power)":False,
            "Phase(Voltage)":False,
            "Phase(Current)":False,
            "Phase(Power)":True,
        }
        self.checkedKeys_multi={
            "Abs(Voltage)":True,
            "Abs(Current)":True,
            "Abs(Power)":True,
            "Phase(Voltage)":True,
            "Phase(Current)":True,
            "Phase(Power)":True,
        }
        self.headers={ "No.":True,"X/m":True,"Y/m":True,"Z/m":True,
                "Abs(Voltage)":True,"Phase(Voltage)":True,
                "Abs(Current)":True,"Phase(Current)":True,
                "Abs(Power)":True,"Phase(Power)":True}
        self.singleChecked=False
        self.barKeys={
            "Abs(Voltage)":"Voltage Abs(V)",
            "Abs(Voltage)dB":"Voltage Abs(dBV)",
            "Abs(Current)": "Current Abs(A)",
            "Abs(Current)dB":"Current Abs(dBA)",
            "Abs(Power)":  "Power Abs(W)",
            "Abs(Power)dB":"Power Abs(dBW)",
            "Phase(Voltage)": "Voltage Phase(deg)",
            "Phase(Current)": "Current Phase(deg)",
            "Phase(Power)": "Power Phase(deg)",
        }
        self.db_Convert=False
        self.db_ConvertKeys={
            "Abs(Voltage)":1,
            "Abs(Current)":1,
            "Abs(Power)":1,
        }
        self.typeName=PostFilter.dataKey_emi
        pass
class filter_xyz():
    vTypeList=["Table","Cloud map"]
    valueKeys={
        "Coordinate X":1,
        "Coordinate Y":2,
        "Coordinate Z":3,
    }
    checkedKeys={
        "Coordinate X":True,
        "Coordinate Y":False,
        "Coordinate Z":False,
    }
    singleChecked=True
    def __init__(self):
        pass
class PostFilter():
    #后处理涉及的枚举值，字典列表，列标题，物理量枚举等
    dataKey_currents="currents"
    dataKey_nf_E="nf_E"
    dataKey_nf_H="nf_H"
    dataKey_emi="emi"
    resultKey_E="电场"
    resultKey_H="磁场"
    dbTitle="dB"
    dotPrecision=4
    db_PowerKey="Abs(Power)"
    # txList=[] #发射阵元列表
    # freqList=[] #频率列表
    # txIndex=0
    # freqIndex=0
    # vTypeIndex=0
    # checkedKeys:dict=None
    # checkedAxis=None
    # # checkedValue="" #当前选中的物理量 
    
    # currents=filter_currents()

    # nf_E=filter_nf_E()
    # nf_H=filter_nf_H()
    # emi=filter_emi()
    # xyz=filter_xyz()

    # filter_now:filter_base=None

    def __init__(self):
        self.txList=[] #发射阵元列表
        self.freqList=[] #频率列表
        self.txIndex=0
        self.freqIndex=0
        self.vTypeIndex=0
        self.xAxisIndex=0
    
        # self.checkedKeys:dict=None
        self.checkedAxis:dict=None
        # checkedValue="" #当前选中的物理量 
        
        self.currents=filter_currents()

        self.nf_E=filter_nf_E()
        self.nf_H=filter_nf_H()
        self.emi=filter_emi()
        self.xyz=filter_xyz()

        self.filter_now:filter_base=None
        self.data_now=None
        pass 

    
    def setCheckedValue(self,k,checked):
        pass
    def getFilterNow(self):
        return self.filter_now
        pass
    def setFilterCurrents(self):
        self.filter_now=self.currents
        self.data_now=self.dataKey_currents
        pass
    def setFilterNF_E(self):
        self.filter_now=self.nf_E
        self.data_now=self.dataKey_nf_E
        pass
    def setFilterNF_H(self):
        self.filter_now=self.nf_H
        self.data_now=self.dataKey_nf_H
        pass
    def setFilterEmi(self):
        self.filter_now=self.emi
        self.data_now=self.dataKey_emi
        pass  
     



