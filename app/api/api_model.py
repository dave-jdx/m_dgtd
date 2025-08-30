import os,traceback
import numpy as np
import subprocess
import threading
import time
from math import degrees,pi
from typing import List, Set, Dict, Tuple
from path import Path
from PyQt5 import QtWidgets

from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Edge, TopoDS_Shape, TopoDS_Builder, TopoDS_Compound
from OCC.Core.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                             TopAbs_SHELL, TopAbs_SOLID)
from OCC.Core.StlAPI import stlapi_Read, StlAPI_Writer,StlAPI_Reader
from OCC.Core.BOPAlgo import BOPAlgo_Splitter,BOPAlgo_Builder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse




from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display import OCCViewer
from OCC.Core.TopExp import topexp, TopExp_Explorer
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln,gp_Ax2,gp_Ax3, gp_Vec,gp_Trsf,gp_GTrsf,gp_Ax1,gp_Lin
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeFace,
                                    BRepBuilderAPI_MakeVertex,
                                    BRepBuilderAPI_MakeEdge,
                                    BRepBuilderAPI_Transform,
                                    BRepBuilderAPI_GTransform)
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.Geom import Geom_Surface,Geom_Plane,Geom_Axis2Placement,Geom_Line
from OCC.Core.AIS import AIS_Trihedron,AIS_Shape
from OCC.Core.Prs3d import Prs3d_DatumParts
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.Poly import Poly_Triangulation,Poly_Array1OfTriangle,Poly_Triangle

from OCC.Core.AIS import AIS_Axis,AIS_ColoredShape
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_RED, Quantity_NOC_GREEN, Quantity_NOC_BLUE1
from OCC.Core.Prs3d import Prs3d_DatumAspect, Prs3d_Drawer
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.TopAbs import TopAbs_ON, TopAbs_IN, TopAbs_OUT

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import (GeomAbs_Plane,GeomAbs_Cone,GeomAbs_Cylinder,GeomAbs_BezierCurve,
GeomAbs_BezierSurface,GeomAbs_BSplineCurve,GeomAbs_BSplineSurface,GeomAbs_Circle,GeomAbs_Cone,GeomAbs_Cylinder,
GeomAbs_OffsetSurface,GeomAbs_Plane,GeomAbs_SurfaceOfExtrusion,GeomAbs_SurfaceOfRevolution,GeomAbs_Torus,GeomAbs_Sphere)

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Prs3d import Prs3d_ShadingAspect, Prs3d_Drawer
from OCC.Core.Aspect import Aspect_TOFM_BOTH_SIDE, Aspect_TOFM_FRONT_SIDE, Aspect_TOFM_BACK_SIDE
from OCC.Core.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                             TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
                               TopAbs_COMPSOLID, TopAbs_FORWARD, TopAbs_REVERSED)
from OCC.Core.BRepTools import BRepTools_ReShape
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
# from OCC.Core.GProp import GProp_GProps
# from OCC.Core.BRepGProp import brepgprop_VolumeProperties
# from OCC.Core.BRepCheck import BRepCheck_Analyzer
# from OCC.Core.ShapeFix import ShapeFix_Solid
# from OCC.Core.ShapeAnalysis import ShapeAnalysis_Shell
#导入检测自相交的方法
# from OCC.Core.BRepCheck import BRepCheck_Analyzer
# from OCC.Core.ShapeFix import ShapeFix_Shape
# from OCC.Core.ShapeAnalysis import ShapeAnalysis_Shell



from ..module import exchangeData
from ..module import  interactiveContext
from ..utils import  get_open_filename

DEFAULT_color = Quantity_Color(0.1, 0.2, 0.3, Quantity_TOC_RGB)  # default color

def removeShapes(viewer: OCCViewer.Viewer3d, ais_shapes: list):
    for s in ais_shapes:
        viewer.Context.Remove(s, False)
    pass
def displayShapes(viewer:OCCViewer.Viewer3d,ais_shapes:list):
    for s in ais_shapes:
        viewer.Context.Display(s,True)


def openModel(viewer: OCCViewer.Viewer3d) -> Tuple[str, TopoDS_Shape]:
    EXTENSIONS = "STP files(*.stp , *.step);;*.iges, *.igs;;*.stl"
    curr_dir = Path('').abspath().dirname()
    fname = get_open_filename(EXTENSIONS, curr_dir)
    if fname != '':
        return openModelWithFile(fname, viewer)

    return ('', None, None,None)


def openModelWithFile(fname: str, viewer: OCCViewer.Viewer3d):
    filepath = fname
    end_with = str(filepath).lower()
    # viewer.EraseAll()
    # viewer.hide_triedron()
    # viewer.display_triedron()
    compoundShape: TopoDS_Shape = None
    shape_list: List[TopoDS_Shape] = []
    ais_shapes: list = []
    time_start = time.time()
    if end_with.endswith(".step") or end_with.endswith("stp"):
        import_shape, assemble_relation_list, DumpToString = exchangeData.read_step_file_with_names_colors(
            filepath)
        time_end = time.time()
        # print('读取模型时间:', time_end - time_start, 's')
        time_start = time.time()
        for shpt_lbl_color in import_shape:
            label, c, property = import_shape[shpt_lbl_color]
            if isinstance(shpt_lbl_color, TopoDS_Face) or isinstance(shpt_lbl_color,
                                                                     TopoDS_Edge):  # 排除非solid和 edge
                continue
            # print("color:",c.Red(),c.Green(),c.Blue())
            c=DEFAULT_color
            return_shape = viewer.DisplayShape(shpt_lbl_color, color=Quantity_Color(c.Red(),
                                                                                    c.Green(),
                                                                                    c.Blue(),
                                                                                    Quantity_TOC_RGB),
                                               update=False)
            # viewer.Context.SetTransparency(return_shape[0], 0.3,True)
          

            # progressBar.Load_part_progressBar_auto()
            shape_list.append(return_shape[0].Shape())
            # shape_list.append(shpt_lbl_color)
            ais_shapes.append(return_shape[0])
        time_end = time.time()
        # print('显示模型时间:', time_end - time_start, 's')

        compoundShape = translation_Assemble(shape_list)
        viewer.FitAll()

    elif end_with.endswith(".iges") or end_with.endswith(".igs"):

        import_shape = exchangeData.read_iges_file(filepath)

        return_shape = viewer.DisplayShape(import_shape)
        shape_list.append(return_shape[0].Shape())
        ais_shapes.append(return_shape[0])
        compoundShape=translation_Assemble(shape_list)
        viewer.FitAll()

    elif end_with.endswith(".stl") or end_with.endswith(".stl"):

        import_shape = exchangeData.read_stl_file(filepath)

        return_shape = viewer.DisplayShape(import_shape)
        shape_list.append(return_shape[0].Shape())
        ais_shapes.append(return_shape[0])
        compoundShape=translation_Assemble(shape_list)
        viewer.FitAll()


    return fname, compoundShape, shape_list, ais_shapes
