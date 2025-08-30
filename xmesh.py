import os,time,traceback,sys,io,json
import gmsh
import numpy as np
from PyQt5 import QtWidgets, QtCore

def createMesh(strJson:str,
               logFileName=None):  # 网格数据导出

    try:
        _dir=os.path.dirname(os.path.abspath(sys.executable))+"/xmesh"
        if(not os.path.exists(_dir)):
            os.makedirs(_dir)
        if(logFileName==None):
            #日志文件名带上日期
            logFileName=_dir+f"/xmesh_{time.strftime('%Y%m%d',time.localtime())}.log"
            print(f"日志文件名:{logFileName}")

        log(strJson,logFileName)
        param_json=json.loads(strJson)
        
    
        fnameList=param_json["fnameList"]
        options=param_json["options"]
        localSize=param_json["localSize"]
        
        vtkFileName=param_json["vtkFileName"]
        mshFileName=param_json["mshFileName"]
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
        # gmsh.option.setNumber("General.Terminal", 1)
    
        mediumDic={}#tag:mdiumIndex
        boundaryDic={} #tag:boundaryIndex
        #从文件列表读取stp文件
        modelTagDic={}
        is_first=True
       
        timeStart=time.time()
        for i,fname in enumerate(fnameList):
            imported_entities=gmsh.model.occ.importShapes(fname)
            # print(f"Imported耗时:{time.time()-timeStart}")
            msg=f"Imported耗时:{time.time()-timeStart}"
            log(msg,logFileName)
            timeStart=time.time()
            gmsh.model.occ.synchronize()
            if(is_first):#只取第一个文件的体域
                volumes = [entity for entity in imported_entities if entity[0] == 3]
                modelTags=[v[1] for v in volumes]
                #列表转字典 key是tag value是index
                modelTagDic=dict(zip(modelTags,[i]*len(modelTags)))
                is_first=False

        surfaces = gmsh.model.getEntities(2)
        surfaces_before=get_face_info(surfaces)
        faceId_used={}#记录已经使用的面编号
        for (dim, tag) in surfaces:
            # 获取实体的名称
            name = gmsh.model.getEntityName(dim, tag)
            # boundaryDic[tag]=tag-1
            
            if(name!=""):
                # print(f"边界面: {name}-{tag}")
                log(f"边界面: {name}-{tag}",logFileName)
                narr=name.split("/")
                if(narr[1].startswith("Bound")):
                    faceId=int(narr[1].replace("Bound",""))
                    if(faceId!=tag-1):
                        continue
                    if(faceId in faceId_used):
                        continue
                    faceId_used[faceId]=1
                    boundaryDic[tag]=(faceId,surfaces_before[(dim,tag)]) #记录原来的面编号，输出时使用


                # selected_surface = (dim, tag)
                # gmsh.model.addPhysicalGroup(2, [selected_surface[1]], tag,name)
        
        #使用布尔碎片处理共享面
        face_origin_now_pairs={} #原编号，新编号
        entities = gmsh.model.getEntities(dim=3)
        desired_entities = [e for e in entities if e[1] in modelTags]

        if(alogrithm_3d_v==4 ):
            desired_entities=entities

        
        out_dim_tags, out_tags_map=gmsh.model.occ.fragment(desired_entities, [])
        gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()
        out_dim_tags=[]

        # 获取每个体的面
        volume_surfaces = {}
        volumes = [dimtag for dimtag in out_dim_tags if dimtag[0] == 3]
        # print("新生成的体：", volumes)
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
        for k in boundaryDic.keys():
            #为新的面赋值entityName和物理组
            for (dim, tag) in surfaces_new:
    
                v_after=surfaces_after[(dim,tag)]
                v_before=boundaryDic[k][1]
                area_diff = abs(v_before['area'] - v_after['area'])
                com_dist = np.linalg.norm(np.array(v_before['com']) - np.array(v_after['com']))
                if area_diff < 1e-6 and com_dist < 1e-6:
                    # print("边界面匹配", k, tag,boundaryDic[k][0])
                    log(f"边界面匹配 {k} {tag} {boundaryDic[k][0]}",logFileName)
                    gmsh.model.setEntityName(2,tag,"Bound"+str(boundaryDic[k][0]))
                    gmsh.model.addPhysicalGroup(2, [tag], tag,"Bound"+str(boundaryDic[k][0]))
                    boundaryDic_new[tag]=boundaryDic[k]
                
                    break
        

        # 设置网格尺寸
        
        gmsh.option.setNumber("Mesh.Algorithm3D", alogrithm_3d_v)  # 使用 Delaunay 算法
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # 一阶单元
        gmsh.option.setNumber("Mesh.MeshSizeMax", maxH)
        gmsh.option.setNumber("Mesh.MeshSizeMin", minH)
        gmsh.option.setNumber("Mesh.Smoothing", smootions_steps)
        gmsh.option.setNumber("Mesh.Optimize", optimize_tetrahedra)
        # gmsh.option.setNumber("Mesh.MeshSizeMin", 1)
        # gmsh.option.setNumber("Mesh.Optimize", 0)
        # gmsh.option.setNumber("Mesh.OptimizeNetgen", 0)
        # gmsh.option.setNumber("Mesh.RecombineAll", 0) 
        # gmsh.option.setNumber("Mesh.Smoothing", 0)
        # gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
 
        # 生成网格
        gmsh.model.occ.synchronize()

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
    
        # print("生成网格")
        log("生成网格",logFileName)
        timeStart=time.time()
        gmsh.option.setNumber("General.NumThreads", 8)
        gmsh.model.mesh.generate(3)
      
        # print(f"生成网格耗时:{time.time()-timeStart}")
        log(f"生成网格耗时:{time.time()-timeStart}",logFileName)
        timeStart=time.time()
        nodeList=[] #所有的网格顶点
        boundaryList=[] #边界面对应的网格
        tetList=[] #四面体对应的网格
    

        # 输出所有的网格顶点
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()

        for i in range(len(node_tags)):
            x = node_coords[3 * i]
            y = node_coords[3 * i + 1]
            z = node_coords[3 * i + 2]
            nodeList.append((x,y,z))
        # print(f"节点数量:{len(nodeList)}")
        msg=f"节点数量:{len(nodeList)}"
        log(msg,logFileName)

        # 输出选中面的三角面网格
     
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
            else:
                print("No tetrahedral elements found.")
        # print(f"\n四面体网格单元:{len(tetList)}")
        msg=f"四面体网格单元:{len(tetList)}"
        # print(msg)
        log(msg,logFileName)
        if(vtkFileName!=None):
            gmsh.write(vtkFileName)
        if(mshFileName!=None):
            gmsh.write(mshFileName)
        msg=f"写入文件耗时:{time.time()-timeStart}"
        # print(msg)
        log(msg,logFileName)
        gmsh.finalize()
        return (1,"网格生成并保存成功",(nodeList,boundaryList,tetList,mode_node_length))
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
def write_mesh(fname:str,nodeList,boundaryList,tetList,model_nodes_length=0):
    '''
    Write mesh to text
    '''
    newline="\n"
    splitext="\t"
    m_unit=1000
    dotPrecision=4 #小数点精度
    node_begin=get_comment("Begin_Node")
    node_end=get_comment("End_Node")
    face_begin=get_comment("Begin_Face")
    face_end=get_comment("End_Face")
    tet_begin=get_comment("Begin_Tet")
    tet_end=get_comment("End_Tet")

    try:
        with open(fname,"w",encoding="utf-8") as f:
            f.write(node_begin+newline)
            f.write(str(len(nodeList))+newline)
            for i in range(len(nodeList)):
                f.write(splitext.join(map(lambda x: f"{x / m_unit:.4f}",nodeList[i]))+newline)
            f.write(node_end+newline)
            f.write(newline)

            f.write(face_begin+newline)
            f.write(str(len(boundaryList))+newline)
            for i in range(len(boundaryList)):
                f.write(splitext.join(map(str,boundaryList[i]))+newline)
            f.write(face_end+newline)
            f.write(newline)

            f.write(tet_begin+newline)
            f.write(str(len(tetList))+newline)
            f.write(str(model_nodes_length)+newline)
            for i in range(len(tetList)):
                f.write(splitext.join(map(str,tetList[i]))+newline)
            f.write(tet_end+newline)
        pass
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
def write_mesh_proc(fname,tetList):
    '''
    Write mesh to text
    '''
    newline="\n"
    splitext="\t"
    m_unit=1000
    dotPrecision=4 #小数点精度
    
    try:
        with open(fname,"w",encoding="utf-8") as f:
            f.write(str(len(tetList))+newline)
            for i in range(len(tetList)):
                f.write(splitext.join(map(str,tetList[i][:-1]))+newline)
        pass
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
def get_comment(str):
    return f"<!--{str}-->"
