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
    lblFrequency="Frequency"
    lblVType="V-Type"
    lblPosition="Z position"
    lblSurface="Plot type"

    home_base="Home"
    home_project="Project"
    home_simulation="Simulation"
    home_filter="Result filter"
    home_filter="Choose"
    value_filter="Values"
    axis_y="Y-Axis"
    axis_x="X-Axis"


    model_base="Model"
    model_geomtry="Geometry"
    model_pick="Pick"
    model_create="Create shapes"
    model_tools="Tools"

    excitaion_base="Port/Excitaion"
    excitaion_settings="Settins"
    excitaion_ports="Ports"
    excitaion_sources="Sources"
    excitaion_loads="Loads"
    request_base="Request"
    request_solution="Solution requests"

    mesh_base="Mesh"
    mesh_file="Mesh file"
    mesh_meshing="Meshing"
    mesh_tools="Tools"

    simualtion_base="Simulation"
    simualtion_operator="Operator"
    simualtion_prop="Properties"

    post_base="Post-Processing"
    post_common="Common"
    post_render="Rendering"
    post_animate="Animate"
    post_filter="Filter"

    view_base="View"
    view_preset="Preset Views"
    view_zoom="Zomming"
    view_pan="Panning"
    view_rotate="Rotate"
    

    home_project_new=menuButton("New","New project")
    home_project_open=menuButton("Open","Open project")
    home_project_save=menuButton("Save","Save project")
    home_project_saveAs=menuButton("Save As","Save project as")
    
    home_simulation_run=menuButton("Run","Run solver")
    home_simulation_stop=menuButton("Stop","Stop solver")
    
    model_geomtry_import=menuButton("Import","Import model")
    model_geomtry_export=menuButton("Export","Export model")
    
    model_pick_point=menuButton("Point","Pick a point")
    model_pick_edge=menuButton("Edge","Pick an edge")
    model_pick_face=menuButton("Face","Pick a face")
    model_pick_body=menuButton("Body","Pick a body")

    model_create_cuboid=menuButton("Cuboid","Create cuboid")
    model_create_sphere=menuButton("Sphere","Create sphere")
    model_create_cylinder=menuButton("Cylinder","Create cylinder")
    model_create_cone=menuButton("Cone","Create cone")
    model_create_rectangle=menuButton("Rectangle","Create rectangle")
    model_create_polygon=menuButton("Polygon","Create polygon")
    model_create_line=menuButton("Line","Create line")
    model_create_polygonLine=menuButton("Polygon line","Create polygon line")

    model_tools_exchange=menuButton("Exchange","Exchange model file")
    model_tools_color=menuButton("Color","Model color and background color")
    
    

    excitaion_settings_freq=menuButton("Frequency","Frequency setting")
    excitaion_settings_power=menuButton("Power","Set the power")
    excitaion_ports_edge=menuButton("Edge port","Create an edge port")
    excitaion_sources_vol=menuButton("Voltage source","Set the source")
    excitaion_loads_addLoad=menuButton("Add load","Add a load")

    request_solution_ffr=menuButton("FarField\nradiation","FarField radiation")
    request_solution_nfr=menuButton("NearField\nradiation","NearField radiation")
    request_solution_nf=menuButton("Near fields","Near fields")
    request_solution_emi=menuButton("EMI","EMI")

    mesh_file_import=menuButton("Import","Import a mesh file")
    mesh_file_export=menuButton("Export","Export a mesh file")
    mesh_meshing_create=menuButton("Create","Create a mesh")

    
    mesh_meshing_refine=menuButton("Refine","Refine selected face")
    mesh_meshing_localsize=menuButton("Local size","Meshing local size")
    
    mesh_tools_measure=menuButton("Measure","Measure distance between two point")
    mesh_tools_transform=menuButton("Transform","Transform the model")
    mesh_tools_find=menuButton("Find","Find element by id")
    mesh_tools_points=menuButton("Points","Show vetex and postion")

    simualtion_operator_run=menuButton("Run","Run solver")
    simualtion_operator_stop=menuButton("Stop","Stop solver")
    simualtion_prop_parallel=menuButton("Parallel","Set mpi process num")

    post_common_exportData=menuButton("Export\ndata","Export data")
    post_common_exportImage=menuButton("Export\nimage","Export image")

    post_render_scalar=menuButton("Scalar","set scalar color and range")
    post_render_points=menuButton("Points","show/hide points of result")
    post_render_grid=menuButton("Grid","show/hide grid of result")
    post_render_surface=menuButton("Surface","show/hide surface of result")
    post_render_opacity=menuButton("Opacity","set the opacity of 3d result")
    post_render_size=menuButton("Size","set the size zoom of 3d result")

    post_animate_play=menuButton("Play","Play animation")
    post_animate_stop=menuButton("Stop","Stop animation")
    post_animate_faster=menuButton("Faster","Increase the speed of animation")
    post_animate_slower=menuButton("Slower","Decrease the speed of animation")
    post_animate_type=menuButton("Animation\ntype","Select the type of animation")
    post_animate_settings=menuButton("Animation\nsettings","Alter the settings of animation")

    view_preset_fit=menuButton("Fit","Fit all")
    view_preset_iso=menuButton("ISO","View iso")
    view_preset_top=menuButton("Top","View top")
    view_preset_bottom=menuButton("Bottom","View bottom")
    view_preset_front=menuButton("Front","View front")
    view_preset_back=menuButton("Back","View back")
    view_preset_left=menuButton("Left","View left")
    view_preset_right=menuButton("Right","View right")
    view_preset_wireframe=menuButton("Wireframe","View wireframe")
    view_preset_shade=menuButton("Shaded","View shaded")

    view_zoom_in=menuButton("Zoom in","Zoom in")
    view_zoom_out=menuButton("Zoom out","Zoom out")

    view_pan_left=menuButton("Left","Panning left")
    view_pan_right=menuButton("Right","Panning right")
    view_pan_up=menuButton("Up","Panning up")
    view_pan_down=menuButton("Down","Panning down")

    view_rotate_thetaAdd=menuButton("Theta+","Theta+")
    view_rotate_thetaDec=menuButton("Theta-","Theta-")
    view_rotate_phiAdd=menuButton("Phi+","Phi+")
    view_rotate_phiDec=menuButton("Phi-","Phi-")

    pass