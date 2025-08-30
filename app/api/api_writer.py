# from ngsolve import Mesh
from ..dataModel.media import Media,MediaItem,Dielectric,Metal
from ..dataModel.mediaN import MediaBase,Isotropic,Anisotropic,DispersiveProp,Dispersive
from ..dataModel.frequency import Frequency
# from ..dataModel.power import Power
from ..dataModel.antenna import Antenna
from ..dataModel.nf import NF
from ..dataModel.ffr import FFR
from ..dataModel.pf import (PF,PF_EBase,PF_EM,PF_Circuit,PF_Thermal,PF_Struct,PF_Circuit_Source,PF_Struct_Force,PF_Thermal_Base)
from ..dataModel.requestParam import(RequestParam,RequestParam_domain,RequestParam_temperature,RequestParam_time)
import os,math, traceback
from . import api_model
def write_medialLibrary_SBR(fname:str,isotropicList:list,dispersiveList:list):
    '''
    Write media library to text
    '''
    sbr_dilectric="Dielectric" # SBR介质
    sbr_metal="Metal"
    sbr_metal_threshold=1000
    newline="\n"
    splitext="\t"
    c_tip=get_comment("注意："+newline
+"1.需要输出所有注释"+newline
+"2.一行中的间隔使用制表符"+newline
+"3.两种媒质间空一行"+newline
+"4.频率需要转换Hz输出"+newline)
    c_begin=get_comment("Begin_Material")
    c_end=get_comment("End_Material")
    c1=get_comment("介质材料编号，用于与模型绑定")
    c2_d=get_comment("标明是电介质")
    c2_m=get_comment("标明是金属")
    c3=get_comment("频点个数")
    c4_d=get_comment("频率/hz、介电常数实部、介电常数虚部、磁导率实部、磁导率虚部")
    c4_m=get_comment("电导率,单位S/m")
    c5=get_comment("根据用户定义的材料名称输出")
    
    # print(fname)
    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(fname,"w",encoding="utf-8") as f:
            mIndex=0
            f.write(c_tip+newline)
            f.write(newline)
            f.write(c_begin)

            for item in isotropicList:
                m_iso:Isotropic=item
                if(float(m_iso.eConductivity)<sbr_metal_threshold):#非金属》1000为金属
                    continue
                f.write(str(mIndex)+splitext+c1+newline)
                f.write(sbr_metal+splitext+c2_m+newline)
                f.write(str(m_iso.eConductivity)+splitext+c4_m+newline)
                f.write(m_iso.name+ splitext+c5+newline)
            
            for item in dispersiveList:
                m:Dispersive=item
                mIndex=mIndex+1
                f.write(newline)
                f.write(str(mIndex)+splitext+c1+newline)
                f.write(sbr_dilectric+splitext+c2_d+newline)
                f.write(str(len(m.itemList))+splitext+c3+newline)
                fIndex=0
                for freq in m.itemList:
                    freq:Dielectric=freq
                    c=(str(freq.frequency)+splitext
                            +str(freq.permittivity_real)+splitext
                            +str(freq.permittivity_imag)+splitext
                            +str(freq.permeability_real)+splitext
                            +str(freq.permeability_imag))
                    f.write(c)
                    if(fIndex==0):
                        f.write(splitext+c4_d+newline)
                    else:
                        f.write(newline)
                    fIndex=fIndex+1
                f.write(m.name+splitext+c5+newline)
            f.write(c_end+newline)
        return (1,"success",None)
    except Exception as e:
        
        return (-1,"failed "+str(e),e)
    pass
def write_mediaLibrary_fem(fname:str,mediaList):
    # Write media to text
    newline="\n"
    splitext="\t"
    c_tip=get_comment("计算对象涉及的材料类别总数")
    c_tip_r=get_comment("材料索引号，用于与模型绑定")
    c_tip_c=get_comment("依次为材料的相对介电常数、相对磁导率、电导率(S/m)、热导率(W/(m*K))、密度(kg/m3)、比热容(J/(kg*K))、杨氏模量（Pa）、泊松比、热膨胀系数(1/K)")
    c_begin=get_comment("Begin_Materials")
    c_end=get_comment("End_Materials")

    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(fname,"w",encoding="utf-8") as f:
            mIndex=0
            f.write(c_begin)
            f.write(newline)
            f.write(c_tip+newline)
            f.write(str(len(mediaList))+newline)
            
            for item in mediaList:
                m:Isotropic=item
                mIndex=mIndex+1
                f.write(c_tip_r+newline)
                f.write(str(mIndex)+newline)
                f.write(c_tip_c+newline)
                f.write(splitext.join(map(str,[m.permittivity,
                                              m.permeability,
                                              m.eConductivity,
                                              m.tConductivity,
                                              m.density,
                                              m.specificHeat,
                                              m.youngModulus,
                                              m.poissonRatio,
                                              m.thermalExpansion]))+newline)

          
            f.write(c_end+newline)
        return (1,"success",None)
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)

