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
from PyQt5 import QtGui, QtCore

# Personal imports
from ...models.parameter_class      import ParameterHandler
from ..graphics_geometry.transformer  import Transformer

class GraphicsItem(ParameterHandler):
    '''
    This is the base of any graphcis object
    in the scene and will handle its display
    '''
    def __init__(self,*args, transformer = True, **kwargs):
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
        self.default_target = None
        self._mode = '2D'
        if transformer:
            self._transformer = Transformer()
            self.addChild(self._transformer)

    def setCurrentTags(self, tags):
        '''
        Overwrite the default current tag setter to allow
        adding and removing the current tranformaer and 
        shader constructor
        '''
        # if "2D" in tags:
        #     if self._transformer.parent() is self:
        #         self.model().removeRows(self._children.index(self._transformer), 1, self)
        #     if self._shader_constructor.parent() is self:
        #         self.model().removeRows(self._children.index(self._shader_constructor), 1, self)
        # elif "3D" in tags:
        #     if self._transformer.parent() is None:
        #         self.model().insertRows(0,1,[self._transformer], self)
        super().setCurrentTags(tags)

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
            'Movable', False,
            tags   = ['2D'],
            method = self.refresh)
        self.addParameter(
            'Z', 0,
            tags   = ['2D'],
            method = self.refresh)

    def initializeVisual2D(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Fill', [True, QtGui.QColor("blue")],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Line', [True, 0.05, QtGui.QColor("black")],
            names  = ["Visible", "Thickness", "Color"],
            tags   = ['2D', '3D'],
            method = self.refresh)

    def initializeVisual3D(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
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

    def redraw(self):
        '''
        Set the visual of the given shape element
        '''
        self.removeItems()
        
        if self['Visible'] and self._mode == '2D':
            self.draw()
        elif self['Visible'] and self._mode == '3D':
            self.drawGL()

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
                    self.setPlotData()
                elif self._mode == '3D':
                    self.setVisual()
                    self.setPlotData()
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

    def setPlotData(self):
        '''
        Set the visual of the given shape element
        '''
        pass

    def setOpenGLMode(self):
        '''
        Set the openg modes
        '''
        pass

    def setColor(self):
        '''
        Set the visual of the given shape element
        '''
        pass

    def getPen(self):
        '''
        '''
        if self['Line'][0]:
            pen = QtGui.QPen()
            pen.setColor(self['Line'][2])
            pen.setWidthF(self['Line'][1])
        else:
            pen = QtGui.QPen(QtCore.Qt.NoPen)

        return pen

    def getBrush(self):
        '''
        '''
        if self['Fill'][0]:
            brush = QtGui.QBrush(self['Fill'][1])
        else:
            brush = QtGui.QBrush(QtCore.Qt.NoBrush)

        return brush

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
                if isinstance(curve, list):
                    for subcurve in curve:
                        self.default_target.removeItem(subcurve)
                else:
                    self.default_target.removeItem(curve)
            del self.draw_items
            
    def handleMove(self,coordinates:list):
        '''
        change the position
        '''
        self.items['Position'].updateValue([
            self['Position'][0]+coordinates[0],
            self['Position'][1]+coordinates[1],
            self['Position'][2]
        ], method = True)
    