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

from ..pyqtgraph.pyqtgraph.GraphicsScene.mouseEvents  import MouseDragEvent
from ..pyqtgraph.pyqtgraph.Point  import Point


class SimpleMouseDragEvent(MouseDragEvent):
    ''' 
    Override GLViewWidget with enhanced behavior and Atom integration.
    '''
    def __init__(self, moveEvent, pressEvent, lastEvent, button, start=False, finish=False):
        self.start = start
        self.finish = finish
        self.accepted = False
        self.currentItem = None

        self._x = moveEvent.x()
        self._y = moveEvent.y()

        if not lastEvent is None:
            self._last_x = lastEvent._x
            self._last_y = lastEvent._y 
        else:
            self._last_x = pressEvent.x()
            self._last_y = pressEvent.y()

        self._button        = button
        self._modifiers     = moveEvent.modifiers()
        self._press_event   = pressEvent
        self.acceptedItem   = None

    def buttonDownPos(self, btn=None):
        """
        Return the position of the mouse at the time the drag was initiated
        in the coordinate system of the item that the event was delivered to.
        """
        if btn is None:
            btn = self.button()
        return Point(self._press_event.x(), self._press_event.y())

    def lastPos(self):
        """
        Return the previous position of the mouse in the coordinate system of the item
        that the event was delivered to.
        """
        return Point(self._last_x, self._last_y)

    def pos(self):
        """
        Return the current position of the mouse in the coordinate system of the item
        that the event was delivered to.
        """
        return Point(self._x, self._y)
