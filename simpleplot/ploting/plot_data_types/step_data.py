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

from ...model.node   import SessionNode

class StepData(PlotData, SessionNode): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self, **kwargs):
        PlotData.__init__(self, **kwargs) 
        SessionNode.__init__(self,'Data')

        self._axes = ['x','y','z']
        self._data = [None, None, None]

    def setData(self, **kwargs):
        '''
        set the local data manually even after
        initialization of the class
        '''
        elements = [None]*len(self._axes)
        changed  = [False, False, False]

        for i,value in enumerate(self._axes):
            if value in kwargs.keys():
                if isinstance(kwargs[value],np.ndarray) or isinstance(kwargs[value],list):
                    elements[i] = np.array(kwargs[value])
                    changed[self._axes.index(value)] = True

        if elements[self._axes.index('z')] is None:
            if not self._data[self._axes.index('z')] is None:
                elements[self._axes.index('z')] = self._data[self._axes.index('z')]  
            else:
                elements[self._axes.index('z')] = np.zeros((1,1))
                changed[self._axes.index('z')] = True

        if elements[self._axes.index('x')] is None:
            if not self._data[self._axes.index('x')] is None:
                elements[self._axes.index('x')] = self._data[self._axes.index('x')]  
            else:
                elements[self._axes.index('x')] = np.arange(elements[self._axes.index('z')].shape[0])
                changed[self._axes.index('x')] = True

        if elements[self._axes.index('y')] is None:
            if not self._data[self._axes.index('y')] is None:
                elements[self._axes.index('y')] = self._data[self._axes.index('y')]  
            else:
                elements[self._axes.index('y')] = np.arange(elements[self._axes.index('z')].shape[1])
                changed[self._axes.index('y')] = True

        if self._sanity(elements):

            self._data = elements 
            self._setBounds()
            self._setHistogram()

            if self.parent().childFromName('Step')._mode == '3D':
                self.set3D(changed = changed)

    def set3D(self, changed = [True, True, True]):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        if changed[0] or changed[1]:
            self._buildVerticeMap()
        elif changed[2] and not changed[0] and not changed[1]:
            self._updateTopography()
        self._setBoundingBox()

    def getData(self):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        return self._data

    def getHistogram(self, direction = 'z'):
        '''
        Produce the histogram according to the 
        direction selected
        '''
        return self._histogram[self._axes.index(direction)]

    def getBounds(self):
        '''
        returns the bounds
        '''
        return self._bounds

    def getProjection(self, direction, x = 0, y = 0, z = 0):
        '''
        returns the bounds
        '''
        if direction == 'x':
            return [self._data[0], self._data[2][:,np.argmin(np.abs(self._data[1]-y))]]
        elif direction == 'y':
            return [ self._data[2][np.argmin(np.abs(self._data[0]-x)), :], self._data[1]]
        else:
            return [[0], [0]]

    def getMesh(self):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        return [self._vertices, self._faces]

    def getIsocurve(self, level):
        '''
        Returns the x,y,z isocurve position fo the given
        level omn the present data
        '''
        return functions.isocurve(self._data[2], level, connected = True)

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
        if not elements[self._axes.index('x')].shape[0] == elements[self._axes.index('z')].shape[0]:
            return False
        if not elements[self._axes.index('y')].shape[0] == elements[self._axes.index('z')].shape[1]:
            return False
        return True

    def _setHistogram(self):
        '''
        Set the histogram of the data along all 
        axes
        '''
        axis        = [0 for i in range(100)]
        elements    = [0 for i in range(100)]
        factor      = (np.amax(self._data[2]) - np.amin(self._data[2]))/(100-1)
        offset      = np.amin(self._data[2])
        for i in range(len(axis)):
            axis[i] = i*factor + offset
            elements[i] = np.argwhere(
                (self._data[2] > i*factor + offset)
                & (self._data[2] < (i+1)*factor + offset)).shape[0]
            
        self._histogram = [
            [self._data[0], np.sum(self._data[2],axis = 0)],
            [self._data[1], np.sum(self._data[2],axis = 0)],
            [axis, elements]]

    def _setBounds(self):
        '''
        returns the bounds of the set datastructure
        '''
        self._bounds = []
        for element in self._data:
            self._bounds.append([np.amin(element), np.amax(element)])

    def _buildVerticeMap(self):
        '''
        build the vertices and positions locally from
        the given axes
        '''
        vertices    = np.zeros((self._data[0].shape[0]*self._data[1].shape[0]*8, 3))
        faces       = np.zeros((self._data[0].shape[0]*self._data[1].shape[0]*12, 3),  dtype='uint')

        xx, yy          = np.meshgrid(self._data[0], self._data[1])
        reshaped_x      = xx.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_y      = yy.reshape(self._data[0].shape[0]*self._data[1].shape[0])
        reshaped_z      = self._data[2].reshape(self._data[0].shape[0]*self._data[1].shape[0])

        count = self._data[0].shape[0]*self._data[1].shape[0]

        vertices    = np.zeros((count*8, 3))
        faces       = np.zeros((count*6, 3),  dtype='uint')

        width_x = ((np.amax(self._data[0]) - np.amin(self._data[0])) / (self._data[0].shape[0] - 1))/2
        width_y = ((np.amax(self._data[1]) - np.amin(self._data[1])) / (self._data[1].shape[0] - 1))/2

        for i in range(count):
            vertices[i*8 + 0] = np.array([reshaped_x[i] - width_x, reshaped_y[i] - width_y, reshaped_z[i]])
            vertices[i*8 + 1] = np.array([reshaped_x[i] + width_x, reshaped_y[i] - width_y, reshaped_z[i]])
            vertices[i*8 + 2] = np.array([reshaped_x[i] + width_x, reshaped_y[i] + width_y, reshaped_z[i]])
            vertices[i*8 + 3] = np.array([reshaped_x[i] - width_x, reshaped_y[i] + width_y, reshaped_z[i]])

            vertices[i*8 + 4] = np.array([
                reshaped_x[i] + width_x, 
                reshaped_y[i] - width_y, 
                reshaped_z[i+1 if not i%(self._data[0].shape[0]) == self._data[0].shape[0]-1  else i]])

            vertices[i*8 + 5] = np.array([
                reshaped_x[i] + width_x, 
                reshaped_y[i] + width_y, 
                reshaped_z[i+1 if not i%(self._data[0].shape[0]) == self._data[0].shape[0]-1  else i]])

            vertices[i*8 + 6] = np.array([
                reshaped_x[i] + width_x, 
                reshaped_y[i] + width_y, 
                reshaped_z[i+self._data[0].shape[0] if not i+self._data[0].shape[0] > count-1 else i]])

            vertices[i*8 + 7] = np.array([
                reshaped_x[i] - width_x, 
                reshaped_y[i] + width_y, 
                reshaped_z[i+self._data[0].shape[0] if not i+self._data[0].shape[0] > count-1 else i]])

            faces[i*6 + 0]  = np.array([i*8 + 0, i*8 + 1, i*8 + 2])
            faces[i*6 + 1]  = np.array([i*8 + 2, i*8 + 3, i*8 + 0])
            faces[i*6 + 2]  = np.array([i*8 + 1, i*8 + 4, i*8 + 5])
            faces[i*6 + 3]  = np.array([i*8 + 5, i*8 + 2, i*8 + 1])
            faces[i*6 + 4]  = np.array([i*8 + 2, i*8 + 6, i*8 + 7])
            faces[i*6 + 5]  = np.array([i*8 + 7, i*8 + 3, i*8 + 2])

        self._vertices = vertices
        self._faces    = faces

    def _updateTopography(self):
        '''
        Update the topography of the surface
        '''
        self._buildVerticeMap()
        
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