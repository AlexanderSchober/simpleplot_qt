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
from ..graph_views_3D.grid_view_2d  import GridView2D
from ...models.parameter_class      import ParameterHandler 

class GridItem2D(GraphicsItem): 
    def __init__(self, parent, canvas, axis_items):
        super().__init__('Grids', transformer=False, parent=parent)
        self.canvas = canvas
        self._axis_items = axis_items

        self._orientations = ['horizontal', 'vertical']
        self._handlers   = [
            ParameterHandler(
                name = 'Horitontal Grid (Main)', parent = self),
            ParameterHandler(
                name = 'Horitontal Grid (Secondary)', parent = self),
            ParameterHandler(
                name = 'Vertical Grid (Main)', parent = self),
            ParameterHandler(
                name = 'Vertical Grid (Secondary)', parent = self)]
        
        self._grid_views = []

    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''

        for i, orientation in enumerate(self._orientations):
            self._grid_views.append(GridView2D(self._axis_items))
            self.canvas.view.addGraphItem(self._grid_views[-1])
            self._grid_views[-1].setProperties(grid_orientation=orientation)

            self._handlers[2*i].addParameter(
                'Active',  True,
                method = partial(self.setParameters, i))

            self._handlers[2*i].addParameter(
                'Thickness', 1.,
                method = partial(self.setParameters, i))

            self._handlers[2*i].addParameter(
                'Color', QtGui.QColor(0, 0, 0, 255),
                method = partial(self.setParameters, i))

            self._handlers[2*i].addParameter(
                'Periodicity', '6, 2, 2, 2',
                method = partial(self.setParameters, i))

            self._handlers[2*i+1].addParameter(
                'Active',  True,
                method = partial(self.setParameters, i))       

            self._handlers[2*i+1].addParameter(
                'Thickness', 0.5,
                method = partial(self.setParameters, i))

            self._handlers[2*i+1].addParameter(
                'Color', QtGui.QColor(0, 0, 0, 255),
                method = partial(self.setParameters, i))

            self._handlers[2*i+1].addParameter(
                'Periodicity', '6, 2, 2, 2',
                method = partial(self.setParameters, i))

            self._handlers[2*i+1].addParameter(
                'Multiplicity', 4,
                method = partial(self.setParameters, i))

        for i in range(len(self._orientations)):
            self.setParameters(i)

    def setParameters(self, i:int)->None:
        '''
        Set the parameters of the axis items
        '''

        main_handler = self._handlers[2*i]
        small_handler = self._handlers[2*i+1]

        parameters = {}
        parameters['draw_grid']         = main_handler['Active']
        parameters['draw_small_grid']   = small_handler['Active']

        parameters['grid_color']        = np.array(main_handler['Color'].getRgbF())
        parameters['grid_thickness']    = np.array([main_handler['Thickness']])
        parameters['grid_periodicity']  = np.array([int(val) for val in main_handler['Periodicity'].split(',')])

        parameters['small_grid_color']        = np.array(small_handler['Color'].getRgbF())
        parameters['small_grid_thickness']    = np.array([small_handler['Thickness']])
        parameters['small_grid_periodicity']  = np.array([int(val) for val in small_handler['Periodicity'].split(',')])
        parameters['small_grid_multiplicity'] = int(small_handler['Multiplicity'])

        self._grid_views[i].setProperties(**parameters)

    def refreshAuto(self):
        '''
        refresh the axes automatically 
        based on the content
        '''
        for i in range(len(self._grid_views)):
            self.setParameters(i)
