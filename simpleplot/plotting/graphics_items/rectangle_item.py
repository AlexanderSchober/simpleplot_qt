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
import numpy as np

# Personal imports
from .graphics_item import GraphicsItem
from ..views.rectangle_view import RectangleView
from ..views_3D.rectangle_view_3D import  RectangleView3D

class RectangleItem(GraphicsItem):
    '''
    This is a derivative of the GrahicsItem class
    that will handle the drawing of a Rectangle either
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
        
        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self.initializeVisual2D(**kwargs)
        self.initializeVisual3D(**kwargs)

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
            'Dimensions', [1.,1.],
            names  = ['x','y'],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Subdivisions', [2,2],
            names  = ['x','y'],
            tags   = ['2D', '3D'],
            method = self.redraw)
        self.addParameter(
            'Subdivision dimensions', [True, 2.,2.],
            names  = ['Fill', 'x','y'],
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
            'positions':[],
            'dimensions':[]
            }

        if self._mode == '2D':
            parameters['dimensions'] = self.getDimensionSubItem()
            for i in range(self['Subdivisions'][0]):
                for j in range(self['Subdivisions'][1]):
                    parameters['positions'] = self.getPositionSubItem(i,j)
                    self.draw_items[i][j].setData(**dict(parameters))
        elif self._mode == '3D':
            parameters['dimensions']    = self.getDimensionSubItem()
            parameters['drawFaces']     = self['Draw faces']
            parameters['drawEdges']     = self['Draw edges']
            parameters['brush_color']   = self['Fill'][1] if self['Fill'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_color']     = self['Line'][2] if self['Line'][0] else QtGui.QColor(0,0,0,0)
            parameters['pen_thickness'] = self['Line'][1] if self['Line'][0] else 0
            for i in range(self['Subdivisions'][0]):
                for j in range(self['Subdivisions'][1]):
                    parameters['positions'].append(self.getPositionSubItem(i,j))
            self.draw_items[0].setData(**dict(parameters)) 

    def getPositionSubItem(self, i:int, j:int)->list:
        '''
        Get the positions of the subitems depending ion their
        indices
        '''
        pos = [
            -self['Dimensions'][0]/2.+(i+0.5)*self['Dimensions'][0]
            /self['Subdivisions'][0],
            -self['Dimensions'][1]/2.+(j+0.5)*self['Dimensions'][1]
            /self['Subdivisions'][1]]

        norm = np.sqrt(pos[0]**2+pos[1]**2)
        if norm == 0.:
            return  [0,0,0]
        else:
            angle = np.arccos(pos[0]/norm)/np.pi*180.
            if np.arcsin(pos[1]/norm) < 0:
                angle = -angle 

            return [
                norm*np.cos((angle)*np.pi/180.),
                norm*np.sin((angle)*np.pi/180.),
                0]

    def getDimensionSubItem(self)->list:
        '''
        Get the dimension of the subitems depending ion their
        indices
        '''        
        if self['Subdivision dimensions'][0]:
            return [
                self['Dimensions'][0]/self['Subdivisions'][0],
                self['Dimensions'][1]/self['Subdivisions'][1]]
        else:
            return [
                self['Subdivision dimensions'][1],
                self['Subdivision dimensions'][2]]  

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
                    item = RectangleView()
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
            self.draw_items = [RectangleView3D()]
            self.default_target.addItem(self.draw_items[0])
            self.setOpenGLMode()
            self.setVisual()
