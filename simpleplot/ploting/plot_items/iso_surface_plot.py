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

from PyQt5 import QtGui
import numpy as np
from OpenGL.GL  import *

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl

from ..plot_geometries.shaders      import ShaderConstructor
from ...model.parameter_class       import ParameterHandler 
from ..plot_geometries.shaders      import ShaderConstructor

class IsoSurfacePlot(ParameterHandler): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.
        '''
        ParameterHandler.__init__(self, 'IsoSurface')
        self.addChild(ShaderConstructor())
        self.initialize(**kwargs)
        self._mode = '3D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Visible', False, 
            tags   = ['3D'],
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
            'Level', 0.2, 
            tags     = ['3D'],
            method = self.refresh)

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        if hasattr(self, 'draw_items'):
            if self['Visible']:
                surface = None
                for draw_item in self.draw_items:
                    if isinstance(draw_item, gl.GLMeshItem):
                        surface = draw_item
                            
                if self._mode == '3D':
                    surface.opts['drawEdges']   = self['Draw edges']
                    surface.opts['drawFaces']   = self['Draw faces']
                    surface.opts['smooth']      = self['Draw smooth']

                    data = self.parent()._plot_data.getIsoSurface(self['Level'])
                    kwargs = {}
                    kwargs['vertexes']  = data[0]
                    kwargs['faces']     = data[1]
                    surface.setMeshData(**kwargs)
                    self.childFromName('Shader').runShader()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i],gl.GLMeshItem):
                        if self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                del self.draw_items
        else:
            if self['Visible'] and self._mode == '3D':
                self.drawGL()

    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        if self._mode == '3D':
            self.draw_items[0].setShader(self.childFromName('Shader').getShader('edgeShader'))

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface

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
            mesh = self.parent()._plot_data.getIsoSurface(self['Level'])
            kwargs = {}
            kwargs['vertexes']  = mesh[0]
            kwargs['faces']     = mesh[1]
            kwargs['smooth']    = self['Draw smooth']
            kwargs['drawFaces'] = self['Draw faces']
            kwargs['drawEdges'] = self['Draw edges']
            self.draw_items.append(gl.GLMeshItem(**kwargs))
            self.draw_items[-1].setGLOptions('opaque')
            self.default_target.view.addItem(self.draw_items[-1])
            self.childFromName('Shader').runShader()

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)
