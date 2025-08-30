

stylesheet_instance = None
from PyQt5.QtCore import QCoreApplication
class theme_ui(object):

    baseWidgetStyle='''
    QMainWindow,QWidget{
    font-family: Arial, 'Segoe UI', Tahoma, "Microsoft YaHei", sans-serif;
    font-size: 16px;
    }
        '''
    def __init__(self,themName:str="gray") -> None:
        self.titleBar=None
        self.ribbon=None
        self.ribbonPane=None
        self.ribbonButton=None
        self.ribbonSmallButton=None
        self.projectTree=None
        self.menu=None
        self.exe_dir = QCoreApplication.applicationDirPath()

    
        
        self.onLoad(themName)
        pass
    def get_stylesheet(self, path):
        path=f"{self.exe_dir}/{path}"
        with open(path) as data_file:
            stylesheet = data_file.read()
        return stylesheet
    def onLoad(self,themeName):
        
        self.titleBar=self.get_stylesheet(f"stylesheets/{themeName}/titleBar.css")
        self.ribbon=self.get_stylesheet(f"stylesheets/{themeName}/ribbon.css")
        self.ribbonPane=self.get_stylesheet(f"stylesheets/{themeName}/ribbonPane.css")
        self.ribbonButton=self.get_stylesheet(f"stylesheets/{themeName}/ribbonButton.css")
        self.ribbonSmallButton=self.get_stylesheet(f"stylesheets/{themeName}/ribbonSmallButton.css")
        self.menu=self.get_stylesheet(f"stylesheets/{themeName}/menu.css")

        


class Stylesheets(object):
    def __init__(self):
        self._stylesheets = {}
        self.make_stylesheet("main", "stylesheets/main.css")
        self.make_stylesheet("ribbon", "stylesheets/ribbon.css")
        self.make_stylesheet("ribbonPane", "stylesheets/ribbonPane.css")
        self.make_stylesheet("ribbonButton", "stylesheets/ribbonButton.css")
        self.make_stylesheet("ribbonSmallButton", "stylesheets/ribbonSmallButton.css")

    def make_stylesheet(self, name, path):
        
        with open(path) as data_file:
            stylesheet = data_file.read()

        self._stylesheets[name] = stylesheet

