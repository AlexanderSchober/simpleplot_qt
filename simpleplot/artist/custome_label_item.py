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
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from OpenGL.GL import *
from ..pyqtgraph.pyqtgraph import functions as fn
from .custome_axis_item import GLAxisItem
import numpy as np
import math

from ..ploting.plot_items.points import Point
from ..ploting.plot_items.transformations import *
from ..ploting.plot_items.operations import *

class GLLabelItem(GLAxisItem):
    def __init__(self, location = None):
        GLAxisItem.__init__(self, location = None)
        self.tick_positions = []

    def _tickValues(self, minVal, maxVal, size):
        """
        Return the values and spacing of ticks to draw::
        
            [  
                (spacing, [major ticks]), 
                (spacing, [minor ticks]), 
                ... 
            ]
        
        By default, this method calls tickSpacing to determine the correct tick locations.
        This is a good method to override in subclasses.
        """
        minVal, maxVal = sorted((minVal, maxVal))
            
        ticks = []
        tickLevels = self._tickSpacing(minVal, maxVal, size)
        allValues = np.array([])
        for i in range(len(tickLevels)):
            spacing, offset = tickLevels[i]
            start = (np.ceil((minVal-offset) / spacing) * spacing) + offset
            num = int((maxVal-start) / spacing) + 1
            values = (np.arange(num) * spacing + start) / self.scale
            values = list(filter(lambda x: all(np.abs(allValues-x) > spacing*0.01), values) )
            allValues = np.concatenate([allValues, values])
            ticks.append((spacing/self.scale, values))
        return allValues, tickLevels


    def _tickSpacing(self, minVal, maxVal, size):
        """Return values describing the desired spacing and offset of ticks.
        
        This method is called whenever the axis needs to be redrawn and is a 
        good method to override in subclasses that require control over tick locations.
        
        The return value must be a list of tuples, one for each set of ticks::
        
            [
                (major tick spacing, offset),
                (minor tick spacing, offset),
                (sub-minor tick spacing, offset),
                ...
            ]
        """
        minVal *= self.scale
        maxVal *= self.scale

        dif = abs(maxVal - minVal)
        if dif == 0:
            return []
        
        
        ## decide optimal minor tick spacing in pixels (this is just aesthetics)
        optimalTickCount = max(4., np.log(size))
        ## optimal minor tick spacing 
        optimalSpacing = dif / optimalTickCount
        ## the largest power-of-10 spacing which is smaller than optimal
        p10unit = 10 ** np.floor(np.log10(optimalSpacing))
        ## Determine major/minor tick spacings which flank the optimal spacing.
        intervals = np.array([1., 2., 10., 20., 100.]) * p10unit
        minorIndex = 0
        while intervals[minorIndex+1] <= optimalSpacing:
            minorIndex += 1
            
        levels = [
            (intervals[minorIndex+2], 0),
            (intervals[minorIndex+1], 0),
            #(intervals[minorIndex], 0)    ## Pretty, but eats up CPU
        ]
        ## decide whether to include the last level of ticks
        minSpacing = min(size / 20., 30.)
        maxTickCount = size / minSpacing
        if dif / intervals[minorIndex] <= maxTickCount:
            levels.append((intervals[minorIndex], 0))
        return levels

    def _tickStrings(self, values, scale, spacing):
        """Return the strings that should be placed next to ticks. This method is called 
        when redrawing the axis and is a good method to override in subclasses.
        The method is called with a list of tick values, a scaling factor (see below), and the 
        spacing between ticks (this is required since, in some instances, there may be only 
        one tick and thus no other way to determine the tick spacing)
        
        The scale argument is used when the axis label is displaying units which may have an SI scaling prefix.
        When determining the text to display, use value*scale to correctly account for this prefix.
        For example, if the axis label's units are set to 'V', then a tick value of 0.001 might
        be accompanied by a scale value of 1000. This indicates that the label is displaying 'mV', and 
        thus the tick should display 0.001 * 1000 = 1.
        """
        places = max(0, np.ceil(-np.log10(spacing*scale)))
        strings = []
        for v in values:
            vs = v * scale
            if abs(vs) < .001 or abs(vs) >= 10000:
                vstr = "%g" % vs
            else:
                vstr = ("%%0.%df" % places) % vs
            strings.append(vstr)
        return strings
        
    def _updateAutoSIPrefix(self, minVal, manVal):
        self.scale  = fn.siScale(max(abs(minVal), abs(manVal)))[0]
        return self.scale

    def _drawLabels(self):
        '''
        '''
        for i in range(len(self.tick_positions)):
            location = Point('', 0, 0,self.tick_positions[i])
            self.rotation.apply([location])
            self.translation.apply([location])
            self.view().renderText(
                location.vec[0], 
                location.vec[1],
                location.vec[2], 
                self.tick_strings[i], 
                font = self.font)

    def _preprocess(self):
        '''
        To avoid the computation of all elements on 
        any frame redraw the values are buffered here
        '''
        #labels
        scale = self._updateAutoSIPrefix(
            self._length[0], 
            self._length[1])

        self.tick_positions, tick_spacing = self._tickValues(
            self._length[0], 
            self._length[1], 
            self._length[1]- self._length[0])

        self.tick_strings = self._tickStrings(
            self.tick_positions, 
            scale, 
            tick_spacing[-1][0])

        calc_angle = getAngle(
            Point('', 0, 0, 0), 
            Point('', 0, 0, 1),
            Point('', *self._direction))

        if not calc_angle == 0:
            normal_vec = getNormal([
                Point('', 0, 0, 0), 
                Point('', 0, 0, 1), 
                Point('', *self._direction)])
            self.rotation = Rotation(normal_vec, calc_angle)

        else:
            self.rotation = Rotation([1,1,1], 0)

        self.translation = Translation(np.array(self._origin))

        self.font = QtGui.QFont()
        self.font.setPixelSize(self._font_size)


    def paint(self):
        '''
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        '''
        self.setupGLState()
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glColor4f(*self._color)
        self.update()
        self._drawLabels()