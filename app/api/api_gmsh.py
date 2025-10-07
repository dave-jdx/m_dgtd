import os,time,traceback,sys,io,json
import gmsh
import numpy as np
from PyQt5 import QtWidgets, QtCore
from typing import Dict, List, Tuple

def createMesh(strJson:str,logFileName=None):  # 网格数据导出

    try:
        # fnameList=["d:/exf1.stp","d:/cube.stp","d:/cube_named.stp"]
        # fnameList=fnameList[2:]
        # fnameList=["d:/ship.stp"]
        # fnameList=fnameList[1:]
        param_json=json.loads(strJson)
        fnameList=param_json["fnameList"]
        options=param_json["options"]
        localSize=param_json["localSize"]
        face_bnd=param_json.get("face_bnd",{})
        
        vtkFileName=param_json["vtkFileName"]
        mshFileName=param_json["mshFileName"]
        sizeH=options["maxh"]*1000
        minH=options["minh"]*1000
        maxH=options["maxh"]*1000
        smootions_steps=options["smoothing_steps"]
        optimize_tetrahedra=int(options["optimize_tetrahedra"])
        alogrithm_3d=options["3dAlogrithm"]
        alogrithm_3d_v=1
        if(alogrithm_3d==0):
            alogrithm_3d_v=1
        elif(alogrithm_3d==1):
            alogrithm_3d_v=4
        elif(alogrithm_3d==2):
            alogrithm_3d_v=10
        elif(alogrithm_3d==3):
            alogrithm_3d_v=7

        

    
        gmsh.initialize()
        gmsh.clear()
     
        
        #gmsh不输出info信息
        gmsh.option.setNumber("General.Terminal", 1)
    
        mediumDic={}#tag:mdiumIndex
        boundaryDic={} #tag:boundaryIndex
        #从文件列表读取stp文件
        modelTagDic={}
        is_first=True
       
        timeStart=time.time()
        shell_entities=[]
        for i,fname in enumerate(fnameList):
            imported_entities=gmsh.model.occ.importShapes(fname)
            print(f"Imported耗时:{time.time()-timeStart}")
            timeStart=time.time()
            gmsh.model.occ.synchronize()
            if(is_first):#只取第一个文件的体域
                volumes = [entity for entity in imported_entities if entity[0] == 3]
                modelTags=[v[1] for v in volumes]
                #列表转字典 key是tag value是index
                modelTagDic=dict(zip(modelTags,[i]*len(modelTags)))
                is_first=False
            else:
                shells = [entity for entity in imported_entities if entity[0] == 2]
                shell_entities.extend(shells)

    
        surfaces = gmsh.model.getEntities(2)
        # surfaces_nodes_befor=get_face_nodes(surfaces)
        surfaces_before=get_face_info(surfaces)
        faceId_used={}#记录已经使用的面编号
        for (dim, tag) in surfaces:
            # 获取实体的名称
            name = gmsh.model.getEntityName(dim, tag)
            # boundaryDic[tag]=tag-1
            
            

            for k in face_bnd:
                v=face_bnd[k]
                com=v["com"]
                area=v["area"]
                area_diff = abs(area - surfaces_before[(dim,tag)]['area'])
                com_dist = np.linalg.norm(np.array(com) - np.array(surfaces_before[(dim,tag)]['com']))
                if area_diff < 1e-6 and com_dist < 1e-6:
                    faceId=k
                    boundaryDic[tag]=(faceId,surfaces_before[(dim,tag)],v["bndType"]) #记录原来的面编号，输出时使用
        

        face_origin_now_pairs={} #原编号，新编号
        entities = gmsh.model.getEntities(dim=3)
        # desired_entities = [e for e in entities if e[1] in modelTags]

        # if(alogrithm_3d_v==4 or alogrithm_3d_v==7):
        #     desired_entities=entities

        
        out_dim_tags, out_tags_map=gmsh.model.occ.fragment(entities, shell_entities,
                                                            removeObject=True, removeTool=True)
        gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()


    
        
        volumes=gmsh.model.getEntities(3)
        s_total_index=1
        

        
                
        for(etype,tag) in volumes:
            
            name=gmsh.model.getEntityName(etype,tag)
            # print(f"Found solid in gmsh with tag: {name}-{tag}")
            if(name!=""):
                selected_volume=(etype,tag)
                if(name.startswith("Shapes/Medium")):
                    mediumDic[tag]=name.replace("Shapes/Medium","")
                else:
                    mediumDic[tag]=-1
                gmsh.model.addPhysicalGroup(3,[selected_volume[1]],tag,name)
                
          
        boundaryDic_new={}

        surfaces_new = gmsh.model.getEntities(dim=2)
        surfaces_after=get_face_info(surfaces_new)
        tag_new_dic={}
        for k in face_bnd.keys():
            #为新的面赋值entityName和物理组
            for (dim, tag) in surfaces_new:
    
                v_after=surfaces_after[(dim,tag)]
                v_before=face_bnd[k]
                area_diff = abs(v_before['area'] - v_after['area'])
                com_dist = np.linalg.norm(np.array(v_before['com']) - np.array(v_after['com']))
                if area_diff < 1e-6 and com_dist < 1e-6:
                    # print("found a match", k, tag,face_bnd[k])
                    gmsh.model.setEntityName(2,tag,"Bound"+str(k))
                    gmsh.model.addPhysicalGroup(2, [tag], tag,"Bound"+str(k))

                    boundaryDic_new[tag]=face_bnd[k]
                
                    break
        


    

        # 设置网格尺寸为 0.001m
        
        gmsh.option.setNumber("Mesh.Algorithm3D", alogrithm_3d_v)  # 使用 Delaunay 算法
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # 一阶单元
        gmsh.option.setNumber("Mesh.MeshSizeMax", maxH)
        gmsh.option.setNumber("Mesh.MeshSizeMin", minH)
        gmsh.option.setNumber("Mesh.Smoothing", smootions_steps)
        gmsh.option.setNumber("Mesh.Optimize", optimize_tetrahedra)
        
        # gmsh.option.setNumber("Mesh.CharacteristicLengthMax",sizeH)

        size_solid={}
        for k in localSize.keys():
            size_solid[int(k)+1]=localSize[k]*1000
   

        for vol in reversed(volumes):
            dim, tag = vol
            # 获取该实体的所有边界（递归获取到点）
            boundary = gmsh.model.getBoundary([vol], recursive=True)
            # 过滤出所有的点（维度为 0）
            points = [entity for entity in boundary if entity[0] == 0]
            if(size_solid.get(tag)!=None):
                size_temp=size_solid[tag]
                gmsh.model.mesh.setSize(points, size_temp)
        
 
 
        # 生成网格
        gmsh.model.occ.synchronize()
    
        
        print("生成网格")
        timeStart=time.time()
        # gmsh.option.setNumber("General.NumThreads", 8)
       
        gmsh.model.mesh.generate(3)
      
        print(f"生成网格耗时:{time.time()-timeStart}")
        timeStart=time.time()

      

        nodeList=[] #所有的网格顶点
        boundaryList=[] #边界面对应的网格
        tetList=[] #四面体对应的网格
    

        # 输出所有的网格顶点
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        print("\n所有的网格顶点:")
        for i in range(len(node_tags)):
            x = node_coords[3 * i]
            y = node_coords[3 * i + 1]
            z = node_coords[3 * i + 2]
            nodeList.append((x,y,z))
        print(f"节点数量:{len(nodeList)}")
        #判断节点中是否有重复的值
        # for i in range(len(nodeList)):
        #     for j in range(i+1,len(nodeList)):
        #         #通过元素的差值判断是否相等
        #         if(np.linalg.norm(np.array(nodeList[i])-np.array(nodeList[j]))<1e-6):
        #             print(f"重复节点{i},{j}")
        # print(f"输出重复节点完毕")
        

        # 输出选中面的三角面网格
        print("\n选中面的三角面网格:")
        # 获取物理组编号为100的元素
        for k in boundaryDic_new.keys():
            #此时k是当前处理过之后的面编号，需要从物理组中获取原来的面编号
            s_tag=k

            entities = gmsh.model.getEntitiesForPhysicalGroup(2, s_tag)
            elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim=2, tag=entities[0])
            if len(elem_tags) > 0:
                for i in range(len(elem_tags[0])):
                    nodes = elem_node_tags[0][3 * i:3 * i + 3]
                    # print(f"单元 {elem_tags[0][i]}: 节点 {nodes}")
                    boundaryList.append((nodes[0],nodes[1],nodes[2],boundaryDic_new[k]["bndId"]))
            else:
                print("No elements found on the selected face.")


        # 输出四面体网格
        
        mode_node_length=0
        is_model=False
        for k in mediumDic.keys():
            tag=k
            v=mediumDic[k]
            if(modelTagDic.get(tag)!=None):
                is_model=True
            else:
                is_model=False

            elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim=3,tag=tag)
            if len(elem_tags) > 0:
                for i in range(len(elem_tags[0])):
                    nodes = elem_node_tags[0][4 * i:4 * i + 4]
                    tetList.append((nodes[0],nodes[1],nodes[2],nodes[3],int(v)))
                    if(is_model):
                        mode_node_length+=1
                    
                    # print(f"体域 {tag} 单元 {elem_tags[0][i]}: 节点 {nodes}")
            else:
                print("No tetrahedral elements found.")
        print(f"\n四面体网格单元:{len(tetList)}")
        if(vtkFileName!=None):
            gmsh.write(vtkFileName)
        if(mshFileName!=None):
            gmsh.write(mshFileName)
        print(f"写入文件耗时:{time.time()-timeStart}")
        return (1,"网格生成并保存成功",(nodeList,boundaryList,tetList,mode_node_length))

        #输出文本
        with open("d:/mesh_solids.txt", "w") as f:
            f.write("网格顶点:\n")
            for i in range(len(nodeList)):
                f.write(f"节点 {i+1}: {nodeList[i]}\n")
            f.write("\n选中面的三角面网格:\n")
            for i in range(len(boundaryList)):
                f.write(f"单元 {i+1}: 节点 {boundaryList[i]}\n")
            f.write("\n四面体网格单元:\n")
            for i in range(len(tetList)):
                f.write(f"体域 {tetList[i][4]} 单元 {i+1}: 节点 {tetList[i]}\n")
        

        # 保存网格
        mesh_filename = "d:/mesh_solids.msh"
        gmsh.write(mesh_filename)
        gmsh.finalize()
        
      
        return (1,"网格生成成功      ","temp.msh")
    except Exception as e:
        errMessage=traceback.format_exc()
        print(errMessage)
        gmsh.finalize()
        return (-1,errMessage,None)
