import numpy as np
from numpy import sin,cos,pi
import time

from vtkmodules.all import(
    vtkActor,
    vtkPolyDataMapper,
    vtkPoints,
    vtkLine,
    vtkCellArray,
    vtkPolyData,
    vtkRuledSurfaceFilter,
    vtkNamedColors,
    vtkConeSource,
    vtkLookupTable,
    vtkDoubleArray,
    vtkDelaunay2D,
    vtkDelaunay3D,
    vtkUnstructuredGrid,
    vtkDataSetMapper,
    vtkParametricFunctionSource,
    vtkPlaneSource,
    vtkVertexGlyphFilter,
    vtkTecplotReader,
    vtkGaussianKernel,
    vtkPointInterpolator,
    vtkPointDensityFilter,
    vtkPointLocator,
    vtkDelimitedTextReader,
    vtkTableToPolyData,
    vtkSTLReader,
    vtkImageData,
    vtkResampleWithDataSet,
    vtkPointGaussianMapper,
    vtkVolume,
    vtkSmartVolumeMapper,
    vtkColorTransferFunction,
    vtkPlotSurface,
    vtkSurfaceReconstructionFilter,
    vtkContourFilter,
    vtkImageActor,
    vtkImageMapper3D,
    vtkPointData,
    vtkLinearKernel,
    vtkGaussianSplatter,
    VTK_FLOAT,
    vtkSphereSource,
    vtkIdList,
    vtkVertex,
    vtkGaussianSplatter,
    vtkImageMapper,
    vtkGlyph3D,
    vtkPolarAxesActor,
    vtkWarpScalar,
    vtkTransformPolyDataFilter,
    vtkTriangleFilter,
    vtkButterflySubdivisionFilter
)
import vtk
import utils
import api_reader

# x = radius * sin(θ) * cos(φ)
# y = radius * sin(θ) * sin(φ)
# z = radius * cos(θ)
def sphereFace2():

    fpath="D:/project/cae/emx/src/data/"
    fname=fpath+"ffr3.txt"
    fList=api_reader.read_ffr(fname)
    item=fList[0]
    sphere=vtkSphereSource()
    radius=1
    # sphere.SetStartPhi(0)
    # sphere.SetEndPhi(180)
    # sphere.SetStartTheta(0)
    # sphere.SetEndTheta(360)
    start_time=time.time()
    
    sphere.SetThetaResolution(item[4])
    sphere.SetPhiResolution(item[3])
    sphere.SetRadius(radius)
    sphere.Update()

    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pointList=item[0]
    pointsX=item[5]
    min=item[1]
    max=item[2]
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)

    for i in range(pLen):
        p=pointList[i]
        px=pointsX[i]
        x = p[0]/p[3]

        y = p[1]/p[3]
        z = p[2]/p[3]
        id=sphere.GetOutput().FindPoint(x, y, z)
        if(id<0):
            continue
        # if(id>0):
        #     print(id)
        points.InsertPoint(id,[p[0],p[1],p[2]])
        scalarArr.SetValue(id,p[3])

    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.SetPolys(sphere.GetOutput().GetPolys())
    polyData.GetPointData().SetScalars(scalarArr)

    # triangleFilter = vtkTriangleFilter()
    # triangleFilter.SetInputData(polyData)

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(2)
    # filter.Update()

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(12)
    # print(lut.GetNumberOfTableValues())
    # lut.SetNumberOfColors(2)
    lut.SetTableRange(min,max)
    lut.Build()
    mapper=vtkPolyDataMapper()
    # mapper.SetInterpolateScalarsBeforeMapping(1)

    mapper.SetInputData(polyData)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)
    end_time = time.time()
    print("sphere读取耗时: {:.2f}秒".format(end_time - start_time))
    return mapper

    pass