def write_mediaLibrary(fname:str,mediaList):
    # Write media to text
    newline="\n"
    splitext="\t"
    c_tip=get_comment("注意："+newline
+"1.需要输出所有注释"+newline
+"2.一行中的间隔使用制表符"+newline
+"3.两种媒质间空一行"+newline
+"4.频率需要转换Hz输出"+newline)
    c_begin=get_comment("Begin_Material")
    c_end=get_comment("End_Material")
    c1=get_comment("介质材料编号，用于与模型绑定")
    c2_d=get_comment("标明是电介质")
    c2_m=get_comment("标明是金属")
    c3=get_comment("频点个数")
    c4_d=get_comment("频率/hz、介电常数实部、介电常数虚部、磁导率实部、磁导率虚部")
    c4_m=get_comment("电导率,单位S/m")
    c5=get_comment("根据用户定义的材料名称输出")
    
    # print(fname)
    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(fname,"w",encoding="utf-8") as f:
            mIndex=0
            f.write(c_tip+newline)
            f.write(newline)
            f.write(c_begin)
            
            for item in mediaList:
                m:MediaItem=item
                mIndex=mIndex+1
                f.write(newline)
                if(m.media.type==Media.dielectric):
                    f.write(str(mIndex)+splitext+c1+newline)
                    f.write(m.media.type+splitext+c2_d+newline)
                    f.write(str(len(m.freqList))+splitext+c3+newline)
                    fIndex=0
                    for freq in m.freqList:
                        freq:Dielectric=freq
                        c=(str(freq.frequency)+splitext
                                +str(freq.permittivity_real)+splitext
                                +str(freq.permittivity_imag)+splitext
                                +str(freq.permeability_real)+splitext
                                +str(freq.permeability_imag))
                        f.write(c)
                        if(fIndex==0):
                            f.write(splitext+c4_d+newline)
                        else:
                            f.write(newline)
                        fIndex=fIndex+1
                    f.write(m.media.name+splitext+c5+newline)

                elif(m.media.type==Media.metal):
                    m_metal:Metal=m.freqList[0]
                    f.write(str(mIndex)+splitext+c1+newline)
                    f.write(m.media.type+splitext+c2_m+newline)
                    f.write(str(m_metal.conductivity)+splitext+c4_m+newline)
                    f.write(m.media.name+ splitext+c5+newline)

                else:
                    pass
            f.write(c_end+newline)
        return (1,"success",None)
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
def write_bound_fem(fname,pf:PF,mediumDic:dict={},defaultMediumIndex=-1):
    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        newline="\n"
        splitext="\t"
        c_id=get_comment("边界条件索引号 用几何建模对应的面编号即可 注意每个面编号必须独一无二 用于与模型绑定")
        c_em_begin=get_comment("Begin_EM_Boundary")
        c_em_end=get_comment("End_EM_Boundary")
        c_em_num=get_comment("电磁边界条件对应总个数")
        c_em_num_pec=get_comment("PEC边界条件对应总个数")
        c_em_num_port_s=get_comment("Port_S边界条件对应总个数")
        c_em_num_port_l=get_comment("Port_L边界条件对应总个数")
        c_em_type=get_comment("边界条件类别，电磁边界包括PEC、Port_S、Port_L等类别")
        
        c_em_source=get_comment("边界条件类别，激励端口一般只有一个")
        c_em_source_type=get_comment("加源类型，1：正弦波，2：调制高斯脉冲 ")
        c_em_source_value=get_comment("加源的幅度（V）、频率（Hz）、脉冲宽度（s）、时延（s） （如果是正弦波，则后两项默认为0；如果是调制高斯脉冲，则需要用户输入；如果用户自定义波形，则4项都输出为0）")
        c_em_load=get_comment("边界条件类别，负载端口存在多个的情况")
        c_em_load_surface=get_comment("端口面的宽度和高度,单位为m")
        c_em_load_value=get_comment("负载元件的值，电阻单位：欧姆")

        c_thermal_begin=get_comment("Begin_Heat_Boundary")
        c_thermal_end=get_comment("End_Heat_Boundary")
        c_thermal_num=get_comment("热边界条件对应总个数")
        c_thermal_type=get_comment("边界条件类别，热边界包括Dirichlet、Convection、Radiation等类别")
        c_thermal_dirichlet=get_comment("Dirichlet边界温度值")
        c_thermal_convection=get_comment("Convection边界对流换热系数值")
        c_thermal_radiation=get_comment("Radiation边界热辐射率数值")

        c_thermal_source_begin=get_comment("Begin_Heat_Source")
        c_thermal_source_end=get_comment("End_Heat_Source")
        c_thermal_source_num=get_comment("热源总个数")
        c_thermal_source_tip=get_comment("两个数据，依次为：热源区域的材料号；该热源的瓦数")
        

        c_struct_dirchilet_begin=get_comment("Begin_Mechanics_Boundary")
        c_struct_dirchilet_end=get_comment("End_Mechanics_Boundary")
        c_struct_dirchilet_num=get_comment("结构边界条件对应总个数")
        c_struct_dirchilet_num=get_comment("结构边界条件对应总个数")

        c_struct_fore_begin=get_comment("Begin_Mechanics_Source")
        c_struct_fore_end=get_comment("End_Mechanics_Source")
        c_struct_dirichlet=get_comment("边界条件类别，结构边界包括Fix")
        c_struct_force_num=get_comment("结构加源点对应总个数")
        c_struct_force=get_comment("施加外力点的编号和坐标值x y z及外力大小fx fy fz")

        c_surface="0.001  0.001            <!--端口面的宽度和高度,单位为m-->"

        v_em_num=len(pf.em.em_pec_dic)+len(pf.circuit.circuit_load_dic)+len(pf.circuit.circuit_source_dic)
        v_em_num_pec=len(pf.em.em_pec_dic)
        v_em_num_port_s=len(pf.circuit.circuit_source_dic)
        v_em_num_port_l=len(pf.circuit.circuit_load_dic)
        v_em_num=str(v_em_num)
        v_em_num_pec=str(v_em_num_pec)
        v_em_num_port_s=str(v_em_num_port_s)
        v_em_num_port_l=str(v_em_num_port_l)
        v_thermal_num=len(pf.thermal.thermal_dirichlet_dic)+len(pf.thermal.thermal_convection_dic)+len(pf.thermal.thermal_radiation_dic)
        v_thermal_num=str(v_thermal_num)

        v_thermal_source_num=str(len(pf.thermal.thermal_source_dic))

        v_struct_dirchilet_num=len(pf.struct.struct_dirichlet_dic)
        v_struct_dirchilet_num=str(v_struct_dirchilet_num)
        v_struct_force_num= len(pf.struct.struct_force_dic)
        v_struct_force_num=str(v_struct_force_num)

        c_circuit_source_type=get_comment("用户添加的加源端口类型，0代表添加线端口，1代表添加面端口")
        v_circuit_source_type="0" #默认是线端口
        for k in pf.circuit.circuit_source_dic:
            sourceObj:PF_Circuit_Source=pf.circuit.circuit_source_dic[k]
            if(hasattr(sourceObj,"source_type") and sourceObj.source_type==1):
                v_circuit_source_type="1"
                break

        with open(fname,"w",encoding="utf-8") as f:
            f.write(c_em_begin+newline)
            f.write(v_em_num+splitext+c_em_num+newline)
            f.write(newline)

            f.write(v_em_num_pec+splitext+c_em_num_pec+newline)
            f.write(newline)
            for key in pf.em.em_pec_dic:
                f.write(str(key+1)+splitext+c_id+newline)
                f.write("PEC"+splitext+c_em_type+newline)
                f.write(newline)
            
            #添加端口类型节点
            f.write(v_circuit_source_type+splitext+c_circuit_source_type+newline)
            f.write(newline)

            f.write(v_em_num_port_s+splitext+c_em_num_port_s+newline)
            f.write(newline)
            for key in pf.circuit.circuit_source_dic:
                v:PF_Circuit_Source=pf.circuit.circuit_source_dic[key]
                f.write(str(key+1)+splitext+c_id+newline)
                f.write("Port_S"+splitext+c_em_source+newline)
                v_length=(0,0)
                if(hasattr(v,"uv")):
                    v_length=v.uv
                c_surface=f"{v_length[0]/1000}  {v_length[1]/1000}            <!--端口面的宽度和高度,单位为m-->"
                f.write(c_surface+newline)
                f.write(str(v.waveType+1)+splitext+c_em_source_type+newline)
                f.write(splitext.join(map(str,[v.amplitude,v.frequency,v.pulseWidth,v.delay]))+splitext+c_em_source_value+newline)
                f.write(newline)

            f.write(v_em_num_port_l+splitext+c_em_num_port_l+newline)
            f.write(newline)
            for key in pf.circuit.circuit_load_dic:
                v=pf.circuit.circuit_load_dic[key]
                #电阻
                v_load=v[0]
                v_length=v[1]
                c_surface=f"{v_length[0]/1000}  {v_length[1]/1000}            <!--端口面的宽度和高度,单位为m-->"
                f.write(str(key+1)+splitext+c_id+newline)
                f.write("Port_L"+splitext+c_em_load+newline)
                f.write(c_surface+newline)
                f.write(str(v_load)+splitext+c_em_load_value+newline)
                f.write(newline)
            f.write(c_em_end+newline)

            f.write(c_thermal_begin+newline)
            f.write(v_thermal_num+splitext+c_thermal_num+newline)
            f.write(newline)

            for k in pf.thermal.thermal_dirichlet_dic:
                v:PF_Thermal_Base=pf.thermal.thermal_dirichlet_dic[k]
                f.write(str(k+1)+splitext+c_id+newline)
                f.write("Dirichlet"+splitext+c_thermal_type+newline)
                f.write(str(v.value)+splitext+c_thermal_dirichlet+newline)
                f.write(newline)
            for k in pf.thermal.thermal_convection_dic:
                v:PF_Thermal_Base=pf.thermal.thermal_convection_dic[k]
                f.write(str(k+1)+splitext+c_id+newline)
                f.write("Convection"+splitext+c_thermal_type+newline)
                f.write(str(v.value)+splitext+c_thermal_convection+newline)
                f.write(newline)
            for k in pf.thermal.thermal_radiation_dic:
                v:PF_Thermal_Base=pf.thermal.thermal_radiation_dic[k]
                f.write(str(k+1)+splitext+c_id+newline)
                f.write("Radiation"+splitext+c_thermal_type+newline)
                f.write(str(v.value)+splitext+c_thermal_radiation+newline)
                f.write(newline)
            f.write(c_thermal_end+newline)
            f.write(newline)

            f.write(c_thermal_source_begin+newline)
            f.write(v_thermal_source_num+splitext+c_thermal_source_num+newline)

            for k in pf.thermal.thermal_source_dic:
                v:PF_Thermal_Base=pf.thermal.thermal_source_dic[k]
                mIndex=defaultMediumIndex
                if(mediumDic!=None and mediumDic.get(k)!=None):
                    mIndex=mediumDic[k]
                f.write(str(mIndex+1)+splitext+str(v.value)+splitext+c_thermal_source_tip+newline)

            f.write(c_thermal_source_end+newline)
            f.write(newline)

            f.write(c_struct_dirchilet_begin+newline)
            f.write(v_struct_dirchilet_num+splitext+c_struct_dirchilet_num+newline)
            f.write(newline)
            for k in pf.struct.struct_dirichlet_dic:
                v=pf.struct.struct_dirichlet_dic[k]
                f.write(str(k+1)+splitext+c_id+newline)
                f.write("Fix"+splitext+c_struct_dirichlet+newline)
                f.write(newline)
            f.write(c_struct_dirchilet_end+newline)
            f.write(newline)

            f.write(c_struct_fore_begin+newline)
            f.write(v_struct_force_num+splitext+c_struct_force_num+newline)
            f.write(newline)
            for k in pf.struct.struct_force_dic:
                v:PF_Struct_Force=pf.struct.struct_force_dic[k]
                vx=[v.pointId+1, v.point_xyz[0],v.point_xyz[1],v.point_xyz[2],v.force_xyz[0],v.force_xyz[1],v.force_xyz[2]]
                f.write(splitext.join(map(str,vx))+splitext+c_struct_force+newline)
                # f.write(newline)
            f.write(c_struct_fore_end+newline)
            f.write(newline)

        return(1,"sucess",None)


        pass
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
        pass
