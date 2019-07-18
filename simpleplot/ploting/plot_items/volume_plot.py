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

class VolumePlot(ParameterHandler): 
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
        ParameterHandler.__init__(self, 'Volume')
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
            'Draw smooth', True, 
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Slice density', 1, 
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'OpenGl mode', 'translucent',
            choices = ['translucent', 'opaque', 'additive'],
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Data range', [False, 0., 1.],#,False, ''],
            names  = ['Constrain','min', 'max'],#,'Cut outs', 'values'],
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'X range', [False, 0., 1.,False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Y range', [False, 0., 1.,False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
            tags   = ['3D'],
            method = self.refresh)
        self.addParameter(
            'Z range', [False, 0., 1.,False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
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
                volume = None
                for draw_item in self.draw_items:
                    if isinstance(draw_item, CustomGLVolumeItem) :
                        volume = draw_item

                if self._mode == '3D':
                    data = self.parent()._plot_data.getData()
                    kwargs = {}
                    kwargs['x']  = data[0]
                    kwargs['y']  = data[1]
                    kwargs['z']  = data[2]
                    kwargs['sliceDensity']  = self['Slice density']
                    kwargs['smooth']        = self['Draw smooth']
                    # kwargs['glOptions']     = self['OpenGl mode']
                    for key in kwargs.keys():
                        volume.__setattr__(key, kwargs[key])
                    self._refreshBounds()
                    volume.setGLOptions(self['OpenGl mode'])
                    self.childFromName('Shader').runShader()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i],CustomGLVolumeItem):
                        if self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                del self.draw_items
        else:
            if self['Visible'] and self._mode == '3D':
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
        if self._mode == '3D'and hasattr(self, 'draw_items'):
            positions = self.childFromName('Shader')._positions
            colors    = np.array(self.childFromName('Shader')._colors, dtype=np.uint)*255
            color_map = pg.ColorMap(positions,colors)

            data_range = self['Data range']
            if data_range[0]:
                positions = [
                        positions[i] 
                        if positions[i]>data_range[1] and positions[i]<data_range[2] else None for i in range(len(positions))]
                positions = list(filter((None).__ne__, positions))
                colors = [
                        colors[i] 
                        if positions[i]>=data_range[1] and positions[i]<=data_range[2] else None for i in range(len(positions))]
                colors = list(filter((None).__ne__, colors))

                positions = [data_range[1]]+[data_range[1]+1e-6]+positions+[data_range[2]-1e-6]+[data_range[2]]

                temp_colors = color_map.map([data_range[1], data_range[1]+1e-6, data_range[2]-1e-6,data_range[2]])
                temp_colors[0][3] = 0
                temp_colors[-1][3] = 0
                temp_colors = temp_colors.tolist()
                colors = np.array(temp_colors[0:2]+colors+temp_colors[2:],dtype=np.uint64)
                color_map = pg.ColorMap(positions,colors)

            data    = self.parent()._plot_data.getData()
            colors  = color_map.map(data[4])

            data_limits = [[], [], []]
            targets     = ['X range', 'Y range', 'Z range']

            for j,target in enumerate(targets):
                data_range = self[target]
                if data_range[0]:
                    inside = [
                        i 
                        if data[j][i]>=data_range[1] and data[j][i]<=data_range[2] 
                        else None for i in range(data[j].shape[0])]
                    inside = list(filter((None).__ne__, inside))
                    if len(inside) == 0:
                        data_limits[j] = [0, data[j].shape[0]]
                    else:
                        data_limits[j] = [np.amin(inside), np.amax(inside)]
                else:
                    data_limits[j] = [0, data[j].shape[0]]

            colors_temp = np.zeros(colors.shape)
            colors_temp[
                data_limits[0][0]:data_limits[0][1],
                data_limits[1][0]:data_limits[1][1],
                data_limits[2][0]:data_limits[2][1]] = colors[
                data_limits[0][0]:data_limits[0][1],
                data_limits[1][0]:data_limits[1][1],
                data_limits[2][0]:data_limits[2][1]]
            colors = colors_temp

            colors_temp = np.zeros(colors.shape)
            for j,target in enumerate(targets):
                data_range = self[target]
                if data_range[3] and not data_range[4] == '':
                    points = sorted([float(e) for e in data_range[4].split(',')])
                else:
                    continue
                if not len(points)%2 == 0 or len(points) == 0 :
                    continue
                for l in range(int(len(points)/2)):
                    if points[2*l] < data_range[1]:
                        points[2*l] = data_range[1]
                    if points[2*l] > data_range[2]:
                        points[2*l] = data_range[2]

                    if points[2*l+1] < data_range[1]:
                        points[2*l+1] = data_range[1]
                    if points[2*l+1] > data_range[2]:
                        points[2*l+1] = data_range[2]
                        
                    inside = [
                        i 
                        if data[j][i]>=points[2*l] and data[j][i]<=points[2*l+1] 
                        else None for i in range(data[j].shape[0])]
                        
                    inside = list(filter((None).__ne__, inside))
                    if len(inside) == 0:
                        continue
                    cut_out = [np.amin(inside), np.amax(inside)]
                    if j == 0:
                        colors[cut_out[0]:cut_out[1],:,:,3] = 0
                    elif j == 1:
                        colors[:,cut_out[0]:cut_out[1],:,3] = 0                    
                    elif j == 2:
                        colors[:,:,cut_out[0]:cut_out[1],3] = 0

            self.draw_items[0].setData(colors)
            

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
            data = self.parent()._plot_data.getData()
            kwargs = {}
            kwargs['x']  = data[0]
            kwargs['y']  = data[1]
            kwargs['z']  = data[2]
            kwargs['sliceDensity']  = self['Slice density']
            kwargs['smooth']        = self['Draw smooth']
            kwargs['glOptions']     = self['OpenGl mode']
            self.draw_items.append(CustomGLVolumeItem(None,**kwargs))
            self.draw_items[-1].setTransform(self.parent().transformer.getTransform())
            self.default_target.view.addItem(self.draw_items[-1])
            self._refreshBounds()
            self.childFromName('Shader').runShader()

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)


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

        