def sphereFace():
    colors=vtkNamedColors()
    sphere=vtkSphereSource()
    radius=10
    sphere.SetStartPhi(0)
    sphere.SetEndPhi(180)
    sphere.SetStartTheta(0)
    sphere.SetEndTheta(180)
    sphere.SetThetaResolution(50)
    sphere.SetPhiResolution(50)
    print(sphere.GetThetaResolution(),sphere.GetPhiResolution())
    sphere.SetRadius(radius)
    sphere.Update()

    pointList=[
        (0,0,0),(0,30,0),(0,60,0),
        (10,0,0),(10,30,0),(10,60,0),
        (20,0,2),(20,10,2),(20,20,2),(20,30,1),(20,40,1),(20,50,1),
        (30,0,2),(30,10,3),(30,20,3),(30,30,2),(30,40,3),(30,50,3),
        (60,0,1.5),(60,30,1.5),(60,60,1.5),
        ]
    pointList=[]
    for i in range(0,180,10):
        for j in range(0,180,10):
            pointList.append((i,j,180-i))
    xyzList=[]

    scalarArr = vtkDoubleArray()
    scalarArr.SetNumberOfValues(len(pointList))
    points=vtkPoints()
    points.SetDataType(VTK_FLOAT)
    for item in pointList:
        x=radius*np.sin(item[0])*np.cos(item[1])
        y=radius*np.sin(item[0])*np.sin(item[1])
        z=radius*np.cos(item[0])
        xyzList.append((x,y,z,item[2]))
    
    for i in range(len(xyzList)):
        p=xyzList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
    

    min=10
    max=180

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(12)
    # print(lut.GetNumberOfTableValues())
    # lut.SetNumberOfColors(2)
    lut.SetTableRange(min,max)
    lut.Build()

    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)
    
    sphereData:vtkPolyData=sphere.GetOutput()
    # sphereData.GetPointData().SetScalars(scalarArr)
    # cells:vtkCellArray=sphereData.GetPolys()
    # cell = vtkIdList()
    # for i in range(cells.GetNumberOfCells()):
    #     cells.GetNextCell(cell)
    #     n = cell.GetNumberOfIds()
    #     print("Number of vertices in cell %d: %d" % (i, n))
        # for j in range(n):
        #     print("  Vertex %d: %d" % (j, cell.GetId(j)))
    
    
    # sphereData.SetPoints(points)
    # sphereData.GetPointData().SetScalars(scalarArr)

    bounds = np.array(sphereData.GetBounds())
    dims = np.array([101, 101, 101])
    box = vtkImageData()
    box.SetDimensions(dims)
    box.SetSpacing((bounds[1::2] - bounds[:-1:2]) / (dims - 1))
    box.SetOrigin(bounds[::2])


    gaussian_kernel = vtkGaussianKernel()
    gaussian_kernel.SetSharpness(2)
    gaussian_kernel.SetRadius(3)

    linearKernel = vtkLinearKernel()
    linearKernel.SetRadius(10)

    interpolator = vtkPointInterpolator()
    interpolator.SetInputData(sphere.GetOutput())
    interpolator.SetSourceData(polyData)
    interpolator.SetKernel(gaussian_kernel)
    interpolator.Update()

    resample = vtkResampleWithDataSet()
    resample.SetInputData(sphereData)
    resample.SetSourceConnection(interpolator.GetOutputPort())

    warp = vtkWarpScalar()
    warp.SetInputConnection(resample.GetOutputPort())
    warp.SetScaleFactor(0.1)
  

    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)

    # mapper.SetInputData(sphereData)
    mapper.SetInputConnection(resample.GetOutputPort())
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)
    

    actor=vtkActor()
    actor.SetMapper(mapper)

    # actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    # actor.GetProperty().SetPointSize(6)
   
    return actor,actor
    
    

    pass

def plotSurface():
    fList=utils.readCurrent()
    pointList=fList[0][0]
    min=fList[0][2]
    max=fList[0][3]

    points = vtkPoints()
    points.SetDataType(VTK_FLOAT)
    scalarArr = vtkDoubleArray()
    
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])

    polyData=vtkPolyData()
    polyData.SetPoints(points)

    
    polyData.GetPointData().SetScalars(scalarArr)

    tris = vtkCellArray()
    cells=fList[0][1]

    for cell in cells:
        tris.InsertNextCell(3)
        for c in cell:
            tris.InsertCellPoint(c)
    polyData.SetPolys(tris)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(12)
    # print(lut.GetNumberOfTableValues())
    # lut.SetNumberOfColors(2)
    lut.SetTableRange(min,max)
    lut.Build()
    
    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(polyData)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)
    
    
    actor = vtkActor()
    actor.SetMapper(mapper)
    
    return actor,actor

    pass

