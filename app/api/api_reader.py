from typing import List, Set, Dict, Tuple
import numpy as np
from numpy import sin, cos, pi
import math


def read_currents(fName: str):
    N_START = 4  # 前4行为描述信息
    N_HEADER = 3  # 每个频点前3行为头文件
    nIndex = 0  # 逐行读取时的行索引
    nv = None  # 顶点数
    nfaces = None  # 三角面数
    fStart = None
    fEnd = None
    space_split = "        "

    pointList: list[tuple(float, float, float, float)] = []
    cellList: list[list[int, int, int]] = []
    fList: List[Tuple[list, list, float, float]] = []
    cN = 12  # 面片顶点序号每列占N个字符
    pN = 20  # 点坐标每列占N个字符
    minV = 0
    maxV = 0

    file = open(fName, "r")
    for line in file:
        if(nIndex == 1):
            nv = int(line.split(space_split)[1])
            # print("nv",nv)
        if(nIndex == 2):
            nfaces = int(line.split(space_split)[1])
            # print("nfaces",nfaces)
            fStart = N_START+N_HEADER
            fEnd = fStart+nv+nfaces
            # print("range",nfaces,fStart,fEnd)
        if(fStart == None or fEnd == None):
            nIndex = nIndex+1
            continue
        if(nIndex >= fStart and nIndex < fEnd):
            if(nIndex < fStart+nv):
                # print("points",line[0:100])
                v = float(line[11*pN:12*pN])
                if(v < minV):
                    minV = v
                if(v > maxV):
                    maxV = v
                pv = (float(line[0*pN:1*pN])*1000, float(line[1*pN:2*pN]) *
                      1000, float(line[2*pN:3*pN])*1000, float(line[11*pN:12*pN]))
                pointList.append(pv)
                # print("points",pointList)
            # 处理频点数据，每个频点的行数 3+nv+nfaces
            else:
                cv = [int(line[0*cN:1*cN])-1, int(line[1*cN:2*cN]) -
                      1, int(line[2*cN:3*cN])-1]
                cellList.append(cv)
                # print("cells",cellList)
            pass
        elif(nIndex == fEnd):
            # 第N+1个频点
            fStart = fEnd+3
            fEnd = fStart+nv+nfaces
            fList.append((pointList, cellList, minV, maxV))
            pointList = []
            cellList = []
            minV = 0
            maxV = 0
            # print("result",fList)
            pass

        nIndex = nIndex+1
    if(len(pointList) > 0 and len(cellList) > 0):
        fList.append((pointList, cellList, minV, maxV))

    return fList



def read_ffr(fName):
    N_START = 1  # 前1行为描述信息
    N_HEADER = 2  # 每个频点2行
    N_FIELD = 1  # 每个计算对象占用一行

    fList = []
    points = []

    nIndex = 0
    fStart = 0
    file = open(fName, "r")

    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):
            if(line.strip().startswith('"')):

                points = sorted(points, key=lambda x: x[1])

                thetaNum = len(list(set(t[0] for t in points)))
                phiNum = len(list(set(t[1] for t in points)))
                # 一组数据增加到列表中，重新计算起始行位置
                fList.append((points, thetaNum, phiNum))
                points = []

                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:

                arr = line.strip().split()
                if(len(arr) == 7):
                    theta = float(arr[0])
                    phi = float(arr[1])
                    r = float(arr[6])
                    points.append((phi, theta, r))
                pass

        nIndex = nIndex+1
        pass
    thetaNum = len(list(set(t[0] for t in points)))
    phiNum = len(list(set(t[1] for t in points)))
    fList.append((points, thetaNum, phiNum))

    resultList = []
    pointList = []
    min = 0
    max = 0
    for item in fList:
        for p in item[0]:
            theta = p[0]
            phi = p[1]
            r = p[2]
            power = 10**(r/20)
            power = power*100
            # power=r
            x = power*sin(phi/180*pi)*sin(theta/180*pi)
            y = power*cos(phi/180*pi)*sin(theta/180*pi)
            z = power*cos(theta/180*pi)
            if(power > max):
                max = power
            if(power < min):
                min = power
            pointList.append((x, y, z, power))
        if(len(pointList) > 0):
            # 已经遍历完成本次的点数组
            resultList.append((pointList, min, max, item[1], item[2], item[0]))
            pointList = []
            min = 0
            max = 0

    return resultList
    return fList
    pass


