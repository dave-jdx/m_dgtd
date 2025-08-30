import os
import pickle
import sys,subprocess
import shutil
from ..dataModel.project import Project
from ..widgets.logViewer import LogViewer
import time,logging
from logging.handlers import TimedRotatingFileHandler
from PyQt5.QtCore import QSettings, QStandardPaths
# from .api_license import validate_license

def saveProject(project:Project):
    path = project.fpath
    mkdir(path)
    for dir in project.dirs:
        mkdir(path+"/"+dir)
    projectFile = path+"/"+project.name+".csip"
    content=project.name+"\n"+project.fpath
    mkfile(projectFile,content)

    paramFile=path+"/"+"param.json"
    paramList:list[str]=[]
    paramList.extend(project.headers)
    
    paramList.append(project.calculateType["key"])
    paramList.append(project.calculateType["value"])
    paramList.append(project.power["key"])
    paramList.append(project.power["value"])
    paramList.append(project.mpi["key"])
    paramList.append(project.mpi["value"])
    paramList.append(project.frequencyStart["key"])
    paramList.append(project.frequencyStart["value"])
    paramList.append(project.frequencyEnd["key"])
    paramList.append(project.frequencyEnd["value"])
    paramList.append(project.frequencyIncrement["key"])
    paramList.append(project.frequencyIncrement["value"])
    paramList.append(project.root["key"])
    paramList.append(project.root["value"])

    content=""
    for param in paramList:
        content=content+str(param)+"\n"
    mkfile(paramFile,content)

def saveEDXProject(project:Project):
    # p_path = project.fpath+"/"+project.name+".results"
    # mkdir(p_path)
    # for dir in project.dirs:
    #     mkdir(p_path+"/"+dir)
    projectFile = project.fpath+"/"+project.name+".csip"
    content=project.name+"\n"+project.fpath
    mkfile(projectFile,content)
    pass

def mkdir(path):
    # os.path.exists 函数判断文件夹是否存在
    folder = os.path.exists(path)

    # 判断是否存在文件夹如果不存在则创建为文件夹
    if not folder:
        # os.makedirs 传入一个path路径，生成一个递归的文件夹；如果文件夹存在，就会报错,因此创建文件夹之前，需要使用os.path.exists(path)函数判断文件夹是否存在；
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print('文件夹创建成功：', path)

    else:
        print('文件夹已经存在：', path)


# 定义函数名：在py文件路径下创建cache的txt文件
def mkfile(fname, content):
    fpath=os.path.dirname(fname)

    # 判断当前路径是否存在，没有则创建文件夹
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    # 在当前py文件所在路径下的new文件中创建txt
    # 打开文件，open()函数用于打开一个文件，创建一个file对象，相关的方法才可以调用它进行读写。
    file = open(fname, 'w')
    # 写入内容信息
    file.write(content)

    file.close()
    print('文件创建成功', fname)
def run_exe(fname,logViewer:LogViewer=None):
    pid = os.getpid()
    args=[fname]
    print(args)
    p = subprocess.Popen(args,stdout=subprocess.PIPE)
    # if(logViewer!=None):     
    #     out = myPopenObj.communicate()[0]
    #     logViewer.appendPlainText(str(out)
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line and logViewer:
            logViewer.appendPlainText(format(line))
            # print('Subprogram output: [{}]'.format(line))
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')
   
def copyFile(src,dst):
    fpath=os.path.dirname(dst)
    # 判断当前路径是否存在，没有则创建文件夹
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    shutil.copyfile(src,dst)
    print("copy success",src,dst)

def dumpData(fname:str,obj):
    fpath=os.path.dirname(fname)
    # 判断当前路径是否存在，没有则创建文件夹
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    f=open(fname,"wb")
    pickle.dump(obj,f)
    f.close()
    return (1,"success")
def loadData(fname):
    f = open(fname, 'rb')
    obj = pickle.load(f)
    f.close()
    return obj
def getLogger(name:str="project",_level:int=logging.DEBUG,fpath:str=None):
    logFile=time.strftime("%Y-%m-%d_{0}.log".format(name))
    # fpath=os.path.dirname(logFile)
    if(fpath==None):
        fpath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)+'/csic/Log'
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    fname=fpath+"/"+logFile
    # print(fname)
    _logger:logging.Logger=logging.getLogger(name)
    _handler=TimedRotatingFileHandler(fname,when="midnight",backupCount=30,encoding="utf-8")
    _handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(_handler)
    _logger.setLevel(_level)
    return _logger
    pass
# getLogger("api_project")