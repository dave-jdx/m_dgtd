from PyQt5 import QtWidgets
QtWidgets.QMessageBox.about(None,"test","m1")
from netgen.occ import *
QtWidgets.QMessageBox.about(None,"test","m2")
# from netgen.libngpy import *
from ngsolve import Mesh
QtWidgets.QMessageBox.about(None,"test","m3")
import typing


def mesh_generate(geo):  # 网格划分，提供几何对象，返回mesh对象，用于可视化显示
    mesh = Mesh(geo.GenerateMesh())
    return mesh
def mesh_generate_shape():
    # shape=TopAbs_ShapeEnum.SHELL(shape)
    box = Box(Pnt(0,0,0), Pnt(1,1,1))
    cyl = Cylinder(Pnt(1,0.5,0.5), X, r=0.3, h=0.5)
    fused = box+cyl
    # geo=Compound([shape])s
    # geo=OCCGeometry(shape)
    # geo.shape=shape
    # face=SHELL(shape)
    # geo=OCCGeometry(face)
    # geo.SetFaceMeshsize()
    geo=OCCGeometry("temp/array.stp")

    return geo,geo.shape
    # print(len(geo.shape.faces))
    # for f in geo.shape.faces:
    #     print(f.center,f.edges[0])
    targetFile = "temp/meshTarget.stl"
    geo.SetFaceMeshsize(1,5)
    mesh = Mesh(geo.GenerateMesh(maxh=10))

    # mesh.Refine()
    mesh.ngmesh.Export(targetFile, "STL Format")
    return targetFile, mesh
def mesh_generate_shapeList(shape: typing.List[TopoDS_Shape]):
    geo=OCCGeometry(shape)
    targetFile = "temp/meshTarget.stl"
    mesh = Mesh(geo.GenerateMesh())
    mesh.ngmesh.Export(targetFile, "STL Format")
    return targetFile, mesh

def mesh_generate_stl(sourceFile, edge):  # 对模型文件进行网格划分,返回生成的stl文件【相对路径+文件名】
    '''传入待划分网格的文件名以及选中的edge信息，进行网格划分后返回stl文件路径、
    Args:
        sourceFile:模型文件名【含路径】
        edge:netgen中的edge对象，需要包含start/end信息
    Returns:
        targetFile:stl文件名【相对路径】
        mesh:ngsolve.com.Mesh 可用于直接访问的mesh对象
    '''
    # print(edge)
    targetFile = "temp/meshTarget.stl"
    geo = OCCGeometry(sourceFile)
    mesh = Mesh(geo.GenerateMesh())
    mesh.ngmesh.Export(targetFile, "STL Format")
    return targetFile, mesh


def mesh_export(mesh, targetFile, format):  # 网格数据导出
    '''传入mesh对象，导出指定格式的文件
    Args:
        mesh：ngsolve.comp.Mesh对象
        targetFile:导出网格文件名【含路径】
        format:导出文件格式 如 "STL Format"/"Gmsh Format"
    Returns:
        result:1:成功 -1:失败
    '''
    mesh.ngmesh.Export(targetFile, format)


# geo = OCCGeometry("temp/s1.stp")
# mesh = mesh_generate(geo)
# mesh_export(mesh, "temp/mesh/test2.msh", "Gmsh Format")
# targetFile,mesh = mesh_generate_stl("temp/s1.stp",{})
# print(targetFile)
# mesh_generate_shape()