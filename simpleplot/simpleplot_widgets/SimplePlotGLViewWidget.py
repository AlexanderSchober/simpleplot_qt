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
import numpy as np

from ..pyqtgraph            import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph  import opengl as gl
from .mouse_drag_event      import SimpleMouseDragEvent

from OpenGL.GL import glReadPixels, GL_RGBA,  GL_FLOAT, glPixelStorei, GL_UNPACK_ALIGNMENT, glFlush, glFinish, glGetIntegerv, glGetDoublev, GL_PROJECTION_MATRIX, GL_VIEWPORT, GL_MODELVIEW_MATRIX

import OpenGL.GLU as GLU

#personal imports
from ..ploting.plot_geometries.shaders      import ShaderConstructor
from ..model.parameter_class                import ParameterHandler 

class MyGLViewWidget(gl.GLViewWidget):
    ''' 
    Override GLViewWidget with enhanced behavior and Atom integration.
    '''
    sigUpdate = QtCore.pyqtSignal()
    rayUpdate = QtCore.pyqtSignal()
    
    def __init__(self,canvas, parent = None):
        '''
        '''
        gl.GLViewWidget.__init__(self)
        self.canvas = canvas
        self._initialize(canvas)
        self._connect()
        self.setMouseTracking(True)
        self.mouse_ray = np.array([[0,0,0],[0,0,0]])
        self._last_drag = None

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

    def _connect(self):
        '''
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        '''
        self.canvas.mouse.bind('release',self._shift,'shit',1, True)
        self.canvas.mouse.bind('release',self._contextMenu,'context',2, True)

        self.canvas.mouse.bind('press',self._showBall,'show_center',1)
        self.canvas.mouse.bind('release',self._hideBall,'hide_center',1)
        self.canvas.mouse.bind('press',self._showBall,'show_center',2)
        self.canvas.mouse.bind('release',self._hideBall,'hide_center',2)
        self.canvas.mouse.bind('press',self._showBall,'show_center',0)
        self.canvas.mouse.bind('release',self._hideBall,'hide_center',0)

        self.canvas.mouse.bind('move',self._rayMovement,'ray',1)

        self.canvas.mouse.bind('drag',self._pan,'pan',1)
        self.canvas.mouse.bind('drag',self._moveXY,'shift_xy',2)
        self.canvas.mouse.bind('drag',self._moveXZ,'shift_yz',0)

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
        self._press_event = ev
        self._press_button = self._press_event.button()
        self.canvas.mouse.press(ev)

    def mouseReleaseEvent(self, ev):
        ''' 
        '''
        self.canvas.mouse.release(ev)
        if not self._last_drag is None:
            self._last_drag = None

    def mouseMoveEvent(self, ev):
        '''
        manage the mouse move events
        '''
        if len(self.canvas.mouse.pressed) == 0:
            self.canvas.mouse.move(ev)
        else:
            event = SimpleMouseDragEvent(
                ev, 
                self._press_event, 
                self._last_drag, 
                self._press_button,
                start   = True, 
                finish  = False)

            self._last_drag = event
            self.canvas.mouse.drag(self._last_drag)

    def _showBall(self):
        '''
        Show the movement ball
        '''
        if self.handler['Show center']:
            self.addItem(self.sphere)
            self.sphere.resetTransform()
            self.sphere.translate(
                self.opts['center'][0],
                self.opts['center'][1],
                self.opts['center'][2])
        
    def _hideBall(self):
        '''
        Show the movement ball
        '''
        if self.handler['Show center']:
            self.removeItem(self.sphere)

    def _shift(self, ev):
        '''
        Shift the view
        '''
        if self._last_drag is None:
            x = ev.pos().x() - self.width() / 2
            y = ev.pos().y() - self.height() / 2
            self.pan(-x, -y, 0, relative=True)
        
    def _contextMenu(self, ev):
        '''
        Shift the view
        '''
        if self._last_drag is None:
            print('show context menu')

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

    def _pan(self, x, y, drag_start, drag_end):
        '''
        move
        '''
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
        self.handler['Camera position'] = [
            self.handler['Camera position'][0],
            -diff_x + self.handler['Camera position'][1],
            np.clip(self.handler['Camera position'][2] + diff_y, -90, 90)]
                
    def _moveXZ(self, x, y, drag_start, drag_end):
        '''
        move
        '''
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
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
            + xVec * xScale * np.array(diff_x)
            + yVec * xScale * np.array(diff_y) 
            + zVec * xScale * 0)

        self.handler['Center position'] = (np.round(
            np.array([
                round(self.opts['center'][0],4),
                round(self.opts['center'][1],4),
                round(self.opts['center'][2],4)]) 
            - self._old_position, decimals = 4)).tolist() 

    def _moveXY(self, x, y, drag_start, drag_end):
        '''
        move
        '''
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
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
            + xVec * xScale * np.array(diff_x)
            + yVec * xScale * 0
            + zVec * xScale * np.array(diff_y))

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

    def _rayMovement(self, x, y):
        '''
        Manage the ray movement
        '''
        # fix the screen
        screens = QtWidgets.QApplication.instance().screens()
        num     = QtWidgets.QApplication.instance().desktop().screenNumber(self)
        ratio   = QtGui.QScreen.devicePixelRatio(screens[num])
        ray     = self._getPickingRay(x*ratio, y*ratio)

        #save the new ray and emit ray
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
        
        # win_coord   = (x*2, viewport[3] - y*2)
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
