import vtk
from math import tan
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
    vtkTransform,
    vtkSTLReader,
    vtkRenderWindow,
    vtkPolyData,
    vtkPolyDataNormals,
    vtkGeometryFilter,
    vtkOBJReader,
    vtkCellLocator,
    vtkGenericCell,
    vtkTriangle,
    vtkCellData,
    vtkPropAssembly
)

# 读取STL文件
# stl_reader = vtkSTLReader()
# stl_reader.SetFileName("D:/project/cae/emx1.1/src/tests/model/cube0.01.stl")
# stl_reader.Update()

obj_reader = vtkOBJReader()
obj_reader.SetFileName("D:/project/cae/emx1.1/src/tests/model/cube0.01.obj")
obj_reader.Update()

poly_data:vtkPolyData = obj_reader.GetOutput()


# 获取面的数量
num_faces = poly_data.GetNumberOfCells()
# print("The number of cell is:", num_faces)

# 创建Mapper和Actor
stl_mapper = vtkPolyDataMapper()
stl_mapper.SetInputData(poly_data)

stl_actor = vtkActor()
stl_actor.SetMapper(stl_mapper)
stl_actor.GetProperty().SetColor(0.5, 0.5, 1.0)

# 创建Renderer和RenderWindow
renderer = vtkRenderer()
render_axis=vtkRenderer()
render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
# render_window.AddRenderer(render_axis)


# 创建RenderWindowInteractor
interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# 将Actor添加到Renderer中
# renderer.AddActor(stl_actor)

transform = vtkTransform()
transform.Translate(-10.0, -10.0, 0)  # 你可以根据需要指定不同的平移值
# transform.RotateWXYZ(45, 0, 0, 1)  # 你可以根据需要指定不同的旋转角度

# 将vtkTransform应用到vtkAxesActor
d_len=20
_center_axes = vtkAxesActor()
_center_axes.SetPosition(0,0,0)
_center_axes.SetTotalLength(d_len,d_len,d_len)
_center_axes.SetConeRadius(0)
_center_axes.SetCylinderRadius(0.01)
# _center_axes.SetShaftTypeToCylinder()
_center_axes.SetShaftTypeToCylinder()
_center_axes.SetShaftTypeToLine()


# _center_axes.set
# _center_axes.SetShaftTypeToUserDefined()

# _center_axes.SetUserTransform(transform)
x_c_acotr:vtkCaptionActor2D=_center_axes.GetXAxisCaptionActor2D()

x_txt_actor:vtkTextActor=x_c_acotr.GetTextActor()
y_text_actor:vtkTextActor=_center_axes.GetYAxisCaptionActor2D().GetTextActor()
z_text_actor:vtkTextActor=_center_axes.GetZAxisCaptionActor2D().GetTextActor()

x_txt_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
y_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)
z_text_actor.SetTextScaleMode(vtkTextActor.TEXT_SCALE_MODE_NONE)


print("scale flag",vtkTextActor.TEXT_SCALE_MODE_NONE,
      vtkTextActor.TEXT_SCALE_MODE_PROP,
      vtkTextActor.TEXT_SCALE_MODE_VIEWPORT)
print("current flag",x_txt_actor.GetTextScaleMode())




x_axis_caption = _center_axes.GetXAxisCaptionActor2D()
# x_axis_caption.SetCaption("X axis")
_center_axes.SetXAxisLabelText("X")


text_property = vtkTextProperty()
text_property.SetFontSize(16)  # 设置字体大小为16
text_property.SetFontFamilyToArial()
text_property.BoldOff()  # 加粗
text_property.SetColor(1,0,0)


_center_axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(text_property)
cprop:vtkTextProperty=_center_axes.GetXAxisCaptionActor2D().GetCaptionTextProperty()
cpropy:vtkTextProperty=_center_axes.GetYAxisCaptionActor2D().GetCaptionTextProperty()
print("x font size",cprop.GetFontSize())
print("y font size",cpropy.GetFontSize())
# cprop.SetColor(1,0,0)
# cprop.SetFontSize(1)
# cprop.BoldOn()
x_text_actor = x_axis_caption.GetTextActor()
x_text_prop:vtkTextProperty = x_text_actor.GetTextProperty()
x_text_prop.SetColor(1, 0, 0)  # 设置x轴标签文本颜色为红色
# _center_axes.SetAxisLabels(1)
cpropy.SetFontSize(16)
cpropy.BoldOff()
cpropy.SetColor(0,1,0)
cprop.SetFontFamilyToArial()
# cprop.SetFontFamilyToCourier

