import vtk

# 假设您有以下数据
# 顶点坐标列表
points_list = [
    (0.0, 0.0, 0.0),  # 点0
    (1.0, 0.0, 0.0),  # 点1
    (0.0, 1.0, 0.0),  # 点2
    (0.0, 0.0, 1.0),  # 点3
    # 添加更多点...
]

# 四面体单元格，定义为点的索引
tetrahedra = [
    (0, 1, 2, 3),
    # 添加更多四面体...
]

# 每个顶点的温度值
temperature_values = [
    100.0,  # 点0的温度
    150.0,  # 点1的温度
    200.0,  # 点2的温度
    250.0,  # 点3的温度
    # 添加更多温度值...
]

# 创建 vtkPoints 对象并插入顶点
points = vtk.vtkPoints()
for coord in points_list:
    points.InsertNextPoint(coord)

# 创建 vtkUnstructuredGrid 对象并设置点
ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(points)

# 创建四面体单元格并添加到 unstructured grid
for tetra in tetrahedra:
    tetra_cell = vtk.vtkTetra()
    for i in range(4):
        tetra_cell.GetPointIds().SetId(i, tetra[i])
    ugrid.InsertNextCell(tetra_cell.GetCellType(), tetra_cell.GetPointIds())

# 创建 vtkFloatArray 来存储温度数据
temperature = vtk.vtkFloatArray()
temperature.SetName("Temperature")
for temp in temperature_values:
    temperature.InsertNextValue(temp)

# 将温度数据添加到点数据中
ugrid.GetPointData().SetScalars(temperature)

# 创建映射器并设置标量范围
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(ugrid)
mapper.SetScalarRange(temperature.GetRange())

# 创建演员
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# 添加演员到渲染器
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)  # 设置背景颜色

# 添加标量条（颜色映射条）
scalar_bar = vtk.vtkScalarBarActor()
scalar_bar.SetLookupTable(mapper.GetLookupTable())
scalar_bar.SetTitle("Temperature")
scalar_bar.SetNumberOfLabels(5)
renderer.AddActor2D(scalar_bar)

# 开始渲染
render_window.Render()
interactor.Initialize()
interactor.Start()
