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
from PyQt5 import QtWidgets, QtGui, QtCore
from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import opengl as gl
import numpy as np


from OpenGL.GL import glReadPixels, GL_RGBA,  GL_FLOAT, glPixelStorei, GL_UNPACK_ALIGNMENT, glFlush, glFinish, glGetIntegerv, glGetDoublev, GL_PROJECTION_MATRIX, GL_VIEWPORT, GL_MODELVIEW_MATRIX

import OpenGL.GLU as GLU

#personal imports
from ..ploting.plot_items.shaders import ShaderConstructor
from ..model.parameter_class import ParameterHandler 

class MyGLViewWidget(gl.GLViewWidget):
    ''' 
    Override GLViewWidget with enhanced behavior and Atom integration.
    '''
    sigUpdate = QtCore.pyqtSignal()
    rayUpdate = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        '''
        '''
        gl.GLViewWidget.__init__(self)
        self._initialize(parent)
        self.setMouseTracking(True)
        self.pointer = gl.GLLinePlotItem(mode = 'line_strip')
        self.addItem(self.pointer)
        self.mouse_ray = np.array([[0,0,0],[0,0,0]])


    def _initialize(self, parent):
        '''
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        '''
        self._old_position = np.array([0.,0.,0.])

        self.handler = ParameterHandler(
            name = 'View options', 
            parent = parent) 

        self.handler.addParameter(
            'Show center',  True)

        self.handler.addParameter(
            'Center size', 0.5,
            method = self._setSphere)

        self.handler.addParameter(
            'Center position', [0.,0.,0.],
            names = ['x', 'y', 'z'],
            method = self._setCenter)

        self.handler.addParameter(
            'Camera position', [20.,45.,45.],
            names = ['distance', 'azimuth', 'elevation'],
            method = self._setCamera)

        self.mousePos = [None, None]

        self.handler.runAll()

    def _setSphere(self):
        '''
        Draw the sphere at the center of the 
        coordinates
        '''
        self.constructor = ShaderConstructor()
        self.shader_prog = self.constructor.getShader('orientation')
        self.sphere = gl.GLMeshItem(
            meshdata = gl.MeshData.sphere(10,10,self.handler['Center size']))
        self.sphere.setShader(self.shader_prog)

    def _setCenter(self):
        '''
        Draw the sphere at the center of the 
        coordinates
        '''
        self.pan(*(np.array(self.handler['Center position']) - self._old_position).tolist())
        self._old_position = np.array(self.handler['Center position'])

    def _setCamera(self):
        '''
        Draw the sphere at the center of the 
        coordinates
        '''
        self.setCameraPosition(
            distance    = self.handler['Camera position'][0],
            azimuth     = self.handler['Camera position'][1],
            elevation   = self.handler['Camera position'][2])

    def mousePressEvent(self, ev):
        ''' 
        Store the position of the mouse press for later use.
        '''
        super(MyGLViewWidget, self).mousePressEvent(ev)
        self._downpos = self.mousePos

        if self.handler['Show center']:
            self.addItem(self.sphere)
            self.sphere.resetTransform()
            self.sphere.translate(
                self.opts['center'][0],
                self.opts['center'][1],
                self.opts['center'][2])
        
    def mouseReleaseEvent(self, ev):
        ''' Allow for single click to move and right click for context menu.
        
        Also emits a sigUpdate to refresh listeners.
        '''
        super(MyGLViewWidget, self).mouseReleaseEvent(ev)
        if self._downpos == ev.pos():
            if ev.button() == 2:
                print('show context menu')
            elif ev.button() == 1:
                x = ev.pos().x() - self.width() / 2
                y = ev.pos().y() - self.height() / 2
                self.pan(-x, -y, 0, relative=True)

        self._prev_zoom_pos = None
        self._prev_pan_pos = None
        self.mousePos = [None, None]

        if self.handler['Show center']:
            self.removeItem(self.sphere)

        self.sigUpdate.emit()
        
    def evalKeyState(self):
        speed = 2.0
        if len(self.keysPressed) > 0:
            for key in self.keysPressed:
                if key == QtCore.Qt.Key_Right:
                    self.orbit(azim=-speed, elev=0)
                elif key == QtCore.Qt.Key_Left:
                    self.orbit(azim=speed, elev=0)
                elif key == QtCore.Qt.Key_Up:
                    self.orbit(azim=0, elev=-speed)
                elif key == QtCore.Qt.Key_Down:
                    self.orbit(azim=0, elev=speed)
                elif key == QtCore.Qt.Key_PageUp:
                    pass
                elif key == QtCore.Qt.Key_PageDown:
                    pass
                self.keyTimer.start(16)
        else:
            self.keyTimer.stop()

    def mouseMoveEvent(self, ev):
        '''
        manage the mouse move events
        '''
        if not self.mousePos == [None, None]:
            diff = ev.pos() - self.mousePos
            self.mousePos = ev.pos()
            
            if ev.buttons() == QtCore.Qt.LeftButton:
                self.handler['Camera position'] = [
                    self.handler['Camera position'][0],
                    -diff.x() + self.handler['Camera position'][1],
                    np.clip(self.handler['Camera position'][2] + diff.y(), -90, 90)]
                
            elif ev.buttons() == QtCore.Qt.MidButton:
                cPos = self.cameraPosition()
                cVec = self.opts['center'] - cPos
                dist = cVec.length()  ## distance from camera to center
                xDist = dist * 2. * np.tan(0.5 * self.opts['fov'] * np.pi / 180.)  ## approx. width of view at distance of center point
                xScale = xDist / self.width()
                zVec = QtGui.QVector3D(0,0,1)
                xVec = QtGui.QVector3D.crossProduct(zVec, cVec).normalized()
                yVec = QtGui.QVector3D.crossProduct(xVec, zVec).normalized()
                self.opts['center'] = (
                    self.opts['center'] 
                    + xVec * xScale * diff.x() 
                    + yVec * xScale * diff.y()  
                    + zVec * xScale * 0)

                self.handler['Center position'] = (np.round(
                    np.array([
                        round(self.opts['center'][0],4),
                        round(self.opts['center'][1],4),
                        round(self.opts['center'][2],4)]) 
                    - self._old_position, decimals = 4)).tolist() 

            elif ev.buttons() == QtCore.Qt.RightButton:
                cPos = self.cameraPosition()
                cVec = self.opts['center'] - cPos
                dist = cVec.length()  ## distance from camera to center
                xDist = dist * 2. * np.tan(0.5 * self.opts['fov'] * np.pi / 180.)  ## approx. width of view at distance of center point
                xScale = xDist / self.width()
                zVec = QtGui.QVector3D(0,0,1)
                xVec = QtGui.QVector3D.crossProduct(zVec, cVec).normalized()
                yVec = QtGui.QVector3D.crossProduct(xVec, zVec).normalized()
                self.opts['center'] = (
                    self.opts['center'] 
                    + xVec * xScale * diff.x() 
                    + yVec * xScale * 0
                    + zVec * xScale * diff.y())

                self.handler['Center position'] = (np.round(
                    np.array([
                        round(self.opts['center'][0],4),
                        round(self.opts['center'][1],4),
                        round(self.opts['center'][2],4)]) 
                    - self._old_position, decimals = 4)).tolist() 

            self.sphere.resetTransform()
            self.sphere.translate(
                self.opts['center'][0],
                self.opts['center'][1],
                self.opts['center'][2])
        else:
            ray = self._getPickingRay(ev.x(), ev.y())
            self.pointer.setData(pos =np.array([self.cameraPosition(), ray[:3]]))
            self.mouse_ray = np.array([self.cameraPosition(), ray[:3]])
            self.rayUpdate.emit()
            
    def _getPickingRay(self,x,y):
        '''
        Process the ray for the current
        mouse position
        '''
        viewport    = glGetIntegerv(GL_VIEWPORT)
        model_mat   = np.array(glGetDoublev(GL_MODELVIEW_MATRIX))
        proj_mat    = np.array(glGetDoublev(GL_PROJECTION_MATRIX))
        
        win_coord   = (x, viewport[3] - y)
        
        near_point  = np.array(GLU.gluUnProject(
            win_coord[0], win_coord[1], 0.0, 
            model_mat, proj_mat, viewport))
        far_point   = np.array(GLU.gluUnProject(
            win_coord[0], win_coord[1], 1.0, 
            model_mat, proj_mat, viewport))

        return far_point - near_point

            
    def wheelEvent(self, ev):
        delta = 0

        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        if (ev.modifiers() & QtCore.Qt.ControlModifier):
            self.opts['fov'] *= 0.999**delta
        else:
            self.opts['distance'] *= 0.999**delta

        self.handler['Camera position'] = [
            round(self.opts['distance'],4),
            self.handler['Camera position'][1],
            self.handler['Camera position'][2]]

    def setBackground(self, color):
        '''
        Set the canvas background
        '''
        self.setBackgroundColor(color)