def pointInterpolator():
    pass

def pointSTLFace():
    # points_fn="D:/project/cae/vtk-examples-master/src/Python/sparsePoints.txt"
    points_fn="D:/project/cae/emx/src/data/a.txt"
    probe_fn="D:/project/cae/emx/src/data/model.stl"

    points_reader = vtkDelimitedTextReader()
    points_reader.SetFileName(points_fn)
    points_reader.DetectNumericColumnsOn()
    points_reader.SetFieldDelimiterCharacters('\t')
    points_reader.SetHaveHeaders(True)

    table_points = vtkTableToPolyData()
    table_points.SetInputConnection(points_reader.GetOutputPort())
    table_points.SetXColumn('x')
    table_points.SetYColumn('y')
    table_points.SetZColumn('z')
    table_points.Update()

    points = table_points.GetOutput()
    points.GetPointData().SetActiveScalars('val')
    range_s = points.GetPointData().GetScalars().GetRange()



    #获取要显示的模型面
    stl_reader = vtkSTLReader()
    stl_reader.SetFileName(probe_fn)
    stl_reader.Update()
    surface:vtkPolyData = stl_reader.GetOutput()


    # fList=utils.readCurrent()
    # pointList=fList[0][0]
    # points2 = vtkPoints()
    # scalarArr = vtkDoubleArray()
    # pLen=len(pointList)
    # scalarArr.SetNumberOfValues(pLen)
    # for i in range(pLen):
    #     p=pointList[i]
    #     points2.InsertPoint(i,[p[0],p[1],p[2]])
    #     scalarArr.SetValue(i,p[3])
    # vpData:vtkPointData=surface.GetPointData()
    # surface.SetPoints(points2)
    # surface.GetPointData().SetScalars(scalarArr)
   
    plane = vtkPlaneSource()
    plane.SetResolution(200,200)
    plane.SetOrigin(0,0,0)
    plane.SetPoint1(200,0,0)
    plane.SetPoint2(0,200,0)
    plane.SetCenter(0,0,0)
    plane.SetNormal(0,0,1)

    bounds = np.array(surface.GetBounds())
    dims = np.array([101, 101, 101])
    box = vtkImageData()
    box.SetDimensions(dims)
    box.SetSpacing((bounds[1::2] - bounds[:-1:2]) / (dims - 1))
    box.SetOrigin(bounds[::2])


    gaussian_kernel = vtkGaussianKernel()
    gaussian_kernel.SetSharpness(4)
    gaussian_kernel.SetRadius(0.5)

    linearKernel = vtkLinearKernel()
    linearKernel.SetRadius(2.5)
    
    

    interpolator = vtkPointInterpolator()
    interpolator.SetInputData(surface)
    interpolator.SetSourceData(points)
    interpolator.SetKernel(gaussian_kernel)
    interpolator.Update()

    # pointsN=interpolator.GetOutput()



    resample = vtkResampleWithDataSet()
    resample.SetInputData(surface)
    resample.SetSourceConnection(interpolator.GetOutputPort())
   

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(1479)
    lut.SetNumberOfColors(100)
    lut.SetTableRange(range_s)
    lut.Build()

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(resample.GetOutputPort())
    mapper.SetScalarRange(range_s)
    # mapper.SetLookupTable(lut)
    
    mapper.Update()

    actor = vtkActor()
    actor.SetMapper(mapper)
    


    point_mapper = vtkPointGaussianMapper()
    point_mapper.SetInputData(points)
    point_mapper.SetScalarRange(0,61)
    point_mapper.SetScaleFactor(0.6)
    point_mapper.EmissiveOff()
    point_mapper.SetSplatShaderCode(
        "//VTK::Color::Impl\n"
        "float dist = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);\n"
        "if (dist > 1.0) {\n"
        "  discard;\n"
        "} else {\n"
        "  float scale = (1.0 - dist);\n"
        "  ambientColor *= scale;\n"
        "  diffuseColor *= scale;\n"
        "}\n"
    )

    point_actor = vtkActor()
    point_actor.SetMapper(point_mapper)
    return actor,point_actor



    

    fList=utils.readCurrent()
    pointList=fList[0][0]
    min=fList[0][2]
    max=fList[0][3]

    polyData=vtkPolyData()
    lut = vtkLookupTable()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    lut.SetHueRange(0.667, 0)
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
    tris = vtkCellArray()
    cells=fList[0][1]

    for cell in cells:
        tris.InsertNextCell(3)
        for c in cell:
            tris.InsertCellPoint(c)
    polyData.SetPoints(points)

    


    
    # polyData.SetPoints(points)
    # polys=surface.GetPolys()
    # print(polys.GetNumberOfCells())
    # polyData.SetPolys(tris)
    # polyData.GetPointData().SetScalars(scalarArr)

    surface.SetVerts(tris)
    surface.SetPoints(points)
    pointsxx=surface.GetPointData()
    surface.GetPointData().SetScalars(scalarArr)

    mapper = vtkPolyDataMapper()
    # mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(surface)
    mapper.SetScalarRange(min, max)
    mapper.SetLookupTable(lut)
    mapper.Update()

    actor = vtkActor()
    actor.SetMapper(mapper)
    
    return actor


    pass

