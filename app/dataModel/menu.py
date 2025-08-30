class menuButton():
    def __init__(self,text:str,toolTip:str,iconName:str=None) -> None:
        self.text=text
        self.toolTip=toolTip
        self.iconName=iconName
        pass

class menuPane():
    def __init__(self,paneName:str) -> None:
        self.paneName=paneName
        self.btnList:list[menuButton]=[]
        pass
    def addButton(self,btn:menuButton):
        self.btnList.append(btn)

class menuTab():
    def __init__(self,tabName:str) -> None:
        self.tabName=tabName
        self.paneList:list[menuPane]=[]
        pass
    def addPane(self,pane:menuPane):
        self.paneList.append(pane)
        pass
class menuPool():
    lblTX="TX"
    lblXAxis="横轴"
    lblFrequency="频率"
    lblVType="显示类型"
    lblPosition="位置"
    lblSurface="选择面"

    home_base="主页"
    home_project="工程"
    home_simulation="求解"
    home_filter="过滤条件"
    home_filter="选择数据"
    value_filter="物理量"
    value_convert="dB值"
    surface_filter="选择面"
    axis_y="Y-Axis"
    axis_x="X-Axis"


    model_base="模型"
    model_geomtry="几何"
    model_pick="拾取"
    model_create="创建"
    model_tools="工具"
    

    excitaion_base="激励"
    excitaion_settings="Settins"
    excitaion_ports="Ports"
    excitaion_sources="Sources"
    excitaion_loads="Loads"
    request_base="求解对象"
    request_solution="Solution requests"

    mesh_base="Mesh"
    mesh_file="Mesh file"
    mesh_meshing="Meshing"
    mesh_tools="Tools"

    simualtion_base="求解器"
    simualtion_operator="仿真"
    simualtion_prop="设置"
    simualtion_excitations="激励"
    simualtion_request="求解对象"

    post_base="结果"
    post_common="导出"
    post_render="显示设置"
    post_animate="Animate"
    post_filter="过滤"

    view_base="视图"
    view_preset="模式"
    view_zoom="缩放"
    view_pan="平移"
    view_rotate="旋转"
    

    home_project_new=menuButton("新建","New project")
    home_project_open=menuButton("打开","Open project")
    home_project_save=menuButton("保存","Save project")
    home_project_saveAs=menuButton("另存为","Save project as")
    
    home_simulation_run=menuButton("分析","Run solver")
    home_simulation_stop=menuButton("停止","Stop solver")

    
    model_geomtry_import=menuButton("导入","Import model")
    model_geomtry_export=menuButton("导出","Export model")
    model_geomtry_medium=menuButton("材料设置","Medium settings")
    
    model_pick_point=menuButton("点","Pick a point")
    model_pick_edge=menuButton("线","Pick an edge")
    model_pick_face=menuButton("面","Pick a face")
    model_pick_body=menuButton("体","Pick a body")

    model_create_cuboid=menuButton("Cuboid","Create cuboid")
    model_create_sphere=menuButton("Sphere","Create sphere")
    model_create_cylinder=menuButton("Cylinder","Create cylinder")
    model_create_cone=menuButton("Cone","Create cone")
    model_create_rectangle=menuButton("Rectangle","Create rectangle")
    model_create_polygon=menuButton("Polygon","Create polygon")
    model_create_line=menuButton("Line","Create line")
    model_create_polygonLine=menuButton("Polygon line","Create polygon line")

    model_tools_exchange=menuButton("格式转换","Exchange model file")
    model_tools_color=menuButton("颜色设置","Model color and background color")
    
    

    excitaion_settings_freq=menuButton("求解设置","Frequency setting")
    excitaion_settings_power=menuButton("Power","Set the power")
    excitaion_ports_edge=menuButton("Edge port","Create an edge port")
    excitaion_sources_vol=menuButton("Voltage source","Set the source")
    excitaion_loads_addLoad=menuButton("Add load","Add a load")

    request_solution_ffr=menuButton("FarField\nradiation","FarField radiation")
    request_solution_nfr=menuButton("NearField\nradiation","NearField radiation")
    resuest_solution_tx=menuButton("发射天线","Transimitter")
    request_solution_nf=menuButton("电磁环境","Near fields")
    request_solution_emi=menuButton("电磁干扰","EMI")

    mesh_file_import=menuButton("Import","Import a mesh file")
    mesh_file_export=menuButton("Export","Export a mesh file")
    mesh_meshing_create=menuButton("Create","Create a mesh")

    
    mesh_meshing_refine=menuButton("Refine","Refine selected face")
    mesh_meshing_localsize=menuButton("Local size","Meshing local size")
    
    mesh_tools_measure=menuButton("Measure","Measure distance between two point")
    mesh_tools_transform=menuButton("Transform","Transform the model")
    mesh_tools_find=menuButton("Find","Find element by id")
    mesh_tools_points=menuButton("Points","Show vetex and postion")

    simualtion_operator_run=menuButton("分析","Run solver")
    simualtion_operator_stop=menuButton("停止","Stop solver")

    simulation_input_generate=menuButton("生成分析","Generate input file")
    simulation_exe_run=menuButton("直接求解","Run directly")
    simualtion_prop_parallel=menuButton("并行设置","Set mpi process num")

    post_common_exportData=menuButton("数据","Export data")
    post_common_exportImage=menuButton("图片","Export image")

    post_render_scalar=menuButton("颜色设置","set scalar color and range")
    post_render_points=menuButton("数据点","show/hide points of result")
    post_render_grid=menuButton("网格","show/hide grid of result")
    post_render_surface=menuButton("表面云图","show/hide surface of result")
    post_render_opacity=menuButton("透明度","set the opacity of 3d result")
    post_render_size=menuButton("尺寸","set the size zoom of 3d result")

    post_animate_play=menuButton("Play","Play animation")
    post_animate_stop=menuButton("Stop","Stop animation")
    post_animate_faster=menuButton("Faster","Increase the speed of animation")
    post_animate_slower=menuButton("Slower","Decrease the speed of animation")
    post_animate_type=menuButton("Animation\ntype","Select the type of animation")
    post_animate_settings=menuButton("Animation\nsettings","Alter the settings of animation")

    view_preset_fit=menuButton("自适应","Fit all")
    view_preset_iso=menuButton("ISO","View iso")
    view_preset_top=menuButton("顶部","View top")
    view_preset_bottom=menuButton("底部","View bottom")
    view_preset_front=menuButton("前视图","View front")
    view_preset_back=menuButton("后视图","View back")
    view_preset_left=menuButton("左视图","View left")
    view_preset_right=menuButton("右视图","View right")
    view_preset_wireframe=menuButton("线框","View wireframe")
    view_preset_shade=menuButton("实体","View shaded")

    view_zoom_in=menuButton("放大","Zoom in")
    view_zoom_out=menuButton("缩小","Zoom out")

    view_pan_left=menuButton("左","Panning left")
    view_pan_right=menuButton("右","Panning right")
    view_pan_up=menuButton("上","Panning up")
    view_pan_down=menuButton("下","Panning down")

    view_rotate_thetaAdd=menuButton("Theta+","Theta+")
    view_rotate_thetaDec=menuButton("Theta-","Theta-")
    view_rotate_phiAdd=menuButton("Phi+","Phi+")
    view_rotate_phiDec=menuButton("Phi-","Phi-")

    pass