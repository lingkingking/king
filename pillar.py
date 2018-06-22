﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-



import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtility          # allplan util library


import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder


from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
from StdReinfShapeBuilder.RotationAngles import RotationAngles

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart   
import math        

from JunheModels.util.LongitudinalBarShape import LongitudinalSteel
from JunheModels.util.Stirrup import Stirrup
from JunheModels.util.calculate import steel_modify

print ('Loading pillar.py ' )


#程序接口
def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version                 

    Args:
        build_ele:  the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version

    # Support all versions
    return True
#程序接口
def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles           

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)
#程序接口
def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.            
        doc:       input document
    Return:
        tuple of element_list and handle_list
    """

    element = Pillar(doc)
 
    return element.create(build_ele)




class Pillar(object):
    '''
    Definition of class Beam
    构件类
    '''
    def __init__(self, doc):
        '''
        Initialisation of class Beam
        初始化函数
        Args:
            doc: Input document
            文档输入
        '''
        self.model_ele_list = None
        self.handle_list = []
        self.document = doc


        #获取画笔信息
        self.texturedef = None

        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()

    def data_read(self,build_dict):

        for key,value in build_dict.items():
            self.__dict__[key] = value

    def data_update(self,build_dict):
        for key,value in self.__dict__.items():
            build_dict.get_parameter_dict()[key] = value

    def create(self, build_ele):
        '''
        Create the elements
        构造物件函数
        Args:
            build_ele: the building element
            .pyp文件输入参数，build_ele代表整个.pyp文件信息

        Returns:
            tuple with created elements and handles.
            被创造元素以及其句柄，由元祖打包返回
        '''
        views_list = []
        #读取数据
        self.data_read(build_ele.get_parameter_dict())
        #建立游标
        self.create_handle()
        
        

        polyhedron = self.create_geometry(build_ele.get_parameter_dict())

        reinforcement = self.create_reinforcement(build_ele.get_parameter_dict())
        
        




        views_list += polyhedron
        views = [View2D3D(views_list)]
        
        pythonpart = PythonPart ("Pillar",                                             #ID
                                 parameter_list = build_ele.get_params_list(),          #.pyp 参数列表
                                 hash_value     = build_ele.get_hash(),                 #.pyp 哈希值
                                 python_file    = build_ele.pyp_file_name,              #.pyp 文件名
                                 views          = views,                                #图形视图
                                 reinforcement  = reinforcement,                        #增强构建
                                 common_props   = self.com_prop)                        #格式参数





        self.model_ele_list = pythonpart.create()

        return (self.model_ele_list, self.handle_list)

    def create_geometry(self, build_ele):
        '''
        Create the element geometries
        构建元素几何图形函数

        Args:
            build_ele: the building element
            .pyp文件输入参数，build_ele代表整个.pyp文件信息
        '''

        #point
        texturedef = AllplanBasisElements.TextureDefinition(self.Surface)
        from_point = AllplanGeo.Point3D(0,0,0)                  
        to_point = AllplanGeo.Point3D(self.Length,self.Width,self.Height)      

        rectangle = AllplanGeo.Polyhedron3D.CreateCuboid(from_point,to_point) #矩形

        
        return [AllplanBasisElements.ModelElement3D(self.com_prop,texturedef, rectangle)]


    def create_reinforcement(self,build_ele):
        '''
        Create the reinforcement element
        构造并添加增强构建函数

        Args:
            build_ele: the building element
            .pyp文件输入参数，buile_ele代表整个.pyp文件信息
        '''
        reinforcement = []
        stirrup = self.create_stirrup()
        longitudinal = self.create_longitudinal_steel()
        tie = self.create_tie_steel()

        for ele_1 in stirrup:
            ele_1.SetAttributes(AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet([AllplanBaseElements.AttributeInteger(1013,self.MarkIndex_Stir)])]))

        for ele_2 in longitudinal:
            ele_2.SetAttributes(AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet([AllplanBaseElements.AttributeInteger(1013,self.MarkIndex_Vert)])]))

        for ele_3 in tie:
            ele_3.SetAttributes(AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet([AllplanBaseElements.AttributeInteger(1013,self.MarkIndex_Tie)])]))

        if self.StirrupVisual:
            reinforcement += stirrup
        if self.VertSteelVisual:
            reinforcement += longitudinal
        if self.TieSteelVisual:
            reinforcement += tie

        return reinforcement

    def create_handle(self):
        '''
        Create handle
        创建可拉动游标句柄

        '''
        self.handle_list.append(
            HandleProperties("Height",
                                AllplanGeo.Point3D(0, 0, self.Height),
                                AllplanGeo.Point3D(0, 0, 0),
                                [("Height", HandleDirection.z_dir)],
                                HandleDirection.z_dir,
                                True))

        self.handle_list.append(
            HandleProperties("Width",
                                AllplanGeo.Point3D(0, self.Width, 0),
                                AllplanGeo.Point3D(0, 0, 0),
                                [("Width", HandleDirection.y_dir)],
                                HandleDirection.y_dir,
                                True))

        self.handle_list.append(
            HandleProperties("Length",
                                AllplanGeo.Point3D(self.Length, 0, 0),
                                AllplanGeo.Point3D(0, 0, 0),
                                [("Length", HandleDirection.x_dir)],
                                HandleDirection.x_dir,
                                True))

    def create_stirrup(self):

        stirrup_list = []

        rebar_prop = {  'diameter':self.StirDiameter,
                        'bending_roller':self.BendingRoller,
                        'steel_grade':self.StirSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.Stirrup}      

        #保护层混凝土属性
        sleeve_cover = ConcreteCoverProperties(self.StirSideCover-self.SleeveThick+self.StirDiameter/2,self.StirSideCover-self.SleeveThick+self.StirDiameter/2,
                                            self.StirFrontCover-self.SleeveThick+self.StirDiameter/2,self.StirFrontCover-self.SleeveThick+self.StirDiameter/2)
        cover = ConcreteCoverProperties(self.StirSideCover+self.StirDiameter/2,self.StirSideCover+self.StirDiameter/2,
                                        self.StirFrontCover+self.StirDiameter/2,self.StirFrontCover+self.StirDiameter/2)

        sleeve_stirrup = Stirrup(sleeve_cover,rebar_prop)
        stirrup = Stirrup(cover,rebar_prop)

        if self.StirExtend:
            if self.StirExtendSide == 1:
                sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,1)
                stir_shape = stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,1)
            elif self.StirExtendSide == 2:
                sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,2)
                stir_shape = stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,2)
            elif self.StirExtendSide == 3:
                sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,3)
                stir_shape = stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,3)
            elif self.StirExtendSide == 4:
                sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,4)
                stir_shape = stirrup.shape_stirrup(self.Length,self.Width,self.StirExtendLength,4)
        else:
            sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length,self.Width)
            stir_shape = stirrup.shape_stirrup(self.Length,self.Width)


        point_f_1 = AllplanGeo.Point3D(0,0,0)
        point_t_1 = AllplanGeo.Point3D(0,0,self.SleeveAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          sleeve_stir_shape,
                                                                          point_f_1,
                                                                          point_t_1,
                                                                          self.StirUpsCover,
                                                                          0,
                                                                          self.StirDenseDistance,
                                                                          3) )       

        point_f_2 = AllplanGeo.Point3D(0,0,self.SleeveAreaLength)
        point_t_2 = AllplanGeo.Point3D(0,0,self.DensAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f_2,
                                                                          point_t_2,
                                                                          self.StirDenseDistance/2,
                                                                          0,
                                                                          self.StirDenseDistance,
                                                                          3) )   

        point_f = AllplanGeo.Point3D(0,0,self.DensAreaLength)
        point_t = AllplanGeo.Point3D(0,0,self.Height-self.TopDensAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f,
                                                                          point_t,
                                                                          0,
                                                                          0,
                                                                          self.StirSparseDistance,
                                                                          3) ) 

        point_f_3 = AllplanGeo.Point3D(0,0,self.Height-self.TopDensAreaLength)
        point_t_3 = AllplanGeo.Point3D(0,0,self.Height)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f_3,
                                                                          point_t_3,
                                                                          0,
                                                                          self.StirUpsCover,
                                                                          self.StirDenseDistance,
                                                                          2) ) 

        return stirrup_list


    def create_longitudinal_steel(self):
        steel_list = []

        rebar_prop = {  'diameter':self.VertSteelDia,
                        'bending_roller':math.pi * 3*self.VertSteelDia / 40,
                        'steel_grade':self.VertSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}      
                        
        hori_rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':math.pi * 3*self.HoriSteelDia / 40,
                        'steel_grade':self.VertSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar} 

        foot_rebar_prop = {  'diameter':self.FootSteelDia,
                        'bending_roller':math.pi * 3*self.FootSteelDia / 40,
                        'steel_grade':self.VertSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar} 

        cover = ConcreteCoverProperties(0,
                                        0,
                                        0,
                                        0)

        longitudinal = LongitudinalSteel(cover,rebar_prop)
        hori_longitudinal = LongitudinalSteel(cover,hori_rebar_prop)
        foot_longitudinal = LongitudinalSteel(cover,foot_rebar_prop)

        steel_shape = longitudinal.shape_extend_steel(length=self.Height,extend=self.VertExtendLength,extend_side=2,vertical=True)
        hori_steel_shape = hori_longitudinal.shape_extend_steel(length=self.Height,extend=self.VertExtendLength,extend_side=2,vertical=True)
        foot_steel_shape = foot_longitudinal.shape_extend_steel(length=self.Height,extend=self.VertExtendLength,extend_side=2,vertical=True)
        #foot steel
        point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.FootSteelDia/2,
                                    0)
        point_t_1 = AllplanGeo.Point3D(self.Length-math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.FootSteelDia/2,
                                    0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,foot_steel_shape,
                                                                                        point_f_1,point_t_1,
                                                                                        0,
                                                                                        0,
                                                                                        2))
        #foot steel
        point_f_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.FootSteelDia/2,0)
        point_t_2 = AllplanGeo.Point3D(self.Length-math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.FootSteelDia/2,0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,foot_steel_shape,
                                                                                        point_f_2,point_t_2,
                                                                                        0,
                                                                                        0,
                                                                                        2))


        point_f_v1 = AllplanGeo.Point3D(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2,
                                        math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance,
                                        0)
        point_t_v1 = AllplanGeo.Point3D(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2,
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.VertDistance,
                                        0)

        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,steel_shape,
                                                                                        point_f_v1,point_t_v1,
                                                                                        0,
                                                                                        0,
                                                                                        self.VertNum))    

        point_f_v2 = AllplanGeo.Point3D(self.Length-(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2),
                                        math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance,
                                        0)
        point_t_v2 = AllplanGeo.Point3D(self.Length-(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.VertDistance,
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,steel_shape,
                                                                                        point_f_v2,point_t_v2,
                                                                                        0,
                                                                                        0,
                                                                                        self.VertNum))        

        point_f_h1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        point_t_h1 = AllplanGeo.Point3D(self.Length-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h1,point_t_h1,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))    

        point_f_h2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        point_t_h2 = AllplanGeo.Point3D(self.Length-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h2,point_t_h2,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))                                                                                                                                                                                                                                                                         

        return steel_list

    def create_tie_steel(self):
        steel_list = []

        rebar_prop = {  'diameter':self.TieSteelDia,
                        'bending_roller':self.BendingRoller,
                        'steel_grade':self.TieSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}      


        cover = ConcreteCoverProperties(self.StirFrontCover-self.SleeveThick+self.StirDiameter/2,self.StirFrontCover-self.SleeveThick+self.StirDiameter/2,0,0)        
        cover_1 = ConcreteCoverProperties(self.StirFrontCover,self.StirFrontCover,0,0)
        sleeve_tie = Stirrup(cover,rebar_prop)
        tie = Stirrup(cover_1,rebar_prop)

        sleeve_tie_shape = sleeve_tie.shape_tie_steel(length=self.Width,width=4*self.TieSteelDia+self.SleeveThick,
                                        rotate=RotationAngles(0,0,90),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        tie_shape = tie.shape_tie_steel(length=self.Width,width=4*self.TieSteelDia,
                                        rotate=RotationAngles(0,0,90),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        vt_cover = ConcreteCoverProperties(self.StirSideCover-self.SleeveThick+self.StirDiameter/2,self.StirSideCover-self.SleeveThick+self.StirDiameter/2,0,0)        
        vt_cover_1 = ConcreteCoverProperties(self.StirSideCover,self.StirSideCover,0,0)
        vt_sleeve_tie = Stirrup(vt_cover,rebar_prop)
        vt_tie = Stirrup(vt_cover_1,rebar_prop)

        vt_sleeve_tie_shape = vt_sleeve_tie.shape_tie_steel(length=self.Length,width=4*self.TieSteelDia+self.SleeveThick,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        vt_tie_shape = vt_tie.shape_tie_steel(length=self.Length,width=4*self.TieSteelDia,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        # count = int((self.Length - 2*(self.StirSideCover+self.StirDiameter+self.VertSteelDia) - self.TieSteelDia) / self.VertDistance) + 1
        # bar_distance = (self.Length - 2*(self.StirSideCover+self.StirDiameter+self.VertSteelDia) - self.TieSteelDia) / count

        #vl -vertical steel total space
        #hl -horizental steel total space
        vl = self.Width-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.VertDistance
        hl = self.Length-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.HoriDistance
        # dv -vertical steel space
        #hl -horizental steel space
        dv = vl / (self.VertNum - 1)
        dh = hl / (self.HoriNum - 1)

        h_cover = ConcreteCoverProperties(-self.SleeveThick/2,-self.SleeveThick/2,self.StirFrontCover-self.SleeveThick+self.StirDiameter/2,self.StirFrontCover-self.SleeveThick+self.StirDiameter/2)        
        h_cover_1 = ConcreteCoverProperties(0,0,self.StirFrontCover+self.StirDiameter/2,self.StirFrontCover+self.StirDiameter/2)
        sleeve_tie = Stirrup(h_cover,rebar_prop)
        tie = Stirrup(h_cover_1,rebar_prop)

        dh_sleeve_stirrup_shape = sleeve_tie.shape_stirrup(dh+self.HoriSteelDia/2+2*self.StirDiameter+2*self.SleeveThick,self.Width,0,1)
        dh_stirrup_shape = tie.shape_stirrup(dh+self.HoriSteelDia/2+2*self.StirDiameter,self.Width,0,1)

        v_cover = ConcreteCoverProperties(self.StirSideCover-self.SleeveThick+self.StirDiameter/2,self.StirSideCover-self.SleeveThick+self.StirDiameter/2,
                                            -self.SleeveThick/2,-self.SleeveThick/2)        
        v_cover_1 = ConcreteCoverProperties(self.StirSideCover+self.StirDiameter/2,self.StirSideCover+self.StirDiameter/2,0,0)
        v_sleeve_tie = Stirrup(v_cover,rebar_prop)
        v_tie = Stirrup(v_cover_1,rebar_prop)

        dv_sleeve_stirrup_shape = v_sleeve_tie.shape_stirrup(self.Length,dv+self.VertSteelDia/2+2*self.StirDiameter+2*self.SleeveThick,0,1)
        dv_stirrup_shape = v_tie.shape_stirrup(self.Length,dv+self.VertSteelDia/2+2*self.StirDiameter,0,1)        

        #dh
        distance = 0
        for x in range(self.HoriNum):
            point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.StirDiameter)
            point_t_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)

            point_f_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)
            point_t_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)

            point_f = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)
            point_t = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height+self.StirDiameter-self.TopDensAreaLength)

            point_f_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height+self.StirDiameter-self.TopDensAreaLength)
            point_t_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height+self.StirDiameter)
            

            if x != self.HoriNum - 1:
                if x % 2 == 0:
                   
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    dh_sleeve_stirrup_shape,
                                                                                                    point_f_1,
                                                                                                    point_t_1,
                                                                                                    self.StirUpsCover,
                                                                                                    0,
                                                                                                    self.StirDenseDistance,
                                                                                                    3))
                   
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dh_stirrup_shape,
                                                                                      point_f_2,
                                                                                      point_t_2,
                                                                                      self.StirDenseDistance/2,
                                                                                      0,
                                                                                      self.StirDenseDistance,
                                                                                      3) )   

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dh_stirrup_shape,
                                                                                      point_f,
                                                                                      point_t,
                                                                                      0,
                                                                                      0,
                                                                                      self.StirSparseDistance,
                                                                                      3) ) 

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dh_stirrup_shape,
                                                                                      point_f_3,
                                                                                      point_t_3,
                                                                                      0,
                                                                                      self.StirUpsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) ) 
            else:
                if x % 2 == 0:
                    t_point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                            0,
                                            self.StirDiameter)
                    t_point_t_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)

                    t_point_f_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)
                    t_point_t_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)

                    t_point_f = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)
                    t_point_t = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height+self.StirDiameter-self.TopDensAreaLength)

                    t_point_f_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height+self.StirDiameter-self.TopDensAreaLength)
                    t_point_t_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height+self.StirDiameter)                    
                    
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    sleeve_tie_shape,
                                                                                                    t_point_f_1,
                                                                                                    t_point_t_1,
                                                                                                    self.StirUpsCover,
                                                                                                    0,
                                                                                                    self.StirDenseDistance,
                                                                                                    3))
                    
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      tie_shape,
                                                                                      t_point_f_2,
                                                                                      t_point_t_2,
                                                                                      self.StirDenseDistance/2,
                                                                                      0,
                                                                                      self.StirDenseDistance,
                                                                                      3) )   

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      tie_shape,
                                                                                      t_point_f,
                                                                                      t_point_t,
                                                                                      0,
                                                                                      0,
                                                                                      self.StirSparseDistance,
                                                                                      3) )

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      tie_shape,
                                                                                      t_point_f_3,
                                                                                      t_point_t_3,
                                                                                      0,
                                                                                      self.StirUpsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) )

            distance += int(dh)


        # #dv
        distance = 0
        for x in range(self.VertNum):
            point_f_1 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2-self.SleeveThick,
                                            self.StirDiameter+self.TieSteelDia)
            point_t_1 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2-self.SleeveThick,
                                            self.SleeveAreaLength+self.StirDiameter+self.TieSteelDia)

            point_f_2 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.SleeveAreaLength+self.StirDiameter+self.TieSteelDia)
            point_t_2 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.DensAreaLength+self.StirDiameter+self.TieSteelDia)

            point_f = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.DensAreaLength+self.StirDiameter+self.TieSteelDia)
            point_t = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.Height+self.StirDiameter+self.TieSteelDia-self.TopDensAreaLength)

            point_f_3 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.Height+self.StirDiameter+self.TieSteelDia-self.TopDensAreaLength)
            point_t_3 = AllplanGeo.Point3D(0,
                                            math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance-self.StirDiameter/2-self.VertSteelDia/2,
                                            self.Height+self.StirDiameter+self.TieSteelDia)            

            if x != self.VertNum - 1:
                if x % 2 == 0:
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    dv_sleeve_stirrup_shape,
                                                                                                    point_f_1,
                                                                                                    point_t_1,
                                                                                                    self.StirUpsCover,
                                                                                                    0,
                                                                                                    self.StirDenseDistance,
                                                                                                    3))

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dv_stirrup_shape,
                                                                                      point_f_2,
                                                                                      point_t_2,
                                                                                      self.StirDenseDistance/2,
                                                                                      0,
                                                                                      self.StirDenseDistance,
                                                                                      3) )   

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dv_stirrup_shape,
                                                                                      point_f,
                                                                                      point_t,
                                                                                      0,
                                                                                      0,
                                                                                      self.StirSparseDistance,
                                                                                      3) ) 

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      dv_stirrup_shape,
                                                                                      point_f_3,
                                                                                      point_t_3,
                                                                                      0,
                                                                                      self.StirUpsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) ) 
            else:
                if x % 2 == 0:
                    vt_point_f_1 = AllplanGeo.Point3D(0,
                                                math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2+self.SleeveThick,
                                                self.StirDiameter+self.TieSteelDia)
                    vt_point_t_1 = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2+self.SleeveThick,
                                                    self.SleeveAreaLength+self.StirDiameter+self.TieSteelDia)

                    vt_point_f_2 = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.SleeveAreaLength+self.StirDiameter+self.TieSteelDia)
                    vt_point_t_2 = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.DensAreaLength+self.StirDiameter+self.TieSteelDia)

                    vt_point_f = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.DensAreaLength+self.StirDiameter+self.TieSteelDia)
                    vt_point_t = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.Height+self.StirDiameter+self.TieSteelDia-self.TopDensAreaLength)

                    vt_point_f_3 = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.Height+self.StirDiameter+self.TieSteelDia-self.TopDensAreaLength)
                    vt_point_t_3 = AllplanGeo.Point3D(0,
                                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance+distance+self.StirDiameter/2+self.VertSteelDia/2,
                                                    self.Height+self.StirDiameter+self.TieSteelDia)

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    vt_sleeve_tie_shape,
                                                                                                    vt_point_f_1,
                                                                                                    vt_point_t_1,
                                                                                                    self.StirUpsCover,
                                                                                                    0,
                                                                                                    self.StirDenseDistance,
                                                                                                    3))

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      vt_tie_shape,
                                                                                      vt_point_f_2,
                                                                                      vt_point_t_2,
                                                                                      self.StirDenseDistance/2,
                                                                                      0,
                                                                                      self.StirDenseDistance,
                                                                                      3) )   

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      vt_tie_shape,
                                                                                      vt_point_f,
                                                                                      vt_point_t,
                                                                                      0,
                                                                                      0,
                                                                                      self.StirSparseDistance,
                                                                                      3) ) 

                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      vt_tie_shape,
                                                                                      vt_point_f_3,
                                                                                      vt_point_t_3,
                                                                                      0,
                                                                                      self.StirUpsCover,
                                                                                      self.StirSparseDistance,
                                                                                      2) ) 
            distance += int(dv)


        return steel_list