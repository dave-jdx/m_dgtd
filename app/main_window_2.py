import sys
# from OCC.Core.gp import gp_Pnt
from OCC.Display import OCCViewer
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QToolBar,
    QDockWidget,
    QAction,
    QDockWidget,
    QTabWidget
)
from PyQt5.QtGui import QPalette, QColor

from .widgets.console import ConsoleWidget

from .widgets.traceback_viewer import TracebackPane

from .widgets.debugger import LocalsView

from .widgets.log import LogViewer

from .widgets.project import Project

from .widgets.meshing import MenuMesh

from .widgets.modeling import MenuModel

from .widgets.simulation import MenuSolver
from .widgets.post_processing import PostProcess
from .widgets.project_tree import ProjectTree
from .widgets.vtk_viewer import vtkOperator

from . import __version__
from .utils import dock, add_actions, open_url, about_dialog, check_gtihub_for_updates, confirm
from .mixins import MainMixin
from .icons import icon
from .preferences import PreferencesWidget

# --------------------------------------------------自己增加的lib
import logging
import os
from OCC.Display.OCCViewer import OffscreenRenderer
from OCC.Display.backend import load_backend, get_qt_modules
from OCC.Extend.TopologyUtils import TopologyExplorer
from .module.interactiveContext import InteractiveContext
from .module.loadPartProcessBar import PartLoadProgressBar



# ------------------------------------------------------------开始初始化环境


log = logging.getLogger(__name__)


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
# ------------------------------------------------------------初始化结束

