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
from .plot_handler                 import PlotHandler

from .plot_items.surface_plot      import SurfacePlot
from .plot_items.iso_curve_plot    import IsoCurvePlot
from .plot_ray_handlers.surface    import SurfaceRayHandler
from .plot_items.SimpleItemSample  import SimpleItemSample

from .plot_geometries.transformer  import Transformer

class SurfacePlotHandler(PlotHandler):

    def __init__(self, **kwargs):
        '''
        '''
        if 'Name' in kwargs.keys():
            PlotHandler.__init__(self, kwargs['Name'])
        else:
            PlotHandler.__init__(self, 'No_name')

        self._plot_data     = SurfaceData()
        self.addChild(self._plot_data)
        self.addChild(SurfacePlot(**kwargs))
        self.addChild(IsoCurvePlot(**kwargs))
        self._ray_handler   = SurfaceRayHandler()
        self.addChild(self._ray_handler)
        self._plot_data.setData(**kwargs)

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
        
        self._model.dataChanged.emit(self._plot_data.index(),self._plot_data.index())

    def legendItems(self):
        '''
        return to the legend the items to be used
        '''
        return SimpleItemSample([self.childFromName('Line'), self.childFromName('Scatter'), self.childFromName('Error')])

    def addProjectionItem(self, item, direction = 'x'):
        '''
        Allows to set 1D projection items 
        as the plot items
        '''
        self._proj_list.append([item, direction])

    def removeProjectionItem(self, item):
        '''
        Remove an item from the projection 
        scheme
        '''
        for i, thing in enumerate(self._proj_list): 
            if thing[0] == item:
                del self._proj_list[i]
                break

    def processProjection(self, x = 0, y = 0, z = 0):
        '''
        The routine that will handle all the 
        projections set by the user
        '''
        for item in self._proj_list:
            if self.childFromName('Data') is not None and hasattr(self.childFromName('Data'), 'getProjection'):
                data = self.childFromName('Data').getProjection(*item[1:], x = x, y = y, z = z)
                item[0].setData(x = data[0], y = data[1])
