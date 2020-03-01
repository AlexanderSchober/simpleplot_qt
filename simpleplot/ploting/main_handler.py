#  -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the NSE analysis contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************
from PyQt5 import QtGui, QtCore
import numpy as np

from .scatter_plot_handler          import ScatterPlotHandler
from .surface_plot_handler          import SurfacePlotHandler 
from .step_plot_handler             import StepPlotHandler
from .bar_plot_handler              import BarPlotHandler
from .volume_plot_handler           import VolumePlotHandler
from .distribution_plot_handler     import DistributionPlotHandler
from .plot_items.vector_field_plot  import VectorFieldPlot
from .crystal_plot_handler          import CrystalPlotHandler

from .graph_items.circle_item       import CircleItem
from .graph_items.ellipse_item      import EllipseItem
from .graph_items.rectangle_item    import RectangleItem
from .graph_items.square_item       import SquareItem
from .graph_items.pie_item          import PieItem

from ..models.session_node          import SessionNode

def get_main_handler(select):
    '''
    Will return the right fit manager depending 
    on the initial input
    '''
    if select == 'Scatter':
        return MainHandler(select, ScatterPlotHandler)
    elif select == 'Surface':
        return MainHandler(select, SurfacePlotHandler)
    elif select == 'Step':
        return MainHandler(select, StepPlotHandler)
    elif select == 'Bar':
        return MainHandler(select, BarPlotHandler)
    elif select == 'Volume':
        return MainHandler(select, VolumePlotHandler)
    elif select == 'Distribution':
        return MainHandler(select, DistributionPlotHandler)
    elif select == 'Vector field':
        return MainHandler(select, VectorFieldPlot)
    elif select == 'Crystal':
        return MainHandler(select, CrystalPlotHandler)
    elif select == 'Items':
        return MainHandler(select)
    else:
        print('Could not find the fit class you are looking for. Error...')        
        return None

class MainHandler(SessionNode):
    '''
    This class will be the manager of all the 
    scatter plots. 
    '''

    def __init__(self, name, target_class = None):
        SessionNode.__init__(self,name)
        self.identifier     = 0
        self.target_class   = target_class
        self.name           = name
        self.type           = 'None'

        self._item_dict = {
            'Circle':CircleItem,
            'Ellipse':EllipseItem,
            'Square':SquareItem,
            'Rectangle':RectangleItem,
            'Pie':PieItem
        }
        
    def addChild(self,*args, **kwargs):
        '''
        This will effectively add an element to the 
        plot_elements array. 
        '''
        if self.target_class == None:
            new_child = self._item_dict[args[0]](*args,**kwargs)
        else:
            new_child = self.target_class(*args,**kwargs)

        self._model.insertRows(len(self._children), 1, [new_child], self)
        return self._children[-1]

    def removeItem(self):
        '''
        here we will ask the element in question to 
        remove one of its items and proceed to a clean
        removal. 
        '''
        # if idx == None and name == '':
        #     print("You can't remove nothing ...")

        # elif not name == '':
        #     names = [element.get_para('Name') for element in self.plot_elements]
        #     self.plot_elements[names.index(name)].remove_items(target)
        #     del self.plot_elements[names.index(name)]

        # elif not idx == None:
        #     self.plot_elements[idx].remove_items(target)
        #     del self.plot_elements[idx]

    def removeItems(self):
        '''
        here we will ask the element in question to 
        remove one of its items and proceed to a clean
        removal. 
        '''
        for plot_element in self._children:
            plot_element.removeItems()
        
    def clear(self, target):
        '''
        Draw all the items onto the plot
        '''
        for plot_element in self._children:
            plot_element.removeItems()
        
        self._model.removeRows(0,len(self._children), self)

    def draw(self, target):
        '''
        Draw all the items onto the plot
        '''
        for plot_element in self._children:
            if target.handler['Type'] == "2D":
                plot_element.draw(target)
            elif target.handler['Type'] == "3D":
                plot_element.drawGL(target)

    def processRay(self, ray):
        '''
        process the ray tracing and then give
        the result back as a hits
        '''
        for plot_element in self._children:
            if hasattr(plot_element, '_ray_handler'):
                plot_element._ray_handler.processRay(ray)

        hits = []
        for plot_element in self._children:
            if hasattr(plot_element, '_ray_handler'):
                if not plot_element._ray_handler.point is None:
                    hits.append([plot_element._ray_handler.point, plot_element._ray_handler])
        return hits

    def processProjection(self, x = 0, y = 0, z = 0):
        '''
        process the ray tracing and then give
        the result back as a hits
        '''
        for plot_element in self._children:
            if hasattr(plot_element, "processProjection"):
                plot_element.processProjection(x,y,z)
