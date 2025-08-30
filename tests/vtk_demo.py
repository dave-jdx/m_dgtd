from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from vtkmodules.vtkRenderingCore import vtkRenderer

from vtkmodules.all import(
    vtkRenderer,
    vtkActor,
    vtkPolyDataMapper,
    vtkContextView,
    vtkContextScene

)
from vtkmodules.vtkCommonColor import vtkNamedColors

from vtkmodules.qt import QVTKRenderWindowInteractor

import api_reader
import api_vtk
import rp
import vtk_actor

def QVTKRenderWidgetConeExample():
    """A simple example that uses the QVTKRenderWindowInteractor class."""

    # every QT app needs an app
    app = QApplication(['QVTKRenderWindowInteractor'])
    

    # _2dView=vtkContextView()
    # # create the widget
    widget = QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(iren=_2dView.GetInteractor(),rw=_2dView.GetRenderWindow())
    # widget.Initialize()
    # # widget.Start()
    # # if you don't want the 'q' key to exit comment this.
    # widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

    
    # # _2dView.SetRenderWindow(widget.GetRenderWindow())
    # chart=api_vtk.ffr_chart()
    # chart.SetBottomBorder(600)
    # chart.SetLeftBorder(200)
    # chart.SetBorders(100,100,100,200)
    # chart.SetZoomWithMouseWheel(True)
    # _contextScene:vtkContextScene=_2dView.GetScene()
    # _contextScene.AddItem(chart)

    # _2dView.GetRenderWindow().Render()
    # _2dView.GetInteractor().Initialize()
    # # _2dView.GetInteractor().Start()
    # widget.show()
    # # start event processing
    # app.exec_()
    # return

    ren = vtkRenderer()
    ren.SetBackground(0.7,0.7,0.7)

    widget.GetRenderWindow().AddRenderer(ren)
    



    fpath="D:/project/cae/emx/src/data/"
    fname=fpath+"current0213.txt"
    

    
    fList=api_reader.read_currents(fname)
    item=fList[0]
    mapper=api_vtk.currents_surface_mapper(item[0],item[1],item[2],item[3])

    fname=fpath+"ffr.txt"
    fList=api_reader.read_ffr(fname)
    item=fList[0]
    mapper=api_vtk.antenna_radio_pattern(item[0],item[1],item[2],item[3],item[4])

    fname=fpath+"nf.txt"
    fList=api_reader.read_nf(fname)
    item=fList[0]
    actor,_=api_vtk.nf_surface(item[0],item[1],item[2],11,6,5)

    # mapper=rp.read_antenna()
    # mapper=vtk_actor.sphereFace2()

    # actor=vtkActor()
    # actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(5)
    
    # actor,_=vtk_actor.pointVertex()
    ren.AddActor(actor)
    
    # ren.AddActor(_)

    # show the widget
    widget.show()
    # start event processing
    app.exec_()
QVTKRenderWidgetConeExample()