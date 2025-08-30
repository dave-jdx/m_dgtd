import os,time,traceback,sys,io,json
import gmsh
import numpy as np
from PyQt5 import QtWidgets, QtCore

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

    

        # gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # 使用 Delaunay 算法
        # gmsh.option.setNumber("Mesh.ElementOrder", 1)  # 一阶单元
        # gmsh.option.setNumber("Mesh.MeshSizeMax", sizeH)
        # gmsh.model.occ.synchronize()
        # gmsh.model.mesh.generate(3)
        # return 
        surfaces = gmsh.model.getEntities(2)
        # surfaces_nodes_befor=get_face_nodes(surfaces)
        surfaces_before=get_face_info(surfaces)
        faceId_used={}#记录已经使用的面编号
        for (dim, tag) in surfaces:
            # 获取实体的名称
            name = gmsh.model.getEntityName(dim, tag)
            # boundaryDic[tag]=tag-1
            
            if(name!=""):
                print(f"Found face in gmsh with tag: {name}-{tag}")
                narr=name.split("/")
                if(narr[1].startswith("Bound")):
                    # faceId=tag-1
                    faceId=int(narr[1].replace("Bound","")) #fragmet之后的EntityName会变化，所以需要记录原来的面编号
                    if(faceId!=tag-1):
                        continue
                    if(faceId in faceId_used):#重复定义过的面
                        continue
                    faceId_used[faceId]=1
                    
                    boundaryDic[tag]=(faceId,surfaces_before[(dim,tag)]) #记录原来的面编号，输出时使用


                # selected_surface = (dim, tag)
                # gmsh.model.addPhysicalGroup(2, [selected_surface[1]], tag,name)
        
        #使用布尔碎片处理共享面

        # 获取所有三维实体（体）

        
        face_origin_now_pairs={} #原编号，新编号
        entities = gmsh.model.getEntities(dim=3)
        desired_entities = [e for e in entities if e[1] in modelTags]

        if(alogrithm_3d_v==4 or alogrithm_3d_v==7):
            desired_entities=entities

        
        out_dim_tags, out_tags_map=gmsh.model.occ.fragment(desired_entities, [])
        # gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()
        # gmsh.model.occ.fuse(desired_entities,desired_entities,removeObject=False,removeTool=True)
        gmsh.model.occ.synchronize()
        # out_dim_tags=[]

        

        # 获取每个体的面
        volume_surfaces = {}
        volumes = [dimtag for dimtag in out_dim_tags if dimtag[0] == 3]
        print("新生成的体：", volumes)
        for vol in volumes:
            # 获取体 vol 的面
            surfaces = gmsh.model.getBoundary([vol], oriented=False, recursive=False)
            surface_tags = [s[1] for s in surfaces if s[0] == 2]
            volume_surfaces[vol[1]] = set(surface_tags)

        # 统计每个面的出现次数
        surface_counts = {}
        surface_index=1
        for surfaces in volume_surfaces.values():
            for s in surfaces:
                
                surface_counts[s] = surface_counts.get(s, 0) + 1
                face_origin_now_pairs[surface_index]=s
                surface_index+=1
            

        # # 找到被多个体共享的面（出现次数大于1）
        shared_surfaces = [s for s, count in surface_counts.items() if count > 1]
        # print("共享的面标签：", shared_surfaces)

        # 打印共享面的详细信息
        for s in shared_surfaces:
            # print(f"共享面标签：{s}")
            pass
        # 可以在此处添加更多处理，如添加物理组或设置属性等
    
        
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
                
                # print(f"Found selected solid in gmsh with tag: {name}-{tag}")
            # surfaces=gmsh.model.getBoundary([(etype,tag)],oriented=False,recursive=False)
    
            # for (dim,tag) in surfaces:
                # name=gmsh.model.getEntityName(dim,tag)
                # s_total_index+=1
                # if(name!=""):
                #     narr=name.split("/")
                #     if(narr[1].startswith("Bound")):
                #         faceId=int(narr[1].replace("Bound",""))
                #         faceId_n=face_origin_now_pairs[faceId+1]#映射到当前处理过之后的面编号
                #         boundaryDic[faceId_n]=faceId #记录原来的面编号，输出时使用
                #     selected_surface=(dim,tag)
                #     gmsh.model.addPhysicalGroup(2,[selected_surface[1]],tag,name)
                #     print(f"Found selected face in gmsh with tag: {name}-{tag}")
        boundaryDic_new={}

        surfaces_new = gmsh.model.getEntities(dim=2)
        surfaces_after=get_face_info(surfaces_new)
        tag_new_dic={}
        for k in boundaryDic.keys():
            #为新的面赋值entityName和物理组
            for (dim, tag) in surfaces_new:
    
                v_after=surfaces_after[(dim,tag)]
                v_before=boundaryDic[k][1]
                area_diff = abs(v_before['area'] - v_after['area'])
                com_dist = np.linalg.norm(np.array(v_before['com']) - np.array(v_after['com']))
                if area_diff < 1e-6 and com_dist < 1e-6:
                    print("found a match", k, tag,boundaryDic[k][0])
                    gmsh.model.setEntityName(2,tag,"Bound"+str(boundaryDic[k][0]))
                    gmsh.model.addPhysicalGroup(2, [tag], tag,"Bound"+str(boundaryDic[k][0]))
                    boundaryDic_new[tag]=boundaryDic[k]
                
                    break
        
            # tag_new=face_origin_now_pairs[k] #新的面编号
            # if(tag_new_dic.get(tag_new)!=None):
            #     continue
            # gmsh.model.setEntityName(2,tag_new,"Bound"+str(boundaryDic[k]))
            # gmsh.model.addPhysicalGroup(2, [tag_new], tag_new,"Bound"+str(boundaryDic[k]))
            # boundaryDic_new[tag_new]=boundaryDic[k]
            # tag_new_dic[tag_new]=1


        # surfaces = gmsh.model.getEntities(2)
        # for (dim, tag) in surfaces:
        #     # 获取实体的名称
        #     name = gmsh.model.getEntityName(dim, tag)
            
        #     if(name!=""):
        #         print(f"Found face in gmsh with tag: {name}-{tag}")
        #         narr=name.split("/")
        #         if(narr[1].startswith("Bound")):
        #             faceId=int(narr[1].replace("Bound",""))
        #             if(faceId+1 in face_origin_now_pairs):
        #                 faceId_n=face_origin_now_pairs[faceId+1]#映射到当前处理过之后的面编号
        #             else:
        #                 faceId_n=faceId+1
        #             boundaryDic[tag]=faceId+1 #记录原来的面编号，输出时使用
        #         selected_surface = (dim, tag)
        #         gmsh.model.addPhysicalGroup(2, [selected_surface[1]], tag,name)
                # print(f"add physical group {name} with tag {tag}")
        #     print(f"Found selected face in gmsh with tag: {name}-{tag}")
        

    

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
        
        # gmsh.option.setNumber("Mesh.Optimize", 0)
        # gmsh.option.setNumber("Mesh.OptimizeNetgen", 0)
        # gmsh.option.setNumber("Mesh.RecombineAll", 0) 
        # gmsh.option.setNumber("Mesh.Smoothing", 0)
        # gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
 
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
                    boundaryList.append((nodes[0],nodes[1],nodes[2],int(boundaryDic_new[k][0]+1)))
            else:
                print("No elements found on the selected face.")

        # for k in mediumDic.keys():
        #     s_tag=k
        #     v=mediumDic[k]
        #     entities = gmsh.model.getEntitiesForPhysicalGroup(2, s_tag)
        #     elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim=2, tag=entities[0])
        #     if len(elem_tags) > 0:
        #         for i in range(len(elem_tags[0])):
        #             nodes = elem_node_tags[0][3 * i:3 * i + 3]
        #             print(f"单元 {elem_tags[0][i]}: 节点 {nodes}")
        #     else:
        #         print("No elements found on the selected face.")

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

