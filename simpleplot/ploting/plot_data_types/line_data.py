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

from ...model.node   import SessionNode

class LineData(PlotData, SessionNode): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self,x = None, y = None, z = None, error = None, **kwargs):
        PlotData.__init__(self, **kwargs) 
        SessionNode.__init__(self, 'Data')

        self._axes = ['x','y','z']
        self.setData(x = x, y = y, z = z)
        
    def setData(self, **kwargs):
        '''
        set the local data manually even after
        initialization of the class
        '''
        elements = [None]*len(self._axes)

        for i,value in enumerate(self._axes):
            if value in kwargs.keys():
                elements[i] = kwargs[value]

        shape = np.amax(
            np.array([np.array(elements)[i].shape[0] 
            if not np.array(elements)[i] is None else 0 
            for i in range(np.array(elements).shape[0])]))

        for i,element in enumerate(elements):
            if element is None:
                elements[i] = np.zeros(shape)

        if 'error' in kwargs.keys():
            self._setError(kwargs['error'])

        self._data = elements

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

    def getError(self):
        '''
        return a dataset as the data on the 
        wanted orientation
        '''
        if hasattr(self, '_error'):
            return self._error
        else:
            return None