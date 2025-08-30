from typing import List,Set,Dict,Tuple
import numpy as np
from numpy import sin,cos,pi
from vtkmodules.all import(
    vtkSTLReader,
    vtkActor,
    vtkScalarBarActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkPolyData,
    vtkPoints,
    vtkDoubleArray,
    vtkLookupTable,
    VTK_FLOAT,
    VTK_DOUBLE,
    vtkCellArray,
    vtkStructuredGrid,
    vtkStructuredGridGeometryFilter,
    vtkTriangleFilter,
    vtkButterflySubdivisionFilter,
    vtkDataSetSurfaceFilter,
    vtkVertexGlyphFilter,
    vtkNamedColors,
    vtkDelaunay2D,
    vtkDelaunay3D,
    vtkTransform,
    vtkTransformFilter,
    vtkChart,
    vtkTable,
    vtkFloatArray,
    vtkChartXY,
    vtkPlot,
    vtkAxis,
    vtkRectf,
    vtkTextProperty,
    vtkConeSource,
    vtkLineSource,
    vtkSphereSource,
    vtkGlyph3D,
    vtkWindowToImageFilter,
    vtkPNGWriter,
    vtkRenderWindow,
    vtkSurfaceReconstructionFilter,
    vtkContourFilter,
    vtkUnstructuredGridReader,
    VTK_TETRA,
    vtkLine,
    vtkUnstructuredGrid,
    vtkTetra

    
)
def stl_mesh(fname:str):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata:vtkPolyData = reader.GetOutput()

    mapper = vtkPolyDataMapper()
    mapper.SetInputData(polydata)


    actor = vtkActor()
    actor.SetMapper(mapper)
    
    #actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    
    return actor
def stl_model(fname:str,opacity=0.5,color=None):
    '''
    显示stl文件为模型
    '''
    reader = vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata:vtkPolyData = reader.GetOutput()

    mapper = vtkPolyDataMapper()
    mapper.SetInputData(polydata)


    actor = vtkActor()
    actor.SetMapper(mapper)
    
    # actor.GetProperty().SetRepresentationToWireframe()
    # actor.GetProperty().SetEdgeVisibility(1)
    #rgb(178,288,255)
    # actor.GetProperty().SetColor(0.5, 0.5, 0.9)
    # actor.GetProperty().SetColor(178/255,228/255,1)
    if(color is None):
        actor.GetProperty().SetColor(58/255, 101/255, 144/255)
    else:
        actor.GetProperty().SetColor(color[0],color[1],color[2])
    # actor.GetProperty().SetColor(109/255, 217/255, 217/255)
    actor.GetProperty().SetOpacity(opacity)
    
    
    return actor
def set_opacity(actorList:list,opacity:float):
    if(opacity<0 or opacity>1):
        opacity=0
    if(actorList is None):
        return
    if(len(actorList)==0):
        return
    for actor in actorList:
        actor.GetProperty().SetOpacity(opacity)

def currents_surface(pointList:List[Tuple[float,float,float,float]],
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

    actor=vtkActor()
    actor.SetMapper(mapper)
       
    return actor

def antenna_radio_pattern(pointList:List[Tuple[float,float,float,float]],
                         min:float,
                         max:float,
                         thetaNum:int,
                         phiNum:int,
                         numberOfColors:int=256):
    '''构造天线方向图
    '''
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()


    #region 旧的三维方向图方法舍弃
    # grid = vtkStructuredGrid()   
    # grid.SetDimensions(thetaNum, phiNum, 1)
    # grid.SetPoints(points)
    # grid.GetPointData().SetScalars(scalarArr)

    # surface = vtkDataSetSurfaceFilter()
    # surface.SetInputData(grid)
    # surface.Update()


    # triangleFilter = vtkTriangleFilter()
    # triangleFilter.SetInputData(surface.GetOutput())

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(1)
    # filter.Update()
    # mapper=vtkPolyDataMapper()
    # mapper.SetInterpolateScalarsBeforeMapping(1)
    # mapper.SetInputData(filter.GetOutput())
    # mapper.SetScalarRange(min,max)
    # mapper.SetLookupTable(lut)
    # endregion
    grid = vtkStructuredGrid()
    grid.SetDimensions(phiNum, thetaNum, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    surface = vtkDataSetSurfaceFilter()
    surface.SetInputData(grid)
    surface.Update()

    mapper = vtkDataSetMapper()
    mapper.SetInputData(surface.GetOutput()) # 直接用原网格
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)


    actor=vtkActor()
    actor.SetMapper(mapper)
    return actor
def nf_surface(pointList:List[Tuple[float,float,float,float]],
               min:float,
               max:float,
               dIndex:int=2,
               xNum:int=11,
               yNum:int=6,
               zNum:int=1,
               numberOfColors:int=256):
    '''
    近场电磁环境图形显示，dIndex 2-xy面 1-xz面 0-yz面
    '''
    
    colors=vtkNamedColors()
    
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])


    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)

    # tpoy = vtkDelaunay2D()
    # tpoy.SetInputData(polyData)
    # tpoy.Update()
    result:vtkPolyData=None

    # tpoy = vtkDelaunay2D()
    # if(dIndex==2):
    #     tpoy.SetInputData(polyData)
    #     tpoy.Update()
    #     result=tpoy.GetOutput()
    #     pass
    # elif(dIndex==1):
    #     transFilter = vtkTransformFilter()
    #     transForm=vtkTransform()
    #     transForm.RotateX(90)
    
    #     transFilter.SetInputData(polyData)
    #     transFilter.SetTransform(transForm)
    #     transFilter.Update()

    #     tpoy.SetInputData(transFilter.GetOutput())
    #     tpoy.Update()

    #     transForm2=vtkTransform()
    #     transForm2.RotateX(-90)
    #     transFilter.SetInputData(tpoy.GetOutput())
    #     transFilter.SetTransform(transForm2)
    #     transFilter.Update()
    #     result=transFilter.GetOutput()
    # elif(dIndex==0):

    #     transForm=vtkTransform()
    #     transForm.RotateY(90)

    #     transFilter = vtkTransformFilter()
    #     transFilter.SetInputData(polyData)
    #     transFilter.SetTransform(transForm)
    #     transFilter.Update()
    #     tpoy.SetInputData(transFilter.GetOutput())
    #     tpoy.Update()

    #     transForm2=vtkTransform()
    #     transForm2.RotateY(-90)
    #     transFilter.SetTransform(transForm2)
    #     transFilter.SetInputData(tpoy.GetOutput())
    #     transFilter.Update()
    #     result=transFilter.GetOutput()
    #     pass


    grid = vtkStructuredGrid()
    if(dIndex==2):
        grid.SetDimensions(xNum, yNum, 1)
    elif(dIndex==1):
        grid.SetDimensions(xNum,1,zNum)
    elif(dIndex==0):
        grid.SetDimensions(1,yNum,zNum)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    surface = vtkStructuredGridGeometryFilter()
    surface.SetInputData(grid)
    surface.Update()
    result=surface.GetOutput()

  
    # glyphFilter = vtkVertexGlyphFilter()
    # glyphFilter.SetInputData(polyData)
    # glyphFilter.Update()
    # pointsData=glyphFilter.GetOutput()
    # pointsData.GetPointData().SetScalars(scalarArr)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()

    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)

    actor=vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(5)
    # actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    return actor
    pass
