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
from .SimplePlotItem import SimplePlotItem
from pyqtgraph import PlotWidget

class SimplePlotWidget(PlotWidget):

    def __init__(self, canvas):
        PlotWidget.__init__(self)
        self.plotItem.sigRangeChanged.disconnect(self.viewRangeChanged)
        self.plotItem = SimplePlotItem()
        self.setCentralItem(self.plotItem)
        ## Explicitly wrap methods from plotItem
        ## NOTE: If you change this list, update the documentation above as well.
        for m in ['addItem', 'removeItem', 'autoRange', 'clear', 'setXRange', 
                  'setYRange', 'setRange', 'setAspectLocked', 'setMouseEnabled', 
                  'setXLink', 'setYLink', 'enableAutoRange', 'disableAutoRange', 
                  'setLimits', 'register', 'unregister', 'viewRect']:
            setattr(self, m, getattr(self.plotItem, m))
        #QtCore.QObject.connect(self.plotItem, QtCore.SIGNAL('viewChanged'), self.viewChanged)
        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)
        self.setAntialiasing(True)
        self.canvas = canvas

    def mouseMoveEvent(self, ev):
        '''
        mouse move event
        '''
        self.canvas.artist.mouse_move(ev)
        super(PlotWidget, self).mouseMoveEvent(ev)

    def mousePressEvent(self, ev):
        '''
        mouse press event
        '''
        self.canvas.artist.mouse_press(ev)
        super(PlotWidget, self).mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        '''
        mouse release event
        '''
        self.canvas.artist.mouse_release(ev)
        super(PlotWidget, self).mouseReleaseEvent(ev)