def read_nfr(fName: str):
    N_START = 2  # 前2行为描述信息
    N_HEADER = 2  # 每个频点2行
    N_FIELD = 1  # 每个计算对象占用一行

    nIndex = 0
    fStart = 0
    file = open(fName, "r",encoding="utf-8")

    fList = []
    points = []
    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):
            if(line.strip().startswith('"')):

                points = sorted(points, key=lambda x: x[1])

                thetaNum = len(list(set(t[0] for t in points)))
                phiNum = len(list(set(t[1] for t in points)))
                # 一组数据增加到列表中，重新计算起始行位置
                fList.append((points, thetaNum, phiNum))
                points = []
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 8):
                    theta = float(arr[0])
                    phi = float(arr[1])
                    r = float(arr[7])
                    points.append((theta, phi, r))
                pass

        nIndex = nIndex+1
        pass
    thetaNum = len(list(set(t[0] for t in points)))
    phiNum = len(list(set(t[1] for t in points)))
    fList.append((points, thetaNum, phiNum))

    resultList = []
    pointList = []
    min = 0
    max = 0
    for item in fList:
        for p in item[0]:
            theta = p[0]
            phi = p[1]
            r = p[2]
            # power=10**(r/10)
            power = r
            x = power*sin(phi/180*pi)*sin(theta/180*pi)
            y = power*cos(phi/180*pi)*sin(theta/180*pi)
            z = power*cos(theta/180*pi)
            if(power > max):
                max = power
            if(power < min):
                min = power
            pointList.append((x, y, z, power))
        if(len(pointList) > 0):
            # 已经遍历完成本次的点数组
            resultList.append((pointList, min, max, item[1], item[2], item[0]))
            pointList = []
            min = 0
            max = 0

    return resultList
    pass


def read_nf(fName: str):
    fList = []
    pointList = []
    min = 0
    max = 0
    N_START = 2  # 前2行为描述信息
    N_HEADER = 2  # 每个频点2行
    N_FIELD = 1  # 每个计算对象占用一行
    nIndex = 0
    fStart = 0
    file = open(fName, "r")
    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):

            if(line.strip().startswith('"')):
                fList.append((pointList, min, max))  # 一组数据增加到列表中，重新计算起始行位置
                pointList = []
                min = 0
                max = 0
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 10):
                    x = float(arr[0])
                    y = float(arr[1])
                    z = float(arr[2])
                    v = float(arr[9])

                    pointList.append((x, y, z, v))
                    if(v > max):
                        max = v
                    if(v < min):
                        min = v
                pass
        nIndex = nIndex+1
        pass
    fList.append((pointList, min, max))
    return fList
    pass

def read_nf_ex(fName: str):
    fList = []
    pointList = []
    min = 0
    max = 0
    N_START = 0  # 前2行为描述信息
    N_HEADER = 0  # 每个频点2行
    N_FIELD = 1  # 每个计算对象占用一行
    nIndex = 0
    fStart = 0
    file = open(fName, "r")
    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):

            if(line.strip().startswith('FREQ')):
                fList.append((pointList, min, max))  # 一组数据增加到列表中，重新计算起始行位置
                pointList = []
                min = 0
                max = 0
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 4):
                    x = float(arr[0])*1000
                    y = float(arr[1])*1000
                    z = float(arr[2])*1000
                    v = float(arr[3])

                    pointList.append((x, y, z, v))
                    if(v > max):
                        max = v
                    if(v < min):
                        min = v
                pass
        nIndex = nIndex+1
        pass
    fList.append((pointList, min, max))
    return fList
    pass

