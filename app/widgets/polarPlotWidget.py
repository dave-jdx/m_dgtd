import sys
import numpy as np
from PyQt5 import QtWidgets
import matplotlib
# 使用与Qt兼容的后端（若使用 PyQt5，请确保配置的是Qt5Agg后端）
matplotlib.use('Qt5Agg') 

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PolarPlotWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        # 创建Figure对象和轴（极坐标）
        self.figure = Figure(figsize=(5,5), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        
        
        
        

        # 创建布局并将canvas嵌入
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    def render(self,data1,title,xIndex):
        # 示例数据 (theta[deg], gain[dB])
        self.figure.clear()
        # 在figure中创建极坐标图
        self.ax = self.figure.add_subplot(111, polar=True)
        # data1 = [
        #     (0,   12),
        #     (15,  11),
        #     (30,  10),
        #     (45,  9),
        #     (60,  12),
        #     (75,  13),
        #     (90,  6),
        #     (105, 10),
        #     (120, 9),
        #     (135, 11),
        #     (150, 12),
        #     (165, 6),
        #     (180, 9)
        # ]
        filtered_data = [d for d in data1 if d[0] == 0]

        # 从筛选后数据中，只取出索引0与索引2位置的数据形成新的列表
        # 即 (theta, gain) 而不包括phi
        data1 = [(d[1], d[2]) for d in filtered_data]

                
        # 解析数据
        theta_deg_1 = [d[0] for d in data1]
        gain_db_1 = [d[1] for d in data1]
        theta_rad_1 = np.radians(theta_deg_1)


        # 在极坐标中绘制曲线
        self.ax.plot(theta_rad_1, gain_db_1, color='r', linewidth=2, label='phi=0')

        # 设置极坐标参考方向与刻度
        self.ax.set_theta_zero_location('N')  
        self.ax.set_theta_direction(-1)
        self.ax.set_thetagrids(range(0, 360, 30))

        max_gain = max(gain_db_1)
        min_gain= min(gain_db_1)
        r_ticks = np.linspace(min_gain, max_gain+5, 5)
        self.ax.set_rgrids(r_ticks, angle=0)
        self.ax.set_rlabel_position(0)

        self.ax.grid(True, linestyle='--', color='gray', alpha=0.7)
        self.ax.set_title(title, va='bottom')
        # self.ax.legend(loc='lower right')
        self.ax.legend(
            loc='center left',      # 图例将以其左边缘为基准进行定位
            bbox_to_anchor=(1.05, 0.5) # 将图例锚点设置在坐标系的 (x=1.05, y=0.5) 处
        )


        # 刷新画布
        self.figure.tight_layout()
        self.canvas.draw()
    def render_multi(self,pointList,title,xIndex,lineName):
        '''
        pointList: 分组后的数据，根据自变量值分组[theta,[(phi1,v1),(phi2,v2)] ]
        '''
        self.figure.clear()
        # 在figure中创建极坐标图

        self.ax = self.figure.add_subplot(111, polar=True)
        for points in pointList:
            theta=points[0]
            data=points[1]
            # 解析数据
            theta_deg_1 = [d[0] for d in data]
            gain_db_1 = [d[1] for d in data]
            theta_rad_1 = np.radians(theta_deg_1)
            # 在极坐标中绘制曲线
            lines=self.ax.plot(theta_rad_1, gain_db_1, linewidth=2, label=f'{lineName}')
            #显示线条颜色
            line=lines[0]
            print("line-color",line.get_color())

        # filtered_data = [d for d in data1 if d[0] == 0]
        # # 从筛选后数据中，只取出索引0与索引2位置的数据形成新的列表
        # # 即 (theta, gain) 而不包括phi
        # data1 = [(d[1], d[2]) for d in filtered_data]
                
        # # 解析数据
        # theta_deg_1 = [d[0] for d in data1]
        # gain_db_1 = [d[1] for d in data1]
        # theta_rad_1 = np.radians(theta_deg_1)


        # # 在极坐标中绘制曲线,这里只绘制了一个曲线
        # # 需要支持多个曲线
        # self.ax.plot(theta_rad_1, gain_db_1, color='r', linewidth=2, label='Phi=0')

        # 设置极坐标参考方向与刻度
        self.ax.set_theta_zero_location('N')  
        self.ax.set_theta_direction(-1)
        self.ax.set_thetagrids(range(0, 360, 30))
        self.ax.legend(loc='upper right')

        max_gain = max(gain_db_1)
        min_gain= min(gain_db_1)
        r_ticks = np.linspace(min_gain, max_gain+5, 5)
        self.ax.set_rgrids(r_ticks, angle=0)
        self.ax.set_rlabel_position(0)
        self.ax.grid(True, linestyle='--', color='gray', alpha=0.7)
        self.ax.set_title(title, va='bottom')
        # self.ax.legend(loc='lower right')
        # self.ax.legend(
        #     loc='center left',      # 图例将以其左边缘为基准进行定位
        #     bbox_to_anchor=(1.05, 0.5) # 将图例锚点设置在坐标系的 (x=1.05, y=0.5) 处
        # )

        # 刷新画布
        self.figure.tight_layout()
        self.canvas.draw()
    def clear(self):
        """
        Clears the plot
        """
        self.figure.clear()
        self.canvas.draw()
    

