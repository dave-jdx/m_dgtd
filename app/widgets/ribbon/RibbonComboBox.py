from PyQt5.QtWidgets import QComboBox


class RibbonComboBox(QComboBox):
    def __init__(self,parent, max_width=180):
        QComboBox.__init__(self)
        # self.setStyleSheet("height:30px;font-size:14px;")
        self.setMaximumWidth(max_width)
        self.setMinimumWidth(100)
        self.setFixedHeight(20)
        
        # self._font=self.font()
        # self._font.setPointSize(12)
        # self.setFont(self._font)
        # self.setMaximumHeight(30)
        # self.textChanged.connect(change_connector)
