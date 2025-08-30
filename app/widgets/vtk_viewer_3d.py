from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QAction
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
from ..mixins import ComponentMixin
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonDataModel import vtkPolyData
from ..api import api_vtk
from. .api.customInterStyle import CustomInterStyle

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
    vtkCubeSource,
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
    vtkTransform,
    vtkLight,
    vtkVertexGlyphFilter
)
COLOR_AXIS_X = (0.81, 0, 0)
COLOR_AXIS_Y=(0,0.81,0)
COLOR_AXIS_Z=(0,0,0.81)


class vtkViewer3d(QVTKRenderWindowInteractor):

    name = 'viewer 3d'
    sigPointClicked=pyqtSignal(int,tuple)#(pointId,pointCoords)

    def __init__(self, parent=None):
        self.parent = parent
        super(vtkViewer3d, self).__init__(parent)
        interStyle=CustomInterStyle(self)
        # interStyle=vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(interStyle)
        self.ren = vtkRenderer()
        self.GetRenderWindow().AddRenderer(self.ren)
        self._highlight_radius = 0.15

        self.iren: vtkRenderWindowInteractor = self.GetRenderWindow().GetInteractor()

        self.axesActor = None
        self.axes: vtkOrientationMarkerWidget = None

        # 创建一个标签演员用于显示所选边的 ID
        self.label_actor = vtkTextActor()
        self.label_actor.GetTextProperty().SetColor(0.8, 0, 0)  # 设置标签颜色为红色
        self.label_actor.GetTextProperty().SetFontSize(18)

        self.pickedSourcePolyData: vtkPolyData = None

        self._3dActor: vtkActor = None  # 当前正在显示的3d actor 包含网格/表面电流/FFR/NFR/NF
        self._modelActor: vtkActor = None  # 当前正在显示的模型actor
        self._arrayActor:vtkActor=None #阵列天线的actor
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
        self._vector_axes=vtkAxesActor()
        self._center_axes_oririn=(0,0,0)
        self._actor_custom=[]

        self._nfr_initTransform=None

        self._light=vtkLight()

        # show the widget
        self.Initialize()
        self.Start()
        self.show()
        self.onLoad()

    def onLoad(self):
        self.ren.SetBackground(0.86, 0.86, 0.86)
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
        self.initVectorAxes()
        # self.testCone()
        self.ren.SetUseImageBasedLighting(False)
        self.ren.SetUseDepthPeeling(False)
        self.ren.LightFollowCameraOff()

        # self.ren.SetUseDepthPeeling(True)
        # self.ren.SetMaximumNumberOfPeels(100)
        # self.ren.SetOcclusionRatio(0.1)

        light = self._light
        light.SetLightTypeToCameraLight()
      
        # light.SetPosition(0, 1,0 )  # 光源位置
        # light.SetFocalPoint(0, 0, 0)  # 光源焦点
        light.SetColor(0.9, 0.9, 0.9)  # 光源颜色（白色）
        light.SetIntensity(0.1)  # 光源强度
        self.ren.AddLight(light)

        pass

    def testCone(self):
        axesLength = 2
        self._center_axes.SetTotalLength(axesLength, axesLength, axesLength)
        self._center_axes.SetConeRadius(0.1)
        self.ren.AddActor(self._center_axes)

        cone = vtkConeSource()
        cone.SetResolution(8)

        coneMapper = vtkPolyDataMapper()
        coneMapper.SetInputConnection(cone.GetOutputPort())

        coneActor = vtkActor()
        coneActor.GetProperty().SetColor(0, 1, 0)
        coneActor.SetMapper(coneMapper)
        self.ren.AddActor(coneActor)
        self.ren.ResetCamera()
        self._3dActor = coneActor

    def initCenterAxes(self):
        # 获取x/y/z轴的vtkCaptionActor2D对象
        axes=self._center_axes
        d_len=1000
        axes.SetShaftTypeToLine()
        axes.SetTotalLength(d_len,d_len,d_len)
        axes.SetConeRadius(0)

        # text_property = vtkTextProperty()
        # text_property.SetFontSize(12)  # 设置字体大小为16
        # text_property.SetFontFamilyToArial()
        # text_property.BoldOff()  # 加粗
        # text_property.SetColor(1,0,0)

        # x_text=vtkTextProperty()
        # x_text.SetFontSize(12)  # 设置字体大小为16
        # x_text.SetFontFamilyToArial()
        # x_text.BoldOff()  # 加粗
        # x_text.SetColor(1,0,0)
        
        


        # y_text=vtkTextProperty()
        # y_text.SetFontSize(12)  # 设置字体大小为16
        # y_text.SetFontFamilyToArial()
        # y_text.BoldOff()  # 加粗
        # y_text.SetColor(0,1,0)

        # z_text=vtkTextProperty()
        # z_text.SetFontSize(12)  # 设置字体大小为16
        # z_text.SetFontFamilyToArial()
        # z_text.BoldOff()  # 加粗
        # z_text.SetColor(0,0,1)

        # x_axis_caption = axes.GetXAxisCaptionActor2D()
        # y_axis_caption = axes.GetYAxisCaptionActor2D()
        # z_axis_caption = axes.GetZAxisCaptionActor2D()

        # x_axis_caption.SetCaptionTextProperty(x_text)
        # y_axis_caption.SetCaptionTextProperty(y_text)
        # z_axis_caption.SetCaptionTextProperty(z_text)
        
        # x_axis_caption.SetWidth(20)
        # y_axis_caption.SetWidth(40)
        # z_axis_caption.SetWidth(60)

        # 获取vtkTextActor对象并设置颜色
        # x_text_actor:vtkTextActor = x_axis_caption.GetTextActor()
        # x_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)

        # y_text_actor:vtkTextActor = y_axis_caption.GetTextActor()
        # y_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
        
        # z_text_actor:vtkTextActor = z_axis_caption.GetTextActor()
        # z_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
        # self.ren.AddActor(self._center_axes)
        axes.SetXAxisLabelText("")
        axes.SetYAxisLabelText("")
        axes.SetZAxisLabelText("")

        x: vtkProperty = axes.GetXAxisShaftProperty()
        
        y: vtkProperty = axes.GetYAxisShaftProperty()
        
        z: vtkProperty = axes.GetZAxisShaftProperty()
        
        x.SetColor(COLOR_AXIS_X)
        y.SetColor(COLOR_AXIS_Y)
        z.SetColor(COLOR_AXIS_Z)
        x.SetOpacity(0.3)
        y.SetOpacity(0.3)
        z.SetOpacity(0.3)
        x.SetLineStipplePattern(0xf0f0)
        x.SetLineStippleRepeatFactor(1)
        

        # transform = vtkTransform()
        # transform.RotateX(45)
        # axes.SetUserTransform(transform)
        # axes.RotateWXYZ(45, 0, 0, 1)

       
        


        
        
        # x_shaft_prop.SetLineStipplePattern(0xf0f0)
        # x_shaft_prop.SetLineStippleRepeatFactor(5)


    def initVectorAxes(self):
        axes=self._vector_axes
        d_len=1000
        axes.SetShaftTypeToLine()
        axes.SetTotalLength(d_len,d_len,d_len)
        
        axes.SetConeRadius(0)

        # text_property = vtkTextProperty()
        # text_property.SetFontSize(12)  # 设置字体大小为16
        # text_property.SetFontFamilyToArial()
        # text_property.BoldOff()  # 加粗
        # text_property.SetColor(1,0,0)

        # x_text=vtkTextProperty()
        # x_text.SetFontSize(12)  # 设置字体大小为16
        # x_text.SetFontFamilyToArial()
        # x_text.BoldOff()  # 加粗
        # x_text.SetColor(1,0,0)
        

        # y_text=vtkTextProperty()
        # y_text.SetFontSize(12)  # 设置字体大小为16
        # y_text.SetFontFamilyToArial()
        # y_text.BoldOff()  # 加粗
        # y_text.SetColor(0,1,0)

        # z_text=vtkTextProperty()
        # z_text.SetFontSize(12)  # 设置字体大小为16
        # z_text.SetFontFamilyToArial()
        # z_text.BoldOff()  # 加粗
        # z_text.SetColor(0,0,1)

        # x_axis_caption = axes.GetXAxisCaptionActor2D()
        # y_axis_caption = axes.GetYAxisCaptionActor2D()
        # z_axis_caption = axes.GetZAxisCaptionActor2D()

        # x_axis_caption.SetCaptionTextProperty(x_text)
        # y_axis_caption.SetCaptionTextProperty(y_text)
        # z_axis_caption.SetCaptionTextProperty(z_text)
        

        # # 获取vtkTextActor对象并设置颜色
        # x_text_actor:vtkTextActor = x_axis_caption.GetTextActor()
        # x_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
        

        # y_text_actor:vtkTextActor = y_axis_caption.GetTextActor()
        # y_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
        

        # z_text_actor:vtkTextActor = z_axis_caption.GetTextActor()
        # z_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
        # self.ren.AddActor(self._center_axes)
        axes.SetXAxisLabelText("")
        axes.SetYAxisLabelText("")
        axes.SetZAxisLabelText("")

        x: vtkProperty = axes.GetXAxisShaftProperty()
        
        y: vtkProperty = axes.GetYAxisShaftProperty()
        
        z: vtkProperty = axes.GetZAxisShaftProperty()
        
        x.SetColor(COLOR_AXIS_X)
        y.SetColor(COLOR_AXIS_Y)
        z.SetColor(COLOR_AXIS_Z)

        x.SetLineWidth(3)
        y.SetLineWidth(3)
        z.SetLineWidth(3)
        # x.SetOpacity(0.3)
        # y.SetOpacity(0.3)
        # z.SetOpacity(0.3)



    def printViewPosition(self):
        c = self.ren.GetActiveCamera()
        print("FocalPoint", c.GetFocalPoint())
        print("ViewUp:", c.GetViewUp())
        print("Position", c.GetPosition())

    def mouseReleaseEvent(self, ev):
        # self.printViewPosition()
        return super().mouseReleaseEvent(ev)

    def display_scalarBar(self):
        '''显示标量颜色条
        '''
        barActor = api_vtk.scalar_actor(0, 1, "NFR(db)")
        self.ren.AddActor(barActor)

        # self.barTitle.SetPosition(self.GetRenderWindow().GetScreenSize()[0]/2,100)
        # self.barTitle.SetInput("NFR(db)")
        # self.ren.AddActor(self.barTitle)

        # print(self.GetRenderWindow().GetSize(),self.GetRenderWindow().GetScreenSize())
        self.ren.ResetCamera()
        self.GetRenderWindow().Render()

        pass

    def range_fixed(self, min: float, max: float,numberOfColors:int=256):
        if(self._3dActor is None):
            return
        lut:vtkLookupTable= self._3dActor.GetMapper().GetLookupTable()
        lut.SetNumberOfColors(numberOfColors)
        self._3dActor.GetMapper().SetScalarRange(min, max)
        lutBar: vtkLookupTable = self._barActor.GetLookupTable()
        lutBar.SetRange(min, max)
     
        # self._3dActor.Modified()
        # self._3dActor.GetMapper().Modified()
        # print("new range",self._3dActor.GetMapper().GetLookupTable().GetRange())
        self.iren.Render()
        # self.GetRenderWindow().Render()

    def range_auto(self,numberOfColors:int=256):
        if(self._3dActor is None):
            return
        min = self._rangeAuto[0]
        max = self._rangeAuto[1]
        lut:vtkLookupTable= self._3dActor.GetMapper().GetLookupTable()
        lut.SetNumberOfColors(numberOfColors)
        self._3dActor.GetMapper().SetScalarRange(min, max)
        lutBar: vtkLookupTable = self._barActor.GetLookupTable()
        lutBar.SetRange(min, max)
        self.iren.Render()

    def display_axes(self):
        self.axesActor = vtkAxesActor()
        # self.axesActor.SetCylinderRadius(0.1)

        x: vtkProperty = self.axesActor.GetXAxisShaftProperty()
        x.SetLineWidth(4)
        y: vtkProperty = self.axesActor.GetYAxisShaftProperty()
        y.SetLineWidth(4)
        z: vtkProperty = self.axesActor.GetZAxisShaftProperty()
        z.SetLineWidth(4)
        x.SetColor(COLOR_AXIS_X)
        y.SetColor(COLOR_AXIS_Y)
        z.SetColor(COLOR_AXIS_Z)

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
    
    def display_array(self,actor:vtkActor):
        self.ren.RemoveActor(self._arrayActor)
        self._arrayActor = actor
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.GetRenderWindow().Render()
        

    def display_model(self, actor: vtkActor):
       
        # actor.GetProperty().SetRepresentationToWireframe()
        self.ren.RemoveActor(self._modelActor)
        self._modelActor = actor
        self.ren.AddActor(actor)

        
        # self.ren.SetAmbient(2,2,2)
        self.ren.ResetCamera()
        
        
        self.GetRenderWindow().Render()


    def display_nf_ex(self, actor: vtkActor, first: bool = False, barActor: vtkScalarBarActor = None, cLength: float = 1):
        self.hide_points()
        self._3dActor = actor
        self._barActor = barActor
        self._rangeAuto = actor.GetMapper().GetLookupTable().GetRange()
        self.clear()
        self.end_pick()

        self._highlight_radius = 0.01  # 设置选中时的球体大小
        # axesLength = cLength
        # self._center_axes.SetTotalLength(axesLength, axesLength, axesLength)
        # self._center_axes.SetConeRadius(0.1)

        # self.ren.AddActor(self._center_axes)
        self.ren.AddActor(actor)
        self.ren.AddActor(self._modelActor)
        if(barActor != None):
            self.ren.AddActor(barActor)
        if(first):
            self.ren.ResetCamera()
        self.iren.Render()
        pass
    def mesh_vertex_actor(self,point:tuple):
        self.highlight_points = vtkPoints()
        self.highlight_points.InsertPoint(0,[point[0], point[1], point[2]])
        self.highlight_polydata = vtkPolyData()
        self.highlight_polydata.SetPoints(self.highlight_points)

        self.vertex_filter = vtkVertexGlyphFilter()
        self.vertex_filter.SetInputData(self.highlight_polydata)

        self.highlight_mapper = vtkPolyDataMapper()
        self.highlight_mapper.SetInputData(self.vertex_filter.GetOutput())

        self.highlight_actor = vtkActor()
        self.highlight_actor.SetMapper(self.highlight_mapper)
        self.highlight_actor.GetProperty().SetPointSize(100)  # 设置点的大小
        self.highlight_actor.GetProperty().SetColor(1, 0, 0)
        return self.highlight_actor

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
        # self.ren.GetActiveCamera().SetViewUp(-0.4,0.55,0.72)
        pass

    def hide_mesh(self, actor: vtkActor):
        self.ren.RemoveActor(actor)
        self.iren.Render()

    # def display_currents(self, actor: vtkActor, barActor: vtkScalarBarActor = None):
    #     self.hide_points()
    #     self._3dActor = actor
    #     self._barActor = barActor
    #     self._rangeAuto = actor.GetMapper().GetLookupTable().GetRange()
    #     self.clear()
    #     self.ren.AddActor(actor)
    #     if(barActor != None):
    #         self.ren.AddActor(barActor)
    #     self.iren.Render()
    #     pass

    def display_ffr(self, actor: vtkActor, barActor: vtkScalarBarActor = None):
        '''
        显示远场电磁辐射方向图
        '''
        self.hide_points()
        self._3dActor = actor
        self._barActor = barActor
        self._rangeAuto = actor.GetMapper().GetLookupTable().GetRange()
        self.clear()
        self.end_pick()
        self.ren.AddActor(actor)
        axesLength = 150
        self._center_axes.SetTotalLength(axesLength, axesLength, axesLength)
        self._center_axes.SetConeRadius(0.1)
        self.ren.AddActor(self._center_axes)
        if(barActor != None):
            self.ren.AddActor(barActor)
        self.ren.ResetCamera()
        self.iren.Render()
        pass

    def display_nfr(self, actor: vtkActor, barActor: vtkScalarBarActor = None,originPoint:tuple=(0,0,0)):
        '''
        显示近场电磁辐射方向图
        '''
        self.hide_points()
        
       
        center_axes=self._center_axes
        vector_axes=self._vector_axes
        self._center_axes_oririn=originPoint
        
        transform = vtkTransform()
        transform.Translate(originPoint[0], originPoint[1], originPoint[2])
        # transform.RotateX(45)
        actor.SetUserTransform(transform)
        center_axes.SetUserTransform(transform)
        vector_axes.SetUserTransform(transform)



        # axesLength = 800
        # self._center_axes.SetTotalLength(axesLength, axesLength, axesLength)
        # self._center_axes.SetConeRadius(0.5)
        # self._center_axes.SetUserTransform(transform)
        # self._center_axes.GetXAxisCaptionActor2D().SetCaption("X axis")
        # txtProp=vtkTextProperty()
        # txtProp.SetColor(1,0,0)
        # txtProp.SetFontSize(2)
        # self._center_axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(txtProp)


        self.ren.AddActor(center_axes)
        self.ren.AddActor(vector_axes)

        # self.ren.RemoveActor(self._3dActor)
        # self.ren.RemoveActor(self._barActor)
        
        self._3dActor = actor
        
        # self._nfr_initTransform=actor.GetUserTransform()

        
        self._barActor = barActor
        self._rangeAuto = actor.GetMapper().GetLookupTable().GetRange()
        # self.clear()
        self.end_pick()
        self.ren.AddActor(actor)

        if(barActor != None):
            self.ren.AddActor(barActor)
        self.ren.ResetCamera()
        # self.ren.ResetCameraScreenSpace()
        # self._RenderWindow.Render()
        
        self.iren.Render()
        # self.GetRenderWindow().Render()
        pass

    def display_nf(self, actor: vtkActor, first: bool = False, barActor: vtkScalarBarActor = None, cLength: float = 1):
        '''
        显示近场电磁环境
        '''
        self.hide_points()
        self._3dActor = actor
        self._barActor = barActor
        self._rangeAuto = actor.GetMapper().GetLookupTable().GetRange()
        self.clear()
        self.end_pick()

        self._highlight_radius = 0.01  # 设置选中时的球体大小
        axesLength = cLength
        self._center_axes.SetTotalLength(axesLength, axesLength, axesLength)
        self._center_axes.SetConeRadius(0.1)

        self.ren.AddActor(self._center_axes)
        self.ren.AddActor(actor)
        if(barActor != None):
            self.ren.AddActor(barActor)
        if(first):
            self.ren.ResetCamera()
        self.iren.Render()
        pass

    def display_points(self, actor: vtkActor, points, actor2: vtkActor):
        '''显示数据点
        '''
        self.pointsActor = actor
        self.pointsActor.GetProperty().SetOpacity(0.5)
        self._sphereActor = actor2
        self.pickedSourcePolyData = actor.GetMapper().GetInput()
        self._points = points
        self.ren.AddActor(self.pointsActor)
        self.ren.AddActor(self._sphereActor)
        self.iren.Render()

        # print("pointsNum",self.pickedSourcePolyData.GetNumberOfPoints(),self._points.GetNumberOfPoints())
    def hide_points(self):
        '''隐藏数据点
        '''
        self.end_pick()
        if(self.pointsActor is not None):
            self.ren.RemoveActor(self.pointsActor)
        if(self._sphereActor is not None):
            self.ren.RemoveActor(self._sphereActor)
        self.iren.Render()

    def display_surface(self):
        self.ren.RemoveActor(self._3dActor)
        self.ren.AddActor(self._3dActor)
        self.end_pick()
        self.iren.Render()
        pass

    def hide_surface(self):
        self.ren.RemoveActor(self._3dActor)
        self.iren.Render()
        pass

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

    def scaleActor(self, actor: vtkActor, scale):  
        actor.SetScale(scale) 
        self.iren.Render()

    def rotate_axis(self,angle:tuple):
        axes=self._center_axes
        originPoint=self._center_axes_oririn
        transform = vtkTransform()
        transform.Translate(originPoint[0], originPoint[1], originPoint[2])
        transform.RotateX(angle[0])
        transform.RotateY(angle[1])
        transform.RotateZ(angle[2])
        axes.SetUserTransform(transform)
        self.iren.Render()

    def rotate_radio(self, actor:vtkActor,angle: tuple):
        #绕X轴逆时针旋转，角度为正
        # roate the actor
        # print("rotate", angle)
        actor.RotateX(angle[0])
        # print("rotate x",angle[0])
        actor.RotateY(angle[1])
        # print("rotate y",angle[1])
        actor.RotateZ(angle[2])
        # print("rotate z",angle[2])
        

        self.iren.Render()

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
        self.iren.Render()
        pass

    def start_point_picker(self):
        picker = vtkPointPicker()
        # picker.AddPickList(self.pointsActor)
        self.pointPicker = picker
        picker.SetTolerance(0.01)
        self.iren.SetPicker(picker)
        self.iren.AddObserver("LeftButtonPressEvent", self.point_pick_callback)
        self.iren.AddObserver("LeftButtonReleaseEvent",
                              self.point_pick_callback)
        self.iren.AddObserver("LeftButtonDoubleClickEvent",
                              self.point_pick_callback)
        self.iren.AddObserver(vtkCommand.MouseMoveEvent,
                              self.point_hover_callback)
        self.iren.SetInteractorStyle(vtkInteractorStyleRubberBandPick())
        # self.ren.AddActor(self.getSphere())

    def start_cell_picker(self):
        picker = vtkCellPicker()
        self.cellPicker = picker
        self.iren.SetPicker(picker)
        self.iren.AddObserver(
            vtkCommand.LeftButtonPressEvent, self.cell_pick_callback)
        self.iren.AddObserver(
            vtkCommand.LeftButtonReleaseEvent, self.cell_pick_callback)
        self.iren.AddObserver(
            vtkCommand.LeftButtonDoubleClickEvent, self.cell_pick_callback)
        self.iren.AddObserver(vtkCommand.MouseMoveEvent,
                              self.cell_hover_callback)
        # self.ren.AddActor(self.getSphere())
        self.iren.SetInteractorStyle(vtkInteractorStyleRubberBandPick())
        pass

    def start_prop_picker(self):
        picker = vtkPropPicker()
        self.cellPicker = picker

        self.iren.SetPicker(picker)
        self.iren.AddObserver(
            vtkCommand.LeftButtonPressEvent, self.prop_pick_callback)
        self.iren.AddObserver(
            vtkCommand.LeftButtonReleaseEvent, self.prop_pick_callback)
        self.iren.AddObserver(
            vtkCommand.LeftButtonDoubleClickEvent, self.prop_pick_callback)
        self.iren.AddObserver(vtkCommand.MouseMoveEvent,
                              self.prop_hover_callback)
        # self.ren.AddActor(self.getSphere())
        self.iren.SetInteractorStyle(vtkInteractorStyleRubberBandPick())
        pass

    def end_pick(self):
        self.iren.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
        pass
    def clear_point_selected(self):
        for key in self.pointSelected:
            self.ren.RemoveActor(self.pointSelected[key])
        self.pointSelected.clear()
        self.iren.Render()
    def init_point_selected(self,pointId:int):
        
        pickedActor = self.point_highlight_actor(
            pointId, color=(1, 0, 0))
        self.pointSelected[pointId] = pickedActor
        self.ren.AddActor(pickedActor)
        self.iren.Render()


    # 定义一个回调函数，用于处理拾取事件
    def point_pick_callback(self, obj: vtkRenderWindowInteractor, event):
        picker = obj.GetPicker()
        position = obj.GetEventPosition()

        picker.Pick(position[0], position[1], 0, self.ren)
        point_id = picker.GetPointId()
        # if point_id != -1:
        #     point_coords = self.pickedSourcePolyData.GetPoints().GetPoint(point_id)
        #     print(f"拾取的点编号: {point_id}")
        #     print(f"坐标值: {point_coords}")
        # else:
            # print("未拾取到任何点")
            # pass
        # self.ren.RemoveActor2D(self.label_actor)
        
        
        if obj.GetRepeatCount() == 1:
            if point_id >= 0 and point_id < self.pickedSourcePolyData.GetNumberOfPoints():
                # for key in self.pointSelected: #清除所有已选择的点，单选模式
                #     self.ren.RemoveActor(self.pointSelected[key])
                # self.pointSelected.clear()
                if point_id in self.pointSelected:  # 已经选中时，双击取消
                    # self.ren.RemoveActor(self.pointSelected[point_id])
                    # del self.pointSelected[point_id]
                    return
                   
                # v = self.scalar_value(point_id)
                pickedActor = self.point_highlight_actor(
                    point_id, color=(1, 0, 0))
                # pickedActor=self.mesh_vertex_actor(self.pickedSourcePolyData.GetPoints().GetPoint(point_id))
                self.pointSelected[point_id] = pickedActor
                point_coords = self.pickedSourcePolyData.GetPoints().GetPoint(point_id)
                self.label_actor.SetPosition(
                    10, self.GetRenderWindow().GetSize()[1]-20)
                # print(self.GetRenderWindow().GetSize(),self.GetRenderWindow().GetScreenSize())
                # self.label_actor.SetInput(
                #     "Selected point: ({:.2f}, {:.2f}, {:.2f},{:.6f})".format(*point_coords, v))
                # self.ren.AddActor2D(self.label_actor)
                self.ren.AddActor(pickedActor)
                self.sigPointClicked.emit(point_id,point_coords)
                keys_deleted=[]
                for key in self.pointSelected: #清除所有已选择的点，单选模式
                    if(key!=point_id):
                        self.ren.RemoveActor(self.pointSelected[key])
                        keys_deleted.append(key)
                for key in keys_deleted:
                    del self.pointSelected[key]


               
                # print("Selected point ID:", point_id)
                # print("Selected point coordinates:", point_coords)
                self.iren.Render()

    def scalar_value(self, point_id):
        v = -1
        scalar_arr: vtkDoubleArray = self.pickedSourcePolyData.GetPointData().GetScalars()
        if(point_id < scalar_arr.GetNumberOfValues()):
            v = scalar_arr.GetValue(point_id)

        else:
            # print("out of range",point_id,scalar_arr.GetNumberOfValues())
            pass
        # print(v)
        return v
        pass

    def point_hover_callback(self, obj: vtkRenderWindowInteractor, event):
        picker = obj.GetPicker()
        position = obj.GetEventPosition()
        picker.Pick(position[0], position[1], 0, self.ren)
        point_id = picker.GetPointId()

        if point_id != -1:
            # point = self._3dActor.GetOutput().GetPoint(point_id)
            # print(f"拾取的点编号: {point_id}")
            pass
            # print(f"坐标值: {point}")
        else:
            # print("未拾取到任何点")
            pass

        return
        self.ren.RemoveActor(self.pointHoverActor)
        self.ren.RemoveActor2D(self.label_actor)
        if point_id >= 0 and point_id < self.pickedSourcePolyData.GetNumberOfPoints():

            v = self.scalar_value(point_id)
            self.pointHoverActor = self.point_highlight_actor(
                point_id)  # 高亮并显示一个新的actor

            point_coords = self.pickedSourcePolyData.GetPoints().GetPoint(point_id)
            self.label_actor.SetPosition(
                10, self.GetRenderWindow().GetSize()[1]-20)
            # c="Selected point: ({:.2f}, {:.2f}, {:.2f})".format(*point_coords)
            # print(self.GetRenderWindow().GetSize(),self.GetRenderWindow().GetScreenSize())
            self.label_actor.SetInput(
                "Selected point: ({:.2f}, {:.2f}, {:.2f},{:.6f})".format(*point_coords, v))
            self.ren.AddActor2D(self.label_actor)  # 添加标签演员到渲染器中
            self.ren.AddActor(self.pointHoverActor)
            # print("Selected point ID:", point_id)
            # print("Selected point coordinates:", point_coords)
            self.iren.Render()
        pass

    def cell_hover_callback(self, obj: vtkRenderWindowInteractor, event):
        picker: vtkCellPicker = obj.GetPicker()
        position = obj.GetEventPosition()
        picker.Pick(position[0], position[1], 0, self.ren)
        cell_id = picker.GetCellId()
        self.ren.RemoveActor2D(self.label_actor)
        self.ren.RemoveActor(self.cellHoverActor)
        if cell_id >= 0:
            self.cellHoverActor = self.cell_highlight_actor(cell_id, (0, 1, 1))

            self.label_actor.SetPosition(
                10, self.GetRenderWindow().GetSize()[1]-20)
            self.label_actor.SetInput("Selected cell ID: {}".format(cell_id))
            self.ren.AddActor2D(self.label_actor)
            self.ren.AddActor(self.cellHoverActor)
            self.iren.Render()

        pass

    def cell_pick_callback(self, obj: vtkRenderWindowInteractor, event):
        picker: vtkCellPicker = obj.GetPicker()
        position = obj.GetEventPosition()
        picker.Pick(position[0], position[1], 0, self.ren)
        cell_id = picker.GetCellId()
        self.ren.RemoveActor2D(self.label_actor)

        if obj.GetRepeatCount() == 1:
            if cell_id >= 0:
                if cell_id in self.cellSelected:  # 已经选中时，双击取消
                    self.ren.RemoveActor(self.cellSelected[cell_id])
                    return
                pickedActor = self.cell_highlight_actor(cell_id)
                self.cellSelected[cell_id] = pickedActor
                self.label_actor.SetInput(
                    "Selected cell ID: {}".format(cell_id))
                self.ren.AddActor2D(self.label_actor)
                self.ren.AddActor(pickedActor)
                self.iren.Render()

    def point_highlight_actor(self, point_id: int, color=(0.5, 0.5, 0.5)):

        # point_coords = self._points.GetPoint(point_id)
        point_coords=self.pickedSourcePolyData.GetPoints().GetPoint(point_id)
        sphereSource = vtkSphereSource()
        sphereSource.SetCenter(point_coords)
        sphereSource.SetRadius(self._highlight_radius)
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        return actor
        pass

    def clear_cell_selected(self):
        for v in self.cellSelected.values():
            self.ren.RemoveActor(v)
        pass

    def display_cell(self, cell_id: int):
        self.clear_cell_selected()
        pickedActor = self.cell_highlight_actor(cell_id)
        self.cellSelected[cell_id] = pickedActor
        self.ren.AddActor(pickedActor)
        self.iren.Render()
        pass

    def cell_highlight_actor(self, cell_id: int, hcolor=(1, 0, 0)):
        id_list = vtkIdList()
        # 将需要提取的单元格的id添加到id_list中
        id_list.InsertNextId(cell_id)
        extract_cells = vtkExtractCells()
        extract_cells.SetInputData(self.pickedSourcePolyData)
        extract_cells.SetCellList(id_list)
        extract_cells.Update()

        # 创建一个mapper和actor来显示高亮效果
        highlight_mapper = vtkDataSetMapper()
        highlight_mapper.SetInputData(extract_cells.GetOutput())

        highlight_actor = vtkActor()
        highlight_actor.SetMapper(highlight_mapper)
        highlight_actor.GetProperty().SetColor(
            hcolor[0], hcolor[1], hcolor[2])  # 设置高亮颜色为红色
        highlight_actor.GetProperty().SetRepresentationToWireframe()
        # highlight_actor.GetProperty().SetRepresentationToSurface()
        highlight_actor.GetProperty().SetLineWidth(3)
        return highlight_actor
        pass

    def prop_hover_callback(self, obj: vtkRenderWindowInteractor, event):
        picker: vtkPropPicker = obj.GetPicker()
        position = obj.GetEventPosition()
        picker.Pick(position[0], position[1], 0, self.ren)
        prop = picker.GetProp3D()

        if prop:
            if isinstance(prop, vtkLine):
                print("选中了一条线")
            else:
                pass
                # print("选中的不是一条线")
            # 设置拾取到的prop为高亮
            # prop.GetProperty().SetColor(1, 0, 0)
            # self.iren.Render()
        pass

    def prop_pick_callback(self, obj: vtkRenderWindowInteractor, event):
        pass
    def reset_camera(self):
        self.ren.ResetCamera()
    def remove_actor(self,actor:vtkActor):
        self.ren.RemoveActor(actor)
        self.iren.Render()
    def display_actor(self,actor:vtkActor,isCustom=True):
        #单独显示的actor可以全部清除
        self.ren.AddActor(actor)
        if(not isCustom): #不再定制actor范围内的，需要调用全局clear才可以清除
            return
        if(actor in self._actor_custom):
            self._actor_custom.remove(actor)
        self._actor_custom.append(actor)

        # self.GetRenderWindow().Render()
            
        self.iren.Render()
        
    def clear_actor_custom(self):
        for a in self._actor_custom:
            self.ren.RemoveActor(a)
        self._actor_custom.clear()
        self.iren.Render()

    def set_axis_center_lenth(self,length:float):
        self._center_axes.SetTotalLength(length,length,length)
        self.iren.Render()
    def set_axis_line_width(self,width:float):
        self._center_axes.GetXAxisShaftProperty().SetLineWidth(width)
        self._center_axes.GetYAxisShaftProperty().SetLineWidth(width)
        self._center_axes.GetZAxisShaftProperty().SetLineWidth(width)
        self.iren.Render()
    def display_axis_center(self):
        self.ren.RemoveActor(self._center_axes)
        self.ren.AddActor(self._center_axes)
        self.iren.Render()
        pass
    def hide_axis_center(self):
        self.ren.RemoveActor(self._center_axes)
        self.iren.Render()
        pass
    def render_manual(self):
        self.iren.Render()
