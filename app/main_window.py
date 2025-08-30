import sys,time,math,subprocess,shutil
from PyQt5 import QtWidgets,QtCore
import qtawesome as qta
from typing import List,Set,Dict,Tuple

# from OCC.Core.gp import gp_Pnt
from OCC.Display import OCCViewer
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QMainWindow,
    QToolBar,
    QDockWidget,
    QAction,
    QDockWidget,
    QTabWidget,
    QSizePolicy,
    QComboBox,
    QMenu
)
from PyQt5.QtGui import QPalette, QColor,QIcon,QMouseEvent,QFont
from PyQt5.QtGui import QKeySequence as QKSec

from .theme import theme_ui
from .dataModel.menu import menuButton,menuPool

from .widgets.console import ConsoleWidget


from .widgets.traceback_viewer import TracebackPane


from .widgets.logViewer import LogViewer


from .widgets.projectTree import ProjectTree

from .widgets.vtk_viewer_3d import vtkViewer3d
from .widgets.vtk_viewer_2d import vtkViewer2d
from .widgets.ribbon.Icons import get_icon
from .widgets.ribbon.RibbonWidget import RibbonWidget
from .widgets.ribbon.RibbonTab import RibbonTab
from .widgets.ribbon.RibbonPane import RibbonPane
from .widgets.ribbon.RibbonButton import RibbonButton
from .widgets.ribbon.RibbonTextbox import RibbonTextbox
from .widgets.ribbon.RibbonComboBox import RibbonComboBox
from .widgets.ribbon.RibbonButton_V import RibbonButton_V

from .widgets.customTitleBar import CTitleBar
from .widgets.sideGrip import SideGrip

from .widgets.frmFindElement import frmFindElement
from .widgets.frmMeasure import frmMeasure
from .widgets.frmLocalSize import frmLocalSize
from .widgets.frmExchange import frmExchange
from .widgets.frmModelColor import frmModelColor
from .widgets.frmMPI import frmMPI
from .widgets.frmScalar import frmScalar
from .widgets.frmLicense import frmLicense
from .widgets.baseStyle import baseStyle

from .widgets.wFilter import wFilter
from .dataModel.postFilter import PostFilter,filter_nf_E,filter_nf_H,filter_emi,filter_xyz
from .widgets.polarPlotWidget import PolarPlotWidget

# QtWidgets.QMessageBox.about(None,"test","启动1.1")

from . import __version__
# from .utils import dock, add_actions, open_url, about_dialog, check_gtihub_for_updates, confirm
from .mixins import MainMixin
from .icons import icon,menuIcons,sysIcons,treeIcons
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from OCC.Display.OCCViewer import OffscreenRenderer

from OCC.Display.backend import load_backend, get_qt_modules
from OCC.Extend.TopologyUtils import TopologyExplorer
from .module.interactiveContext import InteractiveContext
from app.api import api_vtk,api_project,api_model,api_config,api_license
# QtWidgets.QMessageBox.about(None,"test","启动1.2")
from app.dataModel.project import Project
DOCK_POSITIONS = {'right'   : QtCore.Qt.RightDockWidgetArea,
                  'left'    : QtCore.Qt.LeftDockWidgetArea,
                  'top'     : QtCore.Qt.TopDockWidgetArea,
                  'bottom'  : QtCore.Qt.BottomDockWidgetArea}



log = logging.getLogger(__name__)

screen=QtWidgets.QApplication.screens()[0]
SCREEN_WIDTH=screen.geometry().width()
SCREEN_HEIGHT=screen.geometry().height()

TABINDEX_MODEL=0
TABINDEX_MESH=1
TABINDEX_POST3D=2
TABINDEX_POST2D=3
DEBUG_MODE=False

def gui_scale():
    screen = QtWidgets.QApplication.screens()[0]
    dpi = screen.logicalDotsPerInch()
    return dpi / 96

def check_callable(_callable):
    if not callable(_callable):
        raise AssertionError("The function supplied is not callable")



backend_str = None
display_triedron = True
# background_gradient_color1 = [55, 59, 168]
# background_gradient_color2 = [66, 134, 180]
if os.getenv("PYTHONOCC_OFFSCREEN_RENDERER") == "1":
    # create the offscreen renderer
    offscreen_renderer = OffscreenRenderer()

    def do_nothing(*kargs, **kwargs):
        """ takes as many parameters as you want,
        ans does nothing
        """
        pass

    def call_function(s, func):
        """ A function that calls another function.
        Helpfull to bypass add_function_to_menu. s should be a string
        """
        check_callable(func)
        log.info("Execute %s :: %s menu fonction" % (s, func.__name__))
        func()
        log.info("done")

    # returns empty classes and functions
used_backend = load_backend(backend_str)
log.info("GUI backend set to: %s", used_backend)
from .module import qtDisplay
QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()
# QtWidgets.QMessageBox.about(None,"test","启动1.3")
# ------------------------------------------------------------初始化结束
mainStyle="""
    QMainWindow{
        font-size:16px;
        font-family:Arial, 'Segoe UI', Tahoma, "Microsoft YaHei", sans-serif
        }
"""

