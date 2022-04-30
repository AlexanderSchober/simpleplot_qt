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
from ..graph_views_3D.pointer_view_2d  import PointerView2D
from ...models.parameter_class      import ParameterHandler 

class PointerItem2D(GraphicsItem): 
    def __init__(self, parent, canvas, axis_items):
        super().__init__('Grids', transformer=False, parent=parent)
        self.canvas = canvas
        self._axis_items = axis_items
        self._handler = ParameterHandler(name = 'Pointer', parent = self)
        self._pointer_view = None

    def initialize(self):
        '''
        '''
        self._pointer_view = PointerView2D()
        self.canvas.view.addGraphItem(self._pointer_view)

        self._handler.addParameter(
            'Active',  True,
            method = partial(self.setParameters, 0))

        self._handler.addParameter(
            'Thickness', 1.,
            method = partial(self.setParameters, 0))

        self._handler.addParameter(
            'Color', QtGui.QColor(0, 0, 0, 255),
            method = partial(self.setParameters, 0))

        self.setParameters()
        self.bindPointer()

    def setParameters(self)->None:
        '''
        '''
        parameters = {}
        parameters['draw_pointer']        = self._handler['Active']
        parameters['pointer_thickness']   = self._handler['Thickness']
        parameters['pointer_color']       = np.array(self._handler['Color'].getRgbF())

        self._pointer_view.setProperties(**parameters)

    def refreshAuto(self):
        '''
        '''
        self.setParameters()
        
    def bindPointer(self):
        '''
        Binds the cursor to the system signals of th
        mouse 
        '''
        self.canvas.mouse.bind('move', self._pointer_view.setPosition, 'pointer_move')

    def unbindPointer(self):
        '''
        Binds the cursor to the system signals of the
        mouse 
        '''
        self.canvas.mouse.unbind('move', 'pointer_move')