def pointVertex():
    fName=""
    colors=vtkNamedColors()

    fList=utils.readCurrent()
    pointList=fList[0][0]
    min=fList[0][2]
    max=fList[0][3]

    pointList=[(0,1,1,5),(0,2,1,10),(1,1,2,15),(1,2,2,20)]

    pointActor = vtkActor()  

    pointsMapper=vtkPolyDataMapper()

    polyData=vtkPolyData()

    lut = vtkLookupTable()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    lut.SetHueRange(0.667, 0)
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
    polyData.SetPoints(points)
    # polyData.SetPolys(tris)



    # kernel = vtkGaussianKernel()
    # kernel.SetRadius(0.1)
    # kernel.SetSharpness(3)

    # interpolator = vtkPointInterpolator()

    # interpolator.SetInputData(polyData)
    # interpolator.SetSourceData(polyData)
    # interpolator.SetKernel(kernel)
    # interpolator.Update()
    # interpolator.SetNullPointsStrategyToNullValue()

    # rData=interpolator.GetOutput()

    glyphFilter = vtkVertexGlyphFilter()
    glyphFilter.SetInputData(polyData)
    glyphFilter.Update()

    pointsData=glyphFilter.GetOutput()
    pointsData.GetPointData().SetScalars(scalarArr)

    # rData.GetPointData().SetScalars(scalarArr)

    # polyData.GetPointData().SetScalars(scalarArr)
    
    pointsMapper.SetInterpolateScalarsBeforeMapping(1)
    pointsMapper.SetInputData(pointsData)
    pointsMapper.SetScalarRange(min, max)
    pointsMapper.SetLookupTable(lut)
    pointsMapper.Update()
    pointActor.SetMapper(pointsMapper)
    pointActor.GetProperty().SetColor(colors.GetColor3d("Red"))
    pointActor.GetProperty().SetPointSize(3)

    # triangulatedMapper.SetInputConnection(tpoy.GetOutputPort())
    # tActor.SetMapper(triangulatedMapper)




    return pointActor,pointActor

    pass

def planeSurface():
    # 创建平面源
    plane = vtkPlaneSource()
    plane.SetResolution(1000, 50)
    plane.SetOrigin(-0.5, -0.5, 0)
    plane.SetPoint1(0.5, -0.5, 0)
    plane.SetPoint2(-0.5, 0.5, 0)
    
    

    # 创建mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(plane.GetOutputPort())

    # 创建actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor
