from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Edge,TopoDS_Shape,TopoDS_Builder, TopoDS_Compound
class Model():
    objIndex=256+1
    nodeName="模型"
    exportExtension="STP files(*.stp);;STEP files(*.step);;IGS files(*.igs);;IGES files(*.iges);;STL files(*.stl)"
    exchangeExtension="STP files(*.stp);;STEP files(*.step);;IGS files(*.igs);;IGES files(*.iges);;OBJ files(*.obj);;STL files(*.stl)"
    extPostExtension="STL files(*.stl);;STP files(*.stp);;STEP files(*.step);;IGS files(*.igs);;IGES files(*.iges)"
    backgroudColor=(219,219,219)
    modelColor=(26,51,77)
    def __init__(self) -> None:
        self.name:str=""
        self.title:str=""
        self.fileNameNoPath:str=""
        self.fileName:str=""#原始文件完整路径含文件名
        self.geoFile:str=""#STL文件完整路径含文件名
        self.shape:TopoDS_Shape=None #模型的compundshape
        self.shapeList=[]#当前模型的所有shape
        self.aisShapeList=[] #当前模型显示的aisshape
        self.ais_shape_faceNormal=None #法线模式aisshape
        self.faceNum:int=None #面的数量，用于枚举面
        self.face_selected={}#选中面 key:faceId value:True/False
        self.medium:int=-1#模型整体的介质
        self.mediumFaces:dict[int,tuple]={}#面材质设置,key=faceId 从1开始 value=(mediumBase,mediumCoat,thicknessValue)
        self.pml=(0.1,0.1,True,False,0.1,False)#PML设置 距离 宽度 是否显示,创建
        
        self.exf=(0.05,True,False,0.1,False) #外推面设置 距离 是否显示,是否创建

        self.pml_param=(0.1,0,0,0,0,0,0)#pml参数输出 厚度，xmax,ymax,zmax,xmin,ymin,zmin
        self.freq=("1e9",False) #频率设置 频率 是否自动根据频率计算波长-涉及pml设置和外推面设置
        
        self.shapeList_pml=[]#PML的shape
        self.shapeIdList_pml=[]
        self.aisShapeList_pml=[]
        self.shapeList_exf=[]#外推面的shape 0:内部 1:外部
        self.shapeIdList_exf=[]
        self.aisShapeList_exf=[]
        self.opacity=0
        self.opacityMap=0
    def dumpClear(self):
        # self.shapeList.clear()
        self.aisShapeList.clear()
        self.ais_shape_faceNormal=None
        self.aisShapeList_pml.clear()
        self.aisShapeList_exf.clear()
