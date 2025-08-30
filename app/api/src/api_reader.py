from typing import List, Set, Dict, Tuple
from numpy import sin, cos, pi


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
            power = 10**(r/10)
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
    file = open(fName, "r")

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


def readText(fname: str = ""):
    try:
        with open(fname, 'r') as file:
            content = file.readlines()
        return content
    except FileNotFoundError:
        print(f"Error: File '{fname}' not found.")
        return []
    pass