def write_param_fem(fname,pf:PF,requestParam:RequestParam,points:list,ffrObj:FFR,pml_param:tuple):
    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        newline="\n"
        splitext="\t"
        c_begin=get_comment("Begin_Solution Parameters")
        c_end=get_comment("End_Solution Parameters")
        c_type=get_comment("用户添加的物理场类型，对应电磁、电路、热、结构，1代表添加了，0代表没添加")
        c_time1=get_comment("用户设置的电磁_电路时间步长和时间步数，时间步长单位是s")
        # c_time2=get_comment("用户设置的多物理时间步长比例因子") #去掉不在使用
        c_nf_num=get_comment("用户设置观察点个数 0代表没设置")
        c_nf_row=get_comment("用户设置的观察点{0}的X，Y，Z坐标值，单位是m")
        c_domain=get_comment("用户设置的观察域，第一个数字代表电磁求解域是否设置，第二个数字代表热和结构求解域是否设置； 0代表没设置 1代表设置了")
        c_domain_step=get_comment("用户设置的观察域时间步,第一个代表电磁求解域时间步，第二个代表热和结构求解域时间步")
        c_ffr_theta=get_comment("方向图：设置信息和之前快速多极子项目类似：theta_start(degree) theta_end(degree) theta_increment(degree)")
        c_ffr_phi=get_comment("方向图：设置信息和之前快速多极子项目类似：phi_start(degree) phi_end(degree) phi_increment(degree)")
        c_thermal_start=get_comment("用户设置的初始温度，单位为K")
        c_thermal_env=get_comment("用户设置的环境温度，单位为K")
        c_pml=get_comment("用户设置的壳体厚度，后面六个数据依次为PML区域内边界的xmax、ymax、zmax、xmin、ymin、zmin")
        c_freq=get_comment("用户设置方向图对应的频点，单位为Hz")

        c_time_heat=get_comment("用户设置的热时间步长和时间步数，时间步长单位是s") #去掉不在使用
        
        timeObj:RequestParam_time=requestParam.reqTime
        domainObj:RequestParam_domain=requestParam.reqDomain #观察域设置
        thermalObj:RequestParam_temperature=requestParam.reqTemperature

        if(not hasattr(timeObj,"timeStep_heat")):
            timeObj.timeStep_heat="1"
            timeObj.timeStepNum_heat=1
            timeObj.timeStepFactor_heat=1

        calTypeList=[0,0,0,0]
        if(pf.em.used):
            calTypeList[0]=1
        if(pf.circuit.used):
            calTypeList[1]=1
        if(pf.thermal.used):
            calTypeList[2]=1
        if(pf.struct.used):
            calTypeList[3]=1
        v_type=splitext.join(map(str,calTypeList))

        v_time1=splitext.join(map(str,[timeObj.timeStep,timeObj.timeStepNum]))
        # v_time2=str(timeObj.timeStepFactor)
        v_time_heart=splitext.join(map(str,[timeObj.timeStep_heat,timeObj.timeStepNum_heat]))

        v_nf_num=str(len(points))
        domainList=[0,0]
        if(domainObj.domain1[0]):
            domainList[0]=1
        if(domainObj.domain2[0]):
            domainList[1]=1
        v_domain=splitext.join(map(str,domainList))
        v_domain_step=splitext.join(map(str,[domainObj.domain1[1],domainObj.domain2[1]]))
        v_ffr_theta=""
        v_ffr_phi=""
        v_freq=""
        if(ffrObj!=None):
            v_ffr_theta=splitext.join(map(str,[ffrObj.theStart,ffrObj.theEnd,ffrObj.theIncrement]))
            v_ffr_phi=splitext.join(map(str,[ffrObj.phiStart,ffrObj.phiEnd,ffrObj.phiIncrement]))
            v_freq=ffrObj.freq

        v_thermal_start=str(thermalObj.temperatureStart)
        v_thermal_env=str(thermalObj.temperatureEnv)
        #对于pml_param，每个元素/1000并保留6位小数
        
        v_pml=splitext.join(map(lambda x: str(x / 1000),pml_param))
        

        with open(fname,"w",encoding="utf-8") as f:
            f.write(c_begin+newline)
            f.write(v_type+splitext+c_type+newline)
            f.write(v_time1+splitext+c_time1+newline)
            f.write(v_time_heart+splitext+c_time_heat+newline)
            f.write(v_nf_num+splitext+c_nf_num+newline)
            rowIndex=0
            for p in points:
                rowIndex=rowIndex+1
                f.write(splitext.join(map(str,[p[0],p[1],p[2]]))+splitext+c_nf_row.format(rowIndex)+newline)
            f.write(v_domain+splitext+c_domain+newline)
            f.write(v_domain_step+splitext+c_domain_step+newline)
            f.write(v_ffr_theta+splitext+c_ffr_theta+newline)
            f.write(v_ffr_phi+splitext+c_ffr_phi+newline)
            f.write(v_thermal_start+splitext+c_thermal_start+newline)
            f.write(v_thermal_env+splitext+c_thermal_env+newline)
            f.write(v_pml+splitext+c_pml+newline)
            f.write(v_freq+splitext+c_freq+newline)

            f.write(c_end)




        return (1,"success",None)

        pass
    except Exception as e:
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
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
    
