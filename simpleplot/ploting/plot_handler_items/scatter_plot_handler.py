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

# Personal imports
from .plot_handler                  import PlotHandler
from ..plot_data_types.line_data    import LineData
from ..plot_items.scatter_plot      import ScatterPlot
from ..plot_items.line_plot         import LinePlot
from ..plot_items.error_plot        import ErrorPlot
from ..plot_items.SimpleItemSample  import SimpleItemSample

class ScatterPlotHandler(PlotHandler):

    def __init__(self, **kwargs):
        '''
        '''
        super().__init__(kwargs.get('Name', 'No Name'))

        self._plot_data = LineData(**kwargs)
        self.addChild(self._plot_data)

        self.addChild(ScatterPlot(**kwargs))
        self.addChild(LinePlot(**kwargs))
        self.addChild(ErrorPlot(**kwargs))

    def setPlotData(self, **kwargs):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        self['Data'].setPlotData(**kwargs)
        
        for child in self._children:
            if hasattr(child, 'refresh'):
                child.refresh()

        if not self._model is None:
            self._model.dataChanged.emit(self._plot_data.index(),self._plot_data.index())

    def legendItems(self):
        '''
        return to the legend the items to be used
        '''
        return SimpleItemSample([self.childFromName('Line'), self.childFromName('Scatter'), self.childFromName('Error')])
