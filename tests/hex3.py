import gmsh
import sys
import math

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
    # 取得所有 2D 网格单元（dim=2 → faces）
    # elemTypes, elemTagsAll, elemNodeTagsAll = gmsh.model.mesh.getElements(2)

    # face_id = 1
    # print("=== 面信息 (v1 v2 v3 v4 face_id) ===")
    # for etype, tags, flat_nodes in zip(elemTypes, elemTagsAll, elemNodeTagsAll):
    #     # 只处理四边形（3:一阶4点；10:9点二阶；16:8点二阶Serendipity）
    #     if etype not in (3, 10, 16):
    #         continue

    #     # 取该 etype 的每个单元含有多少个节点
    #     name, dim, order, numNodes, paramCoord, _ = gmsh.model.mesh.getElementProperties(etype)
    #     # flat_nodes 是一维数组，需要按 numNodes 切片
    #     assert len(flat_nodes) == len(tags) * numNodes, "数量不匹配，请检查网格/类型"
    #     # 逐面输出，只取前4个角点（Gmsh 的四边形前4个就是角点）
    #     for i, ftag in enumerate(tags):
    #         nids = flat_nodes[i*numNodes : (i+1)*numNodes]
    #         v1, v2, v3, v4 = nids[:4]
    #         print(f"{v1} {v2} {v3} {v4} {face_id}")
    #         face_id += 1

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


# ----------------- 主程序 -----------------
if __name__ == "__main__":
    gmsh.initialize()

    # 示例：几何尺寸 1.2 × 0.8 × 0.6
    # 目标单元尺寸 0.1 × 0.1 × 0.05
    # 并在 z 方向做 1.2 的几何级数渐密（可改为 None 或 1.0 表示均匀）
    build_structured_hex_box(Lx=1, Ly=1, Lz=1,
                             hx=0.5, hy=0.5, hz=0.5,
                             z_progression=1)

    # 可视化
    if "-nopopup" not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()