def write_param(fname:str,
                freq:Frequency,
                # power:Power,
                antenna_t:Antenna,
                antenna_r:Antenna,
                points:list=[],
                resPath="./output",
                mpiNum=2):
    # Write paramfile
    try:
        m_unit=1000
        dotPrecision=4 #小数点精度
        #换行符
        newline="\n"
        splitext="\t"
        spacetext=" "
        commatext=","
        c_tip=get_comment("注意："+newline
+"1.所有注释需要输出"+newline
+"2.一行中的间隔使用制表符"+newline
+"3.激励源信息、发射天线、近场观察点、接收天线之间各空一行"+newline)
        c_excitation_begin=get_comment("Begin_Excitation")
        c_excitation_end=get_comment("End_Excitation")
        c1=get_comment("激励源信息（默认发射波形是正弦信号波形）")
        c1_1=get_comment("目前默认发射波形是正弦信号波形")
        c1_2_0=get_comment("计算频点设置方式，1表示等间隔频点方式；0表示非等间隔频点方式")
        c1_2=get_comment("起始频率 终止频率  间隔  单位为Hz")
        c1_3=get_comment("第1个发射天线辐射功率，单位为W。所有发射天线辐射功率均相等")
        v1_0="Signals"
        v1_1="Sinusoidal" #信号值
        v1_2_0="1" #频率设置方式 输出的参数定义，与程序内部并不一致，因此需要处理
        
        v1_2="" #频率
        v1_3=""#功率
        if(freq!=None):
            v1_2_0=str(1-freq.freqType) #频率设置方式 输出的参数定义，与程序内部并不一致，因此需要处理
            if(freq.freqType==0):
                v1_2=splitext.join(map(str,[freq.start,freq.end,freq.increment]))
            else:
                v1_2=splitext.join(map(str,freq.discreteList))
    
        v1_3=str(antenna_t.power)
        c_transimit_begin=get_comment("Begin_Transmitting Antenna")
        c_transimit_end=get_comment("End_Transmitting Antenna")
        c2=get_comment("发射天线信息")
        c2_1=get_comment("定位发射方向图文件路径")
        c2_2=get_comment("发射天线数目")
        c2_3=get_comment("发射天线编号及位置X,Y,Z 单位(m)")
        c2_4=get_comment("发射天线需要调整的姿态参数-- 局部坐标系旋转轴默认U/V/N,例:输入形式为60/0/30,绕U轴转60度,绕N轴转30度")
        
        v2_0="Tx Antenna"
        v2_1=antenna_t.file_antenna
        v2_1="./input/antenna_transmit.txt" #临时采用固定值，后期更新为绝对路径
        v2_1=antenna_t.file_antenna
        v2_2=str(len(antenna_t.itemList_global))
        # v2_3=""
        v2_4="/".join(map(str,(antenna_t.rotate_x,antenna_t.rotate_y,antenna_t.rotate_z)))

        print("write antenna_t_rotate:",v2_4)

        c_receive_begin=get_comment("Begin_Receiving Antenna")
        c_receive_end=get_comment("End_Receiving Antenna")
        c3=get_comment("接收天线信息")
        c3_1=get_comment("定位接收方向图文件路径")
        c3_2=get_comment("接收天线数目")
        c3_3=get_comment("接收天线编号及位置X,Y,Z 单位(m)")
        c3_4=get_comment("接收天线需要调整的姿态参数-- 局部坐标系旋转轴默认U/V/N,例:输入形式为60/0/30,绕U轴转60度,绕N轴转30度")
        v3_0="Rx Antenna"
        v3_1=antenna_r.file_antenna
        v3_1="./input/antenna_receive.txt" #临时采用固定值，后期更新为绝对路径
        v3_1=antenna_r.file_antenna
        v3_2=str(len(antenna_r.itemList_global))
        v3_4="/".join(map(str,(antenna_r.rotate_x,antenna_r.rotate_y,antenna_r.rotate_z)))

        c_nf_begin=get_comment("Begin_Near Field")
        c_nf_end=get_comment("End_Near Field")
        c4=get_comment("近场观察点信息(电磁环境计算)观察点编号及位置X,Y,Z,单位(m)")
        c4_1=get_comment("观察点数目")
        c4_2=get_comment("观察点编号及位置X,Y,Z,单位为m")
        points_nf=points
        # if(nf!=None):
        #     if(nf.pointType==0):#均匀分布
        #         points=get_nf_points(nf)
        #     else:
        #         points=nf.pointList
            
        #     if(nf.axisType==1 and antenna_t!=None and antenna_t._face_id>0):#局部坐标系，需要转换数据
        #         center=antenna_t.itemList_global[0]
        #         normal=antenna_t.normal_dir
        #         angel=antenna_t.offset_rotate_z
        #         points=api_model.local_global_points(center,normal,angel,points)

        # print(len(points))
        v4_1=str(len(points_nf))

        c5=get_comment("计算结果存储文件夹路径,计算模块将计算结果数据存储于该路径的output文件夹中")
        c_results_begin=get_comment("Begin_Results Path")
        c_results_end=get_comment("End_Results Path")

        v_results=resPath

        # c_results_begin="<!—Begin_Results Path-->" #临时修改，后面需要改回去
        # c_results_end="<!—End_Results Path-->"
        c5_1=get_comment("计算模块将计算结果数据存储于该路径的output文件夹中")

        c_solution_begin=get_comment("Begin_Solution Parameters")
        c_solution_end=get_comment("End_Solution Parameters")
        c_solution_1=get_comment("并行求解核数")
        c_solution_2=get_comment("依次为反射次数、绕射次数、透射次数")
        c_solution_3=get_comment("是否存储表面电流数据，1：存储，0：不存储")
        v_solution_1=str(mpiNum) #并行求解核数
     
        v_solution_2="1/1/1"
        v_solution_3=1
        if(freq!=None):
            v_solution_2="{0}/{1}/{2}".format(freq.reflection,freq.transmission,freq.diffraction) #反射次数、绕射次数、透射次数
            v_solution_3=1 if freq.store_current else 0 #存储表面电流

        c_calculate_begin=get_comment("Begin_Calculation Type")
        c_calculate_end=get_comment("End_Calculation Type")
        c_calculate_1=get_comment("3个数字依次表示是否计算接收天线的电磁干扰耦合、电磁环境和辐射方向图，1表示计算，0表示不计算")

        v_sim_emi=0
        v_sim_nf=0
        v_sim_radio=0
        if(antenna_r!=None and antenna_r.itemList_global!=None and len(antenna_r.itemList_global)>0):
            v_sim_emi=1 #设置了接收天线
        if(len(points_nf)>0 ):
            v_sim_nf=1 #设置了近场观察点
        v_calculate_1="{0}/{1}/{2}".format(v_sim_emi,v_sim_nf,v_sim_radio) #计算接收天线的电磁干扰耦合、电磁环境和辐射方向图
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(fname,"w",encoding="utf-8") as f:
            f.write(c_tip+newline)
            # f.write(c1+newline)
            f.write(newline)
            #激励参数
            f.write(c_excitation_begin+newline)
            f.write(v1_0+newline)
            f.write(v1_1+splitext+c1_1+newline)
            f.write(v1_2_0+splitext+c1_2_0+newline)
            f.write(v1_2+splitext+c1_2+newline)
            f.write(v1_3+splitext+c1_3+newline)
            f.write(c_excitation_end+newline)
            f.write(newline)

            #solution参数

            f.write(c_solution_begin+newline)
            f.write(v_solution_1+splitext+c_solution_1+newline)
            f.write(v_solution_2+splitext+c_solution_2+newline)
            f.write(str(v_solution_3)+splitext+c_solution_3+newline)
            f.write(c_solution_end+newline)
            f.write(newline)

            # f.write(c2+newline)
            #方向图参数-发射天线
            f.write(c_transimit_begin+newline)
            f.write(v2_0+newline)
            f.write(v2_1+splitext+c2_1+newline)
            f.write(v2_2+splitext+c2_2+newline) 
            for i in range(len(antenna_t.itemList_global)):
                p=antenna_t.itemList_global[i]
                v_i=splitext.join(map(str,(i+1,
                                           round(p[0]/m_unit,dotPrecision),
                                           round(p[1]/m_unit,dotPrecision),
                                           round(p[2]/m_unit,dotPrecision))
                                           ))
                # v_i=str(i+1)+spacetext+commatext.join(map(str,(p[0]/m_unit,p[1]/m_unit,p[2]/m_unit))) #临时采用，空格加逗号
                if(i==0):
                    f.write(v_i+splitext+c2_3+newline)
                else:
                    f.write(v_i+newline)
            # f.write(v2_3+c2_3+"\n")
            f.write(v2_4+splitext+c2_4+newline)
            f.write(c_transimit_end+newline)
            f.write(newline)

            #添加计算方式参数
            f.write(c_calculate_begin+newline)
            f.write(v_calculate_1+splitext+c_calculate_1+newline)
            f.write(c_calculate_end+newline)
            f.write(newline)

            # f.write(c3+newline)
            #方向图参数-接收天线
            f.write(c_receive_begin+newline)
            f.write(v3_0+newline)
            f.write(v3_1+splitext+c3_1+newline)
            f.write(v3_2+splitext+c3_2+newline)

            for i in range(len(antenna_r.itemList_global)):
                p=antenna_r.itemList_global[i]
                v_i=splitext.join(map(str,(i+1,
                                           round(p[0]/m_unit,dotPrecision),
                                           round(p[1]/m_unit,dotPrecision),
                                           round(p[2]/m_unit,dotPrecision)
                                           )))
                # v_i=str(i+1)+spacetext+commatext.join(map(str,(p[0]/m_unit,p[1]/m_unit,p[2]/m_unit))) #临时采用，空格加逗号
                if(i==0):
                    f.write(v_i+splitext+c3_3+newline)
                else:
                    f.write(v_i+newline)
            # f.write(v2_3+c2_3+"\n")
            f.write(v3_4+splitext+c3_4+newline)
            f.write(c_receive_end+newline)
            f.write(newline)

            # f.write(c4+newline)
            f.write(c_nf_begin+newline)
            f.write(v4_1+splitext+c4_1+newline)
            
            #近场观察点
            for i in range(len(points)):
                v_i=splitext.join(map(str,(i+1,
                                           round(points[i][0],dotPrecision),
                                           round(points[i][1],dotPrecision),
                                           round(points[i][2],dotPrecision)
                                           )))
                # v_i=str(i+1)+spacetext+commatext.join(map(str,(points[i][0],points[i][1],points[i][2]))) #临时采用，空格加逗号
                if(i==0): 
                    f.write(v_i+splitext+c4_2+newline)
                else:
                    f.write(v_i+newline)
            f.write(c_nf_end+newline)
            f.write(newline)
            # f.write(c5+newline)

            f.write(c_results_begin+newline)
            f.write(v_results+splitext+c5_1+newline)
            f.write(c_results_end+newline)
            


        return (1,"success",None)
    except Exception as e:
        # print(e)
        traceback.print_exc()
        return (-1,"failed "+str(e),e)
