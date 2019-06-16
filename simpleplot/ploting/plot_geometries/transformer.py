
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
from ...model.parameter_class       import ParameterHandler 

class Transformer(ParameterHandler): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self, 'Transform')

        self._position      = np.array([0.,0.,0.])
        self._scale         = np.array([1.,1.,1.])
        self._rotate_angle  = np.array([0.,0.,0.])
        self._rotate_axis   = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])

        self._setTransformerParameters()

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
        '''
        if self.parent()._mode =='3D':
            self.temp_position  = np.array(self._position)
            self.temp_scale     = np.array(self._scale)
            self.temp_angle     = np.array(self._rotate_angle)
            self.temp_axis      = np.array(self._rotate_axis)

            self._position      = np.array([0.,0.,0.])
            self._scale         = np.array([1.,1.,1.])
            self._rotate_angle  = np.array([0.,0.,0.])
            self._rotate_axis   = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])

            if not hasattr(self.parent(), 'draw_items'):
                return None

            for draw_item in self.parent().draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        item.resetTransform()
                else:
                    draw_item.resetTransform()

    def reTransform(self):
        '''
        '''
        if self.parent()._mode == '3D':
            self.translate(self.temp_position)
            self.scale(self.temp_scale)
            self.rotate(self.temp_angle, self.temp_axis)

    def translate(self, position = None):
        '''
        translate in the 3D view
        '''
        if position is None:
            position = np.array(self['Position'])

        if hasattr(self.parent(), 'draw_items') and self.parent()._mode =='3D':
            for draw_item in self.parent().draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.translateItem(item, position)
                else:
                    self.translateItem(draw_item, position)

            self._position = position

        if hasattr(self.parent().parent(), '_ray_handler'):
             self.parent().parent()._ray_handler.reset()

    def translateItem(self, item, position):
        '''
        translate in the 3D view
        '''
        item.translate(-self._position[0], -self._position[1], -self._position[2])
        item.translate(position[0], position[1], position[2])

    def scale(self, scale = None):
        '''
        scale in the 3D view
        '''
        if scale is None:
            scale = np.array(self['Scaling'])

        for i in range(3):
            if scale[i] == 0. :
                scale[i] = 1.

        if hasattr(self.parent(), 'draw_items') and self.parent()._mode =='3D':
            for draw_item in self.parent().draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.scaleItem(item, scale)
                else:
                    self.scaleItem(draw_item, scale)

            self._scale = scale

        if hasattr(self.parent().parent(), '_ray_handler'):
             self.parent().parent()._ray_handler.reset()

    def scaleItem(self, item, scale):
        '''
        scale in the 3D view
        '''
        item.scale(1./self._scale[0], 1./self._scale[1], 1./self._scale[2])
        item.scale(scale[0], scale[1], scale[2])

    def rotate(self, angles = None, axes = None):
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

        if hasattr(self.parent(), 'draw_items') and self.parent()._mode =='3D':
            for draw_item in self.parent().draw_items:
                if isinstance(draw_item, list):
                    for item in draw_item:
                        self.rotateItem(item,  angles, axes)
                else:
                    self.rotateItem(draw_item,  angles, axes)

            self._rotate_angle = angles
            self._rotate_axis  = axes

        if hasattr(self.parent().parent(), '_ray_handler'):
             self.parent().parent()._ray_handler.reset()

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
