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
from .management.tick_management import tickValues, updateAutoSIPrefix, tickStrings

SI_PREFIXES = str('yzafpnµm kMGTPEZY')
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'


class CartesianRepresentation2D(object):
    def __init__(self, axis):
        self._axis = axis
        self._tick_range = None
        self._tick_values = None
        self._ticks_positions = None
        self._label_positions = None
        self._label_string = None
        self._scale = None
        self._spacing = None

        self._screen_size = (0, 0)
        self._margins = (0, 0, 0, 0)
        self._range = (0, 1)
        self._delta = 1

    def setAxis(self, axis: str) -> None:
        self._axis = axis

    def toCameraSpace(self, input_values):
        return input_values

    def fromCameraSpace(self, input_values):
        return input_values

    def reevaluateAxis(self, camera):
        self._margins = camera['Margins (px)']
        self._screen_size = camera['Screen size']
        self._range = camera['Camera x range'] if self._axis == 'x' else camera['Camera y range']
        self._delta = self._range[1] - self._range[0]

        self._tick_range = self._getTickRange()
        self._scale = updateAutoSIPrefix(
            self._tick_range[0], self._tick_range[1])
        self._tick_values, self._spacing = tickValues(
            self._tick_range[0], self._tick_range[1], self._tick_range[1] - self._tick_range[0], self._scale)
        self._ticks_positions = self._getTickPositions()
        self._label_positions, self._label_string = self._getLabelPositions(
            self._tick_values*self._scale)

    def getTicksAndLabels(self):
        return self._tick_values, self._ticks_positions, self._label_positions, self._label_string

    def getTicks(self):
        return self._tick_values, self._ticks_positions, self._scale

    def _getTickRange(self) -> np.array:
        """
        This function will determine the tick values to consider using
        the camera values and margins and return the limits
        :return:
        """
        if self._axis == 'x':
            return np.array([
                self._range[0] + (self._range[1] - self._range[0]) *
                self._margins[0] / self._screen_size[0],
                self._range[1] - (self._range[1] - self._range[0]) *
                self._margins[2] / self._screen_size[0]
            ]) if self._screen_size[0] > 0 else np.array([0, 1])
        else:
            return np.array([
                self._range[0] + (self._range[1] - self._range[0]) *
                self._margins[1] / self._screen_size[1],
                self._range[1] - (self._range[1] - self._range[0]) *
                self._margins[3] / self._screen_size[1]
            ]) if self._screen_size[1] > 0 else np.array([0, 1])

    def _getTickPositions(self):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """

        ticks_positions = np.zeros((self._tick_values.shape[0], 3))

        if self._axis == 'x':
            ticks_positions[:, 0] = (
                self._tick_values*self._scale - self._range[0]) / self._delta * 2 - 1
        elif self._axis == 'y':
            ticks_positions[:, 1] = (
                self._tick_values*self._scale - self._range[0]) / self._delta * 2 - 1
        return ticks_positions

    def _getLabelPositions(self, tick_values):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """
        ticks_positions = np.zeros((tick_values.shape[0], 4))
        if self._axis == 'x':
            ticks_positions[:, 0] = (
                tick_values*self._scale - self._range[0]) / self._delta * 2 - 1
        elif self._axis == 'y':
            ticks_positions[:, 1] = (
                tick_values*self._scale - self._range[0]) / self._delta * 2 - 1

        label_string = ""
        start = 0
        for i, value in enumerate(tick_values):
            if abs(value) > 1e3:
                instance = u"{:.2e}".format(value)
            else:
                instance = str("%g" % value)
            label_string += instance
            ticks_positions[i, 2] = start
            ticks_positions[i, 3] = start + len(instance)
            start += len(instance)
        return ticks_positions, label_string
