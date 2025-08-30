from typing import List,Set,Dict,Tuple
import time
from numpy import sin,cos,pi
from vtkmodules.all import(
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkPolyData,
    vtkPoints,
    vtkDoubleArray,
    vtkLookupTable,
    VTK_FLOAT,
    vtkCellArray,
    vtkStructuredGrid,
    vtkStructuredGridGeometryFilter,
    vtkTriangleFilter,
    vtkButterflySubdivisionFilter,
    vtkVertexGlyphFilter,
    vtkSurfaceReconstructionFilter,
    vtkMarchingCubes,
    vtkUnstructuredGrid,
    vtkUnstructuredGridGeometryFilter,
    vtkGeometryFilter,
    vtkDataSetSurfaceFilter,
    vtkColorTransferFunction,
    vtkNamedColors,
    vtkActor,
    vtkChart,
    vtkChartXY,
    vtkPlot,
    vtkTable,
    vtkFloatArray,
    vtkTetra
)

def currents_surface_mapper(pointList:List[Tuple[float,float,float,float]],
                            cells:List[Tuple[int,int,int]],
                            min:float,
                            max:float,
                            numberOfColors:int=256):
    '''构造表面电流图
    '''
   
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

    polys = vtkCellArray()

    for cell in cells:
        polys.InsertNextCell(3)
        for c in cell:
            polys.InsertCellPoint(c)
    polyData.SetPolys(polys)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()
    
    mapper=vtkDataSetMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(polyData)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)
       
    return mapper

def antenna_radio_pattern(pointList:List[Tuple[float,float,float,float]],
                         min:float,
                         max:float,
                         thetaNum:int,
                         phiNum:int,
                         numberOfColors:int=256):
    '''构造天线方向图
    '''
    start_time=time.time()
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])

    # polyData=vtkPolyData()
    # polyData.SetPoints(points)
    # polyData.GetPointData().SetScalars(scalarArr)


    # glyphFilter = vtkVertexGlyphFilter()
    # glyphFilter.SetInputData(polyData)
    # glyphFilter.Update()

    # pointsData=glyphFilter.GetOutput()
    # pointsData.GetPointData().SetScalars(scalarArr)

    grid = vtkStructuredGrid()
    grid.SetDimensions(phiNum, thetaNum, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    dsf=vtkDataSetSurfaceFilter()
    dsf.SetInputData(grid)
    dsf.Update()

    p:vtkPolyData=dsf.GetOutput()
    

    # surface = vtkStructuredGridGeometryFilter()
    # surface.SetInputData(grid)
    # surface.Update()

    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(p)

    filter = vtkButterflySubdivisionFilter()
    filter.SetInputConnection(triangleFilter.GetOutputPort())
    filter.SetNumberOfSubdivisions(2)
    filter.Update()

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()

    
    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(filter.GetOutput())
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)
    end_time = time.time()
    print("struct-dataset-unstruct读取耗时: {:.2f}秒".format(end_time - start_time))
    return mapper

def nf_surface(pointList:List[Tuple[float,float,float,float]],
               min:float,
               max:float,
               xNum:int,
               yNum:int,
               zNum:int,
               numberOfColors:int=256):
    
    colors=vtkNamedColors()
    # pointList=[(0,1,1,5),(0,2,1,10),(1,1,2,15),(1,2,2,20)]
    # min=5
    # max=20
    
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
    
    # grid = vtkStructuredGrid()
    # grid.SetDimensions(xNum, yNum, zNum)
    # grid.SetPoints(points)
    # grid.GetPointData().SetScalars(scalarArr)


    # surface = vtkDataSetSurfaceFilter()
    # surface.SetInputData(grid)
    # surface.Update()

    # surface = vtkStructuredGridGeometryFilter()
    # surface.SetInputData(grid)
    # surface.Update()


    # triangleFilter = vtkTriangleFilter()
    # triangleFilter.SetInputData(surface.GetOutput())

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(3)
    # filter.Update()

    polyData=vtkPolyData()
    polyData.SetPoints(points)
    # polyData.GetPointData().SetScalars(scalarArr)

    glyphFilter = vtkVertexGlyphFilter()
    glyphFilter.SetInputData(polyData)
    glyphFilter.Update()

    pointsData=glyphFilter.GetOutput()
    pointsData.GetPointData().SetScalars(scalarArr)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()

    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(pointsData)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(5)
    return actor,actor
    
    pass


def ffr_chart():

    table=vtkTable()

    arrX=vtkFloatArray()
    arrX.SetName("X Axis")
    table.AddColumn(arrX)

    arrC=vtkFloatArray()
    arrC.SetName("Cosine")
    table.AddColumn(arrC)

    arrS=vtkFloatArray()
    arrS.SetName("Sine");
    table.AddColumn(arrS);

    #Fill in the table with some example values.
    numPoints = 69
    inc = 7.5 / (numPoints - 1)
    table.SetNumberOfRows(numPoints)
    for i in range(numPoints):

        table.SetValue(i, 0, i * inc)
        table.SetValue(i, 1, cos(i * inc))
        table.SetValue(i, 2, sin(i * inc))
    
    chart=vtkChartXY()
    line:vtkPlot=chart.AddPlot(vtkChart.LINE)
    line.SetInputData(table, 0, 1)
    line.SetColor(0, 255, 0, 255)
    line.SetWidth(1.0)
    
    return chart
    
def thermal_3d(points_list:list,tetrahedra:list,temperature_values:list):
    # 创建 vtkPoints 对象并插入顶点
    points = vtkPoints()
    for coord in points_list:
        points.InsertNextPoint(coord)

    # 创建 vtkUnstructuredGrid 对象并设置点
    ugrid = vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    # 创建四面体单元格并添加到 unstructured grid
    for tetra in tetrahedra:
        tetra_cell = vtkTetra()
        for i in range(4):
            tetra_cell.GetPointIds().SetId(i, tetra[i])
        ugrid.InsertNextCell(tetra_cell.GetCellType(), tetra_cell.GetPointIds())

    # 创建 vtkFloatArray 来存储温度数据
    temperature = vtkFloatArray()
    temperature.SetName("温度(K)")
    for temp in temperature_values:
        temperature.InsertNextValue(temp)

    # 将温度数据添加到点数据中
    ugrid.GetPointData().SetScalars(temperature)

    # 创建映射器并设置标量范围
    mapper = vtkDataSetMapper()
    mapper.SetInputData(ugrid)
    mapper.SetScalarRange(temperature.GetRange())

    # 创建演员
    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor
    