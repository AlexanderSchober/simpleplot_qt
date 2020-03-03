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
        
        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self.initializeVisual2D(**kwargs)
        self.initializeVisual3D(**kwargs)
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
            'Subdivisions', [2,2],
            names  = ['Radial','Angular'],
            tags   = ['2D', '3D'],
            method = self.resetSubdivision)
        self.addParameter(
            'Subdivision dimensions', [True, 2.,10.],
            names  = ['Fill','Radial','Angular'],
            tags   = ['2D', '3D'],
            method = self.resetSubdivision)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        parameters = {
            'angle' : self['Angle'], 
            'pen' : super().getPen(),
            'brush' : super().getBrush(),
            'Z' : self['Z'],
            'movable' : self['Movable'],
            'positions' : self['Position'][:-1],
            'radial_range' : [],
            'angle_range' : []}
            
        for i in range(self['Subdivisions'][0]):
            for j in range(self['Subdivisions'][1]):
                if self['Subdivision dimensions'][0]:
                    parameters['angle_range'] = [
                        self['Angular range'][0]+j
                        *(self['Angular range'][1]-self['Angular range'][0])
                        /self['Subdivisions'][1],
                        self['Angular range'][0]+(j+1)
                        *(self['Angular range'][1]-self['Angular range'][0])
                        /self['Subdivisions'][1]]

                    parameters['radial_range'] = [
                        self['Radial range'][0]+i
                        *(self['Radial range'][1]-self['Radial range'][0])
                        /self['Subdivisions'][0],
                        self['Radial range'][0]+(i+1)
                        *(self['Radial range'][1]-self['Radial range'][0])
                        /self['Subdivisions'][0]]
                else:
                    parameters['angle_range'] = [
                        self['Angular range'][0]+(j+0.5)
                        *(self['Angular range'][1]-self['Angular range'][0])
                        /self['Subdivisions'][1]-self['Subdivision dimensions'][2]/2.,
                        self['Angular range'][0]+(j+0.5)
                        *(self['Angular range'][1]-self['Angular range'][0])
                        /self['Subdivisions'][1]+self['Subdivision dimensions'][2]/2.]

                    parameters['radial_range'] = [
                        self['Radial range'][0]+(i+0.5)
                        *(self['Radial range'][1]-self['Radial range'][0])
                        /self['Subdivisions'][0]-self['Subdivision dimensions'][1]/2.,
                        self['Radial range'][0]+(i+0.5)
                        *(self['Radial range'][1]-self['Radial range'][0])
                        /self['Subdivisions'][0]+self['Subdivision dimensions'][1]/2.]

                self.draw_items[i][j].setData(**dict(parameters))

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
            self.draw_items = []
            for i in range(self['Subdivisions'][0]):
                temp = []
                for j in range(self['Subdivisions'][1]):
                    item = PieView()
                    temp.append(item)
                    self.default_target.addItem(item)
                    item.moved.connect(self.handleMove)
                self.draw_items.append(temp)
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