def cloud_map_cells(pointList:List[Tuple[float,float,float,float]]):
    '''
    输入的点数据分布在一个平面上，根据阵列特点构造cells
    '''
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    minV=1e9
    maxV=-1e9
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
        if(p[3]<minV):
            minV=p[3]
        if(p[3]>maxV):
            maxV=p[3]
        #构造cells
    cells = vtkCellArray()
    for i in range(0, pLen-1, 2):
        cells.InsertNextCell(3)
        cells.InsertCellPoint(i)
        cells.InsertCellPoint(i+1)
        cells.InsertCellPoint(i+2)

        cells.InsertNextCell(3)
        cells.InsertCellPoint(i+2)
        cells.InsertCellPoint(i+1)
        cells.InsertCellPoint(i+3)
    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)
    polyData.SetPolys(cells)
    # polyData.GetPointData().SetScalars(scalarArr)
    #渲染显示
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    mapper = vtkPolyDataMapper()

    mapper.SetInputData(polyData)
    mapper.SetScalarRange(minV,maxV)
    mapper.SetLookupTable(lut)
    actor=vtkActor()
    actor.SetMapper(mapper)
    return actor

def cloud_surface(pointList:List[Tuple[float,float,float,float]],numberOfColors=256):
    points=vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    minV=0
    maxV=0
    for i in range(pLen):
        p=pointList[i]
        # points.InsertPoint(i,[p[0],p[1],p[2]])
        points.InsertNextPoint(p[0],p[1],p[2])
        scalarArr.SetValue(i,p[3])
        if p[3]<minV:
            minV=p[3]
        if p[3]>maxV:
            maxV=p[3]
    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)

    delaunay = vtkDelaunay2D()
    delaunay.SetInputData(polyData)
    delaunay.Update()


    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    mapper = vtkPolyDataMapper()

    mapper.SetInputData(delaunay.GetOutput())
    mapper.SetScalarRange(minV,maxV)
    mapper.SetLookupTable(lut)
    actor=vtkActor()
    actor.SetMapper(mapper)
    # actor.SetScale(1000)
    return actor
def cloud_map_unstruct(pointList:List[Tuple[float,float,float,float]]):
    '''
    云图显示显示某个面的云图 (x,y,z,value)
    '''
    minV=0
    maxV=0
    for p in pointList:
        if(p[3]<minV):
            minV=p[3]
        if(p[3]>maxV):
            maxV=p[3]
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        # points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])

    data_points = [
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.5, 0.5, 0.5),
]

    for point in data_points:
        points.InsertNextPoint(point)

# 创建 vtkPolyData 对象并设置点



    poly_data=vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.GetPointData().SetScalars(scalarArr)

   



  
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    surface_reconstruction_filter = vtkSurfaceReconstructionFilter()
    surface_reconstruction_filter.SetInputData(poly_data)
    surface_reconstruction_filter.Update()

    # 使用 vtkContourFilter 提取等值线（等值面）
    # contour_filter = vtkContourFilter()
    # contour_filter.SetInputConnection(surface_reconstruction_filter.GetOutputPort())
    # contour_filter.SetValue(0, 0.0)  # 设置等值线的值
    # contour_filter.Update()





    # result=surface.GetOutput()

  

    mapper=vtkPolyDataMapper()
    # mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputConnection(surface_reconstruction_filter.GetOutputPort())
    # mapper.SetScalarRange(minV,maxV)
    # mapper.SetLookupTable(lut)

    actor=vtkActor()
    actor.SetMapper(mapper)
 
    actor.SetScale(1000)
    # actor.GetProperty().SetPointSize(5)
    # actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    return actor

    pass
