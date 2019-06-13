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

import numpy as np

from .plot_items.scatter_plot       import ScatterPlot
from .plot_items.surface_plot_handler       import SurfacePlotHandler
from .plot_items.bar_plot           import BarPlot
from .plot_items.volume_plot        import VolumePlot
from .plot_items.vector_field_plot  import VectorFieldPlot
from ..model.node                   import SessionNode

def get_plot_handler(select):
    '''
    Will return the right fit manager depending 
    on the initial input
    '''
    if select == 'Scatter':
        return Plot_Handler(select, ScatterPlot)
    elif select == 'Surface':
        return Plot_Handler(select, SurfacePlotHandler)
    elif select == 'Bar':
        return Plot_Handler(select, BarPlot)
    elif select == 'Volume':
        return Plot_Handler(select, VolumePlot)
    elif select == 'Vector field':
        return Plot_Handler(select, VectorFieldPlot)
    else:
        print('Could not find the fit class you are looking for. Error...')        
        return None

class Plot_Handler(SessionNode):
    '''
    This class will be the manager of all the 
    scatter plots. 
    '''
    def __init__(self, name, target_class):
        SessionNode.__init__(self,name)
        self.identifier     = 0
        self.target_class   = target_class
        self.name           = name
        self.type           = 'None'
        
    def addChild(self,*args, **kwargs):
        '''
        This will effectively add an element to the 
        plot_elements array. 
        '''
        self._children.append(self.target_class(*args,**kwargs))
        self._children[-1]._parent = self

        return self._children[-1]

    def removeItem(self, name = '', idx = None, target = None):
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
        Draw all the items onto the plot
        '''
        hits = []
        for plot_element in self._children:
            hits.append(plot_element.processRay(ray))

        return hits
