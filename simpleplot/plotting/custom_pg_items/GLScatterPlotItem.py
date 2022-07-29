from OpenGL.GL import *
from OpenGL.arrays import vbo
from ...pyqtgraph.pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from ...pyqtgraph.pyqtgraph.opengl import shaders
from ...pyqtgraph.pyqtgraph import QtGui
from ...pyqtgraph.pyqtgraph import functions as fn
import numpy as np

__all__ = ['GLScatterPlotItem']

class GLScatterPlotItem(GLGraphicsItem):
    """Draws points at a list of 3D positions."""
    
    def __init__(self, **kwds):
        GLGraphicsItem.__init__(self)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = []
        self.size = 10
        self.color = [1.0,1.0,1.0,0.5]
        self.pxMode = True
        self.setData(**kwds)
    
    def setData(self, **kwds):
        """
        Update the data displayed by this item. All arguments are optional; 
        for example it is allowed to update spot positions while leaving 
        colors unchanged, etc.
        
        ====================  ==================================================
        **Arguments:**
        pos                   (N,3) array of floats specifying point locations.
        color                 (N,4) array of floats (0.0-1.0) specifying
                              spot colors OR a tuple of floats specifying
                              a single color for all spots.
        size                  (N,) array of floats specifying spot sizes or 
                              a single value to apply to all spots.
        pxMode                If True, spot sizes are expressed in pixels. 
                              Otherwise, they are expressed in item coordinates.
        ====================  ==================================================
        """
        args = ['pos', 'color', 'size', 'pxMode']
        for k in kwds.keys():
            if k not in args:
                raise Exception('Invalid keyword argument: %s (allowed arguments are %s)' % (k, str(args)))
            
        args.remove('pxMode')
        for arg in args:
            if arg in kwds:
                setattr(self, arg, kwds[arg])
                #self.vbo.pop(arg, None)
                
        self.pxMode = kwds.get('pxMode', self.pxMode)
        self.update()

    def initializeGL(self):
        
        ## Generate texture for rendering points
        w = 64
        def fn(x,y):
            r = ((x-w/2.)**2 + (y-w/2.)**2) ** 0.5
            return 255 * (w/2. - np.clip(r, w/2.-1.0, w/2.))
        pData = np.empty((w, w, 4))
        pData[:] = 255
        pData[:,:,3] = np.fromfunction(fn, pData.shape[:2])
        #print pData.shape, pData.min(), pData.max()
        pData = pData.astype(np.ubyte)
        
        if getattr(self, "pointTexture", None) is None:
            self.pointTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.pointTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, pData.shape[0], pData.shape[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, pData)
        
        self.shader = shaders.getShaderProgram('pointSprite')
        
    def paint(self):
        self.setupGLState()
                                
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_NOTEQUAL, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)


        for i in range(len(self.pos)):
            pos = self.pos[i]
            
            if isinstance(self.color, np.ndarray):
                color = self.color[i]
            else:
                color = self.color
            if isinstance(self.color, QtGui.QColor):
                color = fn.glColor(self.color)
                
            if isinstance(self.size, np.ndarray):
                size = self.size[i]
            else:
                size = self.size
                
            pxSize = self.view().pixelSize(QtGui.QVector3D(*pos))
            
            glPointSize(size / pxSize)
            glBegin( GL_POINTS )
            glColor4f(*color)
            glVertex3f(*pos)
            glEnd()
