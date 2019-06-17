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

from PyQt5 import QtGui, QtCore

from .plot_data_types.surface_data import SurfaceData
from ..model.node                  import SessionNode

from .plot_items.surface_plot      import SurfacePlot
from .plot_items.iso_curve_plot    import IsoCurvePlot
from .plot_ray_handlers.surface    import SurfaceRayHandler
from .plot_items.SimpleItemSample  import SimpleItemSample

class SurfacePlotHandler(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.

        Parameters
        -----------
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        if 'Name' in kwargs.keys():
            SessionNode.__init__(self, kwargs['Name'])
        else:
            SessionNode.__init__(self, 'No_name')
            
        self.add_options    = []

        self._plot_data     = SurfaceData()
        self.addChild(self._plot_data)
        self.addChild(SurfacePlot(**kwargs))
        self.addChild(IsoCurvePlot(**kwargs))
        self._ray_handler   = SurfaceRayHandler()
        self.addChild(self._ray_handler)

        self._plot_data.setData(x = x, y = y, z = z)

    def __getitem__(self, value):
        '''
        return the items that are in the 
        current base.
        '''
        return self.childFromName(value)

    def setData(self, **kwargs):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        self['Data'].setData(**kwargs)
        
        for child in self._children:
            if hasattr(child, 'refresh'):
                child.refresh()
        
        self._model.dataChanged.emit(self.index(),self.index())

    def draw(self, target_surface = None):
        '''
        Draw the objects on a 2D canvas
        '''
        for child in self._children:
            if hasattr(child, 'draw'):
                child.draw(target_surface)

    def drawGL(self, target_view = None):
        '''
        Draw the objects on a 3D canvas
        '''
        self['Data'].set3D()

        for child in self._children:
            if hasattr(child, 'drawGL'):
                child.drawGL(target_view)

    def removeItems(self):
        '''
        '''
        for child in self._children:
            if hasattr(child, 'removeItems'):
                child.removeItems()

    def legendItems(self):
        '''
        return to the legend the items to be used
        '''
        return SimpleItemSample([self.childFromName('Line'), self.childFromName('Scatter'), self.childFromName('Error')])

