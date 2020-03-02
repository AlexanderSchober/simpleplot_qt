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

from .rectangle_item import RectangleItem

class SquareItem(RectangleItem):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self,*args, **kwargs):
        '''
        Arrows can be initialized with any keyword arguments accepted by 
        the setStyle() method.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Dimension', 2.,
            names  = ['x','y'],
            tags   = ['2D', '3D'],
            method = self.refresh)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        self.draw_items[-1].setData(
            positions = self['Position'][:-1], 
            dimensions = [self['Dimension'],self['Dimension']],
            angle = self['Angle'], 
            pen = super().getPen(),
            brush = super().getBrush(),
            Z = self['Z'],
            movable = self['Movable'])
