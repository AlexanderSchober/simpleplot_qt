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
from PyQt5 import QtGui
import numpy as np
from .plot_items_helpers import mkPen, mkBrush

# Personal imports
from ..graphics_items.graphics_item import GraphicsItem
from ..plot_views_3D.error_bar_view_3D import ErrorBarView

class ErrorBarItem(GraphicsItem): 
    '''
    This class will be the scatter plots. 
    '''

    def __init__(self, *args, **kwargs):
        '''

        '''
        super().__init__('Error', *args, transformer = False, **kwargs)
        self._initialize(**kwargs)
        self._mode = '2D'
        self.draw_items = [ErrorBarView()]

    def _initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 

        Parameters
        -----------
        kwargs : dict
            The parameters passed on by the user that 
            will override the predefined values
        '''
        self.addParameter(
            'Visible', True , 
            tags    = ['2D'],
            method = self.refresh)

        self.addParameter(
            'Line color', QtGui.QColor('grey') ,
            tags    = ['2D'],
            method  = self.setPlotData)
        
        self.addParameter(
            'Line width', 0.2,
            tags    = ['2D'],
            method  = self.setVisual)
        
        self.addParameter(
            'Beam', 5 ,
            tags    = ['2D'],
            method  = self.setVisual)
        

    def setVisual(self, silent=False):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        parameters = {}
        parameters['line_width'] = np.array([self['Line width']])
        parameters['beam_width'] = np.array([self['Beam']])
        self.draw_items[0].setProperties(**parameters)
        if not silent:
            self.draw_items[0].update()

    def setPlotData(self, silent=False):
        '''
        Build the dictionary used for plotting
        '''
        data = self.parent()._plot_data.getData(['x','y','z'])
        error = self.parent()._plot_data.getError()

        data = np.vstack(data).transpose()
        vertice_data = np.ones((data.shape[0],4), dtype=np.float)
        vertice_data[:,:3] = data
        
        self.draw_items[0].setData(
            vertices = vertice_data, 
            line_colors = np.repeat(
                np.array([self['Line color'].getRgbF()]),
                data.shape[0],
                axis=0),
            error_x=error['x'],
            error_y=error['y'],
            error_z=error['z'],
            )
        if not silent:
            self.draw_items[0].update()
            
    def refresh(self):
        '''
        Set the data of the plot manually after the plot item 
        has been actualized
        '''
        self.setPlotData()
        self.setVisual()

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view.view

        if self['Visible']:
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData(silent=True)
            self.setVisual(silent=True)
