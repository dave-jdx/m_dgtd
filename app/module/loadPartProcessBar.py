#coding=utf-8
from PyQt5.QtWidgets import QApplication, QProgressBar, QLabel
import time,os,math
from . import exchangeData


class PartLoadProgressBar(QProgressBar):
    def __init__(self,parent=None):
        super(PartLoadProgressBar, self).__init__()
        self.progressBar = QProgressBar(parent)
        self.label = QLabel()
        self.label.setText("正在生成      ")
        self.statusBar=parent.statusBar
        self.statusBar().addPermanentWidget(self.label)  # 嵌入进度条
        self.statusBar().addPermanentWidget(self.progressBar)#嵌入进度条
        # 设置进度条的范围，参数1为最小值，参数2为最大值（可以调得更大，比如1000
        self.progressBar.setRange(0, 100)
        self.value=0
        self.total=None
        # 设置进度条的初始值
        self.Hide()
    def Load_part_progressBar(self,shape=None):#
        self.value += 1
        value=int(self.value/shape*100)
        self.progressBar.setValue(value)
        #print(value)
        if value==100:
            self.Value_clear()
    def Load_part_progressBar_auto(self,now_percent=50):#
        self.value += 1
        value=now_percent+(self.value/self.total*100)*(1-now_percent/100)
        if self.value==self.total:
            self.progressBar.setValue(100)
            self.label.setText("数据加载完成")
            time.sleep(0.5)
            self.Value_clear()
            self.Hide()
        else:
            self.progressBar.setValue(value)


    def Read_part_progressBar(self,file=None):#
        test_filepath="./resource/Test_Model/Test_Model.stp"
        test_start_time=time.time()
        shapes_labels_colors = exchangeData.read_step_file_with_names_colors(test_filepath,self)
        test_end_time=time.time()
        file_size=os.lstat(test_filepath).st_size/1024#单位KB
        read_speed=file_size/(test_end_time-test_start_time)#单位KB/S
        print("文件大小",file_size,"读取时间",(test_end_time-test_start_time),"读取速度",read_speed)
        #计算加载时间
        file_size=os.lstat(file).st_size/1024#单位KB
        read_time=math.ceil(file_size/read_speed)
        print(666,read_time)
        sleep_time=0
        self.Show()
        while True:
            time.sleep(0.5)
            sleep_time+=0.5
            if sleep_time>read_time:
                self.Hide()
                break
            else:
                value = int(sleep_time / read_time * 100)
                print(value)
                self.progressBar.setValue(value)


    def Down_load_part_progressBar(self,file_size,now_file_size):
        value = int(float(now_file_size) / float(file_size)*100)
        self.progressBar.setValue(value)
    def Value_clear(self):
        self.value=0
    def Show(self):
        self.progressBar.show()
        self.label.show()
        #self.statusBar().addPermanentWidget(self.progressBar)
    def Hide(self):
        #self.statusBar().removeWidget(self.progressBar)
        self.progressBar.hide()
        self.label.hide()
    def Refresh_gui(self):
        while True:
            QApplication.processEvents()