def get_face_info(faces):
    face_info = {}
    for dim, tag in faces:
        area = gmsh.model.occ.getMass(dim, tag)
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        face_info[(dim, tag)] = {
            "area": area,
            "com": com

        }
        
    return face_info
def get_face_nodes(faces):
    face_nodes = {}
    for dim, tag in faces:
        nodes = gmsh.model.mesh.getElements(dim, tag)
        face_nodes[(dim, tag)] = nodes
    return face_nodes
def createMesh_hex(strJson:str,logFileName=None):  # 网格数据导出
    try:
        param_json=json.loads(strJson)
        fnameList=param_json["fnameList"]
        options=param_json["options"]
        # localSize=param_json["localSize"]
        face_bnd=param_json.get("face_bnd",{})
        
        vtkFileName=param_json["vtkFileName"]
        mshFileName=param_json["mshFileName"]

        z_progression=1

        node_list=[] #所有的网格顶点
        cell_list_face=[] #边界面对应的网格
        cell_list_hex=[] #六面体对应的网格

        gmsh.initialize()
        gmsh.clear()
        #gmsh不输出info信息
        gmsh.option.setNumber("General.Terminal", 1)
    
        for i,fname in enumerate(fnameList):
            gmsh.model.occ.importShapes(fname)
            gmsh.model.occ.synchronize()

        # gmsh.model.occ.addBox(0,0,0, 1000,1000,1000)
        # gmsh.model.occ.synchronize()
        
         # 2) 取出边/面/体
        curves = gmsh.model.getEntities(dim=1)
        surfs  = gmsh.model.getEntities(dim=2)
        vols   = gmsh.model.getEntities(dim=3)

        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        Lx, Ly, Lz = xmax - xmin, ymax - ymin, zmax - zmin
        hx=options["hex_x"]*1000
        hy=options["hex_y"]*1000
        hz=options["hex_z"]*1000
        

        # 3) 计算各方向的单元数（至少 1 个单元 -> 至少 2 个节点）
        Nx = max(1, int(round(Lx / hx)))
        Ny = max(1, int(round(Ly / hy)))
        Nz = max(1, int(round(Lz / hz)))

        # 转为节点数
        nNx = Nx + 1
        nNy = Ny + 1
        nNz = Nz + 1

        # 4) 将边按方向分组，并分别设置 transfinite（可选 progressions）
        x_curves, y_curves, z_curves = classify_curve_dirs(curves)

        for c in x_curves:
            # 均匀划分
            gmsh.model.mesh.setTransfiniteCurve(c, nNx)

        for c in y_curves:
            gmsh.model.mesh.setTransfiniteCurve(c, nNy)

        for c in z_curves:
            if z_progression and z_progression != 1.0:
                # 非均匀：几何级数渐密（靠近曲线的终点）
                gmsh.model.mesh.setTransfiniteCurve(c, nNz, meshType="Progression", coef=z_progression)
            else:
                gmsh.model.mesh.setTransfiniteCurve(c, nNz)

        # 5) 所有面设为 transfinite + 四边形
        for dim, s in surfs:
            gmsh.model.mesh.setTransfiniteSurface(s)
            gmsh.model.mesh.setRecombine(2, s)

        # 6) 体设为 transfinite + 六面体
        for dim, v in vols:
            gmsh.model.mesh.setTransfiniteVolume(v)
            gmsh.model.mesh.setRecombine(3, v)

        # 7) 生成网格
        gmsh.option.setNumber("Mesh.SecondOrderIncomplete", 1)  # 0=完整二阶(27节点), 1=不完整二阶(20节点)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.setOrder(2)
        val = gmsh.option.getNumber("Mesh.SecondOrderIncomplete")
        print("Mesh.SecondOrderIncomplete =", val)  # 0=完整二阶(27节点), 1=不完整二阶(20节点)

        # 8) 保存
        gmsh.write("structured_hex_sized.msh")

        nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()

        # 5. 输出编号和坐标
        print("=== 节点编号和坐标 ===")
        for i, tag in enumerate(nodeTags):
            x = nodeCoords[3 * i + 0]
            y = nodeCoords[3 * i + 1]
            z = nodeCoords[3 * i + 2]
            node_list.append((x,y,z))
            # 按你要求的格式输出
            print(f"{int(tag)} {x:.6f} {y:.6f} {z:.6f}")

        # 6.输出面编号和组成节点
        # 遍历几何外表面（dim=2 的 CAD 面）
        surfaces = gmsh.model.getEntities(2)

        face_id = 1
        print("=== v1 v2 v3 v4 face_id geom_face_tag ===")

        for dim, sTag in surfaces:
            # 仅取该几何面上的二维网格元素（外表面）
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(2, sTag)

            for etype, tags, flat_nodes in zip(elemTypes, elemTags, elemNodeTags):
                # 四边形元素类型：
                # 3 = 一阶四边形(4节点), 10 = 完整二阶四边形(9节点), 16 = 非完整二阶四边形(8节点)
                if etype not in (3, 10, 16):
                    continue

                # 该类型每个单元的节点数
                name, dim_, order, numNodes, paramCoord, _ = gmsh.model.mesh.getElementProperties(etype)

                assert len(flat_nodes) == len(tags) * numNodes, "元素与节点数量不匹配，请检查网格文件。"

                # 逐个四边形面输出
                for i in range(len(tags)):
                    nids = flat_nodes[i*numNodes : (i+1)*numNodes]
                    # 只取前4个角点
                    v1, v2, v3, v4 = map(int, nids[:4])
                    print(f"{v1} {v2} {v3} {v4} {face_id} {sTag}")
                    cell_list_face.append((v1, v2, v3, v4,  sTag))
                    face_id += 1
        # 遍历所有几何体（dim=3）
        volumes = gmsh.model.getEntities(3)

        print("=== volume_tag element_tag v1 v2 v3 v4 v5 v6 v7 v8 e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12 ===")

        for dim, vtag in volumes:
            # 只取属于该几何体的 3D 网格单元
            elemTypes, elemTagsAll, elemNodeTagsAll = gmsh.model.mesh.getElements(3, vtag)

            for etype, elemTags, flatNodes in zip(elemTypes, elemTagsAll, elemNodeTagsAll):
                # Hex 类型：5(8点一阶), 17(20点二阶Serendipity), 92(27点完整二阶)
                if etype not in (5, 17, 92):
                    continue

                # 该类型每个单元的节点数
                name, dim_, order, numNodes, paramCoord, _ = gmsh.model.mesh.getElementProperties(etype)

                # 安全检查
                if len(flatNodes) != len(elemTags) * numNodes:
                    gmsh.finalize()
                    raise RuntimeError("元素与节点数量不匹配，请检查网格。")

                for i, etag in enumerate(elemTags):
                    nodes = list(map(int, flatNodes[i*numNodes:(i+1)*numNodes]))

                    # 前8个一定是角点
                    corners = nodes[:8]

                    # 取12个棱边中点（对于20/27节点单元均存在，位置固定在角点之后）
                    if numNodes >= 20:
                        edge_mids = nodes[8:20]   # 恰好12个
                    else:
                        # 一阶网格(8节点)没有棱边中点，这里给出空或可选择跳过
                        edge_mids = []

                    # 仅输出“顶点+棱边中点”的节点编号
                    if len(edge_mids) == 12:
                        print(
                            f"{vtag} {etag} "
                            + " ".join(map(str, corners))
                            + " "
                            + " ".join(map(str, edge_mids))
                        )
                        cell_list_hex.append((vtag, etag) + tuple(corners) + tuple(edge_mids))
                    else:
                        # 如果不是二阶（例如只8点），也可选择打印，仅含角点：
                        print(
                            f"{vtag} {etag} "
                            + " ".join(map(str, corners))
                        )
                        cell_list_hex.append((vtag, etag) + tuple(corners) + tuple(edge_mids))

        elements_ansys_dic=main_from_existing_model()
        cell_list_hex_ansys=[]
        for i in range(len(cell_list_hex)):
            vtag, etag = cell_list_hex[i][0], cell_list_hex[i][1]
            ansys20 = elements_ansys_dic.get(etag)
         
            cell_list_hex_ansys.append((vtag, etag) + tuple(ansys20))
                
        return (1,"网格生成成功",(node_list,cell_list_face,cell_list_hex,cell_list_hex_ansys))
        pass
          
    except Exception as e:
        gmsh.finalize()
        errMessage=traceback.format_exc()
        print(errMessage)
        return (-1,errMessage,None)

