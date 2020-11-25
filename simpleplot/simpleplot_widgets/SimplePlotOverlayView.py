
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

#public dependencies
from simpleplot.pyqtgraph.pyqtgraph.GraphicsScene import mouseEvents
from PyQt5 import QtWidgets, QtGui, QtCore

class SimplePlotOverlayView(QtWidgets.QGraphicsView):
    '''
    This is an inherited class of the QGraphicsview
    which will propagate its signals to the underlaying
    child class if possible
    '''
    sigTakenMouse = QtCore.pyqtSignal()
    sigReleasedMouse = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        '''
        The contructor
        '''
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("background: transparent")
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        self.setMouseTracking(True)

        self._mouse_captured = False

    def _propagateMouse(self, event:QtGui.QMouseEvent)->bool:
        '''
        This is a helper method supposed to tell the 
        underneath machinery if this should be 
        transmited or not
        '''
        if not self.parent() is None and not self.scene() is None:
            pos = self.mapToScene(event.pos())
            items = [hasattr(item,'ignore_for_mouse') for item in self.scene().items(pos)]
            if all(items) :
                if self._mouse_captured:
                    self.sigReleasedMouse.emit()
                    self._mouse_captured = False
                return True

        if not self._mouse_captured:
            self.sigTakenMouse.emit()
            self._mouse_captured = True
        return False

    def mouseMoveEvent(self, event:QtGui.QMouseEvent):
        '''
        Reimnplementation of the mouse move event
        that tries to proagate th event...
        '''
        super().mouseMoveEvent(event)

        if self._propagateMouse(event):
            self.parent().mouseMoveEvent(event)

    def mousePressEvent(self, event:QtGui.QMouseEvent):
        '''
        Reimnplementation of the mouse press event
        that tries to proagate th event...
        '''
        super().mousePressEvent(event)

        if self._propagateMouse(event):
            self.parent().mousePressEvent(event)

    def mouseReleaseEvent(self, event:QtGui.QMouseEvent):
        '''
        Reimnplementation of the mouse release event
        that tries to proagate th event...
        '''
        super().mouseReleaseEvent(event)
        
        if self._propagateMouse(event):
            self.parent().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event:QtGui.QMouseEvent):
        '''
        Reimnplementation of the mouse double click event
        that tries to proagate th event...
        '''
        super().mouseDoubleClickEvent(event)
        
        if self._propagateMouse(event):
            self.parent().mouseDoubleClickEvent(event)

    def wheelEvent(self, event:QtGui.QWheelEvent):
        '''
        Reimnplementation of the mouse double click event
        that tries to proagate th event...
        '''
        if self._propagateMouse(event):
            self.parent().wheelEvent(event)