def read_nfr_deg(fName:str):
    N_START = 0  # 前2行为描述信息
    N_HEADER = 2  # 每个频点2行
    N_FIELD = 0  # 每个计算对象占用一行

    nIndex = 0
    fStart = 0
    file = open(fName, "r",encoding="utf-8")

    fList = []
    points = []
    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):
            if(line.strip().startswith('"')):

                points = sorted(points, key=lambda x: x[1])

                thetaNum = len(list(set(t[0] for t in points)))
                phiNum = len(list(set(t[1] for t in points)))
                # 一组数据增加到列表中，重新计算起始行位置
                fList.append((points, thetaNum, phiNum))
                points = []
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 9):
                    theta = float(arr[0])
                    phi = float(arr[1])
                    r = float(arr[8])
                    points.append((theta, phi, r))
                pass

        nIndex = nIndex+1
        pass
    # points = sorted(points, key=lambda x:(x[0], x[1]))
    thetaNum = len(list(set(t[0] for t in points)))
    phiNum = len(list(set(t[1] for t in points)))
    fList.append((points, thetaNum, phiNum))

    resultList = []
    pointList = []
    min = 0
    max = 0
    for item in fList:
        for p in item[0]:
            theta = p[0]
            phi = p[1]
            r = p[2]
            power=10**(r/20)
            # power = r
            x = power*sin(phi/180*pi)*sin(theta/180*pi)
            y = power*cos(phi/180*pi)*sin(theta/180*pi)
            z = power*cos(theta/180*pi)
            if(power > max):
                max = power
            if(power < min):
                min = power
            pointList.append((x, y, z, power))
        if(len(pointList) > 0):
            # 已经遍历完成本次的点数组
            resultList.append((pointList, min, max, item[1], item[2], item[0]))#x/x/x/thetaNum/phiNum/originList
            pointList = []
            min = 0
            max = 0

    return resultList
    pass
def readText(fname: str = ""):
    try:
        with open(fname, 'r') as file:
            content = file.readlines()
        return content
    except FileNotFoundError:
        print(f"Error: File '{fname}' not found.")
        return []
    pass
def read_nf_sbr(fName: str):
    fList = []
    pointList = []
    nIndex = 0
    fStart = 1000000
    c_begin=get_comment("Begin_Simulation Data")
    c_end=get_comment("End_Simulation Data")
    c_freq='"Frequency in Hz"'
    m_unit=1000
    v_freq=-1
    file = open(fName, "r",encoding="utf-8")
    for line in file:
        s_line=line.strip()
        if(s_line.startswith(c_begin)):#开始读取数据
            fStart=nIndex+1
        if(s_line.startswith(c_end)):#结束读取数据
            fList.append((v_freq,pointList))
            break
        if(nIndex>=fStart):#开始读取数据
            if(s_line.startswith(c_freq)):
                if(len(pointList)>0):
                    fList.append((v_freq,pointList))  # 一组数据增加到列表中，重新计算起始行位置
                pointList = []
                if(s_line.startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
                v_freq=float(s_line[len(c_freq)+1:])
            else:
                arr = s_line.split()
                if(len(arr) == 18):
                    x = float(arr[1])*m_unit
                    y = float(arr[2])*m_unit
                    z = float(arr[3])*m_unit
                    ve_abs_x = float(arr[4])
                    ve_phase_x = float(arr[5])
                    ve_abs_y = float(arr[6])
                    ve_phase_y = float(arr[7])
                    ve_abs_z = float(arr[8])
                    ve_phase_z = float(arr[9])

                    vh_abs_x = float(arr[10])
                    vh_phase_x = float(arr[11])
                    vh_abs_y = float(arr[12])
                    vh_phase_y = float(arr[13])
                    vh_abs_z = float(arr[14])
                    vh_phase_z = float(arr[15])

                    ve_abs_total = float(arr[16])
                    vh_abs_total = float(arr[17])
                    pointList.append((x, y, z, 
                                        ve_abs_x, ve_phase_x, 
                                        ve_abs_y, ve_phase_y, 
                                        ve_abs_z, ve_phase_z, 
                                        vh_abs_x, vh_phase_x,
                                        vh_abs_y, vh_phase_y, 
                                        vh_abs_z, vh_phase_z,
                                        ve_abs_total, vh_abs_total))
                pass
        nIndex = nIndex+1
        pass
    
    return fList
    pass

def read_nfr_radius(fName:str):
    N_START = 0  # 前2行为描述信息
    N_HEADER = 2  # 每个频点2行
    N_FIELD = 0  # 每个计算对象占用一行

    nIndex = 0
    fStart = 0
    file = open(fName, "r",encoding="utf-8")

    fList = []
    points = []
    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):
            if(line.strip().startswith('"')):

                points = sorted(points, key=lambda x: x[1])

                thetaNum = len(list(set(t[0] for t in points)))
                phiNum = len(list(set(t[1] for t in points)))
                # 一组数据增加到列表中，重新计算起始行位置
                fList.append((points, thetaNum, phiNum))
                points = []
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 9):
                    theta = math.degrees(float(arr[0]))
                    phi = math.degrees(float(arr[1]))
                    r = float(arr[8])
                    points.append((theta, phi, r))
                pass

        nIndex = nIndex+1
        pass
    # points = sorted(points, key=lambda x:(x[0], x[1]))
    thetaNum = len(list(set(t[0] for t in points)))
    phiNum = len(list(set(t[1] for t in points)))
    fList.append((points, thetaNum, phiNum))

    resultList = []
    pointList = []
    min = 0
    max = 0
    for item in fList:
        for p in item[0]:
            theta = p[0]
            phi = p[1]
            r = p[2]
            power=10**(r/20)
            # power = r
            x = power*sin(phi/180*pi)*sin(theta/180*pi)
            y = power*cos(phi/180*pi)*sin(theta/180*pi)
            z = power*cos(theta/180*pi)
            if(power > max):
                max = power
            if(power < min):
                min = power
            pointList.append((x, y, z, power))
        if(len(pointList) > 0):
            # 已经遍历完成本次的点数组
            resultList.append((pointList, min, max, item[1], item[2], item[0]))#x/x/x/thetaNum/phiNum/originList
            pointList = []
            min = 0
            max = 0

    return resultList
    pass
