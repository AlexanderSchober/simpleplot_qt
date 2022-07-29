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

# General imports
from PyQt5 import QtGui, QtCore

# Personal imports
from .graphics_view import GraphView

class ParallepipedView(GraphView):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self, **opts):
        '''

        '''
        super().__init__(**opts)
        self._parameters['dimensions'] = [1.,1.]
        self._parameters['positions'] = [2.,2.]
        self._parameters['angle'] = 0.
        self._parameters['brush'] = QtGui.QBrush()
        self._parameters['pen'] = QtGui.QPen()
        self._parameters['Z'] = 0
        self._parameters['movable'] = False

    def setData(self, **kwargs):
        '''
        Set the data for display
        '''
        self._parameters.update(kwargs)
        self.path = self.getPiePath()
        super().render()

    def paint(self, p, *args):
        '''
        override the paint method
        '''
        super().inPainter(p, *args)

        p.drawPath(self.path)

        super().outPainter(p, *args)

    def boundingRect(self):
        return  QtCore.QRectF(
            self._parameters['positions'][0] - self._parameters['dimensions'][0]/2. 
            - self._parameters['pen'].widthF()*2, 
            self._parameters['positions'][1] - self._parameters['dimensions'][1]/2. 
            - self._parameters['pen'].widthF()*2,
            self._parameters['dimensions'][0] + self._parameters['pen'].widthF()*4., 
            self._parameters['dimensions'][1] + self._parameters['pen'].widthF()*4.)

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
            - self._parameters['dimensions'][0]/2., 
            - self._parameters['dimensions'][1]/2.)
        path.lineTo(
            self._parameters['dimensions'][0]/2., 
            - self._parameters['dimensions'][1]/2.)
        path.lineTo(
            0, 
            self._parameters['dimensions'][1]/2.)
        path.lineTo(
            - self._parameters['dimensions'][0]/2., 
            - self._parameters['dimensions'][1]/2.)

        return path
        
