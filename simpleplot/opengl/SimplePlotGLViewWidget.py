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
from PyQt5 import QtGui, QtCore, QtOpenGL
from simpleplot.artist.interaction import InteractionHandler
from simpleplot.artist.space import SpaceRepresentation
from .gl_context_class import ContextClass

# pylint: disable=E0202
from .mouse_drag_event import SimpleMouseDragEvent
from ..artist.camera_2d import Camera2D
from ..artist.camera_3d import Camera3D
from ..artist.light import LightSource


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
        self._overay_context_class = ContextClass(self)
        self._canvas = canvas
        self._interaction_handler = InteractionHandler(self._canvas, self._context_class)
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
        self._overay_context_class.initializeGL(self.size().width(), self.size().height())

    def context(self) -> moderngl.Context:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._context_class.context()

    def overlayContext(self) -> moderngl.Context:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._overay_context_class.context()

    def contextClass(self) -> ContextClass:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._context_class

    def overlayContextClass(self) -> ContextClass:
        """
        Getter function for the context for 
        doing tests for example
        """
        return self._overay_context_class

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
        pass
        # self.contextClass().render()

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

    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._camera = camera
        self._context_class.setCamera(camera)
        self._interaction_handler.setCamera(camera)
        self._canvas.mouse.bind('move', self._camera.setMousePos, 'camera', 1)

    def setSpace(self, space: SpaceRepresentation) -> None:
        """
        Set the canmera as the local item
        """
        self._space = space
        self._context_class.setSpace(space)
        self._interaction_handler.setSpace(space)

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
        self.overlayContextClass().render()

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> bool:
        """
        Manage the resize event before sending it 
        to the inherited class

        Parameters:
        -------------------------------------
        ev : QtGui.QResizeEvent
        """
        if self.contextClass() is not None:
            self.contextClass().resizeEvent(
                0, 0,
                ev.size().width(),
                ev.size().height())
            
        if self.overlayContextClass() is not None:
            self.overlayContextClass().resizeEvent(
                0, 0,
                ev.size().width(),
                ev.size().height())
            
        self.resized_signal.emit()

        super().resizeEvent(ev)