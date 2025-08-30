class Frequency():
    objIndex=256+1
    nodeName="求解设置"
    def __init__(self) -> None:
        self.start:str=""
        self.end:str=""
        self.increment:str=""
        self.reflection:str="1" #反射
        self.transmission:str="0" #透射
        self.diffraction:str="1" #绕射
        self.store_current:bool=True
        self.discreteList=[] #离散频率列表
        self.freqType=0 # 0:等间隔频率 1:离散频率