def write_model_geo(fname:str,nodeDic:dict,triangleDic:dict):
    m_unit=1000
    newline="\n"
    splitText="\t"
    con_str="_"
    c_tip=get_comment("注意："+newline+
"1.需要输出所有注释"+newline+ 
"2.一行中的间隔使用制表符"+newline+
"3.顶点信息和面信息之间空一行"+newline+
"4.数据需要转换成米输出"+newline)
    c_begin_vertices=get_comment("Begin_Mesh Vertices")
    c_end_vertices=get_comment("End_Mesh Vertices")
    c_begin_triangle=get_comment("Begin_Triangle Mesh")
    c_end_triangle=get_comment("End_Triangle Mesh")
   
    c1_1=get_comment("网格顶点总数")
    c1_2=get_comment("网格顶点编号 X/m  Y/m  Z/m")
    c2_1=get_comment("网格三角面总数")
    c2_2=get_comment("三角面序号 顶点1编号 顶点2编号 顶点3编号 本体材料索引号(1、2、3等) 涂敷材料索引号(1、2、3等,无涂敷对应0) 涂敷材料厚度(m)")
    v1_1=str(len(nodeDic))
    v2_1=str(len(triangleDic))
    fpath=os.path.dirname(fname)
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    with open(fname,"w",encoding="utf-8") as f:
        f.write(c_tip+newline)
        f.write(newline)
        f.write(c_begin_vertices+newline)
       
        f.write(v1_1+splitText+c1_1+newline)

        lineIndex=0
        for k in nodeDic:
            v=nodeDic[k]
            v_str=splitText.join(map(str,[v[0],v[1],v[2],v[3]]))
            if(lineIndex==0):
                f.write(v_str+splitText+c1_2+newline)
            else:
                f.write(v_str+newline)
            lineIndex=lineIndex+1
        f.write(c_end_vertices+newline)
        f.write(newline)

        f.write(c_begin_triangle+newline)
        f.write(v2_1+splitText+c2_1+newline)

        lineIndex=0
        for t in triangleDic:
            v_str=str(t)+splitText+splitText.join(map(str,triangleDic[t]))
            if(lineIndex==0):
                f.write(v_str+splitText+c2_2+newline)
            else:
                f.write(v_str+newline)
            lineIndex=lineIndex+1
        f.write(c_end_triangle+newline)
        pass

    # Write geo model
    return (1,"success",None)
