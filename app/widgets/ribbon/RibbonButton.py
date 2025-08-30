from PyQt5 import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

from . import gui_scale
from .StyleSheets import get_stylesheet

__author__ = 'magnus'


class RibbonButton(QToolButton):
    def __init__(self, parent, is_large=False,styleSheet:str=None):
        QPushButton.__init__(self, parent)
        # sc = 1
        sc = gui_scale()

        
        if is_large:
            self.setMaximumWidth(120 * sc)
            self.setMinimumWidth(50 * sc)
            self.setMinimumHeight(70* sc)
            self.setMaximumHeight(100 * sc)
            if(styleSheet!=None):
                self.setStyleSheet(styleSheet)
            self.setToolButtonStyle(3)
            self.setIconSize(QSize(32 * sc, 32 * sc))
        else:
            self.setToolButtonStyle(2)
            self.setMaximumWidth(150 * sc)
            self.setIconSize(QSize(16 * sc, 16 * sc))
            # self.setStyleSheet(get_stylesheet("ribbonSmallButton"))
  
        # self._font=self.font()
        # self._font.setFamily("Arial")
        # self._font.setPointSize(12)
        # self.setFont(self._font)
        # print("button font family",self._font.family())
        
        

    def update_button_status_from_action(self):
        
        self.setText(self._actionOwner.text())
        self.setStatusTip(self._actionOwner.statusTip())
        self.setToolTip(self._actionOwner.toolTip())
        self.setIcon(self._actionOwner.icon())
        self.setEnabled(self._actionOwner.isEnabled())
        self.setCheckable(self._actionOwner.isCheckable())
        self.setChecked(self._actionOwner.isChecked())
        pass