class MainWindow(QMainWindow, MainMixin):
    name = '多物理场仿真软件V1.0'
    org = 'CSSC'
    _gripSize = 2
    def __init__(self, parent=None, spid=None,projectFile:str=""):

        super(MainWindow, self).__init__(parent)
        MainMixin.__init__(self)

        self._font=self.font()
        # self._font.setPixelSize(baseStyle.fontPixel_14)
        # self._font.setFamilies(baseStyle.fontFamilys)
        # self.setFont(self._font)
        # self.setStyleSheet(theme_ui.baseWidgetStyle)

        self._defaultProjectFile=projectFile
        self._context_menu = QMenu(self)
        self._context_menu.setFont(self._font)


        

        self.setWindowIcon(sysIcons.windowIcon)

        self.themeUI:theme_ui=theme_ui("gray")

        self._appLogger=api_project.getLogger("app")

        self._postPointsDisplay=False#显示后处理数据点
        self._surfaceDisplay=True #显示后处理云图
        # print("project file",projectFile)
        # self.setWindowTitle(f"{self.name}:{projectFile}")
        # self.setWindowTitle(f"{self.name}")
        self.setWindowFlags(self.windowFlags()|QtCore.Qt.WindowType.FramelessWindowHint)
        
        status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(status_bar)
        
        # status_bar.showMessage("Powered by CSSC",100000000)

        label = QLabel("Powered by CSSC")
        status_bar.addWidget(label,1)

        self._titleBar=CTitleBar(self,title=f"{self.name}")#设置系统标题
        self.setMenuWidget(self._titleBar)
        self._titleBar.setStyleSheet(self.themeUI.titleBar)
        self.progress_bar = QtWidgets.QProgressBar()
        status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setRange(0,100)
        self.progress_bar.setFixedWidth(600)
        self.progress_bar.setHidden(True)
    
        # self.progress_bar = QtWidgets.QProgressBar()
        # status_bar.addPermanentWidget(self.progress_bar)

        # self._titleBar=CTitleBar(self,title=f"{self.name}")#设置系统标题
        # self.setMenuWidget(self._titleBar)

        self.tabWidget = QTabWidget()
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")

        self.viewPage = qtDisplay.qtViewer3d(self)  # 链接3D模块
        self.modelViewer:OCCViewer.Viewer3d=self.viewPage._display

        
        
        
        self.tabWidget.addTab(self.viewPage, "几何")

        self.meshViewer = vtkViewer3d(self)
        self.tabWidget.addTab(self.meshViewer, "网格")

        self._3dViewer = vtkViewer3d(self)
        self.tabWidget.addTab(self._3dViewer, "3D云图")

        
    
        self._2dViewer= vtkViewer2d(self)
        self.tabWidget.addTab(self._2dViewer, "曲线图")

        self._tableViewer= QtWidgets.QTableWidget()
        _tableFont=self._tableViewer.font()
        _tableFont.setPixelSize(baseStyle.fontPixel_14)
        _tableFont.setFamilies(["Times New Roman","Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        self._tableViewer.setFont(_tableFont)
        self.tabWidget.addTab(self._tableViewer, "表格")

        self._2dPolarViewer=PolarPlotWidget(self)
        self.tabWidget.addTab(self._2dPolarViewer, "2D极坐标图")
        
        self.setCentralWidget(self.tabWidget)
        self.centralWidget().customContextMenuRequested.connect(self.showContextMenu)
        self.tab_home=None
        self.tab_post_process=None

        self.cbxTX=None
        self.cbxFrequency=None
        self.cbxVType=None
        self.cbxSurface=None
        self.cbxPosition=None
        self.cbxXAxis=None
        self.grid_main=None #主筛选表格 tx/freq/vtype
        self.grid_value=None #值筛选表格
        self.grid_axis=None #曲线图查看横坐标的值，选择x/y/z

        self.btn_solver:QPushButton=None #求解器选择按钮
        self.tab_sim=None
        self.grid_buttons={
            "single":False, #单选,
            "btnList":[]
        }
        #曲线图查看横坐标的值，选择x/y/z
        self.axis_buttons={
            "checked":None,
            "btnList":[]
        }
        self._btn_db:QPushButton=None
        # self._db_convertKeys={}

        self.dic_pane={
            "filter_main":None,
            "filter_value":None,
            "filter_axis":None,
            "filter_surface":None,
            "filter_convert":None
        }

        self.btnStyle=  """
            QPushButton {
                border: 1px solid #8f8f91;
                border-radius: 2px;
                background-color: #f0f0f0;
                padding: 2px;
                margin-left:2px;
                margin-right:2px;
                height:25px;
                min-width:60px;
                font-size:14px;
                font-family:Times New Roman,Arial, 'Segoe UI', Tahoma, "Microsoft YaHei", sans-serif
                
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:checked { background-color: rgb(101,163,249); }
            QPushButton:disabled {
    background-color: rbg(228,228,228); /* disabled 状态下的背景色 */
}

        """
        self.cbxStyle="""
            
            height:50px;
            min-width:100px;
            font-size:14px;
            font-family:Arial, 'Segoe UI', Tahoma, "Microsoft YaHei", sans-serif
                
            
        """
       
        
        # 点线面体拾取交互
        
        self.selectContext = InteractiveContext(self,self.modelViewer)
        
        self.logViewer=LogViewer(self)
        # self.traceBackViewer=TracebackPane(self)
        self.console:ConsoleWidget=ConsoleWidget(self)

        treeSize=QtCore.QSize(round(SCREEN_WIDTH*0.15),round(SCREEN_HEIGHT*0.9))
        self.projectTree:ProjectTree=ProjectTree(self,self.modelViewer,
                                                 self.meshViewer,
                                                 self.console,
                                                 treeSize,
                                                 self._3dViewer,self._2dViewer,
                                                 self.selectContext,
                                                 self._tableViewer,
                                                 self._2dPolarViewer)
        
        
        
        
        self.dock(self.projectTree,"工程管理",defaultArea="left")
        self.dock(self.console,"控制台",defaultArea="bottom",minHeight=20)
        # self.dock(self.traceBackViewer,"Process Viewer",defaultArea="bottom")
        self.dock(self.logViewer,"日志输出",defaultArea="bottom")
        # self.prepare_menubar()
        # self.prepare_toolbar()
        self.prepare_ribbon()

        # self.selectContext.create_actions(parent=self)

        # self.selectContext.sigLineClicked.connect(self.projectTree.sig_createPort)
        self.selectContext.sigFaceClicked.connect(self.sig_selectFace)
        self.selectContext.sigBodyClicked.connect(self.sig_selectBody)

        # self.selectContext.sigFaceChoosed.connect(self.projectTree.sig_chooseFace)

        # self.projectTree.sigPickEdge.connect(self.pickEdge)
        self.projectTree.sigPickFace.connect(self.pickFace)
        

        # self.projectTree.sigRemoveSelectedEdge.connect(self.selectContext.remove_edge)
        self.projectTree.sigClearInterContext.connect(self.selectContext.clear)

        self.projectTree.sigTx.connect(self.cbxTxFill_1)
        self.projectTree.sigTxEnable.connect(self.cbxTxEnable)
        self.projectTree.sigFreq.connect(self.cbxFreqFill_1)
        self.projectTree.sigChooseList.connect(self.filter_value_generate)
        self.projectTree.sigVTypeList.connect(self.filter_vType_generate)
        
        self.projectTree.sigValueButtons.connect(self.filter_value_generate)
        # self.projectTree.sigChooseAxis.connect(self.filter_axis_generate)
        self.projectTree.sigValueButton_convert_disabled.connect(self.v_btn_convert_disabled)
        self.projectTree.sigValueButton_convert_checked.connect(self.v_btn_convert_checked)
        self.projectTree.sigChooseSurface.connect(self.filter_surface_generate)
        self.projectTree.sigPosition.connect(self.filter_postion_generate)
        self.projectTree.sigPFName.connect(self.initPFSelected)
        

        # self.modelViewer.register_select_callback(self.selectContext.body_clicked)
        self.modelViewer.register_select_callback(self.selectContext.line_clicked)
        self.modelViewer.register_select_callback(self.selectContext.face_clicked)
        self.modelViewer.register_select_callback(self.selectContext.body_clicked)
        self.modelViewer.register_select_callback(self.selectContext.point_clicked)


        self.projectTree.sigActivateTab.connect(self.tab_activate)
        self.projectTree.sigActivateToolbar.connect(self.activate_toolbar)

        #ribbon button action定义
        self.action_new_project=None
        self.action_open_project=None
        self.action_save_project=None
        self.action_saveAs_project=None

        self.progressTimer=QtCore.QTimer(self)

        self.prepare_actions_home()
        self.prepare_console()
        self.setup_logging()
        self.onLoad()
        self.restoreWindow()
        self.delay_load()
        # self.start_progress()
        central_widget_pos = self.centralWidget().mapToParent(self.centralWidget().rect().topLeft())

        # print(central_widget_pos.x(),central_widget_pos.y())
    def log_clear(self):
        self.logViewer.clear()
    def delay_load(self):
        self.licenseTimer=QtCore.QTimer(self)
        self.licenseTimer.timeout.connect(self.license_check)
        self.licenseTimer.start(1500)
        self.projectTree.loadProject(self._defaultProjectFile)
    # def start_progress(self):
       
    #     self.progressTimer=QtCore.QTimer(self)
    #     self.progressTimer.timeout.connect(self.update_progressbar)
    #     self.progressTimer.start(1000)
    #     self.progress_bar.setValue(0)
    # def update_progressbar(self):
    #     # print("start",self.progress_bar.minimum(),self.progress_bar.maximum(),self.progress_bar.value())
    #     cValue=self.progress_bar.value()+10
    #     if(cValue>=self.progress_bar.maximum()):
    #         self.progress_bar.setValue(self.progress_bar.maximum())
    #         self.progressTimer.stop()
            
    #         # print("end",self.progress_bar.minimum(),self.progress_bar.maximum(),self.progress_bar.value())
    #     else:
    #         self.progress_bar.setValue(cValue)
    # def clear_progressbar(self):
    #     #清空进度条
    #     self.progress_bar.reset()
    #     pass
    def initPFSelected(self,pfName:str):
        print("initPFSelected",pfName)
        menu_action=None
        pfName_menu=""
        if( pfName == "em_circuit"):
            pfName_menu="电磁-电路"
        elif(pfName == "thermal"):
            pfName_menu="热"
        elif(pfName == "struct"):
            pfName_menu="结构"
        elif(pfName == "thermal_struct"):
            pfName_menu="热-结构"
        elif(pfName == "thermal_struct_em_circuit"):
            pfName_menu="热-结构-电磁-电路"
        elif(pfName == "struct_em_circuit"):
            pfName_menu="结构-电磁-电路"
        elif(pfName == "em_circuit_thermal"):
            pfName_menu="电磁-电路-热"
        elif(pfName == "em_circuit_thermal_struct"):
            pfName_menu="电磁-电路-热-结构"

        for i,action in enumerate(self._menu_simulation_actions):
            if action.text() == pfName_menu:
                menu_action = action
                break
        if menu_action:
            self.update_icons(self._menu_simulation, menu_action)
        pass

    def startProgress(self):
        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.progressTimer.start(200)  # 每100毫秒更新一次
        self.progressTimer.timeout.connect(self.updateProgress)
        self.progress_bar.setTextVisible(False)
    def stopProgress(self):
        self.progressTimer.stop()
        self.progress_bar.setValue(0)
        self.progress_bar.setHidden(True)

    def updateProgress(self):
        current_value = self.progress_bar.value()
        if current_value < 100:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.progress_bar.setValue(0)
            

    def license_check(self):
        self.licenseTimer.stop()
        code,message=api_license.license_validated_date()
        if(code!=1):
            QtWidgets.QMessageBox.about(self,"License Error",message)
            self.close()
            sys.exit(0)

    def onLoad(self):

        self.viewPage.InitDriver()
        self.viewPage.qApp = QtWidgets.QApplication.instance()#app链接
        self.modelViewer.display_triedron()
        self.modelViewer.SetModeShaded()
        self.tabWidget.setTabVisible(2,False)
        self.tabWidget.setTabVisible(3,False)
        self.tabWidget.setTabVisible(4,False)
        self.tabWidget.setTabVisible(5,False)
        background_gradient_color1 = [219, 219, 219]
        background_gradient_color2 = [219, 219, 219]

        # background_gradient_color1 = [140, 211, 255]
        # background_gradient_color2 = [140, 211, 255]

        self.modelViewer.set_bg_gradient_color(background_gradient_color1, background_gradient_color2)

        # self._titleBar.setStyleSheet(self.themeUI.titleBar)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.projectTree.sig_createProject()
       
    def prepare_actions_home(self):
        self.action_new_project=QAction(icon('new'),'New',self,shortcut="ctrl+N",triggered=self.createProject)
        self.action_open_project=QAction(icon('open'),'Open',self,shortcut='ctrl+O',triggered=self.openProject)
        self.action_save_project=QAction(icon('save'),'Save',self,shortcut='ctrl+S',triggered=self.saveProject)
        self.action_saveAs_project=QAction(icon('save_as'),'Save As',self,shortcut='ctrl+shift+S',triggered=self.saveAsProject)

        self.addAction(self.action_new_project)
        self.addAction(self.action_open_project)
        self.addAction(self.action_save_project)
        self.addAction(self.action_saveAs_project)
        pass
        
    def closeEvent(self, event):
        self._2dViewer.closeEvent(event)
        self._3dViewer.closeEvent(event)
        self.meshViewer.closeEvent(event)
        self.saveWindow()
        # self.savePreferences()
        # self.saveComponentState()
        super(MainWindow, self).closeEvent(event)

    def set_solver_dgtd(self):
        if(self.btn_solver!=None):
            self.btn_solver.setText("DGTD")
        self.projectTree.set_solver("DGTD")

        pass
    def set_solver_fem_dgtd(self):
        if(self.btn_solver!=None):
            self.btn_solver.setText("FEM-DGTD")
        self.projectTree.set_solver("FEM-DGTD")

        pass

    def update_icons(self, menu:QMenu,selected_action:QAction):
        # 清空所有Action的图标
        for action in menu.actions():
            action.setIcon(QIcon())  # 清空图标
        
        # 设置当前选中Action的图标
        selected_action.setIcon(menuIcons.model_pick_select)  # 设置新的图标 

    def prepare_menubar(self):  # 主菜单准备函数

        menu = self.menuBar()

        menu_file = menu.addMenu('工程')
        menu_file.addActions(
        [
            QAction(menuIcons.home_new,"新建",self,triggered=self.createProject),
            QAction(menuIcons.home_open,"打开",self,triggered=self.openProject),
            QAction(menuIcons.home_save,"保存",self,triggered=self.saveProject),
            QAction(menuIcons.home_saveAs,"另存为",self,triggered=self.saveAsProject),
        ]
    )
        
       
        menu_model = menu.addMenu('几何')
        menu_model.addActions(
            [
                QAction(menuIcons.model_cuboid,"创建",self,triggered=self.createModel),
                QAction(menuIcons.model_import,"导入",self,triggered=self.importModel),
                QAction(menuIcons.model_export,"导出",self,triggered=self.exportModel),
                QAction(menuIcons.model_medium,"材料管理",self,triggered=self.noneAction),
            ]
        )

        menu_model_pick=QMenu("选择",self)
        menu_model_pick.addActions(
            [
                QAction(menuIcons.model_pick_point,"点",self,triggered=self.pickPoint),
                QAction(menuIcons.model_pick_edge,"线",self,triggered=self.pickEdge),
                QAction(menuIcons.model_pick_face,"面",self,triggered=self.pickFace),
                QAction(menuIcons.model_pick_body,"体",self,triggered=self.pickBody),
            ]
        )
        menu_model_tools=QMenu("工具",self)
        menu_model_tools.addActions(
            [
                QAction(menuIcons.model_exchange,"格式转换",self,triggered=self.exchangeModel),
                QAction(menuIcons.model_color,"颜色设置",self,triggered=self.setModelColor),
                QAction(menuIcons.post_ren_opacity,"透明度",self,triggered=self.setModelOpacity),
            ]
        )
        
        
        menu_model.addMenu(menu_model_pick)
        menu_model.addMenu(menu_model_tools)


        menu_mesh = menu.addMenu('网格')
        menu_mesh.addActions(
            [
                QAction(menuIcons.mesh_create, "创建",self,triggered=self.noneAction),
                # QAction(menuIcons.mesh_import, "导入",self,triggered=self.noneAction),
                QAction(menuIcons.mesh_export, "导出",self,triggered=self.noneAction),
                QAction(menuIcons.mesh_options, "选项",self,triggered=self.noneAction),

            ]
        )


        menu_simulation = menu.addMenu('物理场')
        action_em_circuit=QAction("电磁-电路",self,
                                  triggered=self.projectTree.action_pf_em_circuit)
        action_thermal=QAction("热",self,
                               triggered=self.projectTree.action_pf_thermal)
        action_struct=QAction("结构",self,
                              triggered=self.projectTree.action_pf_struct)
        action_thermal_struct=QAction("热-结构",self,
                                      triggered=self.projectTree.action_pf_thermal_struct)
        action_thermal_struct_em_circuit=QAction("热-结构-电磁-电路",self,
                                                 triggered=self.projectTree.action_pf_thermal_struct_em_circuit)
        action_struct_em_circuit=QAction("结构-电磁-电路",self,
                                         triggered=self.projectTree.action_pf_struct_em_circuit)
        action_em_circuit_thermal=QAction("电磁-电路-热",self,
                                          triggered=self.projectTree.action_pf_em_circuit_thermal)
        action_em_circuit_thermal_struct=QAction("电磁-电路-热-结构",self,
                                                 triggered=self.projectTree.action_pf_em_circuit_thermal_struct)
        
        action_em_circuit.triggered.connect(lambda: self.update_icons(menu_simulation, action_em_circuit))
        action_thermal.triggered.connect(lambda: self.update_icons(menu_simulation, action_thermal))
        action_struct.triggered.connect(lambda: self.update_icons(menu_simulation, action_struct))
        action_thermal_struct.triggered.connect(lambda: self.update_icons(menu_simulation, action_thermal_struct))
        action_thermal_struct_em_circuit.triggered.connect(lambda: self.update_icons(menu_simulation, action_thermal_struct_em_circuit))
        action_struct_em_circuit.triggered.connect(lambda: self.update_icons(menu_simulation, action_struct_em_circuit))
        action_em_circuit_thermal.triggered.connect(lambda: self.update_icons(menu_simulation, action_em_circuit_thermal))
        action_em_circuit_thermal_struct.triggered.connect(lambda: self.update_icons(menu_simulation, action_em_circuit_thermal_struct))

        self._menu_simulation= menu_simulation  # 保存菜单引用以便后续使用
        self._menu_simulation_actions= [
             action_em_circuit,
                action_thermal,
                action_struct,
                action_thermal_struct,
                action_thermal_struct_em_circuit,
                action_struct_em_circuit,
                action_em_circuit_thermal,
                action_em_circuit_thermal_struct,
        ]
        menu_simulation.addActions(self._menu_simulation_actions)
        menu_postprocess = menu.addMenu('结果分析')
        menu_postprocess_export=QMenu("导出",self)
        menu_postprocess_export.addActions(
            [
                QAction(menuIcons.post_export_data, "数据",self,triggered=self.postExportPoints),
                QAction(menuIcons.post_export_img, "图片",self,triggered=self.postExportImg),
            ]
        )
        menu_postprocess.addMenu(menu_postprocess_export)

        menu_postprocess_options=QMenu("显示设置",self)
        menu_postprocess_options.addActions(
            [
                QAction(menuIcons.post_ren_scalar, "颜色设置",self,triggered=self.setScalar),
                QAction(menuIcons.post_ren_points, "数据点",self,triggered=self.displayPostPoints),
                QAction(menuIcons.post_ren_surface, "表面云图",self,triggered=self.displaySurface),
            ]
        )
        menu_postprocess.addMenu(menu_postprocess_options)
        
        menu_view = menu.addMenu('视图')

        menu_view.addActions(
            [
                QAction(menuIcons.view_fit,"自适应",self,triggered=self.viewFit),
                QAction(menuIcons.view_iso,"ISO",self,triggered=self.viewISO),
                QAction(menuIcons.view_top,"顶部",self,triggered=self.viewTop),
                QAction(menuIcons.view_bottom,"底部",self,triggered=self.viewBottom),
                QAction(menuIcons.view_left,"左视图",self,triggered=self.viewLeft),
                QAction(menuIcons.view_right,"右视图",self,triggered=self.viewRight),
                QAction(menuIcons.view_front,"前视图",self,triggered=self.viewFront),
                QAction(menuIcons.view_back,"后视图",self,triggered=self.viewBack),
                QAction(menuIcons.view_wireframe,"线框",self,triggered=self.viewWireframe),
                QAction(menuIcons.view_shaded,"实体",self,triggered=self.viewShaded),
            ]
        )
        menu_help = menu.addMenu('帮助')

        menu_help.addActions(
            [
            QAction(icon('help'), '文档',  self, triggered=self.noneAction),
            QAction(icon('about'), '关于', self, triggered=self.noneAction),
            ]
        )    
        
    def prepare_toolbar(self):

        self.toolbar = QToolBar('Main toolbar', self,
                                objectName='Main toolbar')

        # for c in self.components.values():
        #     add_actions(self.toolbar, c.toolbarActions())
        self.toolbar.addActions(
            [
                QAction(menuIcons.home_new,"新建",self,triggered=self.createProject),
                QAction(menuIcons.home_open,"打开",self,triggered=self.openProject),
                QAction(menuIcons.home_save,"保存",self,triggered=self.saveProject),
                QAction(menuIcons.home_saveAs,"另存为",self,triggered=self.saveAsProject),
                QAction(menuIcons.model_cuboid,"建模",self,triggered=self.createModel),
            ]
        )
        self.toolbar.addSeparator()
        self.toolbar.addActions(
            [
                QAction(menuIcons.sim_p,"并行",self,triggered=self.projectTree.setMPI),
                QAction(menuIcons.mesh_transform,"Metis网格分区",self,triggered=self.projectTree.mpmetis_split),
                QAction(menuIcons.home_run,"运行",self,triggered=self.runSimulation),
                QAction(menuIcons.home_stop,"停止",self,triggered=self.stopSimulation),
            ]
        )
        self.toolbar.addSeparator()
        self.toolbar.addActions(    
            [
              
                QAction(menuIcons.model_pick_point,"点",self,triggered=self.pickPoint),
                QAction(menuIcons.model_pick_edge,"线",self,triggered=self.pickEdge),
                QAction(menuIcons.model_pick_face,"面",self,triggered=self.pickFace),
                QAction(menuIcons.model_pick_body,"体",self,triggered=self.pickBody),
                QAction(menuIcons.post_ren_opacity,"透明度",self,triggered=self.setModelOpacity),
            ]
        )
        self.toolbar.addSeparator()
        self.toolbar.addActions(
            [
                QAction(menuIcons.view_fit,"自适应",self,triggered=self.viewFit),
                QAction(menuIcons.view_iso,"ISO",self,triggered=self.viewISO),
                QAction(menuIcons.view_top,"顶部",self,triggered=self.viewTop),
                QAction(menuIcons.view_bottom,"底部",self,triggered=self.viewBottom),
                QAction(menuIcons.view_left,"左视图",self,triggered=self.viewLeft),
                QAction(menuIcons.view_right,"右视图",self,triggered=self.viewRight),
                QAction(menuIcons.view_front,"前视图",self,triggered=self.viewFront),
                QAction(menuIcons.view_back,"后视图",self,triggered=self.viewBack),
                QAction(menuIcons.view_wireframe,"线框",self,triggered=self.viewWireframe),
                QAction(menuIcons.view_shaded,"实体",self,triggered=self.viewShaded),
               
            ]
        )

        self.addToolBar(self.toolbar)

        return
        
        self._ribbon = RibbonWidget(self)
        self._ribbon.setStyleSheet(self.themeUI.ribbon)
        # self._ribbon.setMinimumWidth(1000)
        self.addToolBar(self._ribbon)
        self.add_tab_home()
        if(not DEBUG_MODE):
            self.add_tab_model()
            # self.add_tab_exciation_port()
            # self.add_tab_request()
            # self.add_tab_mesh()
            self.add_tab_simulation()
            self.add_tab_postprocess()
            self.add_tab_view()
            # self.add_tab_about()
        self.filter_main_generate()
        
        pass
    def prepare_ribbon(self):
        self._ribbon = RibbonWidget(self)
        self._ribbon.setStyleSheet(self.themeUI.ribbon)
        # self._ribbon.setMinimumWidth(1000)
        self.addToolBar(self._ribbon)
        self.add_tab_home()
        if(not DEBUG_MODE):
            self.add_tab_model()
            # self.add_tab_exciation_port()
            # self.add_tab_request()
            # self.add_tab_mesh()
            self.add_tab_simulation()
            self.add_tab_postprocess()
            self.add_tab_view()
            # self.add_tab_about()
        # self.filter_main_generate()

    def activate_toolbar(self,tabIndex:int):
        self._ribbon.activate_tab(tabIndex)
    def add_ribbon_button(self,pane:RibbonPane,btnObject:menuButton,btnIcon:QIcon=None,is_large:bool=True):
        '''向指定的pane增加一个按钮，当icon为none时，使用系统指定的图标【根据text来查找】
        '''
        btn=RibbonButton(self,is_large)
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        btn.setStyleSheet(self.themeUI.ribbonButton)
        btn.setText(btnObject.text)
        btn.setToolTip(btnObject.toolTip)
        if(btnIcon!=None):
            btn.setIcon(btnIcon)
        pane.add_ribbon_widget(btn)
        
        return btn
        pass
    def get_ribbon_pane(self,tab:RibbonTab,paneName:str):
        pane=tab.add_ribbon_pane(paneName)
        
        pane.setStyleSheet(self.themeUI.ribbonPane)
        return pane

    def add_tab_home(self):
        home_tab=self._ribbon.add_ribbon_tab(menuPool.home_base)
        # print("home tab font ",home_tab.font().family(),home_tab.font().pointSize())

        pane_project = self.get_ribbon_pane(home_tab,menuPool.home_project)
        pane_simulation =self.get_ribbon_pane(home_tab,menuPool.home_simulation)
        
        # pane_filter_value=self.get_ribbon_pane(home_tab,menuPool.value_filter)
        # pane_filter_axis=self.get_ribbon_pane(home_tab,menuPool.axis_x)
      

        self.add_ribbon_button(pane_project,menuPool.home_project_new,menuIcons.home_new).clicked.connect(self.createProject)
        self.add_ribbon_button(pane_project,menuPool.home_project_open,menuIcons.home_open).clicked.connect(self.openProject)
        self.add_ribbon_button(pane_project,menuPool.home_project_save,menuIcons.home_save).clicked.connect(self.saveProject)
        self.add_ribbon_button(pane_project,menuPool.home_project_saveAs,menuIcons.home_saveAs).clicked.connect(self.saveAsProject)
    
        self.add_ribbon_button(pane_simulation,menuPool.home_simulation_run,menuIcons.home_run).clicked.connect(self.runSimulation)
        self.add_ribbon_button(pane_simulation,menuPool.home_simulation_stop,menuIcons.home_stop).clicked.connect(self.stopSimulation)

        self.tab_home=home_tab
        
        
        
    def filter_main_generate(self):
        row_height=25
        styleStr="""
            QLabel,QComboBox {
                padding: 2px;
                margin:1px;
                font-size:14px;
                font-family:Arial, 'Segoe UI', Tahoma, "Microsoft YaHei", sans-serif;
                height:25px;
                
            }
            QLabel{
            width:50px;
            }
            QComboBox{
                width:90px;
            }
        """
        home_tab=self.tab_home
        tab_post_process=self.tab_post_process

        pane_filter_main =self.get_ribbon_pane(home_tab,menuPool.home_filter)
        tab_post_process.add_ribbon_pane_widget(pane_filter_main)
        
        cbx_grid=pane_filter_main.add_grid_widget(600*gui_scale())

        lblTX=QLabel(menuPool.lblTX)
        cbxTX=QComboBox(self)
        lblTX.setStyleSheet(styleStr)
        cbxTX.setStyleSheet(styleStr)
        # lblTX.setFont(self._font)
        # cbxTX.setFont(self._font)
        # cbxTX.setStyleSheet(self.cbxStyle)

        lblFrequency=QLabel(menuPool.lblFrequency)
        cbxFrequency=QComboBox(self)
        lblFrequency.setStyleSheet(styleStr)
        cbxFrequency.setStyleSheet(styleStr)

        lblVType=QLabel(menuPool.lblVType)
        cbxVType=QComboBox(self)
        lblVType.setStyleSheet(styleStr)
        cbxVType.setStyleSheet(styleStr)

        lblSurface=QLabel(menuPool.lblSurface)
        cbxSurface=QComboBox(self)
        lblSurface.setStyleSheet(styleStr)
        cbxSurface.setStyleSheet(styleStr)

        lblPosition=QLabel(menuPool.lblPosition)
        cbxPosition=QComboBox(self)
        lblPosition.setStyleSheet(styleStr)
        cbxPosition.setStyleSheet(styleStr)

        lblXAxis=QLabel(menuPool.lblXAxis)
        cbxAxis=QComboBox(self)
        lblXAxis.setStyleSheet(styleStr)
        cbxAxis.setStyleSheet(styleStr)

        lblXAxis.setEnabled(False)
        cbxAxis.setEnabled(False)
        lblSurface.setEnabled(False)
        cbxSurface.setEnabled(False)
        lblPosition.setEnabled(False)
        cbxPosition.setEnabled(False)

        cbx_grid.addWidget(lblSurface,1,1)
        cbx_grid.addWidget(cbxSurface,1,2)

        
        cbx_grid.addWidget(lblTX,1,1)
        cbx_grid.addWidget(cbxTX,1,2)
        cbx_grid.addWidget(lblFrequency,2,1)
        cbx_grid.addWidget(cbxFrequency,2,2)
        cbx_grid.addWidget(lblVType,3,1)
        cbx_grid.addWidget(cbxVType,3,2)

        cbx_grid.addWidget(lblSurface,1,3)
        cbx_grid.addWidget(cbxSurface,1,4)

        cbx_grid.addWidget(lblPosition,2,3)
        cbx_grid.addWidget(cbxPosition,2,4)

        cbx_grid.addWidget(lblXAxis,3,3)
        cbx_grid.addWidget(cbxAxis,3,4)


        cbxTX.currentIndexChanged.connect(self.cbx_tx_changed)
        cbxFrequency.currentIndexChanged.connect(self.cbx_freq_changed)
        cbxVType.currentIndexChanged.connect(self.cbx_vtype_changed)
        cbxSurface.currentIndexChanged.connect(self.cbx_surface_changed)
        cbxPosition.currentIndexChanged.connect(self.cbx_position_changed)
      

        self.cbxTX=cbxTX
        self.cbxFrequency=cbxFrequency
        self.cbxVType=cbxVType
        self.grid_main=cbx_grid
        self.cbxSurface=cbxSurface
        self.cbxPosition=cbxPosition
        self.cbxXAxis=cbxAxis

        self.lblSurface=lblSurface
        self.lblPosition=lblPosition
        self.lblXAxis=lblXAxis

    def filter_vType_generate(self,vTypeList:list):
        self.cbxVType.disconnect()
        self.cbxVType.clear()
        for s in vTypeList:
            self.cbxVType.addItem(s)
        self.cbxVType.currentIndexChanged.connect(self.cbx_vtype_changed)
    def filter_postion_generate(self,positionList:list):
        self.cbxPosition.disconnect()
        self.cbxPosition.clear()
        self.lblPosition.setEnabled(True)
        self.cbxPosition.setEnabled(True)
        for s in positionList:
            self.cbxPosition.addItem(str(s))
        if(len(positionList)<=1):
            self.lblPosition.setEnabled(False)
            self.cbxPosition.setEnabled(False)
        self.cbxPosition.currentIndexChanged.connect(self.cbx_position_changed)

        pass

    def filter_value_generate(self,checkedKeys:dict,singleChoose=False,db_ConvertKeys:dict={}):
        home_tab=self.tab_home
        tab_post_process=self.tab_post_process
        pane_filter_value=self.dic_pane["filter_value"]
        if(pane_filter_value!=None):#已存在过，则删除pane
            home_tab.remove_ribbon_pane(pane_filter_value)
            pane_filter_value.deleteLater()

        pane_filter_convert=self.dic_pane["filter_convert"]
        if(pane_filter_convert!=None):#已存在过，则删除pane
            tab_post_process.remove_ribbon_pane(pane_filter_convert)
            pane_filter_convert.deleteLater()

        pane_filter_value=self.get_ribbon_pane(home_tab,menuPool.value_filter)
        tab_post_process.add_ribbon_pane_widget(pane_filter_value)
        self.dic_pane["filter_value"]=pane_filter_value
        grid_value=pane_filter_value.add_grid_widget(600*gui_scale())
        self.grid_buttons["single"]=singleChoose


    
        pane_filter_convert=self.get_ribbon_pane(tab_post_process,menuPool.value_convert)
        tab_post_process.add_ribbon_pane_widget(pane_filter_convert)
        self.dic_pane["filter_convert"]=pane_filter_convert
        grid_db=pane_filter_convert.add_grid_widget(200*gui_scale())

        btn_db=QPushButton(self)
        btn_db.setText(PostFilter.dbTitle)
        btn_db.setCheckable(True)
        btn_db.setDisabled(True)
        btn_db.setStyleSheet(self.btnStyle)
        btn_db.clicked.connect(lambda checked, b=btn_db: self.v_btn_convert_clicked(b))
        grid_db.addWidget(btn_db,1,1)
        self._btn_db:QPushButton=btn_db
        # self._db_convertKeys=db_ConvertKeys


        #生成物理量筛选
        for btn in self.grid_buttons["btnList"]:
            grid_value.removeWidget(btn)
            btn.deleteLater()
        
        self.grid_buttons["btnList"].clear()
        btnList=[]
        for k,v in checkedKeys.items():
            btn=QPushButton(self)
            
            # btn.setFlat(False)
            btn.setText(k)
            btn.setCheckable(True)
            btn.setStyleSheet(self.btnStyle)
            btn.clicked.connect(lambda checked, b=btn: self.v_btn_clicked(b))
            if(v):
                btn.setChecked(True)
                #选中了物理量
                if(k in db_ConvertKeys.keys()):
                    btn_db.setDisabled(False)

            btnList.append(btn)
            self.grid_buttons["btnList"].append(btn)

        row_current=1
        col_current=1
    
        for btn in btnList:
            grid_value.addWidget(btn,row_current,col_current)
            row_current+=1
            if(row_current>3):
                row_current=1
                col_current+=1
        self.grid_value=grid_value

        
    def filter_value_convert_generate(self,checkedKeys_convert:dict=None):
        tab_post_process=self.tab_post_process
        pane_filter_value=self.dic_pane["filter_convert"]
        if(pane_filter_value!=None):#已存在过，则删除pane
            tab_post_process.remove_ribbon_pane(pane_filter_value)
            pane_filter_value.deleteLater()

        pane_filter_value=self.get_ribbon_pane(tab_post_process,menuPool.value_convert)
        tab_post_process.add_ribbon_pane_widget(pane_filter_value)
        self.dic_pane["filter_convert"]=pane_filter_value

        if(checkedKeys_convert is not None):
            grid_db=pane_filter_value.add_grid_widget(200*gui_scale())
            btnList=[]
            for k,v in checkedKeys_convert.items():
                btn=QPushButton(self)
                btn.setText(k)
                btn.setCheckable(True)
                btn.setStyleSheet(self.btnStyle)
                btn.clicked.connect(lambda checked, b=btn: self.v_btn_convert_clicked(b))
                if(v):
                    btn.setChecked(True)
                btnList.append(btn)
            row_current=1
            col_current=1
            for btn in btnList:
                grid_db.addWidget(btn,row_current,col_current)
                row_current+=1
                if(row_current>3):
                    row_current=1
                    col_current+=1
                
        pass
    def filter_surface_generate(self,surfaceList:list=[],showXAxis=False):
        #生成选择面＆ 选择位置 提供默认面索引和位置索引
        self.cbxSurface.disconnect()
        self.lblSurface.setEnabled(True)
        self.cbxSurface.setEnabled(True)
        self.lblXAxis.setEnabled(True)
        self.cbxXAxis.setEnabled(True)
        self.cbxSurface.clear()
        self.cbxXAxis.clear()
        for s in surfaceList:
            self.cbxSurface.addItem(s)
        # self.cbxSurface.setCurrentIndex(surfaceIndex)
        self.cbxSurface.currentIndexChanged.connect(self.cbx_surface_changed)
        if(len(surfaceList)<=1):
            self.cbxSurface.setEnabled(False)
            self.lblSurface.setEnabled(False)
        if(len(surfaceList)<1 or not showXAxis):
            self.lblXAxis.setEnabled(False)
            self.cbxXAxis.setEnabled(False)
        if(len(surfaceList)>=1 and showXAxis):
            self.filter_axis_generate(surfaceList[0])

      
        # cbxSurface.currentIndexChanged.connect(self.cbx_surface_changed)
        # cbxPosition.currentIndexChanged.connect(self.cbx_position_changed)
        # self.cbxSurface=cbxSurface
        # self.cbxPosition=cbxPosition



    def filter_axis_generate(self,surfaceName:str):
        #横轴筛选的维度 跟面有关 xy面时，可选X/Y xz时可选X/Z yz时可选Y/Z
        self.cbxXAxis.disconnect()
        xAxisList=[]
        if(surfaceName=="XY面"):
            xAxisList.append("X")
            xAxisList.append("Y")
        elif(surfaceName=="XZ面"):
            xAxisList.append("X")
            xAxisList.append("Z")
        elif(surfaceName=="YZ面"):
            xAxisList.append("Y")
            xAxisList.append("Z")
        self.cbxXAxis.clear()
        for s in xAxisList:
            self.cbxXAxis.addItem(s)
        self.cbxXAxis.currentIndexChanged.connect(self.projectTree.xAxisChanged)
        pass

       
    def v_btn_clicked(self,btn:QPushButton):
        # print("clicked",btn.text())
        self.projectTree.valueBtnChanged(btn.text())
        if(self.grid_buttons["single"]):
            for item in self.grid_buttons["btnList"]:
                if(btn!=item):
                    item.setChecked(False)
    def v_btn_convert_disabled(self,db_convert:bool=True):
        if(self._btn_db is not None):
            self._btn_db.setDisabled(not db_convert)
        pass
    def v_btn_convert_checked(self,db_convert:bool=False):
        if(self._btn_db is not None):
            self._btn_db.setChecked(db_convert)
        pass
    def v_btn_convert_clicked(self,btn:QPushButton):
        # print("clicked",btn.text())
        self.projectTree.valueConvertBtnExchanged(btn.text())
        # if(self.grid_buttons["single"]):
        #     for item in self.grid_buttons["btnList"]:
        #         if(btn!=item):
        #             item.setChecked(False)
                
        # self.projectTree.render_results()
        pass
    def axis_btn_checked(self,btn:QPushButton):
        self.projectTree.axisBtnChanged(btn.text())
        self.axis_buttons["checked"]=btn
        for item in self.axis_buttons["btnList"]:
            if(btn!=item):
                item.setChecked(False)
            else:
                item.setChecked(True)

    def cbx_freq_changed(self,index:int):
        print("freq changed",index)
        pass
    def cbx_tx_changed(self,index:int):
        print("tx changed",index)
        pass
    def cbx_vtype_changed(self,index:int):
        print("vtype changed",index)
        self.projectTree.vTypeChanged(index)
        pass
    def cbx_surface_changed(self,index:int):
        print("surface changed",index)
        self.projectTree.surfaceChanged(index)
        if(self.cbxXAxis.isEnabled()):
            self.filter_axis_generate(self.cbxSurface.currentText())
        pass
    def cbx_position_changed(self,index:int):
        print("position changed",index)
        self.projectTree.positionChanged(index)
        pass
        
    def add_tab_model(self):
        model_tab = self._ribbon.add_ribbon_tab(menuPool.model_base) 
        pane_geometry = self.get_ribbon_pane(model_tab,menuPool.model_geomtry)
        pane_pick = self.get_ribbon_pane(model_tab,menuPool.model_pick)
        # pane_create=self.get_ribbon_pane(model_tab,menuPool.model_create)
        pane_tools=self.get_ribbon_pane(model_tab,menuPool.model_tools)
        

        self.add_ribbon_button(pane_geometry,menuPool.model_geomtry_import,menuIcons.model_import).clicked.connect(self.projectTree.nodeAction_ImportModel)
        self.add_ribbon_button(pane_geometry,menuPool.model_geomtry_export,menuIcons.model_export).clicked.connect(self.projectTree.nodeAction_ExportModel)
        self.add_ribbon_button(pane_geometry,menuPool.model_geomtry_medium,menuIcons.model_medium).clicked.connect(self.projectTree.nodeAction_ModelMediaSetting)

        

        self.add_ribbon_button(pane_pick,menuPool.model_pick_point,menuIcons.model_pick_point).clicked.connect(self.selectContext.Action_select_point)
        self.add_ribbon_button(pane_pick,menuPool.model_pick_edge,menuIcons.model_pick_edge).clicked.connect(self.pickEdge)
        self.add_ribbon_button(pane_pick,menuPool.model_pick_face,menuIcons.model_pick_face).clicked.connect(self.pickFace)
        self.add_ribbon_button(pane_pick,menuPool.model_pick_body,menuIcons.model_pick_body).clicked.connect(self.selectContext.Action_select_body)

        # self.add_ribbon_button(pane_create,menuPool.model_create_cuboid,menuIcons.model_cuboid).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_sphere,menuIcons.model_sphere).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_cylinder,menuIcons.model_cylinder).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_cone,menuIcons.model_cone).clicked.connect(self.noneAction)

        # self.add_ribbon_button(pane_create,menuPool.model_create_rectangle,menuIcons.mode_rectangle).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_polygon,menuIcons.model_polygon).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_line,menuIcons.model_line).clicked.connect(self.noneAction)
        # self.add_ribbon_button(pane_create,menuPool.model_create_polygonLine,menuIcons.mode_pline).clicked.connect(self.noneAction)

        self.add_ribbon_button(pane_tools,menuPool.model_tools_exchange,menuIcons.model_exchange).clicked.connect(self.exchangeModel)
        # self.add_ribbon_button(pane_tools,menuPool.model_tools_color,menuIcons.model_color).clicked.connect(self.setModelColor)

        
        pass
    
    def add_tab_exciation_port(self):
        tab = self._ribbon.add_ribbon_tab(menuPool.excitaion_base) 

        pane_settins =self.get_ribbon_pane(tab,menuPool.excitaion_settings)
        pane_ports=self.get_ribbon_pane(tab,menuPool.excitaion_ports)
        pane_sources=self.get_ribbon_pane(tab,menuPool.excitaion_sources)
        pane_loads=self.get_ribbon_pane(tab,menuPool.excitaion_loads)
 
        self.add_ribbon_button(pane_settins,menuPool.excitaion_settings_freq,menuIcons.exc_frequency).clicked.connect(self.projectTree.nodeAction_FrequencyProperties)
        self.add_ribbon_button(pane_settins,menuPool.excitaion_settings_power,menuIcons.exc_power).clicked.connect(self.projectTree.nodeAction_Power)

        self.add_ribbon_button(pane_ports,menuPool.excitaion_ports_edge,menuIcons.exc_edge_port).clicked.connect(self.projectTree.nodeAction_AddPort)
        self.add_ribbon_button(pane_sources,menuPool.excitaion_sources_vol,menuIcons.exc_v_source).clicked.connect(self.projectTree.nodeAction_AddSource)
        self.add_ribbon_button(pane_loads,menuPool.excitaion_loads_addLoad,menuIcons.exc_add_load).clicked.connect(self.projectTree.nodeAction_Loads)

        pass

    def add_tab_request(self):
        tab = self._ribbon.add_ribbon_tab(menuPool.request_base) 
        pane_solution = self.get_ribbon_pane(tab,menuPool.request_solution)

        self.add_ribbon_button(pane_solution,menuPool.excitaion_settings_freq,menuIcons.exc_frequency).clicked.connect(self.projectTree.nodeAction_FrequencyProperties)

        self.add_ribbon_button(pane_solution,menuPool.request_solution_ffr,menuIcons.req_ffr).clicked.connect(self.projectTree.nodeAction_AddFFR)
        self.add_ribbon_button(pane_solution,menuPool.request_solution_nfr,menuIcons.req_nfr).clicked.connect(self.projectTree.nodeAction_AddNFR)
        self.add_ribbon_button(pane_solution,menuPool.request_solution_nf,menuIcons.req_nf).clicked.connect(self.projectTree.nodeAction_AddNF)
        self.add_ribbon_button(pane_solution,menuPool.request_solution_emi,menuIcons.req_emi).clicked.connect(self.projectTree.nodeAction_AddEMI)

        pass
        
        
    def add_tab_mesh(self):
        tab = self._ribbon.add_ribbon_tab(menuPool.mesh_base) 
        pane_file = self.get_ribbon_pane(tab,menuPool.mesh_file)
        pane_meshing=self.get_ribbon_pane(tab,menuPool.mesh_meshing)
        pane_tools=self.get_ribbon_pane(tab,menuPool.mesh_tools)

        self.add_ribbon_button(pane_file,menuPool.mesh_file_import,menuIcons.mesh_import).clicked.connect(self.projectTree.nodeAction_ImportMesh)
        self.add_ribbon_button(pane_file,menuPool.mesh_file_export,menuIcons.mesh_export).clicked.connect(self.projectTree.nodeAction_ExportMesh)
        self.add_ribbon_button(pane_meshing,menuPool.mesh_meshing_create,menuIcons.mesh_create).clicked.connect(self.projectTree.nodeAction_CreateMesh)
        self.add_ribbon_button(pane_meshing,menuPool.mesh_meshing_localsize,menuIcons.mesh_options).clicked.connect(self.meshSetLocalSize)
        self.add_ribbon_button(pane_meshing,menuPool.mesh_meshing_refine,menuIcons.mesh_refine).clicked.connect(self.noneAction)
        

        self.add_ribbon_button(pane_tools,menuPool.mesh_tools_find,menuIcons.mesh_find).clicked.connect(self.findElement)
        self.add_ribbon_button(pane_tools,menuPool.mesh_tools_points,menuIcons.mesh_points).clicked.connect(self.displayVertex)
        self.add_ribbon_button(pane_tools,menuPool.mesh_tools_measure,menuIcons.mesh_measure).clicked.connect(self.measureDistance)
        self.add_ribbon_button(pane_tools,menuPool.mesh_tools_transform,menuIcons.mesh_transform).clicked.connect(self.vtkRotate)
        pass

    def init_toolbuttons_solver_base(self):
        s_tab=self.tab_sim
        pane_solver= self.get_ribbon_pane(s_tab,"求解器")
        btn_solver=self.add_ribbon_button(pane_solver,
                                    menuPool.solver_base,
                                    menuIcons.model_color)
        self.btn_solver=btn_solver
        btn_solver.setFont(self._font)

         # 创建一个下拉菜单
        dropdown_menu_solver = QMenu(btn_solver)
        dropdown_menu_solver.setFont(self._font)
        # 添加一些菜单项
        action1 = QAction("DGTD", self,triggered=self.set_solver_dgtd)
        action2 = QAction("FEM-DGTD", self,triggered=self.set_solver_fem_dgtd)


        action1.triggered.connect(lambda: self.update_icons(dropdown_menu_solver, action1))
        action2.triggered.connect(lambda: self.update_icons(dropdown_menu_solver, action2))
    
        dropdown_menu_solver.addAction(action1)
        dropdown_menu_solver.addAction(action2)
        # 将下拉菜单与按钮关联
        btn_solver.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        btn_solver.setMenu(dropdown_menu_solver)
        pass
    
    def add_tab_simulation(self):
        s_tab = self._ribbon.add_ribbon_tab(menuPool.simualtion_base) 
        self.tab_sim=s_tab
        # pane_excitation = self.get_ribbon_pane(s_tab,menuPool.simualtion_base)
        self.init_toolbuttons_solver_base()
        pane_request=self.get_ribbon_pane(s_tab,menuPool.simualtion_request)
        
        # pane_prop= self.get_ribbon_pane(s_tab,menuPool.simualtion_prop)
        pane_operator = self.get_ribbon_pane(s_tab,menuPool.simualtion_operator)
        

    
        # self.add_ribbon_button(pane_solution,menuPool.request_solution_ffr,menuIcons.req_ffr).clicked.connect(self.projectTree.nodeAction_AddFFR)
        # self.add_ribbon_button(pane_excitation,menuPool.solver_base,menuIcons.model_color).clicked.connect(self.projectTree.nodeAction_tx)

        self.add_ribbon_button(pane_request,menuPool.param_time,menuIcons.exc_frequency).clicked.connect(self.projectTree.nodeAction_TimeProperties)
        self.add_ribbon_button(pane_request,menuPool.param_obs_point,treeIcons.gdtd_req_points).clicked.connect(self.projectTree.nodeAction_NFProperties)
        self.add_ribbon_button(pane_request,menuPool.param_obs_domain,treeIcons.gdtd_req_domain).clicked.connect(self.projectTree.nodeAction_DomainProperties)
        self.add_ribbon_button(pane_request,menuPool.param_obs_ffr,menuIcons.req_ffr).clicked.connect(self.projectTree.nodeAction_FFRProperties)
       
        self.add_ribbon_button(pane_operator,menuPool.simualtion_prop_parallel,menuIcons.sim_p).clicked.connect(self.projectTree.nodeAction_SetMPI)

        self.add_ribbon_button(pane_operator,menuPool.simulation_input_generate,menuIcons.mesh_export).clicked.connect(self.projectTree.simulation_input_generate)
        self.add_ribbon_button(pane_operator,menuPool.simulation_exe_run,menuIcons.post_ani_play).clicked.connect(self.projectTree.simulation_run_directly)
        self.add_ribbon_button(pane_operator,menuPool.simualtion_operator_run,menuIcons.sim_run).clicked.connect(self.runSimulation)
        self.add_ribbon_button(pane_operator,menuPool.simualtion_operator_stop,menuIcons.sim_stop).clicked.connect(self.stopSimulation)
       
        
       
        pass
    def add_tab_postprocess(self):
        tab = self._ribbon.add_ribbon_tab(menuPool.post_base) 
        pane_common = self.get_ribbon_pane(tab,menuPool.post_common)
        # pane_filter= self.get_ribbon_pane(tab,menuPool.post_filter)
        pane_render= self.get_ribbon_pane(tab,menuPool.post_render)
        # pane_animate= self.get_ribbon_pane(tab,menuPool.post_animate)
        

        self.add_ribbon_button(pane_common,menuPool.post_common_exportData,menuIcons.post_export_data).clicked.connect(self.postExportPoints)
        self.add_ribbon_button(pane_common,menuPool.post_common_exportImage,menuIcons.post_export_img).clicked.connect(self.postExportImg)

        self.add_ribbon_button(pane_render,menuPool.post_render_scalar,menuIcons.post_ren_scalar).clicked.connect(self.setScalar)
        self.add_ribbon_button(pane_render,menuPool.post_render_points,menuIcons.post_ren_points).clicked.connect(self.displayPostPoints)
        # self.add_ribbon_button(pane_render,menuPool.post_render_grid,menuIcons.post_ren_grid).clicked.connect(self.noneAction)
        self.add_ribbon_button(pane_render,menuPool.post_render_surface,menuIcons.post_ren_surface).clicked.connect(self.displaySurface)
        self.add_ribbon_button(pane_render,menuPool.post_render_opacity,menuIcons.post_ren_opacity).clicked.connect(self.noneAction)
        self.add_ribbon_button(pane_render,menuPool.post_render_size,menuIcons.post_ren_size).clicked.connect(self.noneAction)

        self.tab_post_process=tab
        pass
    def add_tab_view(self):
        tab = self._ribbon.add_ribbon_tab(menuPool.view_base) 
        pane_preset = self.get_ribbon_pane(tab,menuPool.view_preset)
        pane_zoom = self.get_ribbon_pane(tab,menuPool.view_zoom)
        pane_pan = self.get_ribbon_pane(tab,menuPool.view_pan)
        pane_rotate= self.get_ribbon_pane(tab,menuPool.view_rotate)

        self.add_ribbon_button(pane_preset,menuPool.view_preset_fit,menuIcons.view_fit).clicked.connect(self.viewFit)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_iso,menuIcons.view_iso).clicked.connect(self.viewISO)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_top,menuIcons.view_top).clicked.connect(self.viewTop)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_bottom,menuIcons.view_bottom).clicked.connect(self.viewBottom)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_front,menuIcons.view_front).clicked.connect(self.viewFront)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_back,menuIcons.view_back).clicked.connect(self.viewBack)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_left,menuIcons.view_left).clicked.connect(self.viewLeft)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_right,menuIcons.view_right).clicked.connect(self.viewRight)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_wireframe,menuIcons.view_wireframe).clicked.connect(self.viewWireframe)
        self.add_ribbon_button(pane_preset,menuPool.view_preset_shade,menuIcons.view_shaded).clicked.connect(self.viewShaded)

        self.add_ribbon_button(pane_zoom,menuPool.view_zoom_in,menuIcons.view_zoom_in).clicked.connect(self.viewZoomIn)
        self.add_ribbon_button(pane_zoom,menuPool.view_zoom_out,menuIcons.view_zoom_out).clicked.connect(self.viewZoomOut)

        self.add_ribbon_button(pane_pan,menuPool.view_pan_left,menuIcons.view_pan_left).clicked.connect(self.viewPanLeft)
        self.add_ribbon_button(pane_pan,menuPool.view_pan_right,menuIcons.view_pan_right).clicked.connect(self.viewPanRight)
        self.add_ribbon_button(pane_pan,menuPool.view_pan_up,menuIcons.view_pan_up).clicked.connect(self.viewPanUp)
        self.add_ribbon_button(pane_pan,menuPool.view_pan_down,menuIcons.view_pan_down).clicked.connect(self.viewPanDown)

        self.add_ribbon_button(pane_rotate,menuPool.view_rotate_thetaAdd,menuIcons.view_r_thetaAdd).clicked.connect(self.viewRotateThetaAdd)
        self.add_ribbon_button(pane_rotate,menuPool.view_rotate_thetaDec,menuIcons.view_r_thetaDec).clicked.connect(self.viewRotateThetaDec)
        self.add_ribbon_button(pane_rotate,menuPool.view_rotate_phiAdd,menuIcons.view_r_phiAdd).clicked.connect(self.viewRotatePhiAdd)
        self.add_ribbon_button(pane_rotate,menuPool.view_rotate_phiDec,menuIcons.view_r_phiDec).clicked.connect(self.viewRotatePhiDec)
       

        pass
    def add_tab_about(self):
        tab = self._ribbon.add_ribbon_tab("About") 
        pane1 = tab.add_ribbon_pane("Module1")
        btn11=RibbonButton(self,True)
        btn11.setText("Func1.1")
        btn11.setToolTip("Function 1-1")
        btn11.setIcon(icon("th-list"))
        btn11.clicked.connect(self.noneAction)
        pane1.add_ribbon_widget(btn11)

        btn12=RibbonButton(self,True)
        btn12.setText("Func1.2")
        btn12.setToolTip("Function 2")
        btn12.setIcon(icon("th-list"))
        btn12.clicked.connect(self.noneAction)
        pane1.add_ribbon_widget(btn12)

        pane2 = tab.add_ribbon_pane("Module2")
        btn21=RibbonButton(self,True)
        btn21.setText("Function2.1")
        btn21.setToolTip("Function 2-1")
        btn21.setIcon(icon("th-list"))
        btn21.clicked.connect(self.noneAction)
        pane2.add_ribbon_widget(btn21)

        btn22=RibbonButton(self,True)
        btn22.setText("Function2.2")
        btn22.setToolTip("Function 2-2")
        btn22.setIcon(icon("th-list"))
        btn22.clicked.connect(self.noneAction)
        pane2.add_ribbon_widget(btn22)


        btn23=RibbonButton(self,True)
        btn23.setText("Function2.3")
        btn23.setToolTip("Function 2-3")
        btn23.setIcon(icon("th-list"))
        btn23.clicked.connect(self.noneAction)
        pane2.add_ribbon_widget(btn23)
        pass

    def noneAction(self):
        QtWidgets.QMessageBox.about(self,"tips","The feature to be finished next version,please wait.")
        pass
    def createProject(self):
        self.projectTree.sig_createProject()
        pass
    def openProject(self):
        self.projectTree.loadProject()
        pass
    def saveProject(self):
        self.projectTree.nodeAction_SaveProject()
        pass
    def saveAsProject(self):
        self.projectTree.nodeAction_SaveProjectAs()
        pass
    def runSimulation(self):
        self.projectTree.nodeAction_RunSimulation()
    def stopSimulation(self):
        self.projectTree.nodeAction_StopSimulation()
    def createModel(self):
        #几何建模
        try:
            cadDataPath=os.path.join(os.environ['APPDATA'])

            baseDir=os.path.dirname(os.path.abspath(sys.executable))
            cadExeFile=baseDir+"/CAD/bin/FreeCAD.exe"
            # cadExeFile="C:/Program Files/FreeCAD 0.21/bin/FreeCAD.exe"
            # cadExeFile="D:/project/cae/fem-gdtd/src2/dist/FEM-GDTDV0.2/CAD/bin/FreeCAD.exe"
            userConfigFile=baseDir+"/CAD/user.cfg"
            userConfigFileDest=cadDataPath+"/FreeCAD/user.cfg"
            exe_dir=os.path.dirname(cadExeFile)
            startupFile=baseDir+"/cad/startup.py"
            if(not os.path.exists(cadExeFile)):
                QtWidgets.QMessageBox.about(self, "Error", "CAD模块不存在，请检查.\n"+cadExeFile)
                return
            try:
                #将user.cfg复制到用户目录
                shutil.copy(userConfigFile,userConfigFileDest)
                
                pass
            except Exception as e:
                print(e)
            args = [cadExeFile, startupFile]
            
            # args = ["cad/app.exe", "cad/startup.py"]
            # print(args)
            subprocess.Popen(args,cwd=exe_dir)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.about(self, "Error", "CAD模块启动失败."+str(e))
        pass
    def importModel(self):
        self.projectTree.nodeAction_ImportModel()
        pass
    def exportModel(self):
        self.projectTree.nodeAction_ExportModel()
        pass
    def exchangeModel(self):
        frm_exchange=frmExchange(self)
        frm_exchange.show()
        frm_exchange.sigFormatExchange.connect(self.sig_cadFormatChange)
        pass
    def setModelColor(self):
        self.projectTree.setModelColor()
    def setModelOpacity(self):
        self.projectTree.setModelOpacity()
        
    def sig_cadFormatChange(self,sourceFile,targetFile):
        print(sourceFile,targetFile)
        code,message=api_model.format_excange(sourceFile,targetFile)
        QtWidgets.QMessageBox.about(self, "Model exchange", message)
        pass

    # def sig_setModelColor(self,backgroundColor:Tuple,modelColor:Tuple):
    #     color_back=[backgroundColor[0],backgroundColor[1],backgroundColor[2]]
    #     self.modelViewer.set_bg_gradient_color(color_back, color_back)
    #     self.projectTree.setModelColor(modelColor)
    #     pass

    # def sig_mpiSet(self,mpiNum,installPath):
    #     Project.mpiNum=mpiNum
    #     Project.mpiInstallPath=installPath
    # def setMPI(self):
    #     mpiNum=Project.mpiNum
    #     installPath=Project.mpiInstallPath
    #     frm_mpi=frmMPI(self,mpiNum,installPath)
    #     frm_mpi.show()
    #     frm_mpi.sigMPISet.connect(self.sig_mpiSet)
    #     frm_mpi.sigMPIRegister.connect(self.sig_mpiRegister)
    #     frm_mpi.sigMPITest.connect(self.sig_mpiTest)

    # def sig_mpiRegister(self):
    #     cmd_register=[Project.mpiInstallPath+Project.mpiRegisterFile]
    #     subprocess.Popen(cmd_register)
    #     pass
    # def sig_mpiTest(self):
    #     cmd_register=[Project.mpiInstallPath+Project.mpiTestFile]
    #     subprocess.Popen(cmd_register)
    #     pass
    def setScalar(self):
        '''设置标量值颜色条
        '''
        self.projectTree.setScalarColor()

       
        pass
    def pickPoint(self):
        self.selectContext.Action_select_point()
    def pickEdge(self):
        '''拾取边 创建port用
        '''
        
        # self.selectContext.initEdgeSelected(self.projectTree.getEdgeIdList())
        self.selectContext.Action_select_edge()
        pass
    def pickFace(self):
        '''设置拾取模式为拾取面 设置网格尺寸用
        '''
       
        self.selectContext.Action_select_face()
        # self.selectContext.clear()
        pass
    def pickBody(self):
        self.selectContext.Action_select_body()

    def sig_selectBody(self,bodyId:int,isSelected:bool):
        #选中一个实体
        
        self.projectTree.setBodySelect(bodyId,isSelected)
        pass
    def sig_selectFace(self,faceId:int,isSelected:bool):
        #选中一个面
        # print("faceId")
        # self.projectTree.sig_SelecteMediaFace(faceId)
        self.projectTree.setFaceSelect(faceId,isSelected)
      
        pass
    def sig_chooseFace(self,center:tuple,direction:tuple):
        #选中一个面
        print("mainwindows.sigChooseface",center,direction)
        pass
    def meshSetLocalSize(self):
        '''单独设置选中面的尺寸
        '''
        self.tab_activate(TABINDEX_MODEL)
        self.pickFace()
        fList=[]
        self.frm_localSize=frmLocalSize(self,fList)
        # self.isLocalSize=True
        self.frm_localSize.move(self.centralWidget().geometry().topLeft())
        self.frm_localSize.show()

        self.frm_localSize.sigLocalSize.connect(self.projectTree.sig_setLocalSize)
        pass
    def viewFit(self):
        self.modelViewer.FitAll()
    def viewISO(self):
        self.modelViewer.View_Iso()
    def viewLeft(self):
        self.modelViewer.View_Left()
    def viewRight(self):
        self.modelViewer.View_Right()
    def viewTop(self):
        self.modelViewer.View_Top()
    def viewBottom(self):
        self.modelViewer.View_Bottom()
    def viewFront(self):
        self.modelViewer.View_Front()
    def viewBack(self):
        self.modelViewer.View_Rear()
    def viewWireframe(self):
        self.modelViewer.SetModeWireFrame()
    def viewShaded(self):
        self.modelViewer.SetModeShaded()
    def viewZoomIn(self):
        self.modelViewer.ZoomFactor(1.05)
        pass
    def viewZoomOut(self):
        self.modelViewer.ZoomFactor(0.95)
        pass
    def viewPanLeft(self):
        self.modelViewer.Pan(-20,0)
        pass
    def viewPanRight(self):
        self.modelViewer.Pan(20,0)
        pass
    def viewPanUp(self):
        self.modelViewer.Pan(0,20)
        pass
    def viewPanDown(self):
        self.modelViewer.Pan(0,-20)
        pass
    def viewRotateThetaAdd(self):
        self.modelViewer.StartRotation(0,0)
        self.modelViewer.Rotation(0,15)
        
        
        pass
    def viewRotateThetaDec(self):
        self.modelViewer.StartRotation(0,0)
        self.modelViewer.Rotation(0,-15)
       
        pass
    def viewRotatePhiAdd(self):
        self.modelViewer.StartRotation(0,0)
        self.modelViewer.Rotation(15,0)
        pass
    def viewRotatePhiDec(self):
        self.modelViewer.StartRotation(0,0)
        self.modelViewer.Rotation(-15,0)
        pass
    def displayVertex(self):
        self.meshViewer.start_point_picker()
    def displayPostPoints(self):
        '''显示数据点坐标，需要根据当前不同的显示类型，动态设球体置半径，球体用于选中数据点标识操作
        '''
        self.projectTree.renderPoints()
        # return
        # self._postPointsDisplay=not self._postPointsDisplay
        # if(self._postPointsDisplay):
        #     # self._3dViewer.clear()
        #     actor,points=api_vtk.points_vertex(self.projectTree.resultsCurrentPointList)
        #     actor2,points2=api_vtk.points_sphere(self.projectTree.resultsCurrentPointList,None,None,0.01)
        #     self._3dViewer.display_points(actor,points,actor2)
        #     self._3dViewer.start_point_picker()
        # else:
        #     self._3dViewer.hide_points()
        #     self._3dViewer.end_pick()
        pass
    def displaySurface(self):
        self.projectTree.renderSurfaceMap()
    def postExportPoints(self):
        fname,_ = QtWidgets.QFileDialog.getSaveFileName(filter="Data points file(*.txt)")
        if fname != '':
            
            postData=self.projectTree._postData
            if(self.projectTree._is_extend):
                postData=self.projectTree._postData_extend
            if(postData is None):
                QtWidgets.QMessageBox.about(self, "数据导出","没有数据可以导出.")
                return
            dataList=postData.data_now.points_now
            points_now=[(tup[0]/1000,tup[1]/1000,tup[2]/1000,tup[3]) for tup in dataList]
            headers=postData.data_now.headers_now
            code,message=api_vtk.export_data(fileName=fname, valueList=points_now,headers=headers)

            QtWidgets.QMessageBox.about(self, "数据导出", message)
            
        pass
    def postExportImg(self):
        fname,_ = QtWidgets.QFileDialog.getSaveFileName(filter="Imgage file(*.png)")

        if fname != '':
            code,message=api_vtk.export_img(self._3dViewer.GetRenderWindow(),fname)
            QtWidgets.QMessageBox.about(self, "图片导出", message)
            

        pass
    def displayLine(self,p1,p2):
        actors=api_vtk.distance_line(p1,p2)
        self.meshViewer.display_line(actors[0],actors[1],actors[2])
        pass
    def measureDistance(self):
        frm_measure=frmMeasure(self)
        frm_measure.move(self.centralWidget().geometry().topLeft())
        frm_measure.show()

        frm_measure.sigShowLine.connect(self.displayLine)
        frm_measure.sigHideLine.connect(self.meshViewer.hide_line)
        pass
    def vtkRotate(self):
        # frm_rotate=frmRotate(self)
        # frm_rotate.move(self.centralWidget().geometry().topLeft())
        # frm_rotate.show()
        # frm_rotate.sigRotate.connect(self._3dViewer.rotate)
        pass
    def findElement(self):
        frm_findElement=frmFindElement(self)
        frm_findElement.move(self.centralWidget().geometry().topLeft())
        frm_findElement.show()
        frm_findElement.sigShowElement.connect(self.meshViewer.display_cell)
        frm_findElement.sigClearSelected.connect(self.meshViewer.clear_cell_selected)
        pass

    def prepare_statusbar(self):
        pass
        # self.setStatusBar(self.statusbar)
        # self.statusbar.setObjectName("statusbar")
        # # 设置状态栏样式
        # self.statusbar.setStyleSheet('QStatusBar::item {border: none;}')
        # self.status_label = QLabel('', parent=self)
        # self.statusBar().insertPermanentWidget(0, self.status_label)


    def tab_activate(self,tabIndex:int):
        self.tabWidget.setUpdatesEnabled(False)

        if(tabIndex==0):#model #关闭2d polar
            self.tabWidget.setTabVisible(5,False)
        
       
        if(tabIndex==2):#3d viewer
            self.tabWidget.setTabVisible(3,False)
            # self.tabWidget.setTabVisible(4,False)
            self.tabWidget.setTabVisible(2,True)
            self.tabWidget.setTabVisible(5,False)
            
            self._2dViewer.stopRefresh()
        if(tabIndex==3):#2d viewer
            self.tabWidget.setTabVisible(3,True)
            # self.tabWidget.setTabVisible(4,False)
            self.tabWidget.setTabVisible(2,False)
            self.tabWidget.setTabVisible(5,False)
        if(tabIndex==4):
            # self.tabWidget.setTabVisible(3,False)
            self.tabWidget.setTabVisible(4,True)
            # self.tabWidget.setTabVisible(2,False)

        if(tabIndex==5):
            self.tabWidget.setTabVisible(5,True)
           
        self.tabWidget.setCurrentIndex(tabIndex)
        self.tabWidget.setUpdatesEnabled(True)
        
        pass


    def prepare_console(self):

        console = self.console
        console.push_vars({'self': self})

    def cbxFreqFill(self,freqList:List[str],cbx:RibbonComboBox):
        '''切换频率查看后处理数据
        '''
        cbx.currentIndexChanged.disconnect()
        cbx.clear()
        for str in freqList:
            cbx.addItem(str)
        cbx.currentIndexChanged.connect(self.projectTree.freqChanged)
        pass
    def cbxFreqFill_1(self,freqList:List[str]):
        self.cbxFreqFill(freqList,self.cbxFrequency)
    def cbxFreqFill_2(self,freqList:List[str]):
        # self.cbxFreqFill(freqList,self.cbxFreq2)
        pass
    def cbxTxFill(self,txList:List[str],cbx:RibbonComboBox):
        '''切换发射源
        '''
        cbx.currentIndexChanged.disconnect()
        cbx.clear()
        for str in txList:
            cbx.addItem(str)
        cbx.currentIndexChanged.connect(self.projectTree.txChanged)
        pass
    def cbxTxFill_1(self,txList:List[str]):
        self.cbxTxFill(txList,self.cbxTX)
    def cbxTxEnable(self,enable:bool):
        self.cbxTX.setEnabled(enable)
        pass
    
    # def cbxSurfaceFill(self,surfaceList:List[str],cbx:RibbonComboBox,lblSurface:QLabel):
    #     '''切换查看类型，当为面/体时，切换面
    #     '''
    #     if(surfaceList==None):
    #         cbx.setDisabled(True)
    #         lblSurface.setDisabled(True)
    #         cbx.currentIndexChanged.disconnect()
    #         cbx.clear()
    #         cbx.addItem("X-line")
    #         cbx.currentIndexChanged.connect(self.projectTree.surfaceChanged)
    #         return
    #     cbx.setDisabled(False)
    #     lblSurface.setDisabled(False)
    #     cbx.currentIndexChanged.disconnect()
    #     cbx.clear()
    #     for str in surfaceList:
    #         cbx.addItem(str)
        
    #     cbx.currentIndexChanged.connect(self.projectTree.surfaceChanged)
    #     pass
    # def cbxSurfaceFill_1(self,surfaceList):
    #     self.cbxSurfaceFill(surfaceList,self.cbxSurface,self.lblSurface)
    # def cbxSurfaceFill_2(self,surfaceList):
    #     self.cbxSurfaceFill(surfaceList,self.cbxSurface2,self.lblSurface2)
    #     pass

    #     pass
    # def cbxPositionFill(self,pItem:Tuple[str,list],cbx:RibbonComboBox,lbl:QLabel):
    #     '''切换某个轴的位置，计算区域为长方体时，选择某个面后，另一个轴的坐标值切换查看不同距离的面
    #     '''
        
    #     if(pItem==None):
    #         cbx.setDisabled(True)
    #         lbl.setDisabled(True)
    #         return
    #     tip=pItem[0]
    #     dList=pItem[1]
    #     cbx.setDisabled(False)
    #     lbl.setDisabled(False)
    #     cbx.currentIndexChanged.disconnect()
    #     lbl.setText(tip+" position")
    #     cbx.clear()
    #     for p in dList:
    #         cbx.addItem(str(p))
    #     cbx.currentIndexChanged.connect(self.projectTree.positionChanged)
    #     pass
    # def cbxPositionFill_1(self,pItem):
    #     self.cbxPositionFill(pItem,self.cbxPosition,self.lblPosition)
    # def cbxPositionFill_2(self,pItem):
    #     self.cbxPositionFill(pItem,self.cbxPosition2,self.lblPosition2)
    #     pass
    def reverseNormal(self):
        self.projectTree.reverseNormal()
        pass

    def showContextMenu(self, pos):
        '''显示右键菜单
        '''
        # if(self.projectTree.currentModel!=None and any(self.projectTree.currentModel.face_selected.values())):

        if(self.projectTree.currentModel!=None):

            actions=[
                # QAction("本体材料",self,enabled=True,
                #     triggered=self.projectTree.setFaceMediumBase),

                #     QAction("涂覆材料",self,enabled=True,
                #     triggered=self.projectTree.setFaceMediumCoat),

                #     QAction("法向反转",self,enabled=True,
                #     triggered=self.reverseNormal),
                    QAction("隐藏几何",self,enabled=True,
                    triggered=self.projectTree.showHideSolid),
                    QAction("显示全部",self,enabled=True,
                    triggered=self.projectTree.showSolidAll),
                    ]
            self._context_menu.clear()
            self._context_menu.addActions(actions)
            self._context_menu.exec_(self.tabWidget.mapToGlobal(pos))
        pass
    def dock(self,
             widget,
             title,
         allowedAreas = QtCore.Qt.DockWidgetArea.AllDockWidgetAreas,
         defaultArea = 'right',
         name=None,
         icon = None,
         minHeight:int=None):
    
        dock = QtWidgets.QDockWidget(title,self,objectName=title)
        # if(minHeight!=None):
        #     dock.setMaximumHeight(minHeight)
        # dock.setStyleSheet("background-color:rgb(255,255,255)")
    
        if name: dock.setObjectName(name)
        if icon: dock.toggleViewAction().setIcon(icon)
        
        dock.setAllowedAreas(allowedAreas)
        dock.setWidget(widget)
        action = dock.toggleViewAction()
        action.setText(title)
        
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeatures(\
                        QtWidgets.QDockWidget.AllDockWidgetFeatures))
        
        self.addDockWidget(DOCK_POSITIONS[defaultArea], dock)
        
        return dock

    def setup_logging(self):

        from logbook.compat import redirect_logging
        from logbook import INFO,DEBUG,ERROR, Logger

        redirect_logging()
        self.logViewer.handler.level = INFO
        self.logViewer.handler.push_application()
        # self.logViewer.appendPlainText("text for test")

        self._logger = Logger(self.name)
        

        def handle_exception(exc_type, exc_value, exc_traceback):

            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            if(exc_type==AttributeError):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            self._logger.error("Uncaught exception occurred",
                               exc_info=(exc_type, exc_value, exc_traceback))
            

        sys.excepthook = handle_exception
    
        

if __name__ == "__main__":

    pass