def pSurface():
    # 创建一个vtkParametricFunctionSource对象
    parametricFunction = vtk.vtkParametricFunctionSource()

    # 设置参数函数
    parametricFunction.SetParametricFunction(vtk.vtkParametricSuperEllipsoid())

    # 设置等距参数分布
    parametricFunction.SetUResolution(100)
    parametricFunction.SetVResolution(100)
    parametricFunction.SetWResolution(100)

    # 生成数据
    parametricFunction.Update()

    # 获取输出数据
    surface = parametricFunction.GetOutput()

    # 创建一个 mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(surface)

    # 创建一个 actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor

def pointsPoly3D():
    points = vtkPoints()
    points.InsertNextPoint(1.0, 2.0, 0)
    points.InsertNextPoint(2.0, 2.0, 0)
    points.InsertNextPoint(2, 3, 1)

    points.InsertNextPoint(2, 0, 0.5)

    # Create a polydata object
    polydata = vtkPolyData()
    polydata.SetPoints(points)

    # Perform Delaunay triangulation
    delaunay = vtkDelaunay3D()
    delaunay.SetInputData(polydata)
    delaunay.Update()

    # Create a mapper and actor
    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(delaunay.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor
#根据点和三角面显示云图
def pointsSurface3D():
    pointList=[]
    #构造点集合
    pointList.append((0,0,0,0.1))
    pointList.append((1,0,0,0.15))

    pointList.append((1,1,0,0.35))
    pointList.append((0,1,0,0.45))

    pointList.append((1,1,1,0.55))
    pointList.append((0,1,1,0.55))

    tris = vtkCellArray()
    cells = [[3,4,2],[3,2,1],[5,6,3],[5,3,1] ]

    probe_fn="D:/project/cae/emx/src/data/model.stl"
    stl_reader = vtkSTLReader()
    stl_reader.SetFileName(probe_fn)
    stl_reader.Update()
    surface:vtkPolyData = stl_reader.GetOutput()

    fList=utils.readCurrent()
    pointList=fList[0][0]
    # cells=fList[0][1]

    for cell in cells:
        tris.InsertNextCell(3)
        for c in cell:
            tris.InsertCellPoint(c)

    min=0
    max=60

    actor = vtkActor()    
    mapper=vtkPolyDataMapper()
    polyData=vtkPolyData()
    lut = vtkLookupTable()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    # lut.SetHueRange(0.667, 0)
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,[p[0]*1000,p[1]*1000,p[2]*1000])
        scalarArr.SetValue(i,p[3])

    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)


    # polyData.SetPolys(tris)

    color_function = vtkColorTransferFunction()
    color_function.AddRGBPoint(0.0, 0.0, 0.0, 1.0)
    color_function.AddRGBPoint(1, 1.0, 1.0, 1.0)

    volume = vtkVolume()
    volume.SetMapper(vtkSmartVolumeMapper())
    volume.GetMapper().SetInputData(polyData)
    volume.GetMapper().SetBlendModeToComposite()
    # volume.GetProperty().SetScalarOpacity(0.5)
    volume.GetProperty().SetColor(color_function)
    return volume

    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(polyData)
    mapper.SetScalarRange(min, max)
    mapper.SetLookupTable(lut)
    mapper.Update()
    actor.SetMapper(mapper)
    return actor


    pass
