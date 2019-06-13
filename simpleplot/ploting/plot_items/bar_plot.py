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

from ...pyqtgraph import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph import opengl as gl

from ..plot_geometries.surfaces   import QuadSurface
from ..plot_geometries.points     import Point
from ..plot_geometries.shaders    import ShaderConstructor

from ...model.node   import SessionNode

class BarPlot(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, z_lower = None, **kwargs):
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
        SessionNode.__init__(self, 'No_name')

        self.x_data = deepcopy(x)
        self.y_data = deepcopy(y)
        self.z_data = deepcopy(z)
        self.z_lower_data = deepcopy(z_lower)

        self.initialize(**kwargs)
        self._mode = '2D'
        self.type  = 'Bar'

        self._position = np.array([0,0,0])
        self._scale = np.array([1,1,1])
        self._rotate_angle = np.array([0,0,0])
        self._rotate_axis = np.array([[1,0,0], [0,1,0], [0,0,1]])

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.parameters = {}

        self.parameters['Bar']    = [[True]]
        self.parameters['Colors']     = [[
                [0.,1.,1., 1.],
                [0.,0.,1., 1.],
                [0.,1.,0., 1.],
                [1.,0.,0., 1.],
                [0.,1.,0., 1.]
            ]]
        self.parameters['Positions'] = [[0,0.25,0.5,0.75,1.]]
        self.parameters['Shader']    = [ None, ['str', 'hex', 'list', 'int']]
        self.parameters['Name']      = [ 'No Name', ['str']]
        self.parameters['Width']     = [ [0.1,0.1]]
        self.parameters['Lower']     = [ [0]]

        for key in kwargs.keys():
            self.parameters[key][0] = kwargs[key]

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(self.getParameter('Colors'), dtype=np.ubyte)*255)

        self.shader_parameters = {}
        self.shader_parameters['Bounds x'] = [[True, 0,1]]
        self.shader_parameters['Bounds y'] = [[True, 0,1]]
        self.shader_parameters['Bounds z'] = [[True, 0,1]]

    def getParameter(self, name):
        '''
        Returns the value of the parameter requested
        '''
        return self.parameters[name][0]

    def setData(self, **kwargs):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        if self._mode == '3D':
            temp_position = np.array(self._position)
            temp_scale = np.array(self._scale)
            temp_angle = np.array(self._rotate_angle)
            temp_axis  = np.array(self._rotate_axis)

            self._position = np.array([0,0,0])
            self._scale = np.array([1,1,1])
            self._rotate_angle = np.array([0,0,0])
            self._rotate_axis = np.array([[1,0,0], [0,1,0], [0,0,1]])

            for draw_item in self.draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        item.resetTransform()
                else:
                    draw_item.resetTransform()

        if 'x' in kwargs.keys():
            self.x_data = kwargs['x']
        if 'y' in kwargs.keys():
            self.y_data = kwargs['y']
        if 'z' in kwargs.keys():
            self.z_data = kwargs['z']
        if 'z_lower' in kwargs.keys():
            self.z_lower_data = kwargs['z_lower']
        if 'Lower' in kwargs.keys():
            self.parameters['Lower'] = kwargs['Lower']

        if hasattr(self, 'draw_items'):
            
            #find the surface
            surface = None
            for draw_item in self.draw_items:
                if isinstance(draw_item, gl.GLMeshItem):
                    surface = draw_item

            #if not present draw it
            if surface == None:
                if self._mode == '2D':
                    pass
                elif self._mode == '3D':
                    self.drawGLBar()
                for draw_item in self.draw_items:
                    if isinstance(draw_item, gl.GLMeshItem):
                        surface = draw_item

            #update if 2D
            if self._mode == '2D':
                self.removeItems()
                self.draw()

            #update if 3D
            elif self._mode == '3D':
                xx, yy      = np.meshgrid(self.x_data, self.y_data)
                reshaped_x  = xx.reshape(self.z_data.shape[0]*self.z_data.shape[1])
                reshaped_y  = yy.reshape(self.z_data.shape[0]*self.z_data.shape[1])
                reshaped_z  = np.repeat(self.z_data.reshape(self.z_data.shape[0]*self.z_data.shape[1]), 8)
                if not self.z_lower_data is None:
                    reshaped_z_lower = np.repeat(self.z_lower_data.reshape(self.z_data.shape[0]*self.z_data.shape[1]), 8)
                width_x     = self.getParameter('Width')[0]
                width_y     = self.getParameter('Width')[1]

                self.points[[j*8+0 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
                self.points[[j*8+0 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

                self.points[[j*8+1 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
                self.points[[j*8+1 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

                self.points[[j*8+2 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
                self.points[[j*8+2 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

                self.points[[j*8+3 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
                self.points[[j*8+3 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

                self.points[[j*8+4 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
                self.points[[j*8+4 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

                self.points[[j*8+5 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
                self.points[[j*8+5 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

                self.points[[j*8+6 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
                self.points[[j*8+6 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

                self.points[[j*8+7 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
                self.points[[j*8+7 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

                if not self.z_lower_data is None:
                    self.points[self.change_index_0,2] = reshaped_z_lower[self.change_index_0] 
                else:
                    self.points[self.change_index_0,2] = self.getParameter('Lower')[0]

                self.points[self.change_index_1,2] = reshaped_z[self.change_index_1] 

                kwargs = {}
                kwargs['vertexes']  = self.points
                kwargs['faces']     = self.vertices
                surface.setMeshData(**kwargs)

                if self.shader_parameters['Bounds z'][0][0] == True:
                    self.shader_constructor.setRange(
                        np.amin([np.amin(self.z_data), self.getParameter('Lower')[0]])-1.0e-6 if self.z_lower_data is None else np.amin([np.amin(self.z_data), np.amin(self.z_lower_data)]), np.amax(self.z_data)+1.0e-6 if self.z_lower_data is None else np.amax([np.amax(self.z_data), np.amax(self.z_lower_data)])+1.0e-6)
                else:
                    self.shader_constructor.setRange(
                        0, 
                        self.shader_parameters['Bounds z'][0][2]+1.0e-6)

                self.shader_constructor.setColors(
                    self.parameters['Colors'][0],
                    self.parameters['Positions'][0])


                surface.setShader(self.shader_constructor.getShader('height'))

        else:
            if self._mode == '2D':
                self.draw()
            elif self._mode == '3D':
                self.drawGL()

        if self._mode == '3D':
            self.translate(temp_position)
            self.scale(temp_scale)
            self.rotate(temp_angle, temp_axis)

    def setColor(self, colors, positions):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''

        surface = None
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                surface = draw_item

        self.parameters['Colors']     = [colors]
        self.parameters['Positions']  = [positions]

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(self.getParameter('Colors'), dtype=np.ubyte)*255)

        if self._mode == '2D':
            self.removeItems()
            self.draw()

        elif self._mode == '3D' and not surface == None:
            self.shader_constructor.setColors(
                self.parameters['Colors'][0],
                self.parameters['Positions'][0])
            surface.setShader(self.shader_constructor.getShader('height'))

    def translate(self, position):
        '''
        translate in the 3D view
        '''
        if self._mode == '3D' and hasattr(self, 'draw_items'):
            for draw_item in self.draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.translateItem(item, position)
                else:
                    self.translateItem(draw_item, position)

            self._position = position

    def translateItem(self, item, position):
        '''
        translate in the 3D view
        '''
        item.translate(
            -self._position[0], 
            -self._position[1], 
            -self._position[2])

        item.translate(
            position[0], 
            position[1], 
            position[2])

    def scale(self, scale):
        '''
        scale in the 3D view
        '''
        for i in range(3):
            if scale[i] == 0 :
                scale[i] = 1

        if self._mode == '3D' and hasattr(self, 'draw_items'):
            for draw_item in self.draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.scaleItem(item, scale)
                else:
                    self.scaleItem(draw_item, scale)

            self._scale = scale

    def scaleItem(self, item, scale):
        '''
        scale in the 3D view
        '''
        item.scale(
            1/self._scale[0], 
            1/self._scale[1], 
            1/self._scale[2])

        item.scale(
            scale[0], 
            scale[1], 
            scale[2])

    def rotate(self, angles, axes):
        '''
        rotate in the 3D view
        '''
        if self._mode == '3D' and hasattr(self, 'draw_items'):
            for draw_item in self.draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.rotateItem(item,  angles, axes)
                else:
                    self.rotateItem(draw_item,  angles, axes)

            self._rotate_angle = angles
            self._rotate_axis  = axes

    def rotateItem(self, item, angles, axes):
        '''
        rotate in the 3D view
        '''
        for i in range(3):
            item.rotate(
                -self._rotate_angle[-1-i],
                self._rotate_axis[-1-i,0] + self._position[0], 
                self._rotate_axis[-1-i,1] + self._position[1],
                self._rotate_axis[-1-i,2] + self._position[2])

        for i in range(3):
            item.rotate(
                angles[i],
                axes[i,0] + self._position[0], 
                axes[i,1] + self._position[1],
                axes[i,2] + self._position[2])

    def buildVerticeMap(self):
        '''
        build the vertices and positions locally from
        the given axes
        '''
        positions   = np.zeros((self.z_data.shape[0]*self.z_data.shape[1]*8, 3))
        vertices    = np.zeros((self.z_data.shape[0]*self.z_data.shape[1]*12, 3),  dtype='uint')
        xx, yy      = np.meshgrid(self.x_data, self.y_data)

        reshaped_x  = xx.reshape(self.z_data.shape[0]*self.z_data.shape[1])
        reshaped_y  = yy.reshape(self.z_data.shape[0]*self.z_data.shape[1])
        reshaped_z  = self.z_data.reshape(self.z_data.shape[0]*self.z_data.shape[1])
        if not self.z_lower_data is None:
            use_lower = True
            reshaped_z_lower = self.z_lower_data.reshape(self.z_data.shape[0]*self.z_data.shape[1])
        else:
            use_lower = False
            lower = self.getParameter('Lower')[0]

        width_x     = self.getParameter('Width')[0]
        width_y     = self.getParameter('Width')[1]

        self.change_index_0 = []
        self.change_index_1 = []

        for i in range(self.z_data.shape[0]*self.z_data.shape[1]):
            positions[i*8 + 0] = np.array([reshaped_x[i] - width_x, reshaped_y[i] - width_y, reshaped_z_lower[i] if use_lower else lower])
            positions[i*8 + 1] = np.array([reshaped_x[i] + width_x, reshaped_y[i] - width_y, reshaped_z_lower[i] if use_lower else lower])
            positions[i*8 + 2] = np.array([reshaped_x[i] + width_x, reshaped_y[i] + width_y, reshaped_z_lower[i] if use_lower else lower])
            positions[i*8 + 3] = np.array([reshaped_x[i] - width_x, reshaped_y[i] + width_y, reshaped_z_lower[i] if use_lower else lower])
            positions[i*8 + 4] = np.array([reshaped_x[i] - width_x, reshaped_y[i] - width_y, reshaped_z[i]])
            positions[i*8 + 5] = np.array([reshaped_x[i] + width_x, reshaped_y[i] - width_y, reshaped_z[i]])
            positions[i*8 + 6] = np.array([reshaped_x[i] + width_x, reshaped_y[i] + width_y, reshaped_z[i]])
            positions[i*8 + 7] = np.array([reshaped_x[i] - width_x, reshaped_y[i] + width_y, reshaped_z[i]])

            self.change_index_0 += [l for l in range(i*8 + 0, i*8 + 5)]
            self.change_index_1 += [l for l in range(i*8 + 4, i*8 + 8)]

            vertices[i*12 + 0]  = np.array([i*8 + 0, i*8 + 1, i*8 + 4])
            vertices[i*12 + 1]  = np.array([i*8 + 1, i*8 + 4, i*8 + 5])
            vertices[i*12 + 2]  = np.array([i*8 + 1, i*8 + 2, i*8 + 5])
            vertices[i*12 + 3]  = np.array([i*8 + 2, i*8 + 5, i*8 + 6])
            vertices[i*12 + 4]  = np.array([i*8 + 2, i*8 + 3, i*8 + 6])
            vertices[i*12 + 5]  = np.array([i*8 + 3, i*8 + 6, i*8 + 7])
            vertices[i*12 + 6]  = np.array([i*8 + 3, i*8 + 0, i*8 + 7])
            vertices[i*12 + 7]  = np.array([i*8 + 0, i*8 + 7, i*8 + 4])

            vertices[i*12 + 8]  = np.array([i*8 + 0, i*8 + 1, i*8 + 2])
            vertices[i*12 + 9]  = np.array([i*8 + 0, i*8 + 3, i*8 + 2])
            vertices[i*12 + 10] = np.array([i*8 + 4, i*8 + 5, i*8 + 6])
            vertices[i*12 + 11] = np.array([i*8 + 4, i*8 + 7, i*8 + 6])

        self.points     = positions
        self.vertices   = vertices

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            
        self.draw_items = []
            
        if self.getParameter('Bar')[0]:
            if not self.x_data is None and not self.y_data is None and not self.z_data is None:
                self.drawBar()

    def drawBar(self):
        '''
        Draw the Isocurves in opengl.
        '''
        step = (np.amax(self.x_data) - np.amin(self.x_data))/self.x_data.shape[0]
        segment = step / self.y_data.shape[0] 
        arrangement = np.array([ -step/2. + l * segment for l in range(self.y_data.shape[0])])

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(self.getParameter('Colors'), dtype=np.ubyte)*255)
        self.map = self.color_map.map(
            (self.z_data -  np.amin(self.z_data)) / (np.amax(self.z_data) - np.amin(self.z_data)))

        for i in range(self.x_data.shape[0]):
            y = self.x_data[i] + arrangement
            z = self.z_data[i,:]

            brushes = [pg.mkBrush(self.map[i,j]) for j in range(self.y_data.shape[0])]
            self.draw_items.append(pg.BarGraphItem(x = y, height = z, width = segment, brushes = brushes))
            self.default_target.view.addItem(self.draw_items[-1])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []
            
        if self.getParameter('Bar')[0]:
            if not self.x_data is None and not self.y_data is None and not self.z_data is None:
                self.drawGLBar()

    def drawGLBar(self):
        '''
        Draw the Isocurves in opengl.
        '''
        self.shader_constructor = ShaderConstructor()
        if self.shader_parameters['Bounds z'][0][0] == True:
            self.shader_constructor.setRange(
                np.amin([np.amin(self.z_data), self.getParameter('Lower')[0]])-1.0e-6 if self.z_lower_data is None else np.amin([np.amin(self.z_data), np.amin(self.z_lower_data)]), np.amax(self.z_data)+1.0e-6 if self.z_lower_data is None else np.amax([np.amax(self.z_data), np.amax(self.z_lower_data)])+1.0e-6)
        else:
            self.shader_constructor.setRange(
                0, 
                self.shader_parameters['Bounds z'][0][2]+1.0e-6)

        self.shader_constructor.setColors(
            self.parameters['Colors'][0],
            self.parameters['Positions'][0])

        self.buildVerticeMap()

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(self.getParameter('Colors'), dtype=np.ubyte)*255)
        
        kwargs = {}
        kwargs['vertexes']  = self.points
        kwargs['faces']     = self.vertices
        kwargs['smooth']    = True
        kwargs['drawEdges'] = False
        kwargs['shader']    = self.shader_constructor.getShader('height')
        kwargs['color']     = [0.1,0.1,0.1,1]
        self.draw_items.append(gl.GLMeshItem(**kwargs))

        self.default_target.view.addItem(self.draw_items[-1])

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
        