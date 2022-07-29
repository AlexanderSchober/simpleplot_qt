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
from ..graph_views_3D.axis_orientation_view_3D  import AxisOrientationView3D
from ...models.parameter_class                  import ParameterHandler 

class AxesOrientationItem3D(ParameterHandler): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    def __init__(self, canvas):
        super().__init__('Orientation Axes', parent = canvas)
        self.canvas = canvas
        self.initialize()
            
    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self._axes_list         = []
        self._directions        = [[1,0,0],[0,1,0],[0,0,1]]
        self._colors            = ['blue','red','green']
        self._corner_choices    = ['Top Left', 'Bottom Left', 'Top Right', 'Bottom Right']
        self.drag_on            = False

        for i in range(len(self._directions)):
            self._axes_list.append(AxisOrientationView3D())
            self.canvas.view.addGraphItem(self._axes_list[-1])
            self._axes_list[-1].setProperties(
                axis_direction = np.array(self._directions[i]))

        self.addParameter(
            'Visible',  'On change', 
            choices   = ['Always', 'On change', 'Never'],
            method  = partial(self.setParameters))

        self.addParameter(
            'Position corner',  'Bottom Left',
            choices = self._corner_choices, 
            method  = partial(self.setParameters))

        self.addParameter(
            'Relative Position', [100,100],
            names   = ['x (px)', 'y(px)'], 
            method  = partial(self.setParameters))
            
        self.addParameter(
            'Scale factor',  10., 
            method  = partial(self.setParameters))

        self.addParameter(
            'Axis visual',  
            [
                QtGui.QColor(self._colors[0]), 
                QtGui.QColor(self._colors[1]), 
                QtGui.QColor(self._colors[2]), 
                0.05, 0.1, 0.2
            ],
            names = [
                'Color x', 'Color y', 'Color z', 
                'Width', 'Arrow width', 'Arrow length'
            ],
            method = partial(self.setParameters))

        self.runAll()

    def setParameters(self)->None:
        '''
        Set the parameters of the axis items
        '''
        for i in range(len(self._directions)):
            parameters = {}

            if self['Visible'] == 'Always':
                parameters['draw_axis']         = True
            elif self['Visible'] == 'On change' and self.drag_on:
                parameters['draw_axis']         = True
            else:
                parameters['draw_axis']         = False

            parameters['axis_length']           = np.array([0,1])
            parameters['axis_width']            = np.array([self['Axis visual'][-3]])
            parameters['axis_color']            = np.array(self['Axis visual'][i].getRgbF())
            parameters['axis_arrow_width']      = np.array([self['Axis visual'][-2]])
            parameters['axis_arrow_length']     = np.array([self['Axis visual'][-1]])
            parameters['axis_scale_factor']     = np.array([self['Scale factor']])
            parameters['axis_offset_corner']    = self._corner_choices.index(self['Position corner'])
            parameters['axis_offset_value']     = np.array(self['Relative Position'])

            self._axes_list[i].setProperties(**parameters)
