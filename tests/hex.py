import gmsh
import sys

gmsh.initialize()

gmsh.model.add("structured_hex")

# ==========================
# 1. 建立一个立方体
# ==========================
# 参数：x, y, z, dx, dy, dz
cube = gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
gmsh.model.occ.synchronize()

# ==========================
# 2. 获取立方体的边、面、体
# ==========================
lines = gmsh.model.getEntities(dim=1)   # 所有边
surfs = gmsh.model.getEntities(dim=2)   # 所有面
vols  = gmsh.model.getEntities(dim=3)   # 体

# ==========================
# 3. 设置结构化划分
# ==========================
# 每条边分成 5 段（可调节）
for line in lines:
    gmsh.model.mesh.setTransfiniteCurve(line[1], 5)

# 每个面设置为 transfinite，并重组为四边形
for surf in surfs:
    gmsh.model.mesh.setTransfiniteSurface(surf[1])
    gmsh.model.mesh.setRecombine(2, surf[1])

# 设置体为 transfinite，并重组为六面体
for vol in vols:
    gmsh.model.mesh.setTransfiniteVolume(vol[1])
    gmsh.model.mesh.setRecombine(3, vol[1])

# ==========================
# 4. 生成网格
# ==========================
gmsh.model.mesh.generate(3)

# 保存网格文件
gmsh.write("structured_hex.msh")

# ==========================
# 5. 可视化
# ==========================
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
pause()
