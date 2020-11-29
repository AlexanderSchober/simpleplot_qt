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
from typing import Union

import moderngl
import numpy as np
# import dependencies
from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets

from .gl_context_class import ContextClass
# pylint: disable=E0202
from .mouse_drag_event import SimpleMouseDragEvent
from ..artist.camera_2d import Camera2D
from ..artist.camera_3d import Camera3D
from ..artist.light import LightSource


# personal imports

class MyGLViewWidget(QtOpenGL.QGLWidget):
    """
    Override GLViewWidget with enhanced behavior and Atom integration.
    """
    resized_signal = QtCore.pyqtSignal()
    shown = QtCore.pyqtSignal()
    sigUpdate = QtCore.pyqtSignal()
    rayUpdate = QtCore.pyqtSignal()

    def __init__(self, canvas, parent=None):
        """
        """
        super(MyGLViewWidget, self).__init__(self.qglFormat(), parent)
        self.setMouseTracking(True)
        self._context_class = ContextClass(self)
        self._canvas = canvas
        self._initialize()
        self._connect()

    def qglFormat(self) -> QtOpenGL.QGLFormat:
        """
        Returns the initial qgl fomat for this
        widget to make sure we run on opengl 4,1
        """
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(4, 1)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        return fmt

    def initializeGL(self):
        """
        Initialise the system
        """
        self._context_class.initializeGL(self.size().width(), self.size().height())

    def context(self) -> moderngl.Context:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._context_class.context()

    def contextClass(self) -> ContextClass:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._context_class

    def addItem(self, item):
        """
        Add an item to be drawn
        """
        self._context_class.addItem(item)

    def addGraphItem(self, item):
        """
        Add an item to be drawn
        """
        self._context_class.addGraphItem(item)

    def removeItem(self, item):
        """
        Remove an item
        """
        self._context_class.removeItem(item)

    def removeGraphItem(self, item):
        """
        Remove an item
        """
        self._context_class.removeGraphItem(item)

    def paintGL(self):
        """
        This is the overwrite of the paintGL method. 
        Note that for some reason it is recquired for
        the first draw and can then be set to point to
        a dummy to allow the contextClass to handle the
        drawing process.
        """
        self.contextClass().render()

    def _initialize(self):
        """
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        """
        self._last_drag = None
        self._old_position = np.array([0., 0., 0.])
        self.mousePos = [None, None]
        self._camera = None

    def _connect(self):
        """
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        """
        self._context_class.update.connect(self.update)
        self._canvas.mouse.bind('release', self._contextMenu, 'context', 2, True)
        self._canvas.mouse.bind('press', self._showAxes, 'show_center', 1)
        self._canvas.mouse.bind('release', self._hideAxes, 'hide_center', 1)
        self._canvas.mouse.bind('press', self._showAxes, 'show_center', 2)
        self._canvas.mouse.bind('release', self._hideAxes, 'hide_center', 2)
        self._canvas.mouse.bind('press', self._showAxes, 'show_center', 0)
        self._canvas.mouse.bind('release', self._hideAxes, 'hide_center', 0)
        self._canvas.mouse.bind('move', self._rayMovement, 'ray', 1)
        self._canvas.mouse.bind('drag', self._pan, 'pan', 1)
        self._canvas.mouse.bind('drag', self._moveXY, 'shift_xy', 2)
        self._canvas.mouse.bind('drag', self._moveXZ, 'shift_yz', 0)

    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._camera = camera
        self._context_class.setCamera(camera)
        self._canvas.mouse.bind('move', self._camera.setMousePos, 'camera', 1)

    def setLightSource(self, light: LightSource) -> None:
        """
        Set the canmera as the local item
        """
        self._light = light
        self._context_class.setLightSource(light)

    def mousePressEvent(self, ev):
        """
        Store the position of the mouse press for later use.
        """
        self._press_event = ev
        self._press_button = self._press_event.button()
        self._canvas.mouse.press(ev)

    def mouseReleaseEvent(self, ev):
        """
        """
        self._canvas.mouse.release(ev)
        if not self._last_drag is None:
            self._last_drag = None

    def mouseMoveEvent(self, ev):
        """
        manage the mouse move events
        """
        if len(self._canvas.mouse.pressed) == 0:
            self._canvas.mouse.move(ev)
        else:
            event = SimpleMouseDragEvent(
                ev,
                self._press_event,
                self._last_drag,
                self._press_button,
                start=True,
                finish=False)

            self._last_drag = event
            self._canvas.mouse.drag(self._last_drag)

    def wheelEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Manage the wheel event in order
        to do zoom in and out

        Parameters:
        -------------------------------------
        event : QtGui.QMouseEvent
            The mouse event as wheelevent
        """
        delta = event.angleDelta().x()
        if delta == 0:
            delta = event.angleDelta().y()
        self._camera.zoom(0.999, delta)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """
        verride the normal show behaviour
        """
        super().showEvent(event)
        self.shown.emit()

    def evalKeyState(self):
        if len(self.keysPressed) > 0:
            for key in self.keysPressed:
                if key == QtCore.Qt.Key_Right:
                    self._camera.strafe_right()
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

    def _contextMenu(self, ev):
        """
        Shift the view
        """
        if self._last_drag is None:
            print('show context menu')

    def _pan(self, x, y, drag_start, drag_end):
        """
        This function will handle the paning of the
        openGl view and send it to the camera 
        in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]

        self._camera.pan(diff_x, diff_y)

    def _moveXZ(self, x, y, drag_start, drag_end):
        """
        This function will handle the moving of the
        openGl view in the x and y plane and send 
        it to the camera in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
        self._camera.moveXZ(diff_x, diff_y, self.width())

    def _moveXY(self, x, y, drag_start, drag_end):
        """
        This function will handle the moving of the
        openGl view in the x and y plane and send 
        it to the camera in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
        self._camera.moveXY(diff_x, diff_y, self.width())

    def setBackground(self, color: QtGui.QColor):
        """
        Set the background of the draw context

        Parameters:
        -------------------------------------
        color : QtGui.QColor
            The color to be set internally
            to be set as the background
        """
        self.contextClass()._background_color = [val / 255 for val in color.getRgb()]
        self.contextClass().render()

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> bool:
        """
        Manage the resize event before sending it 
        to the inherited class

        Parameters:
        -------------------------------------
        ev : QtGui.QResizeEvent
        """
        self.resized_signal.emit()
        if not self.contextClass() == None:
            self.contextClass().resizeEvent(
                0, 0,
                ev.size().width() * self.devicePixelRatio(),
                ev.size().height() * self.devicePixelRatio())

        super().resizeEvent(ev)

    def _showAxes(self):
        """
        Show the movement ball
        """
        self._canvas.childFromName('Artist').childFromName('Orientation Axes').drag_on = True
        self._canvas.childFromName('Artist').childFromName('Orientation Axes').setParameters()

    def _hideAxes(self):
        """
        Show the movement ball
        """
        self._canvas.childFromName('Artist').childFromName('Orientation Axes').drag_on = False
        self._canvas.childFromName('Artist').childFromName('Orientation Axes').setParameters()

    def _rayMovement(self, x, y):
        """
        Manage the ray movement
        """
        # fix the screen
        screens = QtWidgets.QApplication.instance().screens()
        num = QtWidgets.QApplication.instance().desktop().screenNumber(self)
        ratio = QtGui.QScreen.devicePixelRatio(screens[num])
        ray = self._context_class.getPickingRay(x * ratio, y * ratio)

        self._context_class.pickRays()

        # save the new ray and emit ray
        # self.mouse_ray = np.array([self._camera['Camera position'], ray[:3]])
        # self.rayUpdate.emit()
