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

from ...models.session_node   import SessionNode

class LineData(PlotData, SessionNode): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self,**kwargs):
        PlotData.__init__(self, **kwargs) 
        SessionNode.__init__(self, 'Data')

        self._axes = ['x','y','z']
        self.setData(**kwargs)
        
    def setData(self, **kwargs):
        '''
        set the local data manually even after
        initialization of the class
        '''
        elements = [None for i in self._axes]

        for i,value in enumerate(self._axes):
            if value in kwargs.keys():
                if isinstance(kwargs[value],np.ndarray) or isinstance(kwargs[value],list):
                    elements[i] = np.array(kwargs[value])

        shape = np.amax(
            np.array(
                [0 if elements[i] is None else elements[i].shape[0]
                for i in range(len(self._axes))]
                )
            )

        for i,element in enumerate(elements):
            if element is None:
                elements[i] = np.zeros(shape)

        if 'error' in kwargs.keys():
            self._setError(kwargs['error'])

        self._data = elements
        self._setBounds()

    def _setError(self, error):
        '''
        set the local data manually even after
        initialization of the class
        '''
        self._error = error

    def getData(self, axis = ['x', 'y']):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        return [self._data[self._axes.index(value)] for value in axis]

    def getBounds(self):
        '''
        returns the bounds
        '''
        return self._bounds

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

    def getError(self):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        if hasattr(self, '_error'):
            return self._error
        else:
            return None

    def _sanity(self, elements):
        '''
        Check that the data makes sense in 
        '''
        if not elements[self._axes.index('x')].shape[0] == elements[self._axes.index('y')].shape[0]:
            return False
        if not elements[self._axes.index('y')].shape[0] == elements[self._axes.index('z')].shape[0]:
            return False
        return True

    def _setBounds(self):
        '''
        returns the bounds of the set datastructure
        '''
        self._bounds = []
        for element in self._data:
            if not element.shape[0] == 0:
                self._bounds.append([
                    np.amin(element), 
                    np.amax(element)])
            else:
                self._bounds.append([0,1])
