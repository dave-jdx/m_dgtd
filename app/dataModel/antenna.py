from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Edge,TopoDS_Shape,TopoDS_Builder, TopoDS_Compound
class Antenna():
    import_arrayExtension="TEXT Files(*.txt)"
    import_radioExtension="TEXT Files(*.txt)"
    mode_array=0
    mode_points=1
    def __init__(self,typeName="TX",name="TX-1") -> None:
        self.name=name
        self.typeName=typeName
        self.m_unit=1000#模型单位 mm UI显示均使用m
        self.antennaType=self.mode_array#0:阵列模式 1:定制阵元模式
        self.waveform:str="Sinusoid"  #波形
        self.power:str="1"#功率
        self.center:tuple=(0,0,0)#中心点坐标
        self.normal_dir:tuple=(0,0,1)#法向量
        self.offset_x:float=0#x轴偏移
        self.offset_y:float=0
        self.offset_z:float=0
        self.offset_rotate_z:float=0#绕z轴轴旋转
        
        self.rotate_x:float=0#方向图x轴旋转
        self.rotate_y:float=0
        self.rotate_z:float=0
        self.radio_scale:float=10#方向图缩放比例

        self.angel_xy:float=0#xy面夹角
        self.angel_xz:float=0#xz面夹角
        self.angel_yz:float=0#yz面夹角
        self.display_size:float=5#显示像素大小
        self.axis_length_array:float=0.8
        self.axis_length_antenna:float=0.8
        self.axis_thickness_antenna:float=1

        self.itemList_local=[]#局部坐标系坐标阵元列表 x y z 幅度系数 相位
        self.itemList_global:list[tuple(float,float,float,float,float)]=[]#全局坐标系坐标 阵元列表
        self.itemList_discrete=[]#离散阵元列表 全局坐标系

        
        self.arrayShape:TopoDS_Shape=None
        self.arrayShape_AIS=None

        self._face_id:int=-1
        

        self.nfr_data=(None,None,None,None,None)#nfr对象解析数据 pointList,min,max,thetaNum,phiNum

        self._actor_antenna=None #方向图ctor
        self._actor_bar=None #方向图颜色条
        self._actor_model=None#模型actor
        self._actor_array=None#阵列actor

        self.file_array:str=""#阵列文件完整路径含文件名
        self.file_array_model:str=""#阵列模型文件完整路径含文件名
        self.file_antenna:str=""#方向图文件完整路径含文件名

        self._show_array=True#显示阵列
        self._show_antenna=True#显示方向图
        self._show_axis_array=True#显示阵列坐标系
        self._show_axis_radio=True#显示方向图坐标系
        self.reverseN=False #反转N轴
        
        pass
    def dumpClear(self):
        '''
        保存对象数据时，清除不可序列化的对象
        '''
        self._actor_antenna=None
        self._actor_bar=None
        self._actor_model=None
        self._actor_array=None
        self.arrayShape=None
        self.arrayShape_AIS=None
