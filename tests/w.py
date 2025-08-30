from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QMenu, QAction
import sys
from PyQt5.QtCore import Qt

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个带下拉箭头的按钮
        self.dropdown_button = QToolButton(self)
        self.dropdown_button.setText("New")
        self.dropdown_button.setPopupMode(QToolButton.InstantPopup)
        self.dropdown_button.setFixedSize(200, 50 )
        self.dropdown_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # self.dropdown_button.setStyleSheet("QToolButton::menu-indicator:image{subcontrol-position: right center;}")
        self.dropdown_button.setStyleSheet(
            '''
            QToolButton {
        padding: 15px;
    }
            QToolButton::menu-indicator{
                
                color:red;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                min-width: 20px;
                min-height: 20px;
                margin-right: 50px;
                padding-right: 50px;
                
            }
           
               
 

            '''
        )

        # 创建一个下拉菜单
        self.dropdown_menu = QMenu(self.dropdown_button)

        # 添加一些菜单项
        action1 = QAction("Option 1", self)
        action2 = QAction("Option 2", self)
        action3 = QAction("Option 3", self)
        self.dropdown_menu.addAction(action1)
        self.dropdown_menu.addAction(action2)
        self.dropdown_menu.addAction(action3)

        # 将下拉菜单与按钮关联
        self.dropdown_button.setMenu(self.dropdown_menu)
        

        # 将按钮放到工具栏上
        # self.addToolBar(self.dropdown_button)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())