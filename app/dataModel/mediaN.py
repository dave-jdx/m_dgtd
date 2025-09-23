class MediaBase():
    isotropic="Isotropic" # 各向同性
    anisotropic="Anisotropic" # 各向异性
    dispersive="Dispersive" # 色散
  
    columns=[] #属性列表
    name:str=""
    def __init__(self) -> None:
        pass
class Isotropic(MediaBase):
    columns=["名称",
             "相对介电常数", 
             "相对磁导率",
             "电导率(S/m)",
             "热导率(W/m·K)",
             "密度(kg/m^3)",
             "比热容(J/kg·K)",
             "杨氏模量(Pa)",
             "泊松比",
             "热膨胀系数(1/K)",
            "电子寿命(s)",
            "空穴寿命(s)",
            "能隙(eV)",
            "电子亲和能(eV)",
            "价带有效态密度(cm^-3)",
            "导带有效态密度(cm^-3)",
            "电子迁移率(cm^2/V·s)",
            "空穴迁移率(cm^2/V·s)",
            
             "创建者"]
    title="各项同性"
    type="Isotropic"

    def __init__(self) -> None:
        self.name:str="" #材料名称
        self.type:str=self.isotropic
        self.owner:str="user"
        self.permittivity:str=None #相对介电常数
        self.permeability:str=None #相对磁导率
        self.eConductivity:str=None #电导率
        self.tConductivity:str=None #热导率
        self.density:str=None #密度
        self.specificHeat:str=None #比热容
        self.youngModulus:str=None #杨氏模量
        self.poissonRatio:str=None #泊松比
        self.thermalExpansion:str=None #热膨胀系数

        self.s_e_lifetime:str=None #电子寿命
        self.s_h_lifetime:str=None #空穴寿命
        self.s_bandgap:str=None #能隙
        self.s_e_affinity:str=None #电子亲和能
        self.s_e_v_band:str=None #价带有效态密度
        self.s_e_c_band:str=None #导带有效态密度
        self.s_e_mobility:str=None #电子迁移率
        self.s_h_mobility:str=None #空穴迁移率
        
        

        pass
class Anisotropic(MediaBase):
    columns=["名称",
             "类型", 
             "介电常数实部",
             "虚部",
             "磁导率实部",
             "虚部",
             "创建者"]
    title="各项异性"
    type="Anisotropic"
    def __init__(self) -> None:
        self.name:str=""
        self.type:str=self.anisotropic
        self.owner:str="user"
        self.permittivity_real:str=None #相对介电常数实部
        self.permeability_real:str=None #相对磁导率实部
        self.permeability_imag:str=None #相对磁导率虚部
        self.permittivity_imag:str=None #相对介电常数虚部
        pass
class DispersiveProp(MediaBase):
    columns=["频率（HZ) ",
             "ϵ' ",
             "ϵ''",
             "μ' ",
             "μ'' ",
             "σ " ,]
    title="色散详情"
    type="DispersiveProp"
    def __init__(self) -> None:
        self.name:str=""
        self.type:str=self.dispersive
        self.owner:str="user"
        self.frequency:str=None #频率
        self.permittivity_real:str=None #相对介电常数实部
        self.permeability_real:str=None #相对磁导率实部
        self.permeability_imag:str=None #相对磁导率虚部
        self.permittivity_imag:str=None #相对介电常数虚部
        self.eConductivity:str=None #电导率
class Dispersive(MediaBase):
    columns=["名称",
             "频点数"]
    title="色散"
    type="Dispersive"
    def __init__(self) -> None:
        self.name:str=""
        self.type:str=self.dispersive
        self.owner:str="user"
        self.itemList:list[DispersiveProp]=[]
        pass

