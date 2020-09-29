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

# external dependincies
from PyQt5 import QtGui
import numpy as np
from functools import partial

#import dependencies
from ..graphics_items.graphics_item import GraphicsItem
from ..graph_views_3D.axis_view_3D  import AxisView3D
from ...models.parameter_class      import ParameterHandler 

class AxesItem3D(GraphicsItem): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    def __init__(self, canvas):
        super().__init__('Axes',transformer = False, parent = canvas)
        self.canvas = canvas

        self.x_direction= ParameterHandler(
            name = 'X direction', parent = self)
        self.y_direction   = ParameterHandler(
            name = 'Y direction', parent = self)
        self.z_direction  = ParameterHandler(
            name = 'Z direction', parent = self)

        self.initialize()
            
    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self._axes_list  = []
        self._directions = [[1,0,0],[0,1,0],[0,0,1]]
        self._tick_directions = [[0,-1,0],[-1,0,0],[-1,-1,0]]
        self._colors     = ['blue','red','green']
        self._handlers   = [self.x_direction, self.y_direction, self.z_direction]

        for i in range(len(self._directions)):
            self._axes_list.append(AxisView3D())
            self.canvas.view.addGraphItem(self._axes_list[-1])
            self._axes_list[-1].setProperties(
                axis_direction = np.array(self._directions[i]))

            self._handlers[i].addParameter(
                'Visible',  [True, True, False, False], 
                names = ['Axis', 'Ticks', 'Values', 'Title'],
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis range',  
                [True, 0, 5],
                names = ['Auto range', 'Length min', 'Length max'],
                method = partial(self.refreshAutoAxis, i))

            self._handlers[i].addParameter(
                'Axis position', [0.,0.,0.],
                names  = ['x', 'y', 'z'],
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis visual',  
                [QtGui.QColor(self._colors[i]), 0.05, 0.1, 0.2],
                names = ['Color', 'Width', 'Arrow width', 'Arrow length'],
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Tick visual',  
                [QtGui.QColor(self._colors[i]), 0.05, 0.1],
                names = ['Color', 'Width', 'Length'],
                method = partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Tick direction', self._tick_directions[i],
                names = ['x', 'y', 'z'],
                method = partial(self.setParameters, i))

            self._handlers[i].runAll()

    def setParameters(self, i:int)->None:
        '''
        Set the parameters of the axis items
        '''
        handler = self._handlers[i]

        parameters = {}
        parameters['draw_axis']        = handler['Visible'][0]
        parameters['draw_ticks']       = handler['Visible'][1]
        parameters['draw_values']      = handler['Visible'][2]
        parameters['draw_title']       = handler['Visible'][3]

        parameters['axis_length']      = np.array(handler['Axis range'][1:])
        parameters['axis_width']       = np.array([handler['Axis visual'][1]])
        parameters['axis_color']       = np.array(handler['Axis visual'][0].getRgbF())
        parameters['axis_center']      = np.array(handler['Axis position'])
        parameters['axis_arrow_width'] = np.array([handler['Axis visual'][2]])
        parameters['axis_arrow_length']= np.array([handler['Axis visual'][3]])

        parameters['tick_length']      = np.array(handler['Tick visual'][2])
        parameters['tick_width']       = np.array(handler['Tick visual'][1])
        parameters['tick_color']       = np.array(handler['Tick visual'][0].getRgbF())
        parameters['tick_direction']   = np.array(handler['Tick direction'])

        self._axes_list[i].setProperties(**parameters)

    def refreshAuto(self):
        '''
        refresh the axes automatically 
        based on the content
        '''
        for i in range(len(self._axes_list)):
            self.refreshAutoAxis(i)

    def refreshAutoAxis(self, i:int):
        '''
        refresh the axes automatically 
        based on the content
        '''
        if self._handlers[i]['Axis range'][0]:

            bounds = [[1.e2, -1.e2], [1.e2, -1.e2], [1.e2, -1.e2]]
            for child in self.canvas._plot_root._children:
                for plot_child in child._children:
                    if hasattr(plot_child, '_plot_data'):
                        new_bounds = plot_child._plot_data.getDrawBounds()
                        bounds = [
                            [
                                min(bounds[0][0], new_bounds[0][0]), 
                                max(bounds[0][1], new_bounds[0][1])],
                            [
                                min(bounds[1][0], new_bounds[1][0]), 
                                max(bounds[1][1], new_bounds[1][1])],
                            [
                                min(bounds[2][0], new_bounds[2][0]), 
                                max(bounds[2][1], new_bounds[2][1])]]
                        

            self._handlers[i].items['Axis position'].updateValue([
                float(bounds[0][0]),
                float(bounds[1][0]), 
                float(bounds[2][0])], 
                method = False)
            self._handlers[i].items['Axis range'].updateValue(
                [True, 0, float(bounds[i][1] - bounds[i][0])], 
                method = False)

        self.setParameters(i)

        if not self.parent() is None:
            self.parent().childFromName('Grids').refreshAuto()
        