def cloud_map_nf(pointList:List[Tuple[float,float,float,float]],numberOfColors=256):
    '''
    云图显示显示某个面的云图 (x,y,z,value)-规则排列数据
    '''
    minV=1e9
    maxV=-1e9
    #排序
    xNum=len(list(set(t[4] for t in pointList)))
    yNum=len(list(set(t[5] for t in pointList)))
    zNum=len(list(set(t[6] for t in pointList)))
    if(zNum==1):#xy面
        pointList=sorted(pointList, key=lambda x: x[5])
    elif(yNum==1):#xz面
        pointList=sorted(pointList, key=lambda x: x[6])
    elif(xNum==1):#yz面
        pointList=sorted(pointList, key=lambda x: x[6])
    for p in pointList:
        if(p[3]<minV):
            minV=p[3]
        if(p[3]>maxV):
            maxV=p[3]
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])


    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)
    result:vtkPolyData=None
    grid = vtkStructuredGrid()

    grid.SetDimensions(xNum,yNum,zNum)
   

    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    surface = vtkStructuredGridGeometryFilter()
    surface.SetInputData(grid)
    surface.Update()

    result=surface.GetOutput()
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    # transform = vtkTransform()
    # transform.Translate(center[0],center[1], center[2])
    # transform.Translate(0,0,1000)

    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(minV,maxV)
    mapper.SetLookupTable(lut)

    actor=vtkActor()
    actor.SetMapper(mapper)
    # actor.SetUserTransform(transform)
    actor.SetScale(1000)
    # actor.GetProperty().SetPointSize(5)
    # actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    return actor

    pass

def cloud_map(pointList:List[Tuple[float,float,float,float]],numberOfColors=256,_xNum=-1,_yNum=-1):
    '''
    云图显示显示某个面的云图 (x,y,z,value)-规则排列数据
    '''
    minV=1e9
    maxV=-1e9
    # pointList.sort(key=lambda x:(x[2],x[1],x[0]))
    # pointList.remove(pointList[0])
    # pointList.remove(pointList[0])
    # _xNum=-1
    if(_xNum<0):#排序
        xNum=len(list(set(t[0] for t in pointList)))
        yNum=len(list(set(t[1] for t in pointList)))
        zNum=len(list(set(t[2] for t in pointList)))
        if(zNum==1):#xy面
            pointList=sorted(pointList, key=lambda x: x[1])
        elif(yNum==1):#xz面
            pointList=sorted(pointList, key=lambda x: x[2])
        elif(xNum==1):#yz面
            pointList=sorted(pointList, key=lambda x: x[2])
    for p in pointList:
        if(p[3]<minV):
            minV=p[3]
        if(p[3]>maxV):
            maxV=p[3]
    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])


    polyData=vtkPolyData()
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)
    result:vtkPolyData=None
    grid = vtkStructuredGrid()
    # if(dIndex==2):
    #     grid.SetDimensions(xNum, yNum, 1)
    # elif(dIndex==1):
    #     grid.SetDimensions(xNum,1,zNum)
    # elif(dIndex==0):
    #     grid.SetDimensions(1,yNum,zNum)
    if(_xNum>0 and _yNum>0):
        grid.SetDimensions(_xNum,_yNum,1)
    # if(xNum>1 and yNum>1):
    #     grid.SetDimensions(xNum,yNum,1)
    else:
        xNum=len(list(set(t[0] for t in pointList)))
        yNum=len(list(set(t[1] for t in pointList)))
        zNum=len(list(set(t[2] for t in pointList)))
        grid.SetDimensions(xNum,yNum,zNum)
   

    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    surface = vtkStructuredGridGeometryFilter()
    surface.SetInputData(grid)
    surface.Update()

    result=surface.GetOutput()
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    # transform = vtkTransform()
    # transform.Translate(center[0],center[1], center[2])
    # transform.Translate(0,0,1000)

    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(minV,maxV)
    mapper.SetLookupTable(lut)

    actor=vtkActor()
    actor.SetMapper(mapper)
    # actor.SetUserTransform(transform)
    actor.SetScale(1000)
    # actor.GetProperty().SetPointSize(5)
    # actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    return actor

    pass
