import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as Axes3D
from numpy import sin,cos,pi, exp,log
from tqdm import tqdm
# import mpl_toolkits.mplot3d.axes3d as Axes3D
from matplotlib import cm, colors
from vtkmodules.all import(
    vtkPolyData,
    vtkPoints,
    vtkCellArray,
    vtkLookupTable,
    vtkDoubleArray,
    vtkPolyDataMapper,
    vtkActor,
    vtkStructuredGrid,
    vtkDataSetSurfaceFilter,
    vtkVertexGlyphFilter,
    vtkUnstructuredGrid,
    vtkTriangleFilter,
    vtkButterflySubdivisionFilter,
    vtkStructuredGridGeometryFilter,
    vtkLinearSubdivisionFilter
)

def read_antenna():
  
    filepath = 'D:\\project\\cae\\emx\\src\\data\\data.txt'
    pointList=[]
    min=0
    max=0
    with open(filepath) as f:
        for s in f.readlines()[2:]:
            # print(s.strip().split())
            arr=s.strip().split()
            phi=float(arr[0])
            theta=float(arr[1])
            r=float(arr[6])
            
            power=10**(r/10)
            x=power*sin(phi/180*pi)*sin(theta/180*pi)
            y=power*cos(phi/180*pi)*sin(theta/180*pi)
            z=power*cos(theta/180*pi)
            pointList.append((x,y,z,power))
            if(power>max):
                max=power
            if(power<min):
                min=power
    
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



    glyphFilter = vtkVertexGlyphFilter()
    glyphFilter.SetInputData(polyData)
    glyphFilter.Update()

    pointsData=glyphFilter.GetOutput()
    pointsData.GetPointData().SetScalars(scalarArr)


    # polys = vtkCellArray()

    # currentSampleIndex = 0
    # xLength = 90 
    # yLength = 90 
    # for m in range(xLength):
    #     currentSampleIndex=currentSampleIndex+xLength
    #     for n in range(yLength):
    #         id0=currentSampleIndex-xLength+n
    #         id1=currentSampleIndex-xLength+n+1
    #         id2=currentSampleIndex+n+1
    #         polys.InsertNextCell(3)
    #         polys.InsertCellPoint(id0)
    #         polys.InsertCellPoint(id1)
    #         polys.InsertCellPoint(id2)
            


    #         id02=currentSampleIndex-xLength+n
    #         id12=currentSampleIndex+n+1
    #         id22=currentSampleIndex+n
    #         polys.InsertNextCell(3)
    #         polys.InsertCellPoint(id02)
    #         polys.InsertCellPoint(id12)
    #         polys.InsertCellPoint(id22)

    # polyData.SetPoints(points)
    # polyData.SetPolys(polys)
    # polyData.GetPointData().SetScalars(scalarArr)

    # triangleFilter = vtkTriangleFilter()
    # triangleFilter.SetInputData(polyData)

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(2)
    # filter.Update()

    


    grid = vtkStructuredGrid()
    grid.SetDimensions(91, 91, 1)
    grid.SetPoints(points)

    surface = vtkStructuredGridGeometryFilter()
    surface.SetInputData(grid)
    surface.Update()

    result:vtkPolyData=surface.GetOutput()
    result.GetPointData().SetScalars(scalarArr)

    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(result)

    filter = vtkButterflySubdivisionFilter()
    filter.SetInputConnection(triangleFilter.GetOutputPort())
    filter.SetNumberOfSubdivisions(3)
    filter.Update()

    # filter=vtkLinearSubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(3)
    # filter.Update()

    
    
    
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(12)
    # print(lut.GetNumberOfTableValues())
    # lut.SetNumberOfColors(2)
    lut.SetTableRange(min,max)
    lut.Build()

    result:vtkPolyData=filter.GetOutput()
    # result.GetPointData().SetScalars(scalarArr)
    
    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)

    return mapper

    actor = vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(5)
    
    return actor,actor
    
# read_antenna()
    