# -*- coding: utf-8 -*-
# 四面体 (单位：mm)

from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_MakeSolid,
)
from OCC.Core.TopoDS import topods_Shell
from OCC.Core.ShapeFix import ShapeFix_Solid
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_NOC_RED, Quantity_NOC_BLUE1
from OCC.Display.SimpleGui import init_display

# ----------------------------
# 1) 定义4个顶点（换算：m → mm）
# ----------------------------
scale = 1000.0

P1 = gp_Pnt(-0.0038*scale,  0.0000*scale,  0.0003*scale)
P2 = gp_Pnt(-0.0030*scale,  0.0005*scale, -0.0003*scale)
P3 = gp_Pnt(-0.0030*scale, -0.0005*scale, -0.0003*scale)
P4 = gp_Pnt(-0.0030*scale,  0.0000*scale,  0.0000*scale)

# ----------------------------
# 2) 生成三角面
# ----------------------------
def make_triangle_face(A, B, C):
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(A); poly.Add(B); poly.Add(C); poly.Close()
    return BRepBuilderAPI_MakeFace(poly.Wire()).Face()

f123 = make_triangle_face(P1, P2, P3)
f124 = make_triangle_face(P1, P2, P4)
f134 = make_triangle_face(P1, P3, P4)
f234 = make_triangle_face(P2, P3, P4)

# ----------------------------
# 3) Sewing → Shell → Solid
# ----------------------------
sew = BRepBuilderAPI_Sewing(1e-7)
for f in (f123, f124, f134, f234):
    sew.Add(f)
sew.Perform()
shell = topods_Shell(sew.SewedShape())

solid = BRepBuilderAPI_MakeSolid(shell).Solid()
fixer = ShapeFix_Solid(solid)
fixer.Perform()
solid_fixed = fixer.Solid()

# ----------------------------
# 4) 检查实体有效性
# ----------------------------
analyzer = BRepCheck_Analyzer(solid_fixed)
print("Solid is valid:", analyzer.IsValid())

# ----------------------------
# 5) 显示
# ----------------------------
display, start_display, add_menu, add_function_to_menu = init_display()
ais = AIS_Shape(solid_fixed)
display.Context.Display(ais, True)
display.Context.SetTransparency(ais, 0.3, True)

display.FitAll()
start_display()