def chart_line(points:List[Tuple[float,float]],xName="X Axis",yName="Y Axis",displayPoints:bool=True):
    '''使用二维曲线显示 x y轴的数据几何
    Args:
        points:x,y分布的点集合 一般 Y轴为标量值
        xName:X轴坐标轴名称
        yName:Y轴坐标轴名称

    '''
    table=vtkTable()

    arrX=vtkFloatArray()
    arrX.SetName(xName)
    table.AddColumn(arrX)

    arrY=vtkFloatArray()
    arrY.SetName(yName)
    table.AddColumn(arrY)

    numPoints=len(points)
    table.SetNumberOfRows(numPoints)
    values_x=[t[0] for t in points]
    valuex_y=[t[1] for t in points]

    for i in range(numPoints):
        table.SetValue(i,0,points[i][0])
        table.SetValue(i,1,points[i][1])

    chart=vtkChartXY()
    xAxis = chart.GetAxis(vtkAxis.BOTTOM)
    yAxis = chart.GetAxis(vtkAxis.LEFT)

    
    # textProperty:vtkTextProperty = yAxis.GetTitleProperties()
    # textProperty.SetOrientation(0)
    
    # yAxis.SetMinimum(0)
    # textProperty.SetCellOffset(100)
    xTextProp:vtkTextProperty=xAxis.GetTitleProperties()
    yTextProp:vtkTextProperty=yAxis.GetTitleProperties()
    xAxis.SetTitle(xName)
    xTextProp.SetFontSize(20)
    xTextProp.SetColor(255,0,0)
    xTextProp.SetOpacity(0.5)
    yAxis.SetTitle(yName)
    yTextProp.SetFontSize(20)
    yTextProp.SetColor(0,255,0)
    yTextProp.SetOpacity(0.5)
    min_x=min(values_x)
    max_x=max(values_x)
    min_y=min(valuex_y)
    max_y=max(valuex_y)
    min_x=1.5*min_x if min_x<0 else 0
    max_x=1.5*max_x if max_x>0 else 0
    min_y=1.5*min_y if min_y<0 else 0
    max_y=1.5*max_y if max_y>0 else 0
    if(max_x==min_x):
        max_x+=1

    xAxis.SetRange(min_x,max_x)
    yAxis.SetRange(min_y,max_y)

    xAxis.SetBehavior(1)
    yAxis.SetBehavior(1)
    

    # xAxis.SetNumberOfTicks(20)
    # yAxis.SetNumberOfTicks(20)

# 取消背景网格
    xAxis.SetGridVisible(False)
    yAxis.SetGridVisible(False)

    # xAxis.SetLabelOffset(100)

    line:vtkPlot=chart.AddPlot(vtkChart.LINE)
    line.SetInputData(table, 0, 1)
    line.SetColor(0, 108, 255, 255)
    line.SetWidth(3.0)
    if(displayPoints):
        pots:vtkPlot=chart.AddPlot(vtkChart.POINTS)

        pots.SetInputData(table, 0, 1)
        pots.SetColor(255, 108, 0, 255)
        pots.SetWidth(3.0)
        # pots.SetLabel("")

    
    

    
    # rect=vtkRectf(0,0,1000,300)
    # chart.SetSize(rect)
    # chart.SetGeometry(100,100)


    return chart

    pass
def chart_line_multi(rList:List,xName:str,yName:str,lineTitle:str="",displayPoints=True):
    chart=vtkChartXY()
    xAxis = chart.GetAxis(vtkAxis.BOTTOM)
    yAxis = chart.GetAxis(vtkAxis.LEFT)
    xAxis.SetGridVisible(False)
    yAxis.SetGridVisible(False)
    xAxis.SetRange(0,10)
    yAxis.SetRange(-100,500)
   
    # chart.GetLegend().SetVisible(True)
   

    # xRange = [0.0, 0.0]  # 创建一个列表来存储范围
    # yRange=[0.0,0.0]

    # xAxis.GetRange(xRange)
    # yAxis.GetRange(yRange)
    
 

    # # 计算新的X轴范围，使其扩展到当前范围的1.5倍
    # midpoint_x = (xRange[0] + xRange[1]) / 2
    # new_range_x = [midpoint_x - (midpoint_x - xRange[0]) * 1.5,
    #             midpoint_x + (xRange[1] - midpoint_x) * 1.5]

    # midpoint_y = (yRange[0] + yRange[1]) / 2
    # new_range_y = [midpoint_y - (midpoint_y - yRange[0]) * 1.5,
    #             midpoint_y + (yRange[1] - midpoint_y) * 1.5]
    # xAxis.SetRange(new_range_x[0], new_range_x[1])
    # yAxis.SetRange(new_range_y[0], new_range_y[1])
    # # xAxis.SetBehavior(1)
    # # yAxis.SetBehavior(1)

    xTextProp:vtkTextProperty=xAxis.GetTitleProperties()
    yTextProp:vtkTextProperty=yAxis.GetTitleProperties()
    xAxis.SetTitle(xName+"/(m)")
    xTextProp.SetFontSize(20)
    xTextProp.SetColor(255,0,0)
    xTextProp.SetOpacity(0.5)
    yAxis.SetTitle(yName)
    yTextProp.SetFontSize(20)
    yTextProp.SetColor(0,255,0)
    yTextProp.SetOpacity(0.5)
    # chart.SetShowLegend(True)

    index=0
    for vx,points in rList:
        table=vtkTable()
        arrX=vtkFloatArray()
        arrX.SetName(xName)
        table.AddColumn(arrX)

        arrY=vtkFloatArray()
        arrY.SetName(yName)
        table.AddColumn(arrY)
        numPoints=len(points)
        table.SetNumberOfRows(numPoints)
        # values_x=[t[0] for t in points]
        # valuex_y=[t[1] for t in points]

        for i in range(numPoints):
            table.SetValue(i,0,points[i][0])
            table.SetValue(i,1,points[i][1])
        line:vtkPlot=chart.AddPlot(vtkChart.LINE)
        line.SetInputData(table, 0, 1)
        line.SetWidth(3.0)
        line.SetLabel(lineTitle+"="+str(vx))
        index+=1

        if(displayPoints):
            pots:vtkPlot=chart.AddPlot(vtkChart.POINTS)
            pots.SetInputData(table, 0, 1)
            pots.SetColor(0, 0, 200, 255)
            pots.SetWidth(3.0)
            pots.SetLabel("")
   
    return chart
