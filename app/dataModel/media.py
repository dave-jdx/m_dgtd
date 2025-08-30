class Media():
    dielectric="Dielectric"
    metal="Metal"
    dielectric_zh="介质材料"
    metal_zh="金属"
    sysOwner="system"
    # title_dielectric="Dielectric modelling"
    # title_metal="Metallic modelling"
    # columnsLibrary=["Type","Name","Owner"]
    # columnsDielectric=["Frequency\n",
    #                     "Permittivity\nreal",
    #                     "Imaginary\n",
    #                     "Permeability\nreal",
    #                     "Imaginary\n"]
    # columnsMetal=["Frequency","Conductivity"]
    columns=["类型","名称","所有者"]
    title="材料库"
    def __init__(self) -> None:
        self.name:str=""
        self.type:str=""# Dielectric,Metal
        self.owner:str=""# system,user
        self.id:str=""
        
        pass
class Dielectric(Media):
    columns=["频率\n",
                        "介电常数\n实部",
                        "虚部\n",
                        "磁导率\n实部",
                        "虚部\n"]
    title="介质材料"
    type="Dielectric"

    def __init__(self) -> None:
        self.name:str=""
        self.type:str=self.dielectric
        self.owner:str=self.sysOwner
        self.frequency:str=None
        self.permittivity_real:str=None
        self.permittivity_imag:str=None
        self.permeability_real:str=None
        self.permeability_imag:str=None
        pass
class Metal(Media):
    columns=["Frequency","电导率"]
    title="金属"
    type="Metal"
    def __init__(self) -> None:
        self.name:str=""
        self.type:str=self.metal
        self.owner:str=self.sysOwner
        self.frequency:float=None
        self.conductivity:str=None
        pass
class MediaItem:
    objIndex=256+1
    def __init__(self) -> None:
        self.media:Media=None
        self.freqList:list[Media]=[]
        pass
