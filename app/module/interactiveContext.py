# -*- coding: utf-8 -*-
import logging,datetime
import os
from typing import List,Tuple
from OCC.Display.OCCViewer import Viewer3d
from OCC.Core.AIS import AIS_Shape,AIS_Point
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QAction
from OCC.Core.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                             TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
                               TopAbs_COMPSOLID, TopAbs_FORWARD, TopAbs_REVERSED)

from OCC.Core.TopExp import topexp,TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Edge,TopoDS_Face,TopoDS_Vertex,topods
from OCC.Core.BRep import BRep_Tool
from app.mixins import ComponentMixin
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Copy
import qtawesome as qta
from OCC.Core.Quantity import (Quantity_Color, Quantity_TOC_RGB, Quantity_NOC_WHITE,
                               Quantity_NOC_BLACK, Quantity_NOC_BLUE1,
                               Quantity_NOC_CYAN1, Quantity_NOC_RED,
                               Quantity_NOC_GREEN, Quantity_NOC_ORANGE, Quantity_NOC_YELLOW)
from OCC.Core.Standard import Standard_Type
from OCC.Core.Geom import Geom_Surface,Geom_Plane,Geom_Axis2Placement

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import (GeomAbs_Plane,GeomAbs_Cone,GeomAbs_Cylinder,GeomAbs_BezierCurve,
GeomAbs_BezierSurface,GeomAbs_BSplineCurve,GeomAbs_BSplineSurface,GeomAbs_Circle,GeomAbs_Cone,GeomAbs_Cylinder,
GeomAbs_OffsetSurface,GeomAbs_Plane,GeomAbs_SurfaceOfExtrusion,GeomAbs_SurfaceOfRevolution,GeomAbs_Torus,GeomAbs_Sphere)
from OCC.Core.gp import gp_Pnt, gp_Dir,gp_Vec, gp_Ax2,gp_Ax3,gp_Trsf,gp_Lin,gp_Pln
from OCC.Core.AIS import AIS_Axis
from OCC.Core.AIS import AIS_Trihedron
from OCC.Core.V3d import V3d_Xpos, V3d_Ypos, V3d_Zpos
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeVertex
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.Adaptor3d import Adaptor3d_Surface
from OCC.Core.AIS import AIS_InteractiveContext,AIS_Shape_SelectionMode
from OCC.Core.Prs3d import Prs3d_TypeOfHighlight
from OCC.Core.SelectMgr import SelectMgr_SelectableObject, SelectMgr_Selection, SelectMgr_SequenceOfOwner
from OCC.Core.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Edge, TopoDS_Shape, TopoDS_Builder, TopoDS_Compound
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.BRepLProp import  BRepLProp_SLProps
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.TopTools import TopTools_IndexedMapOfShape