def demo_chart():

    table=vtkTable()

    arrX=vtkFloatArray()
    arrX.SetName("X Axis")
    table.AddColumn(arrX)

    arrC=vtkFloatArray()
    arrC.SetName("Cosine")
    table.AddColumn(arrC)

    arrS=vtkFloatArray()
    arrS.SetName("Sine")
    table.AddColumn(arrS)

    #Fill in the table with some example values.
    numPoints = 69
    inc = 7.5 / (numPoints - 1)
    table.SetNumberOfRows(numPoints)
    for i in range(numPoints):

        table.SetValue(i, 0, i * inc)
        table.SetValue(i, 1, cos(i * inc))
        table.SetValue(i, 2, sin(i * inc))
    
    chart=vtkChartXY()
    xAxis = chart.GetAxis(vtkAxis.BOTTOM)
    yAxis = chart.GetAxis(vtkAxis.LEFT)

# 取消背景网格
    # xAxis.SetGridVisible(False)
    # yAxis.SetGridVisible(False)
    textProperty = xAxis.GetTitleTextProperty()


    line:vtkPlot=chart.AddPlot(vtkChart.LINE)
    line.SetInputData(table, 0, 1)
    line.SetColor(0, 255, 0, 255)
    line.SetWidth(2.0)
    chart.SetAxisZoom(0)
    return chart

def coneActor():
    cone = vtkConeSource()
    cone.SetResolution(8)

    coneMapper = vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)
    pass
def sphereActor(center:Tuple[float,float,float],radius:float=0.05,color=(1,0,0)):
    sphere =vtkSphereSource()
    sphere.SetCenter(center[0],center[1],center[2])
    sphere.SetRadius(0.1)
    mappper=vtkPolyDataMapper()
    mappper.SetInputConnection(sphere.GetOutputPort())
    actor=vtkActor()
    actor.SetMapper(mappper)
    actor.GetProperty().SetColor(color[0],color[1],color[2])
    return actor

def points_sphere(pointList:List[Tuple[float,float,float,float]],minV=None,maxV=None,radius=0.1):
    if(pointList==None):
        return None
    index = 3
    tuple_values = [t[index] for t in pointList]  # 获取每个元组在指定索引位置的值
    min_value = min(tuple_values)
    max_value = max(tuple_values)
    if(minV is None):
        minV=min_value
    if(maxV is None):
        maxV=max_value
    pointActor = vtkActor()  
    pointsMapper=vtkPolyDataMapper()
    polyData=vtkPolyData()

    lut = vtkLookupTable()
    points = vtkPoints()
    points.SetDataType(VTK_DOUBLE)
    scalarArr = vtkDoubleArray()
    lut.SetHueRange(0.667, 0)
    scalarArr.SetNumberOfValues(len(pointList))
    for i in range(len(pointList)):
        p=pointList[i]
        points.InsertPoint(i,[p[0],p[1],p[2]])
        scalarArr.SetValue(i,p[3])
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(scalarArr)

    sphereSource = vtkSphereSource()
    sphereSource.SetRadius(radius)

    # 创建vtkGlyph3D过滤器，并将vtkSphereSource应用于所有点
    glyph3D = vtkGlyph3D()
    glyph3D.SetInputData(polyData)
    glyph3D.SetSourceConnection(sphereSource.GetOutputPort())
    glyph3D.SetScaleModeToDataScalingOff()
    # glyph3D.SetScaleFactor(0.2)
    glyph3D.Update()

    pointsMapper.SetInputConnection(glyph3D.GetOutputPort())
    pointsMapper.SetScalarRange(minV, maxV)
    pointsMapper.SetLookupTable(lut)
    pointsMapper.Update()
    pointActor.SetMapper(pointsMapper)
    # pointActor.GetProperty().SetColor(1,0,0)
    # pointActor.GetProperty().SetPointSize(5)
    return pointActor,points

def points_vertex(pointList:List[Tuple[float,float,float,float]],minV=None,maxV=None):
    '''显示数据点
    '''
    # pointList=[(0,1,1,5),(0,2,1,10),(1,1,2,15),(1,2,2,20)]
    if(pointList==None):
        return None
    index = 3
    tuple_values = [t[index] for t in pointList]  # 获取每个元组在指定索引位置的值
    min_value = min(tuple_values)
    max_value = max(tuple_values)
    if(minV is None):
        minV=min_value
    if(maxV is None):
        maxV=max_value
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
    
    glyphFilter = vtkVertexGlyphFilter()
    glyphFilter.SetInputData(polyData)
    glyphFilter.Update()

    pointsData=glyphFilter.GetOutput()
    pointsData.GetPointData().SetScalars(scalarArr)

    
    pointsMapper.SetInterpolateScalarsBeforeMapping(1)
    pointsMapper.SetInputData(pointsData)
    pointsMapper.SetScalarRange(minV, maxV)
    pointsMapper.SetLookupTable(lut)
    pointsMapper.Update()
    pointActor.SetMapper(pointsMapper)
    # pointActor.GetProperty().SetColor(1,0,0)
    pointActor.GetProperty().SetPointSize(10)
    
    return pointActor,points
    pass
