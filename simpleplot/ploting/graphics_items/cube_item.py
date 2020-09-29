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
#   Alexander Schober <alex.schober@mac.com>
#
# *****************************************************************************

# General imports
from PyQt5 import QtGui

# Personal imports
from .parallepiped_item     import ParallepipedItem

class CubeItem(ParallepipedItem):
    '''
    This is a derivative of the GrahicsItem class
    that will handle the drawing of a Cube either
    on a 2D or 3D OpenGl canvas
    '''
    def __init__(self,*args, **kwargs):
        '''
        Initialisation of the class and super class

        Parameters:
        -------------------
        *args : -
            These are the arguments of the class
        **kwargs : -
            These are the keyword arguments of the class
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, **kwargs)->None:
        '''
        This initializes the ParameterClass specifictions
        in the inherited item
        
        Parameters:
        -------------------
        **kwargs : -
            These are the keyword arguments if needed
        '''
        self.addParameter(
            'Dimension', 1.,
            tags   = ['2D', '3D'],
            method = self.refresh)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return

        parameters = {}

        parameters['position'] = [0,0,0]
        parameters['dimensions'] = [self['Dimension'],self['Dimension'],self['Dimension']]

        if self._mode == '2D':
            parameters['angle']     = self['Angle']
            parameters['pen']       = super().getPen()
            parameters['brush']     = super().getBrush()
            parameters['Z']         = self['Z']
            parameters['movable']   = self['Movable']
        elif self._mode == '3D':
            parameters['drawFaces']     = self['Draw faces']
            parameters['drawEdges']     = self['Draw edges']
            parameters['brush_color']   = self['Fill'][1] if self['Fill'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_color']     = self['Line'][2] if self['Line'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_thickness'] = self['Line'][1] if self['Line'][0] else 0

        self.draw_items[0].setData(**dict(parameters))
        self.setColor()
