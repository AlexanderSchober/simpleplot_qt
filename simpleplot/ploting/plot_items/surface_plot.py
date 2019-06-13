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

class SurfacePlot(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, **kwargs):
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
        self.initialize(**kwargs)
        self._mode = '2D'
        self.type  = 'Surface'

        self._position = np.array([0,0,0])
        self._scale = np.array([1,1,1])
        self._rotate_angle = np.array([0,0,0])
        self._rotate_axis = np.array([[1,0,0], [0,1,0], [0,0,1]])
        self._pointer = gl.GLMeshItem()

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.parameters = {}

        self.parameters['Surface']    = [[True]]
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

        self.parameters['Isocurve']         = [[False]]
        self.parameters['Levels']           = [[10]]
        self.parameters['Line color grad']  = [[False]]
        self.parameters['Line color']       = [[QtGui.QColor('blue')]]
        self.parameters['Line thickness']   = [[2]]
        self.parameters['Line offset']      = [[0.2]]

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

        if hasattr(self, 'draw_items'):
            
            #find the surface
            surface = None
            for draw_item in self.draw_items:
                if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                    surface = draw_item

            #if we have a surface
            if self.getParameter('Surface')[0]:

                #if not present draw it
                if surface == None:
                    if self._mode == '2D':
                        self.drawSurface()
                    elif self._mode == '3D':
                        self.drawGLSurface()
                    for draw_item in self.draw_items:
                        if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                            surface = draw_item

                #update if 2D
                if self._mode == '2D':
                    surface.setImage(self.z_data)

                #update if 3D
                elif self._mode == '3D':
                    self.points[:,2] =  np.transpose(np.array(self.z_data)).reshape(self.z_data.size)[:]
                    kwargs = {}
                    kwargs['vertexes']  = self.points
                    kwargs['faces']     = self.vertices
                    surface.setMeshData(**kwargs)

                    self.shader_constructor = ShaderConstructor()
                    if self.shader_parameters['Bounds z'][0][0] == True:
                        self.shader_constructor.setRange(
                            np.amin(self.z_data), np.amax(self.z_data))
                    else:
                        self.shader_constructor.setRange(
                            self.shader_parameters['Bounds z'][0][1], 
                            self.shader_parameters['Bounds z'][0][2])

                    self.shader_constructor.setColors(
                        self.parameters['Colors'][0],
                        self.parameters['Positions'][0])

                    surface.setShader(self.shader_constructor.getShader('height'))

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.ImageItem) or isinstance(self.draw_items[i], gl.GLMeshItem):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                        del self.draw_items[i]


            #find the surface
            isocurves = []
            for draw_item in self.draw_items:
                if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                    isocurves.append(draw_item)

            #if we have a surface
            if self.getParameter('Isocurve')[0]:

                #if not present draw it
                if len(isocurves) == 0:
                    if self._mode == '2D':
                        self.drawIsocurves()
                        self.setIsoColor()
                        isocurves = []
                        for draw_item in self.draw_items:
                            if isinstance(draw_item, pg.IsocurveItem):
                                isocurves.append(draw_item)
                #update if 2D
                if self._mode == '2D':
                    for i in range(self.getParameter('Levels')[0]):
                        if isinstance(self.z_data, np.ndarray):
                            level = (
                                (np.amax(self.z_data) - np.amin(self.z_data))/self.getParameter('Levels')[0] * i 
                                + np.amin(self.z_data))
                        else:
                            level = 0
                        isocurves[i].setData(self.z_data, level = level)

                #update if 3D
                elif self._mode == '3D':
                    for i in range(len(self.draw_items))[::-1]:
                        if isinstance(self.draw_items[i], list):
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                            del self.draw_items[i]
                    self.drawGLIsocurves()
                    self.setIsoColor()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.IsocurveItem) or isinstance(self.draw_items[i], list):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                        del self.draw_items[i]

        else:
            if self._mode == '2D':
                self.draw()
            elif self._mode == '3D':
                self.drawGL()

        if self._mode == '3D':
            self.translate(temp_position)
            self.scale(temp_scale)
            self.rotate(temp_angle, temp_axis)

    def setIsoColor(self, color = None):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        if not color == None:
            self.parameters['Line color'] = [[color]]
            
        isocurves = []
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                isocurves.append(draw_item)

        lookUpTable = self.color_map.getLookupTable(nPts = self.getParameter('Levels')[0], alpha = False)

        if not len(isocurves) == 0:
            for i in range(self.getParameter('Levels')[0]):
                if isinstance(self.z_data, np.ndarray):
                    level = (
                        (np.amax(self.z_data) - np.amin(self.z_data))/self.getParameter('Levels')[0] * i 
                        + np.amin(self.z_data))
                else:
                    level = 0
            
                if self._mode == '2D':
                    if self.getParameter('Line color grad')[0]:
                        pen = pg.mkPen({
                            'color': QtGui.QColor(*lookUpTable[i].tolist()), 
                            'width': self.getParameter('Line thickness')[0]})
                    else:
                        pen = pg.mkPen({
                            'color': self.getParameter('Line color')[0], 
                            'width': self.getParameter('Line thickness')[0]})   

                    isocurves[i].setPen(pen)

                elif self._mode == '3D':
                    if self.getParameter('Line color grad')[0]:
                        for curve in isocurves[i]:
                            curve.setData(color = (np.array(QtGui.QColor(*lookUpTable[i].tolist()).getRgb())/255.).tolist())
                    else:
                        for curve in isocurves[i]:
                            curve.setData(color =  (np.array(self.getParameter('Line color')[0].getRgb())/255.).tolist()) 

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

        if self._mode == '2D' and not surface == None:
            surface.setLookupTable(
                self.color_map.getLookupTable(0.0, 1.0, alpha = False))

        elif self._mode == '3D' and not surface == None:
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

    def buildVerticeMap(self):
        '''
        build the vertices and positions locally from
        the given axes
        '''
        border_points = [
            Point('Point_0', np.amin(self.x_data), np.amin(self.y_data), 0),
            Point('Point_1', np.amax(self.x_data), np.amin(self.y_data), 0),
            Point('Point_2', np.amax(self.x_data), np.amax(self.y_data), 0),
            Point('Point_3', np.amin(self.x_data), np.amax(self.y_data), 0)]
        
        self.shapeBuilder = QuadSurface(
            name = self.parameters['Name'], 
            border_points=border_points)

        self.shapeBuilder.setTopography(
            self.z_data, 
            self.parameters['Colors'])

        self.points     = self.shapeBuilder.getVertices()
        self.vertices   = self.shapeBuilder.getFaces()

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            
        self.draw_items = []
            
        if self.getParameter('Surface')[0]:
            self.drawSurface()

        if self.getParameter('Isocurve')[0]:
            self.drawIsocurves()

    def drawSurface(self):
        '''
        Draw the Isocurves in opengl.
        '''
        self.draw_items.append(pg.ImageItem())
        self.draw_items[-1].setLookupTable(self.color_map.getLookupTable(0.0, 1.0, alpha = False))
        self.draw_items[-1].setImage(self.z_data)
        self.default_target.draw_surface.addItem(self.draw_items[-1])

    def drawIsocurves(self):
        '''
        Draw the Isocurves in opengl.
        '''
        if self.getParameter('Isocurve')[0]:
            for i in range(self.getParameter('Levels')[0]):
                pen = pg.mkPen({
                    'color': self.getParameter('Line color')[0], 
                    'width': self.getParameter('Line thickness')[0]})
                if isinstance(self.z_data, np.ndarray):
                    level = (np.amax(self.z_data) - np.amin(self.z_data)) * i + np.amin(self.z_data)
                else:
                    level = 0
                self.draw_items.append(pg.IsocurveItem(data = self.z_data, level = level, pen = pen))
                self.default_target.draw_surface.addItem(self.draw_items[-1])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []
            
        if self.getParameter('Surface')[0]:
            self.drawGLSurface()

        if self.getParameter('Isocurve')[0]:
            self.drawGLIsocurves()

        self.default_target.view.addItem(self._pointer)

    def drawGLSurface(self):
        '''
        Draw the Isocurves in opengl.
        '''
        # to do cache 
        self.shader_constructor = ShaderConstructor()
        if self.shader_parameters['Bounds z'][0][0] == True:
            self.shader_constructor.setRange(
                np.amin(self.z_data)-1.0e-6, np.amax(self.z_data)+1.0e-6)
        else:
            self.shader_constructor.setRange(
                self.shader_parameters['Bounds z'][0][1]-1.0e-6, 
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
        kwargs['drawEdges'] = True
        kwargs['shader']    = self.shader_constructor.getShader('height')
        self.draw_items.append(gl.GLMeshItem(**kwargs))

        self.default_target.view.addItem(self.draw_items[-1])


    def drawGLIsocurves(self):
        '''
        Draw the Isocurves in opengl.
        '''
        x_min = np.amin(self.x_data)
        x_max = np.amax(self.x_data)
        x_fac = (x_max - x_min)

        y_min = np.amin(self.y_data)
        y_max = np.amax(self.y_data)
        y_fac = (y_max - y_min)

        for i in range(self.getParameter('Levels')[0]):
            if isinstance(self.z_data, np.ndarray):
                level = (
                    (np.amax(self.z_data) - np.amin(self.z_data))/self.getParameter('Levels')[0] * i 
                    + np.amin(self.z_data))
            else:
                level = 0

            iso_curves = pg.fn.isocurve(self.z_data, level,  connected = True)

            gl_iso_curve = []
            for curve in iso_curves:
                gl_iso_curve.append(
                    gl.GLLinePlotItem(
                        pos=np.vstack([
                            [(item[0]-0.5) / (self.z_data.shape[0]) * x_fac + x_min for item in curve],
                            [(item[1]-0.5) / (self.z_data.shape[1]) * y_fac + y_min for item in curve],
                            [level+self.getParameter('Line offset')[0] for item in curve]]).transpose(),
                        color = self.getParameter('Line color')[0],
                        width = self.getParameter('Line thickness')[0],
                        mode = 'line_strip'))
                gl_iso_curve[-1].setGLOptions('translucent')
                self.default_target.view.addItem(gl_iso_curve[-1])

            self.draw_items.append(list(gl_iso_curve))

    def removeItems(self):
        '''
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)

    def processRay(self, ray):
        '''
        try to process the ray intersection
        '''
        maxima = [
            np.amax(self.x_data),
            np.amax(self.y_data),
            np.amax(self.z_data)]

        minima = [
            np.amin(self.x_data),
            np.amin(self.y_data),
            np.amin(self.z_data)]

        bounding_box = np.array([
            #top and bottom
            [
                [minima[0], minima[1], minima[2]],
                [maxima[0], minima[1], minima[2]],
                [minima[0], maxima[1], minima[2]]],
            [
                [maxima[0], minima[1], minima[2]],
                [minima[0], maxima[1], minima[2]],
                [maxima[0], maxima[1], minima[2]]],
            [
                [minima[0], minima[1], maxima[2]],
                [maxima[0], minima[1], maxima[2]],
                [minima[0], maxima[1], maxima[2]]],
            [
                [maxima[0], minima[1], maxima[2]],
                [minima[0], maxima[1], maxima[2]],
                [maxima[0], maxima[1], maxima[2]]],

            #front back
            [
                [minima[0], minima[1], minima[2]],
                [maxima[0], minima[1], minima[2]],
                [minima[0], minima[1], maxima[2]]],
            [
                [minima[0], minima[1], maxima[2]],
                [maxima[0], minima[1], minima[2]],
                [maxima[0], minima[1], maxima[2]]],
            [
                [minima[0], maxima[1], minima[2]],
                [maxima[0], maxima[1], minima[2]],
                [minima[0], maxima[1], maxima[2]]],
            [
                [minima[0], maxima[1], maxima[2]],
                [maxima[0], maxima[1], minima[2]],
                [maxima[0], maxima[1], maxima[2]]],
            #left right
            [
                [minima[0], minima[1], minima[2]],
                [minima[0], maxima[1], minima[2]],
                [minima[0], maxima[1], maxima[2]]],
            [
                [minima[0], maxima[1], maxima[2]],
                [minima[0], minima[1], minima[2]],
                [minima[0], minima[1], maxima[2]]],
            [
                [maxima[0], minima[1], minima[2]],
                [maxima[0], maxima[1], minima[2]],
                [maxima[0], maxima[1], maxima[2]]],
            [
                [maxima[0], maxima[1], maxima[2]],
                [maxima[0], minima[1], minima[2]],
                [maxima[0], minima[1], maxima[2]]]])
        
        # print(np.reshape(bounding_box, (bounding_box.shape[0]*bounding_box.shape[1],3)))
        # print(np.reshape(np.arange(0,bounding_box.shape[0]*bounding_box.shape[1]),(int((bounding_box.shape[0]*bounding_box.shape[1])/3),3)))
        # self._pointer.setMeshData(
        #     drawEdges = True,
        #     vertexes = np.reshape(bounding_box, (bounding_box.shape[0]*bounding_box.shape[1],3)), 
        #     faces = np.reshape(np.arange(0,bounding_box.shape[0]*bounding_box.shape[1]),(int((bounding_box.shape[0]*bounding_box.shape[1])/3),3)))

        coordinates = []
        for i in range(bounding_box.shape[0]):
            val  = self.rayTriangleIntersection(
                ray[0], ray[1], [
                    bounding_box[i,0],
                    bounding_box[i,1],
                    bounding_box[i,2]])
            if val[0]:
                coordinates.append(val[1])

        if len(coordinates) < 2:
            return None

        coordinates = np.array(coordinates)
        x_step = self.x_data[1] - self.x_data[0]
        y_step = self.y_data[1] - self.y_data[0]
        maxima = [
            np.amax(coordinates[:,0])+x_step,
            np.amax(coordinates[:,1])+y_step,
            np.amax(coordinates[:,2])]

        minima = [
            np.amin(coordinates[:,0])-x_step,
            np.amin(coordinates[:,1])-y_step,
            np.amin(coordinates[:,2])]

        index_x = np.argwhere((self.x_data > minima[0])&((self.x_data < maxima[0])))[:,0]
        index_y = np.argwhere((self.y_data > minima[1])&((self.y_data < maxima[1])))[:,0]

        if index_x.shape[0] < 2:
            val = np.argmin(np.abs(self.x_data - minima[0]))
            index_x = np.arange(val-1, val + 1)
        if index_y.shape[0] < 2:
            val = np.argmin(np.abs(self.y_data - minima[1]))
            index_y = np.arange(val-1, val + 1)

        flat_x_2 = np.arange(index_x[0]*2-2, index_x[-1]*2+2)
        flat_y_1 = np.arange(index_y[0]-1, index_y[-1]+1)

        flat_x_2 = flat_x_2[np.where(flat_x_2>=0)]
        flat_x_2 = flat_x_2[np.where(flat_x_2<self.x_data.shape[0]*2)]
        flat_y_1 = flat_y_1[np.where(flat_y_1>=0)]
        flat_y_1 = flat_y_1[np.where(flat_y_1<self.y_data.shape[0])]

        flat_index = np.array([flat_x_2 + e*(self.x_data.shape[0]-1)*2 for e in index_y])
        flat_index = np.reshape(flat_index,(flat_index.shape[0]*flat_index.shape[1]) )
        flat_index = flat_index[np.where(flat_index<self.vertices.shape[0])]
    
        for i,face in enumerate(self.vertices[flat_index]):
            test = self.rayTriangleIntersection(
                ray[0], ray[1], 
                [
                    self.points[face[0]],
                    self.points[face[1]],
                    self.points[face[2]]])

            if test[0]:
                self._pointer.setMeshData(
                    vertexes = np.array([
                        self.points[face[0]],
                        self.points[face[1]],
                        self.points[face[2]]])+np.array([0,0,0.01]), 
                    faces = np.array([[0,1,2]]))
                return test[1]

        return None

    def rayTriangleIntersection(self, ray_near, ray_dir, v123):
        """
        Möller–Trumbore intersection algorithm in pure python
        Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
        """
        v1, v2, v3 = v123
        eps = 0.000000001
        edge1 = v2 - v1
        edge2 = v3 - v1
        p_vec = np.cross(ray_dir, edge2)
        det = edge1.dot(p_vec)
        if abs(det) < eps:
            return False, None
        inv_det = 1. / det
        t_vec = ray_near - v1
        u = t_vec.dot(p_vec) * inv_det
        if u < 0. or u > 1.:
            return False, None
        q_vec = np.cross(t_vec, edge1)
        v = ray_dir.dot(q_vec) * inv_det
        if v < 0. or u + v > 1.:
            return False, None

        t = edge2.dot(q_vec) * inv_det
        if t < eps:
            return False, None

        return True, self.linPlaneCollision([v1,v2,v3], ray_dir, ray_near)

    def linPlaneCollision(self, planePoints, rayDirection, rayPoint, epsilon=1e-6):
    
        planeNormal = np.cross(planePoints[1] - planePoints[0], planePoints[2]- planePoints[0])
        planeNormal = planeNormal/np.linalg.norm(planeNormal)
        ndotu       = planeNormal.dot(rayDirection)

        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")
    
        w = rayPoint - planePoints[0]
        si = -planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + planePoints[0]
        return Psi