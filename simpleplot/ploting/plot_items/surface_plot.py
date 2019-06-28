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
from copy import deepcopy
import numpy as np

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl

from ..plot_geometries.shaders      import ShaderConstructor
from ...model.parameter_class       import ParameterHandler 
from ..plot_geometries.shaders      import ShaderConstructor

class SurfacePlot(ParameterHandler): 
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

        Parameters
        -----------
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        ParameterHandler.__init__(self, 'Surface')
        self.addChild(ShaderConstructor())
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Visible', True, 
            tags     = ['2D', '3D'],
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
                    if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                        surface = draw_item
                            
                if self._mode == '2D':
                    surface.setImage(self.parent()._plot_data.getData()[2])
                    self.childFromName('Shader').runShader()
                    
                elif self._mode == '3D':
                    surface.opts['drawEdges']   = self['Draw edges']
                    surface.opts['drawFaces']   = self['Draw faces']
                    surface.opts['smooth']      = self['Draw smooth']

                    data = self.parent()._plot_data.getMesh()
                    kwargs = {}
                    kwargs['vertexes']  = data[0]
                    kwargs['faces']     = data[1]
                    surface.setMeshData(**kwargs)
                    surface.setGLOptions(self['OpenGl mode'])
                    self.childFromName('Shader').runShader()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.ImageItem) or isinstance(self.draw_items[i], gl.GLMeshItem):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                del self.draw_items
        else:
            if self['Visible'] and self._mode == '2D':
                self.draw()
            elif self['Visible'] and self._mode == '3D':
                self.drawGL()
        
    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        if self._mode == '2D':
            color_map = pg.ColorMap(
                self.childFromName('Shader')._positions,
                np.array(self.childFromName('Shader')._colors, dtype=np.uint)*255)
            self.draw_items[0].setLookupTable(color_map.getLookupTable(0.0, 1.0, alpha = False))

        elif self._mode == '3D':
            self.draw_items[0].setShader(self.childFromName('Shader').getShader('height'))

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])

        if self['Visible']:
            self.draw_items = []
            self.draw_items.append(pg.ImageItem())
            self.draw_items[-1].setImage(self.parent()._plot_data.getData()[2])
            self.draw_items[-1].setZValue(-100)
            self.default_target.draw_surface.addItem(self.draw_items[-1])
            self.childFromName('Shader').runShader()

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
            mesh = self.parent()._plot_data.getMesh()
            kwargs = {}
            kwargs['vertexes']  = mesh[0]
            kwargs['faces']     = mesh[1]
            kwargs['smooth']    = self['Draw smooth']
            kwargs['drawFaces'] = self['Draw faces']
            kwargs['drawEdges'] = self['Draw edges']

            self.draw_items.append(gl.GLMeshItem(**kwargs))
            self.draw_items[-1].setGLOptions(self['OpenGl mode'])
            self.default_target.view.addItem(self.draw_items[-1])
            self.childFromName('Shader').runShader()

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)
