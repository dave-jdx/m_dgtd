from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout
from . import gui_scale
from .StyleSheets import get_stylesheet
from PyQt5.QtGui import QFont


__author__ = 'mamj'


class RibbonPane(QWidget):
    def __init__(self, parent, name):
        QWidget.__init__(self, parent)
        # self.setStyleSheet(get_stylesheet("ribbonPane"))

        self._font=self.font()
        self._font.setPixelSize(16)
        self._font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])

        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(0)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(horizontal_layout)
        vertical_widget = QWidget(self)
        horizontal_layout.addWidget(vertical_widget)
        horizontal_layout.addWidget(RibbonSeparator(self))
        vertical_layout = QVBoxLayout()
        vertical_layout.setSpacing(0)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_widget.setLayout(vertical_layout)
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        # label.setStyleSheet("color:#666; margin: 0px 20px 0px 0px; padding: 0px 0px 0px 0px;")
        label.setFont(self._font)
        
        content_widget = QWidget(self)
        vertical_layout.addWidget(content_widget)
        vertical_layout.addWidget(label)
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignLeft)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout = content_layout
        content_widget.setLayout(content_layout)

        
        

    def add_ribbon_widget(self, widget):
        self.contentLayout.addWidget(widget, 0, Qt.AlignTop)

    def add_grid_widget(self, width):
        widget = QWidget()
        # font=widget.font()
        # font.setPixelSize(14)
        # font.setFamilies(["Arial", "Segoe UI", "Tahoma", "Microsoft YaHei", "sans-serif"])
        # widget.setFont(font)
        widget.setMaximumWidth(width)
        widget.setMinimumHeight(gui_scale() * 80)
    
        grid_layout = QGridLayout()
        widget.setLayout(grid_layout)
        grid_layout.setSpacing(4)
        # grid_layout.setVerticalSpacing(20)
        grid_layout.setContentsMargins(2, 2, 2, 2)
        self.contentLayout.addWidget(widget)
        # grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid_layout.setAlignment(Qt.AlignCenter|Qt.AlignLeft)
        return grid_layout


class RibbonSeparator(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setMinimumHeight(gui_scale() * 60)
        self.setMaximumHeight(gui_scale() * 80)
        
        self.setMinimumWidth(1)
        self.setMaximumWidth(1)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.fillRect(event.rect(), Qt.lightGray)
        qp.end()
