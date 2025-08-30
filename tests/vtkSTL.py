#!/bin/env python

"""
Simple VTK example in Python to load an STL mesh and display with a manipulator.
Chris Hodapp, 2014-01-28, (c) 2014
"""

import time
import vtk

def render():
    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    # Create a RenderWindowInteractor to permit manipulating the camera
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    start_time = time.time()
    end_time = time.time()
    print("读取耗时: {:.2f}秒".format(end_time - start_time))
    stlFilename = "model/50.stl"
    polydata = loadStl(stlFilename)
    end_time = time.time()
    print("读取耗时: {:.2f}秒".format(end_time - start_time))
    start_time = time.time()
    ren.AddActor(polyDataToActor(polydata))
    
    # reader=loadStlAsync(stlFilename)
    # ren.AddActor(polyDataToActorAsync(reader))
    # end_time = time.time()
    # print("耗时: {:.2f}秒".format(end_time - start_time))
    ren.SetBackground(0.3, 0.3, 0.3)
    
    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    ren.ResetCamera()
    end_time = time.time()
    print("显示耗时: {:.2f}秒".format(end_time - start_time))
    iren.Start()
    

def loadStlAsync(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    return reader
def loadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def polyDataToActorAsync(reader):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    return actor

def polyDataToActor(polydata):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    return actor

render()