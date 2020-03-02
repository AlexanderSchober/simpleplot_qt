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

from PyQt5 import QtWidgets, QtGui, QtCore
from ...pyqtgraph import pyqtgraph as pg
import numpy as np

class GraphView(pg.GraphicsObject):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self, **opts):
        '''

        '''
        super().__init__(opts.get('parent', None))

        self._parameters = {}
        self._parameters['positions'] = [2.,2.]
        self._parameters['angle'] = 0.
        self._parameters['brush'] = QtGui.QBrush()
        self._parameters['pen'] = QtGui.QPen()
        self._parameters['Z'] = 0
        self._parameters['movable'] = False
        
    def render(self):
        '''
        '''
        if self._parameters['movable']:
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        else:
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)

        self.setZValue(self._parameters['Z'])
        self.prepareGeometryChange()
        self.update()

    def inPainter(self, p, *args):
        '''
        override the paint method
        '''
        p.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        p.setBrush(self._parameters['brush'])
        p.setPen(self._parameters['pen'])
        p.translate(self._parameters['positions'][0], self._parameters['positions'][1])
        p.rotate(self._parameters['angle'])

    def outPainter(self, p, *args):
        '''
        override the paint method
        '''
        p.rotate(-self._parameters['angle'])
        p.translate(-self._parameters['positions'][0], -self._parameters['positions'][1])
