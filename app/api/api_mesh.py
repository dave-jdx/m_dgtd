import os
import traceback
from PyQt5 import QtWidgets
from typing import List,Set,Dict,Tuple
from ngsolve import BND



from netgen.occ import *

from ngsolve import Mesh
from ngsolve.meshes import MeshingParameters as mp

from path import Path
# from netgen import meshing

from netgen.meshing import MeshingStep,MeshingParameters,ImportMesh
from ..dataModel.mesh import MeshFormat
from .api_config import config_path


def mesh_generate(geo):  # 网格划分，提供几何对象，返回mesh对象，用于可视化显示
    mesh = Mesh(geo.GenerateMesh())
    return mesh

def geo_load(fname):
    geo=OCCGeometry(fname)
    
    return geo
def mesh_geo(fname:str):
    geo=OCCGeometry(fname)
    mesh=Mesh(geo.GenerateMesh(maxh=2000,perfstepsend=MeshingStep.MESHSURFACE))
    return mesh,geo
def mesh_generate(fname:str,meshFileName:str,maxH:float=3,localSizeDict:dict={}):
    '''
    生成网格文件并返回网格mesh对象
    :param fname:模型文件名
    :param maxH:尺寸参数maxH
    '''
    try:

        geo=OCCGeometry(fname)
        # shape=geo.GetHandle().GetObject().GetShape()
        if localSizeDict is not None:
            for k in localSizeDict.keys():
                geo.SetFaceMeshsize(k,localSizeDict[k])
        # geo.SetFaceMeshsize(0,3)
        m1=geo.GenerateMesh(maxh=maxH,perfstepsend=MeshingStep.MESHSURFACE,grading=100)
        mesh=Mesh(m1)
        
        # mesh.GenerateVolumeMesh()
        fpath=os.path.dirname(meshFileName)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        mesh.ngmesh.Export(meshFileName, "STL Format")
        # raise SystemError("mesh wrong.")
        return (1,"网格生成成功      ",(meshFileName,mesh))
    except Exception as e:
        errMessage=traceback.format_exc()
        return (-1,errMessage,None)

    
# def mesh_generate_stl(sourceFile, edge):  # 对模型文件进行网格划分,返回生成的stl文件【相对路径+文件名】
#     '''传入待划分网格的文件名以及选中的edge信息，进行网格划分后返回stl文件路径、
#     Args:
#         sourceFile:模型文件名【含路径】
#         edge:netgen中的edge对象，需要包含start/end信息
#     Returns:
#         targetFile:stl文件名【相对路径】
#         mesh:ngsolve.com.Mesh 可用于直接访问的mesh对象
#     '''
#     # print(edge)
#     targetFile = config_path+"/temp/meshTarget.stl"
#     geo = OCCGeometry(sourceFile)
    
#     mesh = Mesh(geo.GenerateMesh())
#     mesh.ngmesh.Export(targetFile, "STL Format")
#     return targetFile, mesh


def exportMesh(mesh:Mesh, fileName:str,format:str):  # 网格数据导出
    '''传入mesh对象，导出指定格式的文件
    Args:
        mesh：ngsolve.comp.Mesh对象
        targetFile:导出网格文件名【含路径】
        format:导出文件格式 如 "STL Format"/"Gmsh Format"
    Returns:
        (1,"success")
    '''
    try:
        cacheFile=export_cache_fname(fileName)
        mesh.ngmesh.Export(cacheFile, MeshFormat.stl)
        if(MeshFormat.emx in (format)):
            exportMesh2EMX(mesh,fileName) 
        elif(MeshFormat.cgns in (format)):
            mesh.ngmesh.Export(fileName,MeshFormat.nf)
        elif(MeshFormat.tec in (format)):
            mesh.ngmesh.Export(fileName,MeshFormat.nf)   
        else:
            for f in MeshFormat.exportList:
                if(f in (format)):
                    mesh.ngmesh.Export(fileName, f)
                    break
            
        # if(MeshFormat.stl in(format) ):
        #     mesh.ngmesh.Export(fileName, MeshFormat.stl)
        # if(MeshFormat.emx in(format) ):#自定义导出格式
        #     exportMesh2EMX(mesh,fileName)
        #     pass
        # if(MeshFormat.gmsh in(format)):
        #     mesh.ngmesh.Export(fileName,MeshFormat.gmsh)
        # if(MeshFormat.nf in (format) ):
        #     mesh.ngmesh.Export(fileName,MeshFormat.nf)
        return(1,"导出网格成功        ")
    except Exception as ex:
        print(str(ex))
        return (-1,"导出网格失败:"+str(ex))
def exportMesh2EMX(mesh:Mesh,fileName:str): 
    meshObj=mesh
    nv=meshObj.nv #顶点数
    nfaces=meshObj.nface #三角面数
    strList:list[str]=[]

    strList.append(str(nfaces))
    strList.append(str(nv))

    for vertice in meshObj.vertices:
        vIndex=vertice.nr+1  
        point=vertice.point
        x=format(point[0],".6f")
        y=format(point[1],".6f")
        z=format(point[2],".6f")
        strList.append(str(vIndex)+" "+str(x)+" "+str(y)+" "+str(z))
    for el in meshObj.Elements(BND):
        # print ("vertices: ", el.vertices)
        # print("faceId",el.index) el.index是原模型的face编号
        fIndex=el.nr+1
        v=el.vertices
        v1=int(str(v[0])[1:])+1
        v2=int(str(v[1])[1:])+1
        v3=int(str(v[2])[1:])+1
        strList.append(str(fIndex)+" "+str(v1)+" "+str(v2)+" "+str(v3))
    fwriter = open(fileName, 'w')
    for s in strList:
        fwriter.write(s+"\n")
    fwriter.close()
    pass
