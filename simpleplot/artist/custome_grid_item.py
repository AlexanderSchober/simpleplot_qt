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

#import dependencies
#import dependencies
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from OpenGL.GLUT    import *
from OpenGL.GL      import *
from OpenGL.GLU     import *

import numpy as np

from ..pyqtgraph            import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph  import opengl as gl

class GLGridItem(gl.GLGridItem):
    def __init__(self, *args, **kwargs):
        gl.GLGridItem.__init__(self, *args, glOptions='opaque', **kwargs)
        self._color = [1,1,1,0.3]

    def setColor(self, color):
        '''
        Set the color in which the plot will be drawn

        Parameters
        - - - - - - 
        r : int red
        g : int green
        b : int blue

        '''
        self._color = color
        self.update()

    def setSize(self, x=[0.,1.], y=[0.,1.], z=[0.,1.], size = None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z or size=QVector3D().
        """
        self._size = [x,y,z]
        self.update()

    def size(self):
        return self._size[:]

    def paint(self):
        self.setupGLState()
        
        # if self.antialias:
            # glEnable(GL_LINE_SMOOTH)
            # glEnable(GL_BLEND)
            # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        xs,ys,zs = self.spacing()
        xvals = np.arange(x[0] - xs*0.001, x[1] + xs*0.001, xs) 
        yvals = np.arange(y[0] - ys*0.001, y[1] + ys*0.001, ys) 
        glColor4f(*self._color.getRgbF())
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x, yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        
        glEnd()