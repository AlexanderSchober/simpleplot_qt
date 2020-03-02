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

from PyQt5 import QtWidgets, QtGui, QtCore

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl

from ...models.parameter_class import ParameterHandler

class GraphItem(ParameterHandler):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self,*args, **kwargs):
        '''
        Arrows can be initialized with any keyword arguments accepted by 
        the setStyle() method.
        '''
        super().__init__(args[0])
        
        self.initializeMain(**kwargs)
        self._mode = '2D'
        self.default_target = None

    def initializeMain(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Visible', True, 
            tags     = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Position', [2.,2.,0.],
            names  = ['x','y','z'],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Angle', 0.,
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Z', 0,
            tags   = ['2D'],
            method = self.refresh)

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        if hasattr(self, 'draw_items'):
            if self['Visible']:
                if self._mode == '2D':
                    self.setVisual()
                elif self._mode == '3D':
                    pass
            else:
                self.removeItems()

        else:
            if self['Visible'] and self._mode == '2D':
                self.draw()
            elif self['Visible'] and self._mode == '3D':
                self.drawGL()

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        pass

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        pass

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        pass

    def removeItems(self):
        '''
        '''
        if self.default_target is None:
            return

        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.removeItem(curve)
            del self.draw_items

    