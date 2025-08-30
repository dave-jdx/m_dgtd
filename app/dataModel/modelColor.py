class ModelColor:
    MODE_MODEL=0
    MODE_FACE_NORMAL=1
    def __init__(self):
        self.colorType:int=0 #0:正常颜色 1:法向颜色 2:材质颜色
        self.color_normal_outside=(78,156,0) #法线向外 绿色
        self.color_normal_inside=(194,65,22) #法线向内 暗红色
        self.color_model_background=(219,219,219) #背景色 灰色
        self.color_model_foreground=(26,51,77) #前景色 深蓝色
        