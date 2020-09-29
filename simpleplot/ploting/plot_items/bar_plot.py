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

from PyQt5      import QtGui
from copy       import deepcopy
import numpy    as np

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl
from ..graphics_geometry.shaders      import ShaderConstructor
from ...models.parameter_class       import ParameterHandler 

class BarPlot(ParameterHandler): 
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
        ParameterHandler.__init__(self, 'BarPlot')
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
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Draw smooth', False, 
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'OpenGl mode', 'opaque',
            choices = ['translucent', 'opaque', 'additive'],
            tags    = ['3D'],
            method  = self.refresh)
        self.addParameter(
            'Width', [0.5,0.5],
            names   = ['x','y'],
            tags    = ['3D'],
            method  = self.refresh)

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        if hasattr(self, 'draw_items'):
            if self['Visible']:

                if self._mode == '2D':
                    self.removeItems()
                    self.draw()
                    
                elif self._mode == '3D':

                    vertices, faces = self.parent()._plot_data.getMesh(*self['Width'])
                    kwargs = {}
                    kwargs['vertexes']  = vertices
                    kwargs['faces']     = faces
                    kwargs['smooth']    = True
                    kwargs['drawEdges'] = False
                    self.draw_items[0].setMeshData(**kwargs)
                    self.draw_items[0].setGLOptions(self['OpenGl mode'])
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
            self.removeItems()
            self.draw()

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
            data        = self.parent()._plot_data.getData()
            bounds      = self.parent()._plot_data.getBounds()
            step        = (bounds[0][1] - bounds[0][0]) / data[0].shape[0]
            segment     = step / data[1].shape[0]
            arrangement = np.array([ -step/2. + l * segment for l in range(data[1].shape[0])])

            positions   = self.childFromName('Shader')._positions
            colors      = np.array(self.childFromName('Shader')._colors, dtype=np.uint)*255
            color_map   = pg.ColorMap(positions,colors)
            mapping     = color_map.map((data[2] -  bounds[2][0]) / (bounds[2][1] - bounds[2][0]))

            for i in range(data[0].shape[0]):
                y = data[0][i] + arrangement
                z = data[2][i,:]

                brushes = [pg.mkBrush(mapping[i,j]) for j in range(data[1].shape[0])]
                self.draw_items.append(pg.BarGraphItem(x = y, height = z, width = segment, brushes = brushes))
                self.default_target.view.addItem(self.draw_items[-1])

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
            vertices, faces = self.parent()._plot_data.getMesh(*self['Width'])
        
            kwargs = {}
            kwargs['vertexes']  = vertices
            kwargs['faces']     = faces
            kwargs['smooth']    = True
            kwargs['drawEdges'] = False
            self.draw_items.append(gl.GLMeshItem(**kwargs))
            self.draw_items[-1].setTransform(self.parent().transformer.getTransform())
            self.default_target.view.addItem(self.draw_items[-1])
            self.childFromName('Shader').runShader()

    def removeItems(self):
        '''
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)

    def processRay(self, ray):
        '''
        try to process the ray intersection
        '''
        pass
        