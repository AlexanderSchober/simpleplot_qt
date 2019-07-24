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

class DistributionPlot(ParameterHandler): 
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
        ParameterHandler.__init__(self, 'Atoms')
        self.addChild(ShaderConstructor())
        self.initialize(**kwargs)
        self._mode = '3D'

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
        self.addParameter(
            'Representation', 'Spherical',
            choices = ['Spherical', 'Circular'],
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
                # data    = self.parent()._plot_data.getData()
                # if not len(self.draw_items) == data[0].shape[0]:
                self.removeItems()
                if self._mode == '2D':
                    self.draw()
                elif self._mode == '3D':
                    self.drawGL() 
                # elif self._mode == '2D':
                #     pass
                # #     surface.setImage(self.parent()._plot_data.getData()[2])
                # #     self.childFromName('Shader').runShader()
    
                # elif self._mode == '3D':
                #     color   = self.parent()._plot_data.getData()[1]
                #     mesh_data    = self.parent()._plot_data.getMesh()
                #     for i, surface in enumerate(self.draw_items):
                        
                #         surface.opts['drawEdges']   = self['Draw edges']
                #         surface.opts['drawFaces']   = self['Draw faces']
                #         surface.opts['smooth']      = self['Draw smooth']

                #         kwargs = {}
                #         kwargs['vertexes']  = mesh_data[i][0]
                #         kwargs['faces']     = mesh_data[i][1]
                #         surface.setMeshData(**kwargs)
                #         surface.setGLOptions(self['OpenGl mode'])

                #     self.childFromName('Shader').runShader()
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

    def _refreshBounds(self):
        '''
        refresh the bounds of the parameter handler 
        as the data is being refreshed
        '''
        bounds = self.parent()._plot_data.getBounds()

        targets     = ['X range', 'Y range', 'Z range']
        for j,target in enumerate(targets):
            data_range = self[target]
            if not data_range[0]:
                data_range[1] = float(bounds[j][0])
                data_range[2] = float(bounds[j][1])
                self.items[target].updateValue(data_range, method = False)

    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        colors = self.parent()._plot_data.getData()[1]
        for i,color in enumerate(colors):
            self.draw_items[i].setColor(color)

            if hasattr(self.draw_items[i], 'setShader'):
                self.draw_items[i].setShader(self.childFromName('Shader').getShader('light'))

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])

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
            kwargs = {}

            if self['Representation'] == 'Spherical':
                kwargs['smooth']    = self['Draw smooth']
                kwargs['drawFaces'] = self['Draw faces']
                kwargs['drawEdges'] = self['Draw edges']
                data = self.parent()._plot_data.getMesh()
                color = self.parent()._plot_data.getData()[1]
                for i,element in enumerate(data):
                    kwargs['vertexes']  = element[0]
                    kwargs['faces']     = element[1]
                    self.draw_items.append(gl.GLMeshItem(**kwargs))
                    self.draw_items[-1].setGLOptions(self['OpenGl mode'])
                    self.default_target.view.addItem(self.draw_items[-1])
                    self.draw_items[-1].setTransform(self.parent().transformer.getTransform())
                self.childFromName('Shader').runShader()

            elif self['Representation'] == 'Circular':
                pos     = self.parent()._plot_data.getData()[0][:,0:3]
                size    = self.parent()._plot_data.getData()[0][:,3]
                color   = self.parent()._plot_data.getData()[1]
                self.draw_items.append(gl.GLScatterPlotItem(
                    pos     = pos, 
                    color   = color, 
                    size    = size, 
                    pxMode  = False,
                    glOptions = self['OpenGl mode']
                    ))
                self.default_target.view.addItem(self.draw_items[-1])
                self.draw_items[-1].setTransform(self.parent().transformer.getTransform())

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)
            del self.draw_items
