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

# General imports
import numpy as np
from pyrr import Matrix44

# Personal imports
from ...models.parameter_class   import ParameterHandler 
from .transform_3D     import Transform3D

class Transformer(ParameterHandler): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self, 'Transform')

        self._transform     = Transform3D()
        self._setTransformerParameters()

    def resetTransform(self):
        '''
        This will be the first step to computing
        a new transform
        '''
        self._transform.setToIdentity()

    def getTransform(self):
        '''
        Get the current transform matrix
        '''
        return self._transform

    def _setTransformerParameters(self):
        '''
        set the parameters
        '''
        self.addParameter(
            'Position', [0.,0.,0.], 
            names = [ 'x', 'y', 'z'],
            method = self.transform)
        self.addParameter(
            'Scaling', [1.,1.,1.], 
            names = [ 'x', 'y', 'z'],
            method = self.transform)
        self.addParameter(
            'Rotation axis x', 
            [0.] + [1.,0.,0.],
            names = ['angle', 'x', 'y', 'z'],
            method = self.transform)
        self.addParameter(
            'Rotation axis y', 
            [0.] + [0.,1.,0.],
            names = ['angle', 'x', 'y', 'z'],
            method = self.transform)
        self.addParameter(
            'Rotation axis z', 
            [0.] + [0.,0.,1.],
            names = ['angle', 'x', 'y', 'z'],
            method = self.transform)

    def transform(self):
        '''
        Transform items again
        '''
        if self.parent() is None:
            return

        self.resetTransform()
        self.scale()
        self.translate()
        self.rotate()

        if hasattr(self.parent(), 'draw_items'):
            for item in self.parent().draw_items:
                if hasattr(item, 'setTransformMatrix'):
                    item.setTransformMatrix(Matrix44(self._transform.data()))
                    item.update()
            return

        for child in self.parent()._children:
            if hasattr(child, 'draw_items'):
                for item in child.draw_items:
                    if hasattr(item, 'setTransformMatrix'):
                        item.setTransformMatrix(Matrix44(self._transform.data()))
                        item.update()

    def translate(self):
        '''
        translate in the 3D view
        '''
        self._transform.translate(*self['Position'])

    def translateItem(self, item):
        '''
        translate in the 3D view
        '''
        item.setTransform(self._transform)
        self._model.dataChanged.emit(self.index(),self.index())

    def scale(self, scale = None):
        '''
        scale in the 3D view
        '''
        scale = self['Scaling']

        for i in range(3):
            if scale[i] == 0. :
                scale[i] = 1.

        self._transform.scale(*scale)

    def rotate(self, angles = None, axes = None):
        '''
        rotate in the 3D view
        '''
        elements = [
            self['Rotation axis x'],
            self['Rotation axis y'],
            self['Rotation axis z']]

        angles = np.array([e[0] for e in elements])
        axes = np.array([e[1:] for e in elements])

        self._transform.translate(*(-np.array(self['Position'])).tolist())

        for i in range(3):
            self._transform.rotate(
                angles[i],
                axes[i,0], 
                axes[i,1],
                axes[i,2])

        self._transform.translate(*self['Position'])

        self._rotate_angle = angles
        self._rotate_axis  = axes

    def transformPoint(self, point):
        '''
        Allows to transform a point with the current 
        transformation matrix
        '''
        transform   = np.reshape(np.array(self._transform.data()),(4,4)).transpose()
        return np.dot(transform,np.hstack((point,1)))[:3]
