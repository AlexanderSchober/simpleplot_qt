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
from scipy.spatial.distance import pdist

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl
from ...pyqtgraph.pyqtgraph.graphicsItems.GradientEditorItem import GradientEditorItem

from ..plot_geometries.shaders      import ShaderConstructor
from ...model.parameter_class       import ParameterHandler 
from ..plot_geometries.transformer  import Transformer

class SurfacePlot(ParameterHandler, Transformer): 
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
        Transformer.__init__(self)
        self.gradient_item = GradientEditorItem()
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        position = [0,0.25,0.5,0.75,1.]
        colors = [
            [0.,1.,1., 1.],
            [0.,0.,1., 1.],
            [0.,1.,0., 1.],
            [1.,0.,0., 1.],
            [0.,1.,0., 1.]]
        state = {'ticks':[[position[i],np.array(colors)[i]*255] for i in range(len(colors))],'mode' : 'rgb'}
        self.gradient_item.restoreState(state)

        self.addParameter(
            'Visible', True, 
            method = self.refresh)
        self.addParameter(
            'Draw faces', True, 
            method = self.refresh)
        self.addParameter(
            'Draw edges', False, 
            method = self.refresh)
        self.addParameter(
            'Draw smooth', True, 
            method = self.refresh)
        self.addParameter(
            'Gradient', self.gradient_item, 
            method = self.setColor)
        self.addParameter(
            'Height range', [True, 0.,1.],
            names = ['automatic', 'min', 'max'],
            method = self.setColor)

        self._setTransformerParameters()
        
    def getParameter(self, name):
        '''
        Returns the value of the parameter requested
        '''
        return self.parameters[name][0]

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        self.unTransform()

        if hasattr(self, 'draw_items'):
            
            #find the surface
            surface = None
            for draw_item in self.draw_items:
                if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                    surface = draw_item

            #if we have a surface
            if self['Visible']:

                #if not present draw it
                if surface == None:
                    if self._mode == '2D':
                        self.draw()
                    elif self._mode == '3D':
                        self.drawGL()
                    for draw_item in self.draw_items:
                        if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                            surface = draw_item

                #update if 2D
                if self._mode == '2D':
                    surface.setImage(self.parent()._plot_data.getData()[2])

                #update if 3D
                elif self._mode == '3D':
                    surface.opts['drawEdges']   = self['Draw edges']
                    surface.opts['drawFaces']   = self['Draw faces']
                    surface.opts['smooth']      = self['Draw smooth']

                    data = self.parent()._plot_data.getMesh()
                    kwargs = {}
                    kwargs['vertexes']  = data[0]
                    kwargs['faces']     = data[1]
                    
                    surface.setMeshData(**kwargs)
                    
                    self.setColor()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.ImageItem) or isinstance(self.draw_items[i], gl.GLMeshItem):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            self.default_target.view.removeItem(self.draw_items[i])
                        del self.draw_items[i]

        self.reTransform()

    def _getColors(self):
        '''
        Use outside of color loop
        '''
        state       = self['Gradient'].saveState()
        positions   = [element[0] for element in state['ticks']]
        colors      = [list(np.array(element[1])/255) for element in state['ticks']]
        colors      = np.array([c for _,c in sorted(zip(positions, colors))])
        positions   = np.array(sorted(positions))
        return colors, positions

    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        colors, positions = self._getColors()

        surface = None
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.ImageItem) or isinstance(draw_item, gl.GLMeshItem):
                surface = draw_item

        if self._mode == '2D' and not surface == None:
            self.color_map = pg.ColorMap(positions,colors*255)
            surface.setLookupTable(self.color_map.getLookupTable(0.0, 1.0, alpha = False))

        elif self._mode == '3D':

            self.shader_constructor = ShaderConstructor()
            if self['Height range'][0] == True:
                self.shader_constructor.setRange(
                    np.amin(self.parent()._plot_data.getData()[2])-1.0e-6, np.amax(self.parent()._plot_data.getData()[2])+1.0e-6)
            else:
                self.shader_constructor.setRange(
                    self['Height range'][1]-1.0e-6, 
                    self['Height range'][2]+1.0e-6)

            self.shader_constructor.setColors(colors, positions)

            if not surface == None:
                surface.setShader(self.shader_constructor.getShader('height'))

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            
        self.draw_items = []
        self.draw_items.append(pg.ImageItem())
        colors, positions = self._getColors()
        self.color_map = pg.ColorMap(positions,colors)
        self.draw_items[-1].setLookupTable(self.color_map.getLookupTable(0.0, 1.0, alpha = False))
        self.draw_items[-1].setImage(self.parent()._plot_data.getData()[2])
        self.default_target.draw_surface.addItem(self.draw_items[-1])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []

        mesh = self.parent()._plot_data.getMesh()
        kwargs = {}
        kwargs['vertexes']  = mesh[0]
        kwargs['faces']     = mesh[1]
        kwargs['smooth']    = self['Draw smooth']
        kwargs['drawFaces'] = self['Draw faces']
        kwargs['drawEdges'] = self['Draw edges']

        self.draw_items.append(gl.GLMeshItem(**kwargs))
        self.default_target.view.addItem(self.draw_items[-1])
        self.setColor()

    def removeItems(self):
        '''
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)

    # def closestPointOnLine(self, a, b, p):
    #     ap = p-a
    #     ab = b-a
    #     result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    #     return np.linalg.norm(result - p)

    # def offprocessRay(self, ray):
    #     '''
    #     try to process the ray intersection
    #     '''

    #     maxima = [
    #         np.amax(self.x_data),
    #         np.amax(self.y_data),
    #         np.amax(self.z_data)]

    #     minima = [
    #         np.amin(self.x_data),    # def closestPointOnLine(self, a, b, p):
    #     ap = p-a
    #     ab = b-a
    #     result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    #     return np.linalg.norm(result - p)
    #         np.amin(self.y_data),    # def closestPointOnLine(self, a, b, p):
    #     ap = p-a
    #     ab = b-a
    #     result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    #     return np.linalg.norm(result - p)
    #         np.amin(self.z_data)]    # def closestPointOnLine(self, a, b, p):
    #     ap = p-a
    #     ab = b-a
    #     result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    #     return np.linalg.norm(result - p)

    #     bounding_box = np.array([    # def closestPointOnLine(self, a, b, p):
    #     ap = p-a
    #     ab = b-a
    #     result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    #     return np.linalg.norm(result - p)
    #         #top and bottom
    #         [
    #             [minima[0], minima[1], minima[2]],
    #             [maxima[0], minima[1], minima[2]],
    #             [minima[0], maxima[1], minima[2]]],
    #         [
    #             [maxima[0], minima[1], minima[2]],
    #             [minima[0], maxima[1], minima[2]],
    #             [maxima[0], maxima[1], minima[2]]],
    #         [
    #             [minima[0], minima[1], maxima[2]],
    #             [maxima[0], minima[1], maxima[2]],
    #             [minima[0], maxima[1], maxima[2]]],
    #         [
    #             [maxima[0], minima[1], maxima[2]],
    #             [minima[0], maxima[1], maxima[2]],
    #             [maxima[0], maxima[1], maxima[2]]],

    #         #front back
    #         [
    #             [minima[0], minima[1], minima[2]],
    #             [maxima[0], minima[1], minima[2]],
    #             [minima[0], minima[1], maxima[2]]],
    #         [
    #             [minima[0], minima[1], maxima[2]],
    #             [maxima[0], minima[1], minima[2]],
    #             [maxima[0], minima[1], maxima[2]]],
    #         [
    #             [minima[0], maxima[1], minima[2]],
    #             [maxima[0], maxima[1], minima[2]],
    #             [minima[0], maxima[1], maxima[2]]],
    #         [
    #             [minima[0], maxima[1], maxima[2]],
    #             [maxima[0], maxima[1], minima[2]],
    #             [maxima[0], maxima[1], maxima[2]]],
    #         #left right
    #         [
    #             [minima[0], minima[1], minima[2]],
    #             [minima[0], maxima[1], minima[2]],
    #             [minima[0], maxima[1], maxima[2]]],
    #         [
    #             [minima[0], maxima[1], maxima[2]],
    #             [minima[0], minima[1], minima[2]],
    #             [minima[0], minima[1], maxima[2]]],
    #         [
    #             [maxima[0], minima[1], minima[2]],
    #             [maxima[0], maxima[1], minima[2]],
    #             [maxima[0], maxima[1], maxima[2]]],
    #         [
    #             [maxima[0], maxima[1], maxima[2]],
    #             [maxima[0], minima[1], minima[2]],
    #             [maxima[0], minima[1], maxima[2]]]])


    #     coordinates = []
    #     for i in range(bounding_box.shape[0]):
    #         val  = self.rayTriangleIntersection(
    #             ray[0], ray[1], [
    #                 bounding_box[i,0],
    #                 bounding_box[i,1],
    #                 bounding_box[i,2]])
    #         if val[0]:
    #             coordinates.append(val[1])

    #     if len(coordinates) < 2:
    #         return None

    #     coordinates = np.array(coordinates)
    #     x_step = self.x_data[1] - self.x_data[0]
    #     y_step = self.y_data[1] - self.y_data[0]
    #     maxima = [
    #         np.amax(coordinates[:,0])+x_step,
    #         np.amax(coordinates[:,1])+y_step,
    #         np.amax(coordinates[:,2])]

    #     minima = [
    #         np.amin(coordinates[:,0])-x_step,
    #         np.amin(coordinates[:,1])-y_step,
    #         np.amin(coordinates[:,2])]

    #     index_x = np.argwhere((self.x_data > minima[0])&((self.x_data < maxima[0])))[:,0]
    #     index_y = np.argwhere((self.y_data > minima[1])&((self.y_data < maxima[1])))[:,0]

    #     if index_x.shape[0] < 2:
    #         val = np.argmin(np.abs(self.x_data - minima[0]))
    #         index_x = np.arange(val-1, val + 1)
    #     if index_y.shape[0] < 2:
    #         val = np.argmin(np.abs(self.y_data - minima[1]))
    #         index_y = np.arange(val-1, val + 1)

    #     flat_x_2 = np.arange(index_x[0]*2-2, index_x[-1]*2+2)
    #     flat_y_1 = np.arange(index_y[0]-1, index_y[-1]+1)

    #     flat_x_2 = flat_x_2[np.where(flat_x_2>=0)]
    #     flat_x_2 = flat_x_2[np.where(flat_x_2<self.x_data.shape[0]*2)]
    #     flat_y_1 = flat_y_1[np.where(flat_y_1>=0)]
    #     flat_y_1 = flat_y_1[np.where(flat_y_1<self.y_data.shape[0])]

    #     flat_index = np.array([flat_x_2 + e*(self.x_data.shape[0]-1)*2 for e in index_y])
    #     flat_index = np.reshape(flat_index,(flat_index.shape[0]*flat_index.shape[1]) )
    #     flat_index = flat_index[np.where(flat_index<self.vertices.shape[0])]
            
    #     points = []
    #     for face in self.vertices[flat_index]:
    #         points.append(face[0])
    #         points.append(face[1])
    #         points.append(face[2])
    #     points = self.points[np.array(list(set(points)))]
        
    #     ray_norm = np.linalg.norm(ray[1] - ray[0])
    #     distance = np.zeros(points.shape[0])

    #     point_vectors = points - ray[0]
    #     for i in range(distance.shape[0]):
    #         distance[i] = self.closestPointOnLine(ray[1], ray[0],points[i])

    #     idx = np.argpartition(distance, 3)
    #     triangle = np.array([
    #             points[idx[0]],
    #             points[idx[1]],
    #             points[idx[2]]])
    #     self._pointer.setMeshData(
    #         vertexes = triangle+np.array([0,0,0.01]), 
    #         faces = np.array([[0,1,2]]))
        
    #     test = self.rayTriangleIntersection(ray[0], ray[1], triangle)

    #     return test[1]

    # def rayTriangleIntersection(self, ray_near, ray_dir, v123):
    #     """
    #     Möller–Trumbore intersection algorithm in pure python
    #     Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    #     """
    #     v1, v2, v3 = v123
    #     eps = 0.000000001
    #     edge1 = v2 - v1
    #     edge2 = v3 - v1
    #     p_vec = np.cross(ray_dir, edge2)
    #     det = edge1.dot(p_vec)
    #     if abs(det) < eps:
    #         return False, None
    #     inv_det = 1. / det
    #     t_vec = ray_near - v1
    #     u = t_vec.dot(p_vec) * inv_det
    #     if u < 0. or u > 1.:
    #         return False, None
    #     q_vec = np.cross(t_vec, edge1)
    #     v = ray_dir.dot(q_vec) * inv_det
    #     if v < 0. or u + v > 1.:
    #         return False, None

    #     t = edge2.dot(q_vec) * inv_det
    #     if t < eps:
    #         return False, None

    #     return True, self.linPlaneCollision([v1,v2,v3], ray_dir, ray_near)

    # def linPlaneCollision(self, planePoints, rayDirection, rayPoint, epsilon=1e-6):
    
    #     planeNormal = np.cross(planePoints[1] - planePoints[0], planePoints[2]- planePoints[0])
    #     planeNormal = planeNormal/np.linalg.norm(planeNormal)
    #     ndotu       = planeNormal.dot(rayDirection)

    #     if abs(ndotu) < epsilon:
    #         raise RuntimeError("no intersection or line is within plane")
    
    #     w = rayPoint - planePoints[0]
    #     si = -planeNormal.dot(w) / ndotu
    #     Psi = w + si * rayDirection + planePoints[0]
    #     return Psi