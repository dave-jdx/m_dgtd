from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QAction
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal,QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
import sys

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonDataModel import vtkPolyData

from vtkmodules.all import(
    vtkRenderer,
    vtkActor,
    vtkAxesActor,
    vtkScalarBarActor,
    vtkLookupTable,
    vtkOrientationMarkerWidget,
    vtkInteractorStyleTrackballCamera,
    vtkActorCollection,
    vtkProperty,
    vtkSphereSource,
    vtkPolyDataMapper,
    vtkCaptionActor2D,
    vtkTextProperty,
    vtkPointPicker,
    vtkCellPicker,
    vtkPropPicker,
    vtkInteractorStyleTrackballCamera,
    vtkConeSource,
    vtkTextActor,
    vtkInteractorStyleRubberBandPick,
    vtkRenderWindowInteractor,
    vtkCommand,
    vtkCellArray,
    vtkVertex,
    vtkCell,
    vtkPoints,
    vtkExtractCells,
    vtkDataSetMapper,
    vtkIdList,
    vtkLineSource,
    vtkLine,
    vtkPropCollection,
    vtkPointData,
    vtkDoubleArray,
    vtkTransform
)


class vtkViewer3d(QVTKRenderWindowInteractor):

    name = 'viewer 3d'

    def __init__(self, parent=None):
        self.parent = parent
        super(vtkViewer3d, self).__init__(parent)
        self.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
        self.ren = vtkRenderer()
        self.GetRenderWindow().AddRenderer(self.ren)
        self._highlight_radius = 0.005

        self.iren: vtkRenderWindowInteractor = self.GetRenderWindow().GetInteractor()

        self.axesActor = None
        self.axes: vtkOrientationMarkerWidget = None

        # 创建一个标签演员用于显示所选边的 ID
        self.label_actor = vtkTextActor()
        self.label_actor.GetTextProperty().SetColor(0.8, 0, 0)  # 设置标签颜色为红色
        self.label_actor.GetTextProperty().SetFontSize(18)

        self.pickedSourcePolyData: vtkPolyData = None
        self.rotateActor:vtkActor=None

        self._3dActor: vtkActor = None  # 当前正在显示的actor 包含网格/表面电流/FFR/NFR/NF
        self._barActor: vtkScalarBarActor = None  # 当前正在显示的颜色条 表面电流/FFR/NFR/NF
        self._rangeAuto = None  # 原数据值范围 （min,max)
        self._rangeFixed = None  # 定制设置的数据值范围 (min,max)

        self._points: vtkPoints = None
        self.pointsActor: vtkActor = None
        self._sphereActor: vtkActor = None

        self.pointPicker: vtkPointPicker = None
        self.cellPicker: vtkCellPicker = None
        self.propPicker: vtkPropPicker = None

        self.pointHoverActor: vtkActor = None
        self.cellHoverActor: vtkActor = None

        self.cellSelected = {}  # 已经选中的cell key-value  cellId-vtkActor
        self.pointSelected = {}

        self.lineActor: vtkActor = None
        self.p1Actor: vtkActor = None
        self.p2Actor: vtkActor = None

        self._index = 0
        self._currentType: str = None
        self._center_axes = vtkAxesActor()

        # show the widget
        self.Initialize()
        self.Start()
        self.show()
        self.onLoad()

    def onLoad(self):
        # self.ren.SetBackground(0.86, 0.86, 0.86)
        self.display_axes()
        # self.display_scalarBar()
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().SetPosition(0.6, -0.6, 0.6)
        # self.ren.GetActiveCamera().SetFocalPoint(0,0,0)
        self.ren.GetActiveCamera().SetViewUp(-0.45, 0.45, 1)
        # print(self.GetRenderWindow().GetSize(),self.GetRenderWindow().GetScreenSize())
        # self.start_point_picker()

        # self.start_prop_picker()
        self.initCenterAxes()

        pass
    def initCenterAxes(self):
        # 获取x/y/z轴的vtkCaptionActor2D对象
        x_axis_caption = self._center_axes.GetXAxisCaptionActor2D()
        y_axis_caption = self._center_axes.GetYAxisCaptionActor2D()
        z_axis_caption = self._center_axes.GetZAxisCaptionActor2D()

        # 获取vtkTextActor对象并设置颜色
        x_text_actor = x_axis_caption.GetTextActor()
        x_text_prop = x_text_actor.GetTextProperty()
        x_text_prop.SetColor(0.3, 0.3, 0.3)  # 设置x轴标签文本颜色为红色

        y_text_actor = y_axis_caption.GetTextActor()
        y_text_prop = y_text_actor.GetTextProperty()
        y_text_prop.SetColor(0.3, 0.3, 0.3)  # 设置y轴标签文本颜色为绿色

        z_text_actor = z_axis_caption.GetTextActor()
        z_text_prop = z_text_actor.GetTextProperty()
        z_text_prop.SetColor(0.3, 0.3, 0.3)  # 设置z轴标签文本颜色为蓝色
    def display_axes(self):
        self.axesActor = vtkAxesActor()
        # self.axesActor.SetCylinderRadius(0.1)

        x: vtkProperty = self.axesActor.GetXAxisShaftProperty()
        x.SetLineWidth(4)
        y: vtkProperty = self.axesActor.GetYAxisShaftProperty()
        y.SetLineWidth(4)
        z: vtkProperty = self.axesActor.GetZAxisShaftProperty()
        z.SetLineWidth(4)
        x.SetColor(0.81, 0, 0)
        y.SetColor(0, 0.81, 0)
        z.SetColor(0, 0, 0.81)

        self.axesActor.SetConeRadius(0.5)
        x1: vtkTextProperty = self.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty()
        x1.SetColor(0.3, 0.3, 0.3)
        x1.SetFontFamilyToArial()
        x1.SetFontSize(10)
        y1: vtkTextProperty = self.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty()
        y1.SetColor(0.3, 0.3, 0.3)
        z1: vtkTextProperty = self.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty()
        z1.SetColor(0.3, 0.3, 0.3)

        # self.axesActor.SetDragable(0)
        # self.axesActor.SetCylinderRadius(0.1)
        axes = vtkOrientationMarkerWidget()
        axes.SetViewport(0, 0, 0.05, 0.1)
        axes.SetOrientationMarker(self.axesActor)
        axes.SetInteractor(self.iren)
        axes.SetZoom(1.5)

        axes.EnabledOn()  # <== application freeze-crash
        axes.InteractiveOff()  # 禁用交互，不被拖动

        # print("render",axes.GetCurrentRenderer().GetViewport())

        self.axes = axes

        # self.ren.AddActor(self.axesActor)

        # self.axes.
        pass

    def display_mesh(self, actor: vtkActor):
        # self.start_point_picker()
        self.pickedSourcePolyData = actor.GetMapper().GetInput()
        self._3dActor = actor
        # actor.GetProperty().SetRepresentationToWireframe()
        self.clear()
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        # actor.Modified()
        # self.iren.Render()
        self.GetRenderWindow().Render()
        self.rotateActor=actor
        # self.ren.GetActiveCamera().SetViewUp(-0.4,0.55,0.72)
        pass

    def hide_mesh(self, actor: vtkActor):
        self.ren.RemoveActor(actor)
        self.iren.Render()


    def display_line(self, line: vtkActor, p1Actor: vtkActor, p2Actor: vtkActor):
        self.hide_line()
        self.lineActor = line
        self.p1Actor = p1Actor
        self.p2Actor = p2Actor
        self.ren.AddActor(self.lineActor)
        self.ren.AddActor(self.p1Actor)
        self.ren.AddActor(self.p2Actor)
        self.iren.Render()

    def hide_line(self):
        self.ren.RemoveActor(self.lineActor)
        self.ren.RemoveActor(self.p1Actor)
        self.ren.RemoveActor(self.p2Actor)
    def clear(self):

        props: vtkPropCollection = self.ren.GetViewProps()
        for i in range(props.GetNumberOfItems()):
            prop = props.GetItemAsObject(i)
            if isinstance(prop, vtkScalarBarActor):
                self.ren.RemoveActor(prop)
        actors: vtkActorCollection = self.ren.GetActors()
        for i in range(actors.GetNumberOfItems()):
            item = actors.GetItemAsObject(i)
            self.ren.RemoveActor(item)
        self.ren.RemoveActor(self._center_axes)
        self.display_axes()
        pass
    def rotate(self):
        print("rotate x")
        # self.rotateActor.RotateY(90)
        self._3dActor.RotateY(10)
        # self.GetRenderWindow().Render()
        self.iren.Render()

def coneActor():
    cone = vtkConeSource()
    cone.SetResolution(8)

    coneMapper = vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)
    return coneActor
    pass
c=coneActor()

def rotate():
    print("rotate")
    c.RotateY(10)
    pass
def main():

    # try:
    app = QtWidgets.QApplication.instance()  # checks if QApplication already exists
    if not app:  # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)

    
    win = vtkViewer3d()
    win.display_mesh(c)
    win.show()
    mytimer = QTimer()
    mytimer.timeout.connect(win.rotate)
    mytimer.start(2000)
   
    sys.exit(app.exec_())


main()




