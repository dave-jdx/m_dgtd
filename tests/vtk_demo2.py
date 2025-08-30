import vtk
import numpy as np

# 生成坐标点
theta, phi = np.linspace(0, np.pi, 20), np.linspace(0, 2*np.pi, 40)
theta, phi = np.meshgrid(theta, phi)
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# 构建polydata
points = vtk.vtkPoints()
for i in range(x.shape[0]):
    for j in range(x.shape[1]):
        points.InsertNextPoint(x[i, j], y[i, j], z[i, j])

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

# 生成球体
delaunay = vtk.vtkDelaunay3D()
delaunay.SetInputData(polydata)
delaunay.Update()
polydata = delaunay.GetOutput()

# 生成天线方向图
glyph = vtk.vtkGlyph3D()
glyph.SetInputData(polydata)

arrow = vtk.vtkArrowSource()
arrow.SetTipRadius(0.05)
arrow.SetShaftRadius(0.01)

glyph.SetSourceConnection(arrow.GetOutputPort())
glyph.SetVectorModeToUseNormal()
glyph.SetScaleModeToScaleByVector()

glyph.SetScaleFactor(0.1)
glyph.Update()

# 使用LUT对点进行渲染
lut = vtk.vtkLookupTable()
lut.SetTableRange(0, 1)
lut.SetHueRange(0.667, 0.0)
lut.SetSaturationRange(1, 1)
lut.SetValueRange(1, 1)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(glyph.GetOutput())
mapper.SetLookupTable(lut)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

renderWindow.Render()
interactor.Start()