def fragment_shape(shapeList):
    if len(shapeList) == 0:
        return None
    if len(shapeList) == 1:
        return shapeList[0]
    fused_shape = shapeList[0]
    for shape in shapeList[1:]:
        fused_shape = BRepAlgoAPI_Fuse(fused_shape, shape).Shape()
    return fused_shape


def refreshWithColor(viewer: OCCViewer.Viewer3d, ais_shapes: list, rgb: Tuple[int, int, int]):
    r = round(rgb[0]/255, 2)
    g = round(rgb[1]/255, 2)
    b = round(rgb[2]/255, 2)
    customColor = Quantity_Color(r, g, b, Quantity_TOC_RGB)
    for s in ais_shapes:
        viewer.Context.Remove(s, True)
    for shape in ais_shapes:
        viewer.DisplayShape(shape.Shape(), color=customColor)
    viewer.Repaint()
    pass


def exportModel(a_shape: TopoDS_Shape, fileName: str,named=None) -> Tuple[int, str]:
    '''
    导出模型文件
    :return: 返回 (int,str)
    '''
    try:
        fpath=os.path.dirname(fileName)
        # 判断当前路径是否存在，没有则创建文件夹
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        format = os.path.splitext(fileName)[1]
        if(format == ".stp" or format == ".step"):
            if(named!=None):
                exchangeData.write_step_file_named(a_shape, fileName,named)
            else:
                exchangeData.write_step_file(a_shape, fileName)
        if(format == ".igs" or format == ".iges"):
            exchangeData.write_step_file(a_shape, fileName)
        if(format == ".stl" or format==".vstl"):
            exchangeData.write_stl_file(a_shape, fileName)
        return(1, "导出模型成功         ")
    except Exception as ex:
        traceback.print_exc()
        return (-1, "导出模型失败:"+str(ex))
    pass


def show_axis(viewer: OCCViewer.Viewer3d):
    viewer.display_triedron()

def show_axis_global(viewer: OCCViewer.Viewer3d,axis_length=1):
    '''
    生成一个局部坐标系坐标轴对象
    '''
    m_unit=1000
    center=(0,0,0)
    normal_dir=(0,0,1)

    
    f_center=gp_Pnt(center[0],center[1],center[2])
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])

    # x_dir=gp_Dir(x_dir[0],x_dir[1],x_dir[2])
        
    local_axes=gp_Ax2(f_center,f_dir)
    color_red = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB) 
    color_green=Quantity_Color(0.0, 1.0, 0.0, Quantity_TOC_RGB)
    color_blue=Quantity_Color(0.0, 0.0, 1.0, Quantity_TOC_RGB)

    color_black=Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)

    th_Axis=Geom_Axis2Placement(local_axes)
    p_trihedron=AIS_Trihedron(th_Axis)
    p_trihedron.SetDrawArrows(False)
    p_trihedron.SetSize(axis_length*m_unit)
    # p_trihedron.SetTextColor(color_black)
    p_trihedron.SetXAxisColor(color_red)
    p_trihedron.SetYAxisColor(color_green)
    p_trihedron.SetAxisColor(color_blue)
    
  

    # 获取 AIS_Trihedron 的 Drawer
    drawer = p_trihedron.Attributes()

    datum_aspect=drawer.DatumAspect()
  


    datum_aspect.SetAxisLength(axis_length*m_unit, axis_length*m_unit, axis_length*m_unit)




    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_XAxis,TCollection_ExtendedString(""))
    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_YAxis,TCollection_ExtendedString(""))
    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_ZAxis,TCollection_ExtendedString(""))
    drawer.SetDatumAspect(datum_aspect)
    

    
    

    # if(angel>0):
     # 创建变换矩阵，绕 Z 轴旋转,正负角度都可以
   
    viewer.Context.Display(p_trihedron,True)
    pass


def hide_axis(viewer: OCCViewer.Viewer3d):
    viewer.hide_triedron()


def clear_model(viewer: OCCViewer.Viewer3d):
    viewer.EraseAll()
    viewer.display_triedron()

    pass
def show_nf(viewer:OCCViewer.Viewer3d,pointList:list=[],color=Quantity_Color(0,0,0.8,Quantity_TOC_RGB)):
    '''
    显示电磁环境观察点
    '''
    #根据u,v,n三个方向的范围显示几何体，可以是线面或者体
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    color_blue=Quantity_Color(color[0], color[1], color[2], Quantity_TOC_RGB) 
    # color_blue=Quantity_Color(0.5, 1, 1, Quantity_TOC_RGB)
    ais_shape_list=[]
    m_unit=1000
 
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    # direction=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    n=len(pointList)
    for i in range(n):
            tObj=pointList[i]
            global_point=gp_Pnt(tObj[0]*m_unit,tObj[1]*m_unit,tObj[2]*m_unit)
            vertex=BRepBuilderAPI_MakeVertex(global_point)
            new_build.Add(New_Compound, vertex.Vertex())
    
    ais_shape=viewer.DisplayShape(New_Compound,color=color_blue,transparency=0.1)[0]
    
    viewer.Repaint()
    return ais_shape
    return ais_shape_list
        



    pass


def select_edge(mSelect: interactiveContext.InteractiveContext):
    mSelect.Action_select_edge()
    pass


def select_none(mSelect: interactiveContext.InteractiveContext):
    mSelect.Action_none()
    pass


def clear_selected(mSelect: interactiveContext.InteractiveContext):
    mSelect.clear_edges()
    pass


def translation_Assemble(shape_list=[]) -> TopoDS_Compound:  # 转换为装配体
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    for shape in shape_list:
        new_build.Add(New_Compound, shape)
    return New_Compound
def format_excange(sourceFile:str,targetFile:str):
    '''模型格式转换 使用cmd命令
    '''
    cmd_exchange = os.path.abspath(".")+"/cadExchanger/bin/ExchangerConv.exe"
    # print(cmd_exchange)

    cmd_exchange =cmd_exchange+ " -i " + sourceFile
    cmd_exchange =cmd_exchange+ " -e " + targetFile
    # os.system(cmd_exchange)
    try:
        result=subprocess.check_output(cmd_exchange, shell=True, universal_newlines=True)
        return(1,"格式转换成功      ")
    except subprocess.CalledProcessError as e:
        print("Command failed with return code", e.returncode)
        return(-1,"格式转换失败"+str(e))
        pass
