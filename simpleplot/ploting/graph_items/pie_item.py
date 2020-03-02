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

from .graph_item import GraphItem
from .pie_view import PieView

class PieItem(GraphItem):
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
        
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Radial range',[1., 2.],
            names = ['Inner', 'Outter'],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Angular range',[45., 325.],
            names = ['Inner', 'Outter'],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Fill', [True, QtGui.QColor("blue")],
            tags   = ['2D'],
            method = self.refresh)
        self.addParameter(
            'Line', [True, 0.1, QtGui.QColor("black")],
            names  = ["Visible", "Thickness", "Color"],
            tags   = ['2D'],
            method = self.refresh)
        self.addParameter(
            'Draw faces', True, 
            tags     = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Draw edges', False, 
            tags     = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Draw smooth', True, 
            tags     = ['3D'],
            method = self.refresh)
        self.addParameter(
            'OpenGl mode', 'opaque',
            choices = ['translucent', 'opaque', 'additive'],
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Representation', 'Spherical',
            choices = ['Spherical', 'Circular'],
            tags   = ['3D'],
            method = self.refresh)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if self['Line'][0]:
            pen = QtGui.QPen()
            pen.setColor(self['Line'][2])
            pen.setWidthF(self['Line'][1])
        else:
            pen = QtCore.Qt.NoPen

        if self['Fill'][0]:
            brush = QtGui.QBrush(self['Fill'][1])
        else:
            brush = QtCore.Qt.NoBrush

        self.draw_items[0].setData(
            positions = self['Position'][:-1], 
            radial_range = self['Radial range'],
            angle_range = self['Angular range'],
            angle = self['Angle'], 
            pen = pen,
            brush = brush,
            Z = self['Z'])

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface.draw_surface.vb
            self.setCurrentTags(['2D'])
            
        if self['Visible']:
            self.draw_items = [PieView()]
            self.default_target.addItem(self.draw_items[0])
            self.setVisual()

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view
            self.setCurrentTags(['3D'])

        if self['Visible']:
            self.draw_items = []
            self.default_target.addItem(self.draw_items[-1])
