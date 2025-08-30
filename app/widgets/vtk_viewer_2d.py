from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QAction
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal,QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from ..mixins import ComponentMixin
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonDataModel import vtkPolyData

from vtkmodules.all import(
    vtkRenderer,
    vtkActor,
    vtkAxesActor,
    vtkOrientationMarkerWidget,
    vtkInteractorStyleTrackballCamera,
    vtkActorCollection,
    vtkChartXY,
    vtkContextView,
    vtkContextScene,
    vtkRenderWindowInteractor,
    vtkGenericRenderWindowInteractor,
    vtkWin32RenderWindowInteractor,
    vtkAxis,
    vtkChartLegend,
    


)

class vtkViewer2d(QVTKRenderWindowInteractor):
    
    name = 'viewer2d'

    def  __init__(self,parent=None):
        self.parent=parent
        self._view=vtkContextView()
        self._scene:vtkContextScene=self._view.GetScene()
        
        super(vtkViewer2d,self).__init__(parent,iren=self._view.GetInteractor(),rw=self._view.GetRenderWindow())

        # self.SetInteractorStyle(vtkInteractorStyleTrackballCamera())

        self.ren:vtkRenderer = self._view.GetRenderer()

        self._Timer.setInterval(100)
        # show the widget
        self.Initialize()
        # self.Start()
        self.show()
        self.onLoad()
        
    
    def onLoad(self):
        self.ren.SetBackground(0.86, 0.86, 0.86)
        self.ren.ResetCamera()
        pass
    # def refresh(self):
    #     self._Iren.Render()
    #     pass

    # def wheelEvent(self, ev):
    #     super(vtkViewer2d,self).wheelEvent(ev)
    #     self._Iren.Render()
    def display_chart(self,chart:vtkChartXY):
        self.clear()
        self._scene.AddItem(chart)
    
        chart.SetShowLegend(True)
        legend:vtkChartLegend = chart.GetLegend()
        legend.SetHorizontalAlignment(vtkChartLegend.RIGHT)
        legend.SetVerticalAlignment(vtkChartLegend.TOP)
        
        self._Iren.Render()

        self._Timer.start()
        
        # self._scene.
        # self._scene.SetScaleTiles(1)
    def clear(self):
        for i in range(self._scene.GetNumberOfItems()):
            self._scene.RemoveItem(i)
        self._Timer.stop()

    def closeEvent(self, evt):
        super().closeEvent(evt)
        self._Timer.stop()
        
    def stopRefresh(self):
        self._Timer.stop()
    def TimerEvent(self):
        self._Iren.Render()
        pass
    def Zoom(self, factor,chart:vtkChartXY):
        # 获取X轴和Y轴
        xAxis = chart.GetAxis(vtkAxis.BOTTOM)
        yAxis = chart.GetAxis(vtkAxis.LEFT)

        # 获取当前范围
        xRange = [0.0, 0.0]
        yRange = [0.0, 0.0]
        xAxis.GetRange(xRange)
        yAxis.GetRange(yRange)

        # 计算新的范围
        xMidpoint = (xRange[0] + xRange[1]) / 2
        yMidpoint = (yRange[0] + yRange[1]) / 2
        xRange[0] = xMidpoint + (xRange[0] - xMidpoint) * factor
        xRange[1] = xMidpoint + (xRange[1] - xMidpoint) * factor
        yRange[0] = yMidpoint + (yRange[0] - yMidpoint) * factor
        yRange[1] = yMidpoint + (yRange[1] - yMidpoint) * factor

        # 设置新的范围
        xAxis.SetRange(xRange[0], xRange[1])
        yAxis.SetRange(yRange[0], yRange[1])

        # 重新渲染
        chart.GetScene().SetDirty(True)
        # self._Iren.Render()
        # self._Timer.start()

    def resizeEvent(self, ev):
        pass
        # scale = self._getPixelRatio()
        # w = int(round(scale*self.width()))
        # h = int(round(scale*self.height()))
        # self._RenderWindow.SetDPI(int(round(72*scale)))
        # vtkRenderWindow.SetSize(self._RenderWindow, w, h)
        # self._Iren.SetSize(w, h)
        # self._Iren.ConfigureEvent()
        # self.update()
         


