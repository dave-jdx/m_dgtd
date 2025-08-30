from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui     import QPalette
from PyQt5.QtCore import Qt, QRect
from ..icons import sysIcons
from .baseStyle import baseStyle
from .customTitleBar import CTitleBar
from ..theme import theme_ui
class frmBase(QtWidgets.QMainWindow):
    def __init__(self,parent=None,):
        super(frmBase,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
    
  

        self.setWindowFlags(self.windowFlags()|QtCore.Qt.WindowType.FramelessWindowHint)
        self._theme:theme_ui=theme_ui("gray")
        self._titleBar=CTitleBar(self,title=f"{self.windowTitle()}")#设置系统标题
        self.setMenuWidget(self._titleBar)
        self._titleBar.setStyleSheet(self._theme.titleBar)
        self.pattern = QtCore.QRegExp("^[+\-]?\d*\.?\d*$")
        self.decimal_validator = QtGui.QRegExpValidator(self.pattern, self)

        self.setAutoFillBackground(True)          # 让自定义调色板生效
        pal = self.palette()
        pal.setColor(QPalette.Window, Qt.white)   # 或 QColor("#ffffff")
        self.setPalette(pal)
        
        self.gbxStyle="QGroupBox:title{left:5px;height:25px}"
        self.lintEditFocusStyle="""
        background-color:rgb(255,255,0);
        font-size:14px;
        font-family:"Microsoft YaHei","Segoe UI", "Arial","Tahoma" , "sans-serif"
        """
        self.lineEditDefaultStyle="""
        background-color:rgb(255,255,255);
        font-size:14px;
        font-family:"Microsoft YaHei","Segoe UI", "Arial","Tahoma" , "sans-serif";
        """
        self.lineEditStyle="""
        QLineEdit:focus{background-color:rgb(255,255,0);}
        """
        
    def onLoad(self):


        self._font=self.font()
        self._font.setPixelSize(baseStyle.fontPixel_14)
        self._font.setFamilies(baseStyle.fontFamilys)
        self.setFont(self._font)
        self.setStyleSheet(self.lineEditStyle)
        self.setFixedHeight(self.height()+36)

    def paintEvent(self, event):
        # 创建QPainter对象
        painter = QPainter(self)
        
        # 设置绘制边框的颜色和宽度
        border_color = QColor(198, 198, 198)  # 黑色
        border_width = 1  # 边框宽度

        # 创建画笔并设置边框样式
        pen = QPen(border_color)
        pen.setWidth(border_width)
        painter.setPen(pen)

        # 绘制边框（矩形边框）
        painter.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

        # 调用父类的绘制事件来绘制其他内容
        super().paintEvent(event)
        
        


        
        

   
        
