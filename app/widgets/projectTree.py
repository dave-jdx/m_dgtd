import sys,os,signal,subprocess,pickle,threading,time,copy,math,json,pathlib
import asyncio
import traceback
from typing import List,Set,Dict,Tuple
from datetime import datetime
from ..utils import  get_open_filename
from path import Path

from OCC.Display.OCCViewer import Viewer3d
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAction, QMenu, QWidget, QAbstractItemView,QHeaderView,QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal,QSize,QTimer,QThread
from PyQt5 import QtWidgets
from PyQt5 import QtCore
#导入qpoint
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QMovie, QPixmap

from pyqtgraph.parametertree import Parameter, ParameterTree
from OCC.Core.Geom import Geom_Axis2Placement, Geom_Plane
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from ..mixins import ComponentMixin
from ..utils import splitter, layout
from OCC.Core.Quantity import *
from OCC.Core.Select3D import *
from OCC.Core.TopoDS import TopoDS_Edge,TopoDS_Shape,TopoDS_Face

from .console import ConsoleWidget

from .frmCreateMesh import frmCreateMesh
from .frmFrequency import frmFrequency
from .frmFrequency2 import frmFrequency2
from .frmPower import frmPower
from .frmVoltageSource import frmVoltageSource
from .frmLoad import frmLoad
from .frmRequstNFR import frmRequestNFR
from .frmRequstFFR import frmRequestFFR
from .frmRequstNF import frmRequestNF
from .frmArrangement import frmArrange
from .frmAntennaSet import frmAntennaSet
from .frmMediaLibrary import frmMediaLibrary
from .frmMediaLibraryN import frmMediaLibraryN
from .frmModelMedia import frmModelMedia
from .frmMediaModify import frmMediaModify
from .frmAntennaPoints import frmAntennaPoints
from .frmArrangement2 import frmArrange2
from .frmTX import frmTX
from .frmMPI import frmMPI
from .frmScalar import frmScalar
from .frmModelColor import frmModelColor
from .frmMediaCoat import frmMediaCoat

from .frmFilter import frmFilter
from .customDialog import customDialog

from .frmEM import frmEM
from .frmEMPEC import frmEMPEC
from .frmEMPML import frmEMPML
from .frmCircuit import frmCircuit
from .frmCircuitSource import frmCircuitSource
from .frmCircuitLoad import frmCircuitLoad
from .frmThermalBase import frmThermalBase
from .frmThermalDirichlet import frmThermalDirichlet
from .frmThermalConvection import frmThermalConvection
from .frmThermalRadiation import frmThermalRadiation
from .frmThermalSource import frmThermalSource
from .frmStructDirichlet import frmStructDirichlet
from .frmStructForce import frmStructSource
from .frmTime import frmTime
from .frmTemperature import frmTemperature
from .frmDomain import frmDomain
from .frmDomainPF import frmDomainPF
from .frmDomainPML import frmDomainPML
from ..module.loadPartProcessBar import PartLoadProgressBar
from .frmOpacity import frmOpacity
from .frmPostParam import frmPostParam
from .frmMeshSize import frmMeshSize
from .frmSimSelect import frmSimSelect
from .polarPlotWidget import PolarPlotWidget
from .frmFilter2dPolar import frmFilter2dPolar

from ..api import api_model
from ..api import api_gmsh

# from ..api import api_mesh

from ..api import api_project

from ..api import api_vtk

from ..api import api_reader

from..api import api_config

from ..api import api_writer

from ..dataModel import tree

from ..dataModel.project import Project
from ..dataModel.model import Model
from ..dataModel.mesh import Mesh,MeshFormat
from ..dataModel.port import Port

from ..dataModel.frequency import Frequency
# from ..dataModel.power import Power
# from ..dataModel.source import Source
# from ..dataModel.load import Load
from ..dataModel.ffr import FFR
# from ..dataModel.nfr import NFR
from ..dataModel.nf import NF
from ..dataModel.antenna import Antenna
from ..dataModel.media import Media,Dielectric,Metal,MediaItem
from ..dataModel.mediaN import MediaBase,Isotropic,Anisotropic,DispersiveProp,Dispersive

from ..dataModel.postFilter import PostFilter,filter_currents,filter_nf_E,filter_emi,filter_nf_H,filter_xyz
from ..dataModel.postData import PostData,data_base,data_nf_E,data_nf_H,data_emi,data_currents
from ..dataModel.postRender import PostRender,render_base,render_currents,render_nf_E,render_nf_H,render_emi
from ..dataModel.modelColor import ModelColor
from ..dataModel.pf import (PF,PF_EBase, PF_EM,PF_Circuit,PF_Thermal,PF_Struct,PF_Struct_Force,PF_Circuit_Source,
                            PF_Thermal_Dirichlet,PF_Thermal_Source,PF_Thermal_Convection,PF_Thermal_Radiation)
from ..dataModel.requestParam import RequestParam,RequestParam_time,RequestParam_domain,RequestParam_temperature

from ..stream_reader import NonBlockingStreamReader as NBSR


# from ..module.loadPartProcessBar import PartLoadProgressBar
from ..module.interactiveContext import InteractiveContext

from .vtk_viewer_3d import vtkViewer3d
from .vtk_viewer_2d import vtkViewer2d
from  ..icons import icon,treeIcons

CONSOLE_WINDOW=True #是否显示控制台窗口


