from typing import List,Set,Dict,Tuple
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
    vtkRenderWindow
    
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

    # polyData=vtkPolyData()
    # polyData.SetPoints(points)

    # glyphFilter = vtkVertexGlyphFilter()
    # glyphFilter.SetInputData(polyData)
    # glyphFilter.Update()

    # pointsData=glyphFilter.GetOutput()
    # pointsData.GetPointData().SetScalars(scalarArr)

    grid = vtkStructuredGrid()
    
    grid.SetDimensions(thetaNum, phiNum, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalarArr)

    # surface = vtkStructuredGridGeometryFilter()
    # surface.SetInputData(grid)
    # surface.Update()

    surface = vtkDataSetSurfaceFilter()
    surface.SetInputData(grid)
    surface.Update()

    # result:vtkPolyData=surface.GetOutput()
    # result.GetPointData().SetScalars(scalarArr)

    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(surface.GetOutput())

    filter = vtkButterflySubdivisionFilter()
    filter.SetInputConnection(triangleFilter.GetOutputPort())
    filter.SetNumberOfSubdivisions(3)
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

    xAxis.SetTitle(xName)
    yAxis.SetTitle(yName)
    min_x=min(values_x)
    max_x=max(values_x)
    min_y=min(valuex_y)
    max_y=max(valuex_y)
    min_x=round(1.5*min_x) if min_x<0 else 0
    max_x=round(1.5*max_x) if max_x>0 else 0
    min_y=round(1.5*min_y) if min_y<0 else 0
    max_y=round(1.5*max_y) if max_y>0 else 0

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

    
    

    
    # rect=vtkRectf(0,0,1000,300)
    # chart.SetSize(rect)
    # chart.SetGeometry(100,100)


    return chart

    pass
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
    xAxis.SetGridVisible(False)
    yAxis.SetGridVisible(False)
    textProperty = xAxis.GetTitleTextProperty()


    line:vtkPlot=chart.AddPlot(vtkChart.LINE)
    line.SetInputData(table, 0, 1)
    line.SetColor(0, 255, 0, 255)
    line.SetWidth(2.0)
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
    pointActor.GetProperty().SetColor(1,0,0)
    pointActor.GetProperty().SetPointSize(5)
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
def scalar_actor(min:float,max:float,title:str=None,numberOfColors:int=256):
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




