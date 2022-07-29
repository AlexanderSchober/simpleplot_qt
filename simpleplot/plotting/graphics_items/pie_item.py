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
from .graphics_item    import GraphicsItem
from ..views.pie_view      import PieView
from ..views_3D.pie_view_3D   import PieView3D

class PieItem(GraphicsItem):
    '''
    This is a derivative of the GrahicsItem class
    that will handle the drawing of a Pie chart either
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
        super().__init__(args[0])
        
        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self.initializeVisual2D(**kwargs)
        self.initializeVisual3D(**kwargs)
        self._mode = '2D'

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
            method = self.redraw)
        self.addParameter(
            'Subdivision dimensions', [True, 2.,10.],
            names  = ['Fill','Radial','Angular'],
            tags   = ['2D', '3D'],
            method = self.setVisual)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return
        if self._mode == '2D':
            if len(self.draw_items) != self['Subdivisions'][0] or len(self.draw_items[0]) != self['Subdivisions'][1]:
                self.redraw()
                return

        parameters = {
            'angle' : self['Angle'], 
            'pen' : super().getPen(),
            'brush' : super().getBrush(),
            'Z' : self['Z'],
            'movable' : self['Movable'],
            'radial_range' : [],
            'angle_range' : []}
            
        radial_range = self.getRadialRanges()
        angle_range = self.getAngleRanges()

        if self._mode == '2D':

            parameters['positions'] = [0,0][:-1]
            for i in range(self['Subdivisions'][0]):
                for j in range(self['Subdivisions'][1]):
                    parameters['radial_range'] = radial_range[i]
                    parameters['angle_range'] = angle_range[j]
                    self.draw_items[i][j].setData(**dict(parameters))
        elif self._mode == '3D':
            parameters['position']      = [0,0,0]
            parameters['drawFaces']     = self['Draw faces']
            parameters['drawEdges']     = self['Draw edges']
            parameters['brush_color']   = self['Fill'][1] if self['Fill'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_color']     = self['Line'][2] if self['Line'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_thickness'] = self['Line'][1] if self['Line'][0] else 0
            parameters['radial_range'] = radial_range
            parameters['angle_range'] = angle_range

            self.draw_items[0].setData(**dict(parameters)) 
        
        self.setColor()

    def getRadialRanges(self):
        '''
        Returns the angle ranges for the drawing
        '''
        radial_range = []
        if self['Subdivision dimensions'][0]: 
            for i in range(self['Subdivisions'][0]):
                radial_range.append([
                    self['Radial range'][0]+i
                    *(self['Radial range'][1]-self['Radial range'][0])
                    /self['Subdivisions'][0],
                    self['Radial range'][0]+(i+1)
                    *(self['Radial range'][1]-self['Radial range'][0])
                    /self['Subdivisions'][0]])
        else:
            for i in range(self['Subdivisions'][0]):
                radial_range.append([
                    self['Radial range'][0]+(i+0.5)
                    *(self['Radial range'][1]-self['Radial range'][0])
                    /self['Subdivisions'][0]-self['Subdivision dimensions'][1]/2.,
                    self['Radial range'][0]+(i+0.5)
                    *(self['Radial range'][1]-self['Radial range'][0])
                    /self['Subdivisions'][0]+self['Subdivision dimensions'][1]/2.])
        return radial_range

    def getAngleRanges(self):
        '''
        Returns the radial ranges for the drawing
        '''
        angle_range = []
        if self['Subdivision dimensions'][0]: 
            for j in range(self['Subdivisions'][1]):
                angle_range.append([
                    self['Angular range'][0]+j
                    *(self['Angular range'][1]-self['Angular range'][0])
                    /self['Subdivisions'][1],
                    self['Angular range'][0]+(j+1)
                    *(self['Angular range'][1]-self['Angular range'][0])
                    /self['Subdivisions'][1]])
        else:
            for j in range(self['Subdivisions'][1]):
                angle_range.append([
                    self['Angular range'][0]+(j+0.5)
                    *(self['Angular range'][1]-self['Angular range'][0])
                    /self['Subdivisions'][1]-self['Subdivision dimensions'][2]/2.,
                    self['Angular range'][0]+(j+0.5)
                    *(self['Angular range'][1]-self['Angular range'][0])
                    /self['Subdivisions'][1]+self['Subdivision dimensions'][2]/2.])
        return angle_range

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
        self.removeItems()
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view.view
            self.setCurrentTags(['3D'])

        if self['Visible']:
            self.draw_items = [PieView3D()]
            self.default_target.addItem(self.draw_items[0])
            self.setOpenGLMode()
            self.setVisual()
