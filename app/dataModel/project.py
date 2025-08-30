from PyQt5.QtCore import QSettings, QStandardPaths
from typing import List,Set,Dict,Tuple
from path import Path
import os
from .model import Model
from .mesh import Mesh
from .ffr import FFR
from .nf import NF
from .pf import (PF,PF_EBase,PF_EM,PF_Circuit,PF_Thermal,PF_Struct,
                PF_Circuit_Source, PF_Struct_Force,
                PF_Thermal_Base,PF_Thermal_Dirichlet,PF_Thermal_Source,PF_Thermal_Convection,PF_Thermal_Radiation)

from .requestParam import(RequestParam,RequestParam_domain,RequestParam_temperature,RequestParam_time)
from .modelColor import ModelColor
class Project():
    userDataPath=QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)+"/FEM-GDTDX"
    defultFreqEnd=10e+9
    solverEncoding="gb2312"
    mpiInstallPath="C:\\Program Files\\MPICH2\\"
    mpiRegisterFile="bin\\wmpiregister.exe"
    mpiTestFile="bin\\wmpiexec.exe"
    licenseExtension="License Files(*.lic)"
    EXTENSIONS="FEM-GDTD Files(*.femx)"
    classTitle="Project"
    solverExe="FASTEM_701.exe"
    solverPath=os.getcwd()+"/"+"Core/FEM-GDTD"


    
    def __init__(self) -> None:
        self.fpath:str=self.userDataPath+"/temp"
        self.defaultPath:str=self.userDataPath+"/temp"
        self.name:str="FEM-GDTD-1"
       

        self.currentModel:Model=None
        self.currentMesh:Mesh=None
        self.modelColor:ModelColor=None
        self.pf:PF=None
        self.requestParam:RequestParam=RequestParam()
        self.nfList:List[Tuple[str,NF]]=[]
        self.ffrList:List[Tuple[str,FFR]]=[]

    
        self.modeList:List[Tuple[str,Model]]=[]
        
        self.mediaList=[]
        self.media_used={}
        self.mpiNum=2

        self.exeName=""
        self.pfName=""#选中的物理场

        pass
    def getSolverPath(self):
        return self.fpath+"/{0}.results/FEM-DGTD".format(self.name)
    def getModelPath(self):
        return self.getSolverPath()+"/input"
    def getMediaPath(self):
        return self.getSolverPath()+"/input"

    def getCurrentsFileName(self,txIndex:int):
        '''获取电流文件名
        '''
        fname=self.getSolverPath()+"/output/res_Current_{}.txt".format(txIndex)
        return fname

    def getModelTempPath(self):
        return self.defaultPath+"/.data/model"
    def getMeshTempPath(self):
        return self.userDataPath+"/temp"
    def getLogRateFileName(self):
        return self.getSBRPath()+"/output/process_rate and error.txt"
    def getLogProcessFileName(self):
        return self.fpath+"/output/process_log.txt"
    def getLogResultFileName(self):
        return self.fpath+"/output/result_log.txt"
    def getOutputPath(self):
        return self.getSolverPath()+"/output"
  