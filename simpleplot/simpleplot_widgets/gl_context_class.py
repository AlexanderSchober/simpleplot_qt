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
from PyQt5 import QtCore
from pyrr import Vector4

from ..artist.camera_2d import Camera2D
from ..artist.camera_3d import Camera3D
from ..artist.light import LightSource


class ContextClass(QtCore.QObject):
    update = QtCore.pyqtSignal()

    def __init__(self, parent):
        """
        Init the class
        """
        super(ContextClass, self).__init__(parent=parent)
        self.items = []
        self.graph_items = []
        self._background_color = (0, 0, 0)

    def context(self) -> moderngl.Context:
        """
        Getter function for the context for 
        doing tests for example
        """
        if hasattr(self, '_moderngl_context'):
            return self._moderngl_context
        else:
            return None

    def addItem(self, item):
        """
        Add an item to be drawn
        """
        self.items.append(item)
        if hasattr(item, 'setRenderer'):
            item.setRenderer(self)
        if hasattr(item, 'initializeGL'):
            item.initializeGL()

        self.setMVP(item)
        self.setLight(item)
        self.render()

    def addGraphItem(self, item):
        """
        Add an item to be drawn
        """
        self.graph_items.append(item)
        if hasattr(item, 'setRenderer'):
            item.setRenderer(self)
        if hasattr(item, 'initializeGL'):
            item.initializeGL()

        self.setMVP(item)
        self.setLight(item)
        self.render()

    def removeItem(self, item):
        """
        Remove an item
        """
        self.items.remove(item)
        self.render()

    def removeGraphItem(self, item):
        """
        Remove an item
        """
        self.graph_items.remove(item)
        self.render()

    def initializeGL(self, width: float, height: float) -> None:
        """
        Initialisation of the  moderngl system

        Parameters:
        -------------------------------------
        width : float
            The width of the resize
        height : float
            The height of the resize
        """
        self._moderngl_context = moderngl.create_context()
        self._moderngl_context.viewport = (0, 0, width, height)
        self.render()

    def render(self):
        """
        This is the main rendering routine
        """
        if not hasattr(self, '_moderngl_context'):
            return

        self._moderngl_context.screen.use()
        self._moderngl_context.clear(*self._background_color, depth=1.0)
        self._moderngl_context.blend_func = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE, moderngl.ONE
        )
        self._moderngl_context.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
        self.drawItemTree()
        self.update.emit()

    def drawItemTree(self):
        """
        This fucntion will draw the items in the self.items
        list through the poaint methods
        """
        items = self.items + self.graph_items
        items.sort(key=lambda a: a.depthValue())
        for item in items:
            item.paint()

    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._camera = camera
        if hasattr(self, '_moderngl_context'):
            self._camera.setRatio(self._moderngl_context.viewport[2] / self._moderngl_context.viewport[3])

    def setMVP(self, item=None) -> None:
        """
        Set all the mvps for the items
        in the item tree that support it
        """
        if item is None:
            items = self.items + self.graph_items
            items.sort(key=lambda a: a.depthValue())
        else:
            items = [item]

        for item in items:
            if hasattr(item, 'setMVP'):
                item.setMVP(**self._camera.getDict())

        self.render()

    def setLightSource(self, light: LightSource) -> None:
        """
        Set the canmera as the local item
        """
        self._light = light

    def setLight(self, item=None) -> None:
        """
        Set all the mvps for the items
        in the item tree that support it
        """
        if item is None:
            items = self.items + self.graph_items
            items.sort(key=lambda a: a.depthValue())
        else:
            items = [item]

        for item in items:
            if hasattr(item, 'setLight'):
                item.setLight(
                    self._light.light_bool,
                    self._light.light_pos,
                    self._light.light_color)

        self.render()

    def resizeEvent(self, x: float, y: float, width: float, height: float) -> None:
        """
        Manage the resize event before sending it 
        to the inherited class

        Parameters:
        -------------------------------------
        x : float
            The x position of the resize
        y : float
            The y position of the resize
        width : float
            The width of the resize
        height : float
            The height of the resize
        """
        if not self.context() is None:
            self.context().viewport = (x, y, width, height)
            if self._camera is not None and self.context().viewport[3] != 0:
                self._camera.setRatio(
                    self.context().viewport[2] / self.context().viewport[3])
                self._camera.setScreenSize(width, height)

        self.render()

    def getPickingRay(self, x: int, y: int):
        """
        Process the ray for the current
        mouse position

        Parameters:
        -------------------------------------
        x : int
            The x position of the mouse on the screen
        y : float
            The y position of the mouse on the screen
        """
        viewport = self.context().viewport
        model_mat = self._camera.mat_look_at.inverse
        proj_mat = self._camera.mat_projection.inverse

        win_coord = (x, viewport[3] - y)
        near_point = model_mat * proj_mat * Vector4([win_coord[0], win_coord[1], 0.0, 1.0])
        far_point = model_mat * proj_mat * Vector4([win_coord[0], win_coord[1], 1.0, 1.0])

        return far_point - near_point

    def pickRays(self):
        """
        This fucntion will draw the items in the self.items
        list through the poaint methods
        """
        items = self.items + self.graph_items
        items.sort(key=lambda a: a.depthValue())
        for item in items:
            if hasattr(item, 'pickRay'):
                item.pickRay()