class ProjectTree(QWidget, ComponentMixin):

    name = 'Project'
    _stash = []

    preferences = Parameter.create(name='Preferences', children=[
        {'name': 'Preserve properties on reload', 'type': 'bool', 'value': False},
        {'name': 'Clear all before each run', 'type': 'bool', 'value': True},
        {'name': 'STL precision', 'type': 'float', 'value': .1}])

    sigActivateTab=pyqtSignal(int)
    sigActivateToolbar=pyqtSignal(int) #切换到指定的工具栏 -查看结果时使用
    # sigCreateProject= pyqtSignal(str, str)
    
    sigPickEdge=pyqtSignal()
    sigPickFace=pyqtSignal()
    sigRemoveSelectedEdge=pyqtSignal(int)
    sigClearInterContext=pyqtSignal()

    sigFreq=pyqtSignal(list) #获取当前频率列表，并传递给主窗口，当做筛选项
    sigTx=pyqtSignal(list) #获取当前发射天线列表，并传递给主窗口，当做筛选项
    sigTxEnable=pyqtSignal(bool) #是否启用阵元的切换，当导入外部数据时禁用
    sigChooseList=pyqtSignal(list,dict,bool)#vTyleList,[物理量字典，包含是否选中],是否单选
    sigVTypeList=pyqtSignal(list) #当前图形类型列表，并传递给主窗口，当做筛选项
    sigValueButtons=pyqtSignal(dict,bool,dict) #当前物理量的按钮状态，true单选 false多选
    sigValueButton_convert_disabled=pyqtSignal(bool) #当前物理量的转换单位按钮
    sigValueButton_convert_checked=pyqtSignal(bool)#db值按钮是否选中，在切换图形类型时需要保持原状态
    
    # sigChooseAxis=pyqtSignal(list) #当选中chart时，可以选择曲线图的横轴显示X/Y/Z
    
    sigChooseSurface=pyqtSignal(list,bool) #(面列表，是否显示横轴，面初始索引）横轴与面选择直接相关联
    sigPosition=pyqtSignal(list)
    sigPFName=pyqtSignal(str) #物理场名称,初始化加载工程时使用

  
   
    def __init__(self, parent=None,
                modelViewer:Viewer3d=None,
                meshViewer:vtkViewer3d=None,
                console:ConsoleWidget=None,
                qSize:QSize=QSize(300,600),
                vtkViewer3d:vtkViewer3d=None,
                vtkViewer2d:vtkViewer2d=None,
                selectContext=None,
                tableViewer:QtWidgets.QTableWidget=None,
                polarViewer:PolarPlotWidget=None):
        super(ProjectTree, self).__init__(parent)
        self.parent = parent
        self._dir=os.path.dirname(os.path.abspath(sys.executable))
        self._is_saved=False
        self._show_axis_global=False #只显示一次即可
        self._pLogger=api_project.getLogger("project")
        self._font=self.font()
        self._font.setPixelSize(16)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self.setFont(self._font)
        # self.setFont(self._font)
        # print("project tree font",self._font.family())

        self.isLoading=False
        self.defaultSize:QSize=qSize

        self.modelViewer=modelViewer
        self._meshViewer=meshViewer #用来显示天线方向图

        self._vtkViewer3d=vtkViewer3d
        self._vtkViewer2d=vtkViewer2d
        self._tableViewer=tableViewer
        self._selectContext:InteractiveContext=selectContext
        self.console=console

        self._2dPolarViewer:PolarPlotWidget=polarViewer
        

        self.tree = QTreeWidget(self, selectionMode=QAbstractItemView.ExtendedSelection)
        # self.tree.setFont(self._font)
        self._context_menu = QMenu(self)
        self._context_menu.setFont(self._font)

        # self.circles_display = {}
        self.properties_editor = ParameterTree(self)
    
        self.actionIndex=Qt.UserRole+9

        # self.currentShapeList:list[TopoDS_Shape]=None #当前正在显示的模型shape
        # self.aisShapes:list=None

        self._mediaList:list[Isotropic]=[] #材料库中的材料
        self._media_used:dict[int,Isotropic]={} #当前已经使用的材料

        self._pf=PF()


        self._frm_model_media:frmModelMedia=None

        self.currentModel:Model=None
        self._modelColor=ModelColor()

        self.currentMesh:Mesh=Mesh()
        # self.currentMeshSizeDic={}#单独设置的尺寸dic(faceId,size)
        # self.currentMeshActor=None

        self.currentProject:Project=None
        self.currentProcess:subprocess.Popen=None
        self._meshProcess:subprocess.Popen=None

        self._postFilter=PostFilter()
        self._postData=PostData()
        self._postRender=PostRender()
        self._ais_shape_nfDic={}

        self._postFilter_extend=PostFilter() #查看外部数据时的后处理对象
        self._postData_extend=PostData()
        self._postRender_extend=PostRender()
        self._stl_actor=None
        self._displace_actor=None

        self._is_extend=False #是否正在查看外部数据

        self._cLogger=api_project.getLogger(name="emx",fpath=os.getcwd()+"/Log") #记录日志
        self._solidSelected_currentId=-1
        self._forms=[]#存储已打开的窗体，在打开新的窗体时，关闭所有已打开的窗体
        self._actors_current=[]#当前显示的actor集合，设置透明度需要



   

      
        # self.dataResults={
        #     "currents":{}, #key:发射阵元 value 多个频点的数据，每个元素为一个频点的数组
        #     "nf_E":{},
        #     "nf_H":{},
        #     "emi":{}
        # }

       

        self.tree.itemDoubleClicked.connect(self.nodeAction_doublClick)
        self.tree.itemClicked.connect(self.nodeAction_itemClick)
        self._selectContext.sigFaceChoosed.connect(self.sig_chooseFace)

        self.tree.customContextMenuRequested.connect(self.showMenu)
        # self.sigCreateProject.connect(self.sig_createProject)

        self.prepareLayout()
        self.onLoad()
  
    def sizeHint(self):
        return self.defaultSize
    
    
    
    def initMPI(self):
        '''初始化mpi，mpi未得到初始化时，需要弹出输入用户名密码窗口
        '''
        isInstalled=api_config.getMpiInstalled()
        try:
            if(isInstalled is None or int(isInstalled)!=1):
                #尚未初始化过mpi，首次使用需要使用命令行去弹出
                installPath="C:\\Program Files\\MPICH2\\"
                mpiexec = installPath+"bin\\wmpiexec.exe"  # 替换为mpiexec.exe的实际路径
                register=installPath+"bin\\wmpiregister.exe"
                cpi = installPath+"examples\cpi.exe"  # 替换为cpi.exe的实际路径
                num_procs = 4  # 设置使用的进程数
                command = [mpiexec,cpi]
                command_register=[register]
                subprocess.Popen(command_register)
                pass
            api_config.setMpiInstalled()
        except Exception as e:
            self._pLogger.error(e)
            pass
    pass

    def initialModelViewer(self):
        if(self.modelViewer!=None):
            self.modelViewer.EraseAll()
            self.modelViewer.hide_triedron()
            # self.modelViewer.display_triedron()
            self.modelViewer.display_graduated_trihedron()
        pass
    def initialVtkViewer(self):
        if(self._meshViewer!=None):
            self._meshViewer.clear()
        if(self._vtkViewer3d!=None):
            self._vtkViewer3d.clear()
        if(self._vtkViewer2d!=None):
            self._vtkViewer2d.clear()
        pass
    def initialNodeField(self):
        '''
        初始化工程树必需的根节点
        '''
        self.root:QTreeWidgetItem=None
        self.materialRoot:QTreeWidgetItem=None
        self.modelRoot:QTreeWidgetItem=None
        self.meshRoot:QTreeWidgetItem=None
        self.portRoot:QTreeWidgetItem=None

        self.pfRoot:QTreeWidgetItem=None
        self.pfBoundRoot:QTreeWidgetItem=None

        self.powerRoot:QTreeWidgetItem=None
        self.frequencyRoot:QTreeWidgetItem=None
        self.sourceRoot:QTreeWidgetItem=None
        self.loadRoot:QTreeWidgetItem=None

        self.requestRoot:QTreeWidgetItem=None
        # self.ffrRoot:QTreeWidgetItem=None
        # self.nfrRoot:QTreeWidgetItem=None
        # self.nfRoot:QTreeWidgetItem=None
        self.emiRoot:QTreeWidgetItem=None

        self.ffrRoot_result:QTreeWidgetItem=None
        self.nfrRoot_result:QTreeWidgetItem=None
        self.nfRoot_result:QTreeWidgetItem=None

        self.resultRoot:QTreeWidgetItem=None
        self.currentsRoot:QTreeWidgetItem=None
        self.resultExtendRoot:QTreeWidgetItem=None #可视化扩展节点

        self.t_arrangeRoot:QTreeWidgetItem=None #发射天线布局操作节点
        self.t_radioRoot:QTreeWidgetItem=None #发射天线方向图操作节点
        self.r_arrangeRoot:QTreeWidgetItem=None #接收天线布局操作节点
        self.r_radioRoot:QTreeWidgetItem=None #接收天线方向图操作节点

        self.emiRoot_result:QTreeWidgetItem=None #管理EMI的计算结果
        # self.emRoot:QTreeWidgetItem=None #物理场-电磁节点
        # self.em_PECRoot:QTreeWidgetItem=None #电磁-PEC节点
        # self.em_PMLRoot:QTreeWidgetItem=None ##电磁-完美匹配层节点
        # self.circuitRoot:QTreeWidgetItem=None #物理场-电路节点
        # self.circuit_sourceRoot:QTreeWidgetItem=None #电路-源节点
        # self.circuit_loadRoot:QTreeWidgetItem=None #电路-负载节点
        # self.thermalRoot:QTreeWidgetItem=None #物理场-热传递节点
        # self.thermal_dirichletRoot:QTreeWidgetItem=None #热传递-固定温度节点
        # self.thermal_convectionRoot:QTreeWidgetItem=None #热传递-热对流节点
        # self.thermal_radiationRoot:QTreeWidgetItem=None #热传递-热辐射节点
        # self.thermal_sourceRoot:QTreeWidgetItem=None #热传递-热源节点
        # self.structRoot:QTreeWidgetItem=None #物理场-结构节点
        # self.struct_dirichletRoot:QTreeWidgetItem=None #结构-固定位移节点
        # self.struct_forceRoot:QTreeWidgetItem=None #结构-外力节点
    def initialNodeActions(self):
        self.actionsRoot=[
            QAction(tree.nodeActions.rename, self, enabled=True,
                        triggered=self.nodeAction_RenameProject),
            QAction(tree.nodeActions.run, self, enabled=True,
                        triggered=lambda:self.nodeAction_RunSimulation(True)),
            QAction(tree.nodeActions.stop, self, enabled=True,
                        triggered=self.nodeAction_StopSimulation),
            QAction(tree.nodeActions.save, self, enabled=True,
                        triggered=lambda: self.nodeAction_SaveProject(True)),
            QAction(tree.nodeActions.saveAs, self, enabled=True,
                        triggered=self.nodeAction_SaveProjectAs),
            # QAction(tree.nodeActions.properties, self, enabled=True,
            #             triggered=self.nodeAction_SaveProject)
        ]
        self.actionsFaceItem=[
            # QAction(tree.nodeActions.mediumBase,self,enabled=True,
            #         triggered=self.setFaceMediumBase),

            # QAction(tree.nodeActions.mediumCoat,self,enabled=True,
            # triggered=self.setFaceMediumCoat),

            # QAction(tree.nodeActions.reverseNormal,self,enabled=True,
            #         triggered=self.reverseNormal)
        ]
        self.actionsSolidItem=[
            QAction(tree.nodeActions.mesh_size,self,enabled=True,
                    triggered=self.set_solid_mesh_size),
        ]
        self.actionsMaterialRoot=[
            QAction(tree.nodeActions.media_library, self, enabled=True,
                        triggered=self.nodeAction_MediaLibrary),
            QAction(tree.nodeActions.medial_setting, self, enabled=True,
                    triggered=self.nodeAction_ModelMediaSetting),

        ]
        self.actionsMaterial=[
            # QAction(tree.nodeActions.properties,self,enabled=True,
            #         triggered=self.nodeAction_MediaProperties)
        ]
        self.actionsModelRoot=[
            QAction(tree.nodeActions.importS, self, enabled=True,
                        triggered=self.nodeAction_ImportModel),
            QAction(tree.nodeActions.export, self, enabled=True,
                        triggered=self.nodeAction_ExportModel),
            
            ]
        self.actionsModelItem=[
            QAction(tree.nodeActions.pml_exf, self, enabled=True,
                        triggered=self.nodeAction_PML_EXFSetting),
            QAction(tree.nodeActions.rename, self, enabled=True,
                        triggered=self.nodeAction_RenameModel),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteModel),
        ]
        self.actionsMeshRoot=[
            QAction(tree.nodeActions.createMesh, self, enabled=True,
                        triggered=self.nodeAction_CreateMesh),
            QAction(tree.nodeActions.importS, self, enabled=True,
                        triggered=self.nodeAction_ImportMesh),
            QAction(tree.nodeActions.export, self, enabled=True,
                        triggered=self.nodeAction_ExportMesh)
        ]
        # self.actionsMeshItem=[
        #     QAction(tree.nodeActions.delete, self, enabled=True,
        #                 triggered=self.nodeAction_DeleteMesh),

        # ]
        # self.actionsPortRoot=[
        #     QAction(tree.nodeActions.addPort, self, enabled=True,
        #                 triggered=self.nodeAction_AddPort),
        # ]
        # self.actionsPortItem=[
        #     QAction(tree.nodeActions.rename, self, enabled=True,
        #                 triggered=self.nodeAction_RenamePort),
        #     QAction(tree.nodeActions.delete, self, enabled=True,
        #                 triggered=self.nodeAction_DeletePort),
        #     QAction(tree.nodeActions.showHide, self, enabled=True,
        #                 triggered=self.nodeAction_ShowHidePort),
        # ]
        self.actionsPFRoot=[
            QAction(tree.nodeActions.pf_em, self, enabled=True,
                        triggered=self.nodeAction_AddEM),
            QAction(tree.nodeActions.pf_circuit, self, enabled=True,
                        triggered=self.nodeAction_AddCircuit),
            QAction(tree.nodeActions.pf_thermal, self, enabled=True,
                        triggered=self.nodeAction_AddThermal),
            QAction(tree.nodeActions.pf_structure, self, enabled=True,
                        triggered=self.nodeAction_AddStruct),
        ]
        # self.actionsExcitationRoot=[
        #     QAction(tree.nodeActions.pf_em, self, enabled=True,
        #                 triggered=self.nodeAction_AddEM),
        #     QAction(tree.nodeActions.pf_circuit, self, enabled=True,
        #                 triggered=self.nodeAction_AddCircuit),
        #     QAction(tree.nodeActions.pf_thermal, self, enabled=True,
        #                 triggered=self.nodeAction_AddThermal),
        #     QAction(tree.nodeActions.pf_structure, self, enabled=True,
        #                 triggered=self.nodeAction_AddStruct),
            
        # ]
        # self.actionsSourceRoot=[
        #     QAction(tree.nodeActions.addSource, self, enabled=True,
        #                 triggered=self.nodeAction_AddSource),

        # ]
        # self.actionsSourceItem=[
        #     QAction(tree.nodeActions.rename, self, enabled=True,
        #                 triggered=self.nodeAction_RenameVSource),
        #     QAction(tree.nodeActions.delete, self, enabled=True,
        #                 triggered=self.nodeAction_DeleteVSource),
        #     QAction(tree.nodeActions.properties, self, enabled=True,
        #                 triggered=self.nodeAction_SourceProperties),

        # ]
        # self.actionsLoadRoot=[
        #     QAction(tree.nodeActions.addLoad, self, enabled=True,
        #                 triggered=self.nodeAction_AddLoad),
        # ]
        # self.actinosLoadItem=[
        #     QAction(tree.nodeActions.rename, self, enabled=True,
        #                 triggered=self.nodeAction_RenameLoad),
        #     QAction(tree.nodeActions.delete, self, enabled=True,
        #                 triggered=self.nodeAction_DeleteLoad),
        #     QAction(tree.nodeActions.properties, self, enabled=True,
        #                 triggered=self.nodeAction_LoadProperties),
        # ]
        self.actionsFrequencyRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_FrequencyProperties)

        ]
        self.actionsReqTimeRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TimeProperties)
        ]
        self.actionsReqThermalRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TemperatureProperties)
        ]
        self.actionsReqDomainRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_DomainProperties)
        ]
        self.actionsReqFFRRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_FFRProperties)
        ]
        self.actionsReqNFRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_NFProperties)
        ]
        # self.actionsPowerRoot=[
        #     QAction(tree.nodeActions.properties, self, enabled=True,
        #                 triggered=self.nodeAction_PowerProperties),
        #     QAction(tree.nodeActions.delete, self, enabled=True,
        #                 triggered=self.nodeAction_DeletePower)

        # ]
        self.actionsRequestRoot=[
            # QAction(tree.nodeActions.nfr, self, enabled=True,
            #             triggered=self.nodeAction_AddNFR),
            # QAction(tree.nodeActions.ffr, self, enabled=True,
            #             triggered=self.nodeAction_AddFFR),
            # QAction(tree.nodeActions.nf, self, enabled=True,
            #             triggered=self.nodeAction_AddNF),
            # QAction(tree.nodeActions.emi, self, enabled=True,
            #             triggered=self.nodeAction_AddEMI)

        ]
        
        self.actionsFFRItem=[
            # QAction(tree.nodeActions.rename, self, enabled=True,
            #             triggered=self.nodeAction_RenameFFRItem),
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteFFRItem),
               
            # QAction(tree.nodeActions.showHide, self, enabled=True,
            #             triggered=self.nodeAction_ShowHideFFRItem),
            # QAction(tree.nodeActions.properties, self, enabled=True,
            #             triggered=self.nodeAction_FFRProperties),

        ]
        self.actionsNFRRoot=[
            # QAction(tree.projctTreeNodes.nfr, self, enabled=True,
            #             triggered=self.nodeAction_AddNFRItem)

        ]
        self.actionsNFRItem=[
            # QAction(tree.nodeActions.rename, self, enabled=True,
            #             triggered=self.nodeAction_RenameNFRItem),
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteNFRItem),
               
            # QAction(tree.nodeActions.showHide, self, enabled=True,
            #             triggered=self.nodeAction_ShowHideNFRItem),
            # QAction(tree.nodeActions.parallel, self, enabled=True,
            #             triggered=self.nodeAction_ParallelNFRItem),
            # QAction(tree.nodeActions.properties, self, enabled=True,
            #             triggered=self.nodeAction_NFRProperties),

        ]
        # self.actionsNFRoot=[
        #     QAction(tree.nodeActions.nf, self, enabled=True,
        #                 triggered=self.nodeAction_AddNFItem)

        # ]
        self.actionsNFItem=[
            # QAction(tree.nodeActions.rename, self, enabled=True,
            #             triggered=self.nodeAction_RenameNFItem),
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteNFItem),
               
            # QAction(tree.nodeActions.showHide, self, enabled=True,
            #             triggered=self.nodeAction_ShowHideNFItem),
            # QAction(tree.nodeActions.properties, self, enabled=True,
            #             triggered=self.nodeAction_NFProperties),
        ]
        self.actionsEMIRoot=[
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteEMI),

        ]
        self.actionsResultRoot=[]
        self.actionsResultEMRoot=[]
        self.actionsResultEMNFRoot=[]
        self.actionsResultEMDomainRoot=[]
        self.actionsResultFFRRoot=[
           
        ]
        self.actionsResultFFR3DRoot=[
            QAction("dB", self, enabled=True,
                    triggered=self.nodeAction_display_ffr_db),
            QAction("linear", self, enabled=True,
                    triggered=self.nodeAction_display_ffr_linear),
        ]




        self.actionsCurrentRoot=[]
        self.actionsResultExtendRoot=[]
        self.actionsExtendModelRoot=[
            QAction(tree.nodeActions.importS, self, enabled=True,
                        triggered=self.nodeAction_extendImportModel),
            QAction(tree.nodeActions.export, self, enabled=True,
                        triggered=self.nodeAction_extendExportModel)
        ]
        self.actionsExtendNFRoot=[
             QAction(tree.nodeActions.importS, self, enabled=True,
                        triggered=self.nodeAction_extendImportNF)
        ]
        self.actionsExtendEMIRoot=[
            QAction(tree.nodeActions.importS, self, enabled=True,
                        triggered=self.nodeAction_extendImportEMI)
        ]
        self.actionsTransimitRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TransimitArrange),
            
            # QAction(tree.nodeActions.t_array, self, enabled=True,
            #             triggered=self.nodeAction_setModeArray),
            # QAction(tree.nodeActions.t_points, self, enabled=True,
            #             triggered=self.nodeAction_setModePoints)
        ]
        self.actionsArrange=[
            # QAction(tree.nodeActions.import_array, self, enabled=True,
            #             triggered=self.nodeAction_importArray),
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TransimitArrange),
            QAction(tree.nodeActions.show_hide,self,enabled=True,
                        triggered=self.nodeAction_showArray)
                        

        ]
        self.actionsRadio=[
            # QAction(tree.nodeActions.import_radio, self, enabled=True,
            #             triggered=self.nodeAction_importRadio),
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TransimitRadio),
            # QAction(tree.nodeActions.show_hide,self,enabled=True,
            #             triggered=self.nodeAction_showAntenna)
        ]
        self.actionsReceiveRoot=[
            QAction(tree.nodeActions.properties, self, enabled=True,
                        triggered=self.nodeAction_TransimitArrange),
            # QAction(tree.nodeActions.t_array, self, enabled=True,
            #             triggered=self.nodeAction_setModeArray),
            # QAction(tree.nodeActions.t_points, self, enabled=True,
            #             triggered=self.nodeAction_setModePoints)
        ]
        self.actionsPFEMRoot=[
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteEM)
        ]
        self.actionsPFBoundEMPEC=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddEMPEC),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearEMPEC),
        ]
        self.actionsPFBoundEMPECItem=[
            QAction(tree.nodeActions.delete,self,enabled=True,
                    triggered=self.nodeAction_DeleteEMPECItem)
        ]
     

        self.actionsPFCircuitRoot=[
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteCircuit),

        ]
        self.actionsPFBoundCircuitSource=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddCircuitSource),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearCircuitSource),
        ]
        self.actionsPFBoundCircuitSourceItem=[
            QAction(tree.nodeActions.modify,self,enabled=True,
                    triggered=self.nodeAction_ModifyCircuitSourceItem),
            QAction(tree.nodeActions.delete,self,enabled=True,
                    triggered=self.nodeAction_DeleteCircuitSourceItem)
        ]
        self.actionsPFBoundCircuitLoad=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddCircuitLoad),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearCircuitLoad),
        ]
        self.actionsPFBoundCircuitLoadItem=[
            QAction(tree.nodeActions.modify,self,enabled=True,
                    triggered=self.nodeAction_ModifyCircuitLoadItem),
            QAction(tree.nodeActions.delete,self,enabled=True,
                    triggered=self.nodeAction_DeleteCircuitLoadItem)    
        ]
        self.actionsPFThermalRoot=[
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteThermal),
        ]
        self.actionsPFBoundThermalDirichlet=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddThermalDirichlet),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearThermalDirichlet),
            
        ]
        self.actionsPFBoundThermalDirichletItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyThermalDirichletItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteThermalDirichletItem),
        ]
        
        self.actionsPFBoundThermalConvection=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddThermalConvection),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearThermalConvection),
        ]
        self.actionsPFBoundThermalConvectionItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyThermalConvectionItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteThermalConvectionItem),
        ]
        self.actionsPFBoundThermalRadiation=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddThermalRadiation),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearThermalRadiation),
        ]
        self.actionsPFBoundThermalRadiationItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyThermalRadiationItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteThermalRadiationItem),  
        ]

        self.actionsPFBoundThermalSource=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddThermalSource),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearThermalSource),
        ]
        self.actionsPFBoundThermalSourceItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyThermalSourceItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteThermalSourceItem),
        ]
        self.actionsPFStructRoot=[
            # QAction(tree.nodeActions.delete, self, enabled=True,
            #             triggered=self.nodeAction_DeleteStruct),
        ]
        self.actionsPFBoundStructDirichlet=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddStructDirichlet),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearStructDirichlet),
        ]
        self.actionsPFBoundStructDirichletItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyStructDirichletItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteStructDirichletItem),
        ]
        self.actionsPFBoundStructForce=[
            QAction(tree.nodeActions.create, self, enabled=True,
                        triggered=self.nodeAction_AddStructForce),
            QAction(tree.nodeActions.clear, self, enabled=True,
                        triggered=self.nodeAction_ClearStructForce),

        ]
        self.actionsPFBoundStructForceItem=[
            QAction(tree.nodeActions.modify, self, enabled=True,
                        triggered=self.nodeAction_ModifyStructForceItem),
            QAction(tree.nodeActions.delete, self, enabled=True,
                        triggered=self.nodeAction_DeleteStructForceItem),
        ]
    def onLoad(self):
        '''
        定义初始化操作
        '''
        self.currentProject=Project()
        self.initialNodeField()
        self.initialNodeActions()
        
        
        self.tree.setStyle(QtWidgets.QStyleFactory.create('windows'))  # 有加号
        self.tree.setColumnCount(1)  # 设置列数
        self.tree.setHeaderLabels([tree.projctTreeNodes.title])  # 设置树形控件头部的标题
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.initMPI()

        if(not self._show_axis_global):
            api_model.show_axis_global(self.modelViewer,5)
            self._show_axis_global=True
            self.modelViewer.FitAll()

        # if(self.tree.)
       



        # self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        # self.tree.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        pass


    # def getNodeActions(self, nodeName:str,item:QTreeWidgetItem):

    #     if(item.parent()!=None 
    #             and item.parent().text(0)==tree.projctTreeNodes.nfr 
    #             and item.parent().parent()!=None 
    #             and item.parent().parent().text(0)==tree.projctTreeNodes.results):
    #         return[
    #             QAction(tree.nodeActions.rename, self, enabled=True,
    #                     triggered=self.nodeAction_RenameRNFRItem),
               
    #             QAction(tree.nodeActions.properties, self, enabled=True,
    #                     triggered=self.nodeAction_RNFRProperties),
    #             QAction(tree.nodeActions.export, self, enabled=True,
    #                     triggered=self.nodeAction_ExportRNFRItem),
    #         ]
    #     elif(nodeName == tree.projctTreeNodes.current):
    #         return[
    #             QAction(tree.nodeActions.rename, self, enabled=True,
    #                     triggered=self.nodeAction_RenameCurrentsItem),
    #             QAction(tree.nodeActions.export, self, enabled=True,
    #                     triggered=self.nodeAction_ExportCurrents)
    #         ]
    #     else:
    #         return[]
    def topLeffPoint(self):
        p=self.parent.centralWidget().geometry().topLeft()
        return QPoint(p.x(),p.y()+35)
    def nodeAction_itemClick(self):
        currentItem=self.tree.currentItem()
        currentText=currentItem.text(0)
        currentItem.setExpanded(False)
        # if(currentItem.parent()==self.faceRoot):
        #     self.nodeAction_faceClicked()
        #     pass
        # elif(currentItem.parent()==self.em_PECRoot):
        #     self.nodeAction_faceClicked()
        #     pass
        # elif(currentItem.parent()==self.em_PMLRoot):
        #     self.nodeAction_solidClicked()
        #     pass
        if(currentItem.parent()==self.componentRoot):
            self.nodeAction_bodyClicked()
        if(currentItem.parent()==self.pfBoundEMPECRoot):
            self.nodeAction_faceClicked()
            pass
        elif(currentItem.parent()==self.pfBoundCircuitSourceRoot):
            self.nodeAction_faceClicked()
            pass
        elif(currentItem.parent()==self.pfBoundCircuitLoadRoot):
            self.nodeAction_faceClicked()
            pass
        elif(currentItem.parent()==self.pfBoundStructDirichletRoot):
            self.nodeAction_faceClicked()
            pass
        elif(currentItem.parent()==self.pfBoundEMPECRoot):
            self.nodeAction_faceClicked()
            pass

    def nodeAction_doublClick(self):
        
        currentItem=self.tree.currentItem()
        currentText=currentItem.text(0)
        currentItem.setExpanded(False)

        if(currentItem==self.portRoot):
            # self.nodeAction_AddPort()
            pass
        elif(currentItem==self.frequencyRoot):
            self.nodeAction_FrequencyProperties()
            pass
        elif(currentItem==self.sourceRoot):
            # self.nodeAction_AddSource()
            pass
        elif(currentItem==self.loadRoot):
            # self.nodeAction_AddLoad()
            pass
        elif(currentItem==self.powerRoot):
            # self.nodeAction_PowerProperties()
            pass
        # elif(currentItem==self.nfrRoot):
        #     self.nodeAction_AddNFRItem()
        #     pass
        # elif(currentItem==self.ffrRoot):
        #     self.nodeAction_AddFFRItem()
        #     pass
        # elif(currentItem==self.nfRoot):
        #     self.nodeAction_AddNFItem()
        #     pass
        # elif(currentItem.parent()!=None and currentItem.parent()==self.sourceRoot):
        #     # self.nodeAction_SourceProperties()
        #     pass
        # elif(currentItem.parent()!=None and currentItem.parent()==self.loadRoot):
        #     # self.nodeAction_LoadProperties()
        #     pass
        # elif(currentItem.parent()!=None and currentItem.parent()==self.nfrRoot):
        #     self.nodeAction_NFRProperties()
        #     pass
        # elif(currentItem.parent()!=None and currentItem.parent()==self.ffrRoot):
        #     self.nodeAction_FFRProperties()
        #     pass
        elif(currentItem.parent()!=None and currentItem.parent()==self.reqNFRoot):
            self.nodeAction_NFProperties()
        elif(currentItem.parent()!=None and currentItem.parent()==self.modelRoot):
            self.nodeAction_DisplayModel()
            pass
        elif(currentItem.parent()!=None and currentItem.parent()==self.meshRoot):
            # self.nodeAction_DisplayMesh()
            pass
        elif(currentItem==self.emiRoot):
            self.ndoeAction_EMIProperties()
        elif(currentItem==self.currentsRoot):

            self.nodeAction_DisplayCurrents()
        elif(currentItem.parent()!=None and currentItem.parent()==self.ffrRoot_result):
            # self.nodeAction_DisplayFFR()
            pass
        elif(currentItem.parent()!=None and currentItem.parent()==self.nfrRoot_result):
            # self.nodeAction_DisplayNFR()
            pass
        elif(currentItem.parent()!=None and currentItem.parent().parent()!=None and currentItem.parent().parent()==self.nfRoot_result):
            self.nodeAction_DisplayNF()
        elif(currentItem==self.emiRoot_result):
            self.nodeAction_DisplayEMI()
        elif(currentItem==self.t_arrangeRoot or currentItem==self.r_arrangeRoot):
            self.nodeAction_TransimitArrange()
        elif(currentItem==self.t_radioRoot or currentItem==self.r_radioRoot):
            self.nodeAction_TransimitRadio()
        elif(currentItem==self.materialRoot):
            self.nodeAction_MediaLibrary()
        # elif(currentItem.parent()!=None and currentItem.parent()==self.materialRoot):
        #     self.nodeAction_MediaProperties()
      
        # elif(currentItem==self.extendEMIRoot):
        #     self.nodeAction_DisplayEMI_extend()
        # elif(currentItem.parent()==self.extendNFRoot):
        #     self.nodeAction_DisplayNF_extend()
        # elif(currentItem.parent()==self.faceRoot):
        #     self.nodeAction_faceClicked()
        #     pass
        elif(currentItem==self.pfBoundEMPECRoot):
            self.nodeAction_AddEMPEC()
        elif(currentItem==self.pfBoundCircuitSourceRoot):
            self.nodeAction_AddCircuitSource()
        elif(currentItem==self.pfBoundCircuitLoadRoot):
            self.nodeAction_AddCircuitLoad()
        elif(currentItem==self.pfBoundStructDirichletRoot):
            self.nodeAction_AddStructDirichlet()
        elif(currentItem==self.pfBoundStructForceRoot):
            self.nodeAction_AddStructForce()
        elif(currentItem==self.pfBoundThermalDirichletRoot):
            self.nodeAction_AddThermalDirichlet()
        elif(currentItem==self.pfBoundThermalConvectionRoot):
            self.nodeAction_AddThermalConvection()
        elif(currentItem==self.pfBoundThermalRadiationRoot):
            self.nodeAction_AddThermalRadiation()
        elif(currentItem==self.pfBoundThermalSourceRoot):
            self.nodeAction_AddThermalSource()
        elif(currentItem.parent()==self.pfBoundCircuitSourceRoot):
            self.nodeAction_ModifyCircuitSourceItem()
        elif(currentItem.parent()==self.pfBoundCircuitLoadRoot):
            self.nodeAction_ModifyCircuitLoadItem()
        elif(currentItem.parent()==self.pfBoundThermalDirichletRoot):
            self.nodeAction_ModifyThermalDirichletItem()
        elif(currentItem.parent()==self.pfBoundThermalConvectionRoot):
            self.nodeAction_ModifyThermalConvectionItem()
        elif(currentItem.parent()==self.pfBoundThermalRadiationRoot):
            self.nodeAction_ModifyThermalRadiationItem()
        elif(currentItem.parent()==self.pfBoundThermalSourceRoot):
            self.nodeAction_ModifyThermalSourceItem()
        elif(currentItem.parent()==self.pfBoundStructDirichletRoot):
            self.nodeAction_ModifyStructDirichletItem()
        elif(currentItem.parent()==self.pfBoundStructForceRoot):
            self.nodeAction_ModifyStructForceItem()
        elif(currentItem==self.reqTimeRoot):
            self.nodeAction_TimeProperties()
        elif(currentItem==self.reqThermalRoot):
            self.nodeAction_TemperatureProperties()
        elif(currentItem==self.reqDomainRoot):
            self.nodeAction_DomainProperties()
        elif(currentItem==self.reqFFRRoot):
            self.nodeAction_FFRProperties()
        elif(currentItem==self.reqNFRoot):
            self.nodeAction_NFProperties()
        elif(currentItem==self.pfEMRoot):
            self.nodeAction_EMProperties()
        elif(currentItem==self.pfCircuitRoot):
            self.nodeAction_CircuitProperties()
        elif(currentItem==self.pfThermalRoot):
            self.nodeAction_ThermalProperties()
        elif(currentItem==self.pfStructRoot):
            self.nodeAction_StructProperties()
        elif(currentItem==self.resultThermal3DRoot):
            self.nodeAction_DisplayThermal3D()
        elif(currentItem==self.resultThermal2DRoot):
            self.nodeAction_DisplayThermal2D()
        elif(currentItem==self.resultDisplacement3DRoot):
            self.nodeAction_DisplayDisplacement3D()
        elif(currentItem==self.resultEM2DRoot):
            self.nodeAction_DisplayEM_2d()
        elif(currentItem==self.resultEMDomainRoot):
            self.nodeAction_DisplayEM_3d()
        elif(currentItem==self.resultFFR3DRoot):
            self.nodeAction_DisplayEM_ffr()
        elif(currentItem==self.resultFFR2DRoot):
            self.nodeAction_DisplayEM_2dPolar()

        pass
    def strList2String(self,strList:list):
        strContent=""
        if(strList!=None and len(strList)>0):
            for s in strList:
                strContent=strContent+s+"\n"
        return strContent

    def nodeAction_None(self):
        pass
    '''
    project节点操作
    '''
    def sig_createProject(self,projectName:str="DGTD_1"):
        try:
            self.initialNodeField()
            # self.initialModelViewer()
            # self.initialVtkViewer()
            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"创建工程","创建工程文件:"+str(e))

        #初始化所有必需的树节点
        self.tree.clear()
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, projectName)
        # self.root.setIcon(0, QIcon('sync.ico'))
        self.root.setIcon(0, treeIcons.root)
        self.root.setData(0,self.actionIndex,self.actionsRoot)
        self.tree.addTopLevelItem(self.root)
        self.modelRoot = QTreeWidgetItem(self.root)
        self.modelRoot.setText(0, Model.nodeName)
        self.modelRoot.setIcon(0, treeIcons.gdtd_model)
        self.modelRoot.setData(0,self.actionIndex,self.actionsModelRoot)
        self.modelRoot.setExpanded(True)

        self.componentRoot = QTreeWidgetItem(self.root)
        self.componentRoot.setText(0, tree.projctTreeNodes.component)
        self.componentRoot.setIcon(0, treeIcons.gdtd_component)
        self.componentRoot.setData(0,self.actionIndex,[])
        self.componentRoot.setExpanded(True)

        # self.solidRoot=QTreeWidgetItem(self.componentRoot)
        # self.solidRoot.setText(0,tree.projctTreeNodes.shapes)
        # self.solidRoot.setIcon(0,treeIcons.model)
        # self.solidRoot.setData(0,self.actionIndex,[])
        # self.solidRoot.setExpanded(False)

        # self.faceRoot=QTreeWidgetItem(self.componentRoot)
        # self.faceRoot.setText(0,tree.projctTreeNodes.faces)
        # self.faceRoot.setIcon(0,treeIcons.model)
        # self.faceRoot.setData(0,self.actionIndex,[])
        # self.faceRoot.setExpanded(False)
        
        self.materialRoot = QTreeWidgetItem(self.root)
        self.materialRoot.setText(0, tree.projctTreeNodes.media)
        self.materialRoot.setIcon(0, treeIcons.materials)
        self.materialRoot.setData(0,self.actionIndex,self.actionsMaterialRoot)
        self.materialRoot.setExpanded(True)

        


        self.pfRoot = QTreeWidgetItem(self.root)
        self.pfRoot.setText(0, tree.projctTreeNodes.pf)
        self.pfRoot.setIcon(0, treeIcons.gdtd_pf)
        self.pfRoot.setData(0,self.actionIndex,self.actionsPFRoot)
        self.pfRoot.setExpanded(True)

        self.pfEMRoot=QTreeWidgetItem(self.pfRoot) #物理场-电磁，默认隐藏，添加时再显示
        self.pfEMRoot.setText(0, tree.projctTreeNodes.pf_em)
        self.pfEMRoot.setIcon(0, treeIcons.pf_em)
        self.pfEMRoot.setData(0,self.actionIndex,self.actionsPFEMRoot)
        self.pfEMRoot.setHidden(True)

        self.pfCircuitRoot=QTreeWidgetItem(self.pfRoot) #物理场-电路，默认隐藏，添加时再显示
        self.pfCircuitRoot.setText(0, tree.projctTreeNodes.pf_circuit)
        self.pfCircuitRoot.setIcon(0, treeIcons.pf_circuit)
        self.pfCircuitRoot.setData(0,self.actionIndex,self.actionsPFCircuitRoot)    
        self.pfCircuitRoot.setHidden(True)

        self.pfThermalRoot=QTreeWidgetItem(self.pfRoot) #物理场-热传递，默认隐藏，添加时再显示
        self.pfThermalRoot.setText(0, tree.projctTreeNodes.pf_thermal)
        self.pfThermalRoot.setIcon(0, treeIcons.pf_thermal)
        self.pfThermalRoot.setData(0,self.actionIndex,self.actionsPFThermalRoot)
        self.pfThermalRoot.setHidden(True)

        self.pfStructRoot=QTreeWidgetItem(self.pfRoot) #物理场-结构，默认隐藏，添加时再显示
        self.pfStructRoot.setText(0, tree.projctTreeNodes.pf_struct)
        self.pfStructRoot.setIcon(0, treeIcons.gdtd_pf_struct)
        self.pfStructRoot.setData(0,self.actionIndex,self.actionsPFStructRoot)
        self.pfStructRoot.setHidden(True)

        self.pfBoundRoot=QTreeWidgetItem(self.root) #物理场-边界条件，默认隐藏，添加时再显示
        self.pfBoundRoot.setText(0, tree.projctTreeNodes.pf_boundary)
        self.pfBoundRoot.setIcon(0, treeIcons.gdtd_bnd_source)
        self.pfBoundRoot.setData(0,self.actionIndex,[])

        self.pfBoundEMRoot=QTreeWidgetItem(self.pfBoundRoot) #物理场-电磁-边界条件，默认隐藏，添加时再显示
        self.pfBoundEMRoot.setText(0, tree.projctTreeNodes.pf_em)
        self.pfBoundEMRoot.setIcon(0, treeIcons.pf_bound_em)
        self.pfBoundEMRoot.setData(0,self.actionIndex,[])
        self.pfBoundEMRoot.setExpanded(True)
        self.pfBoundEMRoot.setHidden(True)

        self.pfBoundEMPECRoot=QTreeWidgetItem(self.pfBoundEMRoot) #物理场-电磁-PEC，默认隐藏，添加时再显示
        self.pfBoundEMPECRoot.setText(0, tree.projctTreeNodes.pf_em_pec)
        self.pfBoundEMPECRoot.setIcon(0, treeIcons.gdtd_bound_pec)
        self.pfBoundEMPECRoot.setData(0,self.actionIndex,self.actionsPFBoundEMPEC)
        # self.pfBoundEMPECRoot.setHidden(True)

        self.pfBoundCircuitRoot=QTreeWidgetItem(self.pfBoundRoot) #物理场-电路-边界条件，默认隐藏，添加时再显示
        self.pfBoundCircuitRoot.setText(0, tree.projctTreeNodes.pf_circuit)
        self.pfBoundCircuitRoot.setIcon(0, treeIcons.pf_bound_circuit)
        self.pfBoundCircuitRoot.setData(0,self.actionIndex,[])
        self.pfBoundCircuitRoot.setExpanded(True)
        self.pfBoundCircuitRoot.setHidden(True)

        self.pfBoundCircuitSourceRoot=QTreeWidgetItem(self.pfBoundCircuitRoot) #物理场-电路-电源，默认隐藏，添加时再显示
        self.pfBoundCircuitSourceRoot.setText(0, tree.projctTreeNodes.pf_circuit_source)
        self.pfBoundCircuitSourceRoot.setIcon(0, treeIcons.pf_bound_circuit_source)
        self.pfBoundCircuitSourceRoot.setData(0,self.actionIndex,self.actionsPFBoundCircuitSource)
        # self.pfBoundCircuitSourceRoot.setHidden(True)

        self.pfBoundCircuitLoadRoot=QTreeWidgetItem(self.pfBoundCircuitRoot) #物理场-电路-负载，默认隐藏，添加时再显示
        self.pfBoundCircuitLoadRoot.setText(0, tree.projctTreeNodes.pf_circuit_load)
        self.pfBoundCircuitLoadRoot.setIcon(0, treeIcons.pf_bound_circuit_load)
        self.pfBoundCircuitLoadRoot.setData(0,self.actionIndex,self.actionsPFBoundCircuitLoad)
        # self.pfBoundCircuitLoadRoot.setHidden(True)

        self.pfBoundThermalRoot=QTreeWidgetItem(self.pfBoundRoot) #物理场-热传递-边界条件，默认隐藏，添加时再显示
        self.pfBoundThermalRoot.setText(0, tree.projctTreeNodes.pf_thermal)
        self.pfBoundThermalRoot.setIcon(0, treeIcons.pf_bound_thermal)
        self.pfBoundThermalRoot.setData(0,self.actionIndex,[])
        self.pfBoundThermalRoot.setExpanded(True)
        self.pfBoundThermalRoot.setHidden(True)

        self.pfBoundThermalDirichletRoot=QTreeWidgetItem(self.pfBoundThermalRoot) #物理场-热传递-Dirichlet，默认隐藏，添加时再显示
        self.pfBoundThermalDirichletRoot.setText(0, tree.projctTreeNodes.pf_thermal_dirichlet)
        self.pfBoundThermalDirichletRoot.setIcon(0, treeIcons.gdtd_bound_thermal_dirichlet)
        self.pfBoundThermalDirichletRoot.setData(0,self.actionIndex,self.actionsPFBoundThermalDirichlet)
        # self.pfBoundThermalDirichletRoot.setHidden(True)

        self.pfBoundThermalConvectionRoot=QTreeWidgetItem(self.pfBoundThermalRoot) #物理场-热传递-对流，默认隐藏，添加时再显示
        self.pfBoundThermalConvectionRoot.setText(0, tree.projctTreeNodes.pf_thermal_convection)
        self.pfBoundThermalConvectionRoot.setIcon(0, treeIcons.gdtd_bound_thermal_convection)
        self.pfBoundThermalConvectionRoot.setData(0,self.actionIndex,self.actionsPFBoundThermalConvection)
        # self.pfBoundThermalConvectionRoot.setHidden(True)

        self.pfBoundThermalRadiationRoot=QTreeWidgetItem(self.pfBoundThermalRoot) #物理场-热传递-辐射，默认隐藏，添加时再显示
        self.pfBoundThermalRadiationRoot.setText(0, tree.projctTreeNodes.pf_thermal_radiation)
        self.pfBoundThermalRadiationRoot.setIcon(0, treeIcons.gdtd_bound_thermal_radiation)
        self.pfBoundThermalRadiationRoot.setData(0,self.actionIndex,self.actionsPFBoundThermalRadiation)
        # self.pfBoundThermalRadiationRoot.setHidden(True)

        self.pfBoundThermalSourceRoot=QTreeWidgetItem(self.pfBoundThermalRoot) #物理场-热传递-热源，默认隐藏，添加时再显示
        self.pfBoundThermalSourceRoot.setText(0, tree.projctTreeNodes.pf_thermal_source)
        self.pfBoundThermalSourceRoot.setIcon(0, treeIcons.gdtd_bound_thermal_source)
        self.pfBoundThermalSourceRoot.setData(0,self.actionIndex,self.actionsPFBoundThermalSource)
        # self.pfBoundThermalSourceRoot.setHidden(True)

        self.pfBoundStructRoot=QTreeWidgetItem(self.pfBoundRoot) #物理场-结构-边界条件，默认隐藏，添加时再显示
        self.pfBoundStructRoot.setText(0, tree.projctTreeNodes.pf_struct)
        self.pfBoundStructRoot.setIcon(0, treeIcons.gdtd_bound_struct)
        self.pfBoundStructRoot.setData(0,self.actionIndex,[])
        self.pfBoundStructRoot.setExpanded(True)
        self.pfBoundStructRoot.setHidden(True)

        self.pfBoundStructDirichletRoot=QTreeWidgetItem(self.pfBoundStructRoot) #物理场-结构-Dirichlet，默认隐藏，添加时再显示
        self.pfBoundStructDirichletRoot.setText(0, tree.projctTreeNodes.pf_struct_dirichlet)
        self.pfBoundStructDirichletRoot.setIcon(0, treeIcons.gdtd_bound_struct_dirichlet)
        self.pfBoundStructDirichletRoot.setData(0,self.actionIndex,self.actionsPFBoundStructDirichlet)
        # self.pfBoundStructDirichletRoot.setHidden(True)

        self.pfBoundStructForceRoot=QTreeWidgetItem(self.pfBoundStructRoot) #物理场-结构-力，默认隐藏，添加时再显示
        self.pfBoundStructForceRoot.setText(0, tree.projctTreeNodes.pf_struct_force)
        self.pfBoundStructForceRoot.setIcon(0, treeIcons.gdtd_bound_struct_force)
        self.pfBoundStructForceRoot.setData(0,self.actionIndex,self.actionsPFBoundStructForce)
        # self.pfBoundStructForceRoot.setHidden(True)


    
        self.requestRoot = QTreeWidgetItem(self.root)
        self.requestRoot.setText(0, tree.projctTreeNodes.requests)
        self.requestRoot.setIcon(0, treeIcons.gdtd_req)
        self.requestRoot.setData(0,self.actionIndex,self.actionsRequestRoot)
        self.requestRoot.setExpanded(True)

        self.reqTimeRoot=QTreeWidgetItem(self.requestRoot)
        self.reqTimeRoot.setText(0,tree.projctTreeNodes.reqTime)
        self.reqTimeRoot.setIcon(0,treeIcons.req_time)
        self.reqTimeRoot.setData(0,self.actionIndex,self.actionsReqTimeRoot)
        self.reqTimeRoot.setExpanded(True)

        self.reqNFRoot=QTreeWidgetItem(self.requestRoot)
        self.reqNFRoot.setText(0, tree.projctTreeNodes.reqNF)
        self.reqNFRoot.setIcon(0, treeIcons.gdtd_req_points)
        self.reqNFRoot.setData(0,self.actionIndex,self.actionsReqNFRoot)
        self.reqNFRoot.setExpanded(True)

        self.reqDomainRoot=QTreeWidgetItem(self.requestRoot)
        self.reqDomainRoot.setText(0,tree.projctTreeNodes.reqDomain)
        self.reqDomainRoot.setIcon(0,treeIcons.gdtd_req_domain)
        self.reqDomainRoot.setData(0,self.actionIndex,[])
        self.reqDomainRoot.setExpanded(True)

        self.reqFFRRoot=QTreeWidgetItem(self.requestRoot)
        self.reqFFRRoot.setText(0, tree.projctTreeNodes.reqFFR)
        self.reqFFRRoot.setIcon(0, treeIcons.req_ffr)
        self.reqFFRRoot.setData(0,self.actionIndex,self.actionsReqFFRRoot)
        self.reqFFRRoot.setHidden(True)

        self.reqThermalRoot=QTreeWidgetItem(self.requestRoot)
        self.reqThermalRoot.setText(0,tree.projctTreeNodes.reqThermal)
        self.reqThermalRoot.setIcon(0,treeIcons.req_thermal)
        self.reqThermalRoot.setData(0,self.actionIndex,self.actionsReqThermalRoot)
        self.reqThermalRoot.setHidden(True)

        self.meshRoot = QTreeWidgetItem(self.root)
        self.meshRoot.setText(0, tree.projctTreeNodes.mesh)
        self.meshRoot.setIcon(0, treeIcons.mesh)
        self.meshRoot.setData(0,self.actionIndex,self.actionsMeshRoot)
        self.meshRoot.setExpanded(True)




        self.resultRoot = QTreeWidgetItem(self.root)
        self.resultRoot.setText(0, tree.projctTreeNodes.results)
        self.resultRoot.setIcon(0, treeIcons.results)
        self.resultRoot.setData(0,self.actionIndex,self.actionsResultRoot)
        self.resultRoot.setExpanded(True)

        self.resultEMRoot=QTreeWidgetItem(self.resultRoot)
        self.resultEMRoot.setText(0,tree.projctTreeNodes.result_em)
        self.resultEMRoot.setIcon(0,treeIcons.gdtd_result_em)
        self.resultEMRoot.setData(0,self.actionIndex,self.actionsResultEMRoot)
        self.resultEMRoot.setExpanded(True)
        self.resultEMRoot.setHidden(True)   

        self.resultEM2DRoot=QTreeWidgetItem(self.resultEMRoot)
        self.resultEM2DRoot.setText(0,tree.projctTreeNodes.result_em_nf)
        self.resultEM2DRoot.setIcon(0,treeIcons.gdtd_result_em_points)
        self.resultEM2DRoot.setData(0,self.actionIndex,self.actionsResultEMNFRoot)
        self.resultEM2DRoot.setExpanded(True)

        self.resultEMDomainRoot=QTreeWidgetItem(self.resultEMRoot)
        self.resultEMDomainRoot.setText(0,tree.projctTreeNodes.result_em_domain)    
        self.resultEMDomainRoot.setIcon(0,treeIcons.gdtd_result_em_domain)
        self.resultEMDomainRoot.setData(0,self.actionIndex,self.actionsResultEMDomainRoot)
        self.resultEMDomainRoot.setExpanded(True)

        self.resultFFRRoot=QTreeWidgetItem(self.resultRoot)
        self.resultFFRRoot.setText(0,tree.projctTreeNodes.result_ffr)
        self.resultFFRRoot.setIcon(0,treeIcons.gdtd_ffr)
        self.resultFFRRoot.setData(0,self.actionIndex,self.actionsResultFFRRoot)
        self.resultFFRRoot.setExpanded(True)
        self.resultFFRRoot.setHidden(True)

        self.resultFFR2DRoot=QTreeWidgetItem(self.resultFFRRoot)
        self.resultFFR2DRoot.setText(0,"2D方向图")
        self.resultFFR2DRoot.setIcon(0,treeIcons.gdtd_2d_ffr)
        # self.resultFFR2DRoot.setData(0,self.actionIndex,self.actionsResultFFR2DRoot)
        self.resultFFR2DRoot.setExpanded(True)

        self.resultFFR3DRoot=QTreeWidgetItem(self.resultFFRRoot)
        self.resultFFR3DRoot.setText(0,"3D方向图")
        self.resultFFR3DRoot.setIcon(0,treeIcons.gdtd_3d_ffr)
        self.resultFFR3DRoot.setData(0,self.actionIndex,self.actionsResultFFR3DRoot)
        self.resultFFR3DRoot.setExpanded(True)
        

        self.resultThermalRoot=QTreeWidgetItem(self.resultRoot)
        self.resultThermalRoot.setText(0,tree.projctTreeNodes.result_thermal)
        self.resultThermalRoot.setIcon(0,treeIcons.gdtd_result_thermal)
        self.resultThermalRoot.setData(0,self.actionIndex,[])
        self.resultThermalRoot.setExpanded(True)
        self.resultThermalRoot.setHidden(True)

        self.resultThermal2DRoot=QTreeWidgetItem(self.resultThermalRoot)
        self.resultThermal2DRoot.setText(0,tree.projctTreeNodes.result_thermal_2d)
        self.resultThermal2DRoot.setIcon(0,treeIcons.gdtd_result_thermal_points)

        self.resultThermal3DRoot=QTreeWidgetItem(self.resultThermalRoot)
        self.resultThermal3DRoot.setText(0,tree.projctTreeNodes.result_thermal_3d)
        self.resultThermal3DRoot.setIcon(0,treeIcons.gdtd_result_thermal_domain)


        self.resultStructRoot=QTreeWidgetItem(self.resultRoot)
        self.resultStructRoot.setText(0,tree.projctTreeNodes.result_struct)
        self.resultStructRoot.setIcon(0,treeIcons.gdtd_result_struct)
        self.resultStructRoot.setData(0,self.actionIndex,[])
        self.resultStructRoot.setExpanded(True)
        self.resultStructRoot.setHidden(True)

        self.resultDisplacement3DRoot=QTreeWidgetItem(self.resultStructRoot)
        self.resultDisplacement3DRoot.setText(0,tree.projctTreeNodes.result_struct_3d)
        self.resultDisplacement3DRoot.setIcon(0,treeIcons.gdtd_result_struct_domain)


        # self.resultExtendRoot=QTreeWidgetItem(self.root)
        # self.resultExtendRoot.setText(0,tree.projctTreeNodes.results_extend)
        # self.resultExtendRoot.setIcon(0,treeIcons.results)
        # self.resultExtendRoot.setData(0,self.actionIndex,self.actionsResultExtendRoot)
        # self.resultExtendRoot.setExpanded(True)

        # self.extendNFRoot=QTreeWidgetItem(self.resultExtendRoot)
        # self.extendNFRoot.setText(0,tree.projctTreeNodes.nf)
        # self.extendNFRoot.setIcon(0,treeIcons.nf)
        # self.extendNFRoot.setData(0,self.actionIndex,self.actionsExtendNFRoot)
        # self.extendNFRoot.setExpanded(True)

        # self.extendEMIRoot=QTreeWidgetItem(self.resultExtendRoot)
        # self.extendEMIRoot.setText(0,tree.projctTreeNodes.emi)
        # self.extendEMIRoot.setIcon(0,treeIcons.emi)
        # self.extendEMIRoot.setData(0,self.actionIndex,self.actionsExtendEMIRoot)
        # self.extendEMIRoot.setExpanded(True)

        self.tree.expandAll()  # 节点全部展开
        # self.sigPickFace.emit()

        pass
    def nodeAction_RenameProject(self):
        self.nodeAction_Rename(self.tree.currentItem())
        pass
    def sig_mpiSet(self,mpiNum,installPath):
        self.currentProject.mpiNum=mpiNum
        Project.mpiInstallPath=installPath
    def setMPI(self):
        mpiNum=self.currentProject.mpiNum
        installPath=Project.mpiInstallPath
        frm_mpi=frmMPI(self,mpiNum,installPath)
        frm_mpi.show()
        frm_mpi.sigMPISet.connect(self.sig_mpiSet)
        frm_mpi.sigMPIRegister.connect(self.sig_mpiRegister)
        frm_mpi.sigMPITest.connect(self.sig_mpiTest)

    def sig_mpiRegister(self):
        cmd_register=[Project.mpiInstallPath+Project.mpiRegisterFile]
        subprocess.Popen(cmd_register)
        pass
    def sig_mpiTest(self):
        cmd_register=[Project.mpiInstallPath+Project.mpiTestFile]
        subprocess.Popen(cmd_register)
        pass
    def nodeAction_StopSimulation(self):
        if(self.currentProcess==None):
            QtWidgets.QMessageBox.about(self,"求解计算","没有正在运行的算法程序")
            return
        os.kill(self.currentProcess.pid,signal.SIGTERM)
        self._logger.info("算法程序已经停止")
        self.readTimer.stop()

    def simulation_input_generate(self):
        try:
            self.nodeAction_SaveProject(False)
            QtWidgets.QMessageBox.about(self,"生成文件","生成输入文件成功             ")
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"生成文件","生成输入文件失败:"+str(e))
            traceback.print_exc()
    def simulation_run_directly(self):
        self.nodeAction_RunSimulation(False)
    def sig_run_sim_exe(self,exeName):
        try:
            sourceSolverFile=self._dir+"\\"+exeName
            print("run exeName",exeName)
            if(self.currentProject.mpiNum>1 and "EM" in exeName):
                print("sim use mpi",exeName)

            # sourceSolverFile="D:\\Program Files\\Axure\Axure RP 8\\AxureRP8.exe"
            # sourceSolverFile="C:/Windows/System32/notepad.exe"
            if(not os.path.exists(sourceSolverFile)):
                QtWidgets.QMessageBox.about(self,"求解计算","算法模块不存在，请检查文件:\n"+sourceSolverFile)
                return
            exe_dir = os.path.dirname(sourceSolverFile)
   

            cmd=[
                sourceSolverFile
            ]
            self.console.clear()
            if(self.currentProject.mpiNum>1 and "EM" in exeName):
                # print("sim use mpi",exeName)
                cmd=f"mpiexec -localonly {self.currentProject.mpiNum} {exeName}"
               
                p = subprocess.Popen(cmd,
                                 cwd=exe_dir, 
                                 creationflags=subprocess.CREATE_NEW_CONSOLE,
                                #  stdout=subprocess.PIPE,
                                #  stderr=subprocess.PIPE
                                 )
                self.currentProcess=p
            else:
                p=None
                if not CONSOLE_WINDOW:
                    p = subprocess.Popen(cmd,
                                        cwd=exe_dir, 
                                        # env=env,
                                        stdout=subprocess.PIPE,
                                        creationflags = subprocess.CREATE_NO_WINDOW,
                                        stderr=subprocess.PIPE,
                                    )
                    self.currentProcess=p 
                    self.nbsr = NBSR(p.stdout)
                    self.startReadTimer() 
            
                else:
                    p = subprocess.Popen(cmd,
                                        cwd=exe_dir, 
                                        creationflags = subprocess.CREATE_NEW_CONSOLE,
                                    )
                    self.currentProcess=p 
                    # self.nbsr = NBSR(p.stdout)
                    # self.startReadTimer() 
                
          
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"求解计算","算法程序出错"+str(e))
        pass
    def nodeAction_RunSimulation(self,saveProject=True):
        '''启动并运行计算模块
        1.检测计算模块是否存在
        2.拷贝计算模块到用户目录
        3.拷贝配置文件到用户目录，与计算模块同一目录
        4.启动计算模块
        '''
        try:
            if(self.currentProject.fpath==None or self.currentProject.fpath==""):
                QtWidgets.QMessageBox.about(self,"求解计算","请先保存工程文件             ")
                return
            if(saveProject):
                self.nodeAction_SaveProject(False)
           
            # self._postFilter=PostFilter() #重置后处理筛选对象
            # self._postData=PostData()

            # self.nodeAction_InitResults()
            if(not hasattr(self.currentProject,"exeName")):#之前的工程，保持兼容
                frm=frmSimSelect(self)
                frm.move(self.topLeffPoint())
                frm.show()
                frm.sigApplySimExe.connect(self.sig_run_sim_exe)
            else:
                exeName=self.currentProject.exeName
                self.sig_run_sim_exe(exeName)
            return


            exeName="thermal.exe"
            pf=self._pf
            calTypeList=[0,0,0,0]
            if(pf.em.used):
                calTypeList[0]=1
            if(pf.circuit.used):
                calTypeList[1]=1
            if(pf.thermal.used):
                calTypeList[2]=1
            if(pf.struct.used):
                calTypeList[3]=1
            if(calTypeList[0]==0 and calTypeList[1]==0 and calTypeList[2]==1 and calTypeList[3]==0):
                exeName="thermal.exe"
            elif(calTypeList[0]==0 and calTypeList[1]==0 and calTypeList[2]==0 and calTypeList[3]==1):
                exeName="Mechanical.exe"
            elif(calTypeList[0]==1 and calTypeList[1]==1 and calTypeList[2]==0 and calTypeList[3]==0):
                
                exeName="EM.exe"
                # else:
                #     exeName=f"mpiexec -localonly {self.currentProject.mpiNum} EM.exe"
            elif(calTypeList[0]==1 and calTypeList[1]==1 and calTypeList[2]==1 and calTypeList[3]==0):
                exeName="EM_Thermal.exe"
            elif(calTypeList[0]==0 and calTypeList[1]==0 and calTypeList[2]==1 and calTypeList[3]==1):
                exeName="Thermal_Mechanical.exe"
            elif(calTypeList[0]==1 and calTypeList[1]==1 and calTypeList[2]==0 and calTypeList[3]==1):
                exeName="EM_Mechanical.exe"
            elif(calTypeList[0]==1 and calTypeList[1]==1 and calTypeList[2]==1 and calTypeList[3]==1):
                exeName="EM_Thermal_Mechanical.exe"
            else:
                QtWidgets.QMessageBox.about(self,"求解计算","不支持的计算类型             ")
                return

            sourceSolverFile=self._dir+"\\"+exeName

            # sourceSolverFile="D:\\Program Files\\Axure\Axure RP 8\\AxureRP8.exe"
            # sourceSolverFile="C:/Windows/System32/notepad.exe"
            if(not os.path.exists(sourceSolverFile)):
                QtWidgets.QMessageBox.about(self,"求解计算","算法模块不存在，请检查文件:\n"+sourceSolverFile)
                return
            exe_dir = os.path.dirname(sourceSolverFile)
   

            cmd=[
                sourceSolverFile
            ]
            self.console.clear()
            if(self.currentProject.mpiNum>1 and exeName=="EM.exe"):
                cmd=f"mpiexec -localonly {self.currentProject.mpiNum} EM.exe"
               
                # subprocess.Popen(['powershell', '-Command', f'Start-Process "{exeName}" -Verb runAs'])

                # cmd=[exeName]
                p = subprocess.Popen(cmd,
                                 cwd=exe_dir, 
                                 creationflags=subprocess.CREATE_NEW_CONSOLE,
                                #  stdout=subprocess.PIPE,
                                #  stderr=subprocess.PIPE
                                 )
                self.currentProcess=p
            else:
                p = subprocess.Popen(cmd,
                                    cwd=exe_dir, 
                                    stdout=subprocess.PIPE,
                                    creationflags = subprocess.CREATE_NO_WINDOW,
                                    stderr=subprocess.PIPE
                                 )
                self.currentProcess=p 
                self.nbsr = NBSR(p.stdout)
                self.startReadTimer() 
          
            
         
            
            # encoding=Project.solverEncoding
               
            
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"求解计算","调用算法程序出错"+str(e))
            traceback.print_exc()
   
    def startReadTimer(self):
        # self._logger.info("开始计算....")
        self.readTimer=QTimer()
        self.readTimer.timeout.connect(self.readSimulationLog)
        self.readTimer.start(200)
        pass
    def readSimulationLog(self):
        # print("read log",datetime.now())
        p=self.currentProcess
        if(p.poll() is None):
            #进程未结束
            output = self.nbsr.readline(0.1)
            if(output!=None):
                self.console.print_text(str(output,Project.solverEncoding)+"\r\n")
                # print("output",str(output,Project.solverEncoding))
                QtWidgets.QApplication.processEvents()
            pass
           
        else:
            if(p.poll() is not None and p.stderr!=None and  p.stderr.readable()):
                line = p.stderr.read()
                line=line.strip()
                if line and self.console!=None:
                    self.console.print_text(str(line,Project.solverEncoding)+"\r\n")
                    # print("error",str(line,Project.solverEncoding))
                
                if(p.stdout!=None and p.stdout.readable()):
                    line = p.stdout.read()
                    line=line.strip()
                    if line and self.console!=None:
                        self.console.print_text(str(line,Project.solverEncoding)+"\r\n")
                        # print("p.out",str(line,Project.solverEncoding))
            self.readTimer.stop()
            self.currentProcess=None
        

            QtWidgets.QApplication.processEvents()  
        return

        #读取进度文件
        
        self.parent.log_clear()
        rate="0"
        endIndex=0
        if(os.path.exists(self.currentProject.getLogRateFileName())):
            rLogs=api_reader.readText(self.currentProject.getLogRateFileName())
            for i in range(len(rLogs)):
                r=rLogs[i].strip()
                if(len(r)<1):
                    continue
            
                if(r.startswith("<!--End_Process Rate")):
                    rate=rLogs[i-1].strip()
                    endIndex=i
            
            res_rate="计算进度:{0}%".format(rate)
            self._pLogger.info(res_rate)
            outList=rLogs[endIndex+1:]
            for r in outList:
                if(len(r.strip())<1):
                    continue
                self._pLogger.info(r)
        
            
            # if("100" in r):
            #     #手动停止程序
            #     os.kill(self.currentProcess.pid,signal.SIGTERM)
            #     pass

           
        pass
    def get_base_path(self):
        return self.currentProject.getSolverPath()
    def get_input_path(self):
        return self.currentProject.getSolverPath()+"/input"
    def get_output_path(self):
        return self.currentProject.getSolverPath()+"/output"
    def get_fname_geo(self):
        return self.currentProject.getSolverPath()+"/input/{0}.geo".format(self.currentProject.name)
    def get_name_model_named(self):
        return self.currentProject.getSolverPath()+"/input/{0}_model_named.stp".format(self.currentProject.name)
    def get_name_pml_named(self):
        return self.currentProject.getSolverPath()+"/input/{0}_pml_named.stp".format(self.currentProject.name)
    def get_name_exf_named(self):
        return self.currentProject.getSolverPath()+"/input/{0}_exf_named.stp".format(self.currentProject.name)
    def get_fname_param(self):
        return self.currentProject.getSolverPath()+"/input/Parameters.txt"
    def get_fname_medium(self):
        return self.currentProject.getSolverPath()+"/input/Materials.txt"
    def get_fname_bound(self):
        return self.currentProject.getSolverPath()+"/input/BoundarySource.txt"
    def get_fname_mesh(self):
        return self.currentProject.getSolverPath()+"/input/Mesh.txt"
    def get_fname_mesh_vtk(self):
        return self.currentProject.getSolverPath()+"/input/Mesh.vtk"
    def get_fname_mesh_msh(self):
        return self.currentProject.getSolverPath()+"/input/Mesh.msh"
    def get_fname_thermal_3d(self):
        return self.currentProject.getSolverPath()+"/output/res_Temperature_3D.txt"
    def get_fname_thermal_2d(self):
        return self.currentProject.getSolverPath()+"/output/res_Temperature_point_time.txt"
    def get_fname_displacement_3d(self):
        return self.currentProject.getSolverPath()+"/output/res_Displacement_3D.txt"
    def get_fname_em_2d(self):
        return self.currentProject.getSolverPath()+"/output/res_E_point_time.txt"
    def get_fname_em_3d(self):
        return self.currentProject.getSolverPath()+"/output/res_E_3D.txt"
    def get_fname_em_ffr(self):
        return self.currentProject.getSolverPath()+"/output/res_Radiation_Pattern.txt"
    
    # def projectSaveMesh(self):
    #     '''保存mesh文件 mesh/target.mesh and target.stl
    #     '''
    #     if(self.currentMesh==None):
    #         return
    #     fname=self.currentProject.fpath+"/mesh/target.mesh"
    #     api_mesh.exportMesh2EMX(self.currentMesh.mesh,fname)
    #     pass
    def projectSaveModel(self):
        '''拷贝模型文件到工程目录下
        '''
        if(self.currentModel!=None):
            srcFile=self.currentModel.fileName
            dstFile=self.currentProject.getModelPath()+"/"+self.currentModel.fileNameNoPath
            srcGeo=self.currentModel.geoFile
            dstGeo=self.currentProject.getModelPath()+"/"+self.currentModel.name+".vstl"

            if(not os.path.exists(srcFile)):
                QtWidgets.QMessageBox.about(self,"保存模型","模型文件不存在:"+srcFile)
                return
            if(not os.path.exists(srcGeo)):
                QtWidgets.QMessageBox.about(self,"保存模型","模型几何文件不存在:"+srcGeo)
                return

            if(srcFile!=dstFile and os.path.exists(srcFile)):
                api_project.copyFile(srcFile,dstFile)
                self.currentModel.fileName=dstFile
                
            if(srcGeo!=dstGeo and os.path.exists(srcGeo)):
                api_project.copyFile(srcGeo,dstGeo)
                self.currentModel.geoFile=dstGeo
            self.copy2Project(self.currentModel.fileName,self.currentProject.getSolverPath()+"/input")
           
            return
        pass

    def copy2Project(self,srcFile:str,dstPath:str):
        '''拷贝文件到工程目录下
        '''
        if(srcFile==None or dstPath==None):
            return
        if(os.path.isdir(srcFile)):
            return #不拷贝文件夹
        dstFile=dstPath+"/"+os.path.basename(srcFile)
        if(srcFile!=dstFile):
            api_project.copyFile(srcFile,dstFile)
        return dstFile
    def copyFolder(self,srcPath:str,dstPath:str):
        '''拷贝out文件夹下的所有内容到工程目录下，另存为时使用
        '''
        if(srcPath==None or dstPath==None):
            return
        if(srcPath==dstPath):
            return
        if(not os.path.exists(srcPath)):
            return
        if(not os.path.exists(dstPath)):
            os.makedirs(dstPath)
        for root,dirs,files in os.walk(srcPath):
            for file in files:
                srcFile=os.path.join(root,file)
                dstFile=dstPath+"/"+file
                if(srcFile!=dstFile):
                    api_project.copyFile(srcFile,dstFile)
        pass
    
    def projectSaveParam(self):
        #保存全局参数文件project.param
        fname=self.get_fname_param()
        ffrObj=self.reqFFRRoot.data(0,FFR.objIndex)
        nfObj=self.reqNFRoot.data(0,NF.objIndex)
        points_nf=[]
        if(nfObj!=None):
            points_nf=self.getPoints_nf(nfObj)

        reqObj=RequestParam()
        timeObj=self.reqTimeRoot.data(0,RequestParam.objIndex)
        domainObj=self.reqDomainRoot.data(0,RequestParam.objIndex)
        thermalObj=self.reqThermalRoot.data(0,RequestParam.objIndex)
        pml_param=(0,0,0,0,0,0,0)
        if(timeObj!=None):
            reqObj.reqTime=timeObj
        if(domainObj!=None):
            reqObj.reqDomain=domainObj
        if(thermalObj!=None):
            reqObj.reqTemperature=thermalObj
        if(self.currentModel!=None and hasattr(self.currentModel,"pml_param")):
            pml_param=self.currentModel.pml_param

    
 
        code,message,data=api_writer.write_param_fem(fname,self._pf,reqObj,points_nf,ffrObj,pml_param)
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"生成求解参数文件",message)
           
            self._cLogger.debug("生成求解参数文件失败:"+message)
            
        pass
    def projectSaveBound(self):
        fname=self.get_fname_bound()
        mediumDic={}
        mediumIndex=-1
        if(self.currentModel!=None):
            mediumDic=self.currentModel.mediumFaces
            mediumIndex=self.currentModel.medium
        code,message,data=api_writer.write_bound_fem(fname,self._pf,mediumDic,mediumIndex)
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"生成边界条件文件",message)
           
            self._cLogger.debug("生成边界条件文件失败:"+message)
        pass
    def getPoints_nf(self,nf:NF):
        if(nf!=None):
            if(nf.pointType==0):#均匀分布
                points=api_writer.get_nf_points(nf)
            else:
                points=nf.pointList
            
            if(nf.axisType==1 and self._antenna_t!=None and self._antenna_t._face_id>0):#局部坐标系，需要转换数据
                center=self._antenna_t.center
                normal=self._antenna_t.normal_dir
                angel=self._antenna_t.offset_rotate_z
                points=api_model.local_global_points(center,normal,angel,points)
            return points
        return []
        pass
    def projectSaveMedia(self):
        '''
        保存材料数据
        '''
        fname=self.get_fname_medium()
        mediaList=self._mediaList
        code,message,_=api_writer.write_mediaLibrary_fem(fname,mediaList)
        # isotropicList=self._mediaDic[MediaBase.isotropic]
        # dispersiveList=self._mediaDic[MediaBase.dispersive]

       
        # code,message,_=api_writer.write_medialLibrary_SBR(fname,isotropicList,dispersiveList)
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"生成材料文件",message)
        pass
    def projectSaveGeo(self):
        '''
        保存几何模型数据，以网格形式保存，需要关联材料信息
        '''
        if(self.currentModel==None or self.currentModel.shape==None):
            return
        shape=self.currentModel.shape
    
        fname=self.get_fname_geo()
        medium=self.currentModel.medium
        mediumFaces=self.currentModel.mediumFaces
        
        code,message,data=api_model.get_geoFile(shape,medium,mediumFaces)
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"save geo error ",message)
            return
        api_writer.write_model_geo(fname,data[0],data[1])
        pass
    def projectSaveAntenna(self):
        '''
        拷贝天线数据到工程目录下
        (1)发射天线-陈列排布数据
        (2)发射天线-方向图数据
        '''

        return
        try:
            antenna_t=self._antenna_t
            if(antenna_t.file_array!=None 
               and antenna_t.antennaType==Antenna.mode_array 
               and os.path.exists(antenna_t.file_array)):
                antenna_t.file_array=self.copy2Project(antenna_t.file_array,
                                                        self.currentProject.getAntennaPath())
               
            if(antenna_t.file_antenna!=None and os.path.exists(antenna_t.file_antenna)):
                antenna_t.file_antenna=self.copy2Project(antenna_t.file_antenna,
                                                        self.currentProject.getAntennaPath())
            self._antenna_t=antenna_t

            antenna_r=self._antenna_r
            if(antenna_r.file_array!=None 
               and antenna_r.antennaType==Antenna.mode_array 
               and os.path.exists(antenna_r.file_array)):
                antenna_r.file_array=self.copy2Project(antenna_r.file_array,
                                                        self.currentProject.getAntennaPath())
                
            if(antenna_r.file_antenna!=None and os.path.exists(antenna_r.file_antenna)):
                antenna_r.file_antenna=self.copy2Project(antenna_r.file_antenna,
                                                            self.currentProject.getAntennaPath())
            self._antenna_r=antenna_r
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"保存天线","保存天线数据错误."+str(e))
            self._cLogger.debug("保存天线数据错误."+str(e),exc_info=True)

        pass

 
    
    def dumpProject(self,fname):
        pObj=Project()
        #清除对象前。，需要先删除模型中的显示，主要指的是阵列显示

 
        
        pObj.mpiNum=self.currentProject.mpiNum
        
        pObj.fpath=self.currentProject.fpath
        pObj.name=self.currentProject.name

        pObj.currentModel=self.currentModel
        pObj.currentMesh=self.currentMesh
        
        pObj.mediaList=self._mediaList
        pObj.media_used=self._media_used
        pObj.modelColor=self._modelColor
        pObj.pf=self._pf
        pObj.requestParam.reqTime=self.reqTimeRoot.data(0,RequestParam.objIndex)
        pObj.requestParam.reqDomain=self.reqDomainRoot.data(0,RequestParam.objIndex)
        pObj.requestParam.reqTemperature=self.reqThermalRoot.data(0,RequestParam.objIndex)
        pObj.nfList.append(self.reqNFRoot.data(0,NF.objIndex))
        pObj.ffrList.append(self.reqFFRRoot.data(0,FFR.objIndex))
        pObj.exeName=self.currentProject.exeName
        pObj.pfName=self.currentProject.pfName
        
        
        if(self.modelRoot!=None and self.modelRoot.childCount()>0):
            for i in range(self.modelRoot.childCount()):
                item=self.modelRoot.child(i)
                modelObj:Model=item.data(0,Model.objIndex)
                
                pObj.modeList.append((item.text(0),modelObj))

        # if(self.nfRoot!=None and self.nfRoot.childCount()>0):
        #     for i in range(self.nfRoot.childCount()):
        #         item=self.nfRoot.child(i)
        #         nf:NF=item.data(0,NF.objIndex)
        #         nf.title=item.text(0)
        #         pObj.nfList.append((item.text(0),nf))
  
        if(pObj.currentModel!=None):
            pObj.currentModel.dumpClear()
        for obj in pObj.modeList:
            if(obj[1]!=None):
                obj[1].dumpClear()
        api_project.dumpData(fname,pObj)
        pass
    

    def loadProject(self,fname:str=None):
        '''
        打开工程文件，首先需要将project中的原路径更新为新的路径，为避免工程文件迁移至其他电脑后绝对路径错误的问题
        '''
        try:
            if(fname is None):
                fname,_ = QtWidgets.QFileDialog.getOpenFileName(filter=Project.EXTENSIONS)
            if(fname=="" or fname is None):
                return
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"加载工程","工程文件不存在:"+fname)
                return
            
            self.isLoading=True
            fpath=os.path.dirname(fname)
        

            pObj:Project=api_project.loadData(fname)
            
        
            pObj.fpath=fpath
            self.currentProject=pObj
            self.currentMesh=pObj.currentMesh
            if(not hasattr(self.currentMesh,"localSize") or self.currentMesh.localSize==None):
                self.currentMesh.localSize={}
            if(not hasattr(self.currentMesh,"options")):
                self.currentMesh.options=Mesh().options
            self.currentModel=pObj.currentModel

            self._mediaList=pObj.mediaList
    
            self._modelColor=pObj.modelColor
       
            self._media_used=pObj.media_used
            self._pf:PF=pObj.pf
         
            # pObj.mpiNum=2
            if(self.currentModel!=None):
                self.currentModel.fileName=self.get_fname_new(pObj.currentModel.fileName,
                                                            self.currentProject.getModelPath())
                self.currentModel.geoFile=self.get_fname_new(pObj.currentModel.geoFile,
                                                            self.currentProject.getModelPath())
            if(self.currentMesh!=None):
                self.currentMesh.fileName=self.get_fname_new(pObj.currentMesh.fileName,
                                                            self.currentProject.getModelPath())
            
         
            
            self.sig_createProject(pObj.name)
            if(self._pf.em.used):
                self.nodeAction_AddEM()
                self.initFaces_pec()
            if(self._pf.circuit.used):
                self.nodeAction_AddCircuit()
                self.initFaces_circuit_source()
                self.initFaces_circle_load()
            if(self._pf.thermal.used):
                self.nodeAction_AddThermal()
                self.initFaces_thermal_dirichlet()
                self.initFaces_thermal_convection()
                self.initFaces_thermal_radiation()
                self.initSolids_thermal_source()
            if(self._pf.struct.used):
                self.nodeAction_AddStruct()
                self.initFaces_struct_dirichlet()
                self.initFaces_struct_force()
            self.reqTimeRoot.setData(0,RequestParam.objIndex,pObj.requestParam.reqTime)
            self.reqDomainRoot.setData(0,RequestParam.objIndex,pObj.requestParam.reqDomain)
            self.reqThermalRoot.setData(0,RequestParam.objIndex,pObj.requestParam.reqTemperature)
            self.reqNFRoot.setData(0,NF.objIndex,pObj.nfList[0])
            self.reqFFRRoot.setData(0,FFR.objIndex,pObj.ffrList[0])
            QtWidgets.QApplication.processEvents()
   
          
            
            if(pObj.modeList!=None and len(pObj.modeList)>0):
                for item in pObj.modeList:
                    self.sig_AddModel(item[1])
                    pass
                #model节点加载
                pass
            # if(pObj.meshList!=None and len(pObj.meshList)>0):
            #     for item in pObj.meshList:
            #         self.sig_AddMeshItem(item[1])
            #     #mesh节点加载
            #     pass

            if(pObj.currentModel!=None):
                self._logger.info("加载模型:{0}...".format(pObj.currentModel.fileName))
                self.console.print_text(" ")
                QtWidgets.QApplication.processEvents()
                fname,shape,shapeList,aisShapeList=api_model.openModelWithFile(pObj.currentModel.fileName,
                                                                                             self.modelViewer)
                self._logger.info("加载模型完成.")
                self.currentModel.shape=shape
                self.currentModel.shapeList=shapeList
                self.currentModel.aisShapeList=aisShapeList
                self.initSolids(len(shapeList))
                self.componentRoot.setExpanded(False)
                self._selectContext.initShape(shapeList,aisShapeList)
                self.sig_setModelColor(self._modelColor)
                pml=self.currentModel.pml
                exf=self.currentModel.exf
                # freq=("1e9",True)
                if(not hasattr(self.currentModel,"freq")):
                    self.currentModel.freq=("1e9",False)
                if(not hasattr(self.currentModel,"opacityMap")):
                    self.currentModel.opacityMap=0
                freq=self.currentModel.freq
                
                self.sig_modifyPML_EXF(pml,exf,freq)
                self.sig_pml_show(pml[2])
                self.sig_exf_show(exf[1])
                
                self._selectContext.setOpacity(self.currentModel.opacity)

            if(self.currentMesh!=None and self.currentMesh.fileName!=None):
                if(os.path.exists(self.currentMesh.fileName)):
                    actor=api_vtk.render_vtk_file(self.currentMesh.fileName)
                    self.currentMeshActor=actor
                    self._meshViewer.display_mesh(actor)
                pass
            self.init_medium_used()
            # self.nodeAction_InitResults()
            self.isLoading=False
            self.tree.setCurrentItem(self.root)
            self.root.setToolTip(0,"{0}/{1}.femx".format(pObj.fpath,pObj.name))
           
            self.sig_setModelColor(self._modelColor)

            self._is_saved=True
            if(hasattr(self.currentProject,"pfName")):
                self.sigPFName.emit(self.currentProject.pfName)
            # self.sigPickFace.emit()
            # print(pObj)
        except Exception as e:
            self.isLoading=False
            QtWidgets.QMessageBox.about(self,"加载工程","加载工程文件失败:"+str(e))
            self._cLogger.error("加载工程文件失败:"+str(e),exc_info=True)
            # return (-1,"加载工程文件失败:"+str(e))

        pass
    def init_medium_used(self):
        '''
        当前设置的材料结果
        '''
        #处理当前使用的材料列表
        #整体材料赋值为模型整体材料的名称
        #本体材料下的节点为单独设置了本体材料的面列表
        #涂覆材料下的节点为单独设置了涂覆材料的面列表
        if(self.currentModel==None):
            return
        mediumFaces=self.currentModel.mediumFaces
        mediumIndex=self.currentModel.medium

        self.node_clear(self.materialRoot)
        media_faces={}
        for k in mediumFaces:
            v:Isotropic=self._mediaList[mediumFaces[k]]
            if(v.name not in media_faces):
                media_faces[v.name]=[]
            media_faces[v.name].append(k)
        for m in media_faces:
            fList=media_faces[m]
            itemM=QTreeWidgetItem(self.materialRoot)
            itemM.setText(0,m)
            itemM.setIcon(0,treeIcons.materials)
            itemM.setExpanded(True)
            for f in fList:
                itemF = QTreeWidgetItem(itemM)
                itemF.setText(0, "Solid"+str(f+1))

        
        # mediumModel=None
        # if(mediumIndex>=0):
        #     mediumModel=self._mediaList[mediumIndex]
        # faceMediumDic={}#所有面的材料设置，key:faceId value:(mediumIndex,coatIndex,thickness)
        # faceNum=self.currentModel.faceNum
        
        # for i in range(faceNum):#初始化所有面的材料设置
        #     faceId=i+1
        #     faceMediumDic[faceId]=(mediumModel)
        #     if(mediumFaces.get(faceId)!=None):
        #         v=mediumFaces[faceId]
        #         mediumBase=mediumModel
        #         if(v>=0):
        #             mediumBase=self._mediaList[v]
               
        #         faceMediumDic[faceId]=(mediumBase)


        pass
    def init_media_used(self,mediaUsed:dict):
        '''
        初始化当前使用的材料列表，在media节点下管理
        '''
        self.node_clear(self.materialRoot)
        media_faces={}
        for k in mediaUsed:
            v:Isotropic=mediaUsed[k]
            if(v.name not in media_faces):
                media_faces[v.name]=[]
            media_faces[v.name].append(k)
        for m in media_faces:
            fList=media_faces[m]
            itemM=QTreeWidgetItem(self.materialRoot)
            itemM.setText(0,m)
            itemM.setIcon(0,treeIcons.materials)
            itemM.setExpanded(True)
            for f in fList:
                itemF = QTreeWidgetItem(itemM)
                itemF.setText(0, "Solid"+str(f))
        pass
    def nodeAction_MediaProperties(self):
        k,v=self.tree.currentItem().data(0,MediaItem.objIndex)
        # QtWidgets.QMessageBox.about(self,"材料属性",v.media.name)
        frm=frmMediaModify(self,(k,v))
        frm.sigMidiaModify.connect(self.sig_modifyMedia)
        frm.show()
        pass
    def sig_modifyMedia(self,mediaData):
        # print("projecttree",mediaData)
        # self._mediaList[mediaData[0]]=mediaData[1]
        # self.tree.currentItem().setData(0,MediaItem.objIndex,mediaData)
        pass
    def get_fname_new(self,srcFile,destPath):
        if(srcFile=="" or srcFile is None):
            return srcFile
        destFile= destPath+"/"+os.path.basename(srcFile)
        return destFile
    def nodeAction_SaveProject(self,tips:bool=True):

        try:
            base_path=self.currentProject.getSolverPath()
            api_writer.write_project_path(self._dir+"/dir.txt",base_path)

            projectName=self.root.text(0)
            fname=self.currentProject.fpath+"/"+projectName+".femx"

            if(self.currentProject.name!=projectName):
                #需要重新选择路径
                self.currentProject.fpath=""
            projectDir=self.currentProject.fpath
            if(projectDir==None or not os.path.exists(projectDir) or projectDir==self.currentProject.defaultPath):
                fname,_ = QtWidgets.QFileDialog.getSaveFileName(None,"保存工程", projectName ,filter=Project.EXTENSIONS)
                if fname == '':
                    return
                projectName=os.path.basename(fname).replace(".femx","")
                dir=os.path.dirname(fname)
                self.currentProject.name=projectName
                self.currentProject.fpath=dir
                self.root.setText(0,projectName)
                pass
            output_path=self.get_output_path()
            if(not os.path.exists(output_path)):
                os.makedirs(output_path)
            
            self.projectSaveParam() #求解设置参数
            self.projectSaveBound() #边界条件
            self.projectSaveMedia()
            self.projectSaveModel()
            # self.projectSaveGeo()
            # self.projectSaveAntenna()
            # self.nodeAction_InitResults()
            self.dumpProject(fname)
            self.root.setToolTip(0,fname)
            self._is_saved=True
            
            if(tips):
                QtWidgets.QMessageBox.about(self,"保存工程","保存工程成功             ")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"保存工程","保存工程失败"+str(e))
            self._cLogger.error("保存工程失败"+str(e),exc_info=True)
    
    def nodeAction_SaveProjectAs(self):
        try:
            projectName=self.root.text(0) 
            output_last=self.currentProject.getOutputPath() 
                #需要重新选择路径
            fname,_ = QtWidgets.QFileDialog.getSaveFileName(None,"保存工程", projectName ,filter=Project.EXTENSIONS)
            if fname == '':
                return
            projectName=os.path.basename(fname).replace(".femx","")
            dir=os.path.dirname(fname)
            self.currentProject.name=projectName
            self.currentProject.fpath=dir
            self.root.setText(0,projectName)
            
            # self.projectSaveParam() #包含了nf切片处理，需要先执行
            self.projectSaveMedia()
            self.projectSaveModel()
            # self.projectSaveGeo()
            # self.projectSaveAntenna()
            # self.nodeAction_InitResults()
            output_now=self.currentProject.getOutputPath()
            self.copyFolder(output_last,output_now)
            self.dumpProject(fname)
        
            QtWidgets.QMessageBox.about(self,"保存工程","保存工程成功             ")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"保存工程","保存工程失败"+str(e))
            self._cLogger.error("另存工程失败"+str(e),exc_info=True)
        pass
        
    '''
    模型节点操作
    '''
    def nodeAction_DisplayModel(self):
        '''
        双击模型节点，显示模型
        '''
        # self.currentShapeList=None
        self.sigClearInterContext.emit()
        if(self.currentModel!=None):
            aisShapes=self.currentModel.aisShapeList
            if(len(aisShapes)>0):
                api_model.removeShapes(self.modelViewer,aisShapes)
            if(self.currentModel.ais_shape_faceNormal!=None):
                api_model.removeShapes(self.modelViewer,[self.currentModel.ais_shape_faceNormal])
        modelObj:Model=self.tree.currentItem().data(0,Model.objIndex)
        fname,shape,shapeList,aisShapeList=api_model.openModelWithFile(modelObj.fileName,self.modelViewer)
        modelObj.shape=shape
        modelObj.shapeList=shapeList
        modelObj.aisShapeList=aisShapeList
        modelObj.faceNum=api_model.get_face_num(shape)
        self.currentModel=modelObj
        self.initFaces(modelObj.faceNum)
        self.sigActivateTab.emit(0)
        self.sigPickFace.emit()
        self.sig_setModelColor(self._modelColor)
        
        pass
    def setModelColor(self):
        '''
        设置模型颜色 正常颜色模式/法向颜色模式
        '''
        try:
            modelColor=copy.deepcopy(self._modelColor)
            frm_modelColor=frmModelColor(self,modelColor)
            frm_modelColor.show()
            frm_modelColor.move(self.parent.centralWidget().geometry().topLeft())
            frm_modelColor.sigSetModelColor.connect(self.sig_setModelColor)
            # color_back=[backgroundColor[0],backgroundColor[1],backgroundColor[2]]
            # self.modelViewer.set_bg_gradient_color(color_back, color_back)
            # api_model.refreshWithColor(self.modelViewer,self.aisShapes,modelColor)
        except Exception as e:
            self._logger.error(traceback.format_exc())
        pass
    def sig_setModelOpacity(self,opacity):
        if(self.currentModel==None):
            return
        self.currentModel.opacity=opacity
        self._selectContext.setOpacity(opacity)
        pass
    def sig_setActorOpacity(self,opacity):
        # if(self.currentMeshActor==None):
        #     return
        # self.currentMeshActor.GetProperty().SetOpacity(opacity)
        # self._meshViewer.render()
        self.currentModel.opacityMap=opacity
        api_vtk.set_opacity(self._actors_current,1-opacity)
        self._vtkViewer3d.render_manual()
        pass
    def sig_setOpacity(self,opacity,opacityMap):
        self.sig_setModelOpacity(opacity)
        self.sig_setActorOpacity(opacityMap)
    def setModelOpacity(self):
        try:
            opacity=self.currentModel.opacity
            opacityMap=self.currentModel.opacityMap
            frm_opacity=frmOpacity(self,opacity,opacityMap)
            frm_opacity.show()
            frm_opacity.move(self.topLeffPoint())
            frm_opacity.sigModify.connect(self.sig_setOpacity)
        except Exception as e:
            self._logger.error(traceback.format_exc())
        pass
    
    def sig_setModelColor(self,modelColor:ModelColor):
        # api_model.refreshWithColor(self.modelViewer,self.aisShapes,modelColor)
        self._modelColor=modelColor
        if(self.currentModel==None):
            return
        # api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList)
        
        if(hasattr(self.currentModel,"ais_shape_faceNormal") and self.currentModel.ais_shape_faceNormal!=None):
            api_model.removeShapes(self.modelViewer,[self.currentModel.ais_shape_faceNormal])
        # api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList)
        if(modelColor.colorType==ModelColor.MODE_MODEL):
            return
        

        ais_shape=api_model.display_face_color_normal(self.modelViewer, 
                                            self.currentModel.shape,
                                            modelColor.color_normal_outside,
                                            modelColor.color_normal_inside)
        self.currentModel.ais_shape_faceNormal=ais_shape
        
        pass
    def sig_AddModel(self,modelObj:Model):

        modelItem=QTreeWidgetItem(self.modelRoot)
        modelItem.setText(0, modelObj.title)
        modelItem.setIcon(0, treeIcons.gdtd_model_item)
        modelItem.setData(0,Model.objIndex,modelObj)
        modelItem.setData(0,self.actionIndex,self.actionsModelItem)
        self.tree.setCurrentItem(modelItem)
        
    def nodeAction_extendImportModel(self):
        '''
        vtk导入模型文件，作为背景，重复导入时，会覆盖前面导入的模型
        '''
        fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=Model.extPostExtension)
        if fname != '':
            actor=api_vtk.stl_model(fname)
            self._vtkViewer3d.display_model(actor)
            QtWidgets.QMessageBox.about(self, "Import", "模型导入成功      ")
            self.sigActivateTab.emit(2)
        pass
    def nodeAction_extendExportModel(self):
        '''
        暂不需要实现
        '''
        pass
    def nodeAction_extendImportNF(self):
        '''
        导入后处理数据文件，显示平面云图
        '''
        nfExtension="电磁环境数据(*.txt)"
        sbr_NFList:list=None
        fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=nfExtension)
        if fname is None or fname=="":
            return
        fname_base=os.path.basename(fname)
        dataRender,freqList=api_reader.read_nf_sbr_E(fname)
        self._postData_extend.nf_E.dataResults["Total"]=dataRender  
        self.node_clear(self.extendNFRoot)
        if(self.nfRoot!=None and self.nfRoot.childCount()>0):
            for i in range(self.nfRoot.childCount()):
                item=self.nfRoot.child(i)
                nf=item.data(0,NF.objIndex)
                nItem_extend=QTreeWidgetItem(self.extendNFRoot)
                nItem_extend.setText(0, fname_base+"/"+str(i+1))
                nItem_extend.setIcon(0, treeIcons.r_nf_item)
                nItem_extend.setData(0,NF.objIndex,nf)
      
        # self.nodeAction_DisplayNF_extend()
      
        pass
    def nodeAction_DisplayNF_extend(self,
                             isRefresh=False,
                             txChanged=False,
                             freqChanged=False,
                             vTypeChanged=False,
                             valueChanged=False,
                             surfaceChanged=False,
                             positionChanged=False,
                             xAxisChanged=False
                             ):
        try:
            self._is_extend=True
            nfItem=self.tree.currentItem()
            nfObj:NF=nfItem.data(0,NF.objIndex)
            if(nfObj.point_slice_start<0):#尚未完成切片处理
                self._cLogger.error("显示电磁环境nf数据切片未初始化")
                pass
            self.sigTxEnable.emit(False)
            self.sigActivateToolbar.emit(3)
            self._postFilter_extend.setFilterNF_E()
            self._postData_extend.setDataNF_E()
            self._postRender_extend.setRenderNF_E()

            freqIndex=self._postFilter_extend.freqIndex #频率编号
            vType=self._postFilter_extend.vTypeIndex #物理量类型
            xAxisIndex=self._postFilter_extend.xAxisIndex #x轴类型

            dataRender=self._postData_extend.nf_E.dataResults["Total"]
            postFilter=self._postFilter_extend
            filter_now=postFilter.filter_now

            db_convertKeys=self._postFilter_extend.filter_now.db_ConvertKeys
            checkedKeys=self._postFilter_extend.filter_now.checkedKeys
            checkedKeys_multi=self._postFilter_extend.filter_now.checkedKeys_multi

            header_dic=self._postFilter_extend.nf_E.headers
            header_title=self._postFilter_extend.nf_E.barKeys

            if(not isRefresh):#首次加载，并非过滤条件改变时加载
                vType=0
                self._postFilter_extend.vTypeIndex=0
                vTypeList=filter_now.vTypeList.copy()
                if(nfObj.pointType==1):
                    vTypeList=vTypeList[:1]
                self.sigVTypeList.emit(vTypeList)
                
                
                if(vType==0):
                    self.sigValueButtons.emit(checkedKeys_multi,False,db_convertKeys)
                    self.sigChooseSurface.emit([],False)
                    self.sigPosition.emit([])
    
                if(vType==1):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)

                if(vType==2):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)

            if(vTypeChanged):

                if(vType==0):
                    self.sigValueButtons.emit(checkedKeys_multi,False,db_convertKeys)
                    self.sigChooseSurface.emit([],False)
                    self.sigPosition.emit([])

                if(vType==1):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)
 
                if(vType==2):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)

            self.sigValueButton_convert_checked.emit(filter_now.db_Convert)

            if(vType==0):#表格数据
                self._postFilter_extend.filter_now.singleChecked=False
                dataItem=dataRender[freqIndex]

                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                dbConvert=filter_now.db_Convert#是否需要变换为db值
                v_convert_index_list=[]
                v_convert_header_list=[]
                if(dbConvert):
                    #先找到需要转换至的列索引
                    v_convert_index_list=[]
                    for k,v in filter_now.checkedKeys_multi.items():
                        if(v and k in filter_now.db_ConvertKeys):
                            v_convert_index_list.append(filter_now.valueKeys[k])
                            v_convert_header_list.append(k)
                         
                        
                    pass
                if(len(v_convert_index_list)>0):
                    dataItem_db=[]
                    for i in range(len(dataItem)):
                        dItem=dataItem[i]
                        temp_list = list(dItem)
                        for i in range(len(v_convert_index_list)):
                            v_temp=temp_list[v_convert_index_list[i]]
                            if(v_temp<=0):
                                temp_list[v_convert_index_list[i]]=filter_now.dbMin
                            else:
                                temp_list[v_convert_index_list[i]]=round(20*math.log10(v_temp),PostFilter.dotPrecision)
                        dataItem_db.append(tuple(temp_list))
                    # print(dataItem[0])
                    header_title=header_title.copy()
                
                    if(len(v_convert_header_list)>0):
                        for c_k in v_convert_header_list:  
                            
                            header_title[c_k]=header_title[c_k+PostFilter.dbTitle]
                  

                        pass

                    self.renderTable(header_dic,dataItem_db,header_title)

                else:
                    self.renderTable(header_dic,dataItem,header_title)
                self.sigActivateTab.emit(4)
            elif(vType==1):#曲线图数据
                self._postFilter_extend.filter_now.singleChecked=True
                self.sigActivateTab.emit(3)
                
                dataItem=dataRender[freqIndex]
                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                valueIndex=-1
                valueText=""
                barTitle=""
                dbConvert=filter_now.db_Convert#是否需要变换为db值
                
                
                for k,v in filter_now.checkedKeys.items():
                    if(v):
                        valueIndex=filter_now.valueKeys[k]
                        valueText=k
                        barTitle=valueText #默认的title与物理量一致
                        break
                if(valueText not in filter_now.db_ConvertKeys):    
                    dbConvert=False #当前物理量不需要转换为db值
                if(filter_now.barKeys.get(valueText)!=None):
                    barTitle=filter_now.barKeys[valueText]
                if(dbConvert):
                    barTitle=filter_now.barKeys[valueText+PostFilter.dbTitle]
                 #处理面，多个面时需要对数据进行切面处理
        
                surfaceList:list[str]=[]#面列表
                pointList=[]
                dataItem_result=dataItem

                #处理坐标数据，添加散列在最后，共计14列
                # 后三列的坐标数据主要用于构造平面使用，
                # 全局坐标系时，后三列与1/2/3相同，局部坐标系时，后三列为局部坐标系的坐标
                # 1/2/3分别为全局坐标系的坐标
                points_local=[]
                
                points_local=api_writer.get_nf_points(nfObj)
               

                # points_local=api_writer.get_nf_points(nfObj)
                for i in range(len(points_local)):
                    dItem=dataItem[i]
                    p_local=points_local[i]
                   
                    dItemN=list(dItem)
                    if(nfObj.axisType==0):
                        dItemN.append(dItem[1])
                        dItemN.append(dItem[2])
                        dItemN.append(dItem[3])
                    else:
                        dItemN.append(p_local[0])
                        dItemN.append(p_local[1])
                        dItemN.append(p_local[2])
                    dataItem[i]=tuple(dItemN)

                dimNum=0 #几个观察面，支持xy/xz/yz
                surfaceList=[]
                xAxis=None

                if(nfObj.uEnd!=nfObj.uStart):
                    dimNum=dimNum+1
                    xAxis=(0,"X/(m)") #x轴
                if(nfObj.vEnd!=nfObj.vStart):
                    dimNum=dimNum+1
                    xAxis=(1,"Y/(m)") #y轴
                if(nfObj.nEnd!=nfObj.nStart):
                    dimNum=dimNum+1
                    xAxis=(2,"Z/(m)") #z轴
                if(dimNum>=2):

                    if(nfObj.uEnd!=nfObj.uStart and nfObj.vEnd!=nfObj.vStart):
                        surfaceList.append("XY面")
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("XZ面")       
                    if(nfObj.vEnd!=nfObj.vStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("YZ面")
                    if(len(surfaceList)>0 and vTypeChanged):
                        #只有当首次时才发送信号 切换面和位置，不再发送信号
                        #切换物理量，也不再发送信号
                        #此时会重置面列表，因此surfaceIndex会与选中项不一致，需要将filter_now.surfaceIndex设置为0
                        
                        positionList=[]
                        self._postFilter_extend.filter_now.surfaceIndex=0
                        #获取z的值列表，需要去掉重复值
                        if(len(surfaceList)>1):
                            vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                            positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                        
                        self.sigChooseSurface.emit(surfaceList,True)
                        self.sigPosition.emit(positionList)
                        self._postFilter_extend.filter_now.surfaceList=surfaceList
                        self._postFilter_extend.filter_now.positionList=positionList
                        self._postFilter_extend.filter_now.surfaceIndex=0
                        self._postFilter_extend.filter_now.positionIndex=0

                    if(surfaceChanged):
                         positionList=[]
                        #  vIndex=3-self._postFilter.filter_now.surfaceIndex
                         vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                         positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                         self._postFilter_extend.filter_now.positionList=positionList
                         self._postFilter_extend.filter_now.positionIndex=0
                         self.sigPosition.emit(positionList)                                 
                if(dimNum==3):
                    #需要选择面
                    # self.sigSurface.emit(self._postFilter.filter_now.checkedSurfaces)  
                    #先只选择xy面并且只看第一个Z的值
                    threshold = 1e-7
                    # pValue=dataItem[0][3]
                    pValue=self._postFilter_extend.filter_now.positionList[self._postFilter_extend.filter_now.positionIndex]
                    # vIndex=3-self._postFilter.filter_now.surfaceIndex
                    vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                    dataItem_result=[x for x in dataItem if abs(x[vIndex]-pValue)<threshold]

                Lindex=[]
               
                if(dimNum==1):
                    xInddex=xAxis[0]+1
                    for item in dataItem_result:
                        v=item[valueIndex]
                        #显示db模式时，需要对数值进行转换
                        if(dbConvert):
                            
                            if(v<=0):
                                v=self._postFilter_extend.filter_now.dbMin
                            else:
                                v=20*math.log10(v)
                        pointList.append((item[xInddex],v))
                    self.renderChart(pointList,xAxis[1],barTitle)
                    return
                    pass
                elif(dimNum==2):
                    if(surfaceList[0]=="XY面"):
                        Lindex=[1,2]
                        Lindex=[11,12]
                        axisList=["X","Y"]
                    elif(surfaceList[0]=="XZ面"):
                        Lindex=[1,3]
                        Lindex=[11,13]
                        axisList=["X","Z"]
                    elif(surfaceList[0]=="YZ面"):
                        Lindex=[2,3]
                        Lindex=[12,13]
                        axisList=["Y","Z"]
                elif(dimNum==3):
                    if(self._postFilter_extend.filter_now.surfaceIndex==0):
                        Lindex=[1,2]
                        Lindex=[11,12]
                        axisList=["X","Y"]
                    elif(self._postFilter_extend.filter_now.surfaceIndex==1):
                        Lindex=[1,3]
                        Lindex=[11,13]
                        axisList=["X","Z"]
                    elif(self._postFilter_extend.filter_now.surfaceIndex==2):
                        Lindex=[2,3]
                        Lindex=[12,13]
                        axisList=["Y","Z"]

                

                for item in dataItem_result:
                    v1=item[Lindex[0]]
                    v2=item[Lindex[1]]
                    v=item[valueIndex]
                    if(dbConvert):
                        if(v<=0):
                            v=self._postFilter_extend.filter_now.dbMin
                        else:
                            v=20*math.log10(v)

                    pointList.append((v1,v2,v))
                if(xAxisIndex<0):
                    xAxisIndex=0
                
                self.renderChart_multi(pointList,axisList,xAxisIndex,barTitle)
    
                
            elif(vType==2):
                #云图显示 支持单面与多面，单面为xy面，yz面，xz面
                #多面时，需要处理数据和过滤项 过滤项有选择面，选择位置 
                #多面时，输入的数据项也需要单独处理，只输入当前面和选择了物理量的数据
                

                self._postFilter_extend.filter_now.singleChecked=True
                self.sigActivateTab.emit(2)
                dataItem=dataRender[freqIndex]
                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                valueIndex=-1
                valueText=""
                barTitle=""
                dbConvert=self._postFilter_extend.filter_now.db_Convert
                for k,v in self._postFilter_extend.filter_now.checkedKeys.items():
                    if(v):
                        valueIndex=self._postFilter_extend.filter_now.valueKeys[k]
                        valueText=k
                        barTitle=k
                        break  
                if(valueText not in self._postFilter_extend.filter_now.db_ConvertKeys):
                    dbConvert=False
                if(self._postFilter_extend.filter_now.barKeys.get(valueText)!=None):
                    barTitle=self._postFilter_extend.filter_now.barKeys[valueText]
                if(dbConvert):
                    barTitle=self._postFilter_extend.filter_now.barKeys[valueText+PostFilter.dbTitle]
                #处理面，多个面时需要对数据进行第二次切面处理

                surfaceList:list[str]=[]#面列表
               

                pointList=[]
                dataItem_result=dataItem
                points_local=api_writer.get_nf_points(nfObj)
                for i in range(len(points_local)):
                    dItem=dataItem[i]
                    p_local=points_local[i]
                    #处理坐标数据，添加散列在最后，共计14列
                    # 后三列的坐标数据主要用于构造平面使用，
                    # 全局坐标系时，后三列与1/2/3相同，局部坐标系时，后三列为局部坐标系的坐标
                    # 1/2/3分别为全局坐标系的坐标
                    dItemN=list(dItem)
                    if(nfObj.axisType==0):
                        dItemN.append(dItem[1])
                        dItemN.append(dItem[2])
                        dItemN.append(dItem[3])
                    else:
                        dItemN.append(p_local[0])
                        dItemN.append(p_local[1])
                        dItemN.append(p_local[2])
                    dataItem[i]=tuple(dItemN)
                    


                dimNum=0 #几个观察面，支持xy/xz/yz
                surfaceList=[]
                xAxis=None

                if(nfObj.uEnd!=nfObj.uStart):
                    dimNum=dimNum+1
                    xAxis=(0,"U Position") #x轴
                if(nfObj.vEnd!=nfObj.vStart):
                    dimNum=dimNum+1
                    xAxis=(1,"V Position") #y轴
                if(nfObj.nEnd!=nfObj.nStart):
                    dimNum=dimNum+1
                    xAxis=(2,"N Position") #z轴
                if(dimNum>=2):
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.vEnd!=nfObj.vStart):
                        surfaceList.append("XY面")
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("XZ面")       
                    if(nfObj.vEnd!=nfObj.vStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("YZ面")

                    if(len(surfaceList)>0 and vTypeChanged):

                        positionList=[]
                        self._postFilter_extend.filter_now.surfaceIndex=0
                        
                        if(len(surfaceList)>1):
                            vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                            positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                       
                        self.sigChooseSurface.emit(surfaceList,False)
                        self.sigPosition.emit(positionList)
                        self._postFilter_extend.filter_now.surfaceList=surfaceList
                        self._postFilter_extend.filter_now.positionList=positionList
                        self._postFilter_extend.filter_now.surfaceIndex=0
                        self._postFilter_extend.filter_now.positionIndex=0

                    if(surfaceChanged):
                         positionList=[]
                         vIndex=3-self._postFilter_extend.filter_now.surfaceIndex
                         vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                         #全局坐标系时从数据中筛选，局部坐标系时从局部坐标系中获取
              
                         positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                         

                         self._postFilter_extend.filter_now.positionList=positionList
                         self._postFilter_extend.filter_now.positionIndex=0
                         self.sigPosition.emit(positionList)                                 
                if(dimNum==3):
                    #需要选择面
                    # self.sigSurface.emit(self._postFilter.filter_now.checkedSurfaces)  
                    threshold = 1e-7
                    pValue=dataItem[0][3]   #先只选择xy面并且只看第一个Z的值
                    pValue=self._postFilter_extend.filter_now.positionList[self._postFilter_extend.filter_now.positionIndex]
                    vIndex=3-self._postFilter_extend.filter_now.surfaceIndex
                    vIndex=13-self._postFilter_extend.filter_now.surfaceIndex #添加了3列数据
                    dataItem_result=[x for x in dataItem if abs(x[vIndex]-pValue)<threshold]

                minV=1e9
                maxV=-1e9
                for item in dataItem_result:
                    v=item[valueIndex]
                    if(dbConvert):
                        if(v<=0):
                            v=self._postFilter_extend.filter_now.dbMin
                        else:
                            v=20*math.log10(v)
                    pointList.append((item[1],item[2],item[3],v,item[11],item[12],item[13]))
                    if(v<minV):
                        minV=v
                    if(v>maxV):
                        maxV=v
                
                
                modelActor=None
                arrayActor_t=None
                arrayActor_r=None
                if(vTypeChanged):#首次加载云图，默认type为0，因此加载云图时一定是发生了vTypeChanged
                    
                    if(not os.path.exists(self.currentModel.geoFile)):
                        api_model.exportModel(self.currentModel.shape,self.currentModel.geoFile)
                    modelActor=api_vtk.stl_model(fname=self.currentModel.geoFile,opacity=1)
                   
                    self._vtkViewer3d.clear()
                    self._vtkViewer3d.display_model(modelActor)
                self._vtkViewer3d.clear_actor_custom()

                nfActor=api_vtk.cloud_map_nf(pointList)
                barActor=api_vtk.scalar_actor(minV,maxV,barTitle)

                self._vtkViewer3d.display_actor(nfActor)
                self._vtkViewer3d.display_actor(barActor)
            
                if(self._antenna_r._show_array 
                   and os.path.exists(self._antenna_r.file_array_model
                    and  os.path.isfile(self._antenna_r.file_array_model))):
                    arrayActor_r=api_vtk.stl_model(self._antenna_r.file_array_model,1,color=(0.5,0.5,0))
                    self._vtkViewer3d.display_actor(arrayActor_r)
                if(self._antenna_t._show_array and os.path.exists(self._antenna_t.file_array_model) and os.path.isfile(self._antenna_t.file_array_model)):
                    arrayActor_t=api_vtk.stl_model(self._antenna_t.file_array_model,1,color=(0.5,0,0))
                    self._vtkViewer3d.display_actor(arrayActor_t)
                points_now=[tup[:4] for tup in pointList]
                #每个点*1000
                points_now=[(tup[0]*1000,tup[1]*1000,tup[2]*1000,tup[3]) for tup in points_now]
                self._postData_extend.data_now.points_now=points_now
                self._postData_extend.data_now.headers_now=["X(m)","Y(m)","Z(m)",barTitle]

                self._postRender_extend.render_now.actorMap=nfActor
                self._postRender_extend.render_now.actorBar=barActor
                self._postRender_extend.render_now.actorArray_TX=arrayActor_t
                self._postRender_extend.render_now.actorArray_RX=arrayActor_r
                self._postRender_extend.render_now.actorModel=modelActor

                self._postRender_extend.render_now.show_surface=True
                self._postRender_extend.render_now.show_points=False

                self._postRender_extend.render_now.minV=minV
                self._postRender_extend.render_now.maxV=maxV
                self._postRender_extend.render_now.min_now=minV
                self._postRender_extend.render_now.max_now=maxV

                
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"nf render","read the nf result error:"+str(e))
            traceback.print_exc()
        pass

        pass
    def nodeAction_DisplayEMI_extend(self,isRefresh=False,freqChanged=False,vTypeChanged=False,
                                     valueChanged=False,dbChanged=False):
        '''
        显示电磁干扰数据
        '''
        self.sigTxEnable.emit(False)
        self.sigActivateToolbar.emit(3)
        self._postFilter_extend.setFilterEmi()
        self._postData_extend.setDataEmi()
        self._postRender_extend.setRenderEmi()

        freqIndex=self._postFilter_extend.freqIndex #频率编号
        vType=self._postFilter_extend.vTypeIndex #物理量类型

        dataEMI=self._postData_extend.emi.dataResults["Total"]

        postFilter=self._postFilter_extend
        filter_now=postFilter.filter_now

        if not isRefresh:
            vType=0
            postFilter.vTypeIndex=0   
            self.sigVTypeList.emit(postFilter.filter_now.vTypeList)
            # self.sigChooseAxis.emit([])
            self.sigChooseSurface.emit([],False)
            self.sigPosition.emit([])
            if(vType==0):
                self.sigValueButtons.emit(filter_now.checkedKeys_multi,
                                          False,
                                          filter_now.db_ConvertKeys)
            if(vType==1):
                self.sigValueButtons.emit(filter_now.checkedKeys,
                                          True,
                                          filter_now.db_ConvertKeys)

        if vTypeChanged:
            if(vType==0):
                self.sigValueButtons.emit(filter_now.checkedKeys_multi,
                                          False,
                                          filter_now.db_ConvertKeys)
            if(vType==1):
                self.sigValueButtons.emit(filter_now.checkedKeys,
                                          True,
                                          filter_now.db_ConvertKeys)
            pass

        self.sigValueButton_convert_checked.emit(filter_now.db_Convert)#同步db按钮的状态

        dataItem=dataEMI[freqIndex]
        dbConvert=filter_now.db_Convert
        if(vType==0):
            header_title=filter_now.barKeys
            postFilter.filter_now.singleChecked=False
            #当为db时，需要转换数据，转换标题
            v_convert_index_list=[]
            v_convert_header_list=[]
            power_index=-1
            if(dbConvert):
                #先找到需要转换至的列索引
                v_convert_index_list=[]
                for k,v in filter_now.checkedKeys_multi.items():
                    if(v and k in filter_now.db_ConvertKeys):
                        v_convert_index_list.append(filter_now.valueKeys[k])
                        v_convert_header_list.append(k)
                        if(k==PostFilter.db_PowerKey):
                            power_index=filter_now.valueKeys[k]
                    
                    
                pass
            if(len(v_convert_index_list)>0):
                #功率的换算公式10*log10需要单独处理
                dataItem_db=[]
                for i in range(len(dataItem)):
                    dItem=dataItem[i]
                    temp_list = list(dItem)
                    for i in range(len(v_convert_index_list)):
                        v_temp=temp_list[v_convert_index_list[i]]
                        if(v_temp<=0):
                            temp_list[v_convert_index_list[i]]=self._postFilter.filter_now.dbMin
                        else:
                            if(v_convert_index_list[i]==power_index):
                                temp_list[v_convert_index_list[i]]=round(10*math.log10(v_temp),PostFilter.dotPrecision)
                            else:
                                temp_list[v_convert_index_list[i]]=round(20*math.log10(v_temp),PostFilter.dotPrecision)
                    dataItem_db.append(tuple(temp_list))
                # print(dataItem[0])
                header_title=header_title.copy()
            
                if(len(v_convert_header_list)>0):
                    for c_k in v_convert_header_list:  
                        header_title[c_k]=header_title[c_k+PostFilter.dbTitle]
                self.renderTable(filter_now.headers,dataItem_db,header_title)
                pass
            else:
                self.renderTable(filter_now.headers,dataItem,header_title)
            self.sigActivateTab.emit(4)
        elif(vType==1):
            postFilter.filter_now.singleChecked=True
            minV=1e9
            maxV=-1e9
            valueList=dataItem
            pointList=[]
            xNum=len(list(set(t[0] for t in self._antenna_r.itemList_local)))
            yNum=len(list(set(t[1] for t in self._antenna_r.itemList_local)))
            # xNum=9
            # yNum=4
            valueIndex=-1
            valueText=""
            barTitle=""
            for k,v in filter_now.checkedKeys.items():
                if(v):
                    valueIndex=filter_now.valueKeys[k]
                    valueText=k
                    barTitle=k
                    break
            if(valueText not in filter_now.db_ConvertKeys):
                dbConvert=False
            if(filter_now.barKeys.get(valueText)!=None):
                barTitle=filter_now.barKeys[valueText]
            if(dbConvert):
                barTitle=filter_now.barKeys[valueText+PostFilter.dbTitle]
            
            for item in valueList:
                v=item[valueIndex]
                if(dbConvert):
                    if(v<=0):
                        v=filter_now.dbMin
                    else:
                        if(valueText==PostFilter.db_PowerKey):
                            v=10*math.log10(v)
                        else:
                            v=20*math.log10(v)
                pointList.append((item[1],item[2],item[3],v))
                if(v<minV):
                    minV=v
                if(v>maxV):
                    maxV=v


            # mapActor=api_vtk.cloud_map(pointList,_xNum=xNum,_yNum=yNum)
            mapActor=api_vtk.cloud_map(pointList,_xNum=xNum,_yNum=yNum)
            modelActor=None
            arrayActor_r=None
            barActor=None
    
            
       
            
            
            if(not valueChanged and not dbChanged):
                #首次加载，不是切换按钮时，切换按钮时不重置相机
                
                if(not os.path.exists(self.currentModel.geoFile)):
                    api_model.exportModel(self.currentModel.shape,self.currentModel.geoFile)
                self._vtkViewer3d.clear()
                modelActor=api_vtk.stl_model(fname=self.currentModel.geoFile,opacity=1)
                # self._vtkViewer3d.display_model(modeActor)
                self._vtkViewer3d.display_actor(modelActor,False)
                self._vtkViewer3d.reset_camera()
            # self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            
            barActor=api_vtk.scalar_actor(minV,maxV,barTitle)
            self._vtkViewer3d.display_actor(mapActor)
            self._vtkViewer3d.display_actor(barActor)
            # self._vtkViewer3d.reset_camera()
            # if(self._antenna_r._show_array and os.path.exists(self._antenna_r.file_array_model)):
            #     arrayActor_r=api_vtk.stl_model(self._antenna_r.file_array_model)
            #     self._vtkViewer3d.display_actor(arrayActor_r)

            self.sigActivateTab.emit(2)
            points_now=[tup[:4] for tup in pointList]
            #每个点*1000
            points_now=[(tup[0]*1000,tup[1]*1000,tup[2]*1000,tup[3]) for tup in points_now]
            self._postData_extend.data_now.points_now=points_now
            self._postData_extend.data_now.headers_now=["X(m)","Y(m)","Z(m)",barTitle]

            self._postRender_extend.render_now.actorArray_RX=arrayActor_r
            self._postRender_extend.render_now.actorModel=modelActor
            self._postRender_extend.render_now.actorMap=mapActor
            self._postRender_extend.render_now.actorBar=barActor
            self._postRender_extend.render_now.show_surface=True
            self._postRender_extend.render_now.show_points=False

            self._postRender_extend.render_now.minV=minV
            self._postRender_extend.render_now.maxV=maxV
            self._postRender_extend.render_now.min_now=minV
            self._postRender_extend.render_now.max_now=maxV
            
            pass


    def nodeAction_extendImportEMI(self):
        '''
        导入后处理数据文件-电磁干扰
        '''
        self._is_extend=True
        emiExtension="电磁干扰(*.txt)"
        fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=emiExtension)
        if fname is None or fname=="":
            return
        dataRender,freqList=api_reader.read_nf_sbr_Power(fname)
        self._postData_extend.emi.dataResults["Total"]=dataRender
        self.node_clear(self.extendEMIRoot)

        nodeItem=QTreeWidgetItem(self.extendEMIRoot)
        nodeItem.setText(0,os.path.basename(fname))
        nodeItem.setIcon(0, treeIcons.emi)
        nodeItem.setData(0,256+1,dataRender)

        self.nodeAction_DisplayEMI_extend()


        
        pass
    # def sig_filterNFExtend(self,pointList,dIndex):
    #     #pointList,过滤后的数据，根据物理分量，面类别，频率过滤后的值
    #     # print("project.tree-filter",freq,plotType,valueType)

    #     v_min=min(pointList,key=lambda x:x[3])[3]
    #     v_max=max(pointList,key=lambda x:x[3])[3]
    #     xNum=len(list(set(t[0] for t in pointList)))
    #     yNum=len(list(set(t[1] for t in pointList)))
    #     zNum=len(list(set(t[2] for t in pointList)))

    #     dIndex=2
    #     if(xNum==1):
    #         dIndex=0
    #     if(yNum==1):
    #         dIndex=1
    #     if(zNum==1):
    #         dIndex=2
    
    #     self.resultsCurrentPointList=pointList
    #     actor=api_vtk.nf_surface(pointList,v_min,v_max,dIndex,xNum,yNum,zNum,64)
    #     barActor=api_vtk.scalar_actor(v_min,v_max,"Nearfield(V/m)")

    #     uValues=[t[0] for t in pointList]
    #     vValues=[t[1] for t in pointList]
    #     nValues=[t[2] for t in pointList]
    #     d_u=max(uValues)-min(uValues)
    #     d_v=max(vValues)-min(vValues)
    #     d_n=max(nValues)-min(nValues)
    #     d_max=max(d_u,d_v,d_n)*1.5

    #     self._vtkViewer3d.display_nf_ex(actor,True,barActor,d_max)
    #     self.sigActivateTab.emit(2)
    #     return
    #     v_min=min(pointList,key=lambda x:x[3])[3]
    #     v_max=max(pointList,key=lambda x:x[3])[3]
    #     xNum=len(list(set(t[0] for t in pointList)))
    #     yNum=len(list(set(t[1] for t in pointList)))
    #     zNum=len(list(set(t[2] for t in pointList)))

    #     self.resultsCurrentPointList=pointList
    #     actor=api_vtk.nf_surface(pointList,v_min,v_max,dIndex,xNum,yNum,zNum,12)
    #     barActor=api_vtk.scalar_actor(v_min,v_max,"Nearfield(V/m)")

    #     uValues=[t[0] for t in pointList]
    #     vValues=[t[1] for t in pointList]
    #     nValues=[t[2] for t in pointList]
    #     d_u=max(uValues)-min(uValues)
    #     d_v=max(vValues)-min(vValues)
    #     d_n=max(nValues)-min(nValues)
    #     d_max=max(d_u,d_v,d_n)*1.5

    #     self._vtkViewer3d.display_nf_ex(actor,True,barActor,d_max)
    #     self.sigActivateTab.emit(2)

    #     pass
    

    def nodeAction_ImportModel(self,reOpen:bool=False):
        

        EXTENSIONS = "STP files(*.stp , *.step);;*.iges, *.igs;;*.stl"
        curr_dir = Path('').abspath().dirname()
        fname = get_open_filename(EXTENSIONS, curr_dir)
        if fname == '':
            return
  


        self._logger.info("导入模型:{0}...".format(fname))
        self.console.print_text(" ")
        # self._logger.info("导入模型中...")
    
        QtWidgets.QApplication.processEvents()

        fname,shape,shapeList,aisShapeList= api_model.openModelWithFile(fname,self.modelViewer)

        self._logger.info("导入模型完成.")
        
        # fname,shape,shapeList,aisShapeList= api_model.openModel(self.modelViewer)
        # self.console.print_text("导入模型完成."+"\r\n")
        
    
        
        if(fname!="" and shape!=None):

            self.sigClearInterContext.emit()
            if(self.currentModel!=None):
                aisShapes=self.currentModel.aisShapeList
                if(len(aisShapes)>0):
                    api_model.removeShapes(self.modelViewer,aisShapes)
                if(self.currentModel.ais_shape_faceNormal!=None):
                    api_model.removeShapes(self.modelViewer,[self.currentModel.ais_shape_faceNormal])
            
            # api_mesh.mesh_generate(fname,"D:/mesh.stl",maxH=1000)
            modelObj=Model()
            fNameNoPath = os.path.basename(fname)
            fnameNoExtension=os.path.splitext(fNameNoPath)[0]
            dstPath=self.currentProject.getModelTempPath()
            if(self.currentProject.fpath!=None):
                dstPath=self.currentProject.getModelPath()
            dstFile=dstPath+"/"+fNameNoPath
            dstSTL=dstPath+"/"+fnameNoExtension+".vstl"
            code,message=api_model.exportModel(shape,dstSTL)#没有目录时会失败
            if(code!=1):
                self._cLogger.debug("保存vstl文件失败:{0}_{1}".format(dstSTL,message))
            if(fname!=dstFile):
                api_project.copyFile(fname,dstFile) #可以自行创建目录
            
            modelObj.fileName=dstFile
            modelObj.title=fNameNoPath
            modelObj.fileNameNoPath=fNameNoPath
            modelObj.name=fnameNoExtension
            modelObj.shape=shape
            modelObj.geoFile=dstSTL
            # modelObj.faceNum=api_model.get_face_num(shape)
            modelObj.shapeList=shapeList
            modelObj.aisShapeList=aisShapeList
            self.initSolids(len(shapeList))
            # self.initFaces(modelObj.faceNum)
            self._selectContext.setOpacity(modelObj.opacity)

            self.sig_AddModel(modelObj)
            self.sigActivateTab.emit(0)
            self.currentModel=modelObj
            if(not self._show_axis_global):
                api_model.show_axis_global(self.modelViewer,5)
                self._show_axis_global=True
            self.sigPickFace.emit()
            self._selectContext.initShape(shapeList,aisShapeList)
            self.sig_setModelColor(self._modelColor)
            self.modelViewer.FitAll()

        pass
    def setBodySelect(self,solidId,isSelected):
        if(isSelected):
            self._solidSelected_currentId=solidId
        else:
            self._solidSelected_currentId=-1
        pass
    def sig_modifyPML_EXF(self,pml:tuple,exf:tuple,freq:tuple):
        #生成完美匹配层和空气域
        if(len(pml)<4):
            pml=pml+(False,)
        if(len(exf)<3):
            exf=exf+(False,)
        if(len(pml)<5):
            pml=pml+(0.01,False)
        if(len(exf)<4):
            exf=exf+(0.01,False)
        self.currentModel.pml=pml

       
        self.currentModel.exf=exf
        self.currentModel.freq=freq
        
       
        # api_model.make_shell(self.modelViewer,self.currentModel.shape,pml[0]*1000,pml[1]*1000)
        #先删除之前的完美匹配层和空气域
        if(self.currentModel!=None):
            solid_index=len(self.currentModel.shapeList)
            for i in range(len(self.currentModel.shapeList_pml)+len(self.currentModel.shapeList_exf)):
                if(self.currentMesh.localSize.get(solid_index)!=None):
                    self.currentMesh.localSize.pop(solid_index)
                solid_index=solid_index+1
            api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList_exf)
            api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList_pml)
            
            
            self._selectContext.removeShapes_idList(self.currentModel.shapeIdList_pml)
            self._selectContext.removeShapes_idList(self.currentModel.shapeIdList_exf)
            self.currentModel.shapeList_pml.clear()
            self.currentModel.aisShapeList_pml.clear()
            self.currentModel.shapeList_exf.clear()
            self.currentModel.aisShapeList_exf.clear()
            self.currentModel.shapeIdList_pml.clear()
            self.currentModel.shapeIdList_exf.clear()
        #重新生成完美匹配层和空气域
        pml_used=pml[3]
        exf_used=exf[2]
        shapes_pml,ais_shapes_pml,shapes_exf,ais_shapes_exf,res_pml_param=api_model.make_shell_domains(self.modelViewer,
                                                          self.currentModel.shape,
                                                          pml[0]*1000,
                                                          pml[1]*1000,
                                                          exf[0]*1000,
                                                          pml_used,
                                                          exf_used)
        
        
        self.currentModel.shapeList_pml=shapes_pml
        self.currentModel.aisShapeList_pml=ais_shapes_pml
        self.currentModel.shapeIdList_pml= self._selectContext.addShapes(shapes_pml,ais_shapes_pml)
        self.currentModel.pml_param=res_pml_param
       
    
        self.currentModel.shapeList_exf=shapes_exf
        self.currentModel.aisShapeList_exf=ais_shapes_exf
        self.currentModel.shapeIdList_exf=self._selectContext.addShapes(shapes_exf,ais_shapes_exf)
      
        
        self._selectContext.setOpacity(self.currentModel.opacity)
        self.initSolids(len(self.currentModel.shapeList)+len(shapes_pml)+len(shapes_exf))
        solid_start_index=len(self.currentModel.shapeList)
        #先删除pml和exf的localSize
       
 
        if(len(shapes_pml)>0 and pml[5]):
            size_pml=pml[4]
            print("size_pml",size_pml)
            for shape in shapes_pml:
                self.currentMesh.localSize[solid_start_index]=size_pml
                solid_start_index=solid_start_index+1
            
            pass
        if(len(shapes_exf)>0 and exf[4]):
            size_exf=exf[3]
            print("size_exf",size_exf)
            for shape in shapes_exf:
                self.currentMesh.localSize[solid_start_index]=size_exf
                solid_start_index=solid_start_index+1
            pass
        self.sig_pml_show(pml[2],False)
        self.sig_exf_show(exf[1],False)
        self._selectContext.repaint()
        self.modelViewer.FitAll()
    def sig_pml_exf_closed(self):
        #当设置界面关闭时，隐藏完美匹配层和空气域
        # if(self.currentModel!=None):
        #     api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList_pml)
        #     api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList_exf)
        #     self._selectContext.removeShapes(self.currentModel.shapeList_pml,self.currentModel.aisShapeList_pml)
        #     self._selectContext.removeShapes(self.currentModel.shapeList_exf,self.currentModel.aisShapeList_exf)
        pass
    def sig_pml_show(self,visible,repaint=True):
        pml=self.currentModel.pml
        pml_new=pml[:2]+(visible,)+pml[3:]
        self.currentModel.pml=pml_new
        self._selectContext.showHide_idList(self.currentModel.shapeIdList_pml,visible)
        if(repaint):
            self._selectContext.repaint()
        pass
    def sig_exf_show(self,visible,repaint=True):
        exf=self.currentModel.exf
        exf_new=exf[:1]+(visible,)+exf[2:]
        self.currentModel.exf=exf_new
        self._selectContext.showHide_idList(self.currentModel.shapeIdList_exf,visible)
        if(repaint):
            self._selectContext.repaint()
        pass

    def nodeAction_PML_EXFSetting(self):
        '''
        完美匹配层与外推面设置
        '''
        pml=self.currentModel.pml
        exf=self.currentModel.exf
        freq=self.currentModel.freq
        frm=frmDomainPML(self,pml,exf,freq)
        frm.show()
        frm.sigModify.connect(self.sig_modifyPML_EXF)
        frm.sigClosed.connect(self.sig_pml_exf_closed)
        frm.sigShowPML.connect(self.sig_pml_show)
        frm.sigShowEXF.connect(self.sig_exf_show)
        frm.move(self.topLeffPoint())
        pass
    def showSolidAll(self):
        self._selectContext.showAll()
        if(self.currentModel!=None):
            pml=self.currentModel.pml
            exf=self.currentModel.exf
            self.sig_pml_show(pml[2],False)
            self.sig_exf_show(exf[1],False)
        self._selectContext.repaint()
        
    def showHideSolid(self):
        self._selectContext.showHide(self._solidSelected_currentId)
        # self._selectContext.showHide(0)
    def initSolids(self,solidNum:int):
        self.node_clear(self.componentRoot)
        if(solidNum<1): return
        for i in range(solidNum):
            #在modelRoot下添加节点
            shapeItem=QTreeWidgetItem(self.componentRoot)
            shapeItem.setText(0,"Solid{0}".format(i+1))
            shapeItem.setData(0,self.actionIndex,self.actionsSolidItem)
            shapeItem.setData(0,Model.objIndex,i)
            shapeItem.setIcon(0,treeIcons.gdtd_component_item)
        # self.componentRoot.setExpanded(False)
        pass
    def sig_apply_solid_mesh_size(self,solid,localSize,used):
        if(used):
            self.currentMesh.localSize[solid]=localSize
        else:
            if(self.currentMesh.localSize.get(solid)!=None):
                self.currentMesh.localSize.pop(solid)
        pass
    def set_solid_mesh_size(self):
        self.closeFormsOpened()
        sizeL=0.01
        used=False
        solidId=self.tree.currentItem().data(0,Model.objIndex)
       
        if(not hasattr(self.currentMesh,"localSize")):
            self.currentMesh.localSize={}
        size_dic=self.currentMesh.localSize
        if(size_dic.get(solidId)!=None):
            sizeL=size_dic[solidId]
            used=True
        frm=frmMeshSize(self,solidId,sizeL,used)
        frm.move(self.topLeffPoint())
        frm.show()
        frm.sigMeshLocalSize.connect(self.sig_apply_solid_mesh_size)
        self._forms.append(frm)
        
        pass
        
    def initFaces(self,faceNum:int):
        return
        self.node_clear(self.faceRoot)
        if(faceNum<1): return
        for i in range(faceNum):
            #在faceRoot下添加节点
            faceItem=QTreeWidgetItem(self.faceRoot)
            faceItem.setText(0,"Face{0}".format(i+1))
            faceItem.setData(0,self.actionIndex,self.actionsFaceItem)
            faceItem.setIcon(0,treeIcons.model_item)
        self.faceRoot.setExpanded(False)
        # self.initFaceToolTips()
            
    
    def nodeAction_ExportModel(self):
        if self.currentModel==None:
            QtWidgets.QMessageBox.about(self, "Model export", "请先导入或双击节点选中一个模型，当前模型为空")
            return
        fname,_ = QtWidgets.QFileDialog.getSaveFileName(filter=Model.exportExtension)

        if fname != '':
            code,message=api_model.exportModel(self.currentModel.shape,fname,True)
            QtWidgets.QMessageBox.about(self, "Model export", message)
            
        pass
    def nodeAction_RenameModel(self):
        self.nodeAction_Rename(self.tree.currentItem())

    def nodeAction_DeleteModel(self):
        '''
        删除模型节点
        '''
        currentItem=self.tree.currentItem()
        modelObj=currentItem.data(0,Model.objIndex)
        if(self.currentModel!=modelObj):#当前模型不是选中的模型
            modelObj=None
            self.modelRoot.removeChild(self.tree.currentItem())
            return

        
        if(self.currentModel!=None):
            api_model.removeShapes(self.modelViewer,self.currentModel.aisShapeList)
            if(self.currentModel.ais_shape_faceNormal!=None):
                api_model.removeShapes(self.modelViewer,[self.currentModel.ais_shape_faceNormal])
            
            self.currentModel.dumpClear()
            # api_model.clear_model(self.modelViewer)
     
        self.currentModel=None
        self.modelRoot.removeChild(self.tree.currentItem())
        # self.node_clear(self.faceRoot)
        pass
    def nodeAction_bodyClicked(self):
        solidId=self.tree.currentItem().data(0,Model.objIndex)
        self._selectContext.initSolidSelected(solidId)
        pass


    def nodeAction_MediaLibrary(self):
        # mList=self._mediaList
        isotropicList=self._mediaList
        frm=frmMediaLibraryN(self,isotropicList)
        frm.show()
        frm.sigApplyMedia.connect(self.sig_applyMedia)
        frm.sigClosed.connect(self.sig_mediaLibraryClosed)
        pass
    def sig_applyMedia(self,isotropicList:list):
        self._mediaList=isotropicList.copy()
        pass

    def sig_mediaLibraryClosed(self):
        mList=self._mediaList
        if(self._frm_model_media!=None):
            self._frm_model_media.refreshMedialList(mList)
        pass
    def sig_MediaSolidClicked(self,solidId):
        self._selectContext.initSolidSelected(solidId)
        # print("click face",faceId)
        pass
    def sig_applyMedium(self,mediumData:tuple):
        # print("apply medium",mediumData)
        if(self.currentModel!=None):
            self.currentModel.medium=mediumData[0]
            self.currentModel.mediumFaces=mediumData[1]
            self.init_medium_used()
        pass
    def sig_applyMedium_used(self,mediaUsed:dict):
        self._media_used=mediaUsed
        self.init_media_used(self._media_used)
        # print("projecttree",mediaUsed)
        pass
    # def sig_SelecteMediaFace(self,faceId):
    #     if(self._frm_model_media!=None):
    #         self._frm_model_media.selectFace(faceId+1)
    #     pass
    def nodeAction_ModelMediaSetting(self):
        '''
        为模型设置材料
        '''
        # faceNum=0
        # if(self.currentModel!=None):
        #     faceNum=self.currentModel.faceNum
        if(self._frm_model_media!=None):
            self._frm_model_media.deleteLater()

        medium=-1
        mediumFaces={}
        if(self.currentModel!=None):
            medium=self.currentModel.medium
            mediumFaces=self.currentModel.mediumFaces
           
        frm=frmModelMedia(self,self._mediaList,medium,mediumFaces)
        frm.show()
        frm.move(self.topLeffPoint())
        frm.sigMedialLibrary.connect(self.nodeAction_MediaLibrary)
        frm.sigSolidClicked.connect(self.sig_MediaSolidClicked)
        frm.sigMediumApply.connect(self.sig_applyMedium)
        self._selectContext.sigBodyClicked.connect(frm.selectSolid)
        # frm.sigMedium_used.connect(self.sig_applyMedium_used)
        self._frm_model_media=frm

        self.sigActivateTab.emit(0)
        self._selectContext.Action_select_body()

    '''
    发射天线节点操作
    '''
    def nodeAction_importArray(self):
        '''
        导入天线阵列文件，装配调整使用
        '''

        return
        antenna_current=self._antenna_c
        
        fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=Antenna.import_arrayExtension)
        if fname != '':

            rList=api_model.import_array(fname)
            # self._arrayItemList=rList
            antenna_current.itemList_local=rList
            antenna_current.file_array=fname
            antenna_current=self.antennaArrayRender(antenna_current)
            antenna_current.mode=Antenna.mode_array
            
            self.sigPickFace.emit()
            if(antenna_current._face_id>=0):
                self._selectContext.initFaceSelected(antenna_current._face_id)
            

            self._frm_arrangement.updateAntennaFile(fname,len(rList))

            self._antenna_c=antenna_current
            QtWidgets.QMessageBox.about(self, "Import", "阵列天线导入成功"+str(len(rList))+"个阵元")
        pass
    # def nodeAction_importPoints(self):
    #     antenna_current=self._antenna_c
    #     if(antenna_current.mode!=Antenna.mode_points):
    #         antenna_current.itemList_global=[]
    #     antenna_current.mode=Antenna.mode_points
        
        
    #     antenna_current.normal_dir=api_model.get_default_normal()
        
    #     # frm=frmAntennaPoints(self,antenna_current)
    #     # frm.show()
    #     self.antennaPointsRender(antenna_current)
    #     self._selectContext.initFaceSelected(antenna_current._face_id)

    #     # frm.sigPointsChanged.connect(self.sig_pointsChanged)
    #     self._antenna_c=antenna_current
    
    #     pass
    # def sig_pointsChanged(self,points,pixel):
    #     antenna_current=self._antenna_c
    #     # antenna_current.mode=Antenna.mode_points
    #     # antenna_current.normal_dir=api_model.get_default_normal()
    #     antenna_current.itemList_global=points
    #     antenna_current.display_size=pixel
    #     # self._frm_arrangement.updateAntennaFile(f"points:{len(points)}")
    #     self.antennaPointsRender(antenna_current)
    #     self._antenna_c=antenna_current

    def nodeAction_tx(self):
        self.tree.setCurrentItem(self.trasimitRoot)
        self.nodeAction_TransimitArrange()
    def nodeAction_rx(self):
        self.tree.setCurrentItem(self.receiveRoot)
        self.nodeAction_TransimitArrange()

    def nodeAction_TransimitArrange(self):
        '''
        发射天线阵列调整,接收阵列天线，使用同样的操作需要加入判断
        '''
        return
        
        if(self._frm_arrangement!=None):
            self._frm_arrangement.close()
            self._frm_arrangement=None
        # if(self._frm_antenna_set!=None):
        #     self._frm_antenna_set.close()
        #     self._frm_antenna_set=None
        if(self._frm_model_media!=None):
            self._frm_model_media.close()
            self._frm_model_media=None
        
        self._is_arrange=True
        currentItem=self.tree.currentItem()
    
        if(currentItem==self.trasimitRoot):
            self._antenna_c=self._antenna_t
        elif(currentItem==self.receiveRoot):
            self._antenna_c=self._antenna_r
 

        antenna_current=self._antenna_c

    
        faceNum=0
        if(self.currentModel!=None):
            faceNum=self.currentModel.faceNum
        frm=frmTX(self,antenna_current,faceNum)
        
        frm.move(self.parent.centralWidget().geometry().topLeft())
        frm.show()

        frm.sigTabActivated.connect(self.sig_antennaTabChanded)
        # return
        frm.sigOffset.connect(self.sig_applyOffset)
        frm.sigRotate.connect(self.sig_rotateByZ)
        frm.sigAxisChange.connect(self.sig_axisRefresh)
        frm.sigPixelChange.connect(self.sig_pixelRefresh)
        frm.sigDirChange.connect(self.sig_dirChange)
        frm.sigClosed.connect(self.sig_arrangeClosed)
        frm.sigImport.connect(self.nodeAction_importArray)
        # frm.sigPoints.connect(self.nodeAction_importPoints)
        # frm.sigPointsChanged.connect(self.sig_pointsChanged)
        frm.sigPointsApply.connect(self.sig_pointsApply)
        frm.sigShowAxis.connect(self.sig_axisShow)
        frm.sigFaceChanged.connect(self.sig_updateFace)

        frm.sigPower.connect(self.sig_powerSet)
        frm.sigShowArray.connect(self.sig_showArray)
        

        
        if(antenna_current.antennaType==Antenna.mode_array):
            self.antennaArrayRender(antenna_current)
            self.sigPickFace.emit()
        if(antenna_current.antennaType==Antenna.mode_points):
            self.antennaPointsRender(antenna_current)
            self._selectContext.Action_select_body()
        
        if(antenna_current._face_id>=0 and antenna_current.antennaType==Antenna.mode_array):
            self.axesRender(antenna_current.center,
                            antenna_current.normal_dir,
                            antenna_current.offset_rotate_z,
                            antenna_current.axis_length_array)
            self._selectContext.initFaceSelected(antenna_current._face_id)
       
        

        frm.sigRotate_radio.connect(self.sig_rotateRadio)
        frm.sigScale_radio.connect(self.sig_scaleRadio)
        frm.sigAxisChange_radio.connect(self.sig_axisRefresh_antenna)
        frm.sigImport_radio.connect(self.nodeAction_importRadio)
        frm.sigShowAxis_radio.connect(self.sig_axisShow_radio)
        frm.sigShowAntenna_radio.connect(self.sig_antennaShow_radio)
        frm.sigAntennaTypeApply.connect(self.sig_antennaTypeApply)

        antenna_current=self.antennaRadioRender(antenna_current)
        
        self._antenna_c=antenna_current
        self._frm_arrangement=frm
        self.sigActivateTab.emit(0)
        if(not antenna_current._show_array):
            self.sig_showArray(False)
        if(not antenna_current._show_axis_array):
            self.sig_axisShow(False)
        self.sigPickFace.emit()
        
        
        
        pass
    def sig_pointsApply(self,pointList,pixel,show):
        antenna_current=self._antenna_c
        antenna_current._show_array=show
        antenna_current.display_size=pixel
        antenna_current.itemList_discrete=pointList
        antenna_current.itemList_global= [(x * 1000, y * 1000,z*1000) for (x, y,z) in pointList]
        antenna_current.antennaType=Antenna.mode_points
        
        self.antennaPointsRender(antenna_current)
        pass
    def sig_antennaTypeApply(self,antennaType):
        self._antenna_c.antennaType=antennaType
    def sig_showArray(self,show):
        antenna_current=self._antenna_c
        antenna_current._show_array=show
        if(antenna_current.arrayShape_AIS!=None):#已经显示过阵列，需要先清除
            api_model.removeShapes(self.modelViewer,
                                   [antenna_current.arrayShape_AIS])
        if(antenna_current._actor_array!=None):
            self._meshViewer.remove_actor(antenna_current._actor_array)
            
        
        if(not show):
            return
        api_model.displayShapes(self.modelViewer,[antenna_current.arrayShape_AIS])
        self._meshViewer.display_actor(antenna_current._actor_array)

        pass
    def sig_powerSet(self,power):
        antenna_current=self._antenna_c
        antenna_current.power=power
        self._antenna_c=antenna_current

    def sig_arrangeClosed(self):
        self._is_arrange=False

    def sig_axisRefresh(self,axis_length):
        antenna_current=self._antenna_c
        if(antenna_current._face_id<0):#尚未选中面，不需要处理局部坐标系旋转和显示
            return
        self.axesRender(antenna_current.center,
                        antenna_current.normal_dir
                        ,antenna_current.offset_rotate_z,
                        axis_length)
        # print("sigAxisCahnge",axis_length)
        antenna_current.axis_length_array=axis_length
        self._antenna_c=antenna_current
        pass
    def sig_axisShow(self,show):
        '''
        显示局部坐标系
        '''
        if(self._local_trihedron!=None):
            if(show):
                api_model.display_local_trihedron(self.modelViewer,self._local_trihedron)
            else:
                api_model.hide_local_trihedron(self.modelViewer,self._local_trihedron)
        self._antenna_c._show_axis_array=show
        pass
    def sig_pixelRefresh(self,pixel):
        # print("sigPixelChange",pixel)
        antenna_current=self._antenna_c
        antenna_current.display_size=pixel
        if(antenna_current.antennaType==Antenna.mode_array):
            antenna_current=self.antennaArrayRender(antenna_current)
        else:
            self.antennaPointsRender(antenna_current)

        self._antenna_c=antenna_current
        pass
    def sig_dirChange(self,dir,reverse=False):
        antenna_current=self._antenna_c
        antenna_current.normal_dir=dir
        antenna_current.reverseN=reverse

        self.axesRender(antenna_current.center,
                        dir,
                        antenna_current.offset_rotate_z,
                        antenna_current.axis_length_array)
        antenna_current=self.antennaArrayRender(antenna_current)
        
        self._antenna_c=antenna_current
        # print("sigDirChange",dir)
        pass
    def sig_antennaTabChanded(self,index):
        if(index==0 or index==1 or index==2):
            self.sigActivateTab.emit(0)
        elif(index==3):
            self.sigActivateTab.emit(1)
        pass
    def sig_rotateByZ(self,angel):
        antenna_current=self._antenna_c

        antenna_current.offset_rotate_z=angel
        if(antenna_current._face_id<0):#尚未选中面，不需要处理局部坐标系旋转和显示
            return
        self.axesRender(antenna_current.center,
                        antenna_current.normal_dir,
                        angel,
                        antenna_current.axis_length_array)
        antenna_current=self.antennaArrayRender(antenna_current)
        
        
        self._antenna_c=antenna_current
    
        pass
    def sig_applyOffset(self,distance_offset):
        # print("sigApplyOffset",distance_offset)
        antenna_current=self._antenna_c
        antenna_current.offset_x=distance_offset[0]
        antenna_current.offset_y=distance_offset[1]
        antenna_current.offset_z=distance_offset[2]

        antenna_current=self.antennaArrayRender(antenna_current)

        self._antenna_c=antenna_current
        return


        pass
    def axesRender(self,center,normal_dir,offset_rotate_z,axis_length):
        trihedon_current=self._local_trihedron

        if(trihedon_current!=None):
            api_model.hide_local_trihedron(self.modelViewer,trihedon_current)
        trihedon_new=api_model.get_local_trihedron(center,normal_dir,offset_rotate_z,axis_length)
        api_model.display_local_trihedron(self.modelViewer,trihedon_new)
        self._local_trihedron=trihedon_new


        pass
    def action_showArray(self,antennaObj:Antenna):
        '''
        显示天线阵列
        '''
        antenna_current=antennaObj

        # antenna_current._show_array=not antenna_current._show_array
        if(antenna_current.arrayShape_AIS!=None):#已经显示过阵列，需要先清除
            api_model.removeShapes(self.modelViewer,
                                   [antenna_current.arrayShape_AIS])
        if(antenna_current._actor_array!=None):
            self._meshViewer.remove_actor(antenna_current._actor_array)
            
        
        if(not antenna_current._show_array):
            return
        api_model.displayShapes(self.modelViewer,[antenna_current.arrayShape_AIS])
        self._meshViewer.display_actor(antenna_current._actor_array)
        pass
    def nodeAction_showArray(self):
        '''
        显示天线阵列
        '''
        item=self.tree.currentItem()
        if(item==self.t_arrangeRoot):
            self.action_showArray(self._antenna_t)
        elif(item==self.r_arrangeRoot):
            self.action_showArray(self._antenna_r)
    

        pass

    def antennaPointsRender(self,antenaObj:Antenna):
        '''
        渲染天线阵元，直接使用全局坐标
        '''
        antenna_current=antenaObj
        trihedon_current=self._local_trihedron
        if(antenna_current==None):
            return None
        if(antenna_current.itemList_global==None or len(antenna_current.itemList_global)<1):#尚未导入阵列数据
            return antenna_current
        if(antenna_current.arrayShape_AIS!=None):#已经显示过阵列，需要先清除
            api_model.removeShapes(self.modelViewer,
                                   [antenna_current.arrayShape_AIS])
            
        if(not antenna_current._show_array):
            return antenna_current
            
        
        shape,ais_shape=api_model.display_antenna(self.modelViewer,
                                                  antenna_current.normal_dir,
                                                  antenna_current.itemList_global,
                                                  antenna_current.display_size)
        

        if(trihedon_current!=None):
            api_model.hide_local_trihedron(self.modelViewer,trihedon_current)
        
        
        array_model="points.vstl"
        arrayModelFile=self.currentProject.getModelPath()+"/"+array_model
        api_model.exportModel(shape,arrayModelFile)

        antenna_current.file_array_model=arrayModelFile

        antenna_current.arrayShape=shape
        antenna_current.arrayShape_AIS=ais_shape
        return antenna_current
        
    def antennaArrayRender(self,antennaObj:Antenna):
        '''渲染阵列天线
        需要考虑 位移、法线、旋转三个因素
        '''
        antenna_current=antennaObj

        if(antenna_current==None):
            return None
        if(antenna_current.itemList_local==None or len(antenna_current.itemList_local)<1):#尚未导入阵列数据
            return antenna_current
        distance_offset=(antenna_current.offset_x,antenna_current.offset_y,antenna_current.offset_z)
        
        if(antenna_current.arrayShape_AIS!=None):#已经显示过阵列，需要先清除
            api_model.removeShapes(self.modelViewer,
                                   [antenna_current.arrayShape_AIS])
        rListN=api_model.offset_antenna(antenna_current.itemList_local,
                                        distance_offset)
        gList=api_model.local_global(antenna_current.center,
                                     antenna_current.normal_dir,
                                     antenna_current.offset_rotate_z,
                                     rListN)
        shape,ais_shape=api_model.display_antenna(self.modelViewer,
                                                  antenna_current.normal_dir,
                                                  gList,
                                                  antenna_current.display_size)
        #将天线文件导出为模型文件stl格式，用于后续处理在vtk中显示
        array_model=os.path.splitext(os.path.basename(antenna_current.file_array))[0]+".vstl"
        arrayModelFile=self.currentProject.getModelPath()+"/"+array_model
        api_model.exportModel(shape,arrayModelFile)

        antenna_current.file_array_model=arrayModelFile

        antenna_current.arrayShape=shape
        antenna_current.arrayShape_AIS=ais_shape
        antenna_current.itemList_global=gList
        return antenna_current
            
        pass
    def nodeAction_faceClicked(self):
   
        currentItem=self.tree.currentItem()
        currentText=currentItem.text(0)
        if(currentText.startswith("Face")):

            if(currentItem.parent()==self.pfBoundCircuitSourceRoot):
                data=currentItem.data(0,PF.objIndex)
                faceId=data[0]
                self._selectContext.initFaceSelected(faceId)
                pass
            else:
                try:
                    faceId=int(currentText.replace("Face",""))-1
                    self._selectContext.initFaceSelected(faceId)
                except Exception as e:
                    print("face clicked error",e)
                    traceback.print_exc()
                    return
            
            # self.sig_SelecteMediaFace(faceId)
            # self.setFaceSelect(faceId,True)
    def sig_selectFaceMaual(self,faceId=-1):
        self._selectContext.initFaceSelected(faceId)
    def sig_selectSolidMaual(self,solidId=-1):
        self._selectContext.initSolidSelected(solidId)
    def sig_clearFaceSelected(self):
        self._selectContext.clearFaceSelected()
    def sig_clearSolidSelected(self):
        self._selectContext.clearSolidSelected()
    def nodeAction_solidClicked(self):
        currentItem=self.tree.currentItem()
        currentText=currentItem.text(0)
        if(currentText.startswith("Solid")):
            solidId=int(currentText.replace("Solid",""))-1
            self._selectContext.initSolidSelected(solidId)
        
    def sig_updateFace(self,faceId):
        '''
        更新选中面，下拉列表更新
        '''
        dotNum=2
        self._selectContext.initFaceSelected(faceId)
        
        face=self._selectContext.get_face_selected(faceId)
        face_center=self._selectContext.get_face_center(face)


        face_dir,_=self._selectContext.get_face_dir(face)
        
        center=(round(face_center.X(),dotNum),round(face_center.Y(),dotNum),round(face_center.Z(),dotNum))
        normal_dir=(round(face_dir.X(),2),round(face_dir.Y(),2),round(face_dir.Z(),2))
        self.sig_chooseFace(center,normal_dir,faceId)

        #重新渲染方向图
        # self.antennaRadioRender(self._antenna_c)
        self.antennaRadioRefresh(self._antenna_c)

        pass
    def sig_chooseFace(self,center:tuple,normal_dir:tuple,faceId):
        dotNum=2
        # print("projectTree choose face",center,gpDir,str(center))
        '''
        当faceId<0时，表示取消选中面
        '''
        if( not self._is_arrange):#非阵列调整状态，直接返回
            return
        antenna_current=self._antenna_c
        # print("arrange.chooseFace",antenna_current.name)

        trihedon_current=self._local_trihedron
        # distance_offset=(antenna_current.offset_x,antenna_current.offset_y,antenna_current.offset_z)
        antenna_current.center=center
        antenna_current.normal_dir=normal_dir
        antenna_current._face_id=faceId
        a_x,a_y,a_z=api_model.get_angel_xyz(center,normal_dir)
        antenna_current.angel_xy=a_x
        antenna_current.angel_yz=a_y
        antenna_current.angel_xz=a_z

        # self._antenna_t=antenna_current
   
        
        
        if(antenna_current.arrayShape_AIS!=None):#已经显示过阵列，需要先清除
            api_model.removeShapes(self.modelViewer,
                                   [antenna_current.arrayShape_AIS])
        if(trihedon_current!=None):#已经显示过局部坐标系，需要先清除
            api_model.hide_local_trihedron(self.modelViewer,
                                           trihedon_current)
        # api_model.clear_model(self.modelViewer)

        if(faceId<0):#取消选中面，直接返回
            return

        self.axesRender(center,
                        normal_dir,
                        antenna_current.offset_rotate_z,
                        antenna_current.axis_length_array)
        # rListN=api_model.offset_antenna(antenna_current.itemList_local,
        #                                 distance_offset)
        # gList=api_model.local_global(antenna_current.center,
        #                              antenna_current.normal_dir,
        #                              rListN)
        # shape,ais_shape=api_model.display_antenna(self.modelViewer,
        #                                           antenna_current.normal_dir,
        #                                           gList,
        #                                           antenna_current.display_size)

        # shape,ais_shape,gList=api_model.dislay_array(self.modelViewer,
        #                                              center,
        #                                              normal_dir,
        #                                              antenna_current.offset_rotate_z,
        #                                              antenna_current.itemList_local)
        # antenna_current.arrayShape=shape
        # antenna_current.arrayShape_AIS=ais_shape
        # antenna_current.itemList_global=gList
        if(len(antenna_current.itemList_local)>0):#尚未导入阵列数据
            antenna_current=self.antennaArrayRender(antenna_current)

        self._antenna_c=antenna_current

        if(self._frm_arrangement!=None):
            self._frm_arrangement.sig_updateChoose(center,normal_dir,faceId)
        
        pass
    def nodeAction_showAntenna(self):
        '''
        显示天线
        '''
        item=self.tree.currentItem()
        if(item==self.t_radioRoot):
            self.action_showAntenna(self._antenna_t)
        elif(item==self.r_radioRoot):
            self.action_showAntenna(self._antenna_r)
        pass
    def action_showAntenna(self,antennaObj:Antenna):
        '''
        显示天线
        '''
        antenna_current=antennaObj
        # if(not hasattr(antenna_current,"_show_antenna")):
        #     antenna_current._show_antenna=True
        # antenna_current._show_antenna=not antenna_current._show_antenna
    

        
        if(antenna_current._actor_antenna!=None):
            #先删除天线方向图
            self._meshViewer.remove_actor(antenna_current._actor_antenna)
            pass
        if(not antenna_current._show_antenna):
            return
        self._meshViewer.display_actor(antenna_current._actor_antenna)

        pass
    def antennaRadioRefresh(self,antennaObj:Antenna):
        '''刷新天线方向图
        
        '''
        self._last_rotate=None
        antenna_current=antennaObj
        
        actor_bar=antenna_current._actor_bar
        actor_antenna=antenna_current._actor_antenna
        actor_array=antenna_current._actor_array
        actor_model=antenna_current._actor_model

        if(actor_bar is None or actor_antenna is None or actor_array is None or actor_model is None):
            return
        start_point=(0,0,0)
        if(antenna_current.itemList_global!=None and len(antenna_current.itemList_global)>0):
            start_point=antenna_current.itemList_global[0]
        self._meshViewer.display_nfr(actor_antenna,actor_bar,start_point)
        # self._meshViewer.display_array(actor_array)
        self._meshViewer.display_model(actor_model)
        arrayFile=antenna_current.file_array_model
        if(antenna_current.file_array!=None and  os.path.exists(arrayFile)):
            # arrayFile=antenna_current.file_array
            #显示天线阵列
            arrayActor=api_vtk.stl_model(arrayFile)
            arrayActor.GetProperty().SetColor(0.9, 0.5, 0.5)
            self._meshViewer.display_array(arrayActor)
            antenna_current._actor_array=arrayActor
        self.sig_rotateRadio((antenna_current.rotate_x,
                                    antenna_current.rotate_y,
                                    antenna_current.rotate_z))
        self.sig_axisRefresh_antenna(antenna_current.axis_length_antenna,antenna_current.axis_thickness_antenna)
    
        


        pass
    def antennaRadioRender(self,antenaObj:Antenna):
        '''渲染天线方向图
        
        '''
        # self._delayTimer.stop()
        self._last_rotate=None#重新定义旋转
        antenna_current=antenaObj
        dataObj=antenna_current.nfr_data

        pointList=dataObj[0]
        min=dataObj[1]
        max=dataObj[2]
        thetaNum=dataObj[3]
        phiNum=dataObj[4]
        self.resultsCurrentPointList=pointList
        self._meshViewer.clear()
        # self._meshViewer.reset()
        

            # self._vtkViewer3d.display_nfr(actor,barActor,start_point)

        if(pointList!=None and len(pointList)>0 and antenna_current._show_antenna):#有数据可以渲染
            try:
                # scale=antenna_current.radio_scale
                # pn_list=[]
                # for p in pointList:
                #     p0=p[0]*scale
                #     p1=p[1]*scale
                #     p2=p[2]*scale
                #     pn_list.append((p0,p1,p2,p[3]))

                actor=api_vtk.antenna_radio_pattern(pointList,min,max,thetaNum,phiNum)
                actor.SetScale(antenna_current.radio_scale)
                
                start_point=(0,0,0)
                if(antenna_current.itemList_global!=None and len(antenna_current.itemList_global)>0):
                    start_point=antenna_current.itemList_global[0]

                barActor=api_vtk.scalar_actor(min,max,"Radiation")
                self._meshViewer.display_nfr(actor,barActor,start_point)
                antenna_current._actor_bar=barActor
                antenna_current._actor_antenna=actor
            except Exception as e:
                self._logger.error(traceback.format_exc())
        arrayFile=antenna_current.file_array_model
        
        if(antenna_current.file_array!=None and  os.path.exists(arrayFile)):
            # arrayFile=antenna_current.file_array
            #显示天线阵列
            arrayActor=api_vtk.stl_model(arrayFile,1)
            arrayActor.GetProperty().SetColor(0.9, 0.5, 0.5)
            self._meshViewer.display_array(arrayActor)
            antenna_current._actor_array=arrayActor
        if(self.currentModel!=None):
            if(not os.path.exists(self.currentModel.geoFile)):
                try:
                    api_model.exportModel(self.currentModel.shape,self.currentModel.geoFile)
                except Exception as e:  
                    traceback.print_exc()
                
                pass
            modeActor=api_vtk.stl_model(self.currentModel.geoFile)
            self._meshViewer.display_model(modeActor)
            antenna_current._actor_model=modeActor
        
        
        if(antenna_current._actor_antenna!=None and antenna_current._show_antenna):
            self.sig_rotateRadio((antenna_current.rotate_x,
                                    antenna_current.rotate_y,
                                    antenna_current.rotate_z))
            self.sig_axisRefresh_antenna(antenna_current.axis_length_antenna,antenna_current.axis_thickness_antenna)
    

        
        return antenna_current
        self._antenna_c=antenna_current

        pass
        
    def nodeAction_importRadio(self):
        '''
        导入天线文件，调整方向图姿态使用
        '''
        #1.导入模型
        #2.导入阵列天线
        #3.导入方向图，局部坐标系原点为方向图原点
        #将方向图文件拷贝到工程目录下，与导入阵列数据，导入模型的处理方式相同，
        #(1)检查是否已经保存过工程，未保存则使用user目录的temp文件夹保存的当前工程
        #(2)将导入的模型、阵列文件、方向图文件，保存一份至工程目录，后续将使用工程目录下的文件
        #(3)保存工程，将当前temp文件目录下的文件，拷贝到工程目录
        antenna_current=self._antenna_c

        fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=Antenna.import_radioExtension)
        if fname != '':
            # rList=api_reader.read_nfr(fname)
            # rList=api_reader.read_nfr_radius(fname)
            rList=api_reader.read_nfr_deg(fname)
            # api_writer.degree_radius(fname)
            
            antenna_current.nfr_data=rList[0]
            antenna_current.file_antenna=fname

            self._antenna_c=antenna_current
            self._frm_arrangement.updateRadioFile(fname)

            antenna_current=self.antennaRadioRender(antenna_current)
            self._antenna_c=antenna_current
            
            QtWidgets.QMessageBox.about(self, "Import", "方向图导入成功")
        pass
    def sig_axisRefresh_antenna(self,axis_length,thickness):
        antenna_current=self._antenna_c
        antenna_current.axis_length_antenna=axis_length
        
        antenna_current.axis_thickness_antenna=thickness

        self._meshViewer.set_axis_center_lenth(axis_length*antenna_current.m_unit)
        self._meshViewer.set_axis_line_width(thickness)
        self._antenna_c=antenna_current

    def sig_scaleRadio(self,scale):
        antenna_current=self._antenna_c
        if(antenna_current._actor_antenna!=None):
            self._meshViewer.scaleActor(antenna_current._actor_antenna,scale)
        antenna_current.radio_scale=scale
        self._antenna_c=antenna_current
    def sig_rotateRadio(self,rorateDegree:tuple):
        # print("projectTree rotate radio",rorateDegree)
        antenna_current=self._antenna_c
        last_rotate=self._last_rotate
        negated_tuple=(0,0,0)
        if(antenna_current._actor_antenna!=None):
            if(last_rotate!=None):#已经旋转过，需要先恢复原始角度
                negated_tuple = tuple(x * -1 for x in last_rotate)
                # self._meshViewer.rotate(antenna_current._actor_antenna,
                #                         negated_tuple)
            sum_tuple = tuple(x + y for x, y in zip(negated_tuple, rorateDegree))
            self._meshViewer.rotate_radio(antenna_current._actor_antenna,
                                    sum_tuple)
            self._meshViewer.rotate_axis(rorateDegree)
        self._last_rotate=rorateDegree
        antenna_current.rotate_x=rorateDegree[0]
        antenna_current.rotate_y=rorateDegree[1]
        antenna_current.rotate_z=rorateDegree[2]
        self._antenna_c=antenna_current
        pass
    def sig_axisShow_radio(self,show):
        if(show):
            self._meshViewer.display_axis_center()
        else:
            self._meshViewer.hide_axis_center()
        self._antenna_c._show_axis_radio=show
    def sig_antennaShow_radio(self,show):
        if(show):
            self._meshViewer.display_actor(self._antenna_c._actor_antenna)
        else:
            self._meshViewer.remove_actor(self._antenna_c._actor_antenna)
        self._antenna_c._show_antenna=show
    def nodeAction_TransimitRadio(self):
        '''
        方向图调整
        '''
        return
 
    '''
    Mesh节点操作
    '''
    # def nodeAction_DisplayMesh(self):
    #     meshObj:Mesh=self.tree.currentItem().data(0,Mesh.objIndex)
    #     self._meshViewer.hide_mesh(self.currentMeshActor)
    #     self.currentMeshActor=api_vtk.stl_mesh(meshObj.fileName)
    #     self._meshViewer.display_mesh(self.currentMeshActor)
    #     self.currentMesh=meshObj
    #     self.sigActivateTab.emit(1)
    #     pass
    # def sig_AddMeshItem(self,meshObj:Mesh):
    #     self.node_clear(self.meshRoot)
    #     meshItem=QTreeWidgetItem(self.meshRoot)
    #     meshItem.setText(0, meshObj.title)
    #     meshItem.setIcon(0, treeIcons.mesh_item)
    #     meshItem.setData(0,Mesh.objIndex,meshObj)
    #     meshItem.setData(0,self.actionIndex,self.actionsMeshItem)
        
    #     self.tree.setCurrentItem(meshItem)
    # def sig_selectFace(self,faceId:int):
    #     '''选中面后的处理，记录下面编号，后续可以为这些面单独设置尺寸
    #     '''
    #     if(faceId in self.currentMeshSizeDic):
    #         del self.currentMeshSizeDic[faceId]
    #     else:
    #         self.currentMeshSizeDic[faceId]=10
    #     QtWidgets.QMessageBox.about(self, "Face", "Selected {},current:faceId:{}".format(len(self.currentMeshSizeDic),faceId))

    #     pass
    # def sig_setLocalSize(self,sizeDic:dict):
    #     '''设置当前网格的局部尺寸
    #     '''
    #     self.currentMeshSizeDic=sizeDic
    #     pass
    def getFaceBound(self):
        #获取面的边界设置，用于生成网格，
        faceDic={}
        if(self._pf.em.used):
            for k in self._pf.em.em_pec_dic.keys():
                faceDic[k]=True 
        if(self._pf.circuit.used):
            for k in self._pf.circuit.circuit_load_dic.keys():
                faceDic[k]=True
            for k in self._pf.circuit.circuit_source_dic.keys():
                faceDic[k]=True
        if(self._pf.thermal.used):
            for k in self._pf.thermal.thermal_convection_dic.keys():
                faceDic[k]=True
            for k in self._pf.thermal.thermal_radiation_dic.keys():
                faceDic[k]=True
            for k in self._pf.thermal.thermal_dirichlet_dic.keys():
                faceDic[k]=True
        if(self._pf.struct.used):
            for k in self._pf.struct.struct_dirichlet_dic.keys():
                faceDic[k]=True
        return faceDic
    def getBodyMaterial(self):
        t=self.currentModel.mediumFaces
        bodyDic={}
        return bodyDic
    def start_mesh_timer(self):
        self._mesh_timer=QTimer()
        self._mesh_timer.timeout.connect(self.mesh_timer_timeout)
        self._mesh_timer.start(100)
    def mesh_timer_timeout(self):
        p=self._meshProcess
        if(p==None):
            self._mesh_timer.stop()
            return
        if(p.poll() is None):
            #进程未结束
            output = self._mesh_nbsr.readline(0.1)
            if(output!=None):
                self.console.print_text(str(output,Project.solverEncoding)+"\r\n")
                QtWidgets.QApplication.processEvents()
            pass
           
        else:
            self._mesh_timer.stop()
            self._meshProcess=None
            QtWidgets.QMessageBox.about(self,"Mesh","网格生成完成")
    def mpmetis_split(self):
        '''
        使用mpmetis进行网格划分,将文件拷贝到input文件夹下
        '''
        _dir=os.path.dirname(os.path.abspath(sys.executable))
        # exeFile=_dir+"/mpmetis.exe"
        cmd=f"mpmetis.exe -gtype=nodal EMProcMesh.txt {self.currentProject.mpiNum}"
        # args=[exeFile,"-gtype=nodal EMProcMesh.txt",str(self.currentProject.mpiNum)]
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             cwd=_dir,
                             creationflags = subprocess.CREATE_NO_WINDOW,
                             stderr=subprocess.PIPE
                             )
        self._mesh_nbsr=NBSR(p.stdout)
        while(p.poll() is None):
            #进程未结束
                output = self._mesh_nbsr.readline(0.1)
                if(output!=None):
                    self.console.print_text(str(output,Project.solverEncoding)+"\r\n")
                    QtWidgets.QApplication.processEvents()
        if(p.poll() is not None):
            output = self._mesh_nbsr.readline(0.1)
            if(output!=None):
                self.console.print_text(str(output,Project.solverEncoding)+"\r\n")
                QtWidgets.QApplication.processEvents()
            if(p.stderr!=None and  p.stderr.readable()):
                line = p.stderr.read()
                line=line.strip()
                if line and self.console!=None:
                    self.console.print_text(str(line,Project.solverEncoding)+"\r\n")
            self.console.print_text("网格分区任务完成.\r\n")
        
        
        QtWidgets.QApplication.processEvents()
        # QtWidgets.QMessageBox.about(self,"Mesh","并行生成完成")
        srcFile=_dir+f"/EMProcMesh.txt.epart.{self.currentProject.mpiNum}"
        destFile=f"{self.get_input_path()}/EMProc.txt"
        if(os.path.exists(srcFile)):
            api_project.copyFile(srcFile,destFile)
        else:
            QtWidgets.QMessageBox.about(self,"Mesh","划分文件不存在")
        pass
    def run_mesh_solver(self,strJson):
        try:
            _dir=os.path.dirname(os.path.abspath(sys.executable))
            
            sourceSolverFile=_dir+"/xmesh.exe"
            # sourceSolverFile=_dir+"/bin/xmesh.exe"
            
            
            if(not os.path.exists(sourceSolverFile)):
                QtWidgets.QMessageBox.about(self,"info","exe文件不存在"+sourceSolverFile)
            # inputFiles=",".join(fnameList)
            args = [sourceSolverFile, strJson]
            
            # print(args)
            # myPopenObj = subprocess.Popen(args=args,creationflags=subprocess.CREATE_NO_WINDOW)
            p = subprocess.Popen(args=args,
                                 stdout=subprocess.PIPE,
                                 creationflags = subprocess.CREATE_NO_WINDOW,
                                 stderr=subprocess.PIPE
                                 )
            self._meshProcess=p 
            self._mesh_nbsr=NBSR(p.stdout)
            # self.start_mesh_timer()
            self.console.clear()
            lineIndex=0
            while(p.poll() is None):
            #进程未结束
                output = self._mesh_nbsr.readline(0.1)
                if(output!=None):
                    lineIndex=lineIndex+1
                    self.console.print_text(str(output,Project.solverEncoding)+"\r\n")
                    if(lineIndex%10==0):
                        QtWidgets.QApplication.processEvents()
        
            QtWidgets.QApplication.processEvents()
            self.console.print_text("网格任务结束.\r\n")
            self._meshProcess=None
            QtWidgets.QMessageBox.about(self,"Mesh","网格生成完成")
            vtkFileName=self.get_fname_mesh_vtk()
            self.currentMesh.fileName=vtkFileName
            self._meshViewer.clear()
            actor=api_vtk.render_vtk_file(vtkFileName)
            self._meshViewer.display_mesh(actor)
            self.sigActivateTab.emit(1)
            if(self.currentProject.mpiNum>1):#并行时再执行分区网格
                self.mpmetis_split()

            pass
            print("start success.")
            # QtWidgets.QMessageBox.about(None, "run", projectFile)
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "网格生成", str(e))
            print(e)
    def sig_options_save(self,options:dict):
        self.currentMesh.options=options
        QtWidgets.QMessageBox.about(self, "网格", "保存设置成功")

    def sig_createMesh(self,options:dict):
        '''创建网格 生成网格对象
        '''
        # print("to create mesh size",maxh)
    
        # fname = self.currentModel.fileName
        #生成网格时，需要先标记材料体域、边界条件面，在gmsh中导入stp文件
        #按照完美匹配层域、空气域1、空气域2，模型域的顺序来生成网格
        if(self.currentModel==None):
            QtWidgets.QMessageBox.about(self, "Mesh", "请先选中一个模型")
            return
        if(not os.path.exists(self.currentModel.fileName)):
            QtWidgets.QMessageBox.about(self, "Mesh", "模型文件丢失:"+self.currentModel.fileName)
            return
        self.currentMesh.options=options
        faceDic=self.getFaceBound()
        bodyDic=self.currentModel.mediumFaces #体编号，材料编号

        fNameList=[]
        #将bodydic的value值+1 材料索引编号
        bodyDicN={}
        for k,v in bodyDic.items():
            bodyDicN[k]=v+1
        # if(self._pf.em.used):#计算电磁域
        #     pass
        fName_model=self.get_name_model_named()
        # fragShape=api_model.fragment_shape(self.currentModel.shapeList)
        api_model.exportModel([self.currentModel.shape],fName_model,(faceDic,bodyDicN))
        fNameList.append(fName_model)
        #pml固定材料，0-7 8个角，10015 12条棱 10011 10013 10014
        pml_bodyDic={
            4:10015,
            5:10015,
            6:10015,
            7:10015,
            8:10015,
            9:10015,
            10:10015,
            11:10015,
            12:10011,
            13:10011,
            14:10011,
            15:10011,
            16:10013,
            17:10013,
            18:10013,
            19:10013,
            20:10014,
            21:10014,
            22:10014,
            23:10014,
            24:10009,
            25:10009,
            26:10012,
            27:10012,
            28:10010,
            29:10010,
        }
        pml_bodyDicN={}
        #将每个key换算为从0开始的编号
        kIndex=0
        for k,v in pml_bodyDic.items():
            pml_bodyDicN[kIndex]=v
            kIndex=kIndex+1
        if(self._pf.em.used):
            if(len(self.currentModel.shapeList_exf)>0):
                fName_exf=self.get_name_exf_named()
                api_model.exportModel(self.currentModel.shapeList_exf,fName_exf,({},{0:10007,1:10008}))
                fNameList.append(fName_exf)
            if(len(self.currentModel.shapeList_pml)>0):
                fName_pml=self.get_name_pml_named()
                api_model.exportModel(self.currentModel.shapeList_pml,fName_pml,({},pml_bodyDicN))
                fNameList.append(fName_pml)
        
        vtkFileName=self.get_fname_mesh_vtk()
        mshFileName=self.get_fname_mesh_msh()
        outputFileName=self.get_fname_mesh()
        # self.original_stdout = sys.stdout#保存标准输出
        # sys.stdout = self
        fname_mesh=self.get_fname_mesh()
        thermal_struct_used=1
        if(not self._pf.thermal.used and not self._pf.struct.used):
            thermal_struct_used=0
        param_json={"fnameList":fNameList,
                    "options":options,
                    "vtkFileName":vtkFileName,
                    "mshFileName":mshFileName,
                    "outputFileName":outputFileName,
                    "thermal_struct_used":thermal_struct_used,
                    "localSize":self.currentMesh.localSize}
        str_json=json.dumps(param_json)
        
        self.run_mesh_solver(str_json)
        return
        

        # rec_json=json.loads(str_json)
        # print("localsize",rec_json["localSize"])
        code,message,data=api_gmsh.createMesh(str_json)
        # sys.stdout = self.original_stdout #恢复标准输出
        if(code==1):
            tLength=data[3]
            if(not self._pf.thermal.used and not self._pf.struct.used):
                tLength=0
            api_writer.write_mesh(fname=fname_mesh,
                                  nodeList=data[0],
                                  boundaryList=data[1],
                                  tetList=data[2],
                                  model_nodes_length=tLength)
            self.currentMesh.fileName=vtkFileName
            self._meshViewer.clear()
            actor=api_vtk.render_vtk_file(vtkFileName)
            self._meshViewer.display_mesh(actor)
            self.sigActivateTab.emit(1)
            

    
        QtWidgets.QMessageBox.about(self, "Mesh", message)
        pass
    # def nodeAction_ImportMesh(self):
    #     # code,message,data=api_mesh.mesh_load()
    #     fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(filter=Mesh.importExtensions)
    #     if fname != '':
    #         code,message,data=api_mesh.mesh_import(fname,filter_)
    #         # print(data)
    #         actor=api_vtk.stl_mesh(data["file"])
    #         self._meshViewer.display_mesh(actor)
    #         QtWidgets.QMessageBox.about(self, "Import", "网格导入成功      ")
    #         self.sigActivateTab.emit(1)
    #     pass
    def write(self, message):
        self.console.print_text(message)
        QtWidgets.QApplication.processEvents()

    def flush(self):
        pass  # 必须实现 flush 方法
    def nodeAction_ImportMesh(self):
        EXTENSIONS = "Mesh files(*.vtk )"
        curr_dir = Path('').abspath().dirname()
        fname = get_open_filename(EXTENSIONS, curr_dir)
        if fname == '':
            return
  


        self._logger.info("导入网格:{0}...".format(fname))
        self.console.print_text(" ")
        # self._logger.info("导入模型中...")
    
        QtWidgets.QApplication.processEvents()

        vtkFileName=fname
     
        self._meshViewer.clear()
        actor=api_vtk.render_vtk_file(vtkFileName)
        self._meshViewer.display_mesh(actor)
        self.sigActivateTab.emit(1)

        self._logger.info("导入网格完成.")
        pass
    def set_solver(self,solver:str):
        print("set solver",solver)
        pass
    def nodeAction_ExportMesh(self):
        if self.currentMesh==None:
            QtWidgets.QMessageBox.about(self, "Export mesh", "请先生成或选择一个网格，当前网格对象为空")
            return
        fname,filter_ = QtWidgets.QFileDialog.getSaveFileName(filter=Mesh.exportExtensions)
        if fname != '':
            # code,message=api_mesh.exportMesh(self.currentMesh.mesh,fname,filter_)
            QtWidgets.QMessageBox.about(self, "Export mesh", message)
        pass
    def nodeAction_CreateMesh(self):
        try: 
            options=self.currentMesh.options
            localsize=self.currentMesh.localSize

            frmMesh=frmCreateMesh(self,options,localsize)
            frmMesh.show()
            frmMesh.move(self.topLeffPoint())
            frmMesh.sigCreate.connect(self.sig_createMesh)
            frmMesh.sigOptions.connect(self.sig_options_save)
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Create mesh", "创建网格错误:"+str(e))
            self._pLogger.error("create mesh",traceback.format_exc())
            pass
    

    def nodeAction_DeleteMesh(self):
        self._meshViewer.clear()
        self.meshRoot.removeChild(self.tree.currentItem())
        self.currentMesh=None
        
        pass

    '''
    port节点操作
    '''
    # def sig_createPort(self,edge:tuple,edgeId:int):
    #     # QtWidgets.QMessageBox.about(self,"Add port","edgeId:"+str(edgeId)) 
    #     #删除已添加的port
    #     childCount=self.portRoot.childCount()
    #     for i in range(childCount):
    #         item=self.portRoot.child(i)
    #         tmpData:Port=item.data(0,Port.objIndex)
    #         if(tmpData.edgeId==edgeId):
    #             self.portRoot.removeChild(item)
    #             return    
    #     portObj=Port()
    #     portObj.index=Port.currentIndex
    #     portObj.name=Port.titlePrefix+str(Port.currentIndex)
    #     portObj.title=portObj.name
    #     portObj.modelName=self.currentModel.name
    #     # portObj.shape=edgeShape
    #     start=edge[0]
    #     end=edge[1]
    #     portObj.edgePoint=edge
    #     portObj.edgeId=edgeId
    #     portObj.startX=start[0]
    #     portObj.startY=start[1]
    #     portObj.startZ=start[2]
    #     portObj.endX=end[0]
    #     portObj.endY=end[1]
    #     portObj.endZ=end[2]
    #     self.addPortItem(portObj)
    #     pass
    # def addPortItem(self,portObj:Port):
    #     edgeItem = QTreeWidgetItem(self.portRoot)
    #     edgeItem.setText(0, portObj.title)
    #     edgeItem.setIcon(0, treeIcons.port_item)
    #     edgeItem.setData(0,self.actionIndex,self.actionsPortItem)
    #     edgeItem.setData(0,Port.objIndex,portObj)
    #     Port.currentIndex = Port.currentIndex+1
    # def getEdgeIdList(self):
    #     idList:list[int]=[]
    #     if(self.portRoot==None):
    #         return idList
    #     childCount=self.portRoot.childCount()
    #     for i in range(childCount):
    #         portObj:Port=self.portRoot.child(i).data(0,Port.objIndex)
    #         if(portObj.modelName==self.currentModel.name):#当前模型的port才加上去
    #             idList.append(portObj.edgeId)
    #     return idList
    # def getPorts(self):
    #     portList:list[Port]=[]
    #     childCount=self.portRoot.childCount()
    #     for i in range(childCount):
    #         portObj=self.portRoot.child(i).data(0,Port.objIndex)
    #         portList.append(portObj)
    #         pass
    #     return portList
    # def portFillVerticeIndex(self,ports,mesh:Mesh):
    #     portList:list[Port]=ports
    #     for port in portList:
    #         vList=api_mesh.getVerticeList(mesh,port.edgePoint)
    #         port.vIndexList=vList
    #         pass
    # def nodeAction_AddPort(self):
    #     self.sigPickEdge.emit()
    #     self.sigActivateTab.emit(0)
    #     self.portRoot.setExpanded(True)
    #     QtWidgets.QMessageBox.about(self,"Add port","请按住ctrl键，然后通过鼠标停在某个边上，单机鼠标左键即可完成.")
    #     pass
    # def nodeAction_RenamePort(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass
    # def nodeAction_DeletePort(self):
    #     item=self.tree.currentItem()
    #     portObj:Port=item.data(0,Port.objIndex)
    #     self.sigRemoveSelectedEdge.emit(portObj.edgeId)
    #     self.portRoot.removeChild(item)
    #     pass
    # def nodeAction_ShowHidePort(self):
    #     self.portFillVerticeIndex(self.getPorts(),self.currentMesh.mesh)
    #     pass
    '''
    激励设置相关节点，frequency,power,sources,loads
    '''
    def sig_modifyFrequency(self,freqObj:Frequency):
        self.frequencyRoot.setData(0,Frequency.objIndex,freqObj)
        pass
    
    def nodeAction_FrequencyProperties(self):
        freqObj=self.frequencyRoot.data(0,Frequency.objIndex)
        frmFreq=frmFrequency2(self,freqObj)
        frmFreq.show()
        frmFreq.sigModify.connect(self.sig_modifyFrequency)
        pass
    def nodeAction_TemperatureProperties(self):
        pass

    # def sig_modifyPower(self,powerObj:Power):
    #     self.powerRoot.setData(0,Power.objIndex,powerObj)
    #     self.tree.setCurrentItem(self.powerRoot)
    # def nodeAction_PowerProperties(self):
    #     powerObj=self.powerRoot.data(0,Power.objIndex)
    #     frmPowerX=frmPower(self,powerObj)
    #     frmPowerX.show()
    #     frmPowerX.sigModifyPower.connect(self.sig_modifyPower)
    #     pass
    # def nodeAction_DeletePower(self):
    #     self.excitationRoot.removeChild(self.powerRoot)
    #     self.powerRoot=None

    # def nodeAction_Power(self):
    #     if(self.powerRoot==None): 
    #         self.powerRoot = QTreeWidgetItem(self.excitationRoot)
    #         self.powerRoot.setText(0, Power.nodeName)
    #         self.powerRoot.setIcon(0, treeIcons.power)
    #         self.powerRoot.setExpanded(True)
    #         self.powerRoot.setData(0,self.actionIndex,self.actionsPowerRoot)
    #     if(not self.isLoading):
    #         self.nodeAction_PowerProperties()
    #     pass


    # def sig_addSourceItem(self,sourceObj:Source):
    #     # print(sourceObj)
    #     sourceItem=QTreeWidgetItem(self.sourceRoot)
    #     sourceItem.setText(0, sourceObj.title)
    #     sourceItem.setIcon(0, treeIcons.source_item)
    #     sourceItem.setData(0,Source.objIndex,sourceObj)
    #     sourceItem.setData(0,self.actionIndex,self.actionsSourceItem)
        
    #     self.sourceRoot.setExpanded(True)
    #     self.tree.setCurrentItem(sourceItem)

    #     Source.currentIndex=Source.currentIndex+1

    #     pass
    # def sig_modifySourceItem(self,sourceObj:Source):
    #     self.tree.currentItem().setData(0,Source.objIndex,sourceObj)

    # def nodeAction_AddSource(self):
    #     # self.source.setExpanded(False)
    #     frmvSource=frmVoltageSource(self,0,None,self.getPorts())
    #     frmvSource.show()
    #     frmvSource.sigCreate.connect(self.sig_addSourceItem)
    #     pass
    # def nodeAction_SourceProperties(self):
    #     sourceObj=self.tree.currentItem().data(0,Source.objIndex)
    #     frm_voltageSource=frmVoltageSource(self,1,sourceObj,self.getPorts())
    #     frm_voltageSource.show()
    #     frm_voltageSource.sigModify.connect(self.sig_modifySourceItem)
    # def nodeAction_DeleteVSource(self):
    #     self.sourceRoot.removeChild(self.tree.currentItem())
    #     pass
    # def nodeAction_RenameVSource(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass

    # def sig_addLoadItem(self,loadObj:Load):
    #     loadItem= QTreeWidgetItem(self.loadRoot)
    #     loadItem.setText(0, loadObj.title)
    #     loadItem.setIcon(0, treeIcons.load_item)
    #     loadItem.setData(0,Load.objIndex,loadObj)
    #     loadItem.setData(0,self.actionIndex,self.actinosLoadItem)
    #     self.tree.setCurrentItem(loadItem)
    #     self.loadRoot.setExpanded(True)

    #     Load.currentIndex=Load.currentIndex+1
    #     pass
    # def sig_modifyLoadItem(self,loadObj:Load):
    #     self.tree.currentItem().setData(0,Load.objIndex,loadObj)
    #     pass
    # def nodeAction_Loads(self):
    #     if(self.loadRoot==None):
    #         self.loadRoot = QTreeWidgetItem(self.excitationRoot)
    #         self.loadRoot.setText(0, tree.projctTreeNodes.loads)
    #         self.loadRoot.setIcon(0, treeIcons.load)
    #         self.loadRoot.setData(0,self.actionIndex,self.actionsLoadRoot)
    #         self.loadRoot.setExpanded(True)
    #     if(not self.isLoading):
    #         self.nodeAction_AddLoad()
       
    # def nodeAction_AddLoad(self):
    #     frmL=frmLoad(self,0,None,self.getPorts())
    #     frmL.show()
    #     frmL.sigCreate.connect(self.sig_addLoadItem)
        
    #     pass
    # def nodeAction_LoadProperties(self):
    #     loadObj=self.tree.currentItem().data(0,Load.objIndex)
    #     frmL=frmLoad(self,1,loadObj,self.getPorts())
    #     frmL.show()
    #     frmL.sigModify.connect(self.sig_modifyLoadItem)
    #     pass
    # def nodeAction_DeleteLoad(self):
    #     self.loadRoot.removeChild(self.tree.currentItem())
    #     if(self.loadRoot.childCount()<1):
    #         self.excitationRoot.removeChild(self.loadRoot)
    #         self.loadRoot=None
    #     pass
    # def nodeAction_RenameLoad(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass
    

    '''
    FFR 节点操作
    '''
    # def sig_addFFRItem(self,ffrObj:FFR):
    #     if(self.ffrRoot==None):
    #         self.ffrRoot=QTreeWidgetItem(self.requestRoot)
    #         self.ffrRoot.setText(0, FFR.classTitle)
    #         self.ffrRoot.setIcon(0, treeIcons.ffr)
    #         self.ffrRoot.setData(0,self.actionIndex,self.actionsFFRRoot)
    #         self.ffrRoot.setExpanded(True)
    #     nItem=QTreeWidgetItem(self.ffrRoot)
    #     nItem.setText(0, ffrObj.title)
    #     nItem.setIcon(0, treeIcons.ffr_item)
    #     nItem.setData(0,FFR.objIndex,ffrObj)
    #     nItem.setData(0,self.actionIndex,self.actionsFFRItem)
    #     self.tree.setCurrentItem(nItem)
    #     self.ffrRoot.setExpanded(True)
    #     FFR.currentIndex=FFR.currentIndex+1

    # def sig_modifyFFRItem(self,ffrObj:FFR):
    #     self.tree.currentItem().setData(0,FFR.objIndex,ffrObj)

    # def nodeAction_AddFFR(self):
    #     '''打开工程时，不需要弹出新增窗体
    #     '''

    #     if(not self.isLoading):
    #         self.nodeAction_AddFFRItem()
    #     pass

    # def nodeAction_AddFFRItem(self):
    #     frmFFR=frmRequestFFR(self)
    #     frmFFR.show()
    #     frmFFR.sigCreate.connect(self.sig_addFFRItem)
    #     pass
    # def nodeAction_FFRProperties(self):
    #     ffrObj=self.tree.currentItem().data(0,FFR.objIndex)
    #     frmFFR=frmRequestFFR(self,1,ffrObj)
    #     frmFFR.show()
    #     frmFFR.sigModify.connect(self.sig_modifyFFRItem)
    #     pass
    # def nodeAction_RenameFFRItem(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass
    # def nodeAction_DeleteFFRItem(self):
    #     self.ffrRoot.removeChild(self.tree.currentItem())
    #     if(self.ffrRoot.childCount()<1):
    #         self.requestRoot.removeChild(self.ffrRoot)
    #         self.ffrRoot=None
    #     pass
    # def nodeAction_ShowHideFFRItem(self):
    #     pass

    '''
    物理场-电磁节点
    '''
    def sig_modifyEM(self,eObj:PF_EBase):
        self.pfEMRoot.setData(0,PF.objIndex,eObj)
        pass
    def nodeAction_DeleteEM(self):
        self.pfEMRoot.setHidden(True)
        self.pfBoundEMRoot.setHidden(True)
        self.reqFFRRoot.setHidden(True)
        self.resultEMRoot.setHidden(True)
        self.resultFFRRoot.setHidden(True)
        self._pf.em.used=False
        pass
    # region 新版本物理场设置
    def action_clear_pf(self):
        #清除所有物理场
        self.nodeAction_DeleteEM()
        self.nodeAction_DeleteCircuit()
        self.nodeAction_DeleteThermal()
        self.nodeAction_DeleteStruct()
        SIM_EXE_LIST=[
    "EM.exe",
    "Thermal.exe",
    "Mechanical.exe",
    "Thermal_Mechanical.exe",
    "Thermal_Mechanical_EM.exe",
    "Mechanical_EM.exe",
    "EM_Thermal.exe",
    "EM_Thermal_Mechanical.exe",
]
       

    def action_pf_em_circuit(self):
        #电磁电路物理场
        self.action_clear_pf()
        self.nodeAction_AddEM()
        self.nodeAction_AddCircuit()
        self.currentProject.exeName="EM.exe"
        self.currentProject.pfName="em_circuit"
        
        pass
    def action_pf_thermal(self):
        self.action_clear_pf()
        self.nodeAction_AddThermal()
        self.currentProject.exeName="Thermal.exe"
        self.currentProject.pfName="thermal"

    def action_pf_struct(self):
        self.action_clear_pf()
        self.nodeAction_AddStruct()
        self.currentProject.exeName="Mechanical.exe"
        self.currentProject.pfName="struct"

    def action_pf_thermal_struct(self):
        #热结构耦合物理场
        self.action_clear_pf()
        self.nodeAction_AddThermal()
        self.nodeAction_AddStruct()
        self.currentProject.exeName="Thermal_Mechanical.exe"
        self.currentProject.pfName="thermal_struct"
        pass
    def action_pf_thermal_struct_em_circuit(self):
        self.action_clear_pf()
        self.nodeAction_AddEM()
        self.nodeAction_AddCircuit()
        self.nodeAction_AddThermal()
        self.nodeAction_AddStruct()
        self.currentProject.exeName="Thermal_Mechanical_EM.exe"
        self.currentProject.pfName="thermal_struct_em_circuit"
        pass
    def action_pf_em_circuit_thermal_struct(self):
        #电磁电路热结构耦合物理场
        self.action_clear_pf()
        self.nodeAction_AddEM()
        self.nodeAction_AddCircuit()
        self.nodeAction_AddThermal()
        self.nodeAction_AddStruct()
        self.currentProject.exeName="Thermal_Mechanical_EM.exe"
        self.currentProject.pfName="em_circuit_thermal_struct"
        pass
    def action_pf_em_circuit_thermal(self):
        #电磁电路热物理场
        self.action_clear_pf()
        self.nodeAction_AddEM()
        self.nodeAction_AddCircuit()
        self.nodeAction_AddThermal()
        self.currentProject.exeName="EM_Thermal.exe"
        self.currentProject.pfName="em_circuit_thermal"
        pass
    def action_pf_struct_em_circuit(self):
        #电磁电路结构物理场
        self.action_clear_pf()
        self.nodeAction_AddEM()
        self.nodeAction_AddCircuit()
        self.nodeAction_AddStruct()
        self.currentProject.exeName="Mechanical_EM.exe"
        self.currentProject.pfName="struct_em_circuit"
        pass

    # endregion

    def nodeAction_AddEM(self):
        '''
        添加电磁节点，每次弹出设置窗体
        '''

        self.pfEMRoot.setHidden(False)
        self.pfBoundEMRoot.setHidden(False)
        self.reqFFRRoot.setHidden(False)
        self.resultEMRoot.setHidden(False)
        self.resultFFRRoot.setHidden(False)
        self.tree.setCurrentItem(self.pfEMRoot)
        self._pf.em.used=True
        self.pfEMRoot.setData(0,PF.objIndex,self._pf.em)

        pass
    def nodeAction_EMProperties(self):
        eObj=self.pfEMRoot.data(0,PF.objIndex)
        if(eObj==None):
            eObj=PF_EM()
        frm=frmDomainPF(self,eObj)
        frm.sigModify.connect(self.sig_modifyEM)
        frm.move(self.topLeffPoint())
        frm.show()
        self.tree.setCurrentItem(self.pfEMRoot)

    def initFaces_pec(self):
        face_dic=self._pf.em.em_pec_dic
        self.node_clear(self.pfBoundEMPECRoot)
        for k in face_dic:
            itemNode=QTreeWidgetItem(self.pfBoundEMPECRoot)
            itemNode.setText(0,"Face"+str(k+1))
            itemNode.setIcon(0,treeIcons.face)
            itemNode.setData(0,PF.objIndex,k)
            itemNode.setData(0,self.actionIndex,self.actionsPFBoundEMPECItem)


    def sig_selectFacePEC(self,faceId:int):
        #选中一个面
        self._pf.em.em_pec_dic[faceId]=True
        self.initFaces_pec()
        pass
    def nodeAction_ClearEMPEC(self):
        self._pf.em.em_pec_dic={}
        self.node_clear(self.pfBoundEMPECRoot)

    def nodeAction_DeleteEMPECItem(self):
        currentItem=self.tree.currentItem()
        k=currentItem.data(0,PF.objIndex)
        del self._pf.em.em_pec_dic[k]
        self.pfBoundEMPECRoot.removeChild(currentItem)
    def closeFormsOpened(self):
        try:
            # for frm in self._forms:
            #     frm.close()
            # self._forms.clear()
            pass
        except Exception as e:
            print("closeFormsOpened",e)

    def nodeAction_AddEMPEC(self):
        self.closeFormsOpened()
        frm=frmEMPEC(self)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigFaceSelected.connect(self.sig_selectFacePEC)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()

        self._forms.append(frm)
        pass
    

    '''
    物理场-电路节点
    '''
    def sig_modifyCircuit(self,eObj):
        self.pfCircuitRoot.setData(0,PF.objIndex,eObj)
    def initFaces_circuit_source(self):
        face_dic=self._pf.circuit.circuit_source_dic
        nodeRoot=self.pfBoundCircuitSourceRoot
        actions=self.actionsPFBoundCircuitSourceItem
        actionIndex=self.actionIndex
        self.node_clear(nodeRoot)
        for k in face_dic:
            sourceObj:PF_Circuit_Source=face_dic[k]
            source_type_str="线端口"
            if(not hasattr(sourceObj,"source_type")):
                sourceObj.source_type=0
            if(sourceObj.source_type==1):
                source_type_str="面端口"
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,f"Face{k+1}({source_type_str})")
            if(sourceObj.source_type==0):
                itemNode.setIcon(0,treeIcons.gdtd_port_line)
            else:
                itemNode.setIcon(0,treeIcons.gdtd_port_face)
            itemNode.setData(0,PF.objIndex,(k,face_dic[k]))
            itemNode.setData(0,actionIndex,actions)
    def initFaces_circle_load(self):
        face_dic=self._pf.circuit.circuit_load_dic
        nodeRoot=self.pfBoundCircuitLoadRoot
        actions=self.actionsPFBoundCircuitLoadItem
        actionIndex=self.actionIndex
        self.node_clear(nodeRoot)
        for k in face_dic:
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,"Face"+str(k+1))
            itemNode.setIcon(0,treeIcons.face)
            itemNode.setData(0,PF.objIndex,(k,face_dic[k]))
            itemNode.setData(0,actionIndex,actions)
    def sig_selectFaceCircuitSource(self,faceId:int,sourceObj:PF_Circuit_Source,faceId_old):
        if(faceId_old in self._pf.circuit.circuit_source_dic):
            del self._pf.circuit.circuit_source_dic[faceId_old]
        self._pf.circuit.circuit_source_dic[faceId]=sourceObj
        self.initFaces_circuit_source()
        pass
    def sig_selectFaceCircuitLoad(self,faceId:int,loadValue:float,faceLength:tuple,faceId_old):
        if(faceId_old in self._pf.circuit.circuit_load_dic):
            del self._pf.circuit.circuit_load_dic[faceId_old]
        self._pf.circuit.circuit_load_dic[faceId]=(loadValue,faceLength)
        self.initFaces_circle_load()
        pass
    def nodeAction_DeleteCircuit(self):
        self.pfCircuitRoot.setHidden(True)
        self.pfBoundCircuitRoot.setHidden(True)
        self._pf.circuit.used=False
        pass
    def nodeAction_AddCircuit(self):
        self.pfCircuitRoot.setHidden(False)
        self.pfBoundCircuitRoot.setHidden(False)
        self.tree.setCurrentItem(self.pfCircuitRoot)
        self._pf.circuit.used=True
        
    def nodeAction_CircuitProperties(self):
        eObj=self.pfCircuitRoot.data(0,PF.objIndex)
        if(eObj==None):
            eObj=PF_Circuit()
        frm=frmDomainPF(self,eObj)
        frm.sigModify.connect(self.sig_modifyCircuit)
        frm.move(self.topLeffPoint())
        frm.show()
        self.tree.setCurrentItem(self.pfCircuitRoot)


        pass
    def nodeAction_AddCircuitSource(self):
        self.closeFormsOpened()
        frm=frmCircuitSource(self)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigFaceSelected.connect(self.sig_selectFaceCircuitSource)
        self._selectContext.sigFaceLengthUV.connect(frm.sig_chooseFaceLength)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm)
        pass
    def nodeAction_AddCircuitLoad(self):
        self.closeFormsOpened()
        frm=frmCircuitLoad(self)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        self._selectContext.sigFaceLengthUV.connect(frm.sig_chooseFaceLength)
        frm.sigFaceSelected.connect(self.sig_selectFaceCircuitLoad)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm) 
        pass
    def nodeAction_ClearCircuitSource(self):
        nodeRoot=self.pfBoundCircuitSourceRoot
        self.node_clear(nodeRoot)
        self._pf.circuit.circuit_source_dic={}
        pass
    def nodeAction_ClearCircuitLoad(self):
        nodeRoot=self.pfBoundCircuitLoadRoot
        self.node_clear(nodeRoot)
        self._pf.circuit.circuit_load_dic={}
        pass
    def nodeAction_DeleteCircuitSourceItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.circuit.circuit_source_dic[k]
        self.pfBoundCircuitSourceRoot.removeChild(currentItem)

    def nodeAction_ModifyCircuitSourceItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,sourceObj=currentItem.data(0,PF.objIndex)
        frm=frmCircuitSource(self,sourceObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigFaceSelected.connect(self.sig_selectFaceCircuitSource)
        self._selectContext.sigFaceLengthUV.connect(frm.sig_chooseFaceLength)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(k)
        self._forms.append(frm)
        pass
    def nodeAction_DeleteCircuitLoadItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.circuit.circuit_load_dic[k]
        self.pfBoundCircuitLoadRoot.removeChild(currentItem)
    def nodeAction_ModifyCircuitLoadItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,loadValue=currentItem.data(0,PF.objIndex)
        frm=frmCircuitLoad(self,(k,loadValue))
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        self._selectContext.sigFaceLengthUV.connect(frm.sig_chooseFaceLength)
        frm.sigFaceSelected.connect(self.sig_selectFaceCircuitLoad)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(k)
        self._forms.append(frm)
        pass
    
    '''
    热节点操作
    '''
    def sig_modifyThermal(self,eObj:PF_Thermal):
        self.pfThermalRoot.setData(0,PF.objIndex,eObj)
        pass
    def nodeAction_DeleteThermal(self):
        self.pfThermalRoot.setHidden(True)
        self.pfBoundThermalRoot.setHidden(True)
        self.reqThermalRoot.setHidden(True)
        self.resultThermalRoot.setHidden(True)
        self._pf.thermal.used=False
        pass
    def nodeAction_AddThermal(self):
        self.pfThermalRoot.setHidden(False)
        self.pfBoundThermalRoot.setHidden(False)
        self.reqThermalRoot.setHidden(False)
        self.resultThermalRoot.setHidden(False)
        self.tree.setCurrentItem(self.pfThermalRoot)
        self._pf.thermal.used=True
        pass
    def nodeAction_ThermalProperties(self):
        eObj=self.pfThermalRoot.data(0,PF.objIndex)
        if(eObj==None):
            eObj=PF_Thermal()
        frm=frmDomainPF(self,eObj)
        frm.sigModify.connect(self.sig_modifyThermal)
        frm.move(self.topLeffPoint())
        frm.show()
        self.tree.setCurrentItem(self.pfThermalRoot)    

    def initFaces_thermal_base(self,face_dic,nodeRoot:QTreeWidgetItem,actions):
        self.node_clear(nodeRoot)
        nodeRoot.setExpanded(True)
        for k in face_dic:
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,"Face"+str(k+1))
            itemNode.setIcon(0,treeIcons.face)
            itemNode.setData(0,PF.objIndex,(k,face_dic[k]))
            itemNode.setData(0,self.actionIndex,actions)

    def initSolids_thermal_base(self,solid_dic,nodeRoot:QTreeWidgetItem,actions):
        self.node_clear(nodeRoot)
        nodeRoot.setExpanded(True)
        for k in solid_dic:
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,"Solid"+str(k+1))
            itemNode.setIcon(0,treeIcons.solid)
            itemNode.setData(0,PF.objIndex,(k,solid_dic[k]))
            itemNode.setData(0,self.actionIndex,actions)
    def initFaces_thermal_dirichlet(self):
        self.initFaces_thermal_base(self._pf.thermal.thermal_dirichlet_dic,
                                    self.pfBoundThermalDirichletRoot,
                                    self.actionsPFBoundThermalDirichletItem)


    def sig_selectFaceThermalDirichlet(self,faceId:int,dirichletObj:PF_Thermal_Dirichlet,faceId_old):
        if(faceId!=faceId_old and faceId_old in self._pf.thermal.thermal_dirichlet_dic):
            del self._pf.thermal.thermal_dirichlet_dic[faceId_old]
        self._pf.thermal.thermal_dirichlet_dic[faceId]=dirichletObj
        self.initFaces_thermal_dirichlet()
        
        pass

    def nodeAction_AddThermalDirichlet(self):
        self.closeFormsOpened()
        thermalObj=PF_Thermal_Dirichlet()
        frm=frmThermalBase(self,thermalObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalDirichlet)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm)
        pass
    def nodeAction_ClearThermalDirichlet(self):
        self._pf.thermal.thermal_dirichlet_dic={}
        self.node_clear(self.pfBoundThermalDirichletRoot)
        pass
    def nodeAction_DeleteThermalDirichletItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.thermal.thermal_dirichlet_dic[k]
        self.pfBoundThermalDirichletRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyThermalDirichletItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,dirichletObj=currentItem.data(0,PF.objIndex)
        frm=frmThermalBase(self,dirichletObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalDirichlet)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(dirichletObj.selectId)
        self._forms.append(frm)
        pass

    def initFaces_thermal_convection(self):
        self.initFaces_thermal_base(self._pf.thermal.thermal_convection_dic,
                                    self.pfBoundThermalConvectionRoot,
                                    self.actionsPFBoundThermalConvectionItem)


    def sig_selectFaceThermalConvection(self,faceId:int,convectionObj:PF_Thermal_Convection,faceId_old):
        if(faceId!=faceId_old and faceId_old in self._pf.thermal.thermal_convection_dic):
            del self._pf.thermal.thermal_convection_dic[faceId_old]
        self._pf.thermal.thermal_convection_dic[faceId]=convectionObj
        self.initFaces_thermal_convection()
        
        pass
    def nodeAction_AddThermalConvection(self):
        self.closeFormsOpened()
        thermalObj=PF_Thermal_Convection()
        frm=frmThermalBase(self,thermalObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalConvection)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm) 
        pass
    def nodeAction_ClearThermalConvection(self):
        self._pf.thermal.thermal_convection_dic={}
        self.node_clear(self.pfBoundThermalConvectionRoot)
        pass
    def nodeAction_DeleteThermalConvectionItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.thermal.thermal_convection_dic[k]
        self.pfBoundThermalConvectionRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyThermalConvectionItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,convectionObj=currentItem.data(0,PF.objIndex)
        frm=frmThermalBase(self,convectionObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalConvection)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(convectionObj.selectId)
        self._forms.append(frm) 
        pass
    def initFaces_thermal_radiation(self):
        self.initFaces_thermal_base(self._pf.thermal.thermal_radiation_dic,
                                    self.pfBoundThermalRadiationRoot,
                                    self.actionsPFBoundThermalRadiationItem)


    def sig_selectFaceThermalRadiation(self,faceId:int,radiationObj:PF_Thermal_Radiation,faceId_old):
        if(faceId!=faceId_old and faceId_old in self._pf.thermal.thermal_radiation_dic):
            del self._pf.thermal.thermal_radiation_dic[faceId_old]
        self._pf.thermal.thermal_radiation_dic[faceId]=radiationObj
        self.initFaces_thermal_radiation()
        
        
    def nodeAction_AddThermalRadiation(self):
        self.closeFormsOpened()
        thermalObj=PF_Thermal_Radiation()
        frm=frmThermalBase(self,thermalObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalRadiation)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm)
        pass
    def nodeAction_ClearThermalRadiation(self):
        self._pf.thermal.thermal_radiation_dic={}
        self.node_clear(self.pfBoundThermalRadiationRoot)
        pass
    def nodeAction_DeleteThermalRadiationItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.thermal.thermal_radiation_dic[k]
        self.pfBoundThermalRadiationRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyThermalRadiationItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,radiationObj=currentItem.data(0,PF.objIndex)
        frm=frmThermalBase(self,radiationObj)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigSelected.connect(self.sig_selectFaceThermalRadiation)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(radiationObj.selectId)
        self._forms.append(frm)
        pass
    def initSolids_thermal_source(self):
        self.initSolids_thermal_base(self._pf.thermal.thermal_source_dic,
                                    self.pfBoundThermalSourceRoot,
                                    self.actionsPFBoundThermalSourceItem)

    def sig_selectSolidThermalSource(self,solidId:int,sourceObj:PF_Thermal_Source,solidId_old):
        if(solidId!=solidId_old and solidId_old in self._pf.thermal.thermal_source_dic):
            del self._pf.thermal.thermal_source_dic[solidId_old]
        self._pf.thermal.thermal_source_dic[solidId]=sourceObj
        self.initSolids_thermal_source()
        pass
    def nodeAction_AddThermalSource(self):
        #热源，选中的是体域
        self.closeFormsOpened()
        sourceObj=PF_Thermal_Source()
        frm=frmThermalBase(self,sourceObj,3)
        self._selectContext.sigBodyClicked.connect(frm.sig_chooseSolid)
        frm.sigSelected.connect(self.sig_selectSolidThermalSource)
        frm.sigSelectSolid.connect(self.sig_selectSolidMaual)
        frm.sigClosed.connect(self.sig_clearSolidSelected)

        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_body()
        self._forms.append(frm) 
        pass
    def nodeAction_ClearThermalSource(self):
        self._pf.thermal.thermal_source_dic={}
        self.node_clear(self.pfBoundThermalSourceRoot)
        pass
    def nodeAction_DeleteThermalSourceItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.thermal.thermal_source_dic[k]
        self.pfBoundThermalSourceRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyThermalSourceItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,sourceObj=currentItem.data(0,PF.objIndex)
        frm=frmThermalBase(self,sourceObj,3)
        self._selectContext.sigBodyClicked.connect(frm.sig_chooseSolid)
        frm.sigSelected.connect(self.sig_selectSolidThermalSource)
        frm.sigSelectSolid.connect(self.sig_selectSolidMaual)
        frm.sigClosed.connect(self.sig_clearSolidSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_body()
        self._selectContext.initSolidSelected(sourceObj.selectId)
        self._forms.append(frm)
        
       
        pass
    '''
    结构节点操作
    '''
    def sig_modifyStruct(self,eObj:PF_Struct):
        self.pfStructRoot.setData(0,PF.objIndex,eObj)
        pass
    def nodeAction_DeleteStruct(self):
        self.pfStructRoot.setHidden(True)
        self.pfBoundStructRoot.setHidden(True)
        self.resultStructRoot.setHidden(True)
        self._pf.struct.used=False
        pass
    def nodeAction_AddStruct(self):
        self.pfStructRoot.setHidden(False)
        self.pfBoundStructRoot.setHidden(False)
        self.resultStructRoot.setHidden(False)
        self.tree.setCurrentItem(self.pfStructRoot)
        self._pf.struct.used=True

    def nodeAction_StructProperties(self):
        eObj=self.pfStructRoot.data(0,PF.objIndex)
        if(eObj==None):
            eObj=PF_Struct()
        frm=frmDomainPF(self,eObj)
        frm.sigModify.connect(self.sig_modifyStruct)
        frm.move(self.topLeffPoint())
        frm.show()
        self.tree.setCurrentItem(self.pfStructRoot)
    
        pass
    def initFaces_struct_dirichlet(self):
        face_dic=self._pf.struct.struct_dirichlet_dic
        nodeRoot=self.pfBoundStructDirichletRoot
        actions=self.actionsPFBoundStructDirichletItem
        actionIndex=self.actionIndex
        self.node_clear(nodeRoot)

        for k in face_dic:
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,"Face"+str(k+1))
            itemNode.setIcon(0,treeIcons.face)
            itemNode.setData(0,PF.objIndex,(k,face_dic[k]))
            itemNode.setData(0,actionIndex,actions)

    def initFaces_struct_force(self):
        face_dic=self._pf.struct.struct_force_dic
        nodeRoot=self.pfBoundStructForceRoot
        actions=self.actionsPFBoundStructForceItem
        actionIndex=self.actionIndex
        self.node_clear(nodeRoot)
        for k in face_dic:
            itemNode=QTreeWidgetItem(nodeRoot)
            itemNode.setText(0,"Point"+str(k+1))
            itemNode.setIcon(0,treeIcons.face)
            itemNode.setData(0,PF.objIndex,(k,face_dic[k]))
            itemNode.setData(0,actionIndex,actions)
    
    def sig_selectFaceStructDirichlet(self,faceId:int,faceId_old):
        if(faceId_old in self._pf.struct.struct_dirichlet_dic):
            del self._pf.struct.struct_dirichlet_dic[faceId_old]
        self._pf.struct.struct_dirichlet_dic[faceId]=True
        self.initFaces_struct_dirichlet()
        pass
    def nodeAction_AddStructDirichlet(self):
        self.closeFormsOpened()
        frm=frmStructDirichlet(self)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigFaceSelected.connect(self.sig_selectFaceStructDirichlet)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._forms.append(frm)
        
        pass
    def nodeAction_ClearStructDirichlet(self):
        self._pf.struct.struct_dirichlet_dic={}
        self.node_clear(self.pfBoundStructDirichletRoot)
        pass
    def nodeAction_DeleteStructDirichletItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.struct.struct_dirichlet_dic[k]
        self.pfBoundStructDirichletRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyStructDirichletItem(self):
        self.closeFormsOpened()
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        frm=frmStructDirichlet(self,k)
        self._selectContext.sigFaceClicked.connect(frm.sig_chooseFace)
        frm.sigFaceSelected.connect(self.sig_selectFaceStructDirichlet)
        frm.sigClosed.connect(self.sig_clearFaceSelected)
        frm.sigSelectFace.connect(self.sig_selectFaceMaual)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_face()
        self._selectContext.initFaceSelected(k)
        self._forms.append(frm) 

    def sig_selectFaceStructForce(self,pointId:int,forceObj:PF_Struct_Force,pointId_old=-1):
        if(pointId_old in self._pf.struct.struct_force_dic):
            del self._pf.struct.struct_force_dic[pointId_old]   
        self._pf.struct.struct_force_dic[pointId]=forceObj
        self.initFaces_struct_force()
        pass
    def sig_clearPointSelected(self):
        self._meshViewer.clear_point_selected()
        self._meshViewer.end_pick()

    def nodeAction_AddStructForce(self):
        #从网格顶点中选择
        if(self.currentMesh.fileName is None):
            QtWidgets.QMessageBox.about(self,"提示","网格文件不存在，请先生成网格.")
        self.closeFormsOpened()
        self.sigActivateTab.emit(1)
        
        frm=frmStructSource(self)
        # self._selectContext.sigPointClicked.connect(frm.sig_choosePoint)
        self._meshViewer.sigPointClicked.connect(frm.sig_choosePoint)
        self._meshViewer.start_point_picker()
        frm.sigFaceSelected.connect(self.sig_selectFaceStructForce)
        frm.sigClosed.connect(self.sig_clearPointSelected)
        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_point()
        self._forms.append(frm)

    
        pass
    def nodeAction_ClearStructForce(self):
        self._pf.struct.struct_force_dic={}
        self.node_clear(self.pfBoundStructForceRoot)
        pass
    def nodeAction_DeleteStructForceItem(self):
        currentItem=self.tree.currentItem()
        k,_=currentItem.data(0,PF.objIndex)
        del self._pf.struct.struct_force_dic[k]
        self.pfBoundStructForceRoot.removeChild(currentItem)
        pass
    def nodeAction_ModifyStructForceItem(self):
        self.closeFormsOpened()
        self.sigActivateTab.emit(1)
        currentItem=self.tree.currentItem()
        k,forceObj=currentItem.data(0,PF.objIndex)
        frm=frmStructSource(self,forceObj)
        self._meshViewer.start_point_picker()
        self._meshViewer.sigPointClicked.connect(frm.sig_choosePoint)
        frm.sigFaceSelected.connect(self.sig_selectFaceStructForce)
        frm.sigClosed.connect(self.sig_clearPointSelected)
        self._meshViewer.init_point_selected(k)
        

        frm.move(self.topLeffPoint())
        frm.show()
        self._selectContext.Action_select_point()
        self._forms.append(frm)
        pass

    '''
    求解设置=时间设置
    '''
    def sig_TimeParamSet(self,timeObj:RequestParam_time):
        self.reqTimeRoot.setData(0,RequestParam.objIndex,timeObj)
        pass
    def nodeAction_TimeProperties(self):
        currentItem=self.reqTimeRoot
        timeObj=currentItem.data(0,RequestParam.objIndex)
        frm=frmTime(self,timeObj)
        frm.sigTimeSet.connect(self.sig_TimeParamSet)
        frm.move(self.topLeffPoint())
        frm.show()
        pass
    '''
    求解设置-温度
    '''
    def sig_TemperatureParamSet(self,tempObj:RequestParam_temperature):
        self.reqThermalRoot.setData(0,RequestParam.objIndex,tempObj)
        pass
    def nodeAction_TemperatureProperties(self):
        currentItem=self.reqThermalRoot
        tempObj=currentItem.data(0,RequestParam.objIndex)
        frm=frmTemperature(self,tempObj)
        frm.sigTemperatureSet.connect(self.sig_TemperatureParamSet)
        frm.move(self.topLeffPoint())
        frm.show()
        pass
    '''
    求解设置-观察域
    '''
    def sig_DomainParamSet(self,observeObj:RequestParam_domain):
        self.reqDomainRoot.setData(0,RequestParam.objIndex,observeObj)
        pass
    def nodeAction_DomainProperties(self):
        currentItem=self.reqDomainRoot
        observeObj=currentItem.data(0,RequestParam.objIndex)
        frm=frmDomain(self,observeObj)
        frm.sigDomainSet.connect(self.sig_DomainParamSet)
        frm.move(self.topLeffPoint())
        frm.show()
        pass

    '''
    求解设置-方向图节点操作
    '''
    def sig_FFRParamSet(self,ffrObj:FFR):
        self.reqFFRRoot.setData(0,FFR.objIndex,ffrObj)
    def nodeAction_FFRProperties(self):
        currentItem=self.reqFFRRoot
        ffrObj=currentItem.data(0,FFR.objIndex)
        frm=frmRequestFFR(self,1,ffrObj)
        frm.sigModify.connect(self.sig_FFRParamSet)
        frm.move(self.topLeffPoint())
        frm.show()

    '''
    求解设置-观察点节点操作
    '''
    def sig_NFParamSet(self,nfObj:NF):
        self.reqNFRoot.setData(0,NF.objIndex,nfObj)
        pass
    def nodeAction_NFProperties(self):
        currentItem=self.reqNFRoot
        nfObj=currentItem.data(0,NF.objIndex)
        frm=frmRequestNF(self,1,nfObj)
        frm.sigModify.connect(self.sig_NFParamSet)
        frm.move(self.topLeffPoint())
        frm.show()
    # def sig_AddNFRItem(self,nfrObj:NFR):
    #     if(self.nfrRoot==None):
    #         self.nfrRoot=QTreeWidgetItem(self.requestRoot)
    #         self.nfrRoot.setText(0, NFR.classTitle)
    #         self.nfrRoot.setIcon(0, treeIcons.nfr_item)
    #         self.nfrRoot.setData(0,self.actionIndex,self.actionsNFRRoot)
    #         self.nfrRoot.setExpanded(True)
    #     nItem=QTreeWidgetItem(self.nfrRoot)
    #     nItem.setText(0, nfrObj.title)
    #     nItem.setIcon(0, treeIcons.nfr)
    #     nItem.setData(0,NFR.objIndex,nfrObj)
    #     nItem.setData(0,self.actionIndex,self.actionsNFRItem)
    #     self.tree.setCurrentItem(nItem)
    #     self.nfrRoot.setExpanded(True)
    #     NFR.currentIndex=NFR.currentIndex+1
    #     pass
    # def sig_ModifyNFRItem(self,nfrObj:NFR):
    #     self.tree.currentItem().setData(0,NFR.objIndex,nfrObj)
    #     pass
    # def nodeAction_AddNFR(self):      
    #     if(not self.isLoading):
    #         self.nodeAction_AddNFRItem()
    #     pass
    # def nodeAction_AddNFRItem(self):
    #     frmNFR=frmRequestNFR(self)
    #     frmNFR.sigCreate.connect(self.sig_AddNFRItem)
    #     frmNFR.show()
    #     pass
    # def nodeAction_NFRProperties(self):
    #     nfrObj=self.tree.currentItem().data(0,NFR.objIndex)
    #     frmNFR=frmRequestNFR(self,1,nfrObj)
    #     frmNFR.sigModify.connect(self.sig_ModifyNFRItem)
    #     frmNFR.show()
        
    #     pass
    # def nodeAction_RenameNFRItem(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass
    # def nodeAction_DeleteNFRItem(self):
    #     self.nfrRoot.removeChild(self.tree.currentItem())
    #     if(self.nfrRoot.childCount()<1):
    #         self.requestRoot.removeChild(self.nfrRoot)
    #         self.nfrRoot=None
    #     pass
    # def nodeAction_ShowHideNFRItem(self):
    #     pass
    # def nodeAction_ParallelNFRItem(self):
    #     pass
    
    # def sig_addNFItem(self,nfObj:NF):
    #     if(self.nfRoot==None):
    #         self.nfRoot=QTreeWidgetItem(self.requestRoot)
    #         self.nfRoot.setText(0, tree.projctTreeNodes.nf)
    #         self.nfRoot.setIcon(0, treeIcons.nf)
    #         self.nfRoot.setData(0,self.actionIndex,self.actionsNFRoot)
    #         self.nfRoot.setExpanded(True)
    #     nItem=QTreeWidgetItem(self.nfRoot)
    #     nItem.setText(0,nfObj.title)
    #     nItem.setIcon(0,treeIcons.nf_item)
    #     nItem.setData(0,NF.objIndex,nfObj)
    #     nItem.setData(0,self.actionIndex,self.actionsNFItem)

    #     self.nfRoot.setExpanded(True)
    #     self.tree.setCurrentItem(nItem)
    #     NF.currentIndex=NF.currentIndex+1
    #     # self.NFitem.setExpanded(False)
    #     pass
    # def sig_modifyNFItem(self,nfObj:NF):
    #     self.tree.currentItem().setData(0,NF.objIndex,nfObj)

    # def nodeAction_AddNF(self):
    #     if(not self.isLoading):
    #         self.nodeAction_AddNFItem()
    #     pass
    # def nodeAction_AddNF_defalut(self):
    #     # if(self.nfRoot==None and self.nfRoot.childCount()>0):
    #     #     self.tree.setCurrentItem(self.nfRoot.child(0))
    #     #     self.nodeAction_NFProperties()
    #         # return
    #     frmNF=frmRequestNF(self,0)
    #     frmNF.sigCreate.connect(self.sig_addNFItem)
    #     frmNF.show()
    #     # self.sigActivateTab.emit(0)
        
    #     pass
    # def sig_showNF(self,nfObj:NF,color=NF.color_default):
    #     ais_shape=self._ais_shape_nfDic.get(nfObj.name)
    #     if(ais_shape is not None):
    #         api_model.removeShapes(self.modelViewer,[ais_shape])
    #     if(nfObj!=None and nfObj.show):
    #         points=[]
    #         if(nfObj.pointType==0):
    #             points=api_writer.get_nf_points(nfObj)
    #         else:
    #             points=nfObj.pointList
    #         if(nfObj.axisType==1):
    #             #将点坐标转换为局部坐标系下的坐标
    #             if(self._antenna_t!=None and self._antenna_t._face_id>0):
    #                 #已经选中面了，所以可以转换为全局坐标
    #                 center=self._antenna_t.center
    #                 normal=self._antenna_t.normal_dir
    #                 angel=self._antenna_t.offset_rotate_z
    #                 points=api_model.local_global_points(center,normal,angel,points)
    #             pass
    #         self._ais_shape_nfDic[nfObj.name]=api_model.show_nf(self.modelViewer,points,color)
    #     pass

    # def nodeAction_AddNFItem(self):
    #     frmNF=frmRequestNF(self,0)
    #     frmNF.move(self.parent.centralWidget().geometry().topLeft())
    #     frmNF.show()
    #     frmNF.sigCreate.connect(self.sig_addNFItem)
    #     frmNF.sigShowNF.connect(self.sig_showNF)
    #     self.sigActivateTab.emit(0)
        
    # def nodeAction_NFProperties(self):

    #     nfObj=self.tree.currentItem().data(0,NF.objIndex)
    #     frmNF=frmRequestNF(self,1,nfObj)
    #     frmNF.move(self.parent.centralWidget().geometry().topLeft())
        
        
    #     frmNF.show()
    #     frmNF.sigModify.connect(self.sig_modifyNFItem)
    #     frmNF.sigShowNF.connect(self.sig_showNF)
    #     self.sig_showNF(nfObj,NF.color_highlight) #需要高亮显示当前的观察点
    #     self.sigActivateTab.emit(0)

        
    #     pass
    # def nodeAction_RenameNFItem(self):
    #     self.nodeAction_Rename(self.tree.currentItem())
    #     pass
    # def nodeAction_DeleteNFItem(self):
    #     nfObj=self.tree.currentItem().data(0,NF.objIndex)
    #     nfObj.show=False
    #     self.sig_showNF(nfObj)
    #     self.nfRoot.removeChild(self.tree.currentItem())
    #     if(self.nfRoot.childCount()<1):
    #         self.requestRoot.removeChild(self.nfRoot)
    #         self.nfRoot=None
    #     pass
    # def nodeAction_ShowHideNFItem(self):
    #     nfObj:NF=self.tree.currentItem().data(0,NF.objIndex)
    #     # if(not hasattr(nfObj,"show")):
    #     #     nfObj.show=True
    #     nfObj.show=not nfObj.show
    #     self.sig_showNF(nfObj)
    #     self.tree.currentItem().setData(0,NF.objIndex,nfObj)
        
        
        
    #     pass


    '''
    EMI节点
    '''
    def ndoeAction_EMIProperties(self):
        QtWidgets.QMessageBox.about(self,"EMI","EMI节点用于标识需要求解EMI类型的计算对象，可以右键删除")
        pass
    def nodeAction_AddEMI(self):
        if(self.emiRoot!=None):
            return
        self.emiRoot=QTreeWidgetItem(self.requestRoot)
        self.emiRoot.setText(0, tree.projctTreeNodes.emi)
        self.emiRoot.setIcon(0, treeIcons.emi)
        self.emiRoot.setData(0,self.actionIndex,self.actionsEMIRoot)
        self.emiRoot.setExpanded(True)
        pass
    def nodeAction_DeleteEMI(self):
        self.requestRoot.removeChild(self.emiRoot)
        pass

    def nodeAction_InitResults(self):
        '''运算完成后，根据计算对象初始化后处理节点
        (1)初始化FFR
        (2)初始化NFR
        (3)初始化NF
        '''
        self.initFreqList()
        self.initTxList()
        self.node_clear(self.resultRoot)
        self.currentsRoot = QTreeWidgetItem(self.resultRoot)
        self.currentsRoot.setText(0, tree.projctTreeNodes.current)
        self.currentsRoot.setIcon(0, treeIcons.currents)
        self.currentsRoot.setData(0,self.actionIndex,self.actionsCurrentRoot)
        self.currentsRoot.setExpanded(True)

        # if(self.ffrRoot!=None and self.ffrRoot.childCount()>0):
        #     self.ffrRoot_result=QTreeWidgetItem(self.resultRoot)
        #     self.ffrRoot_result.setText(0, FFR.classTitle)
        #     self.ffrRoot_result.setIcon(0, treeIcons.r_ffr)
        #     # self.ffrRoot_result.setData(0,self.actionIndex,self.actionsFFRRoot)
        #     self.ffrRoot_result.setExpanded(True)

        #     for i in range(self.ffrRoot.childCount()):
        #         item=self.ffrRoot.child(i)
        #         nItem=QTreeWidgetItem(self.ffrRoot_result)
        #         nItem.setText(0, item.text(0))
        #         nItem.setIcon(0, treeIcons.r_ffr_item)
        #         nItem.setData(0,FFR.objIndex,item.data(0,FFR.objIndex))
        #         # nItem.setData(0,self.actionIndex,self.actionsFFRItem)
        # if(self.nfrRoot!=None and self.nfrRoot.childCount()>0):
        #     self.nfrRoot_result=QTreeWidgetItem(self.resultRoot)
        #     self.nfrRoot_result.setText(0, NFR.classTitle)
        #     self.nfrRoot_result.setIcon(0, treeIcons.r_nfr)
        #     # self.ffrRoot_result.setData(0,self.actionIndex,self.actionsFFRRoot)
        #     self.nfrRoot_result.setExpanded(True)

        #     for i in range(self.nfrRoot.childCount()):
        #         item=self.nfrRoot.child(i)
        #         nItem=QTreeWidgetItem(self.nfrRoot_result)
        #         nItem.setText(0, item.text(0))
        #         nItem.setIcon(0, treeIcons.r_nfr_item)
        #         nItem.setData(0,NFR.objIndex,item.data(0,NFR.objIndex))
        #         # nItem.setData(0,self.actionIndex,self.actionsFFRItem)

        if(self.nfRoot!=None and self.nfRoot.childCount()>0):
            self.nfRoot_result=QTreeWidgetItem(self.resultRoot)
            self.nfRoot_result.setText(0, tree.projctTreeNodes.nf)
            self.nfRoot_result.setIcon(0, treeIcons.r_nf)
            # self.ffrRoot_result.setData(0,self.actionIndex,self.actionsFFRRoot)
            self.nfRoot_result.setExpanded(True)

            for i in range(self.nfRoot.childCount()):
                item=self.nfRoot.child(i)
                nf=item.data(0,NF.objIndex)
                nItem=QTreeWidgetItem(self.nfRoot_result)
                nItem.setText(0, item.text(0))
                nItem.setIcon(0, treeIcons.r_nf_item)
                nItem.setData(0,NF.objIndex,nf)


                nItem_E=QTreeWidgetItem(nItem)
                nItem_E.setText(0, "电场")
                nItem_E.setIcon(0, treeIcons.r_nf_item)
                nItem_E.setData(0,NF.objIndex,item.data(0,NF.objIndex))
                
                nItem_H=QTreeWidgetItem(nItem)
                nItem_H.setText(0, "磁场")
                nItem_H.setIcon(0, treeIcons.r_nf_item)
                nItem_H.setData(0,NF.objIndex,item.data(0,NF.objIndex))
                nItem.setExpanded(True)
                nItem.setData(0,self.actionIndex,self.actionsFFRItem)

                # nItem_extend=QTreeWidgetItem(self.extendNFRoot)
                # nItem_extend.setText(0, item.text(0))
                # nItem_extend.setIcon(0, treeIcons.r_nf_item)
                # nItem_extend.setData(0,NF.objIndex,nf)

        # if(self._antenna_r.itemList_local!=None and len(self._antenna_r.itemList_global)>0):
        #     if(self.emiRoot_result!=None):
        #         return
        self.emiRoot_result=QTreeWidgetItem(self.resultRoot)
        self.emiRoot_result.setText(0, tree.projctTreeNodes.emi)
        self.emiRoot_result.setIcon(0, treeIcons.emi)
        self.emiRoot_result.setExpanded(True)
    
        
        pass
   
    
    def refreshResults(self,isRefresh=False,
                       txChanged=False,
                       freqChanged=False,
                       vTypeChanged=False,
                       valueChanged=False,
                       surfaceChanged=False,
                       positionChanged=False,
                       xAxisChanged=False,
                       dbChanged=False):
        ''' 
        刷新结果显示
        '''
       


        if(self._postFilter.data_now==PostFilter.dataKey_currents):
            self.nodeAction_DisplayCurrents(isRefresh=isRefresh,txChanged=txChanged,freqChanged=freqChanged)
        elif(self._postFilter.data_now==PostFilter.dataKey_nf_E):
            self.nodeAction_DisplayNF(isRefresh=isRefresh,
                                      txChanged=txChanged,
                                      freqChanged=freqChanged,
                                      vTypeChanged=vTypeChanged,
                                      valueChanged=valueChanged,
                                      surfaceChanged=surfaceChanged,
                                      positionChanged=positionChanged,
                                      xAxisChanged=xAxisChanged
                                      )
        elif(self._postFilter.data_now==PostFilter.dataKey_nf_H):
            self.nodeAction_DisplayNF(isRefresh=isRefresh,
                                      txChanged=txChanged,
                                      freqChanged=freqChanged,
                                      vTypeChanged=vTypeChanged,
                                      valueChanged=valueChanged,
                                      surfaceChanged=surfaceChanged,
                                      positionChanged=positionChanged
                                      )
        elif(self._postFilter.data_now==PostFilter.dataKey_emi):
            self.nodeAction_DisplayEMI(isRefresh=isRefresh,
                                       txChanged=txChanged,
                                       freqChanged=freqChanged,
                                       vTypeChanged=vTypeChanged,
                                       valueChanged=valueChanged,
                                       dbChanged=dbChanged)
    def refreshResults_extend(self,isRefresh=False,
                          txChanged=False,
                            freqChanged=False,
                            vTypeChanged=False,
                            valueChanged=False,
                            surfaceChanged=False,
                            positionChanged=False,
                            xAxisChanged=False,
                            dbChanged=False):
        '''
        扩展数据导入时，刷新结果显示
        '''
        if(self._postFilter_extend.data_now==PostFilter.dataKey_nf_E):
            self.nodeAction_DisplayNF_extend(isRefresh=isRefresh,
                                             freqChanged=freqChanged,
                                             vTypeChanged=vTypeChanged,
                                             valueChanged=valueChanged,
                                             surfaceChanged=surfaceChanged,
                                             positionChanged=positionChanged,
                                             xAxisChanged=xAxisChanged)
        elif(self._postFilter_extend.data_now==PostFilter.dataKey_emi):
            self.nodeAction_DisplayEMI_extend(isRefresh=isRefresh,
                                       freqChanged=freqChanged,
                                       vTypeChanged=vTypeChanged,
                                       valueChanged=valueChanged,
                                       dbChanged=dbChanged)
        pass
    
    def initFreqList(self):
        #初始化频率列表
        freqObj:Frequency=self.frequencyRoot.data(0,Frequency.objIndex)
        if(freqObj is None):
            return
        freqList:list[str]=[]
        if(hasattr(freqObj,"freqType") and freqObj.freqType==1):
            #离散频点
            freqList=freqObj.discreteList.copy()
        else:
            thresold=1e-7
            x=float(freqObj.start)
            while x-float(freqObj.end)<thresold:
                freqList.append('{:.2e}'.format(x))
                x=x+float(freqObj.increment)
                pass
        # self.freqIndex=0
        self.sigFreq.emit(freqList)
        pass
    # def initFreqList_extend(self,freqList):
    #     '''
    #     根据导入的数据生成频率列表
    #     '''
    #     self.sigFreq.emit(freqList)
    #     pass
    # def initTxList_extend(self):
    #     '''
    #     扩展数据导入查看时，没有阵元可以切换
    #     '''
    #     self.sigTx.emit([])
    #     pass
    def initTxList(self):
        '''初始化阵元列表
        '''
        txList:list[str]=[]
        txLen=len(self._antenna_t.itemList_local)
        if(self._antenna_t.antennaType==1):
            txLen=len(self._antenna_t.itemList_discrete)
        for i in range(1,txLen+1):
            txList.append(str(i))
        self.sigTx.emit(txList)
        pass

    def initChooseList_emi(self,checkedText=""):
        '''
        初始化物理量选择列表-emi
        '''
        strList=[]
        for k in self._postFilter.emi.valueKeys:
            strList.append(k)
        vTypeList=self._postFilter.emi.vTypeList
        checkedKeys=self._postFilter.emi.checkedKeys
        singleChecked=self._postFilter.emi.singleChecked
        self.sigChooseList.emit(vTypeList,checkedKeys,singleChecked)
        pass
 
    def intVTypeList(self,vTypeList):
        '''初始化物理量选择列表
        '''
        self.sigVTypeList.emit(vTypeList)
        pass
    def initValueButtons(self,checkedKeys):
        self.sigValueButtons.emit(checkedKeys)




    def freqChanged(self,freqIndex):
        if(not self._is_extend):
            self._postFilter.freqIndex=freqIndex
            self.refreshResults(isRefresh=True,freqChanged=True)
        else:
            self._postFilter_extend.freqIndex=freqIndex
            self.refreshResults_extend(isRefresh=True,freqChanged=True)

    def valueBtnChanged(self,btnText:str):
        # self.paramResults["valueText"]=btnText
        # # PostFilter.checkedValue=btnText

        # if(self._postFilter.filter_now.checkedKeys.get(btnText)!=None):
        #     PostFilter.checkedKeys[btnText]=checked
        if(not self._is_extend):
            dbEnable=False

            # postFilter_now=self._postFilter_now
            db_convertKeys=self._postFilter.filter_now.db_ConvertKeys
            singleChecked=self._postFilter.filter_now.singleChecked
        
            if(singleChecked):#当前为单选模式，则需要将其他的取消

                for k in self._postFilter.filter_now.checkedKeys:
                    if(k!=btnText):
                        self._postFilter.filter_now.checkedKeys[k]=False
                    else:
                        self._postFilter.filter_now.checkedKeys[k]=True
                if(btnText in db_convertKeys):#当前的按钮可以db值转换
                    dbEnable=True
            else:
                self._postFilter.filter_now.checkedKeys_multi[btnText]=not self._postFilter.filter_now.checkedKeys_multi[btnText]
                self._postFilter.filter_now.headers[btnText]=not self._postFilter.filter_now.headers[btnText]
                #遍历当前显示的列，看是否有包含在可提供db值的列中，有则允许执行db值转换
                for k,v in self._postFilter.filter_now.headers.items():
                    if(v and k in db_convertKeys):
                        dbEnable=True
                        break

            #需要处理db按钮是否可以响应
            self.sigValueButton_convert_disabled.emit(dbEnable)

            self.refreshResults(isRefresh=True,valueChanged=True)
        else:
            dbEnable=False

            # postFilter_now=self._postFilter_now
            db_convertKeys=self._postFilter_extend.filter_now.db_ConvertKeys
            singleChecked=self._postFilter_extend.filter_now.singleChecked
        
            if(singleChecked):#当前为单选模式，则需要将其他的取消

                for k in self._postFilter_extend.filter_now.checkedKeys:
                    if(k!=btnText):
                        self._postFilter_extend.filter_now.checkedKeys[k]=False
                    else:
                        self._postFilter_extend.filter_now.checkedKeys[k]=True
                if(btnText in db_convertKeys):#当前的按钮可以db值转换
                    dbEnable=True
            else:
                self._postFilter_extend.filter_now.checkedKeys_multi[btnText]=not self._postFilter_extend.filter_now.checkedKeys_multi[btnText]
                self._postFilter_extend.filter_now.headers[btnText]=not self._postFilter_extend.filter_now.headers[btnText]
                #遍历当前显示的列，看是否有包含在可提供db值的列中，有则允许执行db值转换
                for k,v in self._postFilter_extend.filter_now.headers.items():
                    if(v and k in db_convertKeys):
                        dbEnable=True
                        break

            #需要处理db按钮是否可以响应
            self.sigValueButton_convert_disabled.emit(dbEnable)

            self.refreshResults_extend(isRefresh=True,valueChanged=True)


        pass
    def valueConvertBtnExchanged(self,btnText:str):
        if(not self._is_extend):
      
            self._postFilter.filter_now.db_Convert=not self._postFilter.filter_now.db_Convert
            self.refreshResults(isRefresh=True,dbChanged=True)
        else:
            self._postFilter_extend.filter_now.db_Convert=not self._postFilter_extend.filter_now.db_Convert
            self.refreshResults_extend(isRefresh=True,dbChanged=True)

        pass
    def xAxisChanged(self,xAxisIndex:str):
        #选择坐标轴，至少需要选中一个，且为单选
        # print("axis-",btnText)
        # self.paramResults["valueAxis"]=btnText
        # PostFilter.checkedAxis=btnText
        # QtWidgets.QMessageBox.about(self,"axis index","axis index is:"+str(xAxisIndex))
        # self.refreshResults(filterChanged=True)
        if(xAxisIndex<0):
            return
        if(not self._is_extend):
            self._postFilter.xAxisIndex=xAxisIndex
            self.refreshResults(isRefresh=True,xAxisChanged=True)
        else:
            self._postFilter_extend.xAxisIndex=xAxisIndex
            self.refreshResults_extend(isRefresh=True,xAxisChanged=True)
        
        pass
    def txChanged(self,txIndex):
        # self.paramResults["txIndex"]=txIndex
        # PostFilter.txIndex=txIndex

        self._postFilter.txIndex=txIndex
        self.refreshResults(isRefresh=True,txChanged=True)
        pass
    def vTypeChanged(self,vType):
        # self.paramResults["vTypeIndex"]=vType
        # PostFilter.vTypeIndex=vType
        if(not self._is_extend):
            if(self._postFilter.vTypeIndex!=vType):
                self._postFilter.vTypeIndex=vType
                self.refreshResults(isRefresh=True,vTypeChanged=True)
        else:
            if(self._postFilter_extend.vTypeIndex!=vType):
                self._postFilter_extend.vTypeIndex=vType
                self.refreshResults_extend(isRefresh=True,vTypeChanged=True)
        pass

    def surfaceChanged(self,surfaceIndex):
        #切换选中面
        # QtWidgets.QMessageBox.about(self,"surface index","surface index is:"+str(surfaceIndex))
        if(not self._is_extend):
            self._postFilter.filter_now.surfaceIndex=surfaceIndex
            
            self.refreshResults(isRefresh=True,surfaceChanged=True)
        else:
            self._postFilter_extend.filter_now.surfaceIndex=surfaceIndex
            self.refreshResults_extend(isRefresh=True,surfaceChanged=True)
        pass
    def positionChanged(self,pIndex):
        #切换选中的物理量
        # QtWidgets.QMessageBox.about(self,"position index","position index is:"+str(pIndex))
        if(not self._is_extend):
            self._postFilter.filter_now.positionIndex=pIndex
            self.refreshResults(isRefresh=True,positionChanged=True)
        else:
            self._postFilter_extend.filter_now.positionIndex=pIndex
            self.refreshResults_extend(isRefresh=True,positionChanged=True)
        pass
    def setScalarColor(self):
        minV=0
        maxV=0
        numberOfColors=256
        postRender=self._postRender
        if(self._is_extend):
            postRender=self._postRender_extend
        if(postRender.render_now!=None):
            minV=postRender.render_now.min_now
            maxV=postRender.render_now.max_now
            numberOfColors=postRender.render_now.numberOfColors
        frm_scalar=frmScalar(self,minV,maxV,numberOfColors)
        frm_scalar.move(self.parent.centralWidget().geometry().topLeft())
        frm_scalar.show()
        frm_scalar.sigSetRange.connect(self.sig_setScalarRange)
        frm_scalar.sigRangeAuto.connect(self.sig_setScalarRangeAuto)
    def setFaceSelect(self,faceId:int,isSelected:bool):
        '''
        设置选中的面
        '''
        return
        if(self.currentModel==None):
            return
        if(not hasattr(self.currentModel,"face_selected")):
            self.currentModel.face_selected={}
        for k in self.currentModel.face_selected:
            if(isSelected and k!=faceId):
                self.currentModel.face_selected[k]=False
        self.currentModel.face_selected[faceId]=isSelected
        if(isSelected and self.faceRoot.childCount()>=faceId):
            self.tree.clearSelection()

            self.tree.setCurrentItem(self.faceRoot.child(faceId))
            self.tree.currentItem().setSelected(True)
            self.tree.setFocus()
            

    def sig_setScalarRange(self,min:float,max:float,numberOfColors:int):
        '''设置颜色范围，需要设置颜色条以及3维图形的range
        '''
        # print("range",min,max)
        postRender=self._postRender
        if(self._is_extend):
            postRender=self._postRender_extend
        if(postRender.render_now!=None):
            postRender.render_now.min_now=min
            postRender.render_now.max_now=max
            postRender.render_now.numberOfColors=numberOfColors
            postRender.render_now.scalarType=1
            api_vtk.scalar_range_map(postRender.render_now.actorMap,min,max,numberOfColors)
            api_vtk.scalar_range_bar(postRender.render_now.actorBar,min,max)

            self._vtkViewer3d.Render()
            pass
        pass
    def sig_setScalarRangeAuto(self,numberOfColors:int=256):

        postRender=self._postRender
        if(self._is_extend):
            postRender=self._postRender_extend
        if(postRender.render_now!=None):
            postRender.render_now.numberOfColors=numberOfColors
            postRender.render_now.scalarType=0
            minV=postRender.render_now.minV
            maxV=postRender.render_now.maxV
            api_vtk.scalar_range_map(postRender.render_now.actorMap,minV,maxV,numberOfColors)
            api_vtk.scalar_range_bar(postRender.render_now.actorBar,minV,maxV)
            self._vtkViewer3d.Render()
            pass
    

    def nodeAction_DisplayCurrents(self,isRefresh=False,txChanged=False,freqChanged=False):
        '''显示表面电流
        '''
        try:
            # PostFilter.checkedKeys=PostFilter.currents.checkedKeys #选中的物理量 
            self._is_extend=False
            self.sigTxEnable.emit(True)
            self.sigActivateToolbar.emit(3)
            
            self._postFilter.setFilterCurrents()
            self._postData.setDataCurrents()
            self._postRender.setRenderCurrents()
            
            
            if not isRefresh:
                self._postFilter.vTypeIndex=0
                self.sigVTypeList.emit(self._postFilter.filter_now.vTypeList)
                self.sigValueButtons.emit(self._postFilter.filter_now.checkedKeys,
                                          True,
                                          self._postFilter.filter_now.db_ConvertKeys)

                # self.sigChooseAxis.emit([])
                self.sigChooseSurface.emit([],False)
                self.sigPosition.emit([])
            self.sigValueButton_convert_checked.emit(self._postFilter.filter_now.db_Convert)#同步db按钮的状态
            
            txIndex=self._postFilter.txIndex #阵元编号
            freqIndex=self._postFilter.freqIndex #频率编号
            dataCurrents=self._postData.currents.dataResults

            valueText=""
            valueIndex=-1
            for k,v in self._postFilter.currents.checkedKeys.items():
                if(v):
                    valueText=k
                    valueIndex=self._postFilter.currents.valueKeys[k]
                    break
            
            dataRender=None
            if(dataCurrents.get(txIndex+1) is not None):
                #已经包含该阵元的电流数据
                dataRender=dataCurrents[txIndex+1]
            else:
                #需要读取数据
                fname=self.currentProject.getCurrentsFileName(txIndex+1)
                if(not os.path.exists(fname)):
                    QtWidgets.QMessageBox.about(self,"表面电流","表面电流数据不存在，请检查."+fname)
                    return
    
                dataRender=api_reader.read_currents_sbr(fname)
                dataCurrents[txIndex+1]=dataRender
            # self.resultsCurrentsList=api_reader.read_currents(fname1)
           
            pointList=[]
            minV=1e9
            maxV=-1e9
            dataItem=dataRender[freqIndex]
            valueList=dataItem[0]
            dbConvert=self._postFilter.filter_now.db_Convert #是否需要转换为db值
            if(valueText not in self._postFilter.filter_now.db_ConvertKeys):    
                dbConvert=False #当前物理量不需要转换为db值

            for item in valueList:
                v=item[valueIndex]
                if(dbConvert):
                    if(v<=0):
                        v=self._postFilter.filter_now.dbMin
                    else:
                        v=20*math.log10(v)
                pointList.append((item[1],item[2],item[3],v))
                if(v<minV):
                    minV=v
                if(v>maxV):
                    maxV=v
            cells=dataItem[1]
            
            
            barTitle=valueText
            if(dbConvert):
                valueText=valueText+PostFilter.dbTitle
            if(self._postFilter.currents.barKeys.get(valueText)!=None):
                barTitle=self._postFilter.currents.barKeys[valueText]

            mapActor=api_vtk.currents_surface(pointList,cells,minV,maxV)
            barActor=api_vtk.scalar_actor(minV,maxV,barTitle)

            
            
            # actor=api_vtk.points_vertex(pointList,min,max)
            self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            self._vtkViewer3d.display_actor(mapActor)
            self._vtkViewer3d.display_actor(barActor)
            if(not isRefresh):
                self._vtkViewer3d.reset_camera()
          
            # self._vtkViewer3d.display_currents(mapActor,barActor)
            self.sigActivateTab.emit(2)

            self._postData.data_now.points_now=pointList
            self._postData.data_now.headers_now=["X(m)","Y(m)","Z(m)",barTitle]

            self._postRender.render_now.actorMap=mapActor
            self._postRender.render_now.actorBar=barActor
            self._postRender.render_now.show_surface=True
            self._postRender.render_now.show_points=False
            self._postRender.render_now.minV=minV
            self._postRender.render_now.maxV=maxV
            self._postRender.render_now.min_now=minV
            self._postRender.render_now.max_now=maxV
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"currents render","read the currents result error:"+str(e))
            traceback.print_exc()


        # QtWidgets.QMessageBox.about(self,"currents",fname)



        pass
 
   
    def nodeAction_DisplayEMI(self,isRefresh=False,
                              txChanged=False,
                              freqChanged=False,
                              vTypeChanged=False,
                              valueChanged=False,
                              dbChanged=False):
        '''
        显示EMI结果
        '''
        self._is_extend=False
        self.sigTxEnable.emit(True)
        self.sigActivateToolbar.emit(3)
        self._postFilter.setFilterEmi()
        self._postData.setDataEmi()
        self._postRender.setRenderEmi()
        txIndex=self._postFilter.txIndex #阵元编号
        freqIndex=self._postFilter.freqIndex #频率编号
        vType=self._postFilter.vTypeIndex #物理量类型
        tableKey="emi"
        dataEMI=self._postData.emi.dataResults


        if not isRefresh:
            vType=0
            self._postFilter.vTypeIndex=0   
            self.sigVTypeList.emit(self._postFilter.filter_now.vTypeList)
            # self.sigChooseAxis.emit([])
            self.sigChooseSurface.emit([],False)
            self.sigPosition.emit([])
            if(vType==0):
                self.sigValueButtons.emit(self._postFilter.filter_now.checkedKeys_multi,
                                          False,
                                          self._postFilter.filter_now.db_ConvertKeys)
            if(vType==1):
                self.sigValueButtons.emit(self._postFilter.filter_now.checkedKeys,
                                          True,
                                          self._postFilter.filter_now.db_ConvertKeys)

        if vTypeChanged:
            if(vType==0):
                self.sigValueButtons.emit(self._postFilter.filter_now.checkedKeys_multi,
                                          False,
                                          self._postFilter.filter_now.db_ConvertKeys)
            if(vType==1):
                self.sigValueButtons.emit(self._postFilter.filter_now.checkedKeys,
                                          True,
                                          self._postFilter.filter_now.db_ConvertKeys)
            pass

        self.sigValueButton_convert_checked.emit(self._postFilter.filter_now.db_Convert)#同步db按钮的状态

       
        if(dataEMI.get(txIndex+1) is not None):
            #已经包含该阵元的电流数据
            dataRender=dataEMI[txIndex+1]
        else:
            #需要读取数据
            fname=self.currentProject.getEMIFileName(txIndex+1)
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"电磁干扰","电磁干扰结果数据不存在，请检查."+fname)
                return

            dataRender,freqList=api_reader.read_nf_sbr_Power(fname)
            dataEMI[txIndex+1]=dataRender
        dataItem=dataRender[freqIndex]
        dbConvert=self._postFilter.filter_now.db_Convert
        if(vType==0):
            header_title=self._postFilter.filter_now.barKeys
            self._postFilter.filter_now.singleChecked=False
            #当为db时，需要转换数据，转换标题
            v_convert_index_list=[]
            v_convert_header_list=[]
            power_index=-1
            if(dbConvert):
                #先找到需要转换至的列索引
                v_convert_index_list=[]
                for k,v in self._postFilter.filter_now.checkedKeys_multi.items():
                    if(v and k in self._postFilter.filter_now.db_ConvertKeys):
                        v_convert_index_list.append(self._postFilter.filter_now.valueKeys[k])
                        v_convert_header_list.append(k)
                        if(k==PostFilter.db_PowerKey):
                            power_index=self._postFilter.filter_now.valueKeys[k]
                    
                    
                pass
            if(len(v_convert_index_list)>0):
                #功率的换算公式10*log10需要单独处理
                dataItem_db=[]
                for i in range(len(dataItem)):
                    dItem=dataItem[i]
                    temp_list = list(dItem)
                    for i in range(len(v_convert_index_list)):
                        v_temp=temp_list[v_convert_index_list[i]]
                        if(v_temp<=0):
                            temp_list[v_convert_index_list[i]]=self._postFilter.filter_now.dbMin
                        else:
                            if(v_convert_index_list[i]==power_index):
                                temp_list[v_convert_index_list[i]]=round(10*math.log10(v_temp),PostFilter.dotPrecision)
                            else:
                                temp_list[v_convert_index_list[i]]=round(20*math.log10(v_temp),PostFilter.dotPrecision)
                    dataItem_db.append(tuple(temp_list))
                # print(dataItem[0])
                header_title=header_title.copy()
            
                if(len(v_convert_header_list)>0):
                    for c_k in v_convert_header_list:  
                        header_title[c_k]=header_title[c_k+PostFilter.dbTitle]
                self.renderTable(self._postFilter.filter_now.headers,dataItem_db,header_title)
                pass
            else:

                self.renderTable(self._postFilter.filter_now.headers,dataItem,header_title)
            self.sigActivateTab.emit(4)
        elif(vType==1):
            self._postFilter.filter_now.singleChecked=True
            minV=1e9
            maxV=-1e9
            valueList=dataItem
            pointList=[]
            xNum=len(list(set(t[0] for t in self._antenna_r.itemList_local)))
            yNum=len(list(set(t[1] for t in self._antenna_r.itemList_local)))
            valueIndex=-1
            valueText=""
            barTitle=""
            for k,v in self._postFilter.filter_now.checkedKeys.items():
                if(v):
                    valueIndex=self._postFilter.filter_now.valueKeys[k]
                    valueText=k
                    barTitle=k
                    break
            if(valueText not in self._postFilter.filter_now.db_ConvertKeys):
                dbConvert=False
            if(self._postFilter.filter_now.barKeys.get(valueText)!=None):
                barTitle=self._postFilter.filter_now.barKeys[valueText]
            if(dbConvert):
                barTitle=self._postFilter.filter_now.barKeys[valueText+PostFilter.dbTitle]
            
            for item in valueList:
                v=item[valueIndex]
                if(dbConvert):
                    if(v<=0):
                        v=self._postFilter.filter_now.dbMin
                    else:
                        if(valueText==PostFilter.db_PowerKey):
                            v=10*math.log10(v)
                        else:
                            v=20*math.log10(v)
                pointList.append((item[1],item[2],item[3],v))
                if(v<minV):
                    minV=v
                if(v>maxV):
                    maxV=v


            mapActor=api_vtk.cloud_map(pointList,_xNum=xNum,_yNum=yNum)
            modelActor=None
            arrayActor_r=None
            barActor=None
    
            
       
            
            
            if(not valueChanged and not dbChanged):
                #首次加载，不是切换按钮时，切换按钮时不重置相机
                
                if(not os.path.exists(self.currentModel.geoFile)):
                    api_model.exportModel(self.currentModel.shape,self.currentModel.geoFile)
                self._vtkViewer3d.clear()
                modelActor=api_vtk.stl_model(fname=self.currentModel.geoFile,opacity=1)
                # self._vtkViewer3d.display_model(modeActor)
                self._vtkViewer3d.display_actor(modelActor,False)
                self._vtkViewer3d.reset_camera()
            self._vtkViewer3d.clear_actor_custom()
            barActor=api_vtk.scalar_actor(minV,maxV,barTitle)
            self._vtkViewer3d.display_actor(mapActor)
            self._vtkViewer3d.display_actor(barActor)
            if(self._antenna_r._show_array and os.path.exists(self._antenna_r.file_array_model)):
                arrayActor_r=api_vtk.stl_model(self._antenna_r.file_array_model)
                self._vtkViewer3d.display_actor(arrayActor_r)

            self.sigActivateTab.emit(2)
            points_now=[tup[:4] for tup in pointList]
            #每个点*1000
            points_now=[(tup[0]*1000,tup[1]*1000,tup[2]*1000,tup[3]) for tup in points_now]
            self._postData.data_now.points_now=points_now
            self._postData.data_now.headers_now=["X(m)","Y(m)","Z(m)",barTitle]

            self._postRender.render_now.actorArray_RX=arrayActor_r
            self._postRender.render_now.actorModel=modelActor
            self._postRender.render_now.actorMap=mapActor
            self._postRender.render_now.actorBar=barActor
            self._postRender.render_now.show_surface=True
            self._postRender.render_now.show_points=False

            self._postRender.render_now.minV=minV
            self._postRender.render_now.maxV=maxV
            self._postRender.render_now.min_now=minV
            self._postRender.render_now.max_now=maxV
            
            pass
       

        pass
    
    def nodeAction_DisplayNF(self,isRefresh=False,
                             txChanged=False,
                             freqChanged=False,
                             vTypeChanged=False,
                             valueChanged=False,
                             surfaceChanged=False,
                             positionChanged=False,
                             xAxisChanged=False):
        '''
        电磁环境渲染
        '''
        try:
            #支持多个观察点，当前只支持一个观察点，需要根据nf的点数量来对数据切片处理

            nfItem=self.tree.currentItem()
            nfObj:NF=nfItem.data(0,NF.objIndex)
            if(nfObj.point_slice_start<0):#尚未完成切片处理
                self._cLogger.error("显示电磁环境nf数据切片未初始化")
                pass
            self._is_extend=False
            self.sigTxEnable.emit(True)
            self.sigActivateToolbar.emit(3)
            currentText=self.tree.currentItem().text(0)
            if(currentText==PostFilter.resultKey_E):#首次加载时一定是currenttext为E或H
                self._postFilter.setFilterNF_E()
                self._postData.setDataNF_E()
                self._postRender.setRenderNF_E()
                self._postFilter.filter_now.dataObject=nfObj
            elif(currentText==PostFilter.resultKey_H):
                self._postFilter.setFilterNF_H()
                self._postData.setDataNF_H()
                self._postRender.setRenderNF_H()
                self._postFilter.filter_now.dataObject=nfObj
            else:
                #重置nf对象为上次保留的数据
                nfObj=self._postFilter.filter_now.dataObject
                self._cLogger.debug("当前节点是"+currentText+"不设置类型")
            if(self._postFilter.filter_now==None):
                self._cLogger.debug("当前数据类型为空")
                QtWidgets.QMessageBox.warning(self,"电磁环境","请点击电场/磁场节点查看数据")
                return
            postTypeName=self._postFilter.filter_now.typeName #不再使用currentText，而是使用当前的数据类型名称

            if(postTypeName!=PostFilter.dataKey_nf_E 
                and postTypeName!=PostFilter.dataKey_nf_H):
                self._cLogger.debug("当前数据类型不是电场或磁场:"+postTypeName)
                QtWidgets.QMessageBox.warning(self,"电磁环境","请点击电场/磁场节点查看数据")
                return
        
            
            txIndex=self._postFilter.txIndex #阵元编号
            freqIndex=self._postFilter.freqIndex#频率编号
            vType=self._postFilter.vTypeIndex #物理量类型
            xAxisIndex=self._postFilter.xAxisIndex #坐标轴
            # checkedAxis=self._postFilter.xyz.checkedKeys
            db_convertKeys=self._postFilter.filter_now.db_ConvertKeys
            checkedKeys=self._postFilter.filter_now.checkedKeys
            checkedKeys_multi=self._postFilter.filter_now.checkedKeys_multi

            

            if(not isRefresh):#首次加载，并非过滤条件改变时加载
                vType=0
                self._postFilter.vTypeIndex=0
                vTypeList=self._postFilter.filter_now.vTypeList.copy()
                if(nfObj.pointType==1):
                    vTypeList=vTypeList[:1]
                self.sigVTypeList.emit(vTypeList)
                
                
                if(vType==0):
                    self.sigValueButtons.emit(checkedKeys_multi,False,db_convertKeys)
                    self.sigChooseSurface.emit([],False)
                    self.sigPosition.emit([])
                    # self.sigChooseAxis.emit({},False)
                if(vType==1):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)
                    # self.sigChooseSurface.emit([],[])
                    # self.sigChooseAxis.emit(checkedAxis,True)
                if(vType==2):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)
                    # self.sigChooseAxis.emit({},False)
            if(vTypeChanged):
                # self._postFilter.filter_now.db_Convert=False
                if(vType==0):
                    self.sigValueButtons.emit(checkedKeys_multi,False,db_convertKeys)
                    self.sigChooseSurface.emit([],False)
                    self.sigPosition.emit([])
                    # self.sigChooseAxis.emit({},False)
                if(vType==1):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)
                    # self.sigChooseSurface.emit([],[])
                    # self.sigChooseAxis.emit(checkedAxis,True)
                if(vType==2):
                    self.sigValueButtons.emit(checkedKeys,True,db_convertKeys)
                    # self.sigChooseAxis.emit({},False)
            self.sigValueButton_convert_checked.emit(self._postFilter.filter_now.db_Convert)

            
            dataRender=[]
            dataItem=[]

            header_dic=None
            header_title=None #物理量映射的列标题，需要转换原列名为物理量的为定制列标题
            
            if(postTypeName==PostFilter.dataKey_nf_E):
                self._postFilter.setFilterNF_E()
                header_dic=self._postFilter.nf_E.headers
                header_title=self._postFilter.nf_E.barKeys

                dataNF_E=self._postData.nf_E.dataResults
                if(dataNF_E.get(txIndex+1) is not None ):
                #已经包含该阵元的电流数据
                    dataRender=dataNF_E[txIndex+1]
                else:
                #需要读取数据
                    fname=self.currentProject.getNFFileName_E(txIndex+1)
                    if(not os.path.exists(fname)):
                        QtWidgets.QMessageBox.about(self,"电磁环境/电场","电磁环境数据不存在，请检查."+fname)
                        return
                    dataRender,freqList=api_reader.read_nf_sbr_E(fname)
                    #使用观察点切片数据
                   
                    
                    dataNF_E[txIndex+1]=dataRender
                

                
            elif(postTypeName==PostFilter.dataKey_nf_H):
                self._postFilter.setFilterNF_H()
                header_dic=self._postFilter.nf_H.headers
                header_title=self._postFilter.nf_H.barKeys
                dataNF_H=self._postData.nf_H.dataResults

                if(dataNF_H.get(txIndex+1) is not None):
                #已经包含该阵元的电流数据
                    dataRender=dataNF_H[txIndex+1]
                else:
                #需要读取数据
                    fname=self.currentProject.getNFFileName_H(txIndex+1)
                    if(not os.path.exists(fname)):
                        QtWidgets.QMessageBox.about(self,"电磁环境/磁场","电磁环境数据不存在，请检查."+fname)
                        return
                    dataRender=api_reader.read_nf_sbr_H(fname)
                    dataNF_H[txIndex+1]=dataRender
            else:
                QtWidgets.QMessageBox.about(self,"电磁环境","请点击结果节点查看数据")
                return
          
            if(vType==0):#表格数据
                self._postFilter.filter_now.singleChecked=False
                dataItem=dataRender[freqIndex]

                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                dbConvert=self._postFilter.filter_now.db_Convert#是否需要变换为db值
                v_convert_index_list=[]
                v_convert_header_list=[]
                if(dbConvert):
                    #先找到需要转换至的列索引
                    v_convert_index_list=[]
                    for k,v in self._postFilter.filter_now.checkedKeys_multi.items():
                        if(v and k in self._postFilter.filter_now.db_ConvertKeys):
                            v_convert_index_list.append(self._postFilter.filter_now.valueKeys[k])
                            v_convert_header_list.append(k)
                         
                        
                    pass
                if(len(v_convert_index_list)>0):
                    dataItem_db=[]
                    for i in range(len(dataItem)):
                        dItem=dataItem[i]
                        temp_list = list(dItem)
                        for i in range(len(v_convert_index_list)):
                            v_temp=temp_list[v_convert_index_list[i]]
                            if(v_temp<=0):
                                temp_list[v_convert_index_list[i]]=self._postFilter.filter_now.dbMin
                            else:
                                temp_list[v_convert_index_list[i]]=round(20*math.log10(v_temp),PostFilter.dotPrecision)
                        dataItem_db.append(tuple(temp_list))
                    # print(dataItem[0])
                    header_title=header_title.copy()
                
                    if(len(v_convert_header_list)>0):
                        for c_k in v_convert_header_list:  
                            
                            header_title[c_k]=header_title[c_k+PostFilter.dbTitle]
                  

                        pass

                    self.renderTable(header_dic,dataItem_db,header_title)

                else:
                    self.renderTable(header_dic,dataItem,header_title)
                self.sigActivateTab.emit(4)
            elif(vType==1):#曲线图数据
                self._postFilter.filter_now.singleChecked=True
                self.sigActivateTab.emit(3)
                
                dataItem=dataRender[freqIndex]
                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                valueIndex=-1
                valueText=""
                barTitle=""
                dbConvert=self._postFilter.filter_now.db_Convert#是否需要变换为db值
                
                
                for k,v in self._postFilter.filter_now.checkedKeys.items():
                    if(v):
                        valueIndex=self._postFilter.filter_now.valueKeys[k]
                        valueText=k
                        barTitle=valueText #默认的title与物理量一致
                        break
                if(valueText not in self._postFilter.filter_now.db_ConvertKeys):    
                    dbConvert=False #当前物理量不需要转换为db值
                if(self._postFilter.filter_now.barKeys.get(valueText)!=None):
                    barTitle=self._postFilter.filter_now.barKeys[valueText]
                if(dbConvert):
                    barTitle=self._postFilter.filter_now.barKeys[valueText+PostFilter.dbTitle]
                 #处理面，多个面时需要对数据进行切面处理
        
                surfaceList:list[str]=[]#面列表
                pointList=[]
                dataItem_result=dataItem

                #处理坐标数据，添加散列在最后，共计14列
                # 后三列的坐标数据主要用于构造平面使用，
                # 全局坐标系时，后三列与1/2/3相同，局部坐标系时，后三列为局部坐标系的坐标
                # 1/2/3分别为全局坐标系的坐标
                points_local=[]
                
                points_local=api_writer.get_nf_points(nfObj)
               

                # points_local=api_writer.get_nf_points(nfObj)
                for i in range(len(points_local)):
                    dItem=dataItem[i]
                    p_local=points_local[i]
                   
                    dItemN=list(dItem)
                    if(nfObj.axisType==0):
                        dItemN.append(dItem[1])
                        dItemN.append(dItem[2])
                        dItemN.append(dItem[3])
                    else:
                        dItemN.append(p_local[0])
                        dItemN.append(p_local[1])
                        dItemN.append(p_local[2])
                    dataItem[i]=tuple(dItemN)

                dimNum=0 #几个观察面，支持xy/xz/yz
                surfaceList=[]
                xAxis=None

                if(nfObj.uEnd!=nfObj.uStart):
                    dimNum=dimNum+1
                    xAxis=(0,"X/(m)") #x轴
                if(nfObj.vEnd!=nfObj.vStart):
                    dimNum=dimNum+1
                    xAxis=(1,"Y/(m)") #y轴
                if(nfObj.nEnd!=nfObj.nStart):
                    dimNum=dimNum+1
                    xAxis=(2,"Z/(m)") #z轴
                if(dimNum>=2):

                    if(nfObj.uEnd!=nfObj.uStart and nfObj.vEnd!=nfObj.vStart):
                        surfaceList.append("XY面")
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("XZ面")       
                    if(nfObj.vEnd!=nfObj.vStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("YZ面")
                    if(len(surfaceList)>0 and vTypeChanged):
                        #只有当首次时才发送信号 切换面和位置，不再发送信号
                        #切换物理量，也不再发送信号
                        #此时会重置面列表，因此surfaceIndex会与选中项不一致，需要将filter_now.surfaceIndex设置为0
                        
                        positionList=[]
                        self._postFilter.filter_now.surfaceIndex=0
                        #获取z的值列表，需要去掉重复值
                        if(len(surfaceList)>1):
                            vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                            positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                        
                        self.sigChooseSurface.emit(surfaceList,True)
                        self.sigPosition.emit(positionList)
                        self._postFilter.filter_now.surfaceList=surfaceList
                        self._postFilter.filter_now.positionList=positionList
                        self._postFilter.filter_now.surfaceIndex=0
                        self._postFilter.filter_now.positionIndex=0

                    if(surfaceChanged):
                         positionList=[]
                        #  vIndex=3-self._postFilter.filter_now.surfaceIndex
                         vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                         positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                         self._postFilter.filter_now.positionList=positionList
                         self._postFilter.filter_now.positionIndex=0
                         self.sigPosition.emit(positionList)                                 
                if(dimNum==3):
                    #需要选择面
                    # self.sigSurface.emit(self._postFilter.filter_now.checkedSurfaces)  
                    #先只选择xy面并且只看第一个Z的值
                    threshold = 1e-7
                    # pValue=dataItem[0][3]
                    pValue=self._postFilter.filter_now.positionList[self._postFilter.filter_now.positionIndex]
                    # vIndex=3-self._postFilter.filter_now.surfaceIndex
                    vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                    dataItem_result=[x for x in dataItem if abs(x[vIndex]-pValue)<threshold]

                Lindex=[]
               
                if(dimNum==1):
                    xInddex=xAxis[0]+1
                    for item in dataItem_result:
                        v=item[valueIndex]
                        #显示db模式时，需要对数值进行转换
                        if(dbConvert):
                            
                            if(v<=0):
                                v=self._postFilter.filter_now.dbMin
                            else:
                                v=20*math.log10(v)
                        pointList.append((item[xInddex],v))
                    self.renderChart(pointList,xAxis[1],barTitle)
                    return
                    pass
                elif(dimNum==2):
                    if(surfaceList[0]=="XY面"):
                        Lindex=[1,2]
                        Lindex=[11,12]
                        axisList=["X","Y"]
                    elif(surfaceList[0]=="XZ面"):
                        Lindex=[1,3]
                        Lindex=[11,13]
                        axisList=["X","Z"]
                    elif(surfaceList[0]=="YZ面"):
                        Lindex=[2,3]
                        Lindex=[12,13]
                        axisList=["Y","Z"]
                elif(dimNum==3):
                    if(self._postFilter.filter_now.surfaceIndex==0):
                        Lindex=[1,2]
                        Lindex=[11,12]
                        axisList=["X","Y"]
                    elif(self._postFilter.filter_now.surfaceIndex==1):
                        Lindex=[1,3]
                        Lindex=[11,13]
                        axisList=["X","Z"]
                    elif(self._postFilter.filter_now.surfaceIndex==2):
                        Lindex=[2,3]
                        Lindex=[12,13]
                        axisList=["Y","Z"]

                

                for item in dataItem_result:
                    v1=item[Lindex[0]]
                    v2=item[Lindex[1]]
                    v=item[valueIndex]
                    if(dbConvert):
                        if(v<=0):
                            v=self._postFilter.filter_now.dbMin
                        else:
                            v=20*math.log10(v)

                    pointList.append((v1,v2,v))
                if(xAxisIndex<0):
                    xAxisIndex=0
                
                self.renderChart_multi(pointList,axisList,xAxisIndex,barTitle)
    
                
            elif(vType==2):
                #云图显示 支持单面与多面，单面为xy面，yz面，xz面
                #多面时，需要处理数据和过滤项 过滤项有选择面，选择位置 
                #多面时，输入的数据项也需要单独处理，只输入当前面和选择了物理量的数据
                

                self._postFilter.filter_now.singleChecked=True
                self.sigActivateTab.emit(2)
                dataItem=dataRender[freqIndex]
                dataItem=dataItem[nfObj.point_slice_start:nfObj.point_slice_end]#切片处理 多个观察点时需要切片
                valueIndex=-1
                valueText=""
                barTitle=""
                dbConvert=self._postFilter.filter_now.db_Convert
                for k,v in self._postFilter.filter_now.checkedKeys.items():
                    if(v):
                        valueIndex=self._postFilter.filter_now.valueKeys[k]
                        valueText=k
                        barTitle=k
                        break  
                if(valueText not in self._postFilter.filter_now.db_ConvertKeys):
                    dbConvert=False
                if(self._postFilter.filter_now.barKeys.get(valueText)!=None):
                    barTitle=self._postFilter.filter_now.barKeys[valueText]
                if(dbConvert):
                    barTitle=self._postFilter.filter_now.barKeys[valueText+PostFilter.dbTitle]
                #处理面，多个面时需要对数据进行第二次切面处理

                surfaceList:list[str]=[]#面列表
               

                pointList=[]
                dataItem_result=dataItem
                points_local=api_writer.get_nf_points(nfObj)
                for i in range(len(points_local)):
                    dItem=dataItem[i]
                    p_local=points_local[i]
                    #处理坐标数据，添加散列在最后，共计14列
                    # 后三列的坐标数据主要用于构造平面使用，
                    # 全局坐标系时，后三列与1/2/3相同，局部坐标系时，后三列为局部坐标系的坐标
                    # 1/2/3分别为全局坐标系的坐标
                    dItemN=list(dItem)
                    if(nfObj.axisType==0):
                        dItemN.append(dItem[1])
                        dItemN.append(dItem[2])
                        dItemN.append(dItem[3])
                    else:
                        dItemN.append(p_local[0])
                        dItemN.append(p_local[1])
                        dItemN.append(p_local[2])
                    dataItem[i]=tuple(dItemN)
                    


                dimNum=0 #几个观察面，支持xy/xz/yz
                surfaceList=[]
                xAxis=None

                if(nfObj.uEnd!=nfObj.uStart):
                    dimNum=dimNum+1
                    xAxis=(0,"U Position") #x轴
                if(nfObj.vEnd!=nfObj.vStart):
                    dimNum=dimNum+1
                    xAxis=(1,"V Position") #y轴
                if(nfObj.nEnd!=nfObj.nStart):
                    dimNum=dimNum+1
                    xAxis=(2,"N Position") #z轴
                if(dimNum>=2):
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.vEnd!=nfObj.vStart):
                        surfaceList.append("XY面")
                    if(nfObj.uEnd!=nfObj.uStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("XZ面")       
                    if(nfObj.vEnd!=nfObj.vStart and nfObj.nEnd!=nfObj.nStart):
                        surfaceList.append("YZ面")

                    if(len(surfaceList)>0 and vTypeChanged):

                        positionList=[]
                        self._postFilter.filter_now.surfaceIndex=0
                        
                        if(len(surfaceList)>1):
                            vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                            positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                       
                        self.sigChooseSurface.emit(surfaceList,False)
                        self.sigPosition.emit(positionList)
                        self._postFilter.filter_now.surfaceList=surfaceList
                        self._postFilter.filter_now.positionList=positionList
                        self._postFilter.filter_now.surfaceIndex=0
                        self._postFilter.filter_now.positionIndex=0

                    if(surfaceChanged):
                         positionList=[]
                         vIndex=3-self._postFilter.filter_now.surfaceIndex
                         vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                         #全局坐标系时从数据中筛选，局部坐标系时从局部坐标系中获取
              
                         positionList=sorted(list(set(t[vIndex] for t in dataItem)))
                         

                         self._postFilter.filter_now.positionList=positionList
                         self._postFilter.filter_now.positionIndex=0
                         self.sigPosition.emit(positionList)                                 
                if(dimNum==3):
                    #需要选择面
                    # self.sigSurface.emit(self._postFilter.filter_now.checkedSurfaces)  
                    threshold = 1e-7
                    pValue=dataItem[0][3]   #先只选择xy面并且只看第一个Z的值
                    pValue=self._postFilter.filter_now.positionList[self._postFilter.filter_now.positionIndex]
                    vIndex=3-self._postFilter.filter_now.surfaceIndex
                    vIndex=13-self._postFilter.filter_now.surfaceIndex #添加了3列数据
                    dataItem_result=[x for x in dataItem if abs(x[vIndex]-pValue)<threshold]

                minV=1e9
                maxV=-1e9
                for item in dataItem_result:
                    v=item[valueIndex]
                    if(dbConvert):
                        if(v<=0):
                            v=self._postFilter.filter_now.dbMin
                        else:
                            v=20*math.log10(v)
                    pointList.append((item[1],item[2],item[3],v,item[11],item[12],item[13]))
                    if(v<minV):
                        minV=v
                    if(v>maxV):
                        maxV=v
                
                
                modelActor=None
                arrayActor_t=None
                arrayActor_r=None
                if(vTypeChanged):#首次加载云图，默认type为0，因此加载云图时一定是发生了vTypeChanged
                    
                    if(not os.path.exists(self.currentModel.geoFile)):
                        api_model.exportModel(self.currentModel.shape,self.currentModel.geoFile)
                    modelActor=api_vtk.stl_model(fname=self.currentModel.geoFile,opacity=1)
                   
                    self._vtkViewer3d.clear()
                    self._vtkViewer3d.display_model(modelActor)
                self._vtkViewer3d.clear_actor_custom()

                nfActor=api_vtk.cloud_map_nf(pointList)
                barActor=api_vtk.scalar_actor(minV,maxV,barTitle)

                self._vtkViewer3d.display_actor(nfActor)
                self._vtkViewer3d.display_actor(barActor)
            
                if(self._antenna_r._show_array 
                   and os.path.exists(self._antenna_r.file_array_model
                    and  os.path.isfile(self._antenna_r.file_array_model))):
                    arrayActor_r=api_vtk.stl_model(self._antenna_r.file_array_model,1,color=(0.5,0.5,0))
                    self._vtkViewer3d.display_actor(arrayActor_r)
                if(self._antenna_t._show_array and os.path.exists(self._antenna_t.file_array_model) and os.path.isfile(self._antenna_t.file_array_model)):
                    arrayActor_t=api_vtk.stl_model(self._antenna_t.file_array_model,1,color=(0.5,0,0))
                    self._vtkViewer3d.display_actor(arrayActor_t)
                points_now=[tup[:4] for tup in pointList]
                #每个点*1000
                points_now=[(tup[0]*1000,tup[1]*1000,tup[2]*1000,tup[3]) for tup in points_now]
                self._postData.data_now.points_now=points_now
                self._postData.data_now.headers_now=["X(m)","Y(m)","Z(m)",barTitle]

                self._postRender.render_now.actorMap=nfActor
                self._postRender.render_now.actorBar=barActor
                self._postRender.render_now.actorArray_TX=arrayActor_t
                self._postRender.render_now.actorArray_RX=arrayActor_r
                self._postRender.render_now.actorModel=modelActor

                self._postRender.render_now.show_surface=True
                self._postRender.render_now.show_points=False

                self._postRender.render_now.minV=minV
                self._postRender.render_now.maxV=maxV
                self._postRender.render_now.min_now=minV
                self._postRender.render_now.max_now=maxV

                
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"nf render","read the nf result error:"+str(e))
            traceback.print_exc()
        pass
    def renderTable(self,header_dic:dict,data:List[Tuple],header_title:dict):
        '''
        渲染表格
        '''
        
        #判断该列是否已显示，已显示则隐藏，未显示则显示
        #获取当前table的headers

        headers=[]
        for k in header_dic.keys():
                if(header_title.get(k) is not None):
                    headers.append(header_title.get(k))
                else:
                    headers.append(k)
    

        self._tableViewer.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tableViewer.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # self.tbLibrary.setVerticalHeaderLabels(["Type","Media name","From"])
        self._tableViewer.horizontalHeader().setSelectionMode(QHeaderView.SelectionMode.NoSelection)
        # self.tbLibrary.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self._tableViewer.setAlternatingRowColors(True)
        self._tableViewer.horizontalHeader().setHighlightSections(False)
        self._tableViewer.verticalHeader().setVisible(False)
        self._tableViewer.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self._tableViewer.setStyleSheet("""
                                       QHeaderView::section { font-size: 14px;border:1px solid rgb(216,216,216); }
                                      """)

        self._tableViewer.setColumnCount(len(headers))
        self._tableViewer.setHorizontalHeaderLabels(headers)
        self._tableViewer.setRowCount(0)
        rowNum=len(data)
        self._tableViewer.setRowCount(rowNum)
        for i in range(rowNum):
            for j in range(len(headers)):
                item=QTableWidgetItem(str(data[i][j]))
                self._tableViewer.setItem(i,j,item)
        #隐藏为0的列
        cIndex=0
        for v in header_dic.values():
            if(not v):
                self._tableViewer.setColumnHidden(cIndex,True)
            else:
                self._tableViewer.setColumnHidden(cIndex,False)
            cIndex=cIndex+1
        
        self._tableViewer.resizeColumnsToContents()
        min_width = 80
        header = self._tableViewer.horizontalHeader()
        header.setMinimumSectionSize(min_width)
        for column in range(self._tableViewer.columnCount()):
            if header.sectionSize(column) < min_width:
                header.resizeSection(column, min_width)

        pass
    def renderChart(self,pointList:List[Tuple[float,float]],xName,yName):
        '''
        显示二维曲线图
        '''
        chart=api_vtk.chart_line(pointList,xName,yName)
        self._vtkViewer2d.display_chart(chart)
    def renderChart_multi(self,pointList:List[Tuple[float,float,float]],axisList:list,xAxisIndex,yName):
        '''
        显示二维曲线图
        '''
        xName=axisList[xAxisIndex]
        lineName=axisList[1-xAxisIndex]
        rList=[]
        threold=1e-7
        vXList=sorted(list(set(t[1-xAxisIndex] for t in pointList)))

        for vx in vXList:
            _pointList=[]
            for p in pointList:
                if(abs(p[1-xAxisIndex]-vx)<threold):
                    _pointList.append((p[xAxisIndex],p[2]))

            rList.append((vx,_pointList))
   
        chart=api_vtk.chart_line_multi(rList,xName,yName,lineTitle=lineName)

        self._vtkViewer2d.display_chart(chart)
  
        pass
    # def renderColudMap(self,pointList:List[Tuple[float,float,float,float]]):
    #     '''
    #     显示云图，电磁环境观测点，电磁干扰
    #     '''
    #     mapActor=api_vtk.cloud_map(pointList)
    #     self._vtkViewer3d.display_actor(mapActor)
    #     pass
    def renderSurfaceMap(self):
        '''
        显示/隐藏表面云图
        '''
        postRender=self._postRender
        postData=self._postData
        if(self._is_extend):
            postRender=self._postRender_extend
            postData=self._postData_extend
        if(postRender.render_now==None or postData.data_now==None):
            return
        postRender.render_now.show_surface=not postRender.render_now.show_surface
        show_surface=postRender.render_now.show_surface
        mapActor=postRender.render_now.actorMap
        if(mapActor==None):
            return #未曾显示过，不予处理直接返回
        if(show_surface):
            self._vtkViewer3d.display_actor(mapActor)
        else:
            self._vtkViewer3d.remove_actor(mapActor)
    def renderPoints(self):
        '''
        显示数据点,需要分别处理 currents/nf_E/nf_H/EMI
        '''
        # self._vtkViewer3d.clear_actor_custom()
        # print("当前数据类型",self._postFilter.filter_now.typeName)
        postRender=self._postRender
        postData=self._postData
        postFilter=self._postFilter
        if(self._is_extend):

            postRender=self._postRender_extend
            postData=self._postData_extend
            postFilter=self._postFilter_extend

        if(postRender.render_now==None or postData.data_now==None):
            return
        #只有云图需要处理，其他类型的显示直接返回
        vTypeLen=len(postFilter.filter_now.vTypeList)
        vTypeIndex=postFilter.vTypeIndex
        if(vTypeIndex!=vTypeLen-1): #最后一个显示类型是云图，不是则返回
            return
        
        postRender.render_now.show_points=not postRender.render_now.show_points
        show_points=postRender.render_now.show_points

        pointList=postData.data_now.points_now
        if(show_points):
            pointActor,_=api_vtk.points_vertex(pointList)
            self._vtkViewer3d.display_actor(pointActor)
            postRender.render_now.actorPoints=pointActor
        else:
            pointActor=postRender.render_now.actorPoints
            self._vtkViewer3d.remove_actor(pointActor)
        pass
    def reverseNormal(self):
        if(self.currentModel==None):
            return
        if(not hasattr(self.currentModel,"face_selected")):
            return
        for k in self.currentModel.face_selected:
            if(self.currentModel.face_selected[k]):
                shape=api_model.reverse_face(self.currentModel.shape,k+1)
                self.currentModel.shape=shape
                self.sig_setModelColor(self._modelColor)
                api_model.exportModel(shape,self.currentModel.fileName)#保存新的模型文件

                break
        

        pass
    def setFaceMediumBase(self):
        #点击节点触发时，
        faceId=int(self.tree.currentItem().text(0).replace("Face",""))
        self.nodeAction_faceClicked()
        # if(self.currentModel.mediumFaces.get(faceId)!=None):
        #     QtWidgets.QMessageBox.about(self,"设置介质","该面已设置介质，请先取消设置")
        #     return

        isotropicList=self._mediaDic[MediaBase.isotropic]
        anisotropicList=self._mediaDic[MediaBase.anisotropic]
        dispersiveList=self._mediaDic[MediaBase.dispersive]
        frm=frmMediaLibraryN(self,isotropicList,anisotropicList,dispersiveList)
        frm.move(self.parent.centralWidget().geometry().topLeft())
        frm.show()
        frm.sigApplyMedia.connect(self.sig_applyMedia)
        frm.sigClosed.connect(self.sig_mediaLibraryClosed)
        frm.sigMedialSelected.connect(self.sig_MediaSelected)

        pass
    def initFaceToolTips(self):
        try:
            if(self.currentModel==None):
                return
            mediumFaces=self.currentModel.mediumFaces
            mediumIndex=self.currentModel.medium
            mediumModel=None
            if(mediumIndex>=0):
                mediumModel=self._mediaList[mediumIndex]
            for i in range(self.faceRoot.childCount()):
                tips=""
                if(mediumModel!=None):
                    tips=mediumModel.media.name
                item=self.faceRoot.child(i)
                if(mediumFaces.get(i+1)!=None):#单独设置了面材料
                    mediaIndex=mediumFaces[i+1][0]
                    mediaCoatIndex=mediumFaces[i+1][1]
                    
                    mediaBase:MediaItem=self._mediaList[mediaIndex]
                    tips=mediaBase.media.name
                    if(mediaCoatIndex>=0):
                        mediaCoat:MediaItem=self._mediaList[mediaCoatIndex]
                        thickness=mediumFaces[i+1][2]
                        tips=tips+"-涂覆:"+mediaCoat.media.name+"/"+str(thickness)
                item.setToolTip(0,tips)
        except Exception as e:
            print("initFaceToolTips",str(e))
            traceback.print_exc()
    def sig_MediaSelected(self,mediaObj:MediaBase):
        '''
        选择介质
        '''
        faceId=-1
        for k in self.currentModel.face_selected:
            if(self.currentModel.face_selected[k]):
                faceId=k+1
                break
        if(faceId<0):
            return  #未选择面
        # print("选择介质",mediaObj.name)
        mediumFaces=self.currentModel.mediumFaces
        # print("当前面",len(mediumFaces))
        #更新当前mediumFaces
        #先要找到media的索引值
        mediaIndex=-1
        for i in range(len(self._mediaList)):
            mItem=self._mediaList[i]
            if(mItem.media.name==mediaObj.name):
                mediaIndex=i
                break
        v=mediumFaces.get(faceId)
        if(v==None):
            mediumFaces[faceId]=(mediaIndex,-1,0)
        else:
            mediumFaces[faceId]=(mediaIndex,v[1],v[2])
        pass
        # self.initFaceToolTips()
        self.init_medium_used()
    
    def setFaceMediumCoat(self):
        self.nodeAction_faceClicked()
        faceId=-1
        for k in self.currentModel.face_selected:
            if(self.currentModel.face_selected[k]):
                faceId=k+1
                break
        mediumFaces=self.currentModel.mediumFaces
        #先要找到media的索引值
        v=mediumFaces.get(faceId)
        mediaName=""
        thickness=0
        if(v!=None and v[1]>=0):
            mediaCoat:MediaItem=self._mediaList[v[1]]
            mediaName=mediaCoat.media.name
            thickness=v[2]

        frm=frmMediaCoat(self,mediaName,thickness)
        frm.show()
        frm.move(self.parent.centralWidget().geometry().topLeft())
        frm.sigApplyMediaCoat.connect(self.sig_applyMediaCoat)
        frm.sigChooseMeidaCoat.connect(self.sig_chooseMediaCoat)
        self._frm_mediaCoat=frm
        pass
    def sig_chooseMediaCoat(self):
        isotropicList=self._mediaDic[MediaBase.isotropic]
        anisotropicList=self._mediaDic[MediaBase.anisotropic]
        dispersiveList=self._mediaDic[MediaBase.dispersive]
        frm=frmMediaLibraryN(self,isotropicList,anisotropicList,dispersiveList)
        frm.show()
        frm.sigApplyMedia.connect(self.sig_applyMedia)
        frm.sigClosed.connect(self.sig_mediaLibraryClosed)
        if(self._frm_mediaCoat!=None):
            frm.sigMedialSelected.connect(self._frm_mediaCoat.setMedia)
        pass
    def sig_applyMediaCoat(self,mediaObj:MediaBase,thickness:float):
        
        faceId=-1
        for k in self.currentModel.face_selected:
            if(self.currentModel.face_selected[k]):
                faceId=k+1
                break
        if(faceId<0):
            return  #未选择面
        mediumFaces=self.currentModel.mediumFaces
        #先要找到media的索引值
        mediaIndex=-1
        v=mediumFaces.get(faceId)
        if(mediaObj!=None):
            for i in range(len(self._mediaList)):
                mItem=self._mediaList[i]
                if(mItem.media.name==mediaObj.name):
                    mediaIndex=i
                    break
        else:
            if(v!=None):
                mediaIndex=v[1]
        
        if(v==None):
            mediumFaces[faceId]=(-1,mediaIndex,thickness)
        else:
            mediumFaces[faceId]=(v[0],mediaIndex,thickness)
        pass
        # self.initFaceToolTips()
        self.init_medium_used()


        pass
    
    '''
    后处理节点
    '''
    def nodeAction_RenameRNFRItem(self):
        pass
    def nodeAction_RNFRProperties(self):
        pass
    def nodeAction_ExportRNFRItem(self):
        pass
    def nodeAction_DisplayEM_2d(self):
        '''
        显示电磁场观察点
        '''
        try:
            self.closeFormsOpened()
            fname=self.get_fname_em_2d()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"电场","文件不存在，请检查."+fname)
                return
            value_list=api_reader.read_em_2d(fname)
            chart=api_vtk.chart_line(value_list,"Time(S)","E_Total(V/m)",displayPoints=False)
            self._vtkViewer2d.display_chart(chart)
            self.sigActivateTab.emit(3)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"电场分析","查看电场数据错误:"+str(e))
            return
        pass
    def nodeAction_DisplayEM_3d(self):
        '''
        显示电磁场观察域
        '''
        try:
            self.closeFormsOpened()
            fname=self.get_fname_em_3d()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"电场","文件不存在，请检查."+fname)
                return
            
            points_list,tet_list,e_list=api_reader.read_em_3d(fname)
            points=[]
            for i in range(len(points_list)):
                p=points_list[i]
                points.append((p[0],p[1],p[2],e_list[i]))

            v_min=min(e_list)
            v_max=max(e_list)
            
            actor=api_vtk.em_3d(points_list,tet_list,e_list)
            # actor,_=api_vtk.points_vertex(points)
            barActor=api_vtk.scalar_actor(v_min,v_max,"E_Total(V/m)")
            self._actors_current.clear()
            self._actors_current.append(actor)
            self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            
            self._vtkViewer3d.display_actor(actor)
            self._vtkViewer3d.display_actor(barActor)
            self._vtkViewer3d.reset_camera()
            self.sig_setActorOpacity(self.currentModel.opacityMap)
            
            self.sigActivateTab.emit(2)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"电场分析","查看电场数据错误:"+str(e))
            return
        pass
    def nodeAction_display_ffr_db(self):
        '''
        显示方向图的dB值
        '''
        itemData=self.resultFFR3DRoot.data(0,257)
        if(itemData==None):
            return
        actor=itemData[0]
        if(actor==None):
            QtWidgets.QMessageBox.about(self,"电场","方向图数据不存在，请先计算方向图.")
            return
        minV_db=itemData[1]
        maxV_db=itemData[2]
        barTitle="rE(dB)"
        self.refresh_em_ffr(actor,minV_db,maxV_db,barTitle)
        pass
    def nodeAction_display_ffr_linear(self):
        '''
        显示方向图的线性值
        '''
        itemData=self.resultFFR3DRoot.data(0,257)
        if(itemData==None):
            return
        actor=itemData[0]
        if(actor==None):
            QtWidgets.QMessageBox.about(self,"电场","方向图数据不存在，请先计算方向图.")
            return
        minV_linear=itemData[3]
        maxV_linear=itemData[4]
        barTitle="rE(V/m)"
        self.refresh_em_ffr(actor,minV_linear,maxV_linear,barTitle)
        pass
    def refresh_em_ffr(self,actor,minV,maxV,barTittle=""):
        barActor=api_vtk.scalar_actor(minV,maxV,barTittle)
        self._actors_current.clear()
        self._actors_current.append(actor)
        self._vtkViewer3d.clear()
        self._vtkViewer3d.clear_actor_custom()
        
        self._vtkViewer3d.display_actor(actor)
        self._vtkViewer3d.display_actor(barActor)
        self._vtkViewer3d.reset_camera()
        self.sig_setActorOpacity(self.currentModel.opacityMap)
            
        self.sigActivateTab.emit(2)
        pass

    def nodeAction_DisplayEM_ffr(self,isdb:bool=True):
        '''
        显示方向图
        '''
        try:
            fname=self.get_fname_em_ffr()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"电场","方向图文件不存在，请检查."+fname)
                return
            # rList=api_reader.read_em_ffr(fname)
            # if(len(rList)<1):
            #     return
            # item=rList[0]
            # pointList=item[0]
            # minV=item[1]
            # maxV=item[2]
            # thetaNum=item[3]
            # phiNum=item[4]
            # scalar_factor=item[6]
            # actor=api_vtk.antenna_radio_pattern(pointList,minV,maxV,thetaNum,phiNum)

            rList=api_reader.read_ffr_gdtd(fname)
            if(len(rList)<1):
                return
            pointList=rList[0]
          


            actor,pointList_n,minV_db,maxV_db,minV_linear,maxV_linear=api_vtk.ffr_3dpolar(pointList)

            self.resultFFR3DRoot.setData(0,257,(actor,minV_db,maxV_db,minV_linear,maxV_linear))

                
            if(isdb):
                barActor=api_vtk.scalar_actor(minV_db,maxV_db,"rE(dB)")
            else:
                barActor=api_vtk.scalar_actor(minV_linear,maxV_linear,"rE(V/m)")
            
            self._actors_current.clear()
            self._actors_current.append(actor)
            self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            
            self._vtkViewer3d.display_actor(actor)
            self._vtkViewer3d.display_actor(barActor)
            self._vtkViewer3d.reset_camera()
            self.sig_setActorOpacity(self.currentModel.opacityMap)
            
            self.sigActivateTab.emit(2)

            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"电场分析","查看方向图数据错误:"+str(e))
            return
        pass
    def nodeAction_DisplayEM_2dPolar(self):
        try:
            fname=self.get_fname_em_ffr()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"电场","方向图文件不存在，请检查."+fname)
                return

            rList=api_reader.read_ffr_gdtd(fname)
            if(len(rList)<1):
                return
            pointList=rList[0]
            frm=frmFilter2dPolar(self,pointList)
            frm.show()
            frm.move(self.topLeffPoint())
            frm.sigApply.connect(self.sig_applyFilter2dPolar)
            frm.sigClosed.connect(self.sig_filter2dPolarClosed)
            self.sigActivateTab.emit(5)
            # self.renderPolar_multi(pointList,["Theta(°)","Phi(°)"],0,"rE(V/m)")
        
        
            

            pass
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"电场分析","查看方向图数据错误:"+str(e))
            return
    def sig_applyFilter2dPolar(self,filterData:dict):
        '''
        应用2d极坐标图的过滤
        '''
        filterType=filterData["filterType"]
        filterValue=filterData["filterValue"]
        pointList=filterData["filteredPoints"]
        xAxisIndex=1
        if filterType=="phi":
            xAxisIndex=0
        self.renderPolar_multi(pointList,[f"Theta={filterValue}",f"Phi={filterValue}"],xAxisIndex,"rE(dB)")
        # self.sigActivateTab.emit(5)
        pass
    def sig_filter2dPolarClosed(self):
        self.sigActivateTab.emit(0) #回到几何
    def renderPolar_multi(self,pointList:List[Tuple[float,float,float]],axisList:list,xAxisIndex,yName):
        '''
        显示二维极坐标图
        '''
        xName=axisList[xAxisIndex]#自变量名称
        lineName=axisList[1-xAxisIndex]#线的名称
        rList=[]
        threold=1e-7
        vXList=sorted(list(set(t[1-xAxisIndex] for t in pointList)))#自变量的值列表

        for vx in vXList:
            _pointList=[]
            for p in pointList:
                if(abs(p[1-xAxisIndex]-vx)<threold):
                    _pointList.append((p[xAxisIndex],p[2]))
            rList.append((vx,_pointList))#每个自变量对应的数据点列表
   
        self._2dPolarViewer.render_multi(rList,yName,xAxisIndex,lineName)
  
        pass
    def nodeAction_DisplayThermal3D(self):
        try:
            self.closeFormsOpened()
            fname=self.get_fname_thermal_3d()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"热分析","温度文件不存在，请检查."+fname)
                return
            
            points_list,tet_list,temperature_list=api_reader.read_thermal_3d(fname)
            points=[]
            for i in range(len(points_list)):
                p=points_list[i]
                points.append((p[0],p[1],p[2],temperature_list[i]))

            v_min=min(temperature_list)
            v_max=max(temperature_list)
            
            actor=api_vtk.thermal_3d(points_list,tet_list,temperature_list)
            # actor,_=api_vtk.points_vertex(points)
            barActor=api_vtk.scalar_actor(v_min,v_max,"Temperature(K)")
            self._actors_current.clear()
            self._actors_current.append(actor)
            self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            
            self._vtkViewer3d.display_actor(actor)
            self._vtkViewer3d.display_actor(barActor)
            self._vtkViewer3d.reset_camera()
            self.sig_setActorOpacity(self.currentModel.opacityMap)
            
            self.sigActivateTab.emit(2)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"热分析","查看温度数据错误:"+str(e))
            return

        pass
    def nodeAction_DisplayThermal2D(self):
        try:
            self.closeFormsOpened()
            fname=self.get_fname_thermal_2d()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"热分析","温度文件不存在，请检查."+fname)
                return
            temperature_list=api_reader.read_thermal_2d(fname)
            chart=api_vtk.chart_line(temperature_list,"Time(S)","Temperature(K)",displayPoints=False)
            self._vtkViewer2d.display_chart(chart)
            self.sigActivateTab.emit(3)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"热分析","查看温度数据错误:"+str(e))
            return
    def sig_displace_showParam(self,showModel,showActor):
        if(self._stl_actor!=None):
            self._vtkViewer3d.remove_actor(self._stl_actor) 
            if(showModel):
                self._vtkViewer3d.display_actor(self._stl_actor)
        if(self._displace_actor!=None):
            self._vtkViewer3d.remove_actor(self._displace_actor)
            if(showActor):
                self._vtkViewer3d.display_actor(self._displace_actor)
            
    def nodeAction_DisplayDisplacement3D(self):
        try:
            self.closeFormsOpened()
            frm=frmPostParam(self)
            frm.show()
            frm.move(self.topLeffPoint())
            frm.sigShowParam.connect(self.sig_displace_showParam)
            self._forms.append(frm)
            
            
            
            fname=self.get_fname_displacement_3d()
            if(not os.path.exists(fname)):
                QtWidgets.QMessageBox.about(self,"力分析","仿真数据文件不存在，请检查."+fname)
                return
            
            points_list,tet_list,displacement_list=api_reader.read_displacement_3d(fname)
            points=[]
            for i in range(len(points_list)):
                p=points_list[i]
                points.append((p[0],p[1],p[2],displacement_list[i][3]))

            v_min=min(item[3] for item in displacement_list)
            v_max=max(item[3] for item in displacement_list)
       
            actor=api_vtk.displacement_3d(points_list,tet_list,displacement_list)
            stl_actor=api_vtk.stl_model(self.currentModel.geoFile,opacity=0.5)
            # actor,_=api_vtk.points_vertex(points)
            barActor=api_vtk.scalar_actor(v_min,v_max,"Disp(m)",dotPrecision=6)
            self._actors_current.clear()
            self._actors_current.append(actor)
            
            self._vtkViewer3d.clear()
            self._vtkViewer3d.clear_actor_custom()
            self._vtkViewer3d.display_actor(actor)
            self._vtkViewer3d.display_actor(stl_actor)
            self._vtkViewer3d.display_actor(barActor)
            self._vtkViewer3d.reset_camera()
            self._stl_actor=stl_actor
            self._displace_actor=actor
            self.sig_setActorOpacity(self.currentModel.opacityMap)
        
            self.sigActivateTab.emit(2)

            
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"力分析","查看力分析数据错误:"+str(e))
            return

    '''
    后处理电流节点
    '''
    def nodeAction_RenameCurrentsItem(self):
        self.nodeAction_Rename(self.tree.currentItem())
        pass
    def nodeAction_ExportCurrents(self):
        pass

    def nodeAction_SetMPI(self):
        mpiNum=self.currentProject.mpiNum
        frm=frmMPI(self,mpiNum,"")
        frm.show()
        frm.sigMPISet.connect(self.sig_MPISet)
        pass
    def sig_MPISet(self,mpiNum,installPath):
        self.currentProject.mpiNum=mpiNum
    def nodeAction_Rename(self,item:QTreeWidgetItem):
        '''
        编辑节点名称
        '''
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.editItem(item)
        self.currentEditItem=item

    def node_clear(self, node: QTreeWidgetItem):
        for i in reversed(range(node.childCount())):
            node.removeChild(node.child(i))





    # def prepareMenu(self):  # 模型树弹出菜单

    #     self.tree.setContextMenuPolicy(Qt.CustomContextMenu)

    #     self._context_menu = QMenu(self)
    #     # self._context_menu.addActions(self._toolbar_actions)
    #     self._context_menu.addActions((self._export_STL_action,
    #                                    self._export_STEP_action))
    #     pass

    def prepareLayout(self):

        self.sp = QtWidgets.QSplitter(Qt.Vertical)
        # self.sp.setFont(self._font)
    
        self.sp.addWidget(self.tree)
        
        self.sp.setStretchFactor(1,1)

        layout = QtWidgets.QVBoxLayout(self)
        
        self.setLayout(layout)
        
        layout.addWidget(self.sp)

        layout.setSpacing(0)
        layout.setContentsMargins(2,2,2,2)

        self.sp.show()
        
        pass

    def showMenu(self, position):
        # index=self.tree.indexAt(position)
        item = self.tree.itemAt(position)
        if(item==None):
            return
        nodeName = item.text(0)
        # print("click node ", nodeName, item.parent())
        self._context_menu.clear()
       
        # self._context_menu.setFont
        # actions = self.getNodeActions(nodeName,item)
        
        actions=item.data(0,self.actionIndex)
        if(actions==None):
            return
        self._context_menu.addActions(actions)
        # python
        self._context_menu.exec_(self.tree.viewport().mapToGlobal(position))
        




 