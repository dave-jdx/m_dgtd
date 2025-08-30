import vtk
import numpy as np
from vtkmodules.all import(
    vtkActor,
    vtkPolyData,
    vtkPolyDataMapper,
    vtkPoints,
    vtkCellArray,
    vtkDelaunay3D,
    vtkWarpScalar,
    vtkPolarAxesActor
)

def rpActor():
    # create a dataset with points on a sphere
    theta, phi = np.mgrid[0:np.pi:90j, 0:2*np.pi:90j]
    r = np.abs(np.sin(theta)*np.cos(phi)) * np.exp(-0.8*(theta-np.pi/2)**2/np.pi**2)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    points = vtkPoints()
    for i in range(theta.shape[0]):
        for j in range(theta.shape[1]):
            points.InsertNextPoint(x[i,j], y[i,j], z[i,j])

    polys = vtkCellArray()
    for i in range(theta.shape[0]-1):
        for j in range(theta.shape[1]-1):
            id1 = i*theta.shape[1] + j
            id2 = (i+1)*theta.shape[1] + j
            id3 = (i+1)*theta.shape[1] + j+1
            id4 = i*theta.shape[1] + j+1
            polys.InsertNextCell(4)
            polys.InsertCellPoint(id1)
            polys.InsertCellPoint(id2)
            polys.InsertCellPoint(id3)
            polys.InsertCellPoint(id4)
    polydata = vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(polys)

    # create a filter to triangulate the points
    tri = vtkDelaunay3D()
    tri.SetInputData(polydata)

    # create a filter to warp the shape of the mesh based on the scalar values
    warp = vtkWarpScalar()
    warp.SetInputData(polydata)
    warp.SetScaleFactor(0.1)

    # create an actor to display the warped mesh
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(warp.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor,actor