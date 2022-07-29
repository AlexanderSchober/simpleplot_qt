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

from PyQt5 import QtGui
import numpy as np
from ...pyqtgraph.pyqtgraph     import opengl as gl
from ..custom_pg_items.GLLinePlotItem import GLLinePlotItem
from ...models.parameter_class   import ParameterHandler 

from .ray_intersec_lib import rayTriangleIntersection
from .ray_intersec_lib import closestPointOnLine
from .ray_intersec_lib import checkBoundingBox
from .ray_intersec_lib import retrievePositionSurface

class SurfaceRayHandler(ParameterHandler): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self,'Ray handler')
        self.pointer_elements = []
        self._initialize()
        self.reset()

    def _initialize(self):
        '''
        '''
        self.addParameter(
            'Active', True, 
            method = self._setActive)
        self.addParameter(
            'Mode', 'Projection', 
            choices = ['IsoCurve', 'Projection'],
            method = self.dispatchCoordinate)
        self.addParameter(
            'Computation', 'Fast', 
            choices = ['Fast','Mixed', 'Precise'],
            method = self.dispatchCoordinate)
        self.addParameter(
            'Width', 0.5, 
            method = self.dispatchCoordinate)
        self.addParameter(
            'Color', QtGui.QColor('Black'), 
            method = self.dispatchCoordinate)
        self.addParameter(
            'Offset', 0.001, 
            method = self.dispatchCoordinate)
        self.addParameter(
            'Line mode', 'tube', 
            choices = ['line_strip','lines', 'tube'],
            method = self.dispatchCoordinate)
        self.addParameter(
            'GL options', 'opaque', 
            choices = ['opaque','translucent', 'additive'],
            method = self.dispatchCoordinate)
        self.addParameter(
            'Antialiasing', True,
            method = self.dispatchCoordinate)

    def drawGL(self,target):
        '''
        Dummy draw that sets the target of the 
        pointer element
        '''
        self.default_target = target

    def reset(self):
        '''
        reprocess pointer
        '''
        self.point = None
        self.dispatchCoordinate()

    def processRay(self, ray, dispatch = True):
        '''
        Process an input ray by the 
        canvas widget and perform necessary
        operations
        '''
        self._destroyPointer()
        
        if hasattr(self.parent().childFromName('Surface'), 'draw_items'):
            temp        = self.parent().transformer.getTransform().inverted()[0]
            transform   = np.reshape(np.array(temp.data()),(4,4)).transpose()
            new_ray     = [np.dot(transform,np.hstack((e,1)))[:3] for e in ray]
            intersec    = checkBoundingBox(new_ray, self.parent().childFromName('Data'))
            if not intersec is None:
                self.point = retrievePositionSurface(
                    new_ray, intersec, 
                    self.parent().childFromName('Data'), 
                    self['Computation'])
            else:
                self.point = None

    def _setActive(self):
        '''
        '''
        if not self['Active']:
            self._destroyPointer()

    def _destroyPointer(self):
        '''
        '''
        for element in self.pointer_elements:
            if element in self.default_target.view.items:
                self.default_target.view.removeItem(element)
        self.pointer_elements = []

    def dispatchCoordinate(self):
        '''
        '''
        if self['Active']:
            if self['Mode'] == 'IsoCurve' and not self.point is None:
                self._isoCurve(self.point[2])
            elif self['Mode'] == 'Projection' and not self.point is None:
                self._dataCurve(self.point[0], self.point[1])
            else:
                self._destroyPointer()
        else:
            self._destroyPointer()

    def _dataCurve(self,x,y):
        '''
        '''
        self._destroyPointer()

        tranform    = np.reshape(
            np.array(self.parent().transformer.getTransform().data()),
            (4,4))[:3, :]
        data        = self.parent()['Data'].getData()
        index_x     = np.argmin(np.abs(x-data[0]))
        index_y     = np.argmin(np.abs(y-data[1]))

        data_xx = [data[0][index_x] for e in range(data[1].shape[0])]
        data_xy = data[1]
        data_xz = data[2][index_x,:]

        data_x = np.vstack([data_xx, data_xy, data_xz + self['Offset']]).transpose()
        data_x = np.dot(data_x, tranform)[:,:3]

        self.pointer_elements.append(
            GLLinePlotItem(
                pos     = data_x,
                color   = self['Color'].getRgbF(),
                width   = self['Width'],
                mode    = self['Line mode'],
                antialias = self['Antialiasing'],
                direction = 'y'))
        self.pointer_elements[-1].setGLOptions(self['GL options'])
        self.default_target.view.addItem(self.pointer_elements[-1])

        data_yx = data[0]
        data_yy = [data[1][index_y] for e in range(data[0].shape[0])]
        data_yz = data[2][:,index_y]

        data_y = np.vstack([data_yx,data_yy,data_yz + self['Offset']]).transpose()
        data_y = np.dot(data_y, tranform)[:,:3]
        
        self.pointer_elements.append(   
            GLLinePlotItem(
                pos     = data_y,
                color   = self['Color'].getRgbF(),
                width   = self['Width'],
                mode    = self['Line mode'],
                antialias = self['Antialiasing'],
                direction = 'x'))
        self.pointer_elements[-1].setGLOptions(self['GL options'])
        self.default_target.view.addItem(self.pointer_elements[-1])

    def _isoCurve(self,level):
        '''
        '''
        self._destroyPointer()

        tranform    = np.reshape(
            np.array(self.parent().transformer.getTransform().data()),
            (4,4))[:3, :]
        iso_curves  = self.parent()['Data'].getIsocurve(level)
        data        = self.parent()['Data'].getData()
        bounds      = self.parent()['Data'].getBounds()
        x_fac       = (bounds[0][1] - bounds[0][0])
        y_fac       = (bounds[1][1] - bounds[1][0])

        for curve in iso_curves:
            self.pointer_elements.append(
                GLLinePlotItem(
                    pos     =np.dot(np.vstack([
                                [(item[0]-0.5) / (data[2].shape[0]-1) * x_fac + bounds[0][0] for item in curve],
                                [(item[1]-0.5) / (data[2].shape[1]-1) * y_fac + bounds[1][0] for item in curve],
                                [level + self['Offset']for item in curve]]).transpose(),
                                tranform)[:,:3],
                    color   = self['Color'].getRgb(),
                    width   = self['Width'],
                    mode    = self['Line mode'],
                    antialias = self['Antialiasing']))
            self.pointer_elements[-1].setGLOptions(self['GL options'])
            self.default_target.view.addItem(self.pointer_elements[-1])
