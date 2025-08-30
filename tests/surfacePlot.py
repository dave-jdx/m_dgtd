#!/usr/bin/env python

from math import sin, sqrt
from numpy import sin,cos,pi, exp,log
import numpy as np

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingContextOpenGL2
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkChartsCore import (
    vtkChartXYZ,
    vtkPlotSurface
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkCommonDataModel import (
    vtkRectf,
    vtkTable,
    vtkVector2i
)
from vtkmodules.vtkRenderingContext2D import vtkContextMouseEvent
from vtkmodules.vtkViewsContext2D import vtkContextView
from vtkmodules.all import(
    vtkStructuredGrid,
    vtkPoints,
    vtkDoubleArray,
    vtkStructuredGridGeometryFilter,
    vtkChart,
    vtkVariantArray
)


def main():

    filepath = 'D:\\project\\cae\\emx\\src\\data\\data.txt'

    table = vtkTable()

    theta_array = vtkDoubleArray()
    phi_array = vtkDoubleArray()
    gain_array = vtkDoubleArray()

    theta_array.SetName("Theta")
    phi_array.SetName("Phi")
    gain_array.SetName("Gain")

    table.AddColumn(theta_array)
    table.AddColumn(phi_array)
    table.AddColumn(gain_array)

    vals_theta = []
    vals_phi = []
    vals_r = []
    with open(filepath) as f:
        for s in f.readlines()[2:]:
            # print(s.strip().split())
            vals_theta.append(float(s.strip().split()[0]))
            vals_phi.append(float(s.strip().split()[1]))
            vals_r.append(float(s.strip().split()[6]))

            t=float(s.strip().split()[0])
            p=float(s.strip().split()[1])
            r=float(s.strip().split()[6])

            arr=vtkVariantArray()
            arr.InsertNextValue(t)
            arr.InsertNextValue(p)
            arr.InsertNextValue(r)
            

            table.InsertNextRow(arr)


    # theta1d = vals_theta
    # theta = np.array(theta1d)/180*pi;

    # phi1d = vals_phi
    # phi = np.array(phi1d)/180*pi;

    # power1d = vals_r
    # power = np.array(power1d);
    # # power = power-min(power)
    # power = 10**(power/10) # I used linscale

    # X = power*sin(phi)*sin(theta)
    # Y = power*cos(phi)*sin(theta)
    # Z = power*cos(theta)

    # X = X.reshape([91,91])
    # Y = Y.reshape([91,91])
    # Z = Z.reshape([91,91])

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
    
    # points = vtkPoints()
    # scalarArr = vtkDoubleArray()
    # pLen=len(pointList)
    # scalarArr.SetNumberOfValues(pLen)
    # for i in range(pLen):
    #     p=pointList[i]
    #     points.InsertPoint(i,[p[0],p[1],p[2]])
    #     scalarArr.SetValue(i,p[3])
    
    colors = vtkNamedColors()

    chart = vtkChartXYZ()
    chart.SetGeometry(vtkRectf(10.0, 10.0, 630, 470))

    plot = vtkPlotSurface()

    view = vtkContextView()
    view.GetRenderer().SetBackground(colors.GetColor3d("Silver"))
    view.GetRenderWindow().SetSize(640, 480)
    view.GetScene().AddItem(chart)


    # Create a surface
    # table = vtkTable()
    # numPoints = 91
    # inc = 2
    # for i in range(numPoints):
    #     arr = vtkFloatArray()
    #     table.AddColumn(arr)

    # table.SetNumberOfRows(numPoints)
   
    # for i in range(numPoints):
    #     for j in range(numPoints):
    #         table.SetValue(i, j,Z[i,j] )

    # Set up the surface plot we wish to visualize and add it to the chart
    # plot.SetXRange(0, 10.0)
    # plot.SetYRange(0, 10.0)
    plot.SetInputData(table)
    plot.GetPen().SetColorF(colors.GetColor3d("Tomato"))
    chart.AddPlot(plot)

    view.GetRenderWindow().SetMultiSamples(0)
    view.GetInteractor().Initialize()
    view.GetRenderWindow().SetWindowName("SurfacePlot")
    view.GetRenderWindow().Render()

    # Rotate
    mouseEvent = vtkContextMouseEvent()
    mouseEvent.SetInteractor(view.GetInteractor())

    pos = vtkVector2i()

    lastPos = vtkVector2i()
    mouseEvent.SetButton(vtkContextMouseEvent.LEFT_BUTTON)
    lastPos.Set(100, 50)
    mouseEvent.SetLastScreenPos(lastPos)
    pos.Set(150, 100)
    mouseEvent.SetScreenPos(pos)

    sP = [float(x) for x in pos]
    lSP = [float(x) for x in lastPos]
    screenPos = [float(x) for x in mouseEvent.GetScreenPos()]
    lastScreenPos = [float(x) for x in mouseEvent.GetLastScreenPos()]

    chart.MouseMoveEvent(mouseEvent)

    view.GetInteractor().Start()


if __name__ == '__main__':
    main()
