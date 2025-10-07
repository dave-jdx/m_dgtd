import gmsh

gmsh.initialize()
gmsh.open("e:/1.msh")  # 换成你上传的 msh 文件路径

volumes = gmsh.model.getEntities(3)

print("=== 前几个六面体单元节点号 ===")

for _, vtag in volumes:
    elemTypes, elemTagsAll, elemNodeTagsAll = gmsh.model.mesh.getElements(3, vtag)
    for etype, tags, flat in zip(elemTypes, elemTagsAll, elemNodeTagsAll):
        if etype not in (5, 17, 92):  # Hex8, Hex20, Hex27
            continue
        name, dim_, order, nper, _, _ = gmsh.model.mesh.getElementProperties(etype)
        for i, etag in enumerate(tags[:3]):  # 只打印前3个
            nodes = list(map(int, flat[i*nper:(i+1)*nper]))
            if nper >= 20:   # 二阶
                nodes20 = nodes[:20]
                print(f"单元 {etag}: {nodes20}")
            else:            # 一阶
                print(f"单元 {etag}: {nodes}")
gmsh.finalize()