def classify_curve_dirs(curves):
    """
    将所有边按主方向分组：x向、y向、z向。
    做法：用 bounding box 判断每条边沿哪个轴延伸最大。
    """
    x_curves, y_curves, z_curves = [], [], []
    for dim, tag in curves:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        dx, dy, dz = abs(xmax - xmin), abs(ymax - ymin), abs(zmax - zmin)
        # 可能存在数值误差，用最大幅度来判断主方向
        if dx >= dy and dx >= dz:
            x_curves.append(tag)
        elif dy >= dx and dy >= dz:
            y_curves.append(tag)
        else:
            z_curves.append(tag)
    return x_curves, y_curves, z_curves

def build_structured_hex_box(Lx=1.0, Ly=1.0, Lz=1.0,
                             hx=0.5, hy=0.1, hz=0.1,
                             z_progression=None):
    """
    生成尺寸为 (Lx, Ly, Lz) 的方块，目标单元尺寸 (hx, hy, hz)，
    使用 transfinite + recombine 得到结构化六面体网格。
    z_progression: 若给出(>1.0)，则 z 方向采用几何级数渐密（靠近曲线末端）。
    """
    gmsh.model.add("structured_hex_sized")

    # 1) 建几何（OCC）
    vol = gmsh.model.occ.addBox(0, 0, 0, Lx, Ly, Lz)
    gmsh.model.occ.synchronize()

    # 2) 取出边/面/体
    curves = gmsh.model.getEntities(dim=1)
    surfs  = gmsh.model.getEntities(dim=2)
    vols   = gmsh.model.getEntities(dim=3)

    # 3) 计算各方向的单元数（至少 1 个单元 -> 至少 2 个节点）
    Nx = max(1, int(round(Lx / hx)))
    Ny = max(1, int(round(Ly / hy)))
    Nz = max(1, int(round(Lz / hz)))

    # 转为节点数
    nNx = Nx + 1
    nNy = Ny + 1
    nNz = Nz + 1

    # 4) 将边按方向分组，并分别设置 transfinite（可选 progressions）
    x_curves, y_curves, z_curves = classify_curve_dirs(curves)

    for c in x_curves:
        # 均匀划分
        gmsh.model.mesh.setTransfiniteCurve(c, nNx)

    for c in y_curves:
        gmsh.model.mesh.setTransfiniteCurve(c, nNy)

    for c in z_curves:
        if z_progression and z_progression != 1.0:
            # 非均匀：几何级数渐密（靠近曲线的终点）
            gmsh.model.mesh.setTransfiniteCurve(c, nNz, meshType="Progression", coef=z_progression)
        else:
            gmsh.model.mesh.setTransfiniteCurve(c, nNz)

    # 5) 所有面设为 transfinite + 四边形
    for dim, s in surfs:
        gmsh.model.mesh.setTransfiniteSurface(s)
        gmsh.model.mesh.setRecombine(2, s)

    # 6) 体设为 transfinite + 六面体
    for dim, v in vols:
        gmsh.model.mesh.setTransfiniteVolume(v)
        gmsh.model.mesh.setRecombine(3, v)

    # 7) 生成网格
    gmsh.option.setNumber("Mesh.SecondOrderIncomplete", 1)  # 0=完整二阶(27节点), 1=不完整二阶(20节点)
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.setOrder(2)
    val = gmsh.option.getNumber("Mesh.SecondOrderIncomplete")
    print("Mesh.SecondOrderIncomplete =", val)  # 0=完整二阶(27节点), 1=不完整二阶(20节点)

    # 8) 保存
    gmsh.write("structured_hex_sized.msh")

    nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()

    # 5. 输出编号和坐标
    print("=== 节点编号和坐标 ===")
    for i, tag in enumerate(nodeTags):
        x = nodeCoords[3 * i + 0]
        y = nodeCoords[3 * i + 1]
        z = nodeCoords[3 * i + 2]
        # 按你要求的格式输出
        print(f"{int(tag)} {x:.6f} {y:.6f} {z:.6f}")

    # 6.输出面编号和组成节点
    # 遍历几何外表面（dim=2 的 CAD 面）
    surfaces = gmsh.model.getEntities(2)

    face_id = 1
    print("=== v1 v2 v3 v4 face_id geom_face_tag ===")

    for dim, sTag in surfaces:
        # 仅取该几何面上的二维网格元素（外表面）
        elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(2, sTag)

        for etype, tags, flat_nodes in zip(elemTypes, elemTags, elemNodeTags):
            # 四边形元素类型：
            # 3 = 一阶四边形(4节点), 10 = 完整二阶四边形(9节点), 16 = 非完整二阶四边形(8节点)
            if etype not in (3, 10, 16):
                continue

            # 该类型每个单元的节点数
            name, dim_, order, numNodes, paramCoord, _ = gmsh.model.mesh.getElementProperties(etype)

            assert len(flat_nodes) == len(tags) * numNodes, "元素与节点数量不匹配，请检查网格文件。"

            # 逐个四边形面输出
            for i in range(len(tags)):
                nids = flat_nodes[i*numNodes : (i+1)*numNodes]
                # 只取前4个角点
                v1, v2, v3, v4 = map(int, nids[:4])
                print(f"{v1} {v2} {v3} {v4} {face_id} {sTag}")
                face_id += 1
     # 遍历所有几何体（dim=3）
    volumes = gmsh.model.getEntities(3)

    print("=== volume_tag element_tag v1 v2 v3 v4 v5 v6 v7 v8 e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12 ===")

    for dim, vtag in volumes:
        # 只取属于该几何体的 3D 网格单元
        elemTypes, elemTagsAll, elemNodeTagsAll = gmsh.model.mesh.getElements(3, vtag)

        for etype, elemTags, flatNodes in zip(elemTypes, elemTagsAll, elemNodeTagsAll):
            # Hex 类型：5(8点一阶), 17(20点二阶Serendipity), 92(27点完整二阶)
            if etype not in (5, 17, 92):
                continue

            # 该类型每个单元的节点数
            name, dim_, order, numNodes, paramCoord, _ = gmsh.model.mesh.getElementProperties(etype)

            # 安全检查
            if len(flatNodes) != len(elemTags) * numNodes:
                gmsh.finalize()
                raise RuntimeError("元素与节点数量不匹配，请检查网格。")

            for i, etag in enumerate(elemTags):
                nodes = list(map(int, flatNodes[i*numNodes:(i+1)*numNodes]))

                # 前8个一定是角点
                corners = nodes[:8]

                # 取12个棱边中点（对于20/27节点单元均存在，位置固定在角点之后）
                if numNodes >= 20:
                    edge_mids = nodes[8:20]   # 恰好12个
                else:
                    # 一阶网格(8节点)没有棱边中点，这里给出空或可选择跳过
                    edge_mids = []

                # 仅输出“顶点+棱边中点”的节点编号
                if len(edge_mids) == 12:
                    print(
                        f"{vtag} {etag} "
                        + " ".join(map(str, corners))
                        + " "
                        + " ".join(map(str, edge_mids))
                    )
                else:
                    # 如果不是二阶（例如只8点），也可选择打印，仅含角点：
                    print(
                        f"{vtag} {etag} "
                        + " ".join(map(str, corners))
                    )

    main_from_existing_model()
    pass
