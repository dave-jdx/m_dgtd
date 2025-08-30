from vtkmodules.all import(
    vtkInteractorStyleTrackballCamera,
    vtkAxesActor
)
class CustomInterStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self,parent=None):
        super().__init__()
        self.parent = parent
        self._fixedActor=None
    def setFixed(self,vtkAxes):
        self._fixedActor=vtkAxes

    def OnLeftButtonDown(self):
        super().OnLeftButtonDown()
        self.parent.onLeftButtonDown()
    def OnLeftButtonUp(self):
        super().OnLeftButtonUp()
        self.parent.onLeftButtonUp()
    def OnMiddleButtonDown(self):
        super().OnMiddleButtonDown()
        self.parent.onMiddleButtonDown()
    def OnMiddleButtonUp(self):
        super().OnMiddleButtonUp()
        self.parent.onMiddleButtonUp()
    def OnRightButtonDown(self):
        super().OnRightButtonDown()
        self.parent.onRightButtonDown()
    def OnRightButtonUp(self):
        super().OnRightButtonUp()
        self.parent.onRightButtonUp()
    def OnMouseMove(self):
        super().OnMouseMove()
        self.parent.onMouseMove()
    def OnMouseWheelForward(self):
        super().OnMouseWheelForward()
        self.parent.onMouseWheelForward()
    def OnMouseWheelBackward(self):
        super().OnMouseWheelBackward()
        self.parent.onMouseWheelBackward()
    def OnChar(self):
        super().OnChar()
        self.parent.onChar()
    def OnKeyPress(self):
        super().OnKeyPress()
        self.parent.onKeyPress()
    def OnKeyRelease(self):
        super().OnKeyRelease()
        self.parent.onKeyRelease()
    def OnTimer(self):
        super().OnTimer()
        self.parent.onTimer()
    def OnExpose(self):
        super().OnExpose()
        self.parent.onExpose()
    def OnConfigure(self):
        super().OnConfigure()
        self.parent.onConfigure()
    def OnEnter(self):
        super().OnEnter()
        self.parent.onEnter()
    def OnLeave(self):
        super().OnLeave()
        self.parent.onLeave()
    def OnTimer(self):
        super().OnTimer()
        self.parent.onTimer()
    def OnExpose(self):
        super().OnExpose()
        self.parent.onExpose()
    def OnConfigure(self):
        super().OnConfigure()
        self.parent.onConfigure()
    def OnEnter(self):
        super().OnEnter()
        self.parent.onEnter()
    def OnLeave(self):
        super().OnLeave()
        self.parent.onLeave()
    def OnTimer(self):
        super().OnTimer()
        self.parent.onTimer()
    def OnExpose(self):
        super().OnExpose