#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 25 14:47:10 2018

@author: adam
"""

from PyQt5.QtGui import QIcon,QPixmap
import qtawesome as qta

from . import icons_res
_icons = {
    # 'app' : QIcon(":/images/icons/cadquery_logo_dark.svg")
    'app' : QIcon(":/images/icons/app.png"),
    "import":QIcon(":/images/icons/app.png")
    }



_icons_specs = {
    'new'  : (('fa.file-o',),{}),
    'open' : (('fa.folder-open-o',),{}),
    # borrowed from spider-ide
    'autoreload': [('fa.repeat', 'fa.clock-o'), {'options': [{'scale_factor': 0.75, 'offset': (-0.1, -0.1)}, {'scale_factor': 0.5, 'offset': (0.25, 0.25)}]}],
    'save' : (('fa.save',),{}),
    'save_as': (('fa.save','fa.pencil'),
               {'options':[{'scale_factor': 1,},
                           {'scale_factor': 0.8,
                            'offset': (0.2, 0.2)}]}),
    'run'  : (('fa.play',),{}),
    'stop'  : (('fa.stop',),{}),
    'play-circle-o'  : (('fa.play-circle-o',),{}),
    'stop-circle-o'  : (('fa.stop-circle-o',),{}),
    'th'  : (('fa.th',),{}),
    'th-list'  : (('fa.th-list',),{}),
    'wrench'  : (('fa.wrench',),{}),
    'download':(('fa.download',),{}),
    'upload':(('fa.upload',),{}),
    'cog':(('fa.cog',),{}),
    'refresh':(('fa.refresh',),{}),
    'window-restore':(('fa.window-restore',),{}),
    'delete' : (('fa.trash',),{}),
    'delete-many' : (('fa.trash','fa.trash',),
                     {'options' : \
                      [{'scale_factor': 0.8,
                         'offset': (0.2, 0.2),
                         'color': 'gray'},
                       {'scale_factor': 0.8}]}),
    'help' : (('fa.life-ring',),{}),
    'about': (('fa.info',),{}),
    'preferences' : (('fa.cogs',),{}),
    'inspect' : (('fa.cubes','fa.search'),
                 {'options' : \
                  [{'scale_factor': 0.8,
                     'offset': (0,0),
                     'color': 'gray'},{}]}),
    'screenshot' : (('fa.camera',),{}),
    'screenshot-save' : (('fa.save','fa.camera'),
                         {'options' : \
                          [{'scale_factor': 0.8},
                           {'scale_factor': 0.8,
                            'offset': (.2,.2)}]})
}

def icon(name):

    if name in _icons:
        return _icons[name]

    args,kwargs = _icons_specs[name]

    return qta.icon(*args,**kwargs)
class sysIcons():
    windowIcon=QIcon(":/images/icons/app.svg")
    windowIcon=QIcon(":/images/icons/logo_xidian.png")
    
    startupIcon=QIcon(":/images/icons/startup.png")
    startupPixmap=QPixmap(":/images/icons/startup.png")
   
class treeIcons():
    root=QIcon(":/images/icons/tree_node_root.svg")
    model=QIcon(":/images/icons/tree_model_root.svg")
    model_item=QIcon(":/images/icons/tree_model_item.svg")
    materials=QIcon(":/images/icons/tree_material_root.svg")
    mesh=QIcon(":/images/icons/tree_mesh_root.svg")
    mesh_item=QIcon(":/images/icons/tree_mesh_item.svg")
    port=QIcon(":/images/icons/tree_port_root.svg")
    port_item=QIcon(":/images/icons/tree_port_item.svg")
    excitation=QIcon(":/images/icons/tree_exc_root.svg")
    frequency=QIcon(":/images/icons/tree_freq_root.svg")
    power=QIcon(":/images/icons/tree_power_root.svg")
    source=QIcon(":/images/icons/tree_source_root.svg")
    source_item=QIcon(":/images/icons/tree_source_item.svg")
    load=QIcon(":/images/icons/tree_load_root.svg")
    load_item=QIcon(":/images/icons/tree_load_item.svg")
    request=QIcon(":/images/icons/tree_req_root.svg")
    req_time=QIcon(":/images/icons/tree_freq_root.svg")
    req_thermal=QIcon(":/images/icons/tree_nf_root.svg")
    req_nf=QIcon(":/images/icons/tree_nf_root.svg")
    req_ffr=QIcon(":/images/icons/tree_ffr_root.svg")
    req_domain=QIcon(":/images/icons/tree_nf_root.svg")
    results=QIcon(":/images/icons/tree_res_root.svg")
    result_extend=QIcon(":/images/icons/tree_res_root.svg")
    result_em=QIcon(":/images/icons/tree_res_root.svg")
    result_em_nf=QIcon(":/images/icons/tree_res_root.svg")
    result_em_domain=QIcon(":/images/icons/tree_res_root.svg")
    result_ffr=QIcon(":/images/icons/tree_res_root.svg")
    result_thermal=QIcon(":/images/icons/tree_res_root.svg")
    result_struct=QIcon(":/images/icons/tree_res_root.svg")
    ffr=QIcon(":/images/icons/tree_ffr_root.svg")
    ffr_item=QIcon(":/images/icons/tree_ffr_item.svg")
    nfr=QIcon(":/images/icons/tree_nfr_root.svg")
    nfr_item=QIcon(":/images/icons/tree_nfr_item.svg")
    nf=QIcon(":/images/icons/tree_nf_root.svg")
   
    temperature=QIcon(":/images/icons/tree_nf_root.svg")
    nf_item=QIcon(":/images/icons/tree_nf_item.svg")
    emi=QIcon(":/images/icons/tree_emi_root.svg")
    currents=QIcon(":/images/icons/tree_r_currents.svg")
    r_ffr=QIcon(":/images/icons/tree_r_ffr_root.svg")
    r_ffr_item=QIcon(":/images/icons/tree_r_ffr_item.svg")
    r_nfr=QIcon(":/images/icons/tree_r_nfr_root.svg")
    r_nfr_item=QIcon(":/images/icons/tree_r_nfr_item.svg")
    r_nf=QIcon(":/images/icons/tree_r_nf_root.svg")
    r_nf_item=QIcon(":/images/icons/tree_r_nf_item.svg")
    arrange=QIcon(":/images/icons/tree_material_root.svg")
    antenna=QIcon(":/images/icons/tree_material_root.svg")
    pf=QIcon(":/images/icons/tree_req_root.svg")
    pf_em=QIcon(":/images/icons/tree_emi_root.svg")
    pf_circuit=QIcon(":/images/icons/tree_port_root.svg")
    pf_thermal=QIcon(":/images/icons/post_ren_surface.svg")
    pf_struct=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound=QIcon(":/images/icons/tree_req_root.svg")
    pf_bound_em=QIcon(":/images/icons/tree_emi_root.svg")
    pf_bound_em_pec=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_em_pml=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_em_exf=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_circuit=QIcon(":/images/icons/tree_port_root.svg")
    pf_bound_circuit_source=QIcon(":/images/icons/tree_source_root.svg")
    pf_bound_circuit_load=QIcon(":/images/icons/tree_load_root.svg")
    pf_bound_thermal=QIcon(":/images/icons/post_ren_surface.svg")
    pf_bound_thermal_dirichlet=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_thermal_convection=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_thermal_radiation=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_thermal_source=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_struct=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_struct_dirichlet=QIcon(":/images/icons/tree_material_root.svg")
    pf_bound_struct_force=QIcon(":/images/icons/tree_material_root.svg")
    face=QIcon(":/images/icons/tree_material_root.svg")
    solid=QIcon(":/images/icons/tree_model_root.svg")

    gdtd_ffr=QIcon("./icons/dgtd/结果分析-方向图.png")
    gdtd_2d_ffr=QIcon("./icons/dgtd/2D方向图.png")
    gdtd_3d_ffr=QIcon("./icons/dgtd/3D方向图.png")

    gdtd_result_em=QIcon("./icons/dgtd/电场值.png")
    gdtd_result_em_points=QIcon("./icons/dgtd/结果分析-电场值-观察点.png")
    gdtd_result_em_domain=QIcon("./icons/dgtd/结果分析-电场值-观察域.png")

    gdtd_result_thermal=QIcon("./icons/dgtd/温度值.png")
    gdtd_result_thermal_points=QIcon("./icons/dgtd/结果分析-温度值-观察点.png")
    gdtd_result_thermal_domain=QIcon("./icons/dgtd/结果分析-温度值-观察域.png")

    gdtd_result_struct=QIcon("./icons/dgtd/位移量.png")
    gdtd_result_struct_domain=QIcon("./icons/dgtd/结果分析-位移量-观察域.png")

    gdtd_model=QIcon("./icons/dgtd/模型.png")
    gdtd_model_item=QIcon("./icons/dgtd/模型-item.png")
    gdtd_component=QIcon("./icons/dgtd/组件.png")
    gdtd_component_item=QIcon("./icons/dgtd/组件-item.png")

    gdtd_pf=QIcon("./icons/dgtd/物理场.png")
    gdtd_pf_struct=QIcon("./icons/dgtd/物理场-结构.png")

    gdtd_bound_pec=QIcon("./icons/dgtd/PEC.png")

    gdtd_bound_struct=QIcon("./icons/dgtd/边界源-结构.png")
    gdtd_bound_struct_dirichlet=QIcon("./icons/dgtd/固定位移.png")
    gdtd_bound_struct_force=QIcon("./icons/dgtd/外力.png")

    gdtd_bound_thermal_dirichlet=QIcon("./icons/dgtd/固定温度.png")
    gdtd_bound_thermal_convection=QIcon("./icons/dgtd/热对流.png")
    gdtd_bound_thermal_radiation=QIcon("./icons/dgtd/热辐射.png")
    gdtd_bound_thermal_source=QIcon("./icons/dgtd/热源.png")

    gdtd_port_line=QIcon("./icons/dgtd/线端口.png")
    gdtd_port_face=QIcon("./icons/dgtd/面端口.png")

    gdtd_req=QIcon("./icons/dgtd/求解设置.png")
    gdtd_req_points=QIcon("./icons/dgtd/求解设置-观察点.png")
    gdtd_req_domain=QIcon("./icons/dgtd/求解设置-观察域.png")

    

    pass
class menuIcons():
    home_new=QIcon(":/images/icons/home_new.svg")
    home_open=QIcon(":/images/icons/home_open.svg")
    home_save=QIcon(":/images/icons/home_save.svg")
    home_saveAs=QIcon(":/images/icons/home_save_as.svg")
    home_run=QIcon(":/images/icons/home_run")
    home_stop=QIcon(":/images/icons/home_stop")
    model_import=QIcon(":/images/icons/model_import.svg")
    model_export=QIcon(":/images/icons/model_export.svg")
    model_medium=QIcon((":/images/icons/tree_material_root.svg"))
    model_exchange=QIcon(":/images/icons/model_convert.svg")
    model_color=QIcon(":/images/icons/model_color.svg")
    model_pick_point=QIcon(":/images/icons/model_pick_point.svg")
    model_pick_edge=QIcon(":/images/icons/model_pick_edge.svg")
    model_pick_face=QIcon(":/images/icons/model_pick_face.svg")
    model_pick_body=QIcon(":/images/icons/model_pick_body.svg")
    model_cuboid=QIcon(":/images/icons/model_cuboid.svg")
    model_sphere=QIcon(":/images/icons/model_sphere.svg")
    model_cylinder=QIcon(":/images/icons/model_cylinder.svg")
    model_cone=QIcon(":/images/icons/model_cone.svg")
    mode_rectangle=QIcon(":/images/icons/model_rectangle.svg")
    model_polygon=QIcon(":/images/icons/model_polygon.svg")
    model_line=QIcon(":/images/icons/model_line.svg")
    mode_pline=QIcon(":/images/icons/model_pline.svg")
    model_pick_select=QIcon("./icons/select.png")
    

    exc_frequency=QIcon(":/images/icons/exc_frequency.svg")
    exc_power=QIcon(":/images/icons/exc_power.svg")
    exc_v_source=QIcon(":/images/icons/exc_v_source.svg")
    exc_add_load=QIcon(":/images/icons/exc_add_load.svg")
    exc_edge_port=QIcon(":/images/icons/exc_edge_port.svg")
    pf_em=QIcon(":/images/icons/tree_emi_root.svg")
    pf_circuit=QIcon(":/images/icons/tree_port_root.svg")
    pf_thermal=QIcon(":/images/icons/post_ren_surface.svg")
    pf_struct=QIcon(":/images/icons/tree_material_root.svg")

    mesh_import=QIcon(":/images/icons/mesh_import.svg")
    mesh_export=QIcon(":/images/icons/mesh_export.svg")
    mesh_create=QIcon(":/images/icons/mesh_create.svg")
    mesh_refine=QIcon(":/images/icons/mesh_refine.svg")
    mesh_find=QIcon(":/images/icons/mesh_find.svg")
    mesh_options=QIcon(":/images/icons/mesh_options.svg")
    mesh_transform=QIcon(":/images/icons/mesh_transform.svg")
    mesh_measure=QIcon(":/images/icons/mesh_measure.svg")
    mesh_points=QIcon(":/images/icons/post_ren_points.svg")

    req_ffr=QIcon(":/images/icons/req_ffr.svg")
    req_nfr=QIcon(":/images/icons/req_nfr.svg")
    req_nf=QIcon(":/images/icons/req_nf.svg")
    req_emi=QIcon(":/images/icons/req_emi.svg")
    req_tx=QIcon(":/images/icons/req_emi.svg")
    req_rx=QIcon(":/images/icons/req_nfr.svg")

    sim_run=QIcon(":/images/icons/sim_run.svg")
    sim_stop=QIcon(":/images/icons/sim_stop.svg")
    sim_p=QIcon(":/images/icons/sim_p.svg")

    post_export_data=QIcon(":/images/icons/post_export_data.svg")
    post_export_img=QIcon(":/images/icons/post_export_img.svg")

    post_ren_scalar=QIcon(":/images/icons/post_ren_scalar.svg")
    post_ren_points=QIcon(":/images/icons/post_ren_points.svg")
    post_ren_grid=QIcon(":/images/icons/post_ren_grid.svg")
    post_ren_surface=QIcon(":/images/icons/post_ren_surface.svg")
    post_ren_opacity=QIcon(":/images/icons/post_ren_opacity.svg")
    post_ren_size=QIcon(":/images/icons/post_ren_size.svg")

    post_ani_play=QIcon(":/images/icons/post_ani_play.svg")
    post_ani_stop=QIcon(":/images/icons/post_ani_stop.svg")
    post_ani_faster=QIcon(":/images/icons/post_ani_faster.svg")
    post_ani_slower=QIcon(":/images/icons/post_ani_slower.svg")
    post_ani_type=QIcon(":/images/icons/post_ani_type.svg")
    post_ani_settings=QIcon(":/images/icons/post_ani_settings.svg")


    view_fit=QIcon(":/images/icons/view_fit.svg")
    view_iso=QIcon(":/images/icons/view_iso.svg")
    view_top=QIcon(":/images/icons/view_top.svg")
    view_bottom=QIcon(":/images/icons/view_bottom.svg")
    view_front=QIcon(":/images/icons/view_front.svg")
    view_back=QIcon(":/images/icons/view_back.svg")
    view_left=QIcon(":/images/icons/view_left.svg")
    view_right=QIcon(":/images/icons/view_right.svg")
    view_wireframe=QIcon(":/images/icons/view_wireframe.svg")
    view_shaded=QIcon(":/images/icons/view_shaded.svg")
    view_zoom_in=QIcon(":/images/icons/view_zoom_in.svg")
    view_zoom_out=QIcon(":/images/icons/view_zoom_out.svg")
    view_pan_left=QIcon(":/images/icons/view_pan_left.svg")
    view_pan_right=QIcon(":/images/icons/view_pan_right.svg")
    view_pan_up=QIcon(":/images/icons/view_pan_up.svg")
    view_pan_down=QIcon(":/images/icons/view_pan_down.svg")
    view_r_thetaAdd=QIcon(":/images/icons/view_r_thetaAdd.svg")
    view_r_thetaDec=QIcon(":/images/icons/view_r_thetaDec.svg")
    view_r_phiAdd=QIcon(":/images/icons/view_r_phiAdd.svg")
    view_r_phiDec=QIcon(":/images/icons/view_r_phiDec.svg")
    about_help=QIcon("icons/help.png")
    about_license=QIcon("icons/license.png")
    

    pass