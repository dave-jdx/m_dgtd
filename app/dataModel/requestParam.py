'''
求解设置
'''
class RequestParam:
    objIndex=256+1
    def __init__(self):
        self.reqTime=RequestParam_time()
        self.reqDomain=RequestParam_domain()
        self.reqTemperature=RequestParam_temperature()
        pass
#时间设置
class RequestParam_time:
    def __init__(self):
        self.timeStep:str="0" #时间步长
        self.timeStepNum:int=0 #时间步数
        self.timeStepFactor:float=0 #步长比例因子

        self.timeStep_heat:str="0" #热传导时间步长
        self.timeStepNum_heat:int=0 #热传导时间步数
        self.timeStepFactor_heat:float=0

#观察域设置
class RequestParam_domain:
    def __init__(self):
        self.domain1=(False,0)
        self.domain2=(False,0)
        pass
#温度设置
class RequestParam_temperature:
    def __init__(self):
        #初始温度
        self.temperatureStart=0
        #环境温度
        self.temperatureEnv=0
        pass