def read_nf_ex(fName:str):
    fList = []
    pointList = []
    min = 0
    max = 0
    N_START = 0  # 前2行为描述信息
    N_HEADER = 0  # 每个频点2行
    N_FIELD = 1  # 每个计算对象占用一行
    nIndex = 0
    fStart = 0
    file = open(fName, "r")

    for line in file:
        if(nIndex == 0):
            fStart = N_START+N_HEADER+N_FIELD
        if(nIndex >= fStart):
            if(line.strip().startswith('FREQ')):
                fList.append((pointList, min, max))  # 一组数据增加到列表中，重新计算起始行位置
                pointList = []
                min = 0
                max = 0
                if(line.strip().startswith('"Frequency in Hz"')):
                    fStart = nIndex+3
                else:
                    fStart = nIndex+1
                pass
            else:
                arr = line.strip().split()
                if(len(arr) == 4):
                    x = float(arr[0])*1000
                    y = float(arr[1])*1000
                    z = float(arr[2])*1000
                    v = float(arr[3])

                    pointList.append((x, y, z, v))
                    if(v > max):
                        max = v
                    if(v < min):
                        min = v
                pass
        nIndex = nIndex+1
        pass
    fList.append((pointList, min, max))
    return fList
    pass
def get_comment(str):
    return f"<!--{str}-->"

