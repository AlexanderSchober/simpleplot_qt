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
        gl.GLGridItem.__init__(self, *args, **kwargs)
        self.__color = [1,1,1,0.3]

    def setColor(self, r,g,b,a):
        '''
        Set the color in which the plot will be drawn

        Parameters
        - - - - - - 
        r : int red
        g : int green
        b : int blue

        '''
        self.__color = [r,g,b,a]
        self.update()

    def paint(self):
        self.setupGLState()
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        xs,ys,zs = self.spacing()
        xvals = np.arange(-1 * x/2., x/2. + xs*0.001, xs) 
        yvals = np.arange(-1 * y/2., y/2. + ys*0.001, ys) 
        glColor4f(*self.__color)
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x,  yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        
        glEnd()