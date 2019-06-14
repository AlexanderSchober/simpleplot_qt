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
from OpenGL.GL  import *

from ...pyqtgraph           import pyqtgraph    as pg
from ...pyqtgraph.pyqtgraph import opengl       as gl

from ..plot_geometries.surfaces   import QuadSurface
from ..plot_geometries.points     import Point
from ..plot_geometries.shaders    import ShaderConstructor

from ...model.node   import SessionNode

class VolumePlot(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, vol = None, **kwargs):
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
        self._vol   = deepcopy(vol)

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
        self.parameters['Volume']       = [[False]]
        self.parameters['Colors']       = [[
                [0.,1.,1., 0.00],
                [0.,0.,1., 0.45],
                [0.,1.,0., 0.50],
                [1.,0.,0., 0.30],
                [0.,1.,0., 0.00]]]
        self.parameters['Positions']    = [[0,0.45,0.5,0.65,1.]]

        for key in kwargs.keys():
            self.parameters[key][0] = kwargs[key]

        self._generateColorMaps()

        #isosurface
        self.parameters['Iso surface']   = [[True]]
        self.parameters['Iso color']     = [[QtGui.QColor('blue')]]
        self.parameters['Iso value']     = [[0.2]]

    def getParameter(self, name):
        '''
        Returns the value of the parameter requested
        '''
        return self.parameters[name][0]

    def _generateColorMaps(self):
        '''
        Generate the colormaps on the fly 
        depending on the input
        '''
        self.color_map = pg.ColorMap(
            np.array(self.getParameter('Positions')),
            np.array(np.array(self.getParameter('Colors'))*255, dtype=np.ubyte),
            )


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
        if 'data' in kwargs.keys():
            self.z_data = kwargs['data']

        if hasattr(self, 'draw_items'):
            
            #find the surface
            volume = None
            for draw_item in self.draw_items:
                if isinstance(draw_item, gl.GLVolumeItem):
                    volume = draw_item

            #if we have a surface
            if self.getParameter('Volume')[0]:

                #if not present draw it
                if volume == None:
                    if self._mode == '3D':
                        self._drawGLVolume()

                    for draw_item in self.draw_items:
                        if isinstance(draw_item, gl.GLVolumeItem):
                            volume = draw_item

                #update if 3D
                elif self._mode == '3D':
                    volume.setData(self._getVolumeColor())

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(draw_item, gl.GLVolumeItem):
                        if self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                        del self.draw_items[i]

            #find the isosurface
            isosurface = None
            for draw_item in self.draw_items:
                if isinstance(draw_item, gl.GLMeshItem):
                    isosurface = draw_item

            #if we have a surface
            if self.getParameter('Iso surface')[0]:

                #if not present draw it
                if isosurface == None:
                    if self._mode == '3D':
                        self._drawGLIsoSurface()

                    for draw_item in self.draw_items:
                        if isinstance(draw_item, gl.GLMeshItem):
                            isosurface = draw_item

                #update if 3D
                elif self._mode == '3D':
                    vertices, faces = self._getIsoSurface()
                    kwargs = {'vertexes':vertices, 'faces':faces}
                    isosurface.setMeshData(**kwargs)

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(draw_item, gl.GLMeshItem):
                        if self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                        del self.draw_items[i]

        else:
            if self._mode == '3D':
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
        kwargs['x']  = self.x_data
        kwargs['y']  = self.y_data
        kwargs['z']  = self.z_data
        kwargs['sliceDensity']  = 1
        kwargs['smooth']        = True
        self.draw_items.append(CustomGLVolumeItem(self._getVolumeColor(),**kwargs))
        self.default_target.view.addItem(self.draw_items[-1])

    def _getVolumeColor(self):
        '''
        Small function to ease the creation of the 
        color data map for the volume generation
        '''
        self._vol -= np.amin(self._vol)
        self._vol /= np.amax(self._vol)
        colors = self.color_map.map(self._vol)
        return colors

    def updateVolumeColor(self):
        '''
        Reprocesses the isosurface
        '''
        self._generateColorMaps()
        for draw_item in self.draw_items:
            if isinstance(draw_item, gl.GLVolumeItem):
                draw_item.setData(self._getVolumeColor())

    def _drawGLIsoSurface(self):
        '''
        Draw the Isocurves in opengl.
        '''
        vertices, faces = self._getIsoSurface()

        kwargs = {}
        kwargs['vertexes']  = vertices
        kwargs['faces']     = faces
        kwargs['smooth']    = False
        kwargs['drawEdges'] = False
        kwargs['color']     = self.getParameter('Iso color')[0]
        kwargs['shader']    = 'viewNormalColor'#self.shader_constructor.getShader('height')
        kwargs['glOptions'] = 'opaque'

        self.draw_items.append(gl.GLMeshItem(**kwargs))
        self.default_target.view.addItem(self.draw_items[-1])

    def _getIsoSurface(self):
        '''
        Get the vertices and faces to be set to the 
        Meshitem
        '''
        self._vol -= np.amin(self._vol)
        self._vol /= np.amax(self._vol)
        vertices, faces = pg.isosurface(self._vol, self.getParameter('Iso value')[0])

        offset = np.array([
            np.amin(self.x_data), 
            np.amin(self.y_data), 
            np.amin(self.z_data)])

        mult   = np.array([
            np.amax(self.x_data) - np.amin(self.x_data),
            np.amax(self.y_data) - np.amin(self.y_data),
            np.amax(self.z_data) - np.amin(self.z_data)])

        vertices[:] = vertices[:] / mult + offset
        return vertices,faces

    def updateIsoSurface(self):
        '''
        Reprocesses the isosurface
        '''
        for draw_item in self.draw_items:
            if isinstance(draw_item, gl.GLMeshItem):
                vertices, faces = self._getIsoSurface()
                kwargs = {'vertexes':vertices, 'faces':faces}
                draw_item.setMeshData(**kwargs)

    def updateIsoColor(self):
        '''
        Reprocesses the isosurface
        '''
        for draw_item in self.draw_items:
            if isinstance(draw_item, gl.GLMeshItem):
                draw_item.setColor(self.getParameter('Iso color')[0])

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
        