# ANSYS Hex20 的 12 条边顺序（决定 9..20 的中点编号顺序）
ANSYS_EDGES: List[Tuple[int, int]] = [
    (1, 2), (2, 3), (3, 4), (4, 1),   # 底面
    (5, 6), (6, 7), (7, 8), (8, 5),   # 顶面
    (1, 5), (2, 6), (3, 7), (4, 8)    # 立边
]

def _vec(nodes_xyz: Dict[int, Tuple[float, float, float]], nid: int):
    return nodes_xyz[nid]

def _bbox_corner_order_ansys(nodes_xyz: Dict[int, Tuple[float, float, float]],
                             corner_ids: List[int],
                             tol: float = 1e-9) -> List[int]:
    """
    用轴对齐包围盒将 8 个角点映射到 ANSYS 角点 1..8：
      1:(minx,miny,minz) 2:(maxx,miny,minz) 3:(maxx,maxy,minz) 4:(minx,maxy,minz)
      5:(minx,miny,maxz) 6:(maxx,miny,maxz) 7:(maxx,maxy,maxz) 8:(minx,maxy,maxz)
    适用于结构化/轴对齐六面体（你的 structured_hex 就是这类）
    """
    coords = {nid: nodes_xyz[nid] for nid in corner_ids}
    xs, ys, zs = zip(*coords.values())
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    minz, maxz = min(zs), max(zs)

    def find(xx, yy, zz):
        for nid, (x, y, z) in coords.items():
            if abs(x - xx) <= tol and abs(y - yy) <= tol and abs(z - zz) <= tol:
                return nid
        return None

    targets = [
        (minx, miny, minz),
        (maxx, miny, minz),
        (maxx, maxy, minz),
        (minx, maxy, minz),
        (minx, miny, maxz),
        (maxx, miny, maxz),
        (maxx, maxy, maxz),
        (minx, maxy, maxz),
    ]
    ordered = []
    for (xx, yy, zz) in targets:
        nid = find(xx, yy, zz)
        if nid is None:
            raise RuntimeError("角点包围盒匹配失败：该六面体可能不是轴对齐（或 tol 太小）。")
        ordered.append(nid)
    return ordered