def getVerticeList(mesh:Mesh,edge:Tuple[Tuple[float,float,float],Tuple[float,float,float]]):
    '''
    根据edge的start end，选取在这条edge上的vertice并返回
    '''
    meshObj:Mesh=mesh
    vList:List[Tuple[int,Tuple[float,float,float]]]=[]# 顶点编号，
    startPoint=edge[0]
    endPoint=edge[1]
    minX=min(startPoint[0],endPoint[0])
    maxX=max(startPoint[0],endPoint[0])
    minY=min(startPoint[1],endPoint[1])
    maxY=max(startPoint[1],endPoint[1])
    minZ=min(startPoint[2],endPoint[2])
    maxZ=max(startPoint[2],endPoint[2])
    for vertice in meshObj.vertices:
        p=vertice.point
        
        vItem=(vertice.nr+1,p)
        # print("minX",p[0]>=minX)
        # print("minY",p[1]>=minY)
        # print("minZ",p[2]>=minZ)
        # print("maxX",p[0]<=maxX)
        # print("maxY",p[1]<=maxY)
        # print("maxZ",p[2]<=maxZ)

        if(p[0]>=minX and p[0]<=maxX and p[1]>=minY and p[1]<=maxY and p[2]>=minZ and p[2]<=maxZ):
            print("in points",p)
            #保证顶点在edge范围内
            if((p[0]==startPoint[0] and p[1]==startPoint[1])
                or(p[0]==startPoint[0] and p[2]==startPoint[2])
                or(p[1]==startPoint[1] and p[2]==startPoint[2])):
                #任意两点重合，即可认为是在一个线上
                vList.append(vItem)
                pass
            elif((p[0]==endPoint[0] and p[1]==endPoint[1])
                or(p[0]==endPoint[0] and p[2]==endPoint[2])
                or(p[1]==endPoint[1] and p[2]==endPoint[2])):
                #任意两点重合，即可认为是在一个线上
                vList.append(vItem)
                pass
            else:
                #判断x3-x1/x2-x1==y3-y1/y2-y1==z3-z1/z2-z1 则认为在一条直线上
                x=p[0]
                y=p[1]
                z=p[2]
                x1=startPoint[0]
                x2=endPoint[0]
                y1=startPoint[1]
                y2=endPoint[1]
                z1=startPoint[2]
                z2=endPoint[2]
                
                L=x2-x1
                M=y2-y1
                N=z2-z1

                d1=x-x1
                d2=y-y1
                d3=z-z1

                fx=True
                fy=True
                fz=True
                if(L==0):
                    if(d1!=0):
                        continue #不符合条件
                    else:
                        fx=False #不用计算X
                if(M==0):
                    if(d2!=0):
                        continue #不符合条件
                    else:
                        fy=False #不用计算Y
                if(N==0):
                    if(d3!=0):
                        continue #不符合条件
                    else:
                        fz=False #不用计算Z
                s1=None
                s2=None
                s3=None
                if(L!=0):
                    s1=round(d1/L,9)
                if(M!=0):
                    s2=round(d2/M,9)
                if(N!=0):
                    s3=round(d3/N,9)
                # print('斜率',s1,s2,s3)
                if(fx and fy and fz):
                    #三个方向均可计算
                    if(s1==s2 and s2==s3):
                        vList.append(vItem)
                    continue
                if(fx and fy):
                    if(s1==s2):
                        vList.append(vItem)
                    continue
                if(fx and fz):
                    if(s1==s3):
                        vList.append(vItem)
                    continue
                if(fy and fz):
                    if(s2==s3):
                        vList.append(vItem)
                    continue
    vListNext:List[Tuple[int,Tuple[float,float,float],float]]=[]# 顶点编号含与start的距离
    for item in vList:
        p=item[1]
        d=pow(p[0]-startPoint[0],2)+pow(p[1]-startPoint[1],2)+pow(p[2]-startPoint[2],2)
        vListNext.append((item[0],item[1],d))
    vListNext.sort( key=lambda v : v[2])
    vxList:list[tuple[int,int]]=[]
    for i in range(len(vListNext)-1):
        vxList.append((vListNext[i][0],vListNext[i+1][0]))
    return vxList
    pass
def mesh_import(fileName:str,format:str):
    # EXTENSIONS = MeshFormat.importExtensions
    # curr_dir = Path('').abspath().dirname()
    # fname,filter_ = QtWidgets.QFileDialog.getOpenFileName(directory=curr_dir, filter=EXTENSIONS)
    # if fname != '':
    # #   meshObj=ImportMesh(fname)
      
    #   mesh=Mesh(fname)

    targetFile=export_cache_fname(fileName)
    for f in MeshFormat.importExtensionsList:
        if(f in(format)):
            mesh=Mesh(fileName)
            exportMesh(mesh,targetFile,MeshFormat.stl)
            break
    return(1,"网格数据导入成功",{"file":targetFile,"mesh":None})
      
    pass
def export_cache_fname(fileName:str):
    fname,extension=os.path.splitext(os.path.basename(fileName))
    targetFile="temp/{}.{}.stl".format(fname,extension)
    fpath=os.path.dirname(targetFile)
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    return targetFile


