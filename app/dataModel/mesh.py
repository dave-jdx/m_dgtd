class MeshFormat():
    emx="EMX Format"
    ff="Fluent Format"
    nf="Neutral Format"
    stl="STL Format"
    gmsh="Gmsh Format"
    gmsh2="Gmsh2 Format"
    feap="FEAP Format"
    cgns="CGNS Format"
    smf="Surface Mesh Format"
    tec="TecPlot Format"

    exportList=[ff,nf,stl,gmsh,gmsh2,feap,cgns,smf,tec]
    exportExtensionsList=[
        "EMX Format(*.meshx)",
        "Fluent Format(*.mesh)",
        "Neutral Format(*.mesh;)",
        "STL Format(*.stl)",
        "Gmsh Format(*.gmsh)",
        "Gmsh2 Format(*.gmsh2)",
        "FEAP Format(*.mesh)",
        "CGNS Format(*.cgns)",
        "Surface Mesh Format(*.mesh)",
        "TecPlot Format(*.tet)"
    ]
    importExtensionsList=[
        "Neutral format (*.mesh)"
        "Surface file (*.surf)",
        "Tet format (*.tet)",
        "STL Format(*.stl)",
    ]
    
    exportExtensions=";;".join(exportExtensionsList)
    importExtensions=";;".join(exportExtensionsList)
class Mesh():
    objIndex=256+1
    nodeName="Mesh"
    exportExtensions=MeshFormat.exportExtensions
    importExtensions=MeshFormat.importExtensions
    k_maxh="maxh"
    k_minh="minh"
    k_3dAlogrithm="3dAlogrithm"
    k_smoothing_steps="smoothing_steps"
    k_optimize_tetrahedra="optimize_tetrahedra"
    def __init__(self) -> None:
        self.fileName:str=None #mesh stl文件名包含路径
        self.name:str=None
        self.title:str=None
        self.mesh=None
        self.nv:int=None #顶点数
        self.nface:int=None #三角面个数
        self.vertices:list[tuple]=None #顶点列表(x,y,z)
        self.elements:list[tuple]=None #三角网格面 (顶点1,顶点2,顶点3)

        self.maxH:float=0.1 #最大网格尺寸
        self.localSize:dict={} #尺寸设置 体id:ti尺寸
        self.options={"maxh":0.1,
                      "minh":0,
                      "3dAlogrithm":0,
                      "smoothing_steps":1,
                      "optimize_tetrahedra":1,
                      }


# 'Neutral Format'
# 'Surface Mesh Format'
# 'DIFFPACK Format'
# 'TecPlot Format'
# 'Tochnog Format'
# 'Abaqus Format'
# 'Fluent Format'
# 'Permas Format'
# 'FEAP Format'
# 'Elmer Format'
# 'STL Format'
# 'STL Extended Format'
# 'VRML Format'
# 'Gmsh Format'
# 'Gmsh2 Format'
# 'OpenFOAM 1.5+ Format'
# 'OpenFOAM 1.5+ Compressed'
# 'JCMwave Format'
# 'TET Format'
# 'CGNS Format'
        
