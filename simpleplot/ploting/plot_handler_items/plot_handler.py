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
from PyQt5 import QtCore

# Personal imports
from ...models.session_node             import SessionNode
from ..graphics_geometry.transformer    import Transformer

class PlotHandler(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    plotDataChanged = QtCore.pyqtSignal()

    def __init__(self, name):
        '''
        '''
        SessionNode.__init__(self, name)
        self.transformer = Transformer()
        self.addChild(self.transformer)
        self._proj_list = []

    def __getitem__(self, value):
        '''
        return the items that are in the 
        current base.
        '''
        return self.childFromName(value)

    def draw(self, target_surface = None):
        '''
        Draw the objects on a 2D canvas
        '''
        for child in self._children:
            if hasattr(child, 'draw'):
                child.draw(target_surface)

        if self.childFromName(self.transformer._name) is not None:
            self._model.removeRows(self.transformer.index().row(),1,self)

    def drawGL(self, target_view = None):
        '''
        Draw the objects on a 3D canvas
        '''
        if hasattr(self['Data'], 'set3D'):
            self['Data'].set3D()

        for child in self._children:
            if hasattr(child, 'drawGL'):
                child.drawGL(target_view)

        if self.childFromName(self.transformer._name) is None:
            self._model.insertRows(0,1,[self.transformer],self)

    def removeItems(self):
        '''
        '''
        for child in self._children:
            if hasattr(child, 'removeItems'):
                child.removeItems()
        
    def processProjection(self, x = 0, y = 0, z = 0):
        '''
        The routine that will handle all the 
        projections set by the user
        '''
        pass
        
    def legendItems(self, size_w, size_h):
        '''
        return to the legend the items to be used
        '''
        return None