class InteractiveContext(QWidget, ComponentMixin):
    sigPointClicked=QtCore.pyqtSignal(int,tuple)#(edgepoint(p1,p2),edgeId
    sigLineClicked=QtCore.pyqtSignal(tuple,int)#（edgepoint(p1,p2),edgeId
    sigFaceClicked=QtCore.pyqtSignal(int,bool)#edgeId
    sigFaceLengthUV=QtCore.pyqtSignal(float,float)#(u_length,v_length)
    sigFaceChoosed=QtCore.pyqtSignal(tuple,tuple,int)#(x,y,z),(0,0,1) (center,direction)
    sigBodyClicked=QtCore.pyqtSignal(int,bool)#(shapeId,isSelcted)
    EDGETIP="EDGE"
    FACETIP="FACE"
    
    def __init__(self, parent=None,viewer:Viewer3d=None):
        super(InteractiveContext, self).__init__(parent)
        self.parent = parent
        self.select_filter = None #默认触发选中面的事件
        self.viewer:Viewer3d=viewer
        self._shapesSelectedDic={}#key-id,value:(topods_shape,ais_shape)
        self._shapeList:list[TopoDS_Shape]=[]#当前UI显示的shape集合
        self._shapeList_ais:list[AIS_Shape]=[]#当前UI显示的shape集合
        self._solidSelectedDic={}#key-id,value:(topods_shape,ais_shape)
        self._pointSelected=[]#选中的点
        self._points={}#key-（x,y,z),value:pointId
        # self._compShape=None
        # self._aisCompShape=None
        # self._showArray=False
        self._local_axis=(None,None,None,None)#(center,normal_dir,local_axes,ais_thredo)
        self._color_selected=Quantity_Color(0.7,0.7,0,Quantity_TOC_RGB)
        self._color_default=Quantity_Color(0.1,0.2,0.3,Quantity_TOC_RGB)
        self.hide()

    def clear(self):
        if(self._shapesSelectedDic is not None):
            for shapeObj in self._shapesSelectedDic.values():
                self.viewer.Context.Remove(shapeObj[1], True)
            self._shapesSelectedDic.clear()
        # if(self._shapeList is not None):
        #     self._shapeList.clear()
    def setOpacity(self,opacity:float):
        for ais_shape in self._shapeList_ais:
            self.viewer.Context.SetTransparency(ais_shape[0], opacity,False)
        self.viewer.Repaint()

    def initShape(self,shapeList,ais_shapes=[]):
        '''将模型的shape数组来传入当前交互对象
        '''
        self._shapeList_ais.clear()
        self._shapeList.clear()
        for shape in shapeList:
            self._shapeList.append(shape)
        
        for ais_shape in ais_shapes:
            self._shapeList_ais.append((ais_shape,True))
        pointIndex=0
        tstart=datetime.datetime.now()
        
        for shape in self._shapeList:
            vertex_map = TopTools_IndexedMapOfShape()
            vertex_explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
            while vertex_explorer.More():
                v = vertex_explorer.Current()
                point=BRep_Tool.Pnt(v)
                if(not str(point.Coord()) in self._points):
                    self._points[str(point.Coord())]=pointIndex
                    pointIndex=pointIndex+1
                vertex_explorer.Next()
        tend=datetime.datetime.now()
        #输出耗时计算，秒为单位
        # print("initPoint:",(tend-tstart)/1000)
        # print("initShape:",tend-tstart)
    def addShapes(self,shapeList,ais_shape=[]):
        startIndex=len(self._shapeList)
        for shape in shapeList:
            self._shapeList.append(shape)
        for ais_shape in ais_shape:
            self._shapeList_ais.append((ais_shape,True))
        endIndex=len(self._shapeList)
        #返回索引值列表，用于后续整体显示/隐藏
        idList=[i for i in range(startIndex,endIndex)]
        return idList #返回shapeId索引范围，。用于后续整体显示/隐藏
    def removeShapes(self,shapeList,ais_shape=[]):
        try:
            for shape in shapeList:
                self._shapeList.remove(shape)
            for ais_shape in ais_shape:
                self._shapeList_ais.remove(ais_shape)
        except Exception as e:
            print(e)
            pass
    def removeShapes_idList(self,idList:List[int]):
        try:
            del self._shapeList[idList[0]:idList[0]+len(idList)]
            del self._shapeList_ais[idList[0]:idList[0]+len(idList)]
        except Exception as e:
            print(e)
            pass
    def clearFaceSelected(self):
        for k in self._shapesSelectedDic:    
            self.viewer.Context.Remove(self._shapesSelectedDic[k][1], True)
        self._shapesSelectedDic.clear()
        pass
            
    def initFaceSelected(self,faceId_selected):
        c_faceId=0
        isFind=False
        for shape in self._shapeList:
            if(isFind):break
            face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while face_explorer.More():
                f = face_explorer.Current()
                if(c_faceId==faceId_selected):
                    isFind=True
                    # print("find same face",c_faceId)
                    self.clear()
                    k=self.FACETIP+str(c_faceId)
                    show_shape = self.viewer.DisplayShape(f, color=self._color_selected)
                    self._shapesSelectedDic[k]=(f,show_shape[0])
                    self.viewer.Repaint()
                    # u_len,v_len=self.get_face_length_uv(f)
                    # self.sigFaceLengthUV.emit(u_len,v_len)
                    break
                c_faceId=c_faceId+1
                face_explorer.Next()
        if(not isFind):c_faceId=-1
        return c_faceId

        pass
    def clearSolidSelected(self):
        keys_to_delete = [key for key in self._solidSelectedDic if key!=-1]

        # 删除不符合条件的键
        for key in keys_to_delete:
            self.viewer.Context.SetColor(self._solidSelectedDic[key][1],self._color_default,True)
            del self._solidSelectedDic[key]

    def initSolidSelected(self,solidId_selected):
        c_solidId=0
        isFind=False
        for shape in self._shapeList:
            if(isFind):break
            if(c_solidId==solidId_selected):
                isFind=True
                ais_shapeItem=self._shapeList_ais[c_solidId]
                self.viewer.Context.SetColor(ais_shapeItem[0],self._color_selected,True)
                self._solidSelectedDic[c_solidId]=(shape,ais_shapeItem[0])
                break
            c_solidId=c_solidId+1
        if(not isFind):
            c_solidId=-1
        else:
            keys_to_delete = [key for key in self._solidSelectedDic if key!=c_solidId]

            # 删除不符合条件的键
            for key in keys_to_delete:
                self.viewer.Context.SetColor(self._solidSelectedDic[key][1],self._color_default,True)
                del self._solidSelectedDic[key]
        return c_solidId
            

    # def reverse_face(self,faceId):
    #     '''根据face的序号反转该face的方向
    #     '''
    #     face=self.get_face_selected(faceId)
    #     if(face is not None):
    #         face.Reverse()
    #         self._shapeList[faceId]=face
    #         # face.Orientation(TopAbs_REVERSED)
    #         # self.viewer.Context.Remove(self._shapesSelectedDic[self.FACETIP+str(faceId)][1], True)
    #         # del self._shapesSelectedDic[self.FACETIP+str(faceId)]
    #         # k=self.FACETIP+str(faceId)
    #         # show_shape = self.viewer.DisplayShape(face, color=Quantity_NOC_GREEN)
    #         # self._shapesSelectedDic[k]=(face,show_shape[0])
    #         self.viewer.Repaint()
    #     pass

    def remove_edge(self,edgeId):
        '''根据edge的编号删除之前的edge
        '''
        k=self.EDGETIP+str(edgeId)
        if(k in self._shapesSelectedDic):
            self.viewer.Context.Remove(self._shapesSelectedDic[k][1], True)
            del self._shapesSelectedDic[k]  
        pass
    def point_clicked(self, shp, *kwargs):
        """ This function is called whenever a point is selected
        """
        try:
            if self.select_filter != 0:
                return
            if(len(shp)<1):
                return
            #清除已选中的点
            for point in self._pointSelected:
                self.viewer.Context.Remove(point[1], True)
            self._pointSelected.clear()
            pointSelected:TopoDS_Vertex=shp[0]
            #获取点坐标
            point=BRep_Tool.Pnt(pointSelected)
            point=point.Coord()
            # print("point:",point[0],point[1],point[2])
            #高亮显示选中的点
            show_shape = self.viewer.DisplayShape(pointSelected, color=Quantity_NOC_RED)  
            pointId=-1
            if(str(point) in self._points):
                pointId=self._points[str(point)]
            self._pointSelected.append((pointSelected,show_shape[0]))  
            self.sigPointClicked.emit(pointId,point)#-1表示点的编号
            #获取顶点编号


            
            pass
        except Exception as e:
            print(e)
            pass

    def line_clicked(self, shp, *kwargs):

        """ This function is called whenever a line is selected
        """
        try:
            if(len(shp)<1):
                return
            if self.select_filter != 1:
                return
            if self.parent.modifiers != QtCore.Qt.ControlModifier:
                return
            selectedShape=shp[0]

            # copyShape=BRepBuilderAPI_Copy(selectedShape).Shape()
            edgePoint=self.getEdgePoint(selectedShape)
            edgeId=self.getEdgeId(selectedShape)
            k=self.EDGETIP+str(edgeId)
            self.sigLineClicked.emit(edgePoint,edgeId)
            
            if(k in self._shapesSelectedDic):
                self.viewer.Context.Remove(self._shapesSelectedDic[k][1], True)
                del self._shapesSelectedDic[k]  
            else:
                show_shape = self.viewer.DisplayShape(selectedShape, color=self._color_selected)
                self._shapesSelectedDic[k]=(selectedShape,show_shape[0])
    
                        
        except Exception as e:
            print(e)
            pass

    def face_clicked(self, shp, *kwargs):
        """ This function is called whenever a line is selected
        """
        try:
            dotNum=2
            if self.select_filter != 2:
                return
            if self.parent.modifiers != QtCore.Qt.KeyboardModifier.ControlModifier:
                return
            if (len(shp)<1):
                return
            # self.clear()#一次只选中一个面
            selectedShape=shp[0]
            #获取选择面的宽度和高度
            u_length,v_length=self.get_face_length_uv(selectedShape)
        


            # isCurved=self.is_face_curved(selectedShape)
            # print("face is curved:",isCurved)
            

            
            faceId=self.getFaceId(selectedShape)
            k=self.FACETIP+str(faceId)
            # chooseFaceId=faceId
            isSelcted=True

            if(k in self._shapesSelectedDic):
                self.viewer.Context.Remove(self._shapesSelectedDic[k][1], True)
                del self._shapesSelectedDic[k]
                chooseFaceId=-1
                isSelcted=False
            else:
                self.clear()
                show_shape = self.viewer.DisplayShape(selectedShape, color=self._color_selected)
                self._shapesSelectedDic[k]=(selectedShape,show_shape[0])

            # face_center:gp_Pnt=self.get_face_center(selectedShape)
            # # print("center",face_center.X(),face_center.Y(),face_center.Z())
            # normal_dir,x_dir=self.get_face_dir(selectedShape)
            # orientation=selectedShape.Orientation()
            # if orientation == TopAbs_FORWARD:
            #     print(k,"面的方向是正向")
            # elif orientation == TopAbs_REVERSED:
            #     print(k,"面的方向是反向")
            # else:
            #     print("未知的方向")
            # print("origin",face_center.X(),face_center.Y(),face_center.Z())
            # self.display_local_axis(selectedShape)
            # self.display_local_axis_old(selectedShape)
            self.sigFaceClicked.emit(faceId,isSelcted)
            self.sigFaceLengthUV.emit(u_length,v_length)
            # self.sigFaceChoosed.emit(
            #                          (round(face_center.X(),2),round(face_center.Y(),2),round(face_center.Z(),2)),
            #                          (round(normal_dir.X(),2),round(normal_dir.Y(),2),round(normal_dir.Z(),2)),
            #                         #  (x_dir.X(),x_dir.Y(),x_dir.Z()),
            #                          chooseFaceId)
        except Exception as e:
            print(e)
            pass

    def body_clicked(self, shp, *kwargs):
        """ This function is called whenever a body is selected
        """
        try:
            if self.select_filter == 3:
                selectedShape=shp[0]
                shapeId=self.getShapeId(selectedShape)
                if(shapeId<0):
                    # self.viewer.DisplayShape(selectedShape, color=self._color_selected)
                    raise Exception("shapeId<0")
                ais_shapeItem=self._shapeList_ais[shapeId]

                #目前支持单选，所以只能选中一个
                
                #均重置为默认色
                
                    

                if(self._solidSelectedDic.get(shapeId) is not None):#已经选中
                    self.viewer.Context.SetColor(ais_shapeItem[0],self._color_default,True)
                    del self._solidSelectedDic[shapeId]
                    self.sigBodyClicked.emit(shapeId,False)
                    # show_shape = self.viewer.DisplayShape(selectedShape,color=self._color_default)
                    # self._shapeList_ais[shapeId]=(show_shape[0],True)
                else:#设置为选中的颜色
                    # show_shape = self.viewer.DisplayShape(selectedShape, color=self._color_selected)
                    # self._shapeList_ais[shapeId]=(show_shape[0],True)
                    self.viewer.Context.SetColor(ais_shapeItem[0],self._color_selected,True)
                    self._solidSelectedDic[shapeId]=(selectedShape,ais_shapeItem[0])
                    self.sigBodyClicked.emit(shapeId,True)

                keys_to_delete = [key for key in self._solidSelectedDic if key!=shapeId]

                # 删除不符合条件的键
                for key in keys_to_delete:
                    self.viewer.Context.SetColor(self._solidSelectedDic[key][1],self._color_default,True)
                    del self._solidSelectedDic[key]
                

        
                # show_shape = self.viewer.DisplayShape(selectedShape, color=self._color_selected)
                # self.viewer.Context.Erase(show_shape[0], True)
                # for shape in shp:
                #     pass
        except Exception as e:
            print(e)
            pass
    def showHide(self,shapeId):
        try:
            if self.select_filter == 3:

                ais_shapeItem=self._shapeList_ais[shapeId]
                if(ais_shapeItem[1]):
                    self.viewer.Context.Erase(ais_shapeItem[0], True)
                    self._shapeList_ais[shapeId]=(ais_shapeItem[0],False)
                else:
                    self.viewer.Context.Display(ais_shapeItem[0], False)
                    self._shapeList_ais[shapeId]=(ais_shapeItem[0],True)
        except Exception as e:
            print(e)
            pass
    def showHide_idList(self,idList:List[int],visible):
        try:
            for shapeId in idList:
                ais_shapeItem=self._shapeList_ais[shapeId]
                if(not visible):
                    self.viewer.Context.Erase(ais_shapeItem[0], False)
                    self._shapeList_ais[shapeId]=(ais_shapeItem[0],False)
                else:
                    self.viewer.Context.Display(ais_shapeItem[0], False)
                    self._shapeList_ais[shapeId]=(ais_shapeItem[0],True)
            
        except Exception as e:
            print(e)
            pass
    def showHidePML(self):
        pass
    def showHideEXF(self):
        pass
    def showAll(self):
        try:
            for i in range(len(self._shapeList_ais)):
                ais_shapeItem=self._shapeList_ais[i]
                if(not ais_shapeItem[1]):
                    self.viewer.Context.Display(ais_shapeItem[0], False)
                    self._shapeList_ais[i]=(ais_shapeItem[0],True)
            # for ais_shapeItem in self._shapeList_ais:
            #     if(not ais_shapeItem[1]):
            #         self.viewer.Context.Display(ais_shapeItem[0], True)
            #         ais_shapeItem=(ais_shapeItem[0],True)
        except Exception as e:
            print(e)
            pass
    def repaint(self):
        self.viewer.Repaint()
    def get_face_length_uv(self,face:TopoDS_Face):
        '''获取面的宽度和高度
        '''
        # 获取面的UV参数范围
        umin, umax, vmin, vmax = breptools_UVBounds(face)

        # 创建一个面适配器
        surface_adaptor = BRepAdaptor_Surface(face)

        # 在UV参数范围内取样多个点以提高精度
        num_samples = 10
        u_values = [umin + i * (umax - umin) / (num_samples - 1) for i in range(num_samples)]
        v_values = [vmin + i * (vmax - vmin) / (num_samples - 1) for i in range(num_samples)]

        # 收集U方向和V方向的点
        u_points = [surface_adaptor.Value(u, vmin) for u in u_values]
        v_points = [surface_adaptor.Value(umin, v) for v in v_values]

        # 计算U方向的长度（宽度）
        u_length = sum(u_points[i].Distance(u_points[i+1]) for i in range(len(u_points)-1))

        # 计算V方向的长度（高度）
        v_length = sum(v_points[i].Distance(v_points[i+1]) for i in range(len(v_points)-1))

        print(f"宽度（U方向长度）: {u_length}")
        print(f"高度（V方向长度）: {v_length}")
        return (u_length,v_length)


    def Action_none(self):
        pass

    def Action_select_point(self):
  
        self.viewer.SetSelectionModeNeutral()
        self.viewer.SetSelectionMode(TopAbs_VERTEX)
        self.select_filter = 0

    def Action_select_edge(self):

        self.viewer.SetSelectionModeNeutral()
        self.viewer.SetSelectionMode(TopAbs_EDGE)

        self.select_filter = 1

    def Action_select_face(self):
        # s=datetime.datetime.now()
        # self._showArray=not self._showArray
        # if(self._compShape!=None):
        #     self.viewer.Context.Remove(self._aisCompShape,True)
        #     if(self._showArray):
        #         self._aisCompShape=self.viewer.DisplayShape(self._compShape)[0]
        #     # self.viewer.DisplayShape(self._compShape)
        # else:
        #     self.write_box_stp(100)
        # print("write stp:",datetime.datetime.now()-s)
    
        self.viewer.SetSelectionModeNeutral()
        self.viewer.SetSelectionMode(TopAbs_FACE)
        # c:AIS_InteractiveContext=self.viewer.Context
        # c.Activate(AIS_Shape_SelectionMode(TopAbs_FACE),True)
        # c.HighlightStyle( Prs3d_TypeOfHighlight.Prs3d_TypeOfHighlight_Selected)
        # custome_selecteMgr=SelectMgr_SelectableObject()
        # custome_selecteMgr.HilightOwnerWithColor()
        # c.SelectionManager().Activate()
        
        # print(type(c))
        
        self.select_filter = 2

    def Action_select_body(self):
     
        self.viewer.SetSelectionModeNeutral()
        self.viewer.SetSelectionMode(TopAbs_SOLID)
        self.select_filter = 3
    def Action_draw_circle(self):
        #弹出设置圆形包围盒窗体，设置面/半径/圆心点坐标，确定后在模型空间画一个圆形
        # new_dlg=DrawCicle_dlg(parent=self.parent)
        # new_dlg.show()

        pass


    def getEdgePoint(self,edge):
        
        mVer1 = topexp.FirstVertex(edge, True)  # 起点
        mVer2 = topexp.LastVertex(edge, True)  # 终点
        P1 = BRep_Tool.Pnt(mVer1)  # 转换为pnt数据
        P2 = BRep_Tool.Pnt(mVer2)  # 转换为pnt数据
        P1 = P1.Coord()
        P2 = P2.Coord()
        return (P1,P2)
    def getEdgeId(self,edge):
        '''根据edge的shape获取该edge在模型中的序号，该序号每次一致且唯一
        '''
        isFind=False
        edgeId=0
        for shape in self._shapeList:

            if(isFind):break
            edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
            while edge_explorer.More():
                e = edge_explorer.Current()
                if(e.IsSame(edge)):
                    isFind=True
                    break
                edgeId=edgeId+1
                edge_explorer.Next()
        if(not isFind):edgeId=-1
        return edgeId

        pass
        

    def getEdgePoints(self, edges):
        edgeList = []
        for edge in edges:
            vertex_list = []
            mVer1 = topexp.FirstVertex(edge, True)  # 起点
            mVer2 = topexp.LastVertex(edge, True)  # 终点
            P1 = BRep_Tool.Pnt(mVer1)  # 转换为pnt数据
            P2 = BRep_Tool.Pnt(mVer2)  # 转换为pnt数据
            P1 = P1.Coord()
            P2 = P2.Coord()
            vertex_list.append({"start": P1,"end":P2})
            # vertex_list.append({"end": P2})
            vertex_list.append(edge)
            edgeList.append(vertex_list)
        return edgeList
    def getPointId(self,pvertex:TopoDS_Vertex):
        pointId=0
        isFind=False
        timeStart=datetime.datetime.now()
        for shape in self._shapeList:
            if(isFind):break
            vertex_explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
            while vertex_explorer.More():
                v = vertex_explorer.Current()
                if(v.IsSame(pvertex)):
                    isFind=True
                    break
                pointId=pointId+1
                vertex_explorer.Next()
        if(not isFind):pointId=-1
        #记录时间间隔
        timeEnd=datetime.datetime.now()
        print("getPointId:",timeEnd-timeStart)
        return pointId
    def getFaceId(self,face:TopoDS_Face):
        '''根据face的shape获取shape在整个模型中的遍历序号
        '''
        faceId=0
        isFind=False
        for shape in self._shapeList:
            if(isFind):break
            face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while face_explorer.More():
                f = face_explorer.Current()
                if(face.IsSame(f)):
                    isFind=True
                    # print("find same face",faceId)
                    break
                faceId=faceId+1
                face_explorer.Next()
        if(not isFind):faceId=-1
        return faceId
        pass
    def getShapeId(self,shapeSelected:TopoDS_Shape):
        shapeId=0
        isFind=False
        for shape in self._shapeList:

            if(isFind):break
            #判断shape是否topods_compound,是则需要展开
            if(shape.ShapeType()==TopAbs_COMPOUND):
                compound_explorer = TopExp_Explorer(shape, TopAbs_SOLID)
                while compound_explorer.More():
                    solid = compound_explorer.Current()
                    if(solid.IsSame(shapeSelected)):
                        isFind=True
                        break
                    compound_explorer.Next()
                if(isFind):break #跳出外层循环，避免shapeId计数错误
                
            
            else:
                if(shape.IsSame(shapeSelected)):
                    isFind=True
                    break
            shapeId=shapeId+1
            
        if(not isFind):shapeId=-1
        return shapeId

    def initEdgeSelected(self,edgeIdList:List[int]):
        '''根据边的序号查找到所有的边shape,用于初始化选中的边
        '''
        eIndex=0
        if(self._shapeList is None or edgeIdList is None):
            return
        for shape in self._shapeList:
            edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
            while edge_explorer.More():
                shape = edge_explorer.Current()
                if(eIndex in edgeIdList):
                    k=self.EDGETIP+str(eIndex)
                    show_shape = self.viewer.DisplayShape(shape, color=Quantity_NOC_RED)
                    self._shapesSelectedDic[k]=(shape,show_shape[0])
                eIndex=eIndex+1
                edge_explorer.Next()

        pass

    def is_face_curved(self,face):

        # 使用 BRepAdaptor_Surface 对象适配几何体
        adaptor = BRepAdaptor_Surface(face)

        # 获取几何体的类型
        surface_type = adaptor.GetType()
        print("surface_type:",surface_type,surface_type == GeomAbs_Plane)
       
        return surface_type != GeomAbs_Plane
    
    def display_local_axis(self,face:TopoDS_Face):
        center:gp_Pnt=self.get_face_center(face)
        normal_dir,x_dir=self.get_face_dir(face)
        local_axes=gp_Ax2(center,normal_dir,x_dir)

        # X 轴：(1, 0, 0)
        # Y 轴：(0, 1, 0)
        # Z 轴：(0, 0, 1)
  

   

        #显示坐标系
        color_red = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB) 
        color_black=Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)

        th_Axis=Geom_Axis2Placement(local_axes)
        p_trihedron=AIS_Trihedron(th_Axis)
        p_trihedron.SetSize(1000)
        p_trihedron.SetTextColor(color_black)
        p_trihedron.SetArrowColor(color_red)
        p_trihedron.SetXAxisColor(color_red)

        if(self._local_axis[3] is not None):
            self.viewer.Context.Remove(self._local_axis[3], True)
        self.viewer.Context.Display(p_trihedron,True)
        self._local_axis=(center,normal_dir,local_axes,p_trihedron)

        pass
    def move_shape(self, shape:TopoDS_Shape,distance_offset:tuple):
        d_x=distance_offset(0)
        d_y=distance_offset(1)
        d_z=distance_offset(2)
        local_axes:gp_Ax2=self._local_axis[2]
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
        ais_shape=self.viewer.DisplayShape(shape)[0]
        return ais_shape

        pass
    def display_local_axis_old(self,face:TopoDS_Face):
        '''
        显示面的局部坐标系
        '''
        #根据face创建一个局部坐标系，坐标系的原点在face的中心点，坐标轴与face的法向量平行
        #获取面的中心点
        face_center:gp_Pnt=self.get_face_center(face)
        print("origin",face_center.X(),face_center.Y(),face_center.Z())
        
        normal_dir=gp_Dir(0,0,1)
        #获取面的法线方向
        adaptor = BRepAdaptor_Surface(face)
        if adaptor.GetType()==GeomAbs_Plane:
            normal_dir=adaptor.Surface().Plane().Axis().Direction()
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
            normal_dir=gp_Dir(d1u.Crossed(d1v))
            # normal_dir.SetY(-normal_dir.Y())
        


    

        # normal_direction = gp_Dir(0, 0, 1)

        # surface_type = adaptor.GetType()
        # u=0.5
        # v=0.5

        # if surface_type == GeomAbs_Plane:
        #     normal_direction = adaptor.Plane().Axis().Direction()
        # elif surface_type == GeomAbs_Cylinder:
        #     normal_direction = adaptor.Cylinder().Axis().Direction()
        # elif surface_type == GeomAbs_Cone:
        #     normal_direction = adaptor.Cone().Axis().Direction()
        # elif surface_type == GeomAbs_Sphere:
        #     normal_direction = adaptor.Sphere().Position().Direction()
        # elif surface_type == GeomAbs_Torus:
        #     normal_direction = adaptor.Torus().Position().Direction()
        # elif surface_type == GeomAbs_BezierSurface or surface_type == GeomAbs_BSplineSurface:
        #     # 对于 Bézier 曲面和 B 样条曲面，可以使用数值逼近获取法线，类似之前的示例
        #     pass
        # elif surface_type == GeomAbs_SurfaceOfRevolution:
        #     normal_direction = adaptor.Surface().DN(u, v, 1, 0).Crossed(adaptor.Surface().DN(u, v, 0, 1)).Normalized()
        # elif surface_type == GeomAbs_SurfaceOfExtrusion:
        #     # 对于挤压曲面，可以通过其方向向量获取法线
        #     normal_direction = adaptor.Direction()
        # elif surface_type == GeomAbs_OffsetSurface:
        #     # 对于偏移曲面，可以使用原始曲面的法线
        #     normal_direction = adaptor.BasisSurface().DN(u, v, 1, 0).Crossed(adaptor.BasisSurface().DN(u, v, 0, 1)).Normalized()

        # # 输出法线方向
        # print(normal_direction)
        normal_dir.SetY(-normal_dir.Y())
        print("法线adaptor:",normal_dir.X(),normal_dir.Y(),normal_dir.Z())

        print("面方向:",face.Orientation())
        orientation=face.Orientation()
        if orientation == TopAbs_FORWARD:
            print("面的方向是正向")
        elif orientation == TopAbs_REVERSED:
            print("面的方向是反向")
        else:
            print("未知的方向")

       
        dir=gp_Dir(0,0,1)
        normal_dir.SetY(-normal_dir.Y())
        local_axes=gp_Ax2(face_center,normal_dir)

        #显示坐标系
        color_red = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB) 
        color_black=Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)

        th_Axis=Geom_Axis2Placement(local_axes)
        p_trihedron=AIS_Trihedron(th_Axis)
        p_trihedron.SetSize(500)
        p_trihedron.SetTextColor(color_black)
        p_trihedron.SetArrowColor(color_red)
        p_trihedron.SetXAxisColor(color_red)
    
        self.viewer.Context.Display(p_trihedron,True)

        #显示一个box
        dLen=20
        dOffset=50

        # box=BRepPrimAPI_MakeBox(local_axes,dLen,dLen,dLen).Shape()
        box=BRepPrimAPI_MakeBox(gp_Pnt(0,0,0),dLen,dLen,dLen).Shape()
        self.viewer.DisplayShape(box,color=Quantity_NOC_YELLOW)

        
        offset_x=gp_Vec(local_axes.XDirection())
        offset_x.Scale(dOffset)
        print("offsetX:",offset_x.X(),offset_x.Y(),offset_x.Z())

        offset_y=gp_Vec(local_axes.YDirection())
        offset_y.Scale(dOffset)
        print("offsetY:",offset_y.X(),offset_y.Y(),offset_y.Z())

        offset_z=gp_Vec(local_axes.Direction())
        offset_z.Scale(dOffset)
        print("offsetZ:",offset_z.X(),offset_z.Y(),offset_z.Z())


        # boxS=BRepPrimAPI_MakeBox(local_axes.Location().Translated(gp),dLen,dLen,dLen).Shape()
        # self.viewer.DisplayShape(boxS,color=Quantity_NOC_RED)
        boxS=TopoDS_Shape(box)

        T_x=gp_Trsf()
        T_x.SetTranslation(offset_x)
        T_y=gp_Trsf()
        T_y.SetTranslation(offset_y)
        T_z=gp_Trsf()
        T_z.SetTranslation(offset_z)
        
        loc=TopLoc_Location(T_x.Multiplied(T_y).Multiplied(T_z))
        boxS.Location(loc)

        self.viewer.DisplayShape(boxS,color=Quantity_NOC_RED)

        origin_box=boxS.Location().Transformation().TranslationPart()
        print("origin_box:",origin_box.X(),origin_box.Y(),origin_box.Z())

        local_point = gp_Pnt(534.25, 71.25, 150)
        transformation_matrix = gp_Trsf()
        local_axes3=gp_Ax3(local_axes)
        transformation_matrix.SetTransformation(local_axes3, gp_Ax3())
        global_point = local_point.Transformed(transformation_matrix)

        print("局部坐标系中的点:", local_point.X(), local_point.Y(), local_point.Z())
        print("全局坐标系中的点:", global_point.X(), global_point.Y(), global_point.Z())
        

    

        return

        # #设置box在法线方向偏移
        # T=gp_Trsf()
        # # T.SetTranslation(gp_Vec(100,0,0))
        # T.SetTranslationPart(gp_Vec(0,0,100))
        # T.SetTransformation()

        boxS=TopoDS_Shape(box)
        loc=TopLoc_Location(T3)
        boxS.Location(loc)
        self.viewer.DisplayShape(boxS,color=Quantity_NOC_RED)




   
        
        
    
        # boxS=TopoDS_Shape(box)
        
        # # transform = BRepBuilderAPI_Transform(boxS, T)
        # # transform.Perform(boxS)
        # loc=TopLoc_Location(T)
        # # boxS.Location(loc)
        # boxS.Move(loc)
        # self.viewer.DisplayShape(boxS,color=Quantity_NOC_RED)

       

        pass
    def get_face_dir(self,face):

        normal_dir=gp_Dir(0,0,1)
        x_dir=None
        # slprops = BRepLProp_SLProps(1,1e-6)
        # slprops.SetSurface(BRepAdaptor_Surface(face))
        # slprops.SetParameters(u,v)

        # normal_dir=slprops.Normal()
        # x_dir=slprops.D1U

        # return normal_dir

        
        #获取面的法线方向
        adaptor = BRepAdaptor_Surface(face)
        if adaptor.GetType()==GeomAbs_Plane:
            normal_dir=adaptor.Surface().Plane().Axis().Direction()
            x_dir=adaptor.Surface().Plane().XAxis().Direction()
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
            x_dir=gp_Dir(x_vec)
            if(face.Orientation()==TopAbs_REVERSED):
                normal_dir.Reverse()
        
        # print("x_dir",x_dir.X(),x_dir.Y(),x_dir.Z())
        # print("normal_dir",normal_dir.X(),normal_dir.Y(),normal_dir.Z())
        # if(normal_dir.Z()<0):
        #     print("反向")
        # else:
        #     print("正向")
        return normal_dir,x_dir
        return normal_dir
    def get_face_selected(self,faceId):
        '''根据face的序号获取该face的shape
        '''
        c_faceId=0
        isFind=False
        for shape in self._shapeList:
            if(isFind):break
            face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while face_explorer.More():
                f = face_explorer.Current()
                if(c_faceId==faceId):
                    isFind=True
                    return f
                c_faceId=c_faceId+1
                face_explorer.Next()
        if(not isFind):return None
        pass

    def get_face_center(self,face):
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
    def write_box_stp(self,n):
        writer=STEPControl_Writer()
        d=2
        shape_list=[]
        new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
        New_Compound = TopoDS_Compound()  # 定义一个复合体
        new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
        
        for x in range(n):
            for y in range(n):
                gp=gp_Pnt(x*(d+2),y*(d+2),-100)
                # vertex_builder = BRepBuilderAPI_MakeVertex(gp)
                # vertex = vertex_builder.Vertex()
                
                # new_build.Add(New_Compound, vertex)
                # box=BRepPrimAPI_MakeBox(gp,d,d,d).Shape()
                # # shape_list.append(box)
                # new_build.Add(New_Compound, box)
                face_builder = BRepBuilderAPI_MakeFace(gp_Pln(gp,gp_Dir(0,0,1)),0,d,0,d)
                face=face_builder.Face()
                new_build.Add(New_Compound, face)
                

                
        # compShape=self.translation_Assemble(shape_list)
        self._compShape=New_Compound
        self._aisCompShape=self.viewer.DisplayShape(New_Compound)[0]
        
        # self.timer_display=QtCore.QTimer()
        # self.timer_display.timeout.connect(lambda:self.delay_display(New_Compound))
        # self.timer_display.start(200)
     
        # writer.Transfer(New_Compound,STEPControl_AsIs)
            
        # step_file_path = "d:/output_model.step"
        # 将模型写入STEP文件
        # writer.Write(step_file_path)
 

    def translation_Assemble(self,shape_list=[]) -> TopoDS_Compound:  # 转换为装配体
        new_build = TopoDS_Builder()  # 建立一个TopoDS_Builder()
        New_Compound = TopoDS_Compound()  # 定义一个复合体
        new_build.MakeCompound(New_Compound)  # 生成一个复合体DopoDS_shape
        for shape in shape_list:
            new_build.Add(New_Compound, shape)
        return New_Compound
  