def distance_line(p1:Tuple[float,float,float],p2:Tuple[float,float,float]):

    line=vtkLineSource()
    line.SetPoint1(p1[0],p1[1],p1[2])
    line.SetPoint2(p2[0],p2[1],p2[2])
    mapperLine=vtkPolyDataMapper()
    mapperLine.SetInputConnection(line.GetOutputPort())
    actorLine=vtkActor()
    actorLine.SetMapper(mapperLine)
    actorLine.GetProperty().SetLineWidth(5)
    actorLine.GetProperty().SetColor(0,1,0)
    point1=sphereActor(p1,color=(0,1,0))
    point2=sphereActor(p2,color=(0,1,0))


    return (actorLine,point1,point2)

    pass
def export_img(renderWindow:vtkRenderWindow,fileName:str):
    '''当前窗体导出为图片
    '''
    try:
        windowToImageFilter = vtkWindowToImageFilter()
        windowToImageFilter.SetInput(renderWindow)
        windowToImageFilter.Update()

        # 将图像写入文件
        writer = vtkPNGWriter()
        writer.SetFileName(fileName)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()
        return(1,"导出图片成功.")
    except Exception as e:
        return(-1,"导出图片失败: "+str(e))
    pass
def export_points(pointList:List[Tuple[float,float,float,float]],fileName:str,headers="x y z value"):
    '''导出数据点
    '''
    try:
        fwriter = open(fileName, 'w')
        if(headers!=None):
            fwriter.write(headers+"\n")
        for p in pointList:
            x=format(p[0],".6f")
            y=format(p[1],".6f")
            z=format(p[2],".6f")
            v=format(p[3],".6f")
            s=str(x)+" "+str(y)+" "+str(z)+" "+str(v)
            fwriter.write(s+"\n")
        fwriter.close()
        return(1,"导出数据成功.")
    except Exception as e:
        return(-1,"导出数据失败:"+str(e))

    pass
def export_data(fileName:str,valueList,headers):
    '''导出数据点
    '''
    try:
        splitText="\t"
        fwriter = open(fileName, 'w')
        if(headers!=None):
            strHeader=splitText.join(map(str,headers))
            fwriter.write(strHeader+"\n")
        for p in valueList:
            # s=splitText.join(map(lambda x: f"{x:.6f}",p))
            s=splitText.join(map(str,p))
            fwriter.write(s+"\n")
        fwriter.close()
        return(1,"导出数据成功.")
    except Exception as e:
        return(-1,"导出数据失败:"+str(e))

    pass
def scalar_actor(min:float,max:float,title:str=None,numberOfColors:int=256,dotPrecision:int=2):
    actor = vtkScalarBarActor()
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(min,max)
    lut.Build()

    actor.SetLookupTable(lut)
    
    txtPropTitle = vtkTextProperty()
    txtPropTitle.SetColor(255, 255, 0)
    txtPropTitle.SetFontSize(18)
    # txtPropTitle.BoldOff()
    # txtPropTitle.ItalicOff()
    # txtPropTitle.SetFontFamily(0)
    # txtPropTitle.SetVerticalJustificationToTop()
    # txtPropTitle.SetOrientation(-90.0)
    

    txtPropLabel = vtkTextProperty()
    txtPropLabel.SetColor(255, 255, 0)
    txtPropLabel.SetFontSize(18)
    # txtPropLabel.BoldOff()
    # txtPropLabel.ItalicOff()
    # txtPropLabel.SetFontFamily(0)
    # txtPropLabel.SetVerticalJustificationToCentered()

    actor.SetNumberOfLabels(10)
    lableFormat=f"%.{dotPrecision}e"
    actor.SetLabelFormat(lableFormat)
    actor.SetVerticalTitleSeparation(20)
    actor.SetTitleTextProperty(txtPropTitle)
    actor.SetLabelTextProperty(txtPropLabel)
    actor.UnconstrainedFontSizeOn()
 
    if(title is not None):
        actor.SetTitle(title)
    actor.SetWidth(0.05)
    actor.SetHeight(0.9)
    actor.SetPosition(0.9, 0.05)
    
    return actor
    pass
def scalar_range_map(mapActor:vtkActor,minV:float,maxV:float,numberOfColors:int=256):
    '''设置数据范围
    '''
    mapper = mapActor.GetMapper()
    lut:vtkLookupTable = mapper.GetLookupTable()
    lut.SetTableRange(minV,maxV)
    lut.SetNumberOfColors(numberOfColors)
    mapper.SetScalarRange(minV,maxV)
    pass
def scalar_range_bar(actor:vtkScalarBarActor,minV:float,maxV:float):
    '''设置数据范围
    '''
    lut:vtkLookupTable = actor.GetLookupTable()
    lut.SetRange(minV,maxV)
