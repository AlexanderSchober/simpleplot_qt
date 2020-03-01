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

class EllipseView(pg.GraphicsObject):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self, **opts):
        '''

        '''
        super().__init__(opts.get('parent', None))
        
        self.diameters = [1.,1.]
        self.positions = [2.,2.]
        self.angle      = 0.
        self.brush     = QtGui.QBrush()
        self.pen       = QtGui.QPen()

    def setData(self, positions = [1.,1.], diameters = [2.,2.], angle = 0.):
        '''
        Set the data for display
        '''
        self.diameters = diameters
        self.positions = positions
        self.angle = angle
        self.prepareGeometryChange()
        self.update()

    def paint(self, p, *args):
        '''
        override the paint method
        '''
        
        p.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        p.setBrush(self.brush)
        p.setPen(self.pen)

        p.translate(self.positions[0], self.positions[1])
        p.rotate(self.angle)

        p.drawEllipse(
            QtCore.QPointF(0.,0.), 
            self.diameters[0], self.diameters[1])

        p.rotate(-self.angle)
        p.translate(-self.positions[0], -self.positions[1])

    def boundingRect(self):
        return  QtCore.QRectF(
            self.positions[0] - self.diameters[0] - self.pen.widthF()*2, 
            self.positions[1] - self.diameters[1] - self.pen.widthF()*2,
            self.diameters[0]*2 + self.pen.widthF()*4., 
            self.diameters[1]*2 + self.pen.widthF()*4.)

    def shape(self):
        '''
        Override the shape method
        '''
        path = QtGui.QPainterPath()
        path.addEllipse(
            self.positions[0], self.positions[1], 
            self.diameters[0], self.diameters[1])
        return path
