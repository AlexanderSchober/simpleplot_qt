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
from ..pyqtgraph.pyqtgraph import opengl as gl
from ..pyqtgraph.pyqtgraph import functions as fn
from .custome_axis_item import GLAxisItem
import numpy as np
import math

from ..ploting.plot_items.points import Point
from ..ploting.plot_items.transformations import *
from ..ploting.plot_items.operations import *


class GLTickItem(GLAxisItem):
    def __init__(self, location = None):
        GLAxisItem.__init__(self, location = location)

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

    def _drawAxis(self):
        '''
        Draw the line a s cylinder 
        as the line width is not supported
        under normal circumstances
        '''
        glBegin(GL_TRIANGLE_FAN)#drawing the back circle
        for point in self.circle_pts_bot:
            glVertex(*point.vec.tolist())
        glEnd()

        glBegin(GL_TRIANGLE_FAN)#drawing the front circle
        for point in self.circle_pts_top:
            glVertex(*point.vec.tolist())
        glEnd()

        glBegin(GL_TRIANGLE_STRIP)#draw the tube
        for i in range(1,len(self.circle_pts_bot)):
            glVertex(*self.circle_pts_bot[i].vec.tolist())
            glVertex(*self.circle_pts_top[i].vec.tolist())
        glEnd()

    def _updateAutoSIPrefix(self, minVal, manVal):
        self.scale  = fn.siScale(max(abs(minVal), abs(manVal)))[0]
        return self.scale

    def _drawTick(self):
        '''
        Draw the ticks.
        '''
        for i in range(len(self.tick_bots)):
            circle_pts_bot = self.tick_bots[i]
            circle_pts_top = self.tick_tops[i]

            glBegin(GL_TRIANGLE_FAN)#drawing the back circle
            for point in circle_pts_bot:
                glVertex(*point.vec.tolist())
            glEnd()

            glBegin(GL_TRIANGLE_FAN)#drawing the front circle
            for point in circle_pts_top:
                glVertex(*point.vec.tolist())
            glEnd()

            glBegin(GL_TRIANGLE_STRIP)#draw the tube
            for i in range(1,len(circle_pts_bot)):
                glVertex(*circle_pts_bot[i].vec.tolist())
                glVertex(*circle_pts_top[i].vec.tolist())
            glEnd()

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

        #ticks
        self.tick_tops = []
        self.tick_bots = []

        for tick_vec in self._tick_vecs:
            calc_angle = getAngle(
                Point('', 0, 0, 0), 
                Point('', 0, 0, 1),
                Point('', *tick_vec))

            if not calc_angle == 0:
                normal_vec = getNormal([
                    Point('', 0, 0, 0), 
                    Point('', 0, 0, 1), 
                    Point('', *tick_vec)])
                self.tick_rotation = Rotation(normal_vec, calc_angle)

            else:
                self.tick_rotation = Rotation([1,1,1], 0)

            for j in range(len(self.tick_positions)):
                circle_pts_bot = [Point('', 0,0, self._tick_length[0])]
                circle_pts_top = [Point('', 0,0, self._tick_length[1])]
                for i in range(int(10) + 1):
                    angle_val = 2 * math.pi * (i/10)
                    x = self._line_width * math.cos(angle_val)
                    y = self._line_width * math.sin(angle_val)
                    circle_pts_bot.append(Point('', x, y, self._tick_length[0]))
                    circle_pts_top.append(Point('', x, y, self._tick_length[1]))

                self.tick_translation = Translation(np.array([0,0,self.tick_positions[j]]))
                self.tick_rotation.apply(circle_pts_bot)
                self.tick_rotation.apply(circle_pts_top)
                self.tick_translation.apply(circle_pts_bot)
                self.tick_translation.apply(circle_pts_top)
                self.rotation.apply(circle_pts_bot)
                self.rotation.apply(circle_pts_top)
                self.translation.apply(circle_pts_bot)
                self.translation.apply(circle_pts_top)
                self.tick_bots.append(circle_pts_bot)
                self.tick_tops.append(circle_pts_top)

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

        self._drawTick()