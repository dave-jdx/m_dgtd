import sys,os,time,traceback
import gmsh


def createMesh(fnameList:list=[],sizeH:float=6,vtkFileName=None,mshFileName=None,logName="d:/mesh.log"):  # 网格数据导出

    try:
        # fnameList=["d:/exf1.stp","d:/cube.stp","d:/cube_named.stp"]
        # fnameList=fnameList[2:]
        # fnameList=["d:/15cell.stp"]
        time_start_total=time.time()
        gmsh.initialize()
        gmsh.clear()
        fname=fnameList[0]
        log("开始处理文件:"+fname,logName)
   
        mediumDic={}#tag:mdiumIndex
        boundaryDic={} #tag:boundaryIndex
        modelTagDic={}
        
        #gmsh不输出info信息
        # gmsh.option.setNumber("General.Terminal", 0)
      
       
        timeStart=time.time()
        for i,fname in enumerate(fnameList):
            imported_entities=gmsh.model.occ.importShapes(fname)
            print(f"Imported耗时:{time.time()-timeStart}")
            msg=f"Imported耗时:{time.time()-timeStart}"
            log(msg,logName)
            timeStart=time.time()
            gmsh.model.occ.synchronize()
          
    

        # 获取所有三维实体（体）
        face_origin_now_pairs={}
        entities = gmsh.model.getEntities(dim=3)
        
        # object_dim_tags = [entities[0]]  # 第一个模型的体
        # tool_dim_tags = [entities[1]]    # 第二个模型的体
        # out_dim_tags, out_tags_map=gmsh.model.occ.fragment(entities, [])
        # gmsh.model.occ.removeAllDuplicates()
        # gmsh.model.occ.synchronize()
        out_dim_tags = entities

        

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
            surfaces=gmsh.model.getBoundary([(etype,tag)],oriented=False,recursive=False)
    
            

        surfaces = gmsh.model.getEntities(2)
        for (dim, tag) in surfaces:
            # 获取实体的名称
            name = gmsh.model.getEntityName(dim, tag)
            if(name!=""):
                narr=name.split("/")
                if(narr[1].startswith("Bound")):
                    faceId=int(narr[1].replace("Bound",""))
                    if(faceId+1 in face_origin_now_pairs):
                        faceId_n=face_origin_now_pairs[faceId+1]#映射到当前处理过之后的面编号
                    else:
                        faceId_n=faceId+1
                    boundaryDic[tag]=faceId+1 #记录原来的面编号，输出时使用
                selected_surface = (dim, tag)
                gmsh.model.addPhysicalGroup(2, [selected_surface[1]], tag,name)

        

    

        # 设置网格尺寸为 0.001m
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # 使用 Delaunay 算法
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # 一阶单元
        gmsh.option.setNumber("Mesh.MeshSizeMax", sizeH)
        # gmsh.option.setNumber("Mesh.Optimize", 0)
        # gmsh.option.setNumber("Mesh.OptimizeNetgen", 0)
        # gmsh.option.setNumber("Mesh.RecombineAll", 0) 
        # gmsh.option.setNumber("Mesh.Smoothing", 0)
        # gmsh.option.setNumber("Mesh.MeshSizeMin", 0)
 
        # 生成网格
        gmsh.model.occ.synchronize()
        
        print("生成网格")
        timeStart=time.time()
        num_threads = gmsh.option.getNumber("General.NumThreads")
        print(f"默认的线程数为: {int(num_threads)}")
        gmsh.option.setNumber("General.NumThreads", 8)
        num_threads = gmsh.option.getNumber("General.NumThreads")
        print(f"设置的线程数为: {int(num_threads)}")
        gmsh.model.mesh.generate(3)
        
        msg=f"生成网格耗时:{time.time()-timeStart}"
        print(msg)
        log(msg,logName)
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

        # 输出选中面的三角面网格
        print("\n选中面的三角面网格:")
        # 获取物理组编号为100的元素
        for k in boundaryDic.keys():
            #此时k是当前处理过之后的面编号，需要从物理组中获取原来的面编号
            s_tag=k

            entities = gmsh.model.getEntitiesForPhysicalGroup(2, s_tag)
            elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim=2, tag=entities[0])
            if len(elem_tags) > 0:
                for i in range(len(elem_tags[0])):
                    nodes = elem_node_tags[0][3 * i:3 * i + 3]
                    # print(f"单元 {elem_tags[0][i]}: 节点 {nodes}")
                    boundaryList.append((nodes[0],nodes[1],nodes[2],int(boundaryDic[k])))
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
        # print(f"\n四面体网格单元:{len(tetList)}")
        # msg=f"四面体网格单元:{len(tetList)}"
        log(f"四面体网格单元:{len(tetList)}",logName)
        if(vtkFileName!=None):
            gmsh.write(vtkFileName)
        # if(mshFileName!=None):
        #     gmsh.write(mshFileName)
        # print(f"写入文件耗时:{time.time()-timeStart}")
        log(f"网格生成并保存成功,耗时:{time.time()-timeStart}",logName)
        msg=f"网格总耗时:{time.time()-time_start_total}"
        log(msg,logName)
        return (1,"网格生成并保存成功",(nodeList,boundaryList,tetList,mode_node_length))

    except Exception as e:
        errMessage=traceback.format_exc()
        print(errMessage)
        return (-1,errMessage,None)
    
def log(msg,fname="d:/mesh.log"):
    with open(fname,"a") as f:
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
createMesh(["d:/ship.stp"],20,"d:/ship.vtk","d:/ship.msh")
def main():
    #接受启动参数
    import sys
    args=sys.argv
    if(len(args)<2):
        print("请输入文件名")
        return
    fname=args[1]
    findex=args[2]
    outoutFileName=fname.replace(".stp","")+str(findex)+".vtk"
    createMesh([fname],6,outoutFileName,fname.replace(".stp",".msh"))
    pass

if __name__ == "__main__":
    # main()
    pass