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

class PieView(pg.GraphicsObject):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self, **opts):
        '''

        '''
        super().__init__(opts.get('parent', None))
        
        self.radial_range = [1.,1.]
        self.angle_range = [1.,1.]
        self.positions = [2.,2.]
        self.angle = 0.
        self.brush = QtGui.QBrush()
        self.pen = QtGui.QPen()

    def setData(self, positions = [1.,1.], radial_range = [2.,2.], angle_range = [2.,2.], angle = 0.):
        '''
        Set the data for display
        '''
        self.radial_range = radial_range
        self.angle_range = angle_range
        self.positions = positions
        self.angle = angle
        self.path = self.getPiePath()
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

        p.drawPath(self.path)

        p.rotate(-self.angle)
        p.translate(-self.positions[0], -self.positions[1])

    def boundingRect(self):
        return  QtCore.QRectF(
            self.positions[0] - self.radial_range[1] - self.pen.widthF()*2, 
            self.positions[1] - self.radial_range[1] - self.pen.widthF()*2,
            self.radial_range[1]*2 + self.pen.widthF()*4., 
            self.radial_range[1]*2 + self.pen.widthF()*4.)

    def shape(self):
        '''
        Override the shape method
        '''
        return self.path

    def getPiePath(self):
        '''
        This will get the path for the extruded pie
        graph item used by th epainter
        '''
        path = QtGui.QPainterPath()
        path.moveTo(
            np.cos(self.angle_range[0]* np.pi / 180.)*self.radial_range[0],
            np.sin(self.angle_range[0]* np.pi / 180.)*self.radial_range[0])
        path.arcTo(
            -self.radial_range[0], -self.radial_range[0],
            self.radial_range[0]*2., self.radial_range[0]*2.,
            -self.angle_range[0], -(self.angle_range[1]-self.angle_range[0]))
        path.lineTo(
            np.cos(self.angle_range[1]* np.pi / 180.)*self.radial_range[1],
            np.sin(self.angle_range[1]* np.pi / 180.)*self.radial_range[1])
        path.arcTo(
            -self.radial_range[1], -self.radial_range[1],
            self.radial_range[1]*2., self.radial_range[1]*2.,
            -self.angle_range[1], -(self.angle_range[0]-self.angle_range[1]))
        path.closeSubpath()
        
        return path