def import_array(fname:str):
    '''导入天线阵列
    '''
    rList:list[tuple[float,float,float,int,int]]=[]
    m_unit=1000
    splitText="\t"
    i=0
    begin_tag="<!--Begin_arrangement-->"
    end_tag="<!--End_arrangement-->"
    inside_comment=False #是否包含在内容区 
    if fname != '':
        with open(fname, 'r',encoding="utf-8") as file:
            
            for line in file:
                line=line.strip()
                if(not inside_comment and line.startswith(begin_tag)):
                    inside_comment=True
                    continue
                if(line.startswith(end_tag)):
                    inside_comment=False
                if(inside_comment):
                    arr=line.split(splitText)
                    if(len(arr)!=6):
                        continue
                    # t=(float(arr[0])*m_unit,float(arr[1])*m_unit,float(arr[2])*m_unit,int(arr[3]),int(arr[4]))
                    t=(float(arr[1])*m_unit,float(arr[2])*m_unit,float(arr[3])*m_unit,int(arr[4]),int(arr[5]))
                    rList.append(t)
                    # print(t)
    return rList
    d_face=5
    m_unit=1000
    direction=gp_Dir(0,0,1)
    if(gpDir!=None):
        direction=gp_Dir(gpDir[0],gpDir[1],gpDir[2])
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    n=len(rList)
    
    for i in range(n):
            tObj=rList[i]
            gp=gp_Pnt(tObj[0]*m_unit,tObj[1]*m_unit,tObj[2]*m_unit)
            # vertex_builder = BRepBuilderAPI_MakeVertex(gp)
            # vertex = vertex_builder.Vertex()
            
            # new_build.Add(New_Compound, vertex)
            # box=BRepPrimAPI_MakeBox(gp,d,d,d).Shape()
            # # shape_list.append(box)
            # new_build.Add(New_Compound, box)
            face_builder = BRepBuilderAPI_MakeFace(gp_Pln(gp,direction),0,d_face,0,d_face)
            face=face_builder.Face()
            new_build.Add(New_Compound, face)
            

            
    # compShape=self.translation_Assemble(shape_list)
    # viewer.DisplayShape(New_Compound,color=Quantity_Color(0,0,1,Quantity_TOC_RGB))
    ais_shape=viewer.DisplayShape(New_Compound)[0]
    
    return rList,New_Compound,ais_shape

def local_transformed(shape:TopoDS_Shape,center,normal_dir):
        f_center=gp_Pnt(center[0],center[1],center[2])
        f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
        
        local_axes=gp_Ax2(f_center,f_dir)

        local_axes3=gp_Ax3(local_axes)

        transformation_matrix = gp_Trsf()
        local_axes3=gp_Ax3(local_axes)
        transformation_matrix.SetTransformation(local_axes3,gp_Ax3())
        # transformation_matrix.SetTransformation(local_axes3,gp_Ax3())

        transformation = BRepBuilderAPI_Transform(shape, transformation_matrix)
        transformed_shape = TopoDS_Shape(transformation.Shape())
        return transformed_shape
def local_global(center,normal_dir,angel,itemList_local):
    '''
    局部坐标转换为全局坐标
    '''
    f_center=gp_Pnt(center[0],center[1],center[2])
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])

    temp_axes=gp_Ax2(f_center,f_dir)
    x_dir_temp=temp_axes.XDirection()
    if(temp_axes.XDirection().Z()!=0 and  temp_axes.YDirection().Z()==0):
        if(temp_axes.XDirection().Z()>0):
            x_dir_temp=temp_axes.YDirection()
            x_dir_temp.Reverse()
        else:
            x_dir_temp=temp_axes.YDirection()
        
    local_axes=gp_Ax2(f_center,f_dir,x_dir_temp) #与坐标系同步，局部坐标系保持x轴向右侧
    local_axes3=gp_Ax3(local_axes)
    
    transformation_roate=gp_Trsf()

     # 创建变换矩阵，绕 Z 轴旋转
    radians = angel * (pi / 180)
    transformation_roate.SetRotation(local_axes.Axis(), radians)
    local_axes3.Transform(transformation_roate)

    
    transformation_matrix = gp_Trsf()
    transformation_matrix.SetTransformation(local_axes3, gp_Ax3())
    gList=[]
    n=len(itemList_local)
    for i in range(n):
        tObj=itemList_local[i]
        gp_local=gp_Pnt(tObj[0],tObj[1],tObj[2])
        global_point = gp_local.Transformed(transformation_matrix)
        t=(global_point.X(),global_point.Y(),global_point.Z(),tObj[3],tObj[4])
        gList.append(t)
    return gList
def local_global_points(center,normal_dir,angel,itemList_local):
    '''
    局部坐标转换为全局坐标
    '''
    m_unit=1000
    f_center=gp_Pnt(center[0]/m_unit,center[1]/m_unit,center[2]/m_unit)
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])

    temp_axes=gp_Ax2(f_center,f_dir)
    x_dir_temp=temp_axes.XDirection()
    if(temp_axes.XDirection().Z()!=0 and  temp_axes.YDirection().Z()==0):
        if(temp_axes.XDirection().Z()>0):
            x_dir_temp=temp_axes.YDirection()
            x_dir_temp.Reverse()
        else:
            x_dir_temp=temp_axes.YDirection()
        
    local_axes=gp_Ax2(f_center,f_dir,x_dir_temp)
    local_axes3=gp_Ax3(local_axes)
    
    transformation_roate=gp_Trsf()

     # 创建变换矩阵，绕 Z 轴旋转
    radians = angel * (pi / 180)
    transformation_roate.SetRotation(local_axes.Axis(), radians)
    local_axes3.Transform(transformation_roate)

    
    transformation_matrix = gp_Trsf()
    transformation_matrix.SetTransformation(local_axes3, gp_Ax3())
    gList=[]
    n=len(itemList_local)
    for i in range(n):
        tObj=itemList_local[i]
        gp_local=gp_Pnt(tObj[0],tObj[1],tObj[2])
        global_point = gp_local.Transformed(transformation_matrix)
        t=(global_point.X(),global_point.Y(),global_point.Z())
        gList.append(t)
    return gList

    pass
def get_local_trihedron(center,normal_dir,angel=90,axis_length=1):
    '''
    生成一个局部坐标系坐标轴对象
    '''
    m_unit=1000
    f_center=gp_Pnt(center[0],center[1],center[2]+10)
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])

    # x_dir=gp_Dir(x_dir[0],x_dir[1],x_dir[2])
    # 选择一个初始 x 轴方向向量，与法线方向不平行
    temp_axes=gp_Ax2(f_center,f_dir)
    x_dir_temp=temp_axes.XDirection()
    if(temp_axes.XDirection().Z()!=0 and  temp_axes.YDirection().Z()==0):
        if(temp_axes.XDirection().Z()>0):
            x_dir_temp=temp_axes.YDirection()
            x_dir_temp.Reverse()
        else:
            x_dir_temp=temp_axes.YDirection()

    # if(x_dir_temp.Z()<0):

    #     x_dir_temp.Reverse()

    local_axes=gp_Ax2(f_center,f_dir,x_dir_temp)

        
    
    x_dir=local_axes.XDirection()
    print("local-x direction",x_dir.X(),x_dir.Y(),x_dir.Z())

    # center_g=(0,0,0)
    # normal_dir_g=(0,0,1)

    
    # f_center_g=gp_Pnt(center[0],center[1],center[2]+10)
    # f_dir_g=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    # local_axes_g=gp_Ax2(f_center,f_dir)
    # angle_xy = local_axes.XDirection().Angle(local_axes_g.Direction())
    # print("angle_xy:",angle_xy)
    
    color_red = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB) 
    color_black=Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)

    th_Axis=Geom_Axis2Placement(local_axes)
    p_trihedron=AIS_Trihedron(th_Axis)
    
    p_trihedron.SetSize(axis_length*m_unit)
    p_trihedron.SetTextColor(color_black)
    p_trihedron.SetArrowColor(color_red)
    p_trihedron.SetXAxisColor(color_red)
    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_XAxis,TCollection_ExtendedString("U"))
    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_YAxis,TCollection_ExtendedString("V"))
    p_trihedron.SetLabel(Prs3d_DatumParts.Prs3d_DP_ZAxis,TCollection_ExtendedString("N"))
    
    

    # if(angel>0):
     # 创建变换矩阵，绕 Z 轴旋转,正负角度都可以
    radians = (angel) * (pi / 180)
    transformation = gp_Trsf()
    transformation.SetRotation(local_axes.Axis(), radians)
    p_trihedron.SetLocalTransformation(transformation)
    return p_trihedron
    viewer.Context.Display(p_trihedron,True)
    pass
