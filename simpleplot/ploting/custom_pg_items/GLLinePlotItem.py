from OpenGL.GL import *
from OpenGL.arrays import vbo
from ...pyqtgraph.pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from ...pyqtgraph.pyqtgraph.opengl.shaders import shaders
from ...pyqtgraph.pyqtgraph import QtGui
from ...pyqtgraph.pyqtgraph import functions as fn
import numpy as np

from ..graphics_geometry.points           import Point
from ..graphics_geometry.transformations  import *
from ..graphics_geometry.operations       import *

import scipy.linalg as sci_lin
__all__ = ['GLLinePlotItem']

class GLLinePlotItem(GLGraphicsItem):
    """Draws line plots in 3D."""
    
    def __init__(self, **kwds):
        """All keyword arguments are passed to setData()"""
        GLGraphicsItem.__init__(self)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = None
        self.mode = 'line_strip'
        self.width = 1.
        self.color = (1.0,1.0,1.0,1.0)
        self.setData(**kwds)
    
    def setData(self, **kwds):
        """
        Update the data displayed by this item. All arguments are optional; 
        for example it is allowed to update vertex positions while leaving 
        colors unchanged, etc.
        
        ====================  ==================================================
        **Arguments:**
        ------------------------------------------------------------------------
        pos                   (N,3) array of floats specifying point locations.
        color                 (N,4) array of floats (0.0-1.0) or
                              tuple of floats specifying
                              a single color for the entire item.
        width                 float specifying line width
        antialias             enables smooth line drawing
        mode                  'lines': Each pair of vertexes draws a single line
                                       segment.
                              'line_strip': All vertexes are drawn as a
                                            continuous set of line segments.
                                'tube': makes tubes
        ====================  ==================================================
        """
        args = ['pos', 'color', 'width', 'mode', 'antialias', 'direction', 'dual']
        for k in kwds.keys():
            if k not in args:
                raise Exception('Invalid keyword argument: %s (allowed arguments are %s)' % (k, str(args)))
        self.antialias = False
        self.direction = 'auto'
        self.vertices  = 10
        for arg in args:
            if arg in kwds:
                setattr(self, arg, kwds[arg])
                #self.vbo.pop(arg, None)
        self.update()

    def initializeGL(self):
        pass

    def _drawTube(self):
        '''
        Draw the line a s cylinder 
        as the line width is not supported
        under normal circumstances
        '''
        glBegin(GL_TRIANGLE_FAN)#drawing the back circle
        glVertex(*self.pos[0].tolist())
        for i in range(self._circle_points.shape[1]):
            glVertex(*self._circle_points[0,i].tolist())
        glEnd()

        glBegin(GL_TRIANGLE_FAN)#drawing the back circle
        glVertex(*self.pos[-1].tolist())
        for i in range(self._circle_points.shape[1]):
            glVertex(*self._circle_points[-1,i].tolist())
        glEnd()

        glBegin(GL_TRIANGLE_STRIP)#draw the tube
        for j in range(self.pos.shape[0]-1):
            for i in range(self.vertices+1):
                glVertex(*self._circle_points[j+1,i].tolist())
                glVertex(*self._circle_points[j,i].tolist())
        glEnd()

    def _preprocess(self):
        '''
        To avoid the computation of all elements on 
        any frame redraw the values are buffered here
        '''
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glColor4f(*self.color)

        if self.direction in ['x', 'y', 'z']:
            self._template = np.zeros((self.vertices + 1, 3))
            
            for i in range(self.vertices+1):
                if self.direction == 'z':
                    self._template[i] = np.array([
                        self.width * math.cos(2 * math.pi * (i/self.vertices)),  
                        self.width * math.sin(2 * math.pi * (i/self.vertices)), 
                        0])
                elif self.direction == 'x':
                    self._template[i] = np.array([
                        0,  
                        self.width * math.cos(2 * math.pi * (i/self.vertices)), 
                        self.width * math.sin(2 * math.pi * (i/self.vertices))])
                elif self.direction == 'y':
                    self._template[i] = np.array([
                        self.width * math.cos(2 * math.pi * (i/self.vertices)),  
                        0, 
                        self.width * math.sin(2 * math.pi * (i/self.vertices))])

            self._circle_points = np.zeros((self.pos.shape[0], self.vertices+1, 3))
            for j in range(self.pos.shape[0]):
                self._circle_points[j,:,:] = self._template+self.pos[j]

        elif self.direction == 'auto': 
            self._template = np.zeros((3,self.vertices + 1, 3))
            for i in range(self.vertices+1):
                self._template[0,i] = np.array([
                    self.width * math.cos(2 * math.pi * (i/self.vertices)),  
                    self.width * math.sin(2 * math.pi * (i/self.vertices)), 
                    0])
                self._template[1,i] = np.array([
                    0,  
                    self.width * math.cos(2 * math.pi * (i/self.vertices)), 
                    self.width * math.sin(2 * math.pi * (i/self.vertices))])
                self._template[2,i] = np.array([
                    self.width * math.cos(2 * math.pi * (i/self.vertices)),  
                    0, 
                    self.width * math.sin(2 * math.pi * (i/self.vertices))])

            self._circle_points = np.zeros((self.pos.shape[0], self.vertices+1, 3))
            for j in range(self.pos.shape[0]-1):
                vec = (self.pos[j+1]-self.pos[j]) / np.linalg.norm(self.pos[j+1]-self.pos[j])
                new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
                new_y = np.array([vec[1],-vec[0],0])

                for i in range(self.vertices+1):
                    self._circle_points[j,i,:] = (
                        self.width * math.cos(2 * math.pi * (i/self.vertices)) * new_x
                        + self.width * math.sin(2 * math.pi * (i/self.vertices)) * new_y
                        +self.pos[j])

            vec = (self.pos[self.pos.shape[0]-1]-self.pos[self.pos.shape[0]-2]) / np.linalg.norm(self.pos[self.pos.shape[0]-1]-self.pos[self.pos.shape[0]-2])
            new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
            new_y = np.array([vec[1],-vec[0],0])

            for i in range(self.vertices+1):
                self._circle_points[self.pos.shape[0]-1,i,:] = (
                    self.width * math.cos(2 * math.pi * (i/self.vertices)) * new_x
                    + self.width * math.sin(2 * math.pi * (i/self.vertices)) * new_y
                    +self.pos[self.pos.shape[0]-1])

    def _drawLine(self):
        
        glEnableClientState(GL_VERTEX_ARRAY)

        try:
            glVertexPointerf(self.pos)
            
            if isinstance(self.color, np.ndarray):
                glEnableClientState(GL_COLOR_ARRAY)
                glColorPointerf(self.color)
            else:
                if isinstance(self.color, (str, QtGui.QColor)):
                    glColor4f(*fn.glColor(self.color))
                else:
                    glColor4f(*self.color)
            glLineWidth(self.width)
            
            if self.antialias:
                glEnable(GL_LINE_SMOOTH)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
                
            if self.mode == 'line_strip':
                glDrawArrays(GL_LINE_STRIP, 0, int(self.pos.size / self.pos.shape[-1]))
            elif self.mode == 'lines':
                glDrawArrays(GL_LINES, 0, int(self.pos.size / self.pos.shape[-1]))
            else:
                raise Exception("Unknown line mode '%s'. (must be 'lines' or 'line_strip')" % self.mode)
                
        finally:
            glDisableClientState(GL_COLOR_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)

    def paint(self):
        '''
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        '''
        if self.pos is None:
            return
        self.setupGLState()

        if self.mode == 'tube':
            self._preprocess()
            self._drawTube()
        else:
            self._drawLine()