def _assign_edge_mids(nodes_xyz: Dict[int, Tuple[float, float, float]],
                      order8: List[int],
                      mids: List[int]) -> List[int]:
    """
    按 ANSYS_EDGES 的顺序，将 12 个中点节点匹配到对应的几何边中点（就近原则）。
    返回 9..20 的节点编号。
    """
    # 角点位次 -> 实际节点ID
    cm = {i + 1: nid for i, nid in enumerate(order8)}
    ordered_mid = []
    for (a, b) in ANSYS_EDGES:
        ax, ay, az = _vec(nodes_xyz, cm[a])
        bx, by, bz = _vec(nodes_xyz, cm[b])
        mx, my, mz = (0.5 * (ax + bx), 0.5 * (ay + by), 0.5 * (az + bz))
        best = None
        best_d2 = 1e99
        for mid in mids:
            px, py, pz = _vec(nodes_xyz, mid)
            d2 = (px - mx) ** 2 + (py - my) ** 2 + (pz - mz) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best = mid
        ordered_mid.append(best)
    return ordered_mid

def build_nodes_xyz_from_gmsh() -> Dict[int, Tuple[float, float, float]]:
    """
    从 gmsh.model.mesh.getNodes() 构建 {nodeTag: (x,y,z)} 字典。
    """
    nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()
    nodes_xyz = {}
    for i, nid in enumerate(nodeTags):
        x = nodeCoords[3 * i + 0]
        y = nodeCoords[3 * i + 1]
        z = nodeCoords[3 * i + 2]
        nodes_xyz[int(nid)] = (float(x), float(y), float(z))
    return nodes_xyz