def rotate_axis_byZ(center,normal_dir,angel):
    # 定义旋转角度（弧度）
    rotation_angle = 45

    f_center=gp_Pnt(center[0],center[1],center[2])
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
        
    local_axes=gp_Ax2(f_center,f_dir)

    # 创建变换矩阵，绕 Z 轴旋转
    transformation = gp_Trsf()
    transformation.SetRotation(local_axes.Axis(), rotation_angle)
    axes2=local_axes.Transformed(transformation)

    return axes2

    pass
def display_local_trihedron(viewer:OCCViewer.Viewer3d,trihedron):
    viewer.Context.Display(trihedron,True)
def hide_local_trihedron(viewer:OCCViewer.Viewer3d,trihedron):
    viewer.Context.Remove(trihedron,True)
def display_antenna_points(viewer:OCCViewer.Viewer3d,normal_dir,gList,size_pix=10):
    '''
    显示阵列天线,根据全局坐标直接显示
    '''
    d_pix=size_pix
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    direction=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    n=len(gList)
    for i in range(n):
            tObj=gList[i]
            global_point=gp_Pnt(tObj[0],tObj[1],tObj[2])
         
            face_builder = BRepBuilderAPI_MakeFace(gp_Pln(global_point,direction),0,d_pix,0,d_pix)
            face=face_builder.Face()
            new_build.Add(New_Compound, face)

    ais_shape=viewer.DisplayShape(New_Compound)[0]
    viewer.Repaint()
    return New_Compound,ais_shape
    pass
def display_antenna(viewer:OCCViewer.Viewer3d,normal_dir,gList,size_pix=5):
    '''
    显示阵列天线,根据全局坐标直接显示
    '''
    d_pix=size_pix
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    direction=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    temp_axes=gp_Ax2(gp_Pnt(0,0,0),direction)
    x_dir_temp=temp_axes.XDirection()
    if(temp_axes.XDirection().Z()!=0 and  temp_axes.YDirection().Z()==0):
        if(temp_axes.XDirection().Z()>0):
            x_dir_temp=temp_axes.YDirection()
            x_dir_temp.Reverse()
        else:
            x_dir_temp=temp_axes.YDirection()
    
    n=len(gList)
    for i in range(n):
            tObj=gList[i]
            global_point=gp_Pnt(tObj[0],tObj[1],tObj[2])
            
            plane_axis = gp_Ax3(global_point, direction, x_dir_temp)
         
            # face_builder = BRepBuilderAPI_MakeFace(gp_Pln(global_point,direction),0,d_pix,0,d_pix)
            face_builder = BRepBuilderAPI_MakeFace(gp_Pln(plane_axis),0,d_pix,0,d_pix)
            face=face_builder.Face()
            new_build.Add(New_Compound, face)

    ais_shape=viewer.DisplayShape(New_Compound)[0]
    viewer.Repaint()
    return New_Compound,ais_shape
    pass
def offset_antenna(rList,distance_offset):
    '''
    平移天线阵列，获取局部坐标系的坐标值，渲染时转换为全局坐标
    '''
    m_unit=1000
    d_x=distance_offset[0]*m_unit
    d_y=distance_offset[1]*m_unit
    d_z=distance_offset[2]*m_unit
    rListN=[]
    for item in rList:
        t=(item[0]+d_x,item[1]+d_y,item[2]+d_z,item[3],item[4])
        rListN.append(t)
    return rListN
    pass
def dislay_array(viewer: OCCViewer.Viewer3d,center,normal_dir,rList):
    pass
    '''显示天线阵列
    Returns:
    (shape,ais_shape,gList)
    '''
    # m_unit=1000
    d_pix=5
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape

    n=len(rList)

    direction=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    f_center=gp_Pnt(center[0],center[1],center[2])
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
    # x_dir=gp_Dir(x_d[0],x_d[1],x_d[2])
        
    local_axes=gp_Ax2(f_center,f_dir)

    transformation_matrix = gp_Trsf()
    local_axes3=gp_Ax3(local_axes)
    transformation_matrix.SetTransformation(local_axes3, gp_Ax3())

    gList=local_global(center,normal_dir,rList)
    n=len(gList)
    for i in range(n):
            tObj=gList[i]
            global_point=gp_Pnt(tObj[0],tObj[1],tObj[2])
         
            face_builder = BRepBuilderAPI_MakeFace(gp_Pln(global_point,direction),0,d_pix,0,d_pix)
            face=face_builder.Face()
            new_build.Add(New_Compound, face)
        
    ais_shape=viewer.DisplayShape(New_Compound)[0]
    viewer.Repaint()
    return New_Compound,ais_shape,gList
    # local_point = gp_Pnt(0, 0, 100)
    # global_point = local_point.Transformed(transformation_matrix)

    # box=BRepPrimAPI_MakeBox(local_axes,d_pix,d_pix,d_pix).Shape()
    # # box=BRepPrimAPI_MakeBox(gpnt,d_pix,d_pix,d_pix).Shape()
    # face=BRepBuilderAPI_MakeFace(gp_Pln(global_point,direction),0,d_pix,0,d_pix).Face()
    # # ais_shape=viewer.DisplayShape(box,color=Quantity_Color(0,0,1,Quantity_TOC_RGB))[0]
    # ais_shape=viewer.DisplayShape(face,color=Quantity_Color(0,0,1,Quantity_TOC_RGB))[0]
    
    # return face,ais_shape
    gList=[]
    for i in range(n):
            tObj=rList[i]
            gp_local=gp_Pnt(tObj[0]*m_unit,tObj[1]*m_unit,tObj[2]*m_unit)
            global_point = gp_local.Transformed(transformation_matrix)
            gList.append((global_point.X(),global_point.Y(),global_point.Z(),tObj[3],tObj[4]))

            # vertex_builder = BRepBuilderAPI_MakeVertex(gp)
            # vertex = vertex_builder.Vertex()
            
            # new_build.Add(New_Compound, vertex)
            # box=BRepPrimAPI_MakeBox(local_axes,d_pix,d_pix,d_pix).Shape()
            # shape_list.append(box)
            # new_build.Add(New_Compound, box)
            face_builder = BRepBuilderAPI_MakeFace(gp_Pln(global_point,direction),0,d_pix,0,d_pix)
            face=face_builder.Face()
            new_build.Add(New_Compound, face)
            

            
    # compShape=self.translation_Assemble(shape_list)
    # viewer.DisplayShape(New_Compound,color=Quantity_Color(0,0,1,Quantity_TOC_RGB))
    ais_shape=viewer.DisplayShape(New_Compound)[0]
    return New_Compound,ais_shape,gList

    pass


