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

#import dependencies
from PyQt5 import QtGui
from functools import partial
import numpy as np

#import personal dependencies
from ..graphics_items.graphics_item import GraphicsItem
from ..graph_views_3D.grid_view_3d  import GridView3D
from ...models.parameter_class      import ParameterHandler 

class GridItem3D(GraphicsItem): 
    def __init__(self,axis_items, canvas):
        super().__init__('Grids', parent = canvas)
        self.canvas = canvas
        self._axis_items = axis_items

        self.xy_handler = ParameterHandler(
            name = 'xy Grid', parent = self)
        self.xz_handler = ParameterHandler(
            name = 'xz Grid', parent = self)
        self.yz_handler = ParameterHandler(
            name = 'yz Grid', parent = self)

        self.initialize()

    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self._handlers   = [
            self.xy_handler, 
            self.xz_handler, 
            self.yz_handler]
        
        self._planes = ['xy', 'yz', 'xz']

        self.grid_items = [
            GridView3D(self._axis_items), 
            GridView3D(self._axis_items), 
            GridView3D(self._axis_items)]

        for i in range(len(self._handlers)):
            self.canvas.view.addGraphItem(self.grid_items[i])

            self._handlers[i].addParameter(
                'Active',  True,
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Plane',  self._planes[i],
                choices = self._planes,
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Color', QtGui.QColor(0, 0, 0, 255),
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Thickness', 0.01,
                method = partial(self.setParameters, i))

            self._handlers[i].runAll()

    def setParameters(self, i:int)->None:
        '''
        Set the parameters of the axis items
        '''
        handler = self._handlers[i]

        parameters = {}
        parameters['draw_grid']         = handler['Active']
        parameters['grid_mode']         = self._planes.index(handler['Plane'])
        parameters['grid_color']        = np.array(handler['Color'].getRgbF())
        parameters['grid_thickness']    = np.array([handler['Thickness']])

        self.grid_items[i].setProperties(**parameters)

    def refreshAuto(self):
        '''
        refresh the axes automatically 
        based on the content
        '''
        for i in range(len(self.grid_items)):
            self.setParameters(i)
