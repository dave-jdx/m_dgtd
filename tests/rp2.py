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

    vals_theta = []
    vals_phi = []
    vals_r = []
    with open(filepath) as f:
        for s in f.readlines()[2:]:
            # print(s.strip().split())
            vals_theta.append(float(s.strip().split()[0]))
            vals_phi.append(float(s.strip().split()[1]))
            vals_r.append(float(s.strip().split()[6]))


    theta1d = vals_theta
    theta = np.array(theta1d)/180*pi

    phi1d = vals_phi
    phi = np.array(phi1d)/180*pi

    power1d = vals_r
    power = np.array(power1d)
    # power = power-min(power)
    power = 10**(power/10) # I used linscale

    X = power*sin(phi)*sin(theta)
    Y = power*cos(phi)*sin(theta)
    Z = power*cos(theta)

    X = X.reshape([91,91])
    Y = Y.reshape([91,91])
    Z = Z.reshape([91,91])

    def interp_array(N1):  # add interpolated rows and columns to array
        N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
        N2[:, 0] = N1[:, 0]  # original column
        for k in range(N1.shape[1] - 1):  # loop through columns
            N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
            N2[:, 2*k+2] = N1[:, k+1]  # original column
        N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
        N3[0] = N2[0]  # original row
        for k in range(N2.shape[0] - 1):  # loop through rows
            N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
            N3[2*k+2] = N2[k+1]  # original row
        return N3

    interp_factor=1

    for counter in range(interp_factor):  # Interpolate between points to increase number of faces
        X = interp_array(X)
        Y = interp_array(Y)
        Z = interp_array(Z)
    pointList=[]
    for i in range(X.shape[0]):

        for j in range(X.shape[1]):
            pointList.append((X[i,j],Y[i,j],Z[i,j],Z[i,j]))
    min=Z.min()
    max=Z.max()
  
    # filepath = 'D:\\project\\cae\\emx\\src\\data\\data.txt'
    # pointList=[]
    # min=0
    # max=0
    # with open(filepath) as f:
    #     for s in f.readlines()[2:]:
    #         # print(s.strip().split())
    #         arr=s.strip().split()
    #         phi=float(arr[0])
    #         theta=float(arr[1])
    #         r=float(arr[6])
            
    #         power=10**(r/10)
    #         x=power*sin(phi/180*pi)*sin(theta/180*pi)
    #         y=power*cos(phi/180*pi)*sin(theta/180*pi)
    #         z=power*cos(theta/180*pi)
    #         pointList.append((x,y,z,power))
    #         if(power>max):
    #             max=power
    #         if(power<min):
    #             min=power
    
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


    polys = vtkCellArray()

    currentSampleIndex = 0
    xLength = 90 
    yLength = 90 
    for m in range(xLength):
        currentSampleIndex=currentSampleIndex+xLength
        for n in range(yLength):
            id0=currentSampleIndex-xLength+n
            id1=currentSampleIndex-xLength+n+1
            id2=currentSampleIndex+n+1
            polys.InsertNextCell(3)
            polys.InsertCellPoint(id0)
            polys.InsertCellPoint(id1)
            polys.InsertCellPoint(id2)
            


            id02=currentSampleIndex-xLength+n
            id12=currentSampleIndex+n+1
            id22=currentSampleIndex+n
            polys.InsertNextCell(3)
            polys.InsertCellPoint(id02)
            polys.InsertCellPoint(id12)
            polys.InsertCellPoint(id22)

    polyData.SetPoints(points)
    polyData.SetPolys(polys)
    polyData.GetPointData().SetScalars(scalarArr)

    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(polyData)

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(2)
    # filter.Update()

    


    grid = vtkStructuredGrid()
    grid.SetDimensions(181, 181, 1)
    grid.SetPoints(points)

    surface = vtkStructuredGridGeometryFilter()
    surface.SetInputData(grid)
    surface.Update()

    result:vtkPolyData=surface.GetOutput()
    result.GetPointData().SetScalars(scalarArr)

    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(result)

    # filter = vtkButterflySubdivisionFilter()
    # filter.SetInputConnection(triangleFilter.GetOutputPort())
    # filter.SetNumberOfSubdivisions(2)
    # filter.Update()

    filter=vtkLinearSubdivisionFilter()
    filter.SetInputConnection(triangleFilter.GetOutputPort())
    filter.SetNumberOfSubdivisions(3)
    filter.Update()

    
    
    
    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    # lut.SetNumberOfTableValues(12)
    # print(lut.GetNumberOfTableValues())
    # lut.SetNumberOfColors(2)
    lut.SetTableRange(min,max)
    lut.Build()

    result:vtkPolyData=surface.GetOutput()
    result.GetPointData().SetScalars(scalarArr)
    
    mapper=vtkPolyDataMapper()
    mapper.SetInterpolateScalarsBeforeMapping(1)
    mapper.SetInputData(result)
    mapper.SetScalarRange(min,max)
    mapper.SetLookupTable(lut)

    actor = vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(5)
    
    return actor,actor
    
# read_antenna()
    