def move_shape(viewer: OCCViewer.Viewer3d,shape:TopoDS_Shape,center,normal_dir,distance_offset:tuple):
        f_center=gp_Pnt(center[0],center[1],center[2])
        f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
        
        local_axes=gp_Ax2(f_center,f_dir)


        d_x=distance_offset[0]*1000
        d_y=distance_offset[1]*1000
        d_z=distance_offset[2]*1000
      
        offset_x=gp_Vec(local_axes.XDirection())
        offset_x.Scale(d_x)
        # print("offsetX:",offset_x.X(),offset_x.Y(),offset_x.Z())

        offset_y=gp_Vec(local_axes.YDirection())
        offset_y.Scale(d_y)
        # print("offsetY:",offset_y.X(),offset_y.Y(),offset_y.Z())

        offset_z=gp_Vec(local_axes.Direction())
        offset_z.Scale(d_z)

        T_x=gp_Trsf()
        T_x.SetTranslation(offset_x)
        T_y=gp_Trsf()
        T_y.SetTranslation(offset_y)
        T_z=gp_Trsf()
        T_z.SetTranslation(offset_z)
        
        loc=TopLoc_Location(T_x.Multiplied(T_y).Multiplied(T_z))
        shape.Location(loc)
        ais_shape=viewer.DisplayShape(shape)[0]
        viewer.Repaint()
        return shape,ais_shape

def get_angel_xyz(center,normal_dir):
    # 创建全局坐标系
    dotNum=2
    global_ax3 = gp_Ax3()
    f_center=gp_Pnt(center[0],center[1],center[2])
    f_dir=gp_Dir(normal_dir[0],normal_dir[1],normal_dir[2])
        
    local_axes=gp_Ax2(f_center,f_dir)
    local_axes3=gp_Ax3(local_axes)


    # 计算夹角（弧度）
    angle_xy = global_ax3.Direction().Angle(local_axes3.Direction())
    angle_yz=global_ax3.XDirection().Angle(local_axes3.Direction())
    angel_xz=global_ax3.YDirection().Angle(local_axes3.Direction())
    # angel_xz=local_axes.Direction().Angle(global_ax3.YDirection())

    # 将弧度转换为度
    angle_degrees_x = degrees(angle_xy)
    angle_degrees_y=degrees(angle_yz)
    angle_degrees_z=degrees(angel_xz)

    angle_degrees_x=abs(angle_degrees_x) if abs(angle_degrees_x)<90 else 180-abs(angle_degrees_x)
    angle_degrees_y=abs(angle_degrees_y) if abs(angle_degrees_y)<90 else 180-abs(angle_degrees_y)
    angle_degrees_z=abs(angle_degrees_z) if abs(angle_degrees_z)<90 else 180-abs(angle_degrees_z)

    return (round(angle_degrees_x,2),round(angle_degrees_y,2),round(angle_degrees_z,2))

    pass
def get_face_num(shape:TopoDS_Shape):
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faceIndex=0
    while face_explorer.More():
        f = face_explorer.Current()
        faceIndex=faceIndex+1
        face_explorer.Next()
    return faceIndex
def display_face_color_normal(viewer:OCCViewer.Viewer3d,
                              shape:TopoDS_Shape,
                              frontColor=(78,156,0),
                              backColor=(194,65,22)):
    '''
    显示面法向颜色
    '''
    # face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    # while face_explorer.More():
    #     f = face_explorer.Current()
    #     viewer.DisplayShape(f,color=Quantity_Color(78/255,156/255,0,Quantity_TOC_RGB))
    #     face_explorer.Next()
    #     print("面方向",f.Orientation())
    # shape_center=get_shape_center(shape)
    # print("shape.center:",shape_center.X(),shape_center.Y(),shape_center.Z())
    ais_shape=AIS_ColoredShape(shape)
    drawer = ais_shape.Attributes()
    # 正反面分别着色
    face_aspect = Prs3d_ShadingAspect()
    fcolor=Quantity_Color(frontColor[0]/255,frontColor[1]/255,frontColor[2]/255,Quantity_TOC_RGB)
    bcolor=Quantity_Color(backColor[0]/255,backColor[1]/255,backColor[2]/255,Quantity_TOC_RGB)

    face_aspect.SetColor(fcolor,Aspect_TOFM_FRONT_SIDE)
    face_aspect.SetColor(bcolor,Aspect_TOFM_BACK_SIDE)
    
    drawer.SetShadingAspect(face_aspect)
    # for f in TopologyExplorer(shape).faces():

    #     # dir=get_face_dir(f)
    #     # center:gp_Pnt=get_face_center(f)
    #     # ray_end=center.Translated(gp_Vec(dir) * 100)
    #     # # vertex=BRepBuilderAPI_MakeVertex(ray_end)
    #     # # new_build.Add(New_Compound, vertex.Vertex())
        
    #     # classifier = BRepClass3d_SolidClassifier(shape, ray_end, 1e-6)
    #     # state = classifier.State()
    #     # if(state==TopAbs_OUT):
    #     #     # ais_shape.SetCustomColor(f,Quantity_Color(0,1,0,Quantity_TOC_RGB))
    #     #     pass
    #     # elif(state==TopAbs_IN):
    #     #     ais_shape.SetCustomColor(f,Quantity_Color(1,0,0,Quantity_TOC_RGB))

    #     # print("state",state,state==TopAbs_OUT)
        
    #     pass
    viewer.Context.Display(ais_shape,True)
    return ais_shape
def reverse_face(shape:TopoDS_Shape,faceId:int):
    '''
    反转面
    '''
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    c_faceId=0
    new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
    New_Compound = TopoDS_Compound()  # 定义一个复合体
    new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
    reshape = BRepTools_ReShape()
        
    while face_explorer.More():
        f =  topods_Face(face_explorer.Current())
        c_faceId=c_faceId+1
        if(c_faceId==faceId):
            # f=f.Complemented()
            # flipped_face = f.Complemented()
            # n_old=get_face_dir(f)
            # f.Reverse()
            # n_new=get_face_dir(flipped_face)
            # print("old orientation",f.Orientation())    
            # print("new orientation",flipped_face.Orientation())
            # print("old normal:",n_old.X(),n_old.Y(),n_old.Z())
            # print("new normal:",n_new.X(),n_new.Y(),n_new.Z())

            # 使用 BRepTools_ReShape 替换原始面
            
            # reshape.Replace(f, flipped_face)
            # f.Reverse()
            new_build.Add(New_Compound,f.Complemented())
        else:
            new_build.Add(New_Compound, f)
        face_explorer.Next()
    # new_shape=reshape.Apply(shape)
    
    return New_Compound
    
    return shape

   
    

