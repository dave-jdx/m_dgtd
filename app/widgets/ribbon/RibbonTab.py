from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from .RibbonPane import RibbonPane
from PyQt5.QtGui import QFont


class RibbonTab(QWidget):
    def __init__(self, parent, name):
        self.parent=parent
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft)
        # self._font=self.font()
        # self._font.setPointSize(12)
        # self.setFont(self._font)
        

    def add_ribbon_pane(self, name):
        ribbon_pane = RibbonPane(self, name)
        self.layout().addWidget(ribbon_pane)
        return ribbon_pane
    def remove_ribbon_pane(self,panWidget:RibbonPane):
        self.layout().removeWidget(panWidget)
        panWidget.deleteLater()
    
    def add_ribbon_pane_widget(self, widget:RibbonPane):
        self.layout().addWidget(widget)
        return widget

    def add_spacer(self):
        # self.layout().addSpacerItem(QSpacerItem(1, 1, QSizePolicy.MinimumExpanding))
        # self.layout().setStretch(self.layout().count() - 1, 1)
        pass
