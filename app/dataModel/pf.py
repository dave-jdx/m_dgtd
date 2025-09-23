#物理场数据对象
class PF:
    objIndex=256+1
    def __init__(self):
        self.em=PF_EM()
        self.circuit=PF_Circuit()
        self.thermal=PF_Thermal()
        self.struct=PF_Struct()
        self.plane_wave=PF_Plane_Wave()
        self.e_times=PF_E_Times() #迭代电势
        self.dopping=PF_Dopping()
        self.sbound=PF_SBound() #半导体边界
        pass
class PF_EBase:
    def __init__(self):
        self.title=""
        self.used=False
        self.cal_dic=[True,False,False]
        pass
class PF_SBound:#半导体边界
    def __init__(self):
        self.title="半导体边界"
        self.metal_contact_dic={} #金属接触面
        self.insulate_gate_dic={} #绝缘栅面
class PF_SBound_Metal_Contact:
    def __init__(self):
        self.title="金属接触面"
        self.faceId=None
        self.contact_type=1 #1：阳极或者源极电压的标志位；2：阴极或者漏极电压的标志位
        self.voltage:str="1" #电压,直流源幅度
class PF_SBound_Insulate_Gate:
    def __init__(self):
        self.title="绝缘栅面"
     
        self.faceId=None
        self.voltage:str="0" #电压,直流源幅度
        self.thickness:str="3e-8" #氧化层厚度  
        self.permittivity:str="4.5" #相对介电常数
        self.metal_work_function:str="4.1" #金属功函数
        pass
class PF_Dopping:
    def __init__(self):
        self.title="掺杂"
        self.dopping_analysis_dic={} #解析掺杂
        self.dopping_gaussian_dic={} #高斯掺杂
        pass
class PF_Dopping_Analysis:
    def __init__(self):
        self.title="解析掺杂"
        self.dopping_concentration:str="1e15" #杂质浓度
        self.dopping_type=0 #0-施主掺杂 1-受主掺杂
        self.dopping_bodyId=None #区域ID
        pass
class PF_Dopping_Gaussian:
    def __init__(self):
        self.title="高斯掺杂"
        self.dopping_concentration:str="1e15" #杂质浓度
        self.dopping_type=0 #0-施主掺杂 1-受主掺杂
        self.dopping_bodyId=None #区域ID
        self.dopping_faceId=None #面ID
        self.dopping_depth:str="0.000001" #掺杂深度
        pass
class PF_Plane_Wave:
    def __init__(self):
      
        self.waveType=0 # 0-不加源 1-正弦波 2-高斯脉冲 3-自定义
        self.amplitude=1
        self.frequency:str="1"
        self.pulseWidth=0
        self.delay=0

        self.theta=180
        self.phi=0
        self.eAngle=90
        pass
class PF_E_Times:
    def __init__(self):
        self.title="迭代电势"
        self.lblTitle="迭代次数"
        self.value=1
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
        self.circuit_source_dic={}#激励源
        self.circuit_load_dic={}#负载
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
        self.faceId=0 #全局参数，面端口为空不设置
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
        self.title="热-对流设置"
        self.lblTitle="对流系数"
class PF_Thermal_Radiation(PF_Thermal_Base):
    def __init__(self):
        super(PF_Thermal_Radiation,self).__init__()
        self.title="热-辐射"
        self.lblTitle="辐射率"