def get_geoFile(shape:TopoDS_Shape,medium:int=0,mediumFaces:dict={}):
    '''
    使用occ的网格生成算法，生成geo文件
    '''
    try:
        startTime=time.time()
        con_str="_"
        m_unit=1000
        
        mesh = BRepMesh_IncrementalMesh(shape, 1000, False, 0.5, True)
        # mesh = BRepMesh_IncrementalMesh(shape, 0.0001)
        # #mesh.SetDeflection(0.05)
        mesh.Perform()

        # stl_exporter = StlAPI_Writer()
        # fileName="D:/ship0416.stl"
        
       
        # stl_exporter.Write(shape, fileName)
        # triangled_model=mesh.Shape()
        triangled_model=shape
        face_explorer = TopExp_Explorer(triangled_model, TopAbs_FACE)
        c_faceId=0
        tNum=0
        nodeDic={}
        triangleDic={}
        tIndex=0

        while face_explorer.More():
            f = face_explorer.Current()
            c_faceId=c_faceId+1 #面索引从1开始
            mediumIndex=medium+1
            mediumCoatIndex=0
            thickness=0
            if(mediumFaces!=None and mediumFaces.get(c_faceId)!=None):
                mediumIndex=mediumFaces[c_faceId][0]+1
                mediumCoatIndex=mediumFaces[c_faceId][1]+1
                thickness=mediumFaces[c_faceId][2]
            loc=TopLoc_Location()
            triangles:Poly_Triangulation=BRep_Tool.Triangulation(f,loc)
            if(triangles!=None):
                
                ts=triangles.NbTriangles()
                tList:Poly_Array1OfTriangle=triangles.Triangles()
                for t in tList:
                    tIndex=tIndex+1
                    c_t:Poly_Triangle=t
                    # print("V_index",c_t.Get())
                    t_k=tIndex
                    nt=c_t.Get()
                    t_v1=triangles.Node(nt[0])
                    t_v2=triangles.Node(nt[1])
                    t_v3=triangles.Node(nt[2])
                    #每个面，校验三角面的法线方向是否与面的法线方向一致，不一致则交换顺序
                    # p1=t_v1
                    # p2=t_v2
                    # p3=t_v3
                    # normal:gp_Dir = get_face_dir(f)
                    # # norm = normal.Magnitude()
                    # # face_n=None
                    # # if norm == 0:
                    # #     face_n=np.array([0.0, 0.0, 0.0])
                    # # face_n= np.array([normal.X(), normal.Y(), normal.Z()]) / norm
                    # # print("face normal",normal.X(),normal.Y(),normal.Z())
                    # face_n=np.array([normal.X(), normal.Y(), normal.Z()])
                    # # print("face-n",face_n)
                    
                    # vec1 = np.array([p2.X() - p1.X(), p2.Y() - p1.Y(), p2.Z() - p1.Z()])
                    # vec2 = np.array([p3.X() - p2.X(), p3.Y() - p2.Y(), p3.Z() - p2.Z()])
                    # triangle_normal = np.cross(vec1, vec2)
                    # triangle_normal /= np.linalg.norm(triangle_normal)
                    # if np.dot(face_n, triangle_normal) < 0:
                    #     # return p1, p3, p2  # 交换 p2 和 p3 的顺序
                    #     print("面{0}".format(c_faceId),"法线顺序不同，交换顺序")
                    # else:
                    #     print("面{0}".format(c_faceId),"法线顺序一致")
                        # return p1, p2, p3



                    # vec1 = np.array([p2.X() - p1.X(), p2.Y() - p1.Y(), p2.Z() - p1.Z()])
                    # vec2 = np.array([p3.X() - p2.X(), p3.Y() - p2.Y(), p3.Z() - p2.Z()])
                    # triangle_normal = np.cross(vec1, vec2)
                    # triangle_normal /= np.linalg.norm(triangle_normal)
                    
                    # if np.dot(face_normal, triangle_normal) < 0:
                    #     return p1, p3, p2  # 交换 p2 和 p3 的顺序
                    # else:
                    #     return p1, p2, p3
                    v1=con_str.join(map(str,(t_v1.X(),t_v1.Y(),t_v1.Z())))
                    v2=con_str.join(map(str,(t_v2.X(),t_v2.Y(),t_v2.Z())))
                    v3=con_str.join(map(str,(t_v3.X(),t_v3.Y(),t_v3.Z())))
                    triangleDic[t_k]=(v1,v2,v3,mediumIndex,mediumCoatIndex,thickness)

                tNum=tNum+ts
                nodes=triangles.NbNodes()
                for i  in range(nodes):
                    n:gp_Pnt=triangles.Node(i+1)
                    # print("node",n.X(),n.Y(),n.Z())
                    k=str(n.X())+con_str+str(n.Y())+con_str+str(n.Z())
                    
                    nodeDic[k]=n
                    


                # print("face",c_faceId,"triangles",ts,"nodes",nodes)
                pass
            # print("face",c_faceId)
            

            face_explorer.Next()
        nIndex=0
        for k in nodeDic:
            nIndex=nIndex+1
            p:gp_Pnt=nodeDic[k]
            nodeDic[k]=(nIndex,p.X()/m_unit,p.Y()/m_unit,p.Z()/m_unit)
        for t in triangleDic:
            v=triangleDic[t]
            v_1=nodeDic[v[0]][0]
            v_2=nodeDic[v[1]][0]
            v_3=nodeDic[v[2]][0]
            triangleDic[t]=(v_1,v_2,v_3,v[3],v[4],v[5]) #涂覆材料索引序号及涂覆厚度，暂时固定为0

        # print("total triangles",tNum,"triangleDic",len(triangleDic))
        # print(nodeDic,len(nodeDic))
        # print(triangleDic)
        # print("get geo file time:",time.time()-startTime)
        return(1,"success",(nodeDic,triangleDic))
    except Exception as ex:
        traceback.print_exc()

        return(-1,"get geo error "+str(ex),None)
    pass
def get_default_normal():
    global_ax3 = gp_Ax3()
    #获取全局坐标系的默认法向量
    n_dir=global_ax3.Direction()
    return (n_dir.X(),n_dir.Y(),n_dir.Z())
def get_face_center(face):
    surface = BRepAdaptor_Surface(face, True)
    # surface=BRep_Tool.Surface(face)

    # 获取面的参数范围
    # u1, u2, v1, v2 = surface.Bounds()
    u_min=surface.FirstUParameter()
    u_max=surface.LastUParameter()
    v_min=surface.FirstVParameter()
    v_max=surface.LastVParameter()


    # 计算参数范围的中心点
    u_center = (u_min + u_max) / 2.0
    v_center = (v_min + v_max) / 2.0

    # 计算中心点的三维坐标
    center_point = surface.Value(u_center, v_center)
    # print("face center",center_point.X(),center_point.Y(),center_point.Z())
    return center_point
