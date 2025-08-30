class render_base():
    def __init__(self):
        self.actorMap=None#存储云图actor
        self.actorPoints=None #存储点云actor
        self.actorArray_TX=None
        self.actorArray_RX=None
        self.actorModel=None
        self.actorBar=None
        self.show_surface=True #显示表面云图
        self.show_points=False #显示点云
        self.opacity=1 #透明度 0-1 完全透明-完全不透明
        self.minV=0
        self.maxV=0
        self.min_now=0
        self.max_now=0
        self.scalarType=0 #0 自动填充 1手动输入
        self.numberOfColors=256 #颜色阶数

class render_currents(render_base):
    def __init__(self):
        super().__init__()
class render_nf_E(render_base):
    def __init__(self):
        super().__init__()
class render_nf_H(render_base):
    def __init__(self):
        super().__init__()
class render_emi(render_base):
    def __init__(self):
        super().__init__()
class PostRender():
    def __init__(self):
        self.currents=render_currents()
        self.nf_E=render_nf_E()
        self.nf_H=render_nf_H()
        self.emi=render_emi()
        self.render_now:render_base=None
        pass 
    def setRenderCurrents(self):
        self.render_now=self.currents
        pass
    def setRenderNF_E(self):
        self.render_now=self.nf_E
        pass
    def setRenderNF_H(self):
        self.render_now=self.nf_H
        pass
    def setRenderEmi(self):
        self.render_now=self.emi
        pass