def render_vtk_file(fileName:str):
    '''渲染vtk文件
    '''
    # 创建VTK文件读取器
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(fileName)
    reader.Update()

    unstructuredGrid = reader.GetOutput()

    # 2. 提取四面体单元的所有边
    # 获取点数据
    points = unstructuredGrid.GetPoints()

    # 创建用于存储线元的CellArray
    lines = vtkCellArray()

    # 创建一个集合，用于存储已添加的边，避免重复
    edgeSet = set()

    # 遍历所有单元
    for i in range(unstructuredGrid.GetNumberOfCells()):
        cell = unstructuredGrid.GetCell(i)
        if cell.GetCellType() == VTK_TETRA:
            # 获取四面体的4个顶点索引
            ids = [cell.GetPointId(j) for j in range(4)]
            
            # 定义四面体的6条边（由4个顶点两两组合）
            edges = [
                (ids[0], ids[1]),
                (ids[0], ids[2]),
                (ids[0], ids[3]),
                (ids[1], ids[2]),
                (ids[1], ids[3]),
                (ids[2], ids[3]),
            ]
            
            for edge in edges:
                # 为了避免重复，使用排序后的元组作为键
                sorted_edge = tuple(sorted(edge))
                if sorted_edge not in edgeSet:
                    edgeSet.add(sorted_edge)
                    
                    # 创建一条线元
                    line = vtkLine()
                    line.GetPointIds().SetId(0, edge[0])
                    line.GetPointIds().SetId(1, edge[1])
                    
                    # 将线元添加到CellArray中
                    lines.InsertNextCell(line)

    # 3. 创建线元数据集
    linePolyData = vtkPolyData()
    linePolyData.SetPoints(points)
    linePolyData.SetLines(lines)

    # 创建映射器和演员
    mapper = vtkDataSetMapper()
    mapper.SetInputData(linePolyData)

    actor = vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetRepresentationToWireframe()
    # actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetColor(0, 0, 0.6)
    # actor.GetProperty().SetOpacity(0.5)          # 设置透明度
    # actor.GetProperty().EdgeVisibilityOn()       # 显示边框
    return actor
def thermal_3d(points_list:list,tetrahedra:list,temperature_values:list):
    # 创建 vtkPoints 对象并插入顶点
    points = vtkPoints()
    for coord in points_list:
        points.InsertNextPoint(coord)

    # 创建 vtkUnstructuredGrid 对象并设置点
    ugrid = vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    # 创建四面体单元格并添加到 unstructured grid
    tetras = vtkCellArray()
    for tetra in tetrahedra:
        #tetra的每个索引减1
        tetra_cell = vtkTetra()
        for i in range(4):
            tetra_cell.GetPointIds().SetId(i, tetra[i])
        # tetras.InsertNextCell(tetra_cell)
        ugrid.InsertNextCell(tetra_cell.GetCellType(), tetra_cell.GetPointIds())
    # ugrid.SetCells(VTK_TETRA, tetras)

    # 创建 vtkFloatArray 来存储温度数据
    temperature = vtkFloatArray()
    temperature.SetName("Temperature(K)")
    for temp in temperature_values:
        temperature.InsertNextValue(temp)

    # 将温度数据添加到点数据中
    ugrid.GetPointData().SetScalars(temperature)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)

    # 创建映射器并设置标量范围
    mapper = vtkDataSetMapper()
    mapper.SetInputData(ugrid)
    mapper.SetScalarRange(temperature.GetRange())
    mapper.SetLookupTable(lut)

    # 创建演员
    actor = vtkActor()
    actor.SetMapper(mapper)
    #设置透明度
    # actor.GetProperty().SetOpacity(opacity)
    # actor.GetProperty().SetRepresentationToWireframe()
    return actor
def displacement_3d(points_list:list,tetrahedra:list,displacement_list:list):
    # 创建 vtkPoints 对象并插入顶点
    points = vtkPoints()
    for coord in points_list:
        points.InsertNextPoint(coord)

    # 创建 vtkUnstructuredGrid 对象并设置点
    ugrid = vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    # 创建四面体单元格并添加到 unstructured grid
    tetras = vtkCellArray()
    for tetra in tetrahedra:
        #tetra的每个索引减1
        tetra_cell = vtkTetra()
        for i in range(4):
            tetra_cell.GetPointIds().SetId(i, tetra[i])
        # tetras.InsertNextCell(tetra_cell)
        ugrid.InsertNextCell(tetra_cell.GetCellType(), tetra_cell.GetPointIds())
    # ugrid.SetCells(VTK_TETRA, tetras)

    # 创建位移向量（假设已从数据中读取）
    displacements = vtkDoubleArray()
    displacements.SetNumberOfComponents(3)
    displacements.SetName("Displacement")
    for disp in displacement_list:
        displacements.InsertNextTuple3(disp[0], disp[1], disp[2])

    # 将位移向量添加到点数据中
    ugrid.GetPointData().AddArray(displacements)

    # 创建 vtkFloatArray 来存储温度数据
    magList = vtkFloatArray()
    magList.SetName("Magtitude")
    for mag in displacement_list:
        magList.InsertNextValue(mag[3])

    # 将温度数据添加到点数据中
    ugrid.GetPointData().AddArray(magList)
    ugrid.GetPointData().SetScalars(magList)

    # 将位移叠加到原始几何模型上
    new_points = vtkPoints()

    for i in range(ugrid.GetNumberOfPoints()):
        original_point = points.GetPoint(i)
        disp = displacements.GetTuple3(i)
        new_point = [original_point[0] + disp[0],
                    original_point[1] + disp[1],
                    original_point[2] + disp[2]]
        new_points.InsertNextPoint(new_point)
    ugrid.SetPoints(new_points)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfColors(12)

    # 创建映射器并设置标量范围
    mapper = vtkDataSetMapper()
    mapper.SetInputData(ugrid)
    mapper.SetScalarRange(magList.GetRange())
    mapper.SetLookupTable(lut)

    # 创建演员
    actor = vtkActor()
    actor.SetMapper(mapper)
    #设置透明度
    # actor.GetProperty().SetOpacity(opacity)
    # actor.GetProperty().SetRepresentationToWireframe()
    return actor