distance_init=0
# _center_axes.SetScale(0.1)


# 通过拾取器拾取立方体的一个面
picker = vtkCellPicker()
picker.SetTolerance(0.001)
picker.PickFromListOn()
picker.AddPickList(stl_actor)
interactor.SetPicker(picker)




# 定义拾取事件的回调函数
def pick_callback(obj, event):
    
    click_pos = interactor.GetEventPosition()


    picker.Pick(click_pos[0], click_pos[1], 0, renderer)
    picked_points = picker.GetPickPosition()
    cell_id = picker.GetCellId()



    if cell_id != -1:
        print("Picked face of the cube. Cell ID:", cell_id)
        cell:vtkTriangle = stl_actor.GetMapper().GetInput().GetCell(cell_id)

        # 获取vtkPolyData
        poly_data = stl_actor.GetMapper().GetInput()

        # 获取CellData
        cell_data:vtkCellData = poly_data.GetCellData()
        
      
        
        num_faces = cell.GetNumberOfFaces()
      
        print("face num",num_faces)
        

        # original_faces = [cell.GetFaceId(i) for i in range(num_faces)]
        # print(f"Picked Cell Id: {cell_id}, Original Faces: {original_faces}")

        # 在这里可以根据需要执行其他操作，如获取面的信息、显示标注等
        # 通过CellId获取所属的FaceId
       
       

# 将拾取事件与回调函数关联
# picker.AddObserver("EndPickEvent", pick_callback)
# interactor.AddObserver("LeftButtonPressEvent", pick_callback)
def on_mousewheel(obj,event):
    # current_scale=renderer.GetActiveCamera().GetParallelScale()
    # print("scale:",current_scale)

    # 获取当前相机
    current_camera = renderer.GetActiveCamera()
    near_scale= current_camera.GetNearPlaneScale()
    point_scale=current_camera.GetFocalPointScale()
    b=_center_axes.GetBounds()
    # print("near scale:",near_scale)
    # print("point scale:",point_scale)
    distance_c=current_camera.GetDistance()
    

    print("distance",current_camera.GetDistance())
    zoom_factor=1
    if(distance_c>distance_init):
        zoom_factor=distance_init/distance_c
    if(distance_c<distance_init):
        zoom_factor=distance_init/distance_c
    # zoom_factor = round(1+(distance_init-distance_c)/distance_init,2)
    print("zoom factor:",zoom_factor)

    # 获取透视相机的视锥范围
    # near_clip, far_clip = current_camera.GetClippingRange()

    # # 获取透视相机的视角
    # view_angle = current_camera.GetViewAngle()

    # # 计算缩放比例
    # zoom_factor = far_clip / (2 * near_clip * tan(view_angle / 2.0))

    # print("Zoom Factor:", zoom_factor)
    # d_n=d_len*current_scale
    # _center_axes.SetTotalLength(10,10,10)

    # _center_axes.SetScale(1)
    d_n=d_len

    d_n=d_len/zoom_factor
    print("d_n",d_n/zoom_factor)
    _center_axes.SetTotalLength(d_n,d_n,d_n)
    pass
        

interactor.AddObserver("MouseWheelForwardEvent", on_mousewheel)
interactor.AddObserver("MouseWheelBackwardEvent", on_mousewheel)
# assm=vtkPropAssembly()
# assm.AddPart(_center_axes)
# assm.AddPart(stl_actor)
# renderer.GetActiveCamera().ParallelProjectionOn()
# renderer.GetActiveCamera().SetParallelScale(2.0)

renderer.AddActor(stl_actor)
renderer.AddActor(_center_axes)


# 设置Renderer的背景颜色
renderer.SetBackground(0.7, 0.7, 0.7)

# 设置RenderWindow的大小
render_window.SetSize(500, 500)

# 渲染和启动交互
render_window.Render()
current_scale=renderer.GetActiveCamera().GetParallelScale()
distance_init=renderer.GetActiveCamera().GetDistance()
print("init scale:",current_scale)
print("init distance",renderer.GetActiveCamera().GetDistance())
interactor.Start()

