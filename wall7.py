#!/bin/usr/env  python
#_*_ coding :uft-8 _*_
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtility          
import NemAll_Python_Palette as AllplanPalette


import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder


from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
from StdReinfShapeBuilder.RotationAngles import RotationAngles
import GeometryValidate as GeometryValidate

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart   
import logging
import math  
from JunheModels.util.LongitudinalBarShape import LongitudinalSteel
from JunheModels.util.Stirrup import Stirrup
from JunheModels.util.calculate import steel_modify

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
    element = wall(doc)
    return element.create(build_ele)

class wall(object):
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
    def create(self, build_ele):
        '''
        Create the elements
        构造物件函数
        Args:
            build_ele: the building element
            .pyp文件输入参数，build_ele代表整个.pyp文件的信息句柄

        Returns:
            tuple with created elements and handles.
            被创造元素以及其句柄，由元祖打包返回
        '''
        self.data_read(build_ele.get_parameter_dict())

        polyhedron = self.create_geometry()
        reinforcement = self.create_reinforcement()

        views = [View2D3D(polyhedron)]
        
        pythonpart = PythonPart ("wall",                                             #ID
                                 parameter_list = build_ele.get_params_list(),          #.pyp 参数列表
                                 hash_value     = build_ele.get_hash(),                 #.pyp 哈希值
                                 python_file    = build_ele.pyp_file_name,              #.pyp 文件名
                                 views          = views,                                #图形视图
                                 reinforcement  = reinforcement,                        #增强构建
                                 common_props   = self.com_prop)                        #格式参数



        # self.create_handle()

        self.model_ele_list = pythonpart.create()
        self.data_read(build_ele.get_parameter_dict())
        return (self.model_ele_list, self.handle_list)

    def create_geometry(self):
        '''
        Create the element geometries
        构建元素几何图形函数
        return 图形list
        '''
        steel_list = []
        rectangle = self.shape_cuboid(self.Length,self.Width,self.Height)
        #窗
        
        window = self.shape_cuboid(self.WLength,self.Width,self.WHeight,sX=self.WmobilePosition,sZ=self.oWmobilePosition)
        err,rectangle = AllplanGeo.MakeSubtraction(rectangle,window)

        approximation = AllplanGeo.ApproximationSettings(AllplanGeo.eApproximationSettingsType.ASET_BREP_TESSELATION, 1)
        err,rectangle = AllplanGeo.CreatePolyhedron(rectangle,approximation)
     
        steel_list  += [AllplanBasisElements.ModelElement3D(self.com_prop, rectangle)]
        
        
        return steel_list




    def create_reinforcement(self):
        '''
        Create the reinforcement element
        构造并添加增强构建函数

        Args:
            build_ele: build_ele.get_parameter_dict()
            build_ele: .pyp文件内的 Name标签的参数字典
        '''
        reinforcement = []
        
        #垂直的钢筋
        if  self.VertSteelVisual_q:
             reinforcement +=  self.create_longitudinal_steelr()
        #水平钢筋
        if self.HoriSteelVisual:
             reinforcement +=  self.create_horizontal_steelr()
        #拉筋
        if self.TieSteelVisual:
             reinforcement +=  self.create_tie_steel_q()
        #加强筋
        if self.addSteelVisual:
            reinforcement += self.create_add_vertical_steelt()
        
        #梁
        if self.StirVisual:
            reinforcement += self.create_stirrup()
        
        if self.LongbarVisual:
            reinforcement += self.create_long_steel()
        if self.WaistVisual:
            reinforcement += self.create_waist_steel()
        if self.TieBarVisual:
            reinforcement += self.create_tie_steel_l()

        
        #柱子
        stirrup = self.create_stirrup_z()
        longitudinal = self.create_longitudinal_steel_z()
        tie = self.create_tie_steel_z()

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
        if self.TieSteelVisual_z:
            reinforcement += tie
        
        return reinforcement

    def shape_cuboid(self,length,width,height,sX=0,sY=0,sZ=0,rX=0,rY=0,rZ=0):

        axis = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(rX+sX,rY+sY,rZ+sZ),
                                            AllplanGeo.Vector3D(1,0,0),
                                            AllplanGeo.Vector3D(0,0,1))

        args = {'placement':axis,
                'length':length,
                'width':width,
                'height':height}

        shape = AllplanGeo.BRep3D.CreateCuboid(**args)
        return shape

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
    #————————————————————————————
    def create_longitudinal_steelr(self):
        steel_list = []
        #有上梁，有窗户，左右柱时
  
            #窗下钢筋
        point_f_1 = AllplanGeo.Point3D(self.WmobilePosition,self.FrontCover + 3/2*self.HoriSteelDia,0)
        point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.FrontCover + 3/2*self.HoriSteelDia,0)
        point_f_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width - self.FrontCover - 3/2*self.HoriSteelDia,0)
        point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.FrontCover - 3/2*self.HoriSteelDia,0)
        steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2)

        return steel_list
    def create_vertical_steelt(self,SteelLength,point_f_1,point_t_1,point_f_2,point_t_2):
        steel_list = []

        cover = [self.Length_BA,self.Length_BA,self.Length_BA,self.Length_BA]
       
        rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':0,
                        'steel_grade':self.HoriSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}    
                     #纵向钢筋
        longit = LongitudinalSteel(cover,rebar_prop)
        steel_vert_1 = steel_vert_2 = longit.shape_extend_steel(length=SteelLength,extend=0,extend_side=2,vertical=True)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                        steel_vert_1,
                                                                                        point_f_1,
                                                                                        point_t_1,
                                                                                        self.VertSideCover,
                                                                                        self.VertSideCover,
                                                                                        self.VertDistance,
                                                                                        3))

        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                        steel_vert_2,
                                                                                        point_f_2,
                                                                                        point_t_2,
                                                                                        self.VertSideCover,
                                                                                        self.VertSideCover,
                                                                                        self.VertDistance,
                                                                                        3))
        
        if steel_modify(self.WmobilePosition+self.WLength,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover):
                 point_f_3 = AllplanGeo.Point3D(0,0,0)
                 point_t_3 = AllplanGeo.Point3D(self.Length ,0,0)
                 vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))
                 s_shape_1 = AllplanReinf.BendingShape(steel_vert_1)
                 s_shape_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength - self.VertSideCover,self.FrontCover + 3/2*self.HoriSteelDia,0)))
                 s_shape_2 = AllplanReinf.BendingShape(steel_vert_2)
                 s_shape_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength - self.VertSideCover,self.Width-self.FrontCover - 3/2*self.HoriSteelDia,0)))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_3,point_t_3,s_shape_1))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_3,point_t_3,s_shape_2))

        return steel_list
    def create_horizontal_steelr(self): 
        steel_list = []

                   #有上梁，窗户,左右窗柱时
        #if   not self.unbeamVisual:
                              
                   #布窗户以下的钢筋
        lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
        for i in range(lines_1):
                point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.FrontCover+self.HoriSteelDia/2,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.FrontCover-self.HoriSteelDia/2,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                steel_list += self.create_horizontal_steelt(self.WLength-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
        steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition,self.oWmobilePosition,self.oWmobilePosition-self.HoriTopCover-self.HoriSteelDia/2 )
          #有樑，窗，下窗樑,左柱,右柱时：
        """
        elif    self.unbeamVisual:
                              
                #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.FrontCover+self.HoriSteelDia/2,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.FrontCover-self.HoriSteelDia/2,self.HoriBottomCover+self.HoriSteelDia/2+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition,self.oWmobilePosition-self.unBHeight,self.oWmobilePosition-self.unBHeight-self.HoriTopCover-self.HoriSteelDia/2 )
        """
        return steel_list
    ##hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚                                                        extend_side：0左右，1左 2右
    def create_horizontal_steelt(self,SteelLength,hook_side,point_1,point_2,lines,DegreesHook,HoriExtend,extendside): #钢筋长度，锚的延伸方向，第一钢筋的具体位置，第二钢筋的具体方向,第几根钢筋,弯曲的长度,钢筋延长的长度,钢筋延长的方向
        #def create_horizontal_steelt(self):  
        steel_list = []
                    #保护层混凝土属性
        #cover = ConcreteCoverProperties.left_right(self.HoriSideCover,self.HoriSideCover)
        cover = ConcreteCoverProperties(0,0,0,self.HoriBottomCover) #self.VertBottomCover)#第四个参数是设置钢筋元素离底部的距离多少开始
        rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':0,
                        'steel_grade':self.HoriSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}    

        longit = LongitudinalSteel(cover,rebar_prop)

        steel_hs1 = longit.shape_steel(SteelLength)

        if HoriExtend > 0:
            HoriExtend += self.HoriFrontCover
        if not self.Degrees_HS2:
            steel_hs2_1 = steel_hs2_2 = longit.shape_extend_steel(length=SteelLength,extend=HoriExtend,extend_side=extendside)
        else:
            if HoriExtend > 0:
                steel_hs2_1 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2+self.HoriFrontCover,right=self.RightAnchor_HS2+self.HoriFrontCover,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
                steel_hs2_2 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2+self.HoriFrontCover,right=self.RightAnchor_HS2+self.HoriFrontCover,mirror=True)
            else:
                steel_hs2_1 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2,right=self.RightAnchor_HS2,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
                steel_hs2_2 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2,right=self.RightAnchor_HS2,mirror=True)
        point_f_1 = AllplanGeo.Point3D(0,0,0)
        point_t_1 = AllplanGeo.Point3D(0,0,self.Height)

       
        point_f = AllplanGeo.Point3D(0,0,0)
        point_t = AllplanGeo.Point3D(self.Length,self.Width,self.Height)
        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance,0,0))
        distance = self.HoriBottomCover
     
        #else:
        s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
             #s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.HoriFrontCover,distance)))
        s_shape_hs2_1.Move(AllplanGeo.Vector3D(point_1))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))

        s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
            #s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,distance)))
        s_shape_hs2_2.Move(AllplanGeo.Vector3D(point_2))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2))
        
        return steel_list 
    ##hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚                                                        extend_side：0左右，1左 2右
    def create_horizontal_steel_modify(self,SteelLength,hook_side,DegreesHook,HoriExtend,extendside,start,H_flag=0,H=0): #钢筋长度，锚的延伸方向,弯曲的长度,钢筋延长的长度,钢筋延长的方向,补钢筋开始的位置
        #def create_horizontal_steelt(self):  
        steel_list = []
                    #保护层混凝土属性
        #cover = ConcreteCoverProperties.left_right(self.HoriSideCover,self.HoriSideCover)
        cover = ConcreteCoverProperties(0,0,0,self.HoriBottomCover) #self.VertBottomCover)#第四个参数是设置钢筋元素离底部的距离多少开始
        rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':0,
                        'steel_grade':self.HoriSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}    

        longit = LongitudinalSteel(cover,rebar_prop)

        steel_hs1 = longit.shape_steel(SteelLength)

        if HoriExtend > 0:
            HoriExtend += self.HoriFrontCover
        if not self.Degrees_HS2:
            steel_hs2_1 = steel_hs2_2 = longit.shape_extend_steel(length=SteelLength,extend=HoriExtend,extend_side=extendside)
        else:
            if HoriExtend > 0:
                steel_hs2_1 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2+self.HoriFrontCover,right=self.RightAnchor_HS2+self.HoriFrontCover,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
                steel_hs2_2 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2+self.HoriFrontCover,right=self.RightAnchor_HS2+self.HoriFrontCover,mirror=True)
            else:
                steel_hs2_1 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2,right=self.RightAnchor_HS2,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
                steel_hs2_2 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2,right=self.RightAnchor_HS2,mirror=True)
        point_f_1 = AllplanGeo.Point3D(0,0,0)
        point_t_1 = AllplanGeo.Point3D(0,0,self.Height)

       
        point_f = AllplanGeo.Point3D(0,0,0)
        point_t = AllplanGeo.Point3D(self.Length,self.Width,self.Height)
        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance,0,0))
       
        #if steel_modify(H_flag,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
        if H >0:
            s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
            s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.FrontCover+self.HoriSteelDia/2,H)))
            steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
            s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
            s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.Width-self.FrontCover-self.HoriSteelDia/2,H)))
            steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 
        return steel_list 
   
    def create_tie_steel_q(self): 
        steel_list = []
        #有樑，窗，下窗樑,左柱,右柱时：
        #if self.unbeamVisual:
           #窗下梁：
           #steel_list += self.create_tie_steelt(self.WmobilePosition+2*self.VertSteelDia,self.HoriBottomCover + self.HoriSteelDia,self.WmobilePosition+self.WLength,self.WmobilePosition+self.VertSideCover+2*self.VertSteelDia,self.HoriSteelDia,self.oWmobilePosition -self.unBHeight+ self.HoriSteelDia,0)
        
        #有樑，窗，无下窗樑,左柱,右柱时：
        #if  not  self.unbeamVisual:
           #窗下梁：
        steel_list += self.create_tie_steelt(self.WmobilePosition+2*self.VertSteelDia,self.HoriBottomCover + 3/2*self.HoriSteelDia,self.WmobilePosition+self.WLength,self.WmobilePosition+self.VertSideCover+2*self.VertSteelDia,self.HoriSteelDia,self.oWmobilePosition+ self.HoriSteelDia,0)
        return steel_list
    def create_tie_steelt(self,start_x,start_xz,end_x,start2_x,start2_z,end_z,flag=0):
        steel_list = []

        """
        shape = ReinforcementShapeProperties.rebar(self.TieSteelDia,self.BendingRoller, self.TieSteelGrade, self.ConcreteGrade,AllplanReinf.BendingShapeType.Freeform)
        concrete_cover = ConcreteCoverProperties.left_right(0,0)

        
        shape_builder = AllplanReinf.ReinforcementShapeBuilder()

        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover.left),
                             (AllplanGeo.Point2D(self.Width-2*self.HoriFrontCover, 0), 0),
                             (concrete_cover.right)])

        shape_builder.SetHookStart(self.TieSteelHook,90, AllplanReinf.HookType.eStirrup)  #第一个参数是弯曲后的长度第二个参数是钢筋弯曲的角度
        shape_builder.SetHookEnd(self.TieSteelHook,135, AllplanReinf.HookType.eStirrup)
        tie_shape = shape_builder.CreateShape(shape) 
        angle = RotationAngles(0,0,90) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        tie_shape.Rotate(angle)   #旋转钢筋


        """
        cover = ConcreteCoverProperties(0,0,0,self.HoriBottomCover) #self.VertBottomCover)#第四个参数是设置钢筋元素离底部的距离多少开始

        bending_shape_type = AllplanReinf.BendingShapeType.OpenStirrup     #获取箍筋类型属性
        rebar_prop = {  'diameter':self.TieSteelDia,                       #钢铁的直径
                        'bending_roller':0,                                 #弯折栓因子
                        'steel_grade':self.TieSteelGrade,                   #钢铁的等级
                        'concrete_grade':self.ConcreteGrade,                #混泥土的等级
                        'bending_shape_type':bending_shape_type}            #形状类型属性

        longit = LongitudinalSteel(cover,rebar_prop) 
        if self.angle == 135:
            tie_shape= longit.shape_hook_steel(self.Width-2*self.FrontCover+4*self.TieSteelDia,self.TieSteelHook,hook_side=3,degrees=135+180,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
        else:
            tie_shape= longit.shape_hook_steel(self.Width-2*self.FrontCover-self.TieSteelDia,self.TieSteelHook,hook_side=3,degrees=90+180,mirror=False) #hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚
        #steel_hs2_2 = longit.shape_hook_steel(SteelLength,DegreesHook,hook_side=hook_side,left=self.LeftAnchor_HS2+self.HoriFrontCover,right=self.RightAnchor_HS2+self.HoriFrontCover,mirror=True)
        angle = RotationAngles(0,0,90) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        tie_shape.Rotate(angle)   #旋转钢筋
        
        Height2=self.oWmobilePosition+self.WHeight- self.HoriTopCover
       
        lines = int((end_z - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
    #垂直放的钢筋数减1      #长度       垂直左或右保护层         垂直钢筋直径              垂直间距
        rows = int((end_x - 2 * self.VertSideCover - self.VertSteelDia) / self.VertDistance)
        if self.TieMode == 1:
            for x in range(lines+1):

                #point_f = AllplanGeo.Point3D(2 * self.VertSteelDia,0,distance)   #三维点对象
                #point_t = AllplanGeo.Point3D(self.Length + 2 * self.VertSteelDia,0,distance)
                if self.angle == 135:
                      point_f = AllplanGeo.Point3D(start_x,self.FrontCover-2*self.TieSteelDia,start_xz)   #三维点对象
                      point_t = AllplanGeo.Point3D(end_x,self.FrontCover-2*self.TieSteelDia,start_xz)
                else:
                      point_f = AllplanGeo.Point3D(start_x,self.FrontCover+1/2*self.TieSteelDia,start_xz)   #三维点对象
                      point_t = AllplanGeo.Point3D(end_x,self.FrontCover+1/2*self.TieSteelDia,start_xz)
                if x % 3 == 0:                       #创建一个由两个点和一个杆距离定义的线性布局
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,  #位置
                                                                                                tie_shape,  #形状
                                                                                                point_f,  #起点位置
                                                                                                point_t,    #放置点位置
                                                                                                self.VertSideCover,  #混凝土保   护层在左边的位置
                                                                                                self.VertSideCover,  #混凝土保护层在右边的位置
                                                                                                3*self.VertDistance,  #间距
                                                                                                3))    #适用于距离/起止阀盖的调整

                start_xz += self.HoriDistance
            #last row             高             直径            间距                底部层             顶部层

                         
        elif self.TieMode == 2:
           
            for x in range(rows + 1): 
                
                if start2_x > (self.WmobilePosition+self.WLength):
                        break

                if x % 4 == 0:
                    #point_f = AllplanGeo.Point3D(distance,0,self.HoriSteelDia)
                    #point_t = AllplanGeo.Point3D(distance,0,self.Height + self.HoriSteelDia)
                    if self.angle == 135:
                            point_f = AllplanGeo.Point3D(start2_x,self.FrontCover-2*self.TieSteelDia,start2_z)
                            point_t = AllplanGeo.Point3D(start2_x,self.FrontCover-2*self.TieSteelDia,end_z)
                    else:
                         point_f = AllplanGeo.Point3D(start2_x,self.FrontCover+self.TieSteelDia/2,start2_z)
                         point_t = AllplanGeo.Point3D(start2_x,self.FrontCover+self.TieSteelDia/2,end_z)
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                tie_shape,
                                                                                                point_f,
                                                                                                point_t,
                                                                                                self.HoriBottomCover,
                                                                                                self.HoriTopCover,
                                                                                                4*self.HoriDistance,
                                                                                                3))  
                if (x + 2) % 4 == 0 and x != 0:
                    #point_f = AllplanGeo.Point3D(distance,0,self.HoriSteelDia + 2*self.HoriDistance)
                    #point_t = AllplanGeo.Point3D(distance,0,self.Height + self.HoriSteelDia)
                    if self.angle == 135:
                            point_f = AllplanGeo.Point3D(start2_x,self.FrontCover-2*self.TieSteelDia,start2_z+2*self.HoriDistance)
                            point_t = AllplanGeo.Point3D(start2_x,self.FrontCover-2*self.TieSteelDia,end_z)
                    else:
                            point_f = AllplanGeo.Point3D(start2_x,self.FrontCover+self.TieSteelDia/2,start2_z+2*self.HoriDistance)
                            point_t = AllplanGeo.Point3D(start2_x,self.FrontCover+self.TieSteelDia/2,end_z)
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                tie_shape,
                                                                                                point_f,
                                                                                                point_t,
                                                                                                self.HoriBottomCover,
                                                                                                self.HoriTopCover,
                                                                                                4*self.HoriDistance,
                                                                                                3))

                #distance += self.VertDistance
                start2_x += self.VertDistance

        return steel_list     
    def create_add_vertical_steelt(self):
        steel_list = []
        rebar_prop = {  'diameter':self.addSteelDia,
                        'bending_roller':0,
                        'steel_grade':self.addSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}    
                     #纵向钢筋 
        cover = ConcreteCoverProperties(0,0,0,0) #self.VertBottomCover)#第四个参数是设置钢筋元素离底部的距离多少开始

        longitudinal = LongitudinalSteel(cover,rebar_prop)#建立钢筋（默认是纵向/垂直钢筋)

        #steel_shape = longitudinal.shape_extend_steel(length=self.Height,extend=self.VertExtendLength,extend_side=2,vertical=True)  #建立延伸钢筋（默认是纵向/垂直钢筋)
        steel_shape = longitudinal.shape_extend_steel(length=self.add_Length/2,extend=self.add_Length/2,extend_side=1,vertical=True)#extend_side:1底部延长，2顶部延长
        angle = RotationAngles(0,45,0) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        steel_shape.Rotate(angle)   #旋转钢筋

        for  i in range(int(self.count)):
                i +=1
                #左上角
                point_f = AllplanGeo.Point3D(0,0,0)
                point_t = AllplanGeo.Point3D(self.Length ,0,0)
                vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))

                s_shape_12 = AllplanReinf.BendingShape(steel_shape)
                s_shape_12.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition+self.WHeight+math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_12))
        
                s_shape_22 = AllplanReinf.BendingShape(steel_shape)
                s_shape_22.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition+self.WHeight+math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_22))

                  #右下角
                s_shape_32 = AllplanReinf.BendingShape(steel_shape)
                s_shape_32.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((i*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_32))

                s_shape_42 = AllplanReinf.BendingShape(steel_shape)
                s_shape_42.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((i*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_42))

        #还原角度
        angle = RotationAngles(0,90,0) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        steel_shape.Rotate(angle)   #旋转钢筋
        for  i in range(int(self.count)):
                i +=1
                #右上角
                s_shape_52 = AllplanReinf.BendingShape(steel_shape)
                s_shape_52.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((i*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                                      self.oWmobilePosition+self.WHeight+math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_52))

                s_shape_62 = AllplanReinf.BendingShape(steel_shape)
                s_shape_62.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((i*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),  \
                                                                      self.oWmobilePosition+self.WHeight+math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_62))
                #左下角
      
                s_shape_72 = AllplanReinf.BendingShape(steel_shape)
                s_shape_72.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                                      self.oWmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2))))
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_72))

                s_shape_82 = AllplanReinf.BendingShape(steel_shape)
                s_shape_82.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2), \
                                                                      self.oWmobilePosition-math.sqrt(((i*self.mobile_Length)**2)/2)))) 
                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_82))
        
        return steel_list



    #梁########################################
    def shape_cuboid(self,length,width,height,sX=0,sY=0,sZ=0,rX=0,rY=0,rZ=0):

        axis = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(rX+sX,rY+sY,rZ+sZ),
                                            AllplanGeo.Vector3D(1,0,0),
                                            AllplanGeo.Vector3D(0,0,1))

        args = {'placement':axis,
                'length':length,
                'width':width,
                'height':height}

        shape = AllplanGeo.BRep3D.CreateCuboid(**args)
        return shape

    def shape_stirrup(self):
        '''
        箍筋建模函数
        Args:
            build_ele: build_ele.get_parameter_dict()
            build_ele: .pyp文件内的 Name标签的参数字典
        '''
        #参数
        bending_shape_type = AllplanReinf.BendingShapeType.Stirrup
        rebar_prop = {  'diameter':self.StirDiameter,
                        'bending_roller':math.pi * self.StirBendDia / 4,
                        'steel_grade':self.StirSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':bending_shape_type}      



        model_angles = RotationAngles(0,-90,0)

        #保护层混凝土属性
        concrete_props = ConcreteCoverProperties.all(self.ConcreteCover)
        #箍筋属性
        shape_props = ReinforcementShapeProperties.rebar(**rebar_prop)

        #建立箍筋模型
        shape = GeneralShapeBuilder.create_stirrup(self.Height-self.oWmobilePosition-self.WHeight+self.StirExtendLength,
                                                   self.Width,
                                                   model_angles,
                                                   shape_props,
                                                   concrete_props,
                                                   AllplanReinf.StirrupType.Column)
        if shape.IsValid():
            return shape

    def shape_longitudinal_steel(self,bar_diameter,length,extend=0,vert_extend=0,bend_flag=False):
        '''
        纵筋建模函数
        
        Args:

        '''


        point_list = []

        if bend_flag:
            shape_type = AllplanReinf.BendingShapeType.Freeform
            if self.AnchorHeadBend:
                point_list.append((AllplanGeo.Point3D(-extend,vert_extend,0),0))
                point_list.append((AllplanGeo.Point3D(-extend,0,0),0))
                # point_list.append((AllplanGeo.Point3D(-self.A_Anchor-self.B_HoriAnchor,self.B_VertAnchor,0),0))
                # point_list.append((AllplanGeo.Point3D(-self.A_Anchor,0,0),0))

                point_list.append((AllplanGeo.Point3D(length+extend,0,0),0))
            point_list.append((AllplanGeo.Point3D(0,0,0),0))
            point_list.append((AllplanGeo.Point3D(length,0,0),0))

            if self.AnchorTailBend:
                point_list.append((AllplanGeo.Point3D(-extend,0,0),0))
                point_list.append((AllplanGeo.Point3D(length,0,0),0))
            # point_list.append((AllplanGeo.Point3D(length+self.A_Anchor,0,0),0))    
            # point_list.append((AllplanGeo.Point3D(length+self.A_Anchor+self.B_HoriAnchor,self.B_VertAnchor,0),0))
                point_list.append((AllplanGeo.Point3D(length+extend,0,0),0))
                point_list.append((AllplanGeo.Point3D(length+extend,vert_extend,0),0))
        else:
            shape_type = AllplanReinf.BendingShapeType.LongitudinalBar
            point_list.append((AllplanGeo.Point3D(-extend,0,0),0))
            point_list.append((AllplanGeo.Point3D(length+extend,0,0),0))  

        shape_build = AllplanReinf.ReinforcementShapeBuilder()
        shape_build.AddPoints(point_list)
        rebar_prop = {  'diameter':bar_diameter,
                        'bending_roller':bar_diameter*math.pi/10,
                        'steel_grade':self.BarSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type': shape_type}        
        shape_props = ReinforcementShapeProperties.rebar(**rebar_prop)
        shape = shape_build.CreateShape(shape_props)
        angle = RotationAngles(90,0,0)
        shape.Rotate(angle)
        if shape.IsValid():
            return shape 

    def shape_waist_steel(self,bar_diameter,point_f,point_t,extend=0,mirror=False):

        point_list = []

        if mirror:
            point_list.append((AllplanGeo.Point3D(point_f-extend,0,0),0))
            point_list.append((AllplanGeo.Point3D(point_t,0,0),0))
        else:
            point_list.append((AllplanGeo.Point3D(point_f,0,0),0))
            point_list.append((AllplanGeo.Point3D(point_t+extend,0,0),0))

        shape_type = AllplanReinf.BendingShapeType.Freeform
        shape_build = AllplanReinf.ReinforcementShapeBuilder()
        shape_build.AddPoints(point_list)        
        rebar_prop = {  'diameter':bar_diameter,
                        'bending_roller':0,
                        'steel_grade':self.WaistBarGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type': shape_type}        
        shape_props = ReinforcementShapeProperties.rebar(**rebar_prop)
        shape = shape_build.CreateShape(shape_props)
        if shape.IsValid():
            return shape

    def shape_tie_steel(self,length,width):

        bending_shape_type = AllplanReinf.BendingShapeType.OpenStirrup
        rebar_prop = {  'diameter':self.TieBarDia,
                        'bending_roller':0,
                        'steel_grade':self.TieBarGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':bending_shape_type}      

        angle = RotationAngles(90,0,90)

        #保护层混凝土属性
        concrete_props = ConcreteCoverProperties.all(self.ConcreteCover)

        #箍筋属性
        shape_props = ReinforcementShapeProperties.rebar(**rebar_prop)

        #
        args = {'length':length,
                'width':width,
                'shape_props':shape_props,
                'concrete_cover_props':concrete_props,
                'model_angles':angle,
                'start_hook':20,
                'end_hook':20,
                'start_hook_angle':-45,
                'end_hook_angle':-45}

        shape = GeneralShapeBuilder.create_open_stirrup(**args)
        if shape.IsValid():
            return shape

   

    def create_stirrup(self):

        if self.AntiQuakeLevel == 1:
            den_area = max(2*(self.PreHeight+self.Height-self.oWmobilePosition-self.WHeight),500)
        else:
            den_area = max(1.5*(self.PreHeight+self.Height-self.oWmobilePosition-self.WHeight),500)
        stirrup_list = []

        #构模
        shape_stirrup = self.shape_stirrup()      
        if shape_stirrup:
                if not self.DenStir:  #非全程加密
                    p_f_1 = AllplanGeo.Point3D(self.HeadCover+self.StirDiameter/2,0,self.oWmobilePosition+self.WHeight)
                    p_t_1 = AllplanGeo.Point3D(den_area+ self.HeadCover+self.StirDiameter/2+(self.StirDiameter+self.TieBarDia)*1/2,0,self.oWmobilePosition+self.WHeight)

                    p_f_2 = AllplanGeo.Point3D(den_area+self.StirDistance,0,self.oWmobilePosition+self.WHeight)
                    p_t_2 = AllplanGeo.Point3D(self.Length-den_area,0,self.oWmobilePosition+self.WHeight)

                    p_f_3 = AllplanGeo.Point3D(self.Length-den_area,0,self.oWmobilePosition+self.WHeight)
                    p_t_3 = AllplanGeo.Point3D(self.Length,0,self.oWmobilePosition+self.WHeight)  
                    
                    stirrup_1 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          shape_stirrup,
                                                                          p_f_1,
                                                                          p_t_1,
                                                                          self.HeadCover,
                                                                          0,
                                                                          self.StirDenDistance,
                                                                          3)  
                    
              
                    stirrup_2 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          shape_stirrup,
                                                                          p_f_2,
                                                                          p_t_2,
                                                                          0,
                                                                          0,
                                                                          self.StirDistance,
                                                                          3)  
                    stirrup_3 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          shape_stirrup,
                                                                          p_f_3,
                                                                          p_t_3,
                                                                          0,
                                                                          self.EndCover,
                                                                          self.StirDenDistance,
                                                                          3)  
                    
                   # attr_list = []
                    #attr_set_list = []
                    #attr_list.append(AllplanBaseElements.AttributeInteger(1013,100))   
                    #attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                    #stirrup_1.SetAttributes(attr_set_list)
                    stirrup_list.append(stirrup_1)
                    #stirrup_2.SetAttributes(attr_set_list)
                    stirrup_list.append(stirrup_2)
                    #stirrup_3.SetAttributes(attr_set_list)
                    stirrup_list.append(stirrup_3)
                    
                else:   #全程加密
                    p_f = AllplanGeo.Point3D(0,0,self.oWmobilePosition+self.WHeight)
                    p_t = AllplanGeo.Point3D(self.Length,0,self.oWmobilePosition+self.WHeight)
                    stirrup_1 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          shape_stirrup,
                                                                          p_f,
                                                                          p_t,
                                                                          self.HeadCover,
                                                                          self.EndCover,
                                                                          self.StirDenDistance,
                                                                          3)  
                
                    stirrup_list.append(stirrup_1)

                 #箍筋补偿
                                
                point_cnt_3 = AllplanGeo.Point3D(0,0,self.oWmobilePosition+self.WHeight)
                point_cnt_4 = AllplanGeo.Point3D(self.Length,self.Width,self.oWmobilePosition+self.WHeight)
                vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(0,0,0))
                s_shape = AllplanReinf.BendingShape(shape_stirrup)
                s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length-self.EndCover-1.0/2*self.StirDiameter,0,self.oWmobilePosition+self.WHeight)))
                stirrup_4 = AllplanReinf.BarPlacement(0,1,vec,point_cnt_3,point_cnt_4,s_shape)
                #stirrup_4.SetAttributes(attr_set_list)
                stirrup_list.append(stirrup_4)
 
        return stirrup_list


    def create_long_steel(self):
        steel_list = []

        switcher = {
        #钢筋等级，钢筋直径，混凝土等级，抗震等级
        (10,True,1,1):45*self.FirstDia,
        (10,True,1,2):41*self.FirstDia,
        (4,True,1,1 ):44*self.FirstDia,
        (4,True,1,2 ):40*self.FirstDia,

        (10,True,2,1):39*self.FirstDia,
        (10,True,2,2):36*self.FirstDia,
        (4,True,2,1 ):38*self.FirstDia,
        (4,True,2,2 ):35*self.FirstDia,
        (5,True,2,1 ):46*self.FirstDia,
        (5,True,2,2 ):42*self.FirstDia,
        (6,True,2,1 ):55*self.FirstDia,
        (6,True,2,2 ):50*self.FirstDia,
        (5,False,2,1):51*self.FirstDia,
        (5,False,2,2):46*self.FirstDia,
        (6,False,2,1):61*self.FirstDia,
        (6,False,2,2):56*self.FirstDia,

        (10,True,3,1):35*self.FirstDia,
        (10,True,3,2):32*self.FirstDia,
        (4,True,3,1 ):33*self.FirstDia,
        (4,True,3,2 ):30*self.FirstDia,
        (5,True,3,1 ):40*self.FirstDia,
        (5,True,3,2 ):37*self.FirstDia,
        (6,True,3,1 ):49*self.FirstDia,
        (6,True,3,2 ):45*self.FirstDia,
        (5,False,3,1):45*self.FirstDia,
        (5,False,3,2):41*self.FirstDia,
        (6,False,3,1):54*self.FirstDia,
        (6,False,3,2):49*self.FirstDia,

        (10,True,4,1):32*self.FirstDia,
        (10,True,4,2):29*self.FirstDia,
        (4,True,4,1 ):31*self.FirstDia,
        (4,True,4,2 ):28*self.FirstDia,
        (5,True,4,1 ):37*self.FirstDia,
        (5,True,4,2 ):34*self.FirstDia,
        (6,True,4,1 ):45*self.FirstDia,
        (6,True,4,2 ):41*self.FirstDia,
        (5,False,4,1):40*self.FirstDia,
        (5,False,4,2):37*self.FirstDia,
        (6,False,4,1):49*self.FirstDia,
        (6,False,4,2):45*self.FirstDia,

        (10,True,5,1):29*self.FirstDia,
        (10,True,5,2):26*self.FirstDia,
        (4,True,5,1 ):29*self.FirstDia,
        (4,True,5,2 ):26*self.FirstDia,
        (5,True,5,1 ):33*self.FirstDia,
        (5,True,5,2 ):30*self.FirstDia,
        (6,True,5,1 ):41*self.FirstDia,
        (6,True,5,2 ):38*self.FirstDia,
        (5,False,5,1):37*self.FirstDia,
        (5,False,5,2):34*self.FirstDia,
        (6,False,5,1):46*self.FirstDia,
        (6,False,5,2):42*self.FirstDia,

        (10,True,6,1):28*self.FirstDia,
        (10,True,6,2):25*self.FirstDia,
        (4,True,6,1 ):26*self.FirstDia,
        (4,True,6,2 ):24*self.FirstDia,
        (5,True,6,1 ):32*self.FirstDia,
        (5,True,6,2 ):29*self.FirstDia,
        (6,True,6,1 ):39*self.FirstDia,
        (6,True,6,2 ):36*self.FirstDia,
        (5,False,6,1):36*self.FirstDia,
        (5,False,6,2):33*self.FirstDia,
        (6,False,6,1):43*self.FirstDia,
        (6,False,6,2):39*self.FirstDia,

        (10,True,7,1):26*self.FirstDia,
        (10,True,7,2):24*self.FirstDia,
        (4,True,7,1 ):25*self.FirstDia,
        (4,True,7,2 ):23*self.FirstDia,
        (5,True,7,1 ):31*self.FirstDia,
        (5,True,7,2 ):28*self.FirstDia,
        (6,True,7,1 ):37*self.FirstDia,
        (6,True,7,2 ):34*self.FirstDia,
        (5,False,7,1):35*self.FirstDia,
        (5,False,7,2):32*self.FirstDia,
        (6,False,7,1):40*self.FirstDia,
        (6,False,7,2):37*self.FirstDia,

        (10,True,8,1):25*self.FirstDia,
        (10,True,8,2):23*self.FirstDia,
        (4,True,8,1 ):24*self.FirstDia,
        (4,True,8,2 ):22*self.FirstDia,
        (5,True,8,1 ):30*self.FirstDia,
        (5,True,8,2 ):27*self.FirstDia,
        (6,True,8,1 ):36*self.FirstDia,
        (6,True,8,2 ):33*self.FirstDia,
        (5,False,8,1):33*self.FirstDia,
        (5,False,8,2):30*self.FirstDia,
        (6,False,8,1):39*self.FirstDia,
        (6,False,8,2):36*self.FirstDia,

        (10,True,1,3):39*self.FirstDia,
        (4,True,1,3 ):38*self.FirstDia,

        (10,True,2,3):34*self.FirstDia,
        (4,True,2,3 ):33*self.FirstDia,
        (5,True,2,3 ):40*self.FirstDia,
        (6,True,2,3 ):48*self.FirstDia,
        (5,False,2,3):44*self.FirstDia,
        (6,False,2,3):53*self.FirstDia,

        (10,True,3,3):30*self.FirstDia,
        (4,True,3,3 ):29*self.FirstDia,
        (5,True,3,3 ):35*self.FirstDia,
        (6,True,3,3 ):43*self.FirstDia,
        (5,False,3,3):39*self.FirstDia,
        (6,False,3,3):47*self.FirstDia,

        (10,True,4,3):28*self.FirstDia,
        (4,True,4,3 ):27*self.FirstDia,
        (5,True,4,3 ):32*self.FirstDia,
        (6,True,4,3 ):39*self.FirstDia,
        (5,False,4,3):35*self.FirstDia,
        (6,False,4,3):43*self.FirstDia,

        (10,True,5,3):25*self.FirstDia,
        (4,True,5,3 ):25*self.FirstDia,
        (5,True,5,3 ):29*self.FirstDia,
        (6,True,5,3 ):36*self.FirstDia,
        (5,False,5,3):32*self.FirstDia,
        (6,False,5,3):40*self.FirstDia,

        (10,True,6,3):24*self.FirstDia,
        (4,True,6,3 ):23*self.FirstDia,
        (5,True,6,3 ):28*self.FirstDia,
        (6,True,6,3 ):34*self.FirstDia,
        (5,False,6,3):31*self.FirstDia,
        (6,False,6,3):37*self.FirstDia,

        (10,True,7,3):23*self.FirstDia,
        (4,True,7,3 ):22*self.FirstDia,
        (5,True,7,3 ):27*self.FirstDia,
        (6,True,7,3 ):32*self.FirstDia,
        (5,False,7,3):30*self.FirstDia,
        (6,False,7,3):35*self.FirstDia,

        (10,True,8,3):22*self.FirstDia,
        (4,True,8,3 ):21*self.FirstDia,
        (5,True,8,3 ):26*self.FirstDia,
        (6,True,8,3 ):31*self.FirstDia,
        (5,False,8,3):29*self.FirstDia,
        (6,False,8,3):34*self.FirstDia,

        }
        if self.FirstDia > 25:
            d_flag = False
        else:
            d_flag = True

        if self.AntiQuakeLevel == 1 or self.AntiQuakeLevel == 2:
            q_flag = 1
        elif self.AntiQuakeLevel == 3:
            q_flag = 2
        else:
            q_flag = 3


        if (self.BarSteelGrade,d_flag,self.ConcreteGrade,q_flag) not in switcher.keys():
            anchor = 0
        else:
            anchor = switcher[(self.BarSteelGrade,d_flag,self.ConcreteGrade,q_flag)]
        if self.AnchorBend:
            fst_shape = self.shape_longitudinal_steel(self.FirstDia,self.Length,self.SupportWidth,max(anchor-15*self.FirstDia,15*self.FirstDia),self.AnchorBend)
           
        else:
            fst_shape = self.shape_longitudinal_steel(self.FirstDia,self.Length,self.SupportWidth)
           
        cover = self.ConcreteCover + self.FirstDia/2 + self.StirDiameter

        fst_point_f = AllplanGeo.Point3D(0,0,self.ConcreteCover+2*self.StirDiameter+self.oWmobilePosition+self.WHeight)
        
        fst_point_t = AllplanGeo.Point3D(0,self.Width,self.ConcreteCover+2*self.StirDiameter+self.oWmobilePosition+self.WHeight)
        if fst_shape:
            steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,fst_shape,fst_point_f,fst_point_t,cover,cover,self.FirstNum))

            attr_list = []
            attr_set_list = []
            attr_list.append(AllplanBaseElements.AttributeInteger(1013,102))   
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

           
        return steel_list

    def create_waist_steel(self):
        steel_list = []
        waist_length = self.Length  - 2*self.WaistHeadCover

        cover = self.ConcreteCover + self.StirDiameter
  
        distance = 0
        waist_shape = self.shape_waist_steel(self.WaistBarDia,self.WaistHeadCover,self.Length - self.WaistHeadCover,0)
        if waist_shape:
                for x in range(self.WaistNum):
                    point_f = AllplanGeo.Point3D(0,0,self.WaistPosition+distance+self.oWmobilePosition+self.WHeight)
                    point_t = AllplanGeo.Point3D(0,self.Width,self.WaistPosition +distance+self.oWmobilePosition+self.WHeight)
                    steel_1 = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,waist_shape,point_f,point_t,cover,cover,2)
                    
                    steel_list.append(steel_1)

                    distance += self.WaistDistance
        
        return steel_list

    def create_tie_steel_l(self):
        steel_list = []
        if self.AntiQuakeLevel == 1:
            den_area = max(2*(self.PreHeight+self.Height-self.oWmobilePosition-self.WHeight),500)
        else:
            den_area = max(1.5*(self.PreHeight+self.Height-self.oWmobilePosition-self.WHeight),500)
        tie_shape = self.shape_tie_steel(self.Width,self.TieBarDia/4)

        attr_list = []
        attr_set_list = []
        #attr_list.append(AllplanBaseElements.AttributeInteger(1013,103))   
        #attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

        if tie_shape:
                if not self.DenStir:
                    distance = 0
                    for x in range(self.WaistNum):
                        p_f_1 = AllplanGeo.Point3D(self.HeadCover+self.StirDiameter/2+(self.StirDiameter+self.TieBarDia)*3/5,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)
                        p_t_1 = AllplanGeo.Point3D(den_area + self.HeadCover+self.StirDiameter/2+(self.StirDiameter+self.TieBarDia)*3/5,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)

                        p_f_2 = AllplanGeo.Point3D(den_area+self.StirDistance+self.StirDiameter,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)
                        p_t_2 = AllplanGeo.Point3D(self.Length-den_area+self.StirDiameter,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)

                        p_f_3 = AllplanGeo.Point3D(self.Length-den_area+self.StirDiameter,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)
                        p_t_3 = AllplanGeo.Point3D(self.Length +self.StirDiameter,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)  
                        steel_t_1 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    tie_shape,
                                                                                                    p_f_1,
                                                                                                    p_t_1,
                                                                                                    self.HeadCover,
                                                                                                    0,
                                                                                                    self.TieBarRatio*self.StirDenDistance,
                                                                                                    3)
                        steel_t_1.SetAttributes(attr_set_list)
                        steel_list.append(steel_t_1)
                        
                        steel_t_2 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    tie_shape,
                                                                                                    p_f_2,
                                                                                                    p_t_2,
                                                                                                    0,
                                                                                                    0,
                                                                                                    self.TieBarRatio*self.StirDistance,
                                                                                                    3)
                        steel_t_2.SetAttributes(attr_set_list)
                        steel_list.append(steel_t_2)
                        
                        steel_t_3 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    tie_shape,
                                                                                                    p_f_3,
                                                                                                    p_t_3,
                                                                                                    0,
                                                                                                    0,
                                                                                                    self.TieBarRatio*self.StirDenDistance,
                                                                                                    3)
                        steel_t_3.SetAttributes(attr_set_list)
                        steel_list.append(steel_t_3)
                        distance += self.WaistDistance
                
                else:
                    distance = 0
                    for x in range(self.WaistNum):
                        p_f = AllplanGeo.Point3D(self.HeadCover+self.StirDiameter,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)
                        p_t = AllplanGeo.Point3D(self.Length + self.HeadCover+self.StirDiameter/2,0,self.WaistPosition - 2*self.TieBarDia + distance+self.oWmobilePosition+self.WHeight)
                        steel_t_1 = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    tie_shape,
                                                                                                    p_f,
                                                                                                    p_t,
                                                                                                    0,
                                                                                                    0,
                                                                                                    self.TieBarRatio*self.StirDenDistance,
                                                                                                    3)
                        steel_t_1.SetAttributes(attr_set_list)
                        steel_list.append(steel_t_1)
                        distance += self.WaistDistance

   
                
              


        return steel_list

    #柱子##########################################################################
    def create_stirrup_z(self):

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
        #左边柱子
  
        sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.WmobilePosition,self.Width)
        stir_shape = stirrup.shape_stirrup(self.WmobilePosition,self.Width)


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

        point_f_3 = AllplanGeo.Point3D(0,0,self.Height-self.TopDensAreaLength-self.StirDiameter)
        point_t_3 = AllplanGeo.Point3D(0,0,self.Height-self.StirDiameter)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f_3,
                                                                          point_t_3,
                                                                          0,
                                                                          self.StirUnsCover,
                                                                          self.StirDenseDistance,
                                                                          2) ) 

        #右边柱子
        sleeve_stir_shape = sleeve_stirrup.shape_stirrup(self.Length-self.WLength-self.WmobilePosition,self.Width)
        stir_shape = stirrup.shape_stirrup(self.Length-self.WLength-self.WmobilePosition,self.Width)


        point_f_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,0)
        point_t_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.SleeveAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          sleeve_stir_shape,
                                                                          point_f_1,
                                                                          point_t_1,
                                                                          self.StirUpsCover,
                                                                          0,
                                                                          self.StirDenseDistance,
                                                                          3) )       

        point_f_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.SleeveAreaLength)
        point_t_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.DensAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f_2,
                                                                          point_t_2,
                                                                          self.StirDenseDistance/2,
                                                                          0,
                                                                          self.StirDenseDistance,
                                                                          3) )   

        point_f = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.DensAreaLength)
        point_t = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.Height-self.TopDensAreaLength)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f,
                                                                          point_t,
                                                                          0,
                                                                          0,
                                                                          self.StirSparseDistance,
                                                                          3) ) 

        point_f_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.Height-self.TopDensAreaLength-self.StirDiameter)
        point_t_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition,0,self.Height-self.StirDiameter)
        stirrup_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                          stir_shape,
                                                                          point_f_3,
                                                                          point_t_3,
                                                                          0,
                                                                          self.StirUnsCover,
                                                                          self.StirDenseDistance,
                                                                          2) ) 
        return stirrup_list


    def create_longitudinal_steel_z(self):
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

        steel_shape = longitudinal.shape_extend_steel(length=self.Height-self.VertTopLength,extend=0,extend_side=2,vertical=True)
        hori_steel_shape = hori_longitudinal.shape_extend_steel(length=self.Height-self.VertTopLength,extend=0,extend_side=2,vertical=True)
        foot_steel_shape = foot_longitudinal.shape_extend_steel(length=self.Height-self.VertTopLength,extend=0,extend_side=2,vertical=True)
        #左边的柱子钢筋
        
        #foot steel
        point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                    math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.FootSteelDia/2,
                                    0)
        point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
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
        point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
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
        """
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,steel_shape,
                                                                                        point_f_v1,point_t_v1,
                                                                                        0,
                                                                                        0,
                                                                                        self.VertNum))    
        
        point_f_v2 = AllplanGeo.Point3D(self.WmobilePosition-(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2),
                                        math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance,
                                        0)
        point_t_v2 = AllplanGeo.Point3D(self.WmobilePosition-(self.StirSideCover+self.StirDiameter+self.VertSteelDia/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.VertDistance,
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,steel_shape,
                                                                                        point_f_v2,point_t_v2,
                                                                                        0,
                                                                                        0,
                                                                                        self.VertNum))        
        """
        point_f_h1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        point_t_h1 = AllplanGeo.Point3D(self.WmobilePosition-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance_z,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h1,point_t_h1,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))    

        point_f_h2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        point_t_h2 = AllplanGeo.Point3D(self.WmobilePosition-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance_z,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h2,point_t_h2,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))  
        
        #右边的柱子钢筋
         #foot steel
        point_f_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
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
        point_f_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.FootSteelDia/2,0)
        point_t_2 = AllplanGeo.Point3D(self.Length-math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2),
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.FootSteelDia/2,0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,foot_steel_shape,
                                                                                        point_f_2,point_t_2,
                                                                                        0,
                                                                                        0,
                                                                                        2))



        
        point_f_v1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.StirSideCover+self.StirDiameter+self.VertSteelDia/2,
                                        math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.VertDistance,
                                        0)
        point_t_v1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.StirSideCover+self.StirDiameter+self.VertSteelDia/2,
                                        self.Width-(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.VertDistance,
                                        0)
        """
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
        """
        point_f_h1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        point_t_h1 = AllplanGeo.Point3D(self.Length-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance_z,
                                        self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2,
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h1,point_t_h1,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))    

        point_f_h2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        point_t_h2 = AllplanGeo.Point3D(self.Length-(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-self.HoriDistance_z,
                                        self.Width-(self.StirFrontCover+self.StirDiameter+self.VertSteelDia/2),
                                        0)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_count(0,hori_steel_shape,
                                                                                        point_f_h2,point_t_h2,
                                                                                        0,
                                                                                        0,
                                                                                        self.HoriNum))  
        
    
        return steel_list
    
    def create_tie_steel_z(self):
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
        

        ######左边柱子拉筋##############
        vt_sleeve_tie_shape = vt_sleeve_tie.shape_tie_steel(length=self.WmobilePosition,width=4*self.TieSteelDia+self.SleeveThick,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        vt_tie_shape = vt_tie.shape_tie_steel(length=self.WmobilePosition,width=4*self.TieSteelDia,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

     
        vl = self.Width-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.VertDistance
        hl = self.WmobilePosition-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.HoriDistance_z
  


        #dv = vl / (self.VertNum - 1)
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

        #dv_sleeve_stirrup_shape = v_sleeve_tie.shape_stirrup(self.WmobilePosition,dv+self.VertSteelDia/2+2*self.StirDiameter+2*self.SleeveThick,0,1)
        #dv_stirrup_shape = v_tie.shape_stirrup(self.WmobilePosition,dv+self.VertSteelDia/2+2*self.StirDiameter,0,1)        




             #dh
        distance = 0
        for x in range(self.HoriNum):
            point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.StirDiameter)
            point_t_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)

            point_f_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)
            point_t_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)

            point_f = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)
            point_t = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height+self.StirDiameter-self.TopDensAreaLength)

            point_f_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height-self.TopDensAreaLength)
            point_t_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height)
            

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
                                                                                      self.StirUnsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) ) 
            else:
                if x % 2 == 0:
                    t_point_f_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                            0,
                                            self.StirDiameter)
                    t_point_t_1 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)

                    t_point_f_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)
                    t_point_t_2 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)

                    t_point_f = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)
                    t_point_t = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height+self.StirDiameter-self.TopDensAreaLength)

                    t_point_f_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height-self.TopDensAreaLength)
                    t_point_t_3 = AllplanGeo.Point3D(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height)                    
                    
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
                                                                                      self.StirUnsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) )
                    
            distance += int(dh)


        ######右边柱子拉筋##############
        vt_sleeve_tie_shape = vt_sleeve_tie.shape_tie_steel(length=self.Length-self.WLength-self.WmobilePosition,width=4*self.TieSteelDia+self.SleeveThick,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        vt_tie_shape = vt_tie.shape_tie_steel(length=self.Length-self.WLength-self.WmobilePosition,width=4*self.TieSteelDia,
                                        rotate=RotationAngles(180,0,0),hook=self.TieSteelHook,
                                        degrees=self.TieSideHookAngle)

        # count = int((self.Length - 2*(self.StirSideCover+self.StirDiameter+self.VertSteelDia) - self.TieSteelDia) / self.VertDistance) + 1
        # bar_distance = (self.Length - 2*(self.StirSideCover+self.StirDiameter+self.VertSteelDia) - self.TieSteelDia) / count

        #vl -vertical steel total space
        #hl -horizental steel total space
        vl = self.Width-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirFrontCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.VertDistance
        hl = self.Length-self.WLength-self.WmobilePosition-2.0*(math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2))-2.0*self.HoriDistance_z
        # dv -vertical steel space
        #hl -horizental steel space
        #dv = vl / (self.VertNum - 1)
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

        #dv_sleeve_stirrup_shape = v_sleeve_tie.shape_stirrup(self.Length-self.WLength-self.WmobilePosition,dv+self.VertSteelDia/2+2*self.StirDiameter+2*self.SleeveThick,0,1)
        #dv_stirrup_shape = v_tie.shape_stirrup(self.Length-self.WLength-self.WmobilePosition,dv+self.VertSteelDia/2+2*self.StirDiameter,0,1)        

        
        #dh
        distance = 0
        for x in range(self.HoriNum):
            point_f_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.StirDiameter)
            point_t_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2-self.SleeveThick,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)

            point_f_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.SleeveAreaLength+self.StirDiameter)
            point_t_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)

            point_f = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.DensAreaLength+self.StirDiameter)
            point_t = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height+self.StirDiameter-self.TopDensAreaLength)

            point_f_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height-self.TopDensAreaLength)
            point_t_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance-self.StirDiameter/2-self.HoriSteelDia/2,
                                            0,
                                            self.Height)
            

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
                                                                                      self.StirUnsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) ) 
                   
            else:
                if x % 2 == 0:
                    t_point_f_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                            0,
                                            self.StirDiameter)
                    t_point_t_1 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2+self.SleeveThick,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)

                    t_point_f_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.SleeveAreaLength+self.StirDiameter)
                    t_point_t_2 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)

                    t_point_f = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.DensAreaLength+self.StirDiameter)
                    t_point_t = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height+self.StirDiameter-self.TopDensAreaLength)

                    t_point_f_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height-self.TopDensAreaLength)
                    t_point_t_3 = AllplanGeo.Point3D(self.WLength+self.WmobilePosition+math.sqrt(((math.sqrt(2.0*((self.StirSideCover+3.0*self.StirDiameter)**2.0))-3.0/2*self.StirDiameter+self.FootSteelDia/2.0)**2)/2)+self.HoriDistance_z+distance+self.StirDiameter/2+self.HoriSteelDia/2,
                                                    0,
                                                    self.Height)                    
                    
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

                    
                    #steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                       #               tie_shape,
                                                                       #               t_point_f_3,
                                                                       #               t_point_t_3,
                                                                        #              0,
                                                                        ##              self.StirUnsCover,
                                                                        #              self.StirSparseDistance,
                                                                        #              2) ) 
                    steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                      tie_shape,
                                                                                      t_point_f_3,
                                                                                      t_point_t_3,
                                                                                      0,
                                                                                      self.StirUnsCover,
                                                                                      self.StirDenseDistance,
                                                                                      2) )
                    

            distance += int(dh)

 
        return steel_list