def pointsMap3D():

    pointList=[]

    # pointList.append((1,2,0,0.2))
    # pointList.append((2,2,0,0.25))
    # pointList.append((2,3,1,0.25))
    # pointList.append((2,0,0.5,0.25))

    pointList.append((0,0,0,0.1))
    pointList.append((1,0,0,0.15))

    pointList.append((2,0,0,0.2))
    pointList.append((2,1,0,0.25))
    pointList.append((2,2,0,0.25))

    pointList.append((1,2,0,0.3))
    pointList.append((0,2,0,0.35))
    pointList.append((0,1,0,0.5))

    pointList.append((2,0,1,0.2))
    pointList.append((2,1,1,0.25))
    pointList.append((2,2,1,0.25))

    pointList.append((1.8,0,1.5,0.5))
    pointList.append((1.8,1,1.5,0.5))
    pointList.append((1.8,2,1.5,0.5))

    pointList.append((1.5,0,0.6,0.5))
    pointList.append((1.5,1,0.7,0.5))
    pointList.append((1.5,2,0.8,0.5))

    pointList.append((1.5,3,0.6,0.5))
    pointList.append((1.6,3,0.7,0.5))
    pointList.append((1.5,2,0.8,0.5))

    min=0.1
    max=60

    actor = vtkActor()    
    mapper=vtkDataSetMapper()
    polyData=vtkPolyData()
    lut = vtkLookupTable()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    lut.SetHueRange(0.667, 0)
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,p[0],p[1],p[2])
        scalarArr.SetValue(i,p[3])
    polyData.SetPoints(points)

    tpoy = vtkDelaunay3D()
    tpoy.SetInputData(polyData)
    tpoy.Update()
    tpoy.GetOutput()

    result:vtkUnstructuredGrid = tpoy.GetOutput()
    result.GetPointData().SetScalars(scalarArr)

    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(min, max)
    mapper.SetLookupTable(lut)
    mapper.Update()
    actor.SetMapper(mapper)
    return actor

def pointsMap2D():
    pointList=[]
    pointList.append((0,0,0,0.1))
    pointList.append((1,0,0,0.15))

    pointList.append((2,0,0,0.2))
    pointList.append((2,1,0,0.25))
    pointList.append((2,2,0,0.25))

    pointList.append((1,2,0,0.3))
    pointList.append((0,2,0,0.35))
    pointList.append((0,1,0,0.5))

    fList=utils.readCurrent()


    pointList=fList[0][0]

    

    min=0.1
    max=60

    actor = vtkActor()    
    mapper=vtkPolyDataMapper()
    polyData=vtkPolyData()
    lut = vtkLookupTable()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    lut.SetHueRange(0.667, 0)
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,p[0],p[1],p[2])
        scalarArr.SetValue(i,p[3])
    polyData.SetPoints(points)
    tpoy = vtkDelaunay2D()
    tpoy.SetInputData(polyData)
    tpoy.Update()

    result:vtkPolyData = tpoy.GetOutput()
    result.GetPointData().SetScalars(scalarArr)
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(min, max)
    mapper.SetLookupTable(lut)
    mapper.Update()
    actor.SetMapper(mapper)
    return actor



    pass

def getActor():
    colors=vtkNamedColors()
    # Create the points fot the lines.
    points = vtkPoints()
    points.InsertPoint(0, 0, 0, 1)
    points.InsertPoint(1, 1, 0, 0)
    points.InsertPoint(2, 0, 1, 0)
    points.InsertPoint(3, 1, 1, 1)

    # Create line1
    line1 = vtkLine()
    line1.GetPointIds().SetId(0, 0)
    line1.GetPointIds().SetId(1, 1)

    # Create line2
    line2 = vtkLine()
    line2.GetPointIds().SetId(0, 2)
    line2.GetPointIds().SetId(1, 3)

    # Create a cellArray containing the lines
    lines = vtkCellArray()
    lines.InsertNextCell(line1)
    lines.InsertNextCell(line2)

    # Create the vtkPolyData to contain the points and cellArray with the lines
    polydata = vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)

    # Create the ruledSurfaceFilter from the polydata containing the lines
    ruledSurfaceFilter = vtkRuledSurfaceFilter()
    ruledSurfaceFilter.SetInputData(polydata)
    ruledSurfaceFilter.SetResolution(21, 21)
    ruledSurfaceFilter.SetRuledModeToResample()

    # Create the mapper with the ruledSurfaceFilter as input
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(ruledSurfaceFilter.GetOutputPort())

    # Create the actor with the mapper
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("Banana"))
    actor.GetProperty().SetSpecular(0.6)
    actor.GetProperty().SetSpecularPower(30)
    return actor
    pass
def coneActor():
    cone = vtkConeSource()
    cone.SetResolution(8)

    coneMapper = vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)
    pass