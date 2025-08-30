class data_base():
    def __init__(self):
        self.dataResults = {}#存储全部数据 key为阵元编号，value为各个频点的数组
        self.points_now=[] #当前正在显示的数据
        self.headers_now=[]
class data_currents(data_base):
    def __init__(self):
        super().__init__()
class data_nf_E(data_base):
    def __init__(self):
        super().__init__()
class data_nf_H(data_base):
    def __init__(self):
        super().__init__()
class data_emi(data_base):
    def __init__(self):
        super().__init__()
class PostData():
    def __init__(self):
        self.currents=data_currents()
        self.nf_E=data_nf_E()
        self.nf_H=data_nf_H()
        self.emi=data_emi()
        self.data_now:data_base=None
        pass 
    def setDataCurrents(self):
        self.data_now=self.currents
        pass
    def setDataNF_E(self):
        self.data_now=self.nf_E
        pass
    def setDataNF_H(self):
        self.data_now=self.nf_H
        pass
    def setDataEmi(self):
        self.data_now=self.emi
        pass
    def clear(self):
        self.currents.dataResults.clear()
        self.nf_E.dataResults.clear()
        self.nf_H.dataResults.clear()
        self.emi.dataResults.clear()
        pass
    