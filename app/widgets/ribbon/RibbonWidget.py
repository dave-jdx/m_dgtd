from PyQt5.QtWidgets import *
from .RibbonTab import RibbonTab
from .import gui_scale
from .StyleSheets import get_stylesheet
from PyQt5.QtGui import QFont

__author__ = 'magnus'


class RibbonWidget(QToolBar):
    def __init__(self, parent):
        QToolBar.__init__(self, parent)
        self.parent=parent
        # self.setStyleSheet(get_stylesheet("ribbon"))
        self.setObjectName("ribbonWidget")
        self.setWindowTitle("Ribbon")
        self._ribbon_widget = QTabWidget(self)
        self._ribbon_widget.setMaximumHeight(150*gui_scale())
        self._ribbon_widget.setMinimumHeight(80*gui_scale())
        self.setMovable(False)
        self.addWidget(self._ribbon_widget)
        # self._font=self.font()
        # self._font.setPointSize(12)
        
        # self.setFont(self._font)
       
        # font=QFont()
        # print(font.family())

    def add_ribbon_tab(self, name):
        ribbon_tab = RibbonTab(self, name)
        ribbon_tab.setObjectName("tab_" + name)
        self._ribbon_widget.addTab(ribbon_tab, name)
        return ribbon_tab
    def activate_tab(self, tabIndex:int):
        self._ribbon_widget.setCurrentIndex(tabIndex)

    # def set_active(self, name):
    #     obj=self.findChild("tab_" + name)
    #     self.setCurrentWidget(obj)