def read_currents_sbr(fName:str):
    '''
    读取sbr表面电流数据，支持多个频点
    '''
    #读取cells
    splitText="\t"
    begin_cell=get_comment("Begin_Triangle Mesh")
    end_cell=get_comment("End_Triangle Mesh")
    begin_current=get_comment("Begin_Simulation Data")
    end_current=get_comment("End_Simulation Data")
    inside_cell=False
    inside_current=False
  
    pointList: list[Tuple[float, float, float, float]] = []
    cellList: list[list[int, int, int]] = []
    fList: List[Tuple[list, list, float, float]] = []

    with open(fName, 'r',encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            
            if(line.startswith(begin_cell)):
                inside_cell=True
                continue
            if(line.startswith(end_cell)):
                inside_cell=False
            
            if(line.startswith(begin_current)):
                inside_current=True
                continue
            if(line.startswith(end_current)):
                inside_current=False
                if(len(pointList)>0):
                    #已经存储了上一个频率的电流数据
                    fList.append((pointList,cellList))
                    pointList=[]
            if(inside_cell):
                #处理网格顶点cell数据
                arr=line.split(splitText)
                if(len(arr)>=4):
                    cellList.append((int(arr[1])-1,int(arr[2])-1,int(arr[3])-1))

                continue
            if(inside_current):
                #处理电流数据 
                
                if(line.startswith("\"Frequency in Hz\"")):
                    if(len(pointList)>0):
                        #已经存储了上一个频率的电流数据
                        fList.append((pointList,cellList))
                        pointList=[]
                else:
                    arr=line.split(splitText)
                
                    if(len(arr)>=13 and not arr[1].startswith("Node")):
                        pointList.append((int(arr[0]),float(arr[1]),float(arr[2]),float(arr[3]),
                                          float(arr[4]),float(arr[5]),float(arr[6]),
                                          float(arr[7]),float(arr[8]),float(arr[9]),
                                          float(arr[10]),float(arr[11]),float(arr[12])))

                continue

            
    return fList

    pass
def read_nf_sbr_E(fName:str):
     #读取nf_E
    splitText="\t"
    begin_E=get_comment("Begin_Simulation Data")
    end_E=get_comment("End_Simulation Data")
    inside_E=False
    pointList=[]#观察点的电场数据 x/y/z "Abs(Ex)"（V/m）  "Phase(Ex)"（deg）  "Abs(Ey)"（V/m）  "Phase(Ey)"（deg）  "Abs(Ez)"（V/m）  "Phase(Ez)"（deg）  "Abs(E_total)"（V/m）
    fList=[]#返回的数据列表 每个元素为一个频点的数据
    freqList=[]
    with open(fName, 'r',encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            
            if(line.startswith(begin_E)):
                inside_E=True
                continue
            if(line.startswith(end_E)): #结束读取电场数据，最后一个频点的数据需要加入fList
                inside_E=False
                if(len(pointList)>0):
                    fList.append(pointList)
                    pointList=[]
            if(inside_E):
                #处理电场数据 
                if(line.startswith("\"Frequency in Hz\"")):
                    freq=line.split(splitText)[1]
                    freqList.append('{:.2e}'.format(float(freq))) 
                    if(len(pointList)>0):
                        
                        fList.append(pointList)
                          
                        pointList=[]
                else:
                    arr=line.split(splitText)
                    if(len(arr)>=11 and not arr[0].startswith('Point_x')):
                        pointList.append((int(arr[0]),float(arr[1]),float(arr[2]),float(arr[3]),
                                        float(arr[4]),float(arr[5]),
                                        float(arr[6]),float(arr[7]),
                                        float(arr[8]),float(arr[9]),
                                        float(arr[10])))
                continue
    return fList,freqList
def read_nf_sbr_H(fName:str):
     #读取nf_H
    splitText="\t"
    begin_E=get_comment("Begin_Simulation Data")
    end_E=get_comment("End_Simulation Data")
    inside_E=False
    pointList=[]#观察点的电场数据 x/y/z "Abs(Ex)"（V/m）  "Phase(Ex)"（deg）  "Abs(Ey)"（V/m）  "Phase(Ey)"（deg）  "Abs(Ez)"（V/m）  "Phase(Ez)"（deg）  "Abs(E_total)"（V/m）
    fList=[]#返回的数据列表 每个元素为一个频点的数据
    with open(fName, 'r',encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            
            if(line.startswith(begin_E)):
                inside_E=True
                continue
            if(line.startswith(end_E)): #结束读取电场数据，最后一个频点的数据需要加入fList
                inside_E=False
                if(len(pointList)>0):
                    fList.append(pointList)
                    pointList=[]
            if(inside_E):
                #处理电场数据 
                if(line.startswith("\"Frequency in Hz\"")):
                    if(len(pointList)>0):
                        fList.append(pointList)
                        pointList=[]
                else:
                    arr=line.split(splitText)
                    if(len(arr)>=11 and not arr[0].startswith('Point_x')):
                        pointList.append((int(arr[0]),float(arr[1]),float(arr[2]),float(arr[3]),
                                        float(arr[4]),float(arr[5]),
                                        float(arr[6]),float(arr[7]),
                                        float(arr[8]),float(arr[9]),
                                        float(arr[10])))
                continue
    return fList
def read_nf_sbr_Power(fName:str):
     #读取nf_H
    '''
    sbr-电磁干扰数据
    '''
    splitText="\t"
    begin_E=get_comment("Begin_Simulation Data")
    end_E=get_comment("End_Simulation Data")
    inside_E=False
    pointList=[]#观察点的电场数据 x/y/z  "Abs(Voltage)"（V）  "Phase(Voltage)"（deg）  "Abs(Current)"（A）  "Phase(Current)"（deg）  "Abs(Power)"（W）   "Phase(Power)"（deg）
    fList=[]#返回的数据列表 每个元素为一个频点的数据
    freqList=[]
    with open(fName, 'r',encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            
            if(line.startswith(begin_E)):
                inside_E=True
                continue
            if(line.startswith(end_E)): #结束读取电场数据，最后一个频点的数据需要加入fList
                inside_E=False
                if(len(pointList)>0):
                    fList.append(pointList)
                    pointList=[]
            if(inside_E):
                #处理电场数据 
                if(line.startswith("\"Frequency in Hz\"")):
                    freq=line.split(splitText)[1]
                    freqList.append('{:.2e}'.format(float(freq)))
                    if(len(pointList)>0):
                        fList.append(pointList)
                        pointList=[]
                else:
                    arr=line.split(splitText)
                    if(len(arr)>=10):
                        pointList.append((int(arr[0]),float(arr[1]),float(arr[2]),float(arr[3]),
                                        float(arr[4]),float(arr[5]),
                                        float(arr[6]),float(arr[7]),
                                        float(arr[8]),float(arr[9])))
                continue
    return fList,freqList
def read_thermal_3d(fname:str):
    splitText="\t"
    m_unit=1000
    begin_tet=get_comment("Begin_Tet Mesh")
    end_tet=get_comment("End_Tet Mesh")

    begin_node=get_comment("Begin_Node Coord")
    end_node=get_comment("End_Node Coord")

    begin_thermal=get_comment("Begin_Simulation Data")
    end_thermal=get_comment("End_Simulation Data")
    points_list=[]
    cell_list=[]
    thermal_values=[]
    inside_tet=False
    inside_node=False
    inside_thermal=False
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            if(line.startswith(begin_tet)):
                inside_tet=True
                continue
            if(line.startswith(end_tet)):
                inside_tet=False
                continue
            if(line.startswith(begin_node)):
                inside_node=True
                continue
            if(line.startswith(end_node)):
                inside_node=False
                continue
            if(line.startswith(begin_thermal)):
                inside_thermal=True
                continue
            if(line.startswith(end_thermal)):
                inside_thermal=False
                continue
            if(inside_tet):
                #处理四面体网格数据
                arr=line.split()
                if(len(arr)>=5):
                    index=int(arr[0])-1
                    i=int(arr[1])-1
                    j=int(arr[2])-1
                    k=int(arr[3])-1
                    l=int(arr[4])-1
                    cell_list.append((i,j,k,l))
            if(inside_node):
                #处理节点数据
                arr=line.split()
                if(len(arr)>=4):
                    index=int(arr[0])-1
                    x=float(arr[1])*m_unit
                    y=float(arr[2])*m_unit
                    z=float(arr[3])*m_unit
                    points_list.append((x,y,z))
            if(inside_thermal):
                #处理热分析数据
                arr=line.split()
                if(len(arr)>=2):
                    index=int(arr[0])-1
                    thermal=float(arr[1])
                    thermal_values.append((thermal))
    return points_list,cell_list,thermal_values
def read_thermal_2d(fname:str):
    splitText="\t"
    begin_2d_data=get_comment("Begin_Simulation Data")
    end_2d_data=get_comment("End_Simulation Data")

    thermal_values=[]

    inside_thermal=False
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            line=line.strip()
    
            if(line.startswith(begin_2d_data)):
                inside_thermal=True
                continue
            if(line.startswith(end_2d_data)):
                inside_thermal=False
                continue

            if(inside_thermal):
                #处理热分析数据
                arr=line.split()
                if(len(arr)>=6):
                    try:
                        timeStep=round(float(arr[0]),0)
                        thermal=float(arr[5])
                        thermal_values.append((timeStep,thermal))
                    except Exception as e:
                        print(e)
                        pass
    return thermal_values

def read_displacement_3d(fname:str):
    splitText="\t"
    m_unit=1000
    begin_tet=get_comment("Begin_Tet Mesh")
    end_tet=get_comment("End_Tet Mesh")

    begin_node=get_comment("Begin_Node Coord")
    end_node=get_comment("End_Node Coord")

    begin_thermal=get_comment("Begin_Simulation Data")
    end_thermal=get_comment("End_Simulation Data")
    points_list=[]
    cell_list=[]
    displacement_values=[]
    inside_tet=False
    inside_node=False
    inside_thermal=False
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            if(line.startswith(begin_tet)):
                inside_tet=True
                continue
            if(line.startswith(end_tet)):
                inside_tet=False
                continue
            if(line.startswith(begin_node)):
                inside_node=True
                continue
            if(line.startswith(end_node)):
                inside_node=False
                continue
            if(line.startswith(begin_thermal)):
                inside_thermal=True
                continue
            if(line.startswith(end_thermal)):
                inside_thermal=False
                continue
            if(inside_tet):
                #处理四面体网格数据
                arr=line.split()
                if(len(arr)>=5):
                    index=int(arr[0])-1
                    i=int(arr[1])-1
                    j=int(arr[2])-1
                    k=int(arr[3])-1
                    l=int(arr[4])-1
                    cell_list.append((i,j,k,l))
            if(inside_node):
                #处理节点数据
                arr=line.split()
                if(len(arr)>=4):
                    index=int(arr[0])-1
                    x=float(arr[1])*m_unit
                    y=float(arr[2])*m_unit
                    z=float(arr[3])*m_unit
                    points_list.append((x,y,z))
            if(inside_thermal):
                #处理热分析数据
                arr=line.split()
                if(len(arr)>=5):
                    index=int(arr[0])-1
                    d_x=float(arr[1])*m_unit
                    d_y=float(arr[2])*m_unit
                    d_z=float(arr[3])*m_unit
                    magnitude=float(arr[4])
                    displacement_values.append((d_x,d_y,d_z,magnitude))
    return points_list,cell_list,displacement_values

def read_em_2d(fname:str):
    splitText="\t"
    begin_2d_data=get_comment("Begin_Simulation Data")
    end_2d_data=get_comment("End_Simulation Data")

    s_values=[]

    inside_data=False
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            line=line.strip()
    
            if(line.startswith(begin_2d_data)):
                inside_data=True
                continue
            if(line.startswith(end_2d_data)):
                inside_data=False
                continue

            if(inside_data):
                #处理热分析数据
                arr=line.split()
                if(len(arr)>=9):
                    try:
                        timeStep=float(arr[0])
                        v=float(arr[8])
                        s_values.append((timeStep,v))
                    except Exception as e:
                        print(e)
                        pass
    return s_values
    pass
def read_em_3d(fname:str):
    splitText="\t"
    m_unit=1000
    begin_tet=get_comment("Begin_Tet Mesh")
    end_tet=get_comment("End_Tet Mesh")

    begin_node=get_comment("Begin_Node Coord")
    end_node=get_comment("End_Node Coord")

    begin_data=get_comment("Begin_Simulation Data")
    end_data=get_comment("End_Simulation Data")
    points_list=[]
    cell_list=[]
    e_values=[]
    inside_tet=False
    inside_node=False
    inside_data=False
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            line=line.strip()
            if(line.startswith(begin_tet)):
                inside_tet=True
                continue
            if(line.startswith(end_tet)):
                inside_tet=False
                continue
            if(line.startswith(begin_node)):
                inside_node=True
                continue
            if(line.startswith(end_node)):
                inside_node=False
                continue
            if(line.startswith(begin_data)):
                inside_data=True
                continue
            if(line.startswith(end_data)):
                inside_data=False
                continue
            if(inside_tet):
                #处理四面体网格数据
                arr=line.split()
                if(len(arr)>=5):
                    index=int(arr[0])-1
                    i=int(arr[1])-1
                    j=int(arr[2])-1
                    k=int(arr[3])-1
                    l=int(arr[4])-1
                    cell_list.append((i,j,k,l))
            if(inside_node):
                #处理节点数据
                arr=line.split()
                if(len(arr)>=4):
                    index=int(arr[0])-1
                    x=float(arr[1])*m_unit
                    y=float(arr[2])*m_unit
                    z=float(arr[3])*m_unit
                    points_list.append((x,y,z))
            if(inside_data):
                #处理热分析数据
                arr=line.split()
                if(len(arr)>=2):
                    index=int(arr[0])-1
                    v=float(arr[4])
                    e_values.append((v))
    return points_list,cell_list,e_values
    pass
def read_em_ffr(fname:str):
    N_START = 0  # 前1行为描述信息
    N_HEADER = 4  # 每个频点2行
    N_FIELD = 0  # 每个计算对象占用一行

    fList = []
    points = []

    nIndex = 0
    fStart = 0
    maxV=0
    minV=0
    with open(fname,"r",encoding="utf-8") as file:
        for line in file:
            if(nIndex == 0):
                fStart = N_START+N_HEADER+N_FIELD
            if(nIndex >= fStart):

                arr = line.strip().split()
                if(len(arr) >= 7):
                    theta = float(arr[0])
                    phi = float(arr[1])
                    r = float(arr[6])
                    points.append((theta, phi, r))
                    # if(abs(r)>=maxV):
                    #     maxV=abs(r)
                    # pass
                    if(r > maxV):
                        maxV = r
                    if(r < minV):
                        minV = r


            nIndex = nIndex+1
            pass
    thetaNum = len(list(set(t[0] for t in points)))
    phiNum = len(list(set(t[1] for t in points)))
    points = sorted(points, key=lambda x: x[1])
    fList.append((points, thetaNum, phiNum))

    resultList = []
    pointList = []
    # minV = 0
    # maxV = 0
    scaling_factor=1

    
    offset=0
    if(minV < 0):
        # R_linear+=offset #将db值全部转换为正值
        offset=0-minV #偏移量，将db值全部转换为正值
        minV+=offset
        maxV+=offset

    # 检查 max_value 是否为零，避免对数运算错误
    # if maxV == 0:
    #     scaling_factor = 1  # 数据全为零，不需要缩放
    # else:
    #     # 计算数量级
    #     exponent = np.floor(np.log10(maxV))
    #     # 设定目标数量级
    #     desired_exponent = 0  # 使数据接近 1
    #     # 计算缩放因子
    #     scaling_factor = 10 ** (desired_exponent - exponent)
    # scaling_factor=1
    


    for item in fList:
        for p in item[0]:
            theta = p[0]
            phi = p[1]
            r = p[2]
            # power = 10**(r/20)
            # power = power*100
            # power=r*scaling_factor

            power=r+offset
            x = power*sin(theta/180*pi)*cos(phi/180*pi)
            y = power*sin(theta/180*pi)*sin(phi/180*pi)
            z = power*cos(theta/180*pi)
            # if(power > max):
            #     max = power
            # if(power < min):
            #     min = power
            pointList.append((x, y, z, power))
        if(len(pointList) > 0):
            # 已经遍历完成本次的点数组
            resultList.append((pointList, minV, maxV, item[1], item[2], item[0],scaling_factor))
            pointList = []
            # min = 0
            # max = 0

    return resultList
    pass

def read_ffr_gdtd(fName:str):
    #暂时只支持读取一个频点的数据
    N_START = 0  # 前1行为描述信息
    N_HEADER = 4  # 每个频点2行
    N_FIELD = 0  # 每个计算对象占用一行

    fList = []
    points = []
    nIndex = 0
    fStart = 0
    with open(fName,"r",encoding="utf-8") as file:
        for line in file:
            if(nIndex == 0):
                fStart = N_START+N_HEADER+N_FIELD
            if(nIndex >= fStart):

                arr = line.strip().split()
                if(len(arr) >= 8):
                    theta = float(arr[0])
                    phi = float(arr[1])
                    r = float(arr[6])
                    r_db=float(arr[7]) #dB值
                    points.append((theta, phi, r_db,r))
            nIndex = nIndex+1
            pass

    fList.append(points)
    return fList