def log(msg,fname="d:/mesh.log"):
    with open(fname,"a",encoding="utf-8") as f:
        #记录当前时间，utc-8
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+":"+msg)
        # f.write(msg)
        f.write("\n")
    pass
def handle_exception(exc_type, exc_value, exc_traceback):

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        if(exc_type==AttributeError):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
sys.excepthook = handle_exception
def main():
    #接受启动参数
    import sys
    args=sys.argv
    if(len(args)<1):
        print("请输入正确的参数")
        return
    # print(args)
    try:
        strJson=args[1]
        param_json=json.loads(strJson)
        outputFileName=param_json["outputFileName"]
        thermal_struct_used=param_json["thermal_struct_used"]
        # print(f"开始生成网格{outputFileName}")


        code,message,data=createMesh(strJson)
        if(code==1):
            
            # write_mesh(outputFileName,*data)
            tLength=data[3]
            if(thermal_struct_used==0):
                tLength=0
            write_mesh(fname=outputFileName,
                                    nodeList=data[0],
                                    boundaryList=data[1],
                                    tetList=data[2],
                                    model_nodes_length=tLength)
            print(f"网格保存成功{outputFileName}")
            fname=os.path.dirname(os.path.abspath(sys.executable))+"/EMProcMesh.txt"
            write_mesh_proc(fname,data[2])
            print(f"网格保存成功{fname}")
            
            #休眠2秒钟
            sys.stdout.flush()
            time.sleep(2)
            sys.exit(0)
        else:
            print("网格生成失败")
            print(message)
    except Exception as e:
        print("网格生成失败")
        print(e)
        traceback.print_exc()
        time.sleep(10)
        sys.exit(-1)
    pass

if __name__ == "__main__":
    main()
    pass
# strJson='{"fnameList": ["D:/project/cae/fem-gdtd/test/24_11_17EMTest/EMTest.results/FEM-DGTD/input/EMTest_model_named.stp"], "options": {"maxh": 0.1, "minh": 0.0, "smoothing_steps": 1, "optimize_tetrahedra": false, "3dAlogrithm": 0}, "vtkFileName": "D:/project/cae/fem-gdtd/test/24_11_17EMTest/EMTest.results/FEM-DGTD/input/Mesh.vtk", "mshFileName": "D:/project/cae/fem-gdtd/test/24_11_17EMTest/EMTest.results/FEM-DGTD/input/Mesh.msh", "thermal_struct_used": 0, "localSize": {"3": 0.001}}'
# code,message,data=createMesh(strJson)
# print(code)


