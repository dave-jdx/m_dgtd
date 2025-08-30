import os
def readCurrent(fName:str="data/current0213.txt"):
    nStart=4 #前4行为描述信息
    nHeader=3#每个频点前3行为头文件
    nIndex=0 #逐行读取时的行索引
    nv=None #顶点数
    nfaces=None #三角面数
    fStart=None
    fEnd=None
    space_split="        "

    pointList:list[tuple(float,float,float,float)]=[]
    cellList:list[list[int,int,int]]=[]
    fList:list[tuple[list,list]]=[]
    cN=12
    pN=20
    minV=0
    maxV=0

    file=open(fName,"r")
    for line in file:
        if(nIndex==1):
            nv=int(line.split(space_split)[1])
            # print("nv",nv)
        if(nIndex==2):
            nfaces=int(line.split(space_split)[1])
            # print("nfaces",nfaces)
            fStart=nStart+nHeader
            fEnd=fStart+nv+nfaces
            print("range",nfaces,fStart,fEnd)
        if(fStart ==None or fEnd ==None):
            nIndex=nIndex+1
            continue
        if(nIndex>=fStart and nIndex<fEnd):
            if(nIndex<fStart+nv):
                # print("points",line[0:100])
                v=float(line[11*pN:12*pN])
                if(v<minV):
                    minV=v
                if(v>maxV):
                    maxV=v
                pv=(float(line[0*pN:1*pN]),float(line[1*pN:2*pN]),float(line[2*pN:3*pN]),float(line[11*pN:12*pN]))
                pointList.append(pv)
                # print("points",pointList)
            #处理频点数据，每个频点的行数 3+nv+nfaces
            else:
                cv=[int(line[0*cN:1*cN])-1,int(line[1*cN:2*cN])-1,int(line[2*cN:3*cN])-1]
                cellList.append(cv)
                # print("cells",cellList)
            pass
        elif(nIndex==fEnd):
            #第N+1个频点
            fStart=fEnd+3
            fEnd=fStart+nv+nfaces
            fList.append((pointList,cellList,minV,maxV))
            pointList=[]
            cellList=[]
            minV=0
            maxV=0
            # print("result",fList)
            pass
        
        nIndex=nIndex+1
    if(len(pointList)>0 and len(cellList)>0):
        fList.append((pointList,cellList,minV,maxV))
    # print("result",fList)
    pList=fList[0][0]
    f=open("data/a.txt","w")
    f.write("x\ty\tz\tval"+"\n")
    for p in pList:
        f.write(str(p[0]*1000)+"\t"+str(p[1]*1000)+"\t"+str(p[2]*1000)+"\t"+str(p[3])+"\n")
        pass
    f.close()
        
    return fList
    pass
# readCurrent("data/current.txt")