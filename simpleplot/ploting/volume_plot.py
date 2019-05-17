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

import pyqtgraph as pg
import pyqtgraph.opengl as gl

from copy import deepcopy
import numpy as np
from PyQt5 import QtGui
from OpenGL.GL import *

from .plot_items.surfaces   import QuadSurface
from .plot_items.points     import Point
from .plot_items.shaders    import ShaderConstructor

from ..model.node   import SessionNode

class VolumePlot(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, data = None, **kwargs):
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
        self.data   = deepcopy(data)

        self.initialize(**kwargs)
        self._mode = '3D'
        self.type  = 'Volume'

        self._position      = np.array([0,0,0])
        self._scale         = np.array([1,1,1])
        self._rotate_angle  = np.array([0,0,0])
        self._rotate_axis   = np.array([[1,0,0], [0,1,0], [0,0,1]])

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.parameters = {}

        #Volume part
        self.parameters['Volume']    = [[True]]
        self.parameters['Colors']     = [[
                [0.,1.,1., 1.],
                [0.,0.,1., 1.],
                [0.,1.,0., 1.],
                [1.,0.,0., 1.],
                [0.,1.,0., 1.]]]
        self.parameters['Positions']    = [[0,0.45,0.5,0.65,1.]]
        self.parameters['Alpha']        = [[0.,0.,1.,0.,1.,0.,0.]]
        self.parameters['Alpha pos.']   = [[0,0.3,0.45,0.5,0.65,0.7,1.]]

        for key in kwargs.keys():
            self.parameters[key][0] = kwargs[key]

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(np.array(self.getParameter('Colors'))*255, dtype=np.ubyte),
            )

        alpha = np.zeros((len(self.parameters['Alpha'][0]), 4), dtype=np.ubyte) 
        alpha[:,3] = np.array(np.array(self.getParameter('Alpha'))*255., dtype=np.ubyte)[:]
        self.alpha_map = pg.ColorMap(np.array(self.getParameter('Alpha pos.')),alpha)

        #isosurface
        self.parameters['Iso surface']    = [[True]]
        self.parameters['Iso color']     = [[QtGui.QColor('blue')]]
        self.parameters['Iso value']     = [[0.2]]

        # self.shader_parameters = {}
        # self.shader_parameters['Bounds x'] = [[True, 0,1]]
        # self.shader_parameters['Bounds y'] = [[True, 0,1]]
        # self.shader_parameters['Bounds z'] = [[True, 0,1]]

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
        #find the surface
        surface = None
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                surface = draw_item

        self.parameters['Colors']     = [colors]
        self.parameters['Positions']  = [positions]

        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(self.getParameter('Colors'), dtype=np.ubyte)*255)

        if self._mode == '3D' and not surface == None:
            self.shader_constructor.setColors(
                self.parameters['Colors'][0],
                self.parameters['Positions'][0])
            surface.setShader(self.shader_constructor.getShader('height'))

        if self.getParameter('Line color grad')[0]:
            self.setIsoColor()

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

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []
            
        if self.getParameter('Volume')[0]:
            self._drawGLVolume()

        if self.getParameter('Iso surface')[0]:
            self._drawGLIsoSurface()

    def _drawGLVolume(self):
        '''
        Draw the Isocurves in opengl.
        '''
        kwargs = {}
        kwargs['sliceDensity']  = 100
        kwargs['smooth']        = True
        self.draw_items.append(CustomGLVolumeItem(self._getVolumeColor(),**kwargs))
        self.default_target.view.addItem(self.draw_items[-1])

    def _getVolumeColor(self):
        '''
        Small function to ease the creation of the 
        color data map for the volume generation
        '''
        self.data -= np.amin(self.data)
        self.data /= np.amax(self.data)
        colors = self.color_map.map(self.data)
        colors[:,:,:,3] = self.alpha_map.map(self.data)[:,:,:,3]
        return colors

    def _drawGLIsoSurface(self):
        '''
        Draw the Isocurves in opengl.
        '''
        self.data -= np.amin(self.data)
        self.data /= np.amax(self.data)

        vertices, faces = pg.isosurface(self.data, self.getParameter('Iso value')[0])
        print(vertices, faces)

        kwargs = {}
        kwargs['vertexes']  = vertices
        kwargs['faces']     = faces
        kwargs['smooth']    = True
        kwargs['drawEdges'] = False
        kwargs['color']     = self.getParameter('Iso color')[0]
        kwargs['shader']    = 'edgeHilight'#self.shader_constructor.getShader('height')
        kwargs['glOptions'] = 'opaque'

        self.draw_items.append(gl.GLMeshItem(**kwargs))
        self.default_target.view.addItem(self.draw_items[-1])

    def removeItems(self):
        '''
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)

class CustomGLVolumeItem(gl.GLVolumeItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    
    Displays volumetric data. 
    """
    
    def __init__(self, data, sliceDensity=1, smooth=True, glOptions='translucent'):
        """
        ==============  =======================================================================================
        **Arguments:**
        data            Volume data to be rendered. *Must* be 4D numpy array (x, y, z, RGBA) with dtype=ubyte.
        sliceDensity    Density of slices to render through the volume. A value of 1 means one slice per voxel.
        smooth          (bool) If True, the volume slices are rendered with linear interpolation 
        ==============  =======================================================================================
        """
        gl.GLVolumeItem.__init__(self, data, sliceDensity=1, smooth=True, glOptions='translucent')
        self.x = None
        self.y = None
        self.z = None

    def drawVolume(self, ax, d):
        '''
        Draw the volume in the referential
        '''
        N = 5
        
        imax = [0,1,2]
        imax.remove(ax)
        print('d',d)
        
        tp = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        vp = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

        nudge = [0.5/x for x in self.data.shape]
        
        tp[0][imax[0]] = 0+nudge[imax[0]]
        tp[0][imax[1]] = 0+nudge[imax[1]]
        tp[1][imax[0]] = 1-nudge[imax[0]]
        tp[1][imax[1]] = 0+nudge[imax[1]]
        tp[2][imax[0]] = 1-nudge[imax[0]]
        tp[2][imax[1]] = 1-nudge[imax[1]]
        tp[3][imax[0]] = 0+nudge[imax[0]]
        tp[3][imax[1]] = 1-nudge[imax[1]]
        
        vp[0][imax[0]] = 0
        vp[0][imax[1]] = 0
        vp[1][imax[0]] = self.data.shape[imax[0]]
        vp[1][imax[1]] = 0
        vp[2][imax[0]] = self.data.shape[imax[0]]
        vp[2][imax[1]] = self.data.shape[imax[1]]
        vp[3][imax[0]] = 0
        vp[3][imax[1]] = self.data.shape[imax[1]]
        slices = self.data.shape[ax] * self.sliceDensity
        r = list(range(slices))
        if d == -1:
            r = r[::-1]
            
        glBegin(GL_QUADS)
        tzVals = np.linspace(nudge[ax], 1.0-nudge[ax], slices)
        vzVals = np.linspace(0, self.data.shape[ax], slices)
        for i in r:
            z = tzVals[i]
            w = vzVals[i]
            
            tp[0][ax] = z
            tp[1][ax] = z
            tp[2][ax] = z
            tp[3][ax] = z
            
            vp[0][ax] = w
            vp[1][ax] = w
            vp[2][ax] = w
            vp[3][ax] = w
            
            glTexCoord3f(*tp[0])
            glVertex3f(*vp[0])
            glTexCoord3f(*tp[1])
            glVertex3f(*vp[1])
            glTexCoord3f(*tp[2])
            glVertex3f(*vp[2])
            glTexCoord3f(*tp[3])
            glVertex3f(*vp[3])
        glEnd()