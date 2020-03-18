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
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************

import numpy as np
from .plot_data import PlotData

from ..plot_geometries.surfaces import QuadSurface
from ..plot_geometries.points   import Point
from ..plot_geometries.shaders  import ShaderConstructor
from ...pyqtgraph.pyqtgraph     import functions

from ...models.session_node   import SessionNode

class BarData(PlotData, SessionNode): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self, **kwargs):
        PlotData.__init__(self, **kwargs) 
        SessionNode.__init__(self,'Data')

        self._axes = ['x','y','upper', 'lower']
        self._data = [None, None, None, None]
        self._bounds = [[0,1],[0,1],[0,1],[0,1]]
        self._buffer = {}

    def setData(self, **kwargs):
        '''
        set the local data manually even after
        initialization of the class
        '''
        elements = [None, None, None, None]
        changed  = [False, False, False, False]

        for i,value in enumerate(self._axes):
            if value in kwargs.keys():
                if isinstance(kwargs[value],np.ndarray) or isinstance(kwargs[value],list):
                    elements[i] = np.array(kwargs[value])
                    changed[self._axes.index(value)] = True

        if elements[self._axes.index('upper')] is None:
            if not self._data[self._axes.index('upper')] is None:
                elements[self._axes.index('upper')] = self._data[self._axes.index('upper')]  
            else:
                elements[self._axes.index('upper')] = np.ones((5,5))
                changed[self._axes.index('upper')] = True

        if elements[self._axes.index('lower')] is None:
            if not self._data[self._axes.index('lower')] is None:
                elements[self._axes.index('lower')] = self._data[self._axes.index('lower')]  
            else:
                elements[self._axes.index('lower')] = np.zeros(elements[self._axes.index('upper')].shape)
                changed[self._axes.index('lower')] = True

        if elements[self._axes.index('x')] is None:
            if not self._data[self._axes.index('x')] is None:
                elements[self._axes.index('x')] = self._data[self._axes.index('x')]  
            else:
                elements[self._axes.index('x')] = np.arange(elements[self._axes.index('upper')].shape[0])
                changed[self._axes.index('x')] = True

        if elements[self._axes.index('y')] is None:
            if not self._data[self._axes.index('y')] is None:
                elements[self._axes.index('y')] = self._data[self._axes.index('y')]  
            else:
                elements[self._axes.index('y')] = np.arange(elements[self._axes.index('upper')].shape[1])
                changed[self._axes.index('y')] = True

        if self._sanity(elements):
            self._data = elements 
            self._createMesh()
            self._setBounds()

    def _createMesh(self,width_x = 0.1, width_y = 0.1):
        '''
        This creates the mesh elements in
        a numpy array
        '''
        vertices    = np.zeros((self._data[0].shape[0]*self._data[1].shape[0]*8, 3))
        faces       = np.zeros((self._data[0].shape[0]*self._data[1].shape[0]*12, 3),  dtype='uint')

        xx, yy          = np.meshgrid(self._data[0], self._data[1])
        reshaped_x      = xx.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_y      = yy.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_upper  = self._data[2].reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_lower  = self._data[3].reshape(self._data[0].shape[0]*self._data[1].shape[0])

        self._change_index_0 = []
        self._change_index_1 = []

        count = self._data[0].shape[0]*self._data[1].shape[0]
        vertices    = np.zeros((count*8, 3))
        faces       = np.zeros((count*12, 3),  dtype='uint')

        for i in range(count):
            vertices[i*8 + 0] = np.array([reshaped_x[i] - width_x, reshaped_y[i] - width_y, reshaped_lower[i]])
            vertices[i*8 + 1] = np.array([reshaped_x[i] + width_x, reshaped_y[i] - width_y, reshaped_lower[i]])
            vertices[i*8 + 2] = np.array([reshaped_x[i] + width_x, reshaped_y[i] + width_y, reshaped_lower[i]])
            vertices[i*8 + 3] = np.array([reshaped_x[i] - width_x, reshaped_y[i] + width_y, reshaped_lower[i]])
            vertices[i*8 + 4] = np.array([reshaped_x[i] - width_x, reshaped_y[i] - width_y, reshaped_upper[i]])
            vertices[i*8 + 5] = np.array([reshaped_x[i] + width_x, reshaped_y[i] - width_y, reshaped_upper[i]])
            vertices[i*8 + 6] = np.array([reshaped_x[i] + width_x, reshaped_y[i] + width_y, reshaped_upper[i]])
            vertices[i*8 + 7] = np.array([reshaped_x[i] - width_x, reshaped_y[i] + width_y, reshaped_upper[i]])

            self._change_index_0 += [l for l in range(i*8 + 0, i*8 + 5)]
            self._change_index_1 += [l for l in range(i*8 + 4, i*8 + 8)]

            faces[i*12 + 0]  = np.array([i*8 + 0, i*8 + 1, i*8 + 4])
            faces[i*12 + 1]  = np.array([i*8 + 1, i*8 + 4, i*8 + 5])
            faces[i*12 + 2]  = np.array([i*8 + 1, i*8 + 2, i*8 + 5])
            faces[i*12 + 3]  = np.array([i*8 + 2, i*8 + 5, i*8 + 6])
            faces[i*12 + 4]  = np.array([i*8 + 2, i*8 + 3, i*8 + 6])
            faces[i*12 + 5]  = np.array([i*8 + 3, i*8 + 6, i*8 + 7])
            faces[i*12 + 6]  = np.array([i*8 + 3, i*8 + 0, i*8 + 7])
            faces[i*12 + 7]  = np.array([i*8 + 0, i*8 + 7, i*8 + 4])
            faces[i*12 + 8]  = np.array([i*8 + 0, i*8 + 1, i*8 + 2])
            faces[i*12 + 9]  = np.array([i*8 + 0, i*8 + 3, i*8 + 2])
            faces[i*12 + 10] = np.array([i*8 + 4, i*8 + 5, i*8 + 6])
            faces[i*12 + 11] = np.array([i*8 + 4, i*8 + 7, i*8 + 6])

        self._vertices = vertices
        self._faces    = faces
        
    def getMesh(self, width_x = 0.1, width_y = 0.1):
        '''
        Provide the mesh of the data
        '''
        xx, yy      = np.meshgrid(self._data[0], self._data[1])

        reshaped_x  = xx.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_y  = yy.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_upper = np.repeat(self._data[2].reshape(self._data[0].shape[0]*self._data[1].shape[0]), 8)
        reshaped_lower = np.repeat(self._data[3].reshape(self._data[0].shape[0]*self._data[1].shape[0]), 8)

        self._vertices[[j*8+0 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
        self._vertices[[j*8+0 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

        self._vertices[[j*8+1 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
        self._vertices[[j*8+1 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

        self._vertices[[j*8+2 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
        self._vertices[[j*8+2 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

        self._vertices[[j*8+3 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
        self._vertices[[j*8+3 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

        self._vertices[[j*8+4 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
        self._vertices[[j*8+4 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

        self._vertices[[j*8+5 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
        self._vertices[[j*8+5 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] - width_y

        self._vertices[[j*8+6 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] + width_x
        self._vertices[[j*8+6 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

        self._vertices[[j*8+7 for j in range(reshaped_x.shape[0])], 0] = reshaped_x[:] - width_x
        self._vertices[[j*8+7 for j in range(reshaped_x.shape[0])], 1] = reshaped_y[:] + width_y

        self._vertices[self._change_index_0,2] = reshaped_lower[self._change_index_0]
        self._vertices[self._change_index_1,2] = reshaped_upper[self._change_index_1] 

        return self._vertices, self._faces

    def getData(self):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        return self._data

    def getBounds(self):
        '''
        returns the bounds
        '''
        return self._bounds

    def getBoundingBox(self):
        '''
        Returns the x,y,z isocurve position fo the given
        level omn the present data
        '''
        return self._boundingBox

    def getDrawBounds(self):
        '''
        Provide the bounds that are really 
        visible on the current figure
        '''
        bounds = self.getBounds()
        points = [
            [bounds[0][0], bounds[1][0], bounds[2][0]],
            [bounds[0][1], bounds[1][0], bounds[2][0]],
            [bounds[0][0], bounds[1][1], bounds[2][0]],
            [bounds[0][1], bounds[1][1], bounds[2][0]],
            [bounds[0][0], bounds[1][0], bounds[2][1]],
            [bounds[0][1], bounds[1][0], bounds[2][1]],
            [bounds[0][0], bounds[1][1], bounds[2][1]],
            [bounds[0][1], bounds[1][1], bounds[2][1]]
        ]

        for i in range(len(points)):
            points[i] = self.parent().transformer.transformPoint(np.array(points[i]))

        points = np.array(points)

        return [
            [np.amin(points[:,0]), np.amax(points[:,0])],
            [np.amin(points[:,1]), np.amax(points[:,1])],
            [np.amin(points[:,2]), np.amax(points[:,2])]]

    def _sanity(self, elements):
        '''
        Check that the data makes sense in 
        '''
        if not elements[self._axes.index('x')].shape[0] == elements[self._axes.index('upper')].shape[0]:
            return False
        if not elements[self._axes.index('y')].shape[0] == elements[self._axes.index('upper')].shape[1]:
            return False
        return True

    def _setBounds(self):
        '''
        returns the bounds of the set datastructure
        '''
        bounds = []
        for element in self._data:
            bounds.append([np.amin(element), np.amax(element)])
            
        self._bounds = [bounds[0], bounds[1], [bounds[3][0] , bounds[2][1]]]
            
    def _setBoundingBox(self):
        '''
        Update the topography of the surface
        '''
        bounds = self._bounds

        bounding_box = np.array([
            #top and bottom
            [
                [bounds[0][0], bounds[1][0], bounds[2][0]],
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][0], bounds[1][1], bounds[2][0]]],
            [
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][0], bounds[1][1], bounds[2][0]],
                [bounds[0][1], bounds[1][1], bounds[2][0]]],
            [
                [bounds[0][0], bounds[1][0], bounds[2][1]],
                [bounds[0][1], bounds[1][0], bounds[2][1]],
                [bounds[0][0], bounds[1][1], bounds[2][1]]],
            [
                [bounds[0][1], bounds[1][0], bounds[2][1]],
                [bounds[0][0], bounds[1][1], bounds[2][1]],
                [bounds[0][1], bounds[1][1], bounds[2][1]]],

            #front back
            [
                [bounds[0][0], bounds[1][0], bounds[2][0]],
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][0], bounds[1][0], bounds[2][1]]],
            [
                [bounds[0][0], bounds[1][0], bounds[2][1]],
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][1], bounds[1][0], bounds[2][1]]],
            [
                [bounds[0][0], bounds[1][1], bounds[2][0]],
                [bounds[0][1], bounds[1][1], bounds[2][0]],
                [bounds[0][0], bounds[1][1], bounds[2][1]]],
            [
                [bounds[0][0], bounds[1][1], bounds[2][1]],
                [bounds[0][1], bounds[1][1], bounds[2][0]],
                [bounds[0][1], bounds[1][1], bounds[2][1]]],
                
            #left right
            [
                [bounds[0][0], bounds[1][0], bounds[2][0]],
                [bounds[0][0], bounds[1][1], bounds[2][0]],
                [bounds[0][0], bounds[1][1], bounds[2][1]]],
            [
                [bounds[0][0], bounds[1][1], bounds[2][1]],
                [bounds[0][0], bounds[1][0], bounds[2][0]],
                [bounds[0][0], bounds[1][0], bounds[2][1]]],
            [
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][1], bounds[1][1], bounds[2][0]],
                [bounds[0][1], bounds[1][1], bounds[2][1]]],
            [
                [bounds[0][1], bounds[1][1], bounds[2][1]],
                [bounds[0][1], bounds[1][0], bounds[2][0]],
                [bounds[0][1], bounds[1][0], bounds[2][1]]]])

        self._boundingBox = bounding_box