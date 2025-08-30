import vtk
import numpy as np

# 极坐标角度和半径数据
theta = np.linspace(0, 2 * np.pi, 36)
phi = np.linspace(0, np.pi, 18)
theta, phi = np.meshgrid(theta, phi)
r = np.ones_like(theta)

# 计算直角坐标系下的点位置
x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

# 天线增益值数据
gain = np.random.rand(len(theta.ravel()))

# 创建vtk数据对象
points = vtk.vtkPoints()
vertices = vtk.vtkCellArray()
scalars = vtk.vtkDoubleArray()
scalars.SetName("Gain")

# 将数据添加到vtk数据对象中
for i in range(len(theta.ravel())):
    id = points.InsertNextPoint(x.ravel()[i], y.ravel()[i], z.ravel()[i])
    vertices.InsertNextCell(1)
    vertices.InsertCellPoint(id)
    scalars.InsertNextValue(gain[i])

# 创建vtkPolyData对象
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetVerts(vertices)
polydata.GetPointData().SetScalars(scalars)

# 创建vtkSphereSource对象，作为glyph3D的源数据
sphere = vtk.vtkSphereSource()
sphere.SetRadius(0.05)
sphere.SetPhiResolution(10)
sphere.SetThetaResolution(10)

# 创建vtkGlyph3D对象
glyph = vtk.vtkGlyph3D()
glyph.SetInputData(polydata)
glyph.SetSourceConnection(sphere.GetOutputPort())
glyph.SetScaleModeToScaleByScalar()
glyph.SetScaleFactor(0.1)

# 创建vtkLookupTable对象，用于将天线增益值映射到颜色
lut = vtk.vtkLookupTable()
lut.SetTableRange(0, 1)
lut.SetHueRange(0.7, 0)
lut.Build()

# 创建vtkPolyDataMapper对象，用于将glyph3D的输出数据映射到可视化对象上
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(glyph.GetOutputPort())
mapper.SetScalarRange(0, 1)
mapper.SetLookupTable(lut)

# 创建vtkActor对象
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建vtkRenderer对象
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)
renderer.AddActor(actor)

# 创建vtkRenderWindow对象
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

renderWindow.Render()
interactor.Start()

print("ok")