def get_face_dir(face:TopoDS_Face):
    normal_dir=gp_Dir(0,0,1)
    x_dir=None
    
    #获取面的法线方向
    adaptor = BRepAdaptor_Surface(face)
    if adaptor.GetType()==GeomAbs_Plane:
        normal_dir=adaptor.Surface().Plane().Axis().Direction()
        x_dir=adaptor.Surface().Plane().XAxis().Direction()
        if(face.Orientation()==TopAbs_REVERSED):
            normal_dir.Reverse()
        return normal_dir
    if adaptor.GetType()==GeomAbs_SurfaceOfExtrusion:

        u_min=adaptor.FirstUParameter()
        u_max=adaptor.LastUParameter()
        v_min=adaptor.FirstVParameter()
        v_max=adaptor.LastVParameter()


        # 计算参数范围的中心点
        u_center = (u_min + u_max) / 2.0
        v_center = (v_min + v_max) / 2.0

        gp_center=gp_Pnt()
        d1u=gp_Vec()
        d1v=gp_Vec()

        adaptor.D1(u_center,v_center,gp_center,d1u,d1v)
        x_vec=d1u.Normalized()
        normal_dir=gp_Dir(d1u.Crossed(d1v))
        if(face.Orientation()==TopAbs_REVERSED):
            normal_dir.Reverse()
        x_dir=gp_Dir(x_vec)
    return normal_dir
def get_shape_center(shape:TopoDS_Shape):
    #获取包围盒中心
    bounding_box = Bnd_Box()
    brepbndlib_Add(shape, bounding_box)
    xmin, ymin, zmin, xmax, ymax, zmax = bounding_box.Get()
    center = gp_Pnt((xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2)
    return center
def set_transparency(viewer:OCCViewer.Viewer3d,shape,transpan:float):
    # 
    pass
def make_shell(modelViewer:OCCViewer.Viewer3d, shape:TopoDS_Compound,distance=10,thickness=10):
    '''
    生成壳体
    '''
    #获取最小包围盒
    bounding_box = Bnd_Box()
    brepbndlib_Add(shape, bounding_box)
    xmin, ymin, zmin, xmax, ymax, zmax = bounding_box.Get()
   
   # 在所有方向上扩展distance的距离
    xmin -= distance
    ymin -= distance
    zmin -= distance
    xmax += distance
    ymax += distance
    zmax += distance
    # 创建内部壳体
    box_inner = BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin), gp_Pnt(xmax, ymax, zmax)).Shape()
    # 创建外部壳体
    box_outer = BRepPrimAPI_MakeBox(gp_Pnt(xmin-thickness, ymin-thickness, zmin-thickness),
                                     gp_Pnt(xmax+thickness, ymax+thickness, zmax+thickness)).Shape()
    # 创建一个壳体
    shell = BRepAlgoAPI_Cut(box_outer, box_inner).Shape()
    ais_shape=modelViewer.DisplayShape(shell,color=DEFAULT_color)
    modelViewer.Context.SetTransparency(ais_shape[0], 0.6,True)
    return shell
