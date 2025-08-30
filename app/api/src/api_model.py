import os
import subprocess
import threading
import time
from typing import List, Set, Dict, Tuple
from path import Path
from PyQt5 import QtWidgets

from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Edge, TopoDS_Shape, TopoDS_Builder, TopoDS_Compound
from OCC.Core.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                             TopAbs_SHELL, TopAbs_SOLID)




from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display import OCCViewer
from OCC.Core.TopExp import topexp, TopExp_Explorer


from ..module import exchangeData
from ..module import  interactiveContext
from ..utils import  get_open_filename

def removeShapes(viewer: OCCViewer.Viewer3d, ais_shapes: list):
    for s in ais_shapes:
        viewer.Context.Remove(s, True)
    pass


def openModel(viewer: OCCViewer.Viewer3d) -> Tuple[str, TopoDS_Shape]:
    EXTENSIONS = "STP files(*.stp , *.step);;*.iges, *.igs;;*.stl"
    curr_dir = Path('').abspath().dirname()
    fname = get_open_filename(EXTENSIONS, curr_dir)
    if fname != '':
        return openModelWithFile(fname, viewer)

    return ('', None, None)


def openModelWithFile(fname: str, viewer: OCCViewer.Viewer3d):
    filepath = fname
    end_with = str(filepath).lower()
    # viewer.EraseAll()
    # viewer.hide_triedron()
    # viewer.display_triedron()
    compoundShape: TopoDS_Shape = None
    shape_list: List[TopoDS_Shape] = []
    ais_shapes: list = []
    if end_with.endswith(".step") or end_with.endswith("stp"):
        import_shape, assemble_relation_list, DumpToString = exchangeData.read_step_file_with_names_colors(
            filepath)
        for shpt_lbl_color in import_shape:
            label, c, property = import_shape[shpt_lbl_color]
            if isinstance(shpt_lbl_color, TopoDS_Face) or isinstance(shpt_lbl_color,
                                                                     TopoDS_Edge):  # 排除非solid和 edge
                continue
            # print("color:",c.Red(),c.Green(),c.Blue(),)
            return_shape = viewer.DisplayShape(shpt_lbl_color, color=Quantity_Color(c.Red(),
                                                                                    c.Green(),
                                                                                    c.Blue(),
                                                                                    Quantity_TOC_RGB),
                                               update=True)

            # progressBar.Load_part_progressBar_auto()
            shape_list.append(return_shape[0].Shape())
            ais_shapes.append(return_shape[0])

        compoundShape = translation_Assemble(shape_list)
        viewer.FitAll()

    elif end_with.endswith(".iges") or end_with.endswith(".igs"):

        import_shape = exchangeData.read_iges_file(filepath)

        return_shape = viewer.DisplayShape(import_shape)

    elif end_with.endswith(".stl") or end_with.endswith(".stl"):

        import_shape = exchangeData.read_stl_file(filepath)

        return_shape = viewer.DisplayShape(import_shape)

    return fname, compoundShape, shape_list, ais_shapes


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


def exportModel(a_shape: TopoDS_Shape, fileName: str) -> Tuple[int, str]:
    '''
    导出模型文件
    :return: 返回 (int,str)
    '''
    try:
        format = os.path.splitext(fileName)[1]
        if(format == ".stp" or format == ".step"):
            exchangeData.write_step_file(a_shape, fileName)
        if(format == ".igs" or format == ".iges"):
            exchangeData.write_step_file(a_shape, fileName)
        if(format == ".stl"):
            exchangeData.write_stl_file(a_shape, fileName)
        return(1, "导出模型成功         ")
    except Exception as ex:
        return (-1, "导出模型失败:"+str(ex))
    pass


def show_axis(viewer: OCCViewer.Viewer3d):
    viewer.display_triedron()


def hide_axis(viewer: OCCViewer.Viewer3d):
    viewer.hide_triedron()


def clear_model(viewer: OCCViewer.Viewer3d):
    viewer.EraseAll()

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