def iter_hex20_from_getElements():
    """
    遍历 gmsh.model.mesh.getElements() 中的 Hex20（etype=17），
    产出 (eid, conn20)；conn20 为 Gmsh 原顺序的 20 节点。
    """
    # getElements(dim=-1, tag=-1) 返回所有维度的元素
    elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements()
    for t, tags, nodes_flat in zip(elemTypes, elemTags, elemNodeTags):
        etype = int(t)
        if etype != 17:  # 只要 Hex20
            continue
        per_elem_n = 20  # Hex20 每个单元 20 节点
        assert len(nodes_flat) % per_elem_n == 0
        num_elems = len(nodes_flat) // per_elem_n
        # tags 是每个单元的 EID 列表
        for i in range(num_elems):
            eid = int(tags[i])
            conn = list(map(int, nodes_flat[i * per_elem_n:(i + 1) * per_elem_n]))
            yield eid, conn

def remap_hex20_conn_to_ansys(nodes_xyz: Dict[int, Tuple[float, float, float]],
                              gmsh_conn20: List[int]) -> List[int]:
    """
    输入：Gmsh 的 20 节点顺序（Hex20）
    输出：ANSYS SOLID186 的 1..20 顺序（角点1..8 + 边中点9..20）
    """
    corners = gmsh_conn20[:8]
    mids    = gmsh_conn20[8:20]
    order8  = _bbox_corner_order_ansys(nodes_xyz, corners)
    order9_20 = _assign_edge_mids(nodes_xyz, order8, mids)
    return order8 + order9_20

def main_from_existing_model():
    """
    在“当前Gmsh模型已完成网格”的前提下直接运行：
    - 提取全部 Hex20
    - 打印 ANSYS 顺序（1..20）
    - 可选：打印 EN 卡片行，方便粘贴到 .cdb
    """
    elements_ansys_dic={}
    nodes_xyz = build_nodes_xyz_from_gmsh()
    found = False
    for eid, conn in iter_hex20_from_getElements():
        found = True
        ansys20 = remap_hex20_conn_to_ansys(nodes_xyz, conn)
        elements_ansys_dic[eid]=ansys20
        # 打印结果
        print(f"[Hex20] EID {eid} -> ANSYS(1..20): {', '.join(map(str, ansys20))}")

        # 如需 EN 卡片可取消下面注释：
        # print(f"EN, {eid}, " + ", ".join(map(str, ansys20)))

    if not found:
        print("未在当前模型中找到 Hex20 (etype=17) 单元。")
    return elements_ansys_dic