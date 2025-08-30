from PyQt5.QtCore import QSettings, QStandardPaths

# 获取应用程序的配置文件路径
config_path = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)+"/ShipEMX"
config_file=config_path + "/emx.ini"

# 创建 QSettings 对象
settings = QSettings(config_file, QSettings.IniFormat)
key_mpi="mpiInstalled"

def initConfig():
    settings.setValue(key_mpi,0)
def getMpiInstalled():
    return settings.value(key_mpi)
def setMpiInstalled():
    settings.setValue(key_mpi,1)
# initConfig()
# print(config_file)
# initConfig()
# setMpiInstalled()
# print(getMpiInstalled())