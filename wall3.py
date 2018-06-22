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
        #梁
        beam_height = 0  #没有梁时梁高度为0
        if self.beamVisual:
            beam = self.shape_cuboid(self.Length,self.Width,self.BHeight,sZ=self.Height-self.BHeight)
            err,rectangle = AllplanGeo.MakeSubtraction(rectangle,beam)
            beam_height = self.BHeight                  
        #窗
        if self.windowVisual:
             window = self.shape_cuboid(self.WLength,self.Width,self.WHeight,sX=self.WmobilePosition,sZ=self.oWmobilePosition)
             err,rectangle = AllplanGeo.MakeSubtraction(rectangle,window)
        #左窗柱
        if  self.LpillarsVisual and self.windowVisual:
             Lpillars = self.shape_cuboid(self.LPLength,self.Width,self.Height-beam_height,sX=self.WmobilePosition-self.LPLength)
             err,rectangle = AllplanGeo.MakeSubtraction(rectangle,Lpillars)
        #右窗柱
        if  self.RpillarsVisual and self.windowVisual:
           Rpillars = self.shape_cuboid(self.RPLength,self.Width,self.Height-beam_height,sX=self.WmobilePosition+self.WLength)
           err,rectangle = AllplanGeo.MakeSubtraction(rectangle,Rpillars)
        #上窗梁
        if self.onbeamVisual and self.windowVisual:
            onbeam = self.shape_cuboid(self.onBLength,self.Width,self.onBHeight,sX=(self.WmobilePosition+self.WLength/2-self.onBLength/2),sZ=self.oWmobilePosition+self.WHeight)
            err,rectangle = AllplanGeo.MakeSubtraction(rectangle,onbeam)
        #下窗梁
        if self.unbeamVisual and self.windowVisual :
            unbeam = self.shape_cuboid(self.unBLength,self.Width,self.unBHeight,sX=(self.WmobilePosition+self.WLength/2-self.unBLength/2),sZ=self.oWmobilePosition-self.unBHeight)
            err,rectangle = AllplanGeo.MakeSubtraction(rectangle,unbeam)
        #门
        if self.DoorVisual:
            door = self.shape_cuboid(self.DLength,self.Width,self.DHeight,sX=self.DmobilePosition,sZ=self.oDmobilePosition)
            err,rectangle = AllplanGeo.MakeSubtraction(rectangle,door)
        #左门柱
        if self.LDpillarsVisual and self.DoorVisual:
             LDpillars = self.shape_cuboid(self.LDPLength,self.Width,self.Height-beam_height,sX=self.DmobilePosition-self.LDPLength)
             err,rectangle = AllplanGeo.MakeSubtraction(rectangle,LDpillars)
        #右门柱
        if self.RDpillarsVisual and self.DoorVisual :
             RDpillars = self.shape_cuboid(self.RDPLength,self.Width,self.Height-beam_height,sX=self.DmobilePosition+self.DLength)
             err,rectangle = AllplanGeo.MakeSubtraction(rectangle,RDpillars)
        
        approximation = AllplanGeo.ApproximationSettings(AllplanGeo.eApproximationSettingsType.ASET_BREP_TESSELATION, 1)
        err,rectangle = AllplanGeo.CreatePolyhedron(rectangle,approximation)
     
        steel_list  += [AllplanBasisElements.ModelElement3D(self.com_prop, rectangle)]
        
        #有梁时
        beam_height = 0  #没有梁时梁高度为0
        if  self.beamVisual:
            beam_2 = self.shape_cuboid(self.Length,self.Width,self.BHeight,sZ=self.Height-self.BHeight)

            com_prop2 = AllplanBaseElements.CommonProperties()

            com_prop2.GetGlobalProperties()
            com_prop2.Pen = 1
            com_prop2.Color = 6
            steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,beam_2))
            beam_height = self.BHeight 
        #左窗柱
        if  self.LpillarsVisual and self.windowVisual:
             Lpillars_2 = self.shape_cuboid(self.LPLength,self.Width,self.Height-beam_height,sX=self.WmobilePosition-self.LPLength)
             com_prop2 = AllplanBaseElements.CommonProperties()

             com_prop2.GetGlobalProperties()
             com_prop2.Pen = 1
             com_prop2.Color = 6
             steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,Lpillars_2))
         #右窗柱
        if  self.RpillarsVisual and self.windowVisual:
             Rpillars_2 = self.shape_cuboid(self.RPLength,self.Width,self.Height-beam_height,sX=self.WmobilePosition+self.WLength)
             com_prop2 = AllplanBaseElements.CommonProperties()

             com_prop2.GetGlobalProperties()
             com_prop2.Pen = 1
             com_prop2.Color = 6
             steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,Rpillars_2))

         #上窗梁
        if  self.beamVisual and ((self.oWmobilePosition + self.WHeight +self.onBHeight) <= (self.Height - self.BHeight)):
             if self.onbeamVisual and self.windowVisual:
                    onbeam_2 = self.shape_cuboid(self.onBLength,self.Width,self.onBHeight,sX=(self.WmobilePosition+self.WLength/2-self.onBLength/2),sZ=self.oWmobilePosition+self.WHeight)
                    com_prop2 = AllplanBaseElements.CommonProperties()

                    com_prop2.GetGlobalProperties()
                    com_prop2.Pen = 1
                    com_prop2.Color = 6
                    steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,onbeam_2))
        elif  not self.beamVisual and ((self.oWmobilePosition + self.WHeight +self.onBHeight) <= (self.Height)):
             if self.onbeamVisual and self.windowVisual:
                    onbeam_2 = self.shape_cuboid(self.onBLength,self.Width,self.onBHeight,sX=(self.WmobilePosition+self.WLength/2-self.onBLength/2),sZ=self.oWmobilePosition+self.WHeight)
                    com_prop2 = AllplanBaseElements.CommonProperties()

                    com_prop2.GetGlobalProperties()
                    com_prop2.Pen = 1
                    com_prop2.Color = 6
                    steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,onbeam_2))
        #下窗梁
        if self.unbeamVisual and self.windowVisual:
             unbeam_2 = self.shape_cuboid(self.unBLength,self.Width,self.unBHeight,sX=(self.WmobilePosition+self.WLength/2-self.unBLength/2),sZ=self.oWmobilePosition-self.unBHeight)
             com_prop2 = AllplanBaseElements.CommonProperties()

             com_prop2.GetGlobalProperties()
             com_prop2.Pen = 1
             com_prop2.Color = 6
             steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,unbeam_2))
        #左门柱
        if  self.LDpillarsVisual and  self.DoorVisual:
             LDpillars_2 = self.shape_cuboid(self.LDPLength,self.Width,self.Height-beam_height,sX=self.DmobilePosition-self.LDPLength)
             com_prop2 = AllplanBaseElements.CommonProperties()

             com_prop2.GetGlobalProperties()
             com_prop2.Pen = 1
             com_prop2.Color = 6
             steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,LDpillars_2))
         #右门柱
        if  self.RDpillarsVisual and  self.DoorVisual:
             RDpillars_2 = self.shape_cuboid(self.RDPLength,self.Width,self.Height-beam_height,sX=self.DmobilePosition+self.DLength)
             com_prop2 = AllplanBaseElements.CommonProperties()

             com_prop2.GetGlobalProperties()
             com_prop2.Pen = 1
             com_prop2.Color = 6
             steel_list.append(AllplanBasisElements.ModelElement3D(com_prop2,RDpillars_2))
        
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
        """
        if self.StirVisual:
            reinforcement += self.create_stirrup()
       """
        #垂直的钢筋
        if  self.VertSteelVisual:
             reinforcement +=  self.create_longitudinal_steelr()
        #水平钢筋
        if self.HoriSteelVisual:
             reinforcement +=  self.create_horizontal_steelr()
        #拉筋
        if self.TieSteelVisual:
             reinforcement +=  self.create_tie_steel()
        #加强筋
        if self.addSteelVisual:
            reinforcement += self.create_add_vertical_steelt()
        #reinforcement += self.add()
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
        #只有樑时
        if  self.beamVisual  and not self.windowVisual  and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                             and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:
            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
        #有上梁，有窗户时
        elif  self.beamVisual and self.windowVisual  and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗上钢筋
            if  ((self.oWmobilePosition + self.WHeight ) < (self.Height - self.BHeight)):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
         #有上梁，有窗户，左柱时
        elif  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #窗上钢筋
            if (self.oWmobilePosition + self.WHeight ) < (self.Height - self.BHeight):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
         #有上梁，有窗户，右柱时
        elif  self.beamVisual and self.windowVisual  and not self.LpillarsVisual   and  self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗上钢筋
            if (self.oWmobilePosition + self.WHeight ) < (self.Height - self.BHeight):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            #lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
        #有上梁，有窗户，左右柱时
        elif  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and  self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #窗上钢筋
            if (self.oWmobilePosition + self.WHeight ) < (self.Height - self.BHeight):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            #lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
         #有上梁，有窗户，左右柱,上樑下樑时
        elif  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and  self.RpillarsVisual   and  self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #窗上钢筋
            if  ((self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height - self.BHeight)):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight +2*self.Hole_cover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.oWmobilePosition -self.WHeight- self.onBHeight,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下钢筋
            point_f_1 = AllplanGeo.Point3D(self.WmobilePosition+self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(self.WmobilePosition+self.VertSideCover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
        #有樑，门:
        elif  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
          #有樑，门,左柱:
        elif  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and  self.LDpillarsVisual  and not  self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
           #有樑，门,右柱:
        elif  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and not self.LDpillarsVisual  and   self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
           #有樑，门,左右柱:
        elif  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and  self.LDpillarsVisual  and   self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #门上的钢筋
            if (self.oDmobilePosition+self.DHeight + self.BHeight) < self.Height:
                    lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
                    point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                    point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                    point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                    point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                    steel_list += self.create_vertical_steelt(self.Height-self.BHeight -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
        #没樑，有窗户时
        elif  self.windowVisual  and not self.beamVisual and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗上钢筋
            if  ((self.oWmobilePosition + self.WHeight ) < self.Height):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗右边钢筋
            lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
         #无上梁，有窗户，左柱时
        elif  not self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #窗上钢筋
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            steel_list += self.create_vertical_steelt(self.Height-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
         #无上梁，有窗户，右柱时
        elif not  self.beamVisual and self.windowVisual  and not self.LpillarsVisual   and  self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗上钢筋
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
            steel_list += self.create_vertical_steelt(self.Height-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            #lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
         #无上梁，有窗户，左右柱时
        elif not  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and  self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.WmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #窗上钢筋
            if (self.oWmobilePosition + self.WHeight ) < self.Height:
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight+ 2*self.Hole_cover-self.HoriBottomCover)
                steel_list += self.create_vertical_steelt(self.Height-self.oWmobilePosition -self.WHeight-2*self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下刚劲
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
            #窗右边钢筋
            #lines_2 = int((self.WmobilePosition + self.WLength - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
        #无上梁，有窗户，左右柱,上樑下樑时
        elif not self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and  self.RpillarsVisual   and  self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual: 
            #窗左边钢筋
            lines_1 = int((self.WmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #窗上钢筋
            if  ((self.oWmobilePosition + self.WHeight +self.onBHeight) < self.Height):
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight +2*self.Hole_cover)
                point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.HoriFrontCover + self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.oWmobilePosition+self.WHeight-self.HoriBottomCover + self.onBHeight+2*self.Hole_cover)
                steel_list += self.create_vertical_steelt(self.Height-self.oWmobilePosition -self.WHeight- self.onBHeight,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #窗下钢筋
            #point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia+self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength-self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia+self.VertSideCover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength-self.VertSideCover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)

            point_f_1 = AllplanGeo.Point3D(self.WmobilePosition+self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength-self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(self.WmobilePosition+self.VertSideCover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength-self.VertSideCover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.oWmobilePosition-self.Hole_cover,point_f_1,point_t_1,point_f_2,point_t_2,0)
        #无樑，有门:
        elif  not self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
          #无樑，有门,左柱:
        elif not  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and  self.LDpillarsVisual  and not  self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
           #没有樑，门,右柱:
        elif not  self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and not self.LDpillarsVisual  and   self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1

            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition-self.Hole_cover,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
            steel_list += self.create_vertical_steelt(self.Height -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            #门右边的钢筋
            #point_f_1 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            #point_f_2 = AllplanGeo.Point3D(lines_2 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            #steel_list += self.create_vertical_steelt(self.Height-self.BHeight-self.HoriTopCover-self.HoriBottomCover,point_f_1,point_t_1,point_f_2,point_t_2)
         #没有樑，门,左右柱:
        elif  not self.beamVisual and not self.windowVisual  and not  self.LpillarsVisual   and not  self.RpillarsVisual   and not  self.onbeamVisual  \
                              and  self.DoorVisual    and  self.LDpillarsVisual  and   self.RDpillarsVisual and  not self.unbeamVisual:
            #门左边的钢筋
            lines_1 = int((self.DmobilePosition - self.HoriSteelDia) / self.VertDistance) +1
            #门上的钢筋
            lines_2 = int((self.DmobilePosition + self.DLength- self.HoriSteelDia) / self.VertDistance) +1
            if (self.oDmobilePosition+self.DHeight + self.BHeight) < self.Height:
                point_f_1 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                point_t_1 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.HoriFrontCover + self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                point_f_2 = AllplanGeo.Point3D(lines_1 * self.VertDistance + self.HoriSteelDia,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                point_t_2 = AllplanGeo.Point3D(self.DmobilePosition+self.DLength,self.Width - self.HoriFrontCover - self.HoriSteelDia,self.DHeight+self.Hole_cover+self.oDmobilePosition)
                steel_list += self.create_vertical_steelt(self.Height -self.DHeight-self.oDmobilePosition-self.Hole_cover-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
        else:
            point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
            point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)
            point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
            steel_list += self.create_vertical_steelt(self.Height-self.Length_BA,point_f_1,point_t_1,point_f_2,point_t_2,1)
            
        return steel_list

    def create_vertical_steelt(self,SteelLength,point_f_1,point_t_1,point_f_2,point_t_2,flag): #当flag等于1时，钢筋支持延长和弯钩
        steel_list = []

        cover = [self.Length_BA,self.Length_BA,self.Length_BA,self.Length_BA]
       
        rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':0,
                        'steel_grade':self.HoriSteelGrade,
                        'concrete_grade':self.ConcreteGrade,
                        'bending_shape_type':AllplanReinf.BendingShapeType.LongitudinalBar}    
                     #纵向钢筋
        longit = LongitudinalSteel(cover,rebar_prop)
        if flag == 1:
            if self.BendingAnchor: #弯曲锚   #锚
                 steel_vert_1 = longit.shape_anchor_steel(SteelLength,self.Length_TA,self.BendPosition,self.BendLength,self.BendWidth,2,False,True)
                 steel_vert_2 = longit.shape_anchor_steel(SteelLength,self.Length_TA,self.BendPosition,self.BendLength,self.BendWidth,2,True,True)

            else:
                 steel_vert_1 = steel_vert_2 = longit.shape_extend_steel(length=SteelLength,extend=self.Length_TA,extend_side=2,vertical=True)
        else:
            steel_vert_1 = steel_vert_2 = longit.shape_extend_steel(length=SteelLength,extend=0,extend_side=2,vertical=True)

        #point_f_1 = AllplanGeo.Point3D(0,self.HoriFrontCover + self.HoriSteelDia,0)
        #point_t_1 = AllplanGeo.Point3D(self.Length,self.HoriFrontCover + self.HoriSteelDia,0)

        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                        steel_vert_1,
                                                                                        point_f_1,
                                                                                        point_t_1,
                                                                                        self.VertSideCover,
                                                                                        self.VertSideCover,
                                                                                        self.VertDistance,
                                                                                        3))

        #point_f_2 = AllplanGeo.Point3D(0,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)
        #point_t_2 = AllplanGeo.Point3D(self.Length,self.Width - self.HoriFrontCover - self.HoriSteelDia,0)

        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                        steel_vert_2,
                                                                                        point_f_2,
                                                                                        point_t_2,
                                                                                        self.VertSideCover,
                                                                                        self.VertSideCover,
                                                                                        self.VertDistance,
                                                                                        3))
        if not  self.RpillarsVisual and not self.RDpillarsVisual:
            if steel_modify(self.Length,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover):
                 point_f_3 = AllplanGeo.Point3D(0,0,0)
                 point_t_3 = AllplanGeo.Point3D(self.Length ,0,0)
                 vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))
                 s_shape_1 = AllplanReinf.BendingShape(steel_vert_1)
                 s_shape_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover,self.HoriFrontCover + self.HoriSteelDia,0)))
                 s_shape_2 = AllplanReinf.BendingShape(steel_vert_2)
                 s_shape_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover,self.Width-self.HoriFrontCover - self.HoriSteelDia,0)))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_3,point_t_3,s_shape_1))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_3,point_t_3,s_shape_2))

        return steel_list
    def create_horizontal_steelr(self): 
        steel_list = []
        
        #有上梁时
        if  self.beamVisual  and not self.windowVisual  and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                             and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:
                lines = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
        #有上梁，窗户时
        elif  self.beamVisual and self.windowVisual  and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:     
                #布窗户以下的钢筋

                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.HoriFrontCover-self.Hole_cover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover) 
        #有上梁，窗户,左窗柱时
        elif  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                    # point_1 = AllplanGeo.Point3D(0,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #point_2 = AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-self.WmobilePosition-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.WmobilePosition)
        #有上梁，窗户,右窗柱时
        elif  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and not self.LpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     #point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
                   #有上梁，窗户,左右窗柱时
        elif  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                 #布窗上钢筋
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength,3,self.DegreesHook_HS2,self.HoriExtend,0,self.WmobilePosition)
                   #有上梁，窗户,上窗梁时
        elif  self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋   
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布上梁两边的钢筋
                if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height - self.BHeight):
                    lines_3 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_3 - lines_2):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.onBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.onBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,2)
                    #布窗梁以上钢筋
                    lines_4 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                else:
                    #布窗梁以上钢筋
                    lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_3 - lines_2):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
                     #有上梁，窗户,下窗梁时
        elif  self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:  
                   #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗下梁两边的钢筋
                #布下梁两边的钢筋
                lines_2 = int((self.oWmobilePosition - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.unBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.unBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗户两边钢筋   
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗以上钢筋
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
               #有樑，窗，上下窗樑时：
        elif  self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗下梁两边的钢筋
                lines_2 = int((self.oWmobilePosition - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.unBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.unBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                 #布窗户两边钢筋   
                lines_3 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布上梁两边的钢筋
                if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height - self.BHeight):
                    lines_4 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.onBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.onBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,2)
                    #布窗梁以上钢筋
                    lines_5 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_5 - lines_4):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_4*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+self.onBHeight+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_4*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_4+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                else:
                    #布窗梁以上钢筋
                    lines_4 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
          #有樑，窗，上下窗樑,左柱,右柱时：
        elif  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.HoriFrontCover,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+self.HoriSteelDia/2+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition,self.oWmobilePosition-self.unBHeight,self.oWmobilePosition-self.unBHeight-self.HoriTopCover-self.HoriSteelDia/2 )
                   #布窗下梁两边的钢筋
                #布窗梁以上钢筋
                lines_2 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                lines_3 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance +self.HoriSteelDia/2)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance +self.HoriSteelDia/2)
                        steel_list += self.create_horizontal_steelt(self.WLength,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition)
                    #______有樑，门时__________________
        elif  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                         #门槛钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)

                line_3 = int((self.Height- self.BHeight-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length-2*self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
                #______有樑，门,左柱时__________________
        elif  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and  self.LDpillarsVisual  and not  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                         #门槛钢筋
                         point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         steel_list += self.create_horizontal_steelt(self.Length - self.DmobilePosition-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     """
                     point_1 = AllplanGeo.Point3D(0,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                    """
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)

                line_3 = int((self.Height- self.BHeight-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length - self.DmobilePosition-self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)
                steel_list +=self.create_horizontal_steel_modify(self.Length - self.DmobilePosition-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.DmobilePosition)
             #______有樑，门,右柱时__________________
        elif  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.LDpillarsVisual  and  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                         #门槛钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     """
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                     """
                line_3 = int((self.Height- self.BHeight-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)    
                steel_list +=self.create_horizontal_steel_modify(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover) 
                #______有樑，门,左右柱时__________________
        elif  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and  self.LDpillarsVisual  and  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition <0:
                    for i in range(line_1):
                         #门槛钢筋
                         point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         steel_list += self.create_horizontal_steelt(self.DLength,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                line_3 = int((self.Height- self.BHeight-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1  
                if (self.oDmobilePosition +self.DHeight + self.BHeight) < self.Height:
                       for i in range(line_3 - line_2):
                        #门上边钢筋
                   
                            point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                            point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                            steel_list += self.create_horizontal_steelt(self.DLength,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)   
                       steel_list +=self.create_horizontal_steel_modify(self.DLength,3,self.DegreesHook_HS2,self.HoriExtend,0,self.DmobilePosition)  
        #++++++++++++++++++++++++
        
        #没有上梁，窗户时
        elif  not self.beamVisual and self.windowVisual  and not self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual  \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:     
                #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.HoriFrontCover-self.Hole_cover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
                   #没有上梁，窗户,左窗柱时
        elif not  self.beamVisual and self.windowVisual  and  self.LpillarsVisual   and not self.RpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                    # point_1 = AllplanGeo.Point3D(0,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #point_2 = AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-self.WmobilePosition-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.WmobilePosition)
        #没有上梁，窗户,右窗柱时
        elif not  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and not self.LpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋 
                
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     #point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     #steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗上钢筋
                
                lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WmobilePosition+self.WLength-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover) 
                  #没有上梁，窗户,左右窗柱时
        elif  not self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and not self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗户以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                 #布窗上钢筋
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5
                steel_list +=self.create_horizontal_steel_modify(self.WLength,3,self.DegreesHook_HS2,self.HoriExtend,0,self.WmobilePosition) 
          #没有上梁，窗户,上窗梁时
        elif  not self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not self.unbeamVisual:  
                   #布窗以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗户两边钢筋   
                lines_2 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布上梁两边的钢筋
                if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height):
                    lines_3 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_3 - lines_2):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.onBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.onBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,2)
                    #布窗梁以上钢筋
                    lines_4 = int((self.Height -self.BHeight-self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+self.onBHeight+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                else:
                    #布窗梁以上钢筋
                    lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_3 - lines_2):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+self.onBHeight+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
                  #没有上梁，窗户,下窗梁时
        elif  not  self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:  
                   #布窗以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布下梁两边的钢筋
                lines_2 = int((self.oWmobilePosition - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.unBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.unBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗户两边钢筋   
                lines_3 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布窗梁以上钢筋
                lines_4 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_4 - lines_3):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
               #没有樑，窗，上下窗樑时：
        elif   not self.beamVisual and self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight-self.Hole_cover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                #布窗下梁两边的钢筋
                lines_2 = int((self.oWmobilePosition - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_2 - lines_1):
                #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.unBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.unBLength/2,self.Width-self.HoriFrontCover,(lines_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-(self.WmobilePosition -self.WLength/2-self.unBLength/2)-self.HoriFrontCover,2,point_1,point_2,lines_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                 #布窗户两边钢筋   
                lines_3 = int((self.oWmobilePosition + self.WHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                     #左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WmobilePosition-self.Hole_cover-self.HoriFrontCover,1,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     #右边钢筋
                     point_1 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.WmobilePosition+self.WLength+self.Hole_cover,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition-self.WLength-self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,2)
                #布上梁两边的钢筋
                if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height):
                    lines_4 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        #左边钢筋
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WmobilePosition + (self.WLength/2-self.onBLength/2)-self.HoriFrontCover,1,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,1)
                        #右边钢筋
                        point_1 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.WmobilePosition + self.WLength/2+self.onBLength/2,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-self.WmobilePosition -self.WLength/2-self.onBLength/2-self.HoriFrontCover,2,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,2)
                    #布窗梁以上钢筋
                    lines_5 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_5 - lines_4):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_4*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+self.onBHeight+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_4*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_4+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                else:
                    #布窗梁以上钢筋
                    lines_4 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                    for i in range(lines_4 - lines_3):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+self.onBHeight+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(lines_3*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,lines_3+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover) 
          #没有樑，窗，上下窗樑,左柱,右柱时：
        elif  not  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                #布窗下梁以下的钢筋
                lines_1 = int((self.oWmobilePosition-self.unBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_1):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.HoriFrontCover,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.HoriFrontCover,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.WLength-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition,self.oWmobilePosition-self.unBHeight,self.oWmobilePosition-self.unBHeight-self.HoriTopCover-self.HoriSteelDia/2)
                  #布窗下梁两边的钢筋
                 #布窗梁以上钢筋
                lines_2 = int((self.oWmobilePosition + self.WHeight +self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                lines_3 = int((self.Height -self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(lines_3 - lines_2):
                        point_1 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.HoriFrontCover+self.WmobilePosition,self.Width-self.HoriFrontCover,(lines_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.WLength-2*self.HoriFrontCover,3,point_1,point_2,lines_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.WLength-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover+self.WmobilePosition) 
        #______没有樑，门时__________________
        elif not  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                        #门槛钢筋
                         point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)

                line_3 = int((self.Height-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length-2*self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
              #______没有樑，门,左柱时__________________
        elif not  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and  self.LDpillarsVisual  and not  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                        #门槛钢筋
                        point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                        steel_list += self.create_horizontal_steelt(self.Length - self.DmobilePosition-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     """
                     point_1 = AllplanGeo.Point3D(0,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                    """
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover-self.HoriFrontCover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)

                line_3 = int((self.Height-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length - self.DmobilePosition-self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)
                steel_list +=self.create_horizontal_steel_modify(self.Length - self.DmobilePosition-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.DmobilePosition)
         #______没有樑，门,右柱时__________________
        elif  not self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.LDpillarsVisual  and  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                         #门槛钢筋
                         point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         steel_list += self.create_horizontal_steelt(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                for i in range(line_2 - line_1):
                     #门左边钢筋
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition -self.HoriFrontCover-self.Hole_cover,1,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,1)
                     """
                     #门右边钢筋
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition + self.DLength +self.Hole_cover,self.Width-self.HoriFrontCover,(line_1*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt( self.Length -self.DLength- self.DmobilePosition -self.Hole_cover,2,point_1,point_2,line_1+i,self.DegreesHook_HS2,self.HoriExtend,2)
                     """
                line_3 = int((self.Height-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)  
                steel_list +=self.create_horizontal_steel_modify(self.DmobilePosition + self.DLength-self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)  
        #______没有樑，门,左右柱时__________________
        elif not  self.beamVisual and   self.DoorVisual and  not self.windowVisual  and  not self.RpillarsVisual   and  not self.LpillarsVisual   and not  self.onbeamVisual   \
                              and  self.LDpillarsVisual  and  self.RDpillarsVisual and  not  self.unbeamVisual:
                line_1 = int((self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                if self.oDmobilePosition >0:
                    for i in range(line_1):
                      #门槛钢筋
                         point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,self.HoriBottomCover+i*self.HoriDistance)
                         steel_list += self.create_horizontal_steelt(self.DLength,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)


                line_2 = int((self.DHeight + self.oDmobilePosition- self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1
                line_3 = int((self.Height-self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) +1              
                for i in range(line_3 - line_2):
                     #门上边钢筋
                   
                     point_1 = AllplanGeo.Point3D(self.DmobilePosition,self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.DmobilePosition,self.Width-self.HoriFrontCover,(line_2*self.HoriDistance+self.HoriBottomCover + self.HoriSteelDia)+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.DLength,3,point_1,point_2,line_2+i,self.DegreesHook_HS2,self.HoriExtend,0)    
                steel_list +=self.create_horizontal_steel_modify(self.DLength,3,self.DegreesHook_HS2,self.HoriExtend,0,self.DmobilePosition)    
        #++++++++++++++++++++++++
        else: 
                #当没有柱子，窗，窗梁，门，上梁时
                lines = int((self.Height - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance) + 1
                for i in range(lines):
                     point_1 = AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     point_2 = AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.HoriSteelDia/2+self.HoriBottomCover+i*self.HoriDistance)
                     steel_list += self.create_horizontal_steelt(self.Length-2*self.HoriFrontCover,3,point_1,point_2,i,self.DegreesHook_HS2,self.HoriExtend,0)  #第二个参数hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚 0不延伸左右锚 4  5 
                steel_list +=self.create_horizontal_steel_modify(self.Length-2*self.HoriFrontCover,3,self.DegreesHook_HS2,self.HoriExtend,0,self.HoriFrontCover)
        return steel_list
    ##hook_side:1 左延伸锚 2 右延伸锚 3左右延伸锚                                                        extend_side：0左右，1左 2右
    def create_horizontal_steelt(self,SteelLength,hook_side,point_1,point_2,lines,DegreesHook,HoriExtend,extendside): #钢筋长度，锚的延伸方向，第一钢筋的具体位置，第二钢筋的具体方向,第几根钢筋,弯曲的长度,钢筋延长的长度,钢筋延长的方向
        #def create_horizontal_steelt(self):  
        steel_list = []
                    #保护层混凝土属性
        #cover = ConcreteCoverProperties.left_right(self.HoriSideCover,self.HoriSideCover)
        cover = ConcreteCoverProperties(0,0,0,self.HoriBottomCover) #self.VertBottomCover)#第四个参数是设置钢筋元素离底部的距离多少开始
        rebar_prop = {  'diameter':self.HoriSteelDia,
                        'bending_roller':20,
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
        """
        if lines % 3 != 0:                      #生成图形
             s_shape_hs1_1 = AllplanReinf.BendingShape(steel_hs1)
                              #移动位移              
             #s_shape_hs1_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.HoriFrontCover,distance))) #该三维点是钢筋的具体位置
             s_shape_hs1_1.Move(AllplanGeo.Vector3D(point_1))
                                                  #建立钢筋
             steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_1))

             s_shape_hs1_2 = AllplanReinf.BendingShape(steel_hs1)
             #s_shape_hs1_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,distance)))
             s_shape_hs1_2.Move(AllplanGeo.Vector3D(point_2))
             steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_2))
         """   
        #else:
        s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
             #s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.HoriFrontCover,distance)))
        s_shape_hs2_1.Move(AllplanGeo.Vector3D(point_1))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))

        s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
            #s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,distance)))
        s_shape_hs2_2.Move(AllplanGeo.Vector3D(point_2))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2))
        """
        #右上梁时，填补最后一根钢筋
        if  self.beamVisual:    
            lines_1 = int((self.Height -self.BHeight - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
            if steel_modify(self.Height -self.BHeight,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
                #if (lines_1 + 1) % 3 != 0:
                     #s_shape_hs1_1 = AllplanReinf.BendingShape(steel_hs1)
                    # s_shape_hs1_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover)))
                    # steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_1))
                    # s_shape_hs1_2 = AllplanReinf.BendingShape(steel_hs1)
                     #s_shape_hs1_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover)))
                    # steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_2))
                #else:
                 s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
                 s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover)))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
                 s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
                 s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover)))
                 steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 
        else:
            lines_1 = int((self.Height - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
            if steel_modify(self.Height,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
                #if (lines_1 + 1) % 3 != 0:
                    #s_shape_hs1_1 = AllplanReinf.BendingShape(steel_hs1)
                   # s_shape_hs1_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.HoriFrontCover,self.Height-self.HoriTopCover)))
                   # steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_1))
                    #s_shape_hs1_2 = AllplanReinf.BendingShape(steel_hs1)
                    #s_shape_hs1_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(0,self.Width-self.HoriFrontCover,self.Height-self.HoriTopCover)))
                    #steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs1_2))
                #else:
                    s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
                    s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.HoriFrontCover,self.HoriFrontCover,self.Height-self.HoriTopCover)))
                    steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
                    s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
                    s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.HoriFrontCover,self.Width-self.HoriFrontCover,self.Height-self.HoriTopCover)))
                    steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 
        """
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
        
   
        #右上梁时，填补最后一根钢筋
        if  self.beamVisual:    
            lines_1 = int((self.Height -self.BHeight - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
            if steel_modify(self.Height -self.BHeight,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
                 if  ((self.Height - self.BHeight) <= (self.oWmobilePosition + self.WHeight +self.onBHeight)) and  ((self.oWmobilePosition + self.WHeight +self.onBHeight) < self.Height ):
                     pass               
                 elif ((self.Height - self.BHeight) <= (self.oWmobilePosition + self.WHeight))  and ((self.Height - self.BHeight) < self.Height ):
                     pass 
                 elif ((self.Height - self.BHeight) <= (self.oDmobilePosition + self.DHeight ))  and ((self.oDmobilePosition + self.DHeight ) < self.Height ):
                     pass
                 else:
                       s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
                       s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover-self.HoriSteelDia/2)))
                       steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
                       s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
                       s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.Width-self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover-self.HoriSteelDia/2)))
                       steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 
        else:
            lines_1 = int((self.Height - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
            if steel_modify(self.Height,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
                    if  ((self.oWmobilePosition + self.WHeight +self.onBHeight) >=  self.Height):
                        pass
                    elif  ((self.oWmobilePosition + self.WHeight) >= self.Height):
                        pass 
                    elif ((self.oDmobilePosition + self.DHeight ) >=  self.Height):
                        pass
                    else:
                         s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
                         s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover-self.HoriSteelDia/2)))
                         steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
                         s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
                         s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.Width-self.HoriFrontCover,self.Height-self.BHeight-self.HoriTopCover-self.HoriSteelDia/2)))
                         steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 

        #if steel_modify(H_flag,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
        if H >0:
            s_shape_hs2_1 = AllplanReinf.BendingShape(steel_hs2_1)
            s_shape_hs2_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.HoriFrontCover,H)))
            steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_1))
            s_shape_hs2_2 = AllplanReinf.BendingShape(steel_hs2_2)
            s_shape_hs2_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(start,self.Width-self.HoriFrontCover,H)))
            steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_hs2_2)) 
        return steel_list 
    
    def shape_tie_steel(self,length,width):

        bending_shape_type = AllplanReinf.BendingShapeType.OpenStirrup     #获取箍筋类型属性
        rebar_prop = {  'diameter':self.TieSteelDia,                       #钢铁的直径
                        'bending_roller':0,                                 #弯曲度
                        'steel_grade':self.TieSteelGrade,                   #钢铁的等级
                        'concrete_grade':self.ConcreteGrade,                #混泥土的等级
                        'bending_shape_type':bending_shape_type}            #形状类型属性
                        
        angle = RotationAngles(0,0,90)  #旋转角度

        #保护层混凝土属性
        concrete_props = ConcreteCoverProperties.all(self.HoriFrontCover - self.HoriSteelDia)

        #箍筋属性
        shape_props = ReinforcementShapeProperties.rebar(**rebar_prop)

        #
        args = {'length':length,       #长度
                'width':width,          #宽度
                'shape_props':shape_props,
                'concrete_cover_props':concrete_props,
                'model_angles':angle,    #模型角度
                'start_hook':self.TieSteelHook, #开始钩
                'end_hook':self.TieSteelHook,   #结束钩
                'start_hook_angle':-45, #开始钩的角度
                'end_hook_angle':0}   #结束钩的角度

        shape = GeneralShapeBuilder.create_open_stirrup(**args) #创建箍筋
        if shape.IsValid():
            return shape
       
    def create_tie_steel(self):
        steel_list = []
        #只有梁
        if self.beamVisual and not self.windowVisual  and not  self.RpillarsVisual   and not   self.LpillarsVisual   and not  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and not  self.unbeamVisual:
             steel_list += self.create_tie_steelt(2 * self.VertSteelDia,self.HoriBottomCover + self.HoriSteelDia,self.Length + 2 * self.VertSteelDia,self.VertSideCover + 2 * self.VertSteelDia,self.HoriSteelDia,self.Height-self.BHeight-self.HoriTopCover+ self.HoriSteelDia)
        #有樑，窗，上下窗樑,左柱,右柱时：
        elif self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
           #窗上梁：
           if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height-self.BHeight):
                    steel_list += self.create_tie_steelt(self.WmobilePosition +3.5 * self.VertSteelDia+self.VertSideCover,self.oWmobilePosition+self.WHeight+self.onBHeight+self.HoriBottomCover +8* self.HoriSteelDia,self.WmobilePosition+self.WLength, \
                                                 self.WmobilePosition + 3.5 * self.VertSteelDia+self.VertSideCover,self.oWmobilePosition+self.WHeight+self.onBHeight+6*self.HoriSteelDia, \
                                                 self.Height-self.BHeight-self.HoriTopCover+ self.HoriSteelDia,1)
           #窗下梁：
           steel_list += self.create_tie_steelt(self.WmobilePosition +3.5 * self.VertSteelDia+self.VertSideCover,self.HoriBottomCover + self.HoriSteelDia,self.WmobilePosition+self.WLength,self.WmobilePosition + 3.5 * self.VertSteelDia+self.VertSideCover,self.HoriSteelDia,self.oWmobilePosition -self.unBHeight+ self.HoriSteelDia,0)
        #没有樑，窗，上下窗樑,左柱,右柱时：
        elif not self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                              and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
            #窗上梁：
            if (self.oWmobilePosition + self.WHeight +self.onBHeight) < (self.Height):
                    steel_list += self.create_tie_steelt(self.WmobilePosition+ 3.5 * self.VertSteelDia+self.VertSideCover,self.oWmobilePosition+self.WHeight+self.onBHeight+8*self.HoriSteelDia,self.WmobilePosition+self.WLength-self.VertSideCover, \
                                                 self.WmobilePosition + 3.5 * self.VertSteelDia+self.VertSideCover,self.oWmobilePosition+self.WHeight+self.onBHeight+6*self.HoriSteelDia, \
                                                 self.Height-self.HoriTopCover+ self.HoriSteelDia,1)
            #窗下梁：
            steel_list += self.create_tie_steelt(self.WmobilePosition+ 3.5 * self.VertSteelDia+self.VertSideCover,self.HoriBottomCover + self.HoriSteelDia,self.WmobilePosition+self.WLength-self.VertSideCover,self.WmobilePosition + 3.5 * self.VertSteelDia+self.VertSideCover,self.HoriSteelDia,self.oWmobilePosition -self.unBHeight+ self.HoriSteelDia,0)
        else:
            steel_list += self.create_tie_steelt(2 * self.VertSteelDia,self.HoriBottomCover + self.HoriSteelDia,self.Length + 2 * self.VertSteelDia,self.VertSideCover + 2 * self.VertSteelDia,self.HoriSteelDia,self.Height + self.HoriSteelDia)
        return steel_list
    def create_tie_steelt(self,start_x,start_xz,end_x,start2_x,start2_z,end_z,flag=0):
        steel_list = []
        #tie_shape = self.shape_tie_steel(self.Width,4*self.TieSteelDia)
        
        shape = ReinforcementShapeProperties.rebar(self.TieSteelDia,0, self.TieSteelGrade, -1,AllplanReinf.BendingShapeType.Stirrup)
        concrete_cover = ConcreteCoverProperties.left_right(self.HoriFrontCover - self.HoriSteelDia/2,self.HoriFrontCover - self.HoriSteelDia/2)


        tie_length = int((self.Width -2*self.HoriFrontCover-self.TieSteelDia-self.Chuan_factor*self.TieSteelDia)+(self.before_angle*3.1415926*self.Chuan_factor*self.TieSteelDia/360)+(self.after_angle*3.1415926*self.Chuan_factor*self.TieSteelDia/360) +2*self.TieSteelHook)

        shape_builder = AllplanReinf.ReinforcementShapeBuilder()

        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover.left),
                             (AllplanGeo.Point2D(tie_length, 0), 0),
                             (concrete_cover.right)])

        shape_builder.SetHookStart(0,self.before_angle, AllplanReinf.HookType.eStirrup)  #第一个参数是弯曲后的长度第二个参数是钢筋弯曲的角度
        shape_builder.SetHookEnd(0,self.after_angle, AllplanReinf.HookType.eStirrup)
        tie_shape = shape_builder.CreateShape(shape) 
        angle = RotationAngles(0,0,90) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        tie_shape.Rotate(angle)   #旋转钢筋

        #distance = self.HoriBottomCover + self.HoriSteelDia
        if self.beamVisual:
                 Height2=self.Height-self.BHeight-- self.HoriTopCover
        else:
                Height2=self.Height
        #上窗梁1
        if flag==1:
       
                #没有樑，窗，上下窗樑,左柱,右柱时：
                if not self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                                      and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                           lines = int((end_z -self.oWmobilePosition-self.WHeight-self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
                elif  self.beamVisual and self.windowVisual  and  self.RpillarsVisual   and  self.LpillarsVisual   and  self.onbeamVisual   \
                                      and not self.DoorVisual    and not self.LDpillarsVisual  and not  self.RDpillarsVisual and  self.unbeamVisual:
                           lines = int((end_z -self.oWmobilePosition-self.WHeight-self.onBHeight - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
                #else:   
                    #水平放的钢筋数减1      #高        水平顶部保护层     水平底部保护层              水平钢筋直径        水平间距
                      #lines = int((end_z - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
        #下窗梁0
        else:
             lines = int((end_z - self.HoriTopCover - self.HoriBottomCover - self.HoriSteelDia) / self.HoriDistance)
    #垂直放的钢筋数减1      #长度       垂直左或右保护层         垂直钢筋直径              垂直间距
        rows = int((end_x - 2 * self.VertSideCover - self.VertSteelDia) / self.VertDistance)
        if self.TieMode == 1:
            for x in range(lines+1):

                #point_f = AllplanGeo.Point3D(2 * self.VertSteelDia,0,distance)   #三维点对象
                #point_t = AllplanGeo.Point3D(self.Length + 2 * self.VertSteelDia,0,distance)
                point_f = AllplanGeo.Point3D(start_x,0,start_xz)   #三维点对象
                point_t = AllplanGeo.Point3D(end_x,0,start_xz)
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
            if not  self.RpillarsVisual and not self.RDpillarsVisual:
                    if steel_modify(Height2,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover) and (lines + 1) % 3 == 0:
                        point_f = AllplanGeo.Point3D(2 * self.VertSteelDia,0,self.Height - self.HoriTopCover + self.HoriSteelDia)
                        point_t = AllplanGeo.Point3D(self.Length + 2 * self.VertSteelDia,0,Height2 - self.HoriTopCover + self.HoriSteelDia)     
                        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                    tie_shape,
                                                                                                    point_f,
                                                                                                    point_t,
                                                                                                    self.VertSideCover,
                                                                                                    self.VertSideCover,
                                                                                                    3*self.VertDistance,
                                                                                                    3))       



         
                    #last line    
                    if steel_modify(self.Length,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover) and (rows + 1) % 3 == 0:
                        l_distance = self.HoriBottomCover + self.HoriSteelDia
                        for y in range(lines + 1):
                            if y % 3 == 0:
                                point_f_e = AllplanGeo.Point3D(0,0,0)
                                point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                                vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))
                                s_shape = AllplanReinf.BendingShape(tie_shape)
                                s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover - self.VertSteelDia + 2 * self.VertSteelDia,0,l_distance)))
                                steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))
                            l_distance += self.HoriDistance
                        #last line & row
                        if steel_modify(Height2,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover) and (lines + 1) % 3 == 0:
                            point_f_e = AllplanGeo.Point3D(0,0,0)
                            point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                            vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))
                            s_shape = AllplanReinf.BendingShape(tie_shape)
                            s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover - self.VertSteelDia + 2 * self.VertSteelDia,0,Height2 - self.HoriTopCover + self.HoriSteelDia)))
                            steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))   
                         
        elif self.TieMode == 2:
           
            for x in range(rows + 1): 
                if self.RpillarsVisual and self.windowVisual:
                    if start2_x > (self.WmobilePosition+self.WLength):
                        break

                if x % 4 == 0:
                    #point_f = AllplanGeo.Point3D(distance,0,self.HoriSteelDia)
                    #point_t = AllplanGeo.Point3D(distance,0,self.Height + self.HoriSteelDia)
                    point_f = AllplanGeo.Point3D(start2_x,0,start2_z)
                    point_t = AllplanGeo.Point3D(start2_x,0,end_z)
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
                    point_f = AllplanGeo.Point3D(start2_x,0,start2_z+2*self.HoriDistance)
                    point_t = AllplanGeo.Point3D(start2_x,0,end_z)
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

            if not  self.RpillarsVisual:
                        if steel_modify(self.Length,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover):
                            if (rows + 1) % 4 == 0:
                                point_f = AllplanGeo.Point3D(self.Length - self.VertSideCover,0,self.HoriSteelDia)
                                point_t = AllplanGeo.Point3D(self.Length - self.VertSideCover,0,Height2 + self.HoriSteelDia)
                                steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                            tie_shape,
                                                                                                            point_f,
                                                                                                            point_t,
                                                                                                            self.HoriBottomCover,
                                                                                                            self.HoriTopCover,
                                                                                                            4*self.HoriDistance,
                                                                                                            3))
                            if (rows + 3) % 4 == 0:
                                point_f = AllplanGeo.Point3D(self.Length - self.VertSideCover,0,self.HoriSteelDia + 2*self.HoriDistance)
                                point_t = AllplanGeo.Point3D(self.Length - self.VertSideCover,0,Height2 + self.HoriSteelDia)
                                steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,
                                                                                                            tie_shape,
                                                                                                            point_f,
                                                                                                            point_t,
                                                                                                            self.HoriBottomCover,
                                                                                                            self.HoriTopCover,
                                                                                                            4*self.HoriDistance,
                                                                                                            3))
                        #last row
                        if steel_modify(Height2,self.HoriSteelDia,self.HoriDistance,self.HoriBottomCover,self.HoriTopCover):
                            if(lines + 1) % 4 == 0:
                                r_distance = self.VertSideCover + 2 * self.VertSteelDia

                                for z1 in range(rows + 1):
                                    if z1 % 4 == 0:
                                        point_f_e = AllplanGeo.Point3D(0,0,0)
                                        point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                                        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance / 2,0,0))
                                        s_shape = AllplanReinf.BendingShape(tie_shape)
                                        s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(r_distance,0,Height2 - self.HoriTopCover + self.HoriSteelDia)))
                                        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))   
                                    r_distance += self.VertDistance             
                                    #last row & line
                                    if steel_modify(self.Length,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover) and (rows + 1) % 4 == 0:                    
                                        point_f_e = AllplanGeo.Point3D(0,0,0)
                                        point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                                        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance / 2,0,0))
                                        s_shape = AllplanReinf.BendingShape(tie_shape)
                                        s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover - self.VertSteelDia + 2 * self.VertSteelDia,0,self.Height - self.HoriTopCover + self.HoriSteelDia)))
                                        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))

                            #last row
                            if (lines + 3) % 4 == 0:
                                r_distance = self.VertSideCover + 2 * self.VertSteelDia
                    
                                for z2 in range(rows + 1):
                                    if (z2 + 2) % 4 == 0:
                                        point_f_e = AllplanGeo.Point3D(0,0,0)
                                        point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                                        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance / 2,0,0))
                                        s_shape = AllplanReinf.BendingShape(tie_shape)
                                        s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(r_distance,0,Height2 - self.HoriTopCover + self.HoriSteelDia)))
                                        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))  
                                    r_distance += self.VertDistance 
                                    #last row & line
                                    if steel_modify(self.Length,self.VertSteelDia,self.VertDistance,self.VertSideCover,self.VertSideCover) and (rows + 3) % 4 == 0:
                                        point_f_e = AllplanGeo.Point3D(0,0,0)
                                        point_t_e = AllplanGeo.Point3D(self.Length ,0,0)
                                        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.HoriDistance / 2,0,0))
                                        s_shape = AllplanReinf.BendingShape(tie_shape)
                                        s_shape.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.Length - self.VertSideCover - self.VertSteelDia + 2 * self.VertSteelDia,0,self.Height - self.HoriTopCover + self.HoriSteelDia)))
                                        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f_e,point_t_e,s_shape))



                    



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
        #左上角
        angle = RotationAngles(0,45,0) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        steel_shape.Rotate(angle)   #旋转钢筋

        point_f = AllplanGeo.Point3D(0,0,0)
        point_t = AllplanGeo.Point3D(self.Length ,0,0)
        vec = AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Point3D(self.VertDistance / 2,0,0))

        s_shape_1 = AllplanReinf.BendingShape(steel_shape)
        s_shape_1.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition+self.WHeight+math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_1))
        
        s_shape_2 = AllplanReinf.BendingShape(steel_shape)
        s_shape_2.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition+self.WHeight+math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_2))

        s_shape_12 = AllplanReinf.BendingShape(steel_shape)
        s_shape_12.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition+self.WHeight+math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_12))
        
        s_shape_22 = AllplanReinf.BendingShape(steel_shape)
        s_shape_22.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition+self.WHeight+math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_22))

          #右下角
        s_shape_3 = AllplanReinf.BendingShape(steel_shape)
        s_shape_3.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition-math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_3))

        s_shape_4 = AllplanReinf.BendingShape(steel_shape)
        s_shape_4.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition-math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_4))

        s_shape_32 = AllplanReinf.BendingShape(steel_shape)
        s_shape_32.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((2*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2,self.oWmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_32))

        s_shape_42 = AllplanReinf.BendingShape(steel_shape)
        s_shape_42.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((2*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),self.oWmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_42))

        #还原角度
        angle = RotationAngles(0,0,0) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        steel_shape.Rotate(angle)   #旋转钢筋
        
        #右上角
        angle = RotationAngles(0,90,0) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        steel_shape.Rotate(angle)   #旋转钢筋

        s_shape_5 = AllplanReinf.BendingShape(steel_shape)
        s_shape_5.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                              self.oWmobilePosition+self.WHeight+math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_5))

        s_shape_6 = AllplanReinf.BendingShape(steel_shape)
        s_shape_6.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),  \
                                                              self.oWmobilePosition+self.WHeight+math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_6))

        s_shape_52 = AllplanReinf.BendingShape(steel_shape)
        s_shape_52.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((2*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                              self.oWmobilePosition+self.WHeight+math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_52))

        s_shape_62 = AllplanReinf.BendingShape(steel_shape)
        s_shape_62.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition+self.WLength+math.sqrt(((2*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2),  \
                                                              self.oWmobilePosition+self.WHeight+math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_62))
        #左下角
        s_shape_7 = AllplanReinf.BendingShape(steel_shape)
        s_shape_7.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                              self.oWmobilePosition-math.sqrt(((self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_7))

        s_shape_8 = AllplanReinf.BendingShape(steel_shape)
        s_shape_8.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2), \
                                                              self.oWmobilePosition-math.sqrt(((self.mobile_Length)**2)/2)))) 
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_8))

        s_shape_72 = AllplanReinf.BendingShape(steel_shape)
        s_shape_72.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2),self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2, \
                                                              self.oWmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2))))
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_72))

        s_shape_82 = AllplanReinf.BendingShape(steel_shape)
        s_shape_82.Move(AllplanGeo.Vector3D(AllplanGeo.Point3D(self.WmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2),self.Width-(self.HoriFrontCover+self.VertSteelDia+self.HoriSteelDia+self.TieSteelDia/2), \
                                                              self.oWmobilePosition-math.sqrt(((2*self.mobile_Length)**2)/2)))) 
        steel_list.append(AllplanReinf.BarPlacement(0,1,vec,point_f,point_t,s_shape_82))
        
        return steel_list

    def add(self):
        steel_list = []
    
        shape = ReinforcementShapeProperties.rebar(10,0, 2, -1,AllplanReinf.BendingShapeType.Stirrup)
        concrete_cover = ConcreteCoverProperties.left_right(10,30)


        shape_builder = AllplanReinf.ReinforcementShapeBuilder()

        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover.left),
                             (AllplanGeo.Point2D(500, 0), 0),
                             (concrete_cover.right)])

        shape_builder.SetHookStart(500, -90, AllplanReinf.HookType.eStirrup)  #第一个参数是弯曲后的长度第二个参数是钢筋弯曲的角度
        shape_builder.SetHookEnd(0, -135, AllplanReinf.HookType.eStirrup)
        tie_shape = shape_builder.CreateShape(shape) 
        angle = RotationAngles(0,0,90) #建立角度旋转偏移的变量   参数： #向高轴偏移的角度,向y轴偏移的角度,向X轴偏移的角度
        tie_shape.Rotate(angle)   #旋转钢筋

        
        point_f = AllplanGeo.Point3D(1000,0,0)
        point_t = AllplanGeo.Point3D(1000,0,500)
        steel_list.append(LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(0,  #位置
                                                                                                tie_shape,  #形状
                                                                                                point_f,  #起点位置
                                                                                                point_t,    #放置点位置
                                                                                                50,  #混凝土保护层在左边的位置
                                                                                                50,  #混凝土保护层在右边的位置
                                                                                                150,  #间距
                                                                                                3))    #适用于距离/起止阀盖的调整
                                                                                                
        return steel_list 


    def create_s_hook(length, model_angles,
                  shape_props,
                  concrete_cover_props, hook_length=0):
        """
        Create a S hook

        Return: Bar shape of the S hook shape in world coordinates

        Parameter:  length                      Length of the geometry side
                model_angles                Angles for the local to global shape transformation
                shape_props                 Shape properties
                concrete_cover_props        Concrete cover properties: needed top and bottom
                hook_length                 0 = calculate / >0 = value
        """

        shape_builder = AllplanReinf.ReinforcementShapeBuilder()

        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),
                             (AllplanGeo.Point2D(length, 0), 0),
                             (concrete_cover_props.right)])

        shape_builder.SetHookStart(hook_length, -90, AllplanReinf.HookType.eStirrup)
        shape_builder.SetHookEnd(hook_length, -90, AllplanReinf.HookType.eStirrup)

        shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model

        if shape.IsValid() is True:
             shape.Rotate(model_angles)

        return shape


    def create_hook_stirrup(length, model_angles,
                        shape_props,
                        concrete_cover_props, hook_length=0):
        """
        Create a hook stirrup

        Return: Bar shape of the S hook shape in world coordinates

        Parameter:  length                      Length of the geometry side
                model_angles                Angles for the local to global shape transformation
                shape_props                 Shape properties
                concrete_cover_props        Concrete cover properties: needed top and bottom
                hook_length                 0 = calculate / >0 = value
        """

        shape_builder = AllplanReinf.ReinforcementShapeBuilder()

        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),
                             (AllplanGeo.Point2D(length, 0), 0),
                             (concrete_cover_props. right)])

        shape_builder.SetHookStart(hook_length, 180, AllplanReinf.HookType.eStirrup)
        shape_builder.SetHookEnd(hook_length, 180, AllplanReinf.HookType.eStirrup)

        shape = shape_builder.CreateShape(shape_props)


        #----------------- Rotate the shape to the model

        if shape.IsValid() is True:
            shape.Rotate(model_angles)

        return shape