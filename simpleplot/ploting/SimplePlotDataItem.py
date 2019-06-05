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

from ..pyqtgraph import pyqtgraph as pg
from PyQt5 import QtCore


class SimplePlotDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # Need to switch off the "has no contents" flag
        self.setFlags(self.flags() & ~self.ItemHasNoContents)

    # def mouseDragEvent(self, ev):
    #     self.parentItem().parentItem().parentItem().canvas.artist.zoomer.end_zoom(quiet = True)
    #     print("drag")
    #     if ev.button() != QtCore.Qt.LeftButton:
    #         ev.ignore()
    #         return

    #     if ev.isStart():
    #         print("start")
    #     elif ev.isFinish():
    #         self.parentItem().parentItem().parentItem().canvas.artist.zoomer.listen()
    #         print("finish")

    # def shape(self):
    #     # Inherit shape from the curve item
    #     return self.curve.shape()

    # def boundingRect(self):
    #     # All graphics items require this method (unless they have no contents)
    #     return self.shape().boundingRect()

    # def paint(self, p, *args):
    #     # All graphics items require this method (unless they have no contents)
    #     return

    # def hoverEvent(self, ev):
    #     # This is recommended to ensure that the item plays nicely with 
    #     # other draggable items
    #     ev.acceptDrags(QtCore.Qt.LeftButton)

