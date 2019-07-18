
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

import numpy as np
from ...model.parameter_class   import ParameterHandler 
from ...pyqtgraph.pyqtgraph     import Transform3D

class Transformer(ParameterHandler): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self, 'Transform')

        self._transform     = Transform3D()
        self._position      = np.array([0.,0.,0.])
        self._scale         = np.array([1.,1.,1.])
        self._rotate_angle  = np.array([0.,0.,0.])
        self._rotate_axis   = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])

        self._setTransformerParameters()

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
            'Position', self._position.tolist(), 
            names = [ 'x', 'y', 'z'],
            method = self.translate)
        self.addParameter(
            'Scaling', self._scale.tolist(), 
            names = [ 'x', 'y', 'z'],
            method = self.scale)
        self.addParameter(
            'Rotation axis x', 
            [self._rotate_angle[0]] + self._rotate_axis[0].tolist(),
            names = ['angle', 'x', 'y', 'z'],
            method = self.rotate)
        self.addParameter(
            'Rotation axis y', 
            [self._rotate_angle[1]] + self._rotate_axis[1].tolist(),
            names = ['angle', 'x', 'y', 'z'],
            method = self.rotate)
        self.addParameter(
            'Rotation axis z', 
            [self._rotate_angle[2]] + self._rotate_axis[2].tolist(),
            names = ['angle', 'x', 'y', 'z'],
            method = self.rotate)

    def unTransform(self):
        '''
        Detranfrom the 3D item to perform the adequate
        operations on it. 
        '''
        self.temp_position  = np.array(self._position)
        self.temp_scale     = np.array(self._scale)
        self.temp_angle     = np.array(self._rotate_angle)
        self.temp_axis      = np.array(self._rotate_axis)

        self._position      = np.array([0.,0.,0.])
        self._scale         = np.array([1.,1.,1.])
        self._rotate_angle  = np.array([0.,0.,0.])
        self._rotate_axis   = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])

        self._transform.setToIdentity()

        for child in self.parent()._children:
            if not  hasattr(child, 'draw_items'):
                continue

            for draw_item in child.draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        item.resetTransform()
                else:
                    draw_item.resetTransform()

    def reTransform(self):
        '''
        Transform items again
        '''
        for child in self.parent()._children:
            if not  hasattr(child, 'draw_items'):
                continue

            self.translate(self.temp_position, child)
            self.scale(self.temp_scale, child)
            self.rotate(self.temp_angle, self.temp_axis, child)

    def translate(self, position = None, child = None):
        '''
        translate in the 3D view
        '''
        if position is None:
            position = np.array(self['Position'])

        self._transform.translate(
            -self._position[0], 
            -self._position[1], 
            -self._position[2])

        self._transform.translate(
            position[0], 
            position[1], 
            position[2])

        for child in self.parent()._children:
            if  hasattr(child, 'draw_items'):
                for draw_item in child.draw_items:
                    if isinstance(draw_item, list):
                        for item in draw_item:
                            self.translateItem(item)
                    else:
                        self.translateItem(draw_item)

        self._position = position

        if hasattr(self.parent(), '_ray_handler'):
             self.parent()._ray_handler.reset()

    def translateItem(self, item):
        '''
        translate in the 3D view
        '''
        item.setTransform(self._transform)
        self._model.dataChanged.emit(self.index(),self.index())

    def scale(self, scale = None, child = None):
        '''
        scale in the 3D view
        '''
        if scale is None:
            scale = np.array(self['Scaling'])

        for i in range(3):
            if scale[i] == 0. :
                scale[i] = 1.

        self._transform.scale(
            1./self._scale[0], 
            1./self._scale[1], 
            1./self._scale[2])

        self._transform.scale(
            scale[0], 
            scale[1], 
            scale[2])

        for child in self.parent()._children:
            if  hasattr(child, 'draw_items'):
                for draw_item in child.draw_items:
                    if isinstance(draw_item, list):
                        for item in draw_item:
                            self.scaleItem(item)
                    else:
                        self.scaleItem(draw_item)

        self._scale = scale

        if hasattr(self.parent(), '_ray_handler'):
             self.parent()._ray_handler.reset()

    def scaleItem(self, item):
        '''
        scale in the 3D view
        '''
        item.setTransform(self._transform)
        self._model.dataChanged.emit(self.index(),self.index())

    def rotate(self, angles = None, axes = None, child = None):
        '''
        rotate in the 3D view
        '''
        if angles is None or axes is None:
            elements = [
                self['Rotation axis x'],
                self['Rotation axis y'],
                self['Rotation axis z']]

            angles = np.array([e[0] for e in elements])
            axes = np.array([e[1:] for e in elements])

        self._transform.translate(
            -self._position[0], 
            -self._position[1], 
            -self._position[2])

        for i in range(3):
            self._transform.rotate(
                -self._rotate_angle[-1-i],
                self._rotate_axis[-1-i,0], 
                self._rotate_axis[-1-i,1],
                self._rotate_axis[-1-i,2])

        for i in range(3):
            self._transform.rotate(
                angles[i],
                axes[i,0], 
                axes[i,1],
                axes[i,2])

        self._transform.translate(
            self._position[0], 
            self._position[1], 
            self._position[2])

        for child in self.parent()._children:
            if  hasattr(child, 'draw_items'):
                for draw_item in child.draw_items:
                    if isinstance(draw_item, list):
                        for item in draw_item:
                            self.rotateItem(item)
                    else:
                        self.rotateItem(draw_item)

        self._rotate_angle = angles
        self._rotate_axis  = axes

        if hasattr(self.parent(), '_ray_handler'):
             self.parent()._ray_handler.reset()

    def rotateItem(self, item):
        '''
        rotate in the 3D view
        '''
        item.setTransform(self._transform)
        self._model.dataChanged.emit(self.index(),self.index())

    def transformPoint(self, point):
        '''
        Allows to transform a point with the current 
        transformation matrix
        '''
        transform   = np.reshape(np.array(self._transform.data()),(4,4)).transpose()
        return np.dot(transform,np.hstack((point,1)))[:3]
