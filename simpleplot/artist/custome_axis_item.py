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

#import dependencies
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import opengl as gl
from ..pyqtgraph.pyqtgraph import functions as fn
import numpy as np
import math

from ..ploting.plot_items.points import Point
from ..ploting.plot_items.transformations import *
from ..ploting.plot_items.operations import *

class GLAxisItem(gl.GLAxisItem):
    def __init__(self, location = None):
        gl.GLAxisItem.__init__(self)

        if location == 'x':
            self._length       = [-5., 5.]
            self._line_width   = 0.05
            self._color        = [1,0,0,1]
            self._direction    = [1,0,0]
            self._origin       = [0,0,0]
            self._tick_length  = [-0.2,0.2]
            self._tick_vecs    = [[0,1,0],[1,0,0]]
            self._font_size    = 12

        elif location == 'y':
            self._length       = [-5., 5.]
            self._line_width   = 0.05
            self._color        = [0,1,0,1]
            self._direction    = [0,1,0]
            self._origin       = [0,0,0]
            self._tick_length  = [-0.2,0.2]
            self._tick_vecs    = [[0,1,0],[1,0,0]]
            self._font_size    = 12

        elif location == 'z':
            self._length       = [-5., 5.]
            self._line_width   = 0.05
            self._color        = [0,0,1,1]
            self._direction    = [0,0,1]
            self._origin       = [0,0,0]
            self._tick_length  = [-0.2,0.2]
            self._tick_vecs    = [[0,1,0],[1,0,0]]
            self._font_size    = 12

        else:
            self._length       = [-5., 5.]
            self._line_width   = 0.05
            self._color        = [1,0,0,1]
            self._direction    = [1,0,0]
            self._origin       = [0,0,0]
            self._tick_length  = [-0.2,0.2]
            self._tick_vecs    = [[0,1,0],[1,0,0]]
            self._font_size    = 12

    def setLength(self, min_val,max_val):
        '''
        set the length of the axis

        Parameters
        ----------
        length : float 
            the length parameter
        '''
        self._length = [float(min_val),float(max_val)]
        self._preprocess()
        self.update()

    def setColor(self, r, g, b, alpha):
        '''
        set the length of the axis

        Parameters
        ----------
        length : int 
            the length parameter
        '''
        self._color = list([r,g,b,alpha])
        self._preprocess()
        self.update()

    def setDirection(self,vec):
        '''
        set the ticks

        Parameters
        ----------
        vec : float array 
            The direction of the vector
        '''
        self._direction = vec
        self._preprocess()
        self.update()

    def setPosition(self,pos):
        '''
        set the ticks

        Parameters
        - - - - - - - 
        pos : float array 
            The origin of the vector
        '''
        self._origin = pos
        self._preprocess()
        self.update()

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

    def _preprocess(self):
        '''
        To avoid the computation of all elements on 
        any frame redraw the values are buffered here
        '''
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

        #axis
        self.circle_pts_bot = [Point('', 0,0,self._length[0])]
        self.circle_pts_top = [Point('', 0,0,self._length[1])]
        for i in range(int(10) + 1):
            angle_val = 2 * math.pi * (i/10)
            x = self._line_width * math.cos(angle_val)
            y = self._line_width * math.sin(angle_val)
            self.circle_pts_bot.append(Point('', x, y, self._length[0]))
            self.circle_pts_top.append(Point('', x, y, self._length[1]))

        self.rotation.apply(self.circle_pts_bot)
        self.rotation.apply(self.circle_pts_top)
        self.translation.apply(self.circle_pts_bot)
        self.translation.apply(self.circle_pts_top)

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

        self._drawAxis()