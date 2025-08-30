#物理场数据对象
class PF:
    objIndex=256+1
    def __init__(self):
        self.em=PF_EM()
        self.circuit=PF_Circuit()
        self.thermal=PF_Thermal()
        self.struct=PF_Struct()
        pass
class PF_EBase:
    def __init__(self):
        self.title=""
        self.used=False
        self.cal_dic=[True,False,False]
        pass
class PF_EM(PF_EBase):
    def __init__(self):
        super().__init__()
        self.title="物理场-电磁"
        self.em_pec_dic={}
        self.em_pml_dic={}
        self.em_exf_dic={}#外推面
        self.cal_dic=[True,True,True] #电磁求解域
        pass
class PF_Circuit(PF_EBase):
    def __init__(self):
        super().__init__()
        self.title="物理场-电路"
        self.circuit_source_dic={}
        self.circuit_load_dic={}
        self.cal_dic=[True,False,False] #求解域
        pass
class PF_Thermal(PF_EBase):
    def __init__(self):
        super().__init__()
        self.title="物理场-热"
        self.thermal_dirichlet_dic={}
        self.thermal_convection_dic={}
        self.thermal_radiation_dic={}
        self.thermal_source_dic={}
        self.cal_dic=[True,False,False] #求解域
        pass
class PF_Struct(PF_EBase):
    def __init__(self):
        super().__init__()
        self.title="物理场-结构"
        self.struct_force_dic={}
        self.struct_dirichlet_dic={}
        self.cal_dic=[True,False,False] #求解域
        pass
class PF_Struct_Force:
    def __init__(self):
        self.pointId=-1
        self.point_xyz=(0,0,0)
        self.force_xyz=(0,0,0)
class PF_Circuit_Source:
    def __init__(self):
        self.source_type=0 #0-线端口 1-面端口
        self.faceId=0
        self.waveType=0
        self.amplitude=1
        self.frequency:str="1"
        self.pulseWidth=0
        self.delay=0
        self.uv=(0,0)
        pass
class PF_Thermal_Base:
    def __init__(self):
        self.title=""
        self.lblTitle=""
        self.selectId=None
        self.value=None

class PF_Thermal_Dirichlet(PF_Thermal_Base):
    def __init__(self):
        super(PF_Thermal_Dirichlet,self).__init__()
        self.title="热-固定温度"
        self.lblTitle="温度"
 
class PF_Thermal_Source(PF_Thermal_Base):
    def __init__(self):
        super(PF_Thermal_Source,self).__init__()
        self.title="热源"
        self.lblTitle="功率"
class PF_Thermal_Convection(PF_Thermal_Base):
    def __init__(self):
        super(PF_Thermal_Convection,self).__init__()
        self.title="热-对流"
        self.lblTitle="对流系数"
class PF_Thermal_Radiation(PF_Thermal_Base):
    def __init__(self):
        super(PF_Thermal_Radiation,self).__init__()
        self.title="热-辐射"
        self.lblTitle="辐射率"