class CustomGLVolumeItem(gl.GLVolumeItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    
    Displays volumetric data. 
    """
    
    def __init__(self, data, x = None, y = None, z = None , sliceDensity=1, smooth=True, glOptions='translucent'):
        """
        ==============  =======================================================================================
        **Arguments:**
        data            Volume data to be rendered. *Must* be 4D numpy array (x, y, z, RGBA) with dtype=ubyte.
        sliceDensity    Density of slices to render through the volume. A value of 1 means one slice per voxel.
        smooth          (bool) If True, the volume slices are rendered with linear interpolation 
        ==============  =======================================================================================
        """
        gl.GLVolumeItem.__init__(self, data, sliceDensity=1, smooth=True, glOptions='translucent')
        self.x = x
        self.y = y
        self.z = z

    def drawVolume(self, ax, d):
        '''
        Draw the volume in the referential
        '''
        N = 5
        
        imax = [0,1,2]
        dim  = [self.x, self.y, self.z]
        imax.remove(ax)
        
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
        
        vp[0][imax[0]] = np.amin(dim[imax[0]])
        vp[0][imax[1]] = np.amin(dim[imax[1]])
        vp[1][imax[0]] = (np.amax(dim[imax[0]]) - np.amin(dim[imax[0]])) + np.amin(dim[imax[0]])
        vp[1][imax[1]] = np.amin(dim[imax[1]])
        vp[2][imax[0]] = (np.amax(dim[imax[0]]) - np.amin(dim[imax[0]])) + np.amin(dim[imax[0]])
        vp[2][imax[1]] = (np.amax(dim[imax[1]]) - np.amin(dim[imax[1]])) + np.amin(dim[imax[1]])
        vp[3][imax[0]] = np.amin(dim[imax[0]])
        vp[3][imax[1]] = (np.amax(dim[imax[1]]) - np.amin(dim[imax[1]])) + np.amin(dim[imax[1]])

        slices = self.data.shape[ax] * self.sliceDensity
        r = list(range(slices))
        if d == -1:
            r = r[::-1]
            
        glBegin(GL_QUADS)
        tzVals = np.linspace(nudge[ax], 1.0-nudge[ax], slices)
        vzVals = np.linspace(np.amin(dim[ax]), np.amax(dim[ax]), slices)
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

    def paint(self):
        '''
        Paint the elements necessary depending
        on the camera position
        '''
        if self.data is None:
            return
        
        if self._needUpload:
            self._uploadData()
        
        self.setupGLState()
        
        glEnable(GL_TEXTURE_3D)
        glBindTexture(GL_TEXTURE_3D, self.texture)
        
        glColor4f(1,1,1,1)

        view = self.view()
        dim  = [self.x, self.y, self.z]
        center = QtGui.QVector3D(*[(np.amax(x)-np.amin(x)) /2. + np.amin(x) for x in dim])
        cam = self.mapFromParent(view.cameraPosition()) - center
        
        cam = np.array([cam.x(), cam.y(), cam.z()])
        ax = np.argmax(abs(cam))
        d = 1 if cam[ax] > 0 else -1
        glCallList(self.lists[(ax,d)])  ## draw axes
        glDisable(GL_TEXTURE_3D)

        