def get_comment(str):
    return f"<!--{str}-->"
def get_nf_points(nf:NF):
    '''
    获取近场观察点坐标
    '''
    f_tolerance=1e-6
    points=[]
    p_dic={f"{nf.uStart}_{nf.vStart}_{nf.nStart}":(nf.uStart,nf.vStart,nf.nStart)}
  
    u_num=1
    if(abs(nf.uEnd-nf.uStart)>f_tolerance):
        u_num=2
        if(abs(nf.uIncrement)>f_tolerance):#终点与起点不同
            u_num=int((nf.uEnd-nf.uStart)/nf.uIncrement)+1
    v_num=1
    if(abs(nf.vEnd-nf.vStart)>f_tolerance):
        v_num=2
        if(abs(nf.vIncrement)>f_tolerance):#终点与起点不同
            v_num=int((nf.vEnd-nf.vStart)/nf.vIncrement)+1

    n_num=1
    if(abs(nf.nEnd-nf.nStart)>f_tolerance):
        n_num=2
        if(abs(nf.nIncrement)>f_tolerance):#终点与起点不同
            n_num=int((nf.nEnd-nf.nStart)/nf.nIncrement)+1

    for u in range(u_num+1):
        p_u=nf.uStart+u*nf.uIncrement
        if(p_u>nf.uEnd):
            p_u=nf.uEnd
        if(abs(nf.uIncrement)<f_tolerance and u>0):
            p_u=nf.uEnd
        for v in range(v_num+1):
            p_v=nf.vStart+v*nf.vIncrement
            if(p_v>nf.vEnd):
                p_v=nf.vEnd
            if(abs(nf.vIncrement)<f_tolerance and v>0):
                p_v=nf.vEnd
            for n in range(n_num+1):
                p_n=nf.nStart+n*nf.nIncrement
                if(p_n>nf.nEnd):
                    p_n=nf.nEnd
                if(abs(nf.nIncrement)<f_tolerance and n>0):
                    p_n=nf.nEnd
                k=f"{round(p_u,6)}_{round(p_v,6)}_{round(p_n,6)}"
                if(k in p_dic):
                    continue
                p_dic[k]=(round(p_u,6),round(p_v,6),round(p_n,6))

    if(abs(nf.uEnd-nf.uStart)>f_tolerance
        or abs(nf.vEnd-nf.vStart)>f_tolerance 
        or abs(nf.nEnd!=nf.nStart)>f_tolerance):#如果end不是一个点
        # points.append((nf.uEnd,nf.vEnd,nf.nEnd))
        k=f"{nf.uEnd}_{nf.vEnd}_{nf.nEnd}"
        p_dic[k]=(nf.uEnd,nf.vEnd,nf.nEnd)
    for k in p_dic:
        points.append(p_dic[k])
    return points
# print(get_comment("test"))
# write_mediaLibrary("d:/test.txt",[])
def degree_radius(fname:str):
    '''
    角度处理为弧度
    '''
    try:
        destFile="D:/radio.txt"
        splitText="\t"
        with open(fname,"r",encoding="utf-8") as f:
            lines=f.readlines()
        with open(destFile,"w",encoding="utf-8") as f:
            lineIndex=0
            for line in lines:
                if(lineIndex==0 or lineIndex==1):
                    f.write(line)
                else:
                    arr = line.strip().split()
                    if(len(arr) == 9):
                        theta = float(arr[0])
                        phi = float(arr[1])
                        # arr[0] = str(math.radians(theta))
                        # arr[1] = str(math.radians(phi))
                        f.write(splitText.join(arr)+"\n")
                lineIndex=lineIndex+1
                
        return (1,"success",None)
    except Exception as e:
        print(e)
        return (-1,"failed "+str(e),e)
    pass
def write_project_path(fname,fpath):
    try:
        print("dir.txt",fname,fpath)
        with open(fname,"w",encoding="utf-8") as f:
            f.write(fpath)
        return (1,"success",None)
    except Exception as e:
        return (-1,"failed "+str(e),e)