class MainWindow(QMainWindow, MainMixin):
    name = 'FEM-GDTD'
    org = 'Xidian University'

    def __init__(self, parent=None, spid=None):

        super(MainWindow, self).__init__(parent)
        MainMixin.__init__(self)

        self.setWindowIcon(icon('app'))
        # self.setWindowTitle(f"{self.name}:{spid}")
        self.setWindowTitle(f"{self.name}")
    

        self.tabWidget = QTabWidget()
        
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")

        self.canva = qtDisplay.qtViewer3d(self)  # 链接3D模块
        self.modelViewer:OCCViewer.Viewer3d=self.canva._display

        self.tabWidget.addTab(self.canva, "Model Viewer")

        self.vtkViewer = vtkOperator(self)
        self.tabWidget.addTab(self.vtkViewer, "Mesh Viewer")

       
        self.canva.create_actions(parent=self)
        self.setCentralWidget(self.tabWidget)

        # 建立交互模块
        self.select = InteractiveContext(self,self.modelViewer)
        
        

        # 定义状态栏
        self.statusbar = QtWidgets.QStatusBar(self)
        # 将状态栏设置为当前窗口的状态栏
        self.setStatusBar(self.statusbar)
        # 设置状态栏的对象名称
        self.statusbar.setObjectName("statusbar")
        # 设置状态栏样式
        self.statusbar.setStyleSheet('QStatusBar::item {border: none;}')
        #初始化进度条
        self.progressBar:PartLoadProgressBar=PartLoadProgressBar(self)

        self.projectTree:ProjectTree=ProjectTree(self,self.modelViewer,self.progressBar,self.vtkViewer)
        self.project=Project(self)


        # self.select.create_actions(parent=self)
        self.select.sigLineClicked.connect(self.projectTree.sig_createPort)
        self.projectTree.sigSelectEdge.connect(self.select.Action_select_edge)
        self.projectTree.sigRemoveSelectedEdge.connect(self.select.remove_selectedEdge)

        self.project.sigCreateProject.connect(self.projectTree.sig_createProject)

        self.modelViewer.register_select_callback(self.select.line_clicked)
        self.modelViewer.register_select_callback(self.select.face_clicked)
        self.modelViewer.register_select_callback(self.select.body_clicked)

        self.registerComponent('project', self.project)
        self.registerComponent('modeling', MenuModel(self))
        self.registerComponent('meshing', MenuMesh(self))
        self.registerComponent('simulation', MenuSolver(self))
        self.registerComponent('postprocess', PostProcess(self))

        self.registerComponent('canva', self.canva)
        self.registerComponent('select', self.select)

        self.registerComponent('project_tree',
                               self.projectTree,
                               lambda c: dock(c,
                                              'Project Manager',
                                              self,
                                              defaultArea='left'))

        self.prepare_panes()
        # 添加自定义菜单

        self.prepare_toolbar()
        self.prepare_menubar()

        self.prepare_statusbar()
        self.prepare_actions()

        # self.components['project_tree'].addwcs()
        # self.components['project_tree'].adddCube()

        self.prepare_console()

        # self.fill_dummy()

        self.setup_logging()

        self.restorePreferences()
        self.restoreWindow()

        # if filename:
        #     self.components['editor'].load_from_file(filename)

        self.restoreComponentState()


    def closeEvent(self, event):

        self.vtkViewer.closeEvent(event)
        self.saveWindow()
        self.savePreferences()
        self.saveComponentState()
        super(MainWindow, self).closeEvent(event)
     
        # if self.components['editor'].document().isModified():

        #     rv = confirm(self, 'Confirm close', 'Close without saving?')

        #     if rv:
        #         event.accept()
        #         super(MainWindow, self).closeEvent(event)
        #     else:
        #         event.ignore()
        # else:
        #     super(MainWindow, self).closeEvent(event)

    def prepare_panes(self):  # 界面准备
        # 注册界面组件
        # self.registerComponent('editor',
        #                        Editor(self),
        #                        lambda c : dock(c,
        #                                        'Editor',
        #                                        self,
        #                                        defaultArea='bottom'))

        # self.registerComponent('object_tree',
        #                        ObjectTree(self),
        #                        lambda c: dock(c,
        #                                       'Project Manager',
        #                                       self,
        #                                       defaultArea='left'))
        
        
        self.registerComponent('console',
                               ConsoleWidget(self),
                               lambda c: dock(c,
                                              'Console',
                                              self,
                                              defaultArea='bottom'))

        self.registerComponent('traceback_viewer',
                               TracebackPane(self),
                               lambda c: dock(c,
                                              'Current traceback',
                                              self,
                                              defaultArea='bottom'))

        # self.registerComponent('debugger', Debugger(self))

        self.registerComponent('variables_viewer', LocalsView(self),
                               lambda c: dock(c,
                                              'Variables',
                                              self,
                                              defaultArea='right'))

        # self.registerComponent('cq_object_inspector',
        #                        CQObjectInspector(self),
        #                        lambda c: dock(c,
        #                                       'Object inspector',
        #                                       self,
        #                                       defaultArea='right'))
        self.registerComponent('log',
                               LogViewer(self),
                               lambda c: dock(c,
                                              'Log viewer',
                                              self,
                                              defaultArea='bottom'))

        for d in self.docks.values():
            d.show()

    def prepare_menubar(self):  # 主菜单准备函数

        menu = self.menuBar()

        menu_file = menu.addMenu('工程')
        menu_model = menu.addMenu('几何')
        menu_mesh = menu.addMenu('网格')
        menu_simulation = menu.addMenu('求解器')
        menu_postprocess = menu.addMenu('结果分析')
        # menu_edit = menu.addMenu('&Edit')
        # menu_tools = menu.addMenu('&Tools')
        # menu_run = menu.addMenu('&Run')
        menu_view = menu.addMenu('视图')
        # menu_select = menu.addMenu('&Select')
        menu_help = menu.addMenu('帮助')

        # per component menu elements
        # 增加了 Select 选择器菜单
        menus = {'File': menu_file,
                 'Model': menu_model,
                 'Mesh': menu_mesh,
                 'Simulation': menu_simulation,
                 'PostProcess': menu_postprocess,
                 #  'Edit': menu_edit,
                 #  'Run': menu_run,
                 #  'Tools': menu_tools,
                 'View': menu_view,
                 #  "Select": menu_select,
                 'Help': menu_help}
        for comp in self.components.values():
            print(comp)
            self.prepare_menubar_component(menus,
                                           comp.menuActions())

        # global menu elements
        menu_view.addSeparator()
        for d in self.findChildren(QDockWidget):
            menu_view.addAction(d.toggleViewAction())

        menu_view.addSeparator()
        for t in self.findChildren(QToolBar):
            menu_view.addAction(t.toggleViewAction())

        # ----------------后增加的菜单--------------------------------
        # menu_edit.addAction(
        #     QAction(icon('preferences'),
        #             'Preferences',
        #             self, triggered=self.edit_preferences))

        menu_help.addAction(
            QAction(icon('help'),
                    'Documentation',
                    self, triggered=self.documentation))

        # menu_help.addAction(
        #     QAction('documentation',
        #             self, triggered=self.cq_documentation))

        menu_help.addAction(
            QAction(icon('about'),
                    'About',
                    self, triggered=self.about))

        # menu_help.addAction( \
        #     QAction('Check for CadQuery updates',
        #             self,triggered=self.check_for_cq_updates))
        # menu_file.addAction( \
        #     QAction('Check for CadQuery updates',
        #             self,triggered=self.check_for_cq_updates))

    def prepare_menubar_component(self, menus, comp_menu_dict):  # 建立菜单和里面的按钮

        for name, action in comp_menu_dict.items():  # 循环增加菜单栏 及其按钮
            if name in menus:
                menus[name].addActions(action)
            else:
                pass

    def prepare_toolbar(self):

        self.toolbar = QToolBar('Main toolbar', self,
                                objectName='Main toolbar')

        for c in self.components.values():
            add_actions(self.toolbar, c.toolbarActions())

        self.addToolBar(self.toolbar)

    def prepare_statusbar(self):

        self.status_label = QLabel('', parent=self)
        self.statusBar().insertPermanentWidget(0, self.status_label)

    def prepare_actions(self):
        """
        debugger.sigRenderd->object_tree.addObjects->viewer.display_many
        """
        # self.components['debugger'].sigRendered\
        #     .connect(self.components['object_tree'].addObjects)

        # self.components['debugger'].sigRendered\
        #     .connect(self.components['project_tree'].addObjects)
        # self.components['debugger'].sigTraceback\
        #     .connect(self.components['traceback_viewer'].addTraceback)
        # self.components['debugger'].sigLocals\
        #     .connect(self.components['variables_viewer'].update_frame)
        # self.components['debugger'].sigLocals\
        #     .connect(self.components['console'].push_vars)

        # self.components['object_tree'].sigEdgesAdded[list] \
        #     .connect(self.components['object_tree'].addedge)

        # self.components['object_tree'].sigFacesAdded[list] \
        #     .connect(self.components['object_tree'].addface)

        # self.components['project_tree'].sigEdgesAdded[list] \
        #     .connect(self.components['project_tree'].addedge)

        self.components['project_tree'].sigFacesAdded[list] \
            .connect(self.components['project_tree'].addface)

        self.components['project_tree'].sigActivateTab.connect(self.tab_activate)
        '''
        self.components['object_tree'].sigObjectsAdded[list]\
            .connect(self.components['viewer'].display_many)
        self.components['object_tree'].sigObjectsAdded[list,bool]\
            .connect(self.components['viewer'].display_many)
        self.components['object_tree'].sigItemChanged.\
            connect(self.components['viewer'].update_item)
        self.components['object_tree'].sigObjectsRemoved\
            .connect(self.components['viewer'].remove_items)
        self.components['object_tree'].sigCQObjectSelected\
            .connect(self.components['cq_object_inspector'].setObject)
        self.components['object_tree'].sigObjectPropertiesChanged\
            .connect(self.components['viewer'].redraw)
        self.components['object_tree'].sigAISObjectsSelected\
            .connect(self.components['viewer'].set_selected)

        
        self.components['canva'].sigObjectSelected\
            .connect(self.components['object_tree'].handleGraphicalSelection)

        self.components['traceback_viewer'].sigHighlightLine\
            .connect(self.components['editor'].go_to_line)

        self.components['cq_object_inspector'].sigDisplayObjects\
            .connect(self.components['viewer'].display_many)
        self.components['cq_object_inspector'].sigRemoveObjects\
            .connect(self.components['viewer'].remove_items)
        self.components['cq_object_inspector'].sigShowPlane\
            .connect(self.components['viewer'].toggle_grid)
        self.components['cq_object_inspector'].sigShowPlane[bool,float]\
            .connect(self.components['viewer'].toggle_grid)
        self.components['cq_object_inspector'].sigChangePlane\
            .connect(self.components['viewer'].set_grid_orientation)
        """
        self.components['debugger'].sigLocalsChanged\
            .connect(self.components['variables_viewer'].update_frame)
        self.components['debugger'].sigLineChanged\
            .connect(self.components['editor'].go_to_line)
        self.components['debugger'].sigDebugging\
            .connect(self.components['object_tree'].stashObjects)
        self.components['debugger'].sigCQChanged\
            .connect(self.components['object_tree'].addObjects)
        self.components['debugger'].sigTraceback\
            .connect(self.components['traceback_viewer'].addTraceback)

        # trigger re-render when file is modified externally or saved
        self.components['editor'].triggerRerender \
            .connect(self.components['debugger'].render)
        self.components['editor'].sigFilenameChanged\
            .connect(self.handle_filename_change)

        # self.components['editor'].triggerView \
            # .connect(self.components['viewer'].display_many)
        '''
    def tab_activate(self,tabIndex):
        self.tabWidget.setCurrentIndex(tabIndex)
        pass

    def prepare_console(self):

        console = self.components['console']
        # obj_tree = self.components['object_tree']
        project_tree = self.components['project_tree']

        # application related items
        console.push_vars({'self': self})

        # CQ related items
        # console.push_vars({'show': obj_tree.addObject,
        #                    'show_object': obj_tree.addObject,
        #                    'cq': cq})
        console.push_vars({'show': project_tree.addObject,
                           'show_object': project_tree.addObject,
                           'cq': None})

    # def fill_dummy(self):

    #     self.components['editor']\
    #         .set_text('import cadquery as cq\nresult = cq.Workplane("XY" ).box(3, 3, 0.5).edges("|Z").fillet(0.125)')

    def setup_logging(self):

        from logbook.compat import redirect_logging
        from logbook import INFO, Logger

        redirect_logging()
        self.components['log'].handler.level = INFO
        self.components['log'].handler.push_application()

        self._logger = Logger(self.name)

        def handle_exception(exc_type, exc_value, exc_traceback):

            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            self._logger.error("Uncaught exception occurred",
                               exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception

    def edit_preferences(self):  # 编辑设置

        prefs = PreferencesWidget(self, self.components)
        prefs.exec_()

    def about(self):

        about_dialog(
            self,
            f'CAE1.01',
            f'CAE Tools for CSI',
        )

    def check_for_cq_updates(self):

        check_gtihub_for_updates(self, cq)

    def documentation(self):

        open_url('https://www.baidu.com')

    def cq_documentation(self):

        open_url('https://cadquery.readthedocs.io/en/latest/')

    def handle_filename_change(self, fname):
        pass

        # new_title = fname if fname else "*"
        # self.setWindowTitle(f"{self.name}: {new_title}")


if __name__ == "__main__":

    pass
