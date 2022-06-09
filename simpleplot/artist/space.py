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

from typing import Union
from simpleplot.artist.camera_2d import Camera2D
from simpleplot.artist.camera_3d import Camera3D
from ..models.parameter_class import ParameterHandler
from .space_modules.space_cartesian_2d import CartesianRepresentation2D
# from .space_modules.space_logarythmic import LogarythmicRepresentation


class SpaceRepresentation(ParameterHandler):
    '''
    This class will handle very important transformation elements. 
    For example the input will be cartesian and displaed as log2, log10
    or polar coordinates. Meaning that the camera will always display the 
    same infomation and the present class will trnaform the space on the 
    fly. 

    To this purpose th ecurrent transformation module will be loaded 
    for each axis. These modules will also handle the tick position
    and placement.
    '''

    def __init__(self):
        super(SpaceRepresentation, self).__init__('Space representation')
        self._camera = None

        self._selected_spaces = {
            'x': CartesianRepresentation2D('x'),
            'y': CartesianRepresentation2D('y'),
            'z': CartesianRepresentation2D('z')
        }

    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._camera = camera
        self.reevaluateAxis()

    def toCameraSpace(self, axis, input_values):
        return self._selected_spaces[axis].toCameraSpace(input_values)

    def fromCameraSpace(self, axis, input_values):
        return self._selected_spaces[axis].fromCameraSpace(input_values)

    def getTicksAndLabels(self, axis):
        return self._selected_spaces[axis].getTicksAndLabels()

    def getTicks(self, axis):
        return self._selected_spaces[axis].getTicks()

    def reevaluateAxis(self):
        if self._camera is None:
            return
        for _, item in self._selected_spaces.items():
            item.reevaluateAxis(self._camera)