def make_shell_domains(viewer:OCCViewer.Viewer3d,shape:TopoDS_Compound,
                       distance=20,thickness=10,
                       outer_offset_distance=10,
                       pml_used=True,
                       exf_used=True):
    #获取最小包围盒
    bounding_box = Bnd_Box()
    brepbndlib_Add(shape, bounding_box)
    xmin, ymin, zmin, xmax, ymax, zmax = bounding_box.Get()
   
    # 创建内部壳体（距离模型边界为distance）
    xmin_in = xmin - distance
    ymin_in = ymin - distance
    zmin_in = zmin - distance
    xmax_in = xmax + distance
    ymax_in = ymax + distance
    zmax_in = zmax + distance

    res_pml_param=(thickness,xmax_in,ymax_in,zmax_in,xmin_in,ymin_in,zmin_in)

    inner_shell = BRepPrimAPI_MakeBox(gp_Pnt(xmin_in, ymin_in, zmin_in),
                                    gp_Pnt(xmax_in, ymax_in, zmax_in)).Shape()

    # 创建外部壳体（将内部壳体向外偏移厚度）
    xmin_out = xmin_in - thickness
    ymin_out = ymin_in - thickness
    zmin_out = zmin_in - thickness
    xmax_out = xmax_in + thickness
    ymax_out = ymax_in + thickness
    zmax_out = zmax_in + thickness

    outer_shell = BRepPrimAPI_MakeBox(gp_Pnt(xmin_out, ymin_out, zmin_out),
                                    gp_Pnt(xmax_out, ymax_out, zmax_out)).Shape()

    # 创建一个壳体
    shell = BRepAlgoAPI_Cut(outer_shell, inner_shell).Shape() #弃用，因为改为多个子域直接创建

    # 创建外推面，距离模型 outer_offset_distance 单位
    xmin_offset = xmin - outer_offset_distance
    ymin_offset = ymin - outer_offset_distance
    zmin_offset = zmin - outer_offset_distance
    xmax_offset = xmax + outer_offset_distance
    ymax_offset = ymax + outer_offset_distance
    zmax_offset = zmax + outer_offset_distance

    offset_shape = BRepPrimAPI_MakeBox(gp_Pnt(xmin_offset, ymin_offset, zmin_offset),
                                    gp_Pnt(xmax_offset, ymax_offset, zmax_offset)).Shape()
    


    # 创建域1：外推面内部的区域，材料编号1007
    solidList=[]
    if(shape.ShapeType()==TopAbs_COMPOUND):
        #展开复合体
        shape_explorer = TopExp_Explorer(shape, TopAbs_SOLID)
        
        while shape_explorer.More():
            solid = shape_explorer.Current()
            solidList.append(solid)
            shape_explorer.Next()
    else:
        solidList.append(shape)
    fused_shape=fragment_shape(solidList)
   
    domain_1007 = BRepAlgoAPI_Cut(offset_shape,fused_shape).Shape()  # 外推面内部的全部区域

    # domain_1007=BRepAlgoAPI_Fuse(offset_shape, shape).Shape()
    #对于多实体的模型，不能直接使用Cut函数，使用splitter进行分割
    # 使用 BOPAlgo_Splitter 进行布尔减法
    # splitter = BOPAlgo_Splitter()
    # splitter.AddArgument(offset_shape)
    # splitter.AddTool(shape)
    # splitter.Perform()
    # # 获取布尔运算的结果形状
    # result_shape = splitter.Shape()
    # # 提取结果中的所有实体
    # result_solids = []
    # explorer = TopExp_Explorer(result_shape, TopAbs_SOLID)
    # while explorer.More():
    #     solid = explorer.Current()
    #     result_solids.append(solid)
    #     explorer.Next()

    # # 选择最大的实体作为空气域（外部壳体）
    # max_volume = 0
    # air_domain_solid = None
    # for solid in result_solids:
    #     props = GProp_GProps()
    #     brepgprop_VolumeProperties(solid, props)
    #     volume = props.Mass()
    #     if volume > max_volume:
    #         max_volume = volume
    #         air_domain_solid = solid
    # analyzer = BRepCheck_Analyzer(air_domain_solid)
    # if not analyzer.IsValid():
    #     print("警告：空气域实体无效，正在尝试修复。")
    #     fixer = ShapeFix_Solid(air_domain_solid)
    #     fixer.Perform()
    #     air_domain_solid = fixer.Solid()
    # fixer = ShapeFix_Shape(air_domain_solid)
    # fixer.Perform()
    # fixed_shape = fixer.Shape()


    # shell_analyzer = ShapeAnalysis_Shell()
    # shell_analyzer.LoadShells(fixed_shape)
    # if shell_analyzer.HasConnectedEdges():
    #     print("Shell has connected edges.")
    # mesh = BRepMesh_IncrementalMesh(fixed_shape, 0.1)
    # mesh.Perform()
    # if not mesh.IsDone():
    #     print("Meshing failed; geometry may have defects.")

    

    # domain_1007 = fixed_shape

    # 创建域2：外推面之外的区域，材料编号1008
    domain_1008 = BRepAlgoAPI_Cut(inner_shell, offset_shape).Shape()


    # 创建一个列表来存储16个体域
    domains_pml = []
    ais_shapes_pml = []

    domains_exf=[] #外推面的内外域
    ais_shapes_exf=[]

    # 1. 创建8个角的立方体
    corner_coords = [
        (xmin_out, ymin_out, zmin_out),
        (xmax_out - thickness, ymin_out, zmin_out),
        (xmin_out, ymax_out - thickness, zmin_out),
        (xmax_out - thickness, ymax_out - thickness, zmin_out),
        (xmin_out, ymin_out, zmax_out - thickness),
        (xmax_out - thickness, ymin_out, zmax_out - thickness),
        (xmin_out, ymax_out - thickness, zmax_out - thickness),
        (xmax_out - thickness, ymax_out - thickness, zmax_out - thickness)
    ]
    for x, y, z in corner_coords:
        cube = BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), thickness, thickness, thickness).Shape()
        domains_pml.append(cube)

    # 2. 创建剩余的8个长方体
    # 计算内部壳体的尺寸
    dx_in = xmax_in - xmin_in
    dy_in = ymax_in - ymin_in
    dz_in = zmax_in - zmin_in

    # 定义长方体的位置和尺寸
    rect_prisms = [
        # X方向长方体（上下）
        (xmin_out + thickness, ymin_out, zmin_out, dx_in, thickness, thickness),  # 底部前面
        (xmin_out + thickness, ymax_out - thickness, zmin_out, dx_in, thickness, thickness),  # 底部后面
        (xmin_out + thickness, ymin_out, zmax_out - thickness, dx_in, thickness, thickness),  # 顶部前面
        (xmin_out + thickness, ymax_out - thickness, zmax_out - thickness, dx_in, thickness, thickness),  # 顶部后面

        # Y方向长方体（左右）
        (xmin_out, ymin_out + thickness, zmin_out, thickness, dy_in, thickness),  # 左侧前面
        (xmax_out - thickness, ymin_out + thickness, zmin_out, thickness, dy_in, thickness),  # 右侧前面
        (xmin_out, ymin_out + thickness, zmax_out - thickness, thickness, dy_in, thickness),  # 左侧后面
        (xmax_out - thickness, ymin_out + thickness, zmax_out - thickness, thickness, dy_in, thickness),  # 右侧后面

        # Z方向长方体（前后）
        (xmin_out, ymin_out, zmin_out + thickness, thickness, thickness, dz_in),  # 左下侧
        (xmax_out - thickness, ymin_out, zmin_out + thickness, thickness, thickness, dz_in),  # 右下侧
        (xmin_out, ymax_out - thickness, zmin_out + thickness, thickness, thickness, dz_in),  # 左上侧
        (xmax_out - thickness, ymax_out - thickness, zmin_out + thickness, thickness, thickness, dz_in),  # 右上侧
    ]

    # 只取前8个长方体
    for prism in rect_prisms:
        x, y, z, dx, dy, dz = prism
        box = BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()
        domains_pml.append(box)

    # 3. 创建6个面的长方体
    face_prisms = [
        # 前后面板（X方向）
        (xmin_out + thickness, ymin_out + thickness, zmin_out,
        xmax_out - xmin_out - 2 * thickness, ymax_out - ymin_out - 2 * thickness, thickness),
        (xmin_out + thickness, ymin_out + thickness, zmax_out - thickness,
        xmax_out - xmin_out - 2 * thickness, ymax_out - ymin_out - 2 * thickness, thickness),

        # 左右面板（Y方向）
        (xmin_out, ymin_out + thickness, zmin_out + thickness,
        thickness, ymax_out - ymin_out - 2 * thickness, zmax_out - zmin_out - 2 * thickness),
        (xmax_out - thickness, ymin_out + thickness, zmin_out + thickness,
        thickness, ymax_out - ymin_out - 2 * thickness, zmax_out - zmin_out - 2 * thickness),

        # 上下面板（Z方向）
        (xmin_out + thickness, ymin_out, zmin_out + thickness,
        xmax_out - xmin_out - 2 * thickness, thickness, zmax_out - zmin_out - 2 * thickness),
        (xmin_out + thickness, ymax_out - thickness, zmin_out + thickness,
        xmax_out - xmin_out - 2 * thickness, thickness, zmax_out - zmin_out - 2 * thickness)
    ]

    for prism in face_prisms:
        x, y, z, dx, dy, dz = prism
        box = BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()
        domains_pml.append(box)

    # 为每个体域设置不同的颜色
    colors = ['RED', 'GREEN', 'YELLOW', 'CYAN', 'MAGENTA', 'ORANGE', 'WHITE', 'GRAY',
            'BROWN', 'PINK', 'VIOLET', 'LIME', 'NAVY', 'TEAL', 'OLIVE', 'MAROON', 'BLACK', 'GOLD']
    if pml_used:
        for i, domain in enumerate(domains_pml):
            ais_shape=viewer.DisplayShape(domain, color=DEFAULT_color)
            ais_shapes_pml.append(ais_shape[0])
    else:
        domains_pml = []
    #显示域1
    if exf_used:
        ais_shape_1007=viewer.DisplayShape(domain_1007, color=DEFAULT_color,update=False)
        domains_exf.append(domain_1007)
        ais_shapes_exf.append(ais_shape_1007[0])

        # 显示域2
        ais_shape_1008=viewer.DisplayShape(domain_1008, color=DEFAULT_color, update=False)
        domains_exf.append(domain_1008)
        ais_shapes_exf.append(ais_shape_1008[0])
    exportModel(domain_1007,"D:/exf1.stp")
    # exportModel(domain_1008,"D:/exf2.stp")

    return domains_pml,ais_shapes_pml,domains_exf,ais_shapes_exf,res_pml_param