def em_3d(points_list:list,tetrahedra:list,e_values:list):
    # 创建 vtkPoints 对象并插入顶点
    points = vtkPoints()
    for coord in points_list:
        points.InsertNextPoint(coord)

    # 创建 vtkUnstructuredGrid 对象并设置点
    ugrid = vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    # 创建四面体单元格并添加到 unstructured grid
    tetras = vtkCellArray()
    for tetra in tetrahedra:
        #tetra的每个索引减1
        tetra_cell = vtkTetra()
        for i in range(4):
            tetra_cell.GetPointIds().SetId(i, tetra[i])
        # tetras.InsertNextCell(tetra_cell)
        ugrid.InsertNextCell(tetra_cell.GetCellType(), tetra_cell.GetPointIds())
    # ugrid.SetCells(VTK_TETRA, tetras)

    # 创建 vtkFloatArray 来存储温度数据
    eList = vtkDoubleArray()
    # temperature.SetName("Temperature(K)")
    vIndex=0
    for temp in e_values:
        eList.InsertNextValue(temp)
        # v=vIndex%100
        # eList.InsertNextValue(v)
        # vIndex+=1

    # 将温度数据添加到点数据中
    ugrid.GetPointData().SetScalars(eList)
     
    r=eList.GetRange()
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetRange(eList.GetRange())  
    

    # 创建映射器并设置标量范围
    mapper = vtkDataSetMapper()
    mapper.SetInputData(ugrid)
    mapper.SetScalarRange(eList.GetRange())
    mapper.SetLookupTable(lut)

    # 创建演员
    actor = vtkActor()
    actor.SetMapper(mapper)
    #设置透明度
    # actor.GetProperty().SetOpacity(opacity)
    # actor.GetProperty().SetRepresentationToWireframe()
    return actor

def ffr_3dpolar(pointList,isdb=True,numberOfColors=256):
    '''
    3D极坐标图 三维数据点(theta,phi,value)
    '''

    thetaNum=len(list(set(t[0] for t in pointList)))
    phiNum=len(list(set(t[1] for t in pointList)))
    #使用numpy数组，将极坐标转换为笛卡尔坐标
    data = np.array(pointList)
    theta_deg = data[:,0]
    phi_deg   = data[:,1]
    R_db= data[:,2] #R为db值
    R_linear         = data[:,3]

    minV_db=np.min(R_db)
    maxV_db=np.max(R_db)

    minV_linear=np.min(R_linear)
    maxV_linear=np.max(R_linear)

    # R_db=20*np.log10(R_db) #将线性值转化为db值
    #对R由db值转换为非db值
    # if(not isdb):
    #     R_linear = 10 ** (R_db / 10)
       
    #     # R_linear = np.sqrt(R_linear) #开方处理
    # else:
    #     R_linear=R_db
    # R_linear = 10 ** (R_db / 10)
    R_Values=R_db
    minV=np.min(R_Values)
    maxV=np.max(R_Values)
    offset=0-minV #偏移量，将db值全部转换为正值
    if(isdb):
        R_Values+=offset #将db值全部转换为正值
        minV+=offset
        maxV+=offset

    
    # 转换为弧度
    theta = np.radians(theta_deg)
    phi = np.radians(phi_deg)
    scalar_factor=5
    # 球坐标到笛卡尔坐标转换

    X = R_Values * np.sin(theta) * np.cos(phi)
    Y = R_Values * np.sin(theta) * np.sin(phi)
    Z = R_Values * np.cos(theta)


    points = vtkPoints()
    scalarArr = vtkDoubleArray()
    pLen=len(pointList)
    scalarArr.SetNumberOfValues(pLen)
    for i in range(pLen):
        
        points.InsertPoint(i,[X[i],Y[i],Z[i]])
        scalarArr.SetValue(i,R_Values[i])

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetNumberOfTableValues(numberOfColors)
    lut.SetTableRange(minV,maxV)
    lut.Build()

    grid = vtkStructuredGrid()
    grid.SetDimensions(phiNum, thetaNum, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)


    surface = vtkDataSetSurfaceFilter()
    surface.SetInputData(grid)
    surface.Update()

    mapper = vtkDataSetMapper()
    mapper.SetInputData(surface.GetOutput()) # 直接用原网格
    mapper.SetScalarRange(minV,maxV)
    mapper.SetLookupTable(lut)

    actor=vtkActor()
    actor.SetMapper(mapper)

    #将数据点返回
    # R_linear-=offset#将db值还原
    # R_linear=10 ** (R_linear / 20) #将db值还原为线性值
    
    # minV-=offset
    # maxV-=offset

    
    pointList_n= list(zip(X, Y, Z, R_linear, R_db))

    return actor,pointList_n,minV_db,maxV_db,minV_linear,maxV_linear
    pass


