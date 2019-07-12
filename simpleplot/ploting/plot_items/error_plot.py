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

from PyQt5 import QtGui
from copy import deepcopy
import numpy as np

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl

from ..custom_pg_items.SimplePlotDataItem import SimplePlotDataItem
from ..custom_pg_items.SimpleErrorBarItem import SimpleErrorBarItem

from ...model.parameter_class       import ParameterHandler 

class ErrorPlot(ParameterHandler): 
    '''
    This class will be the scatter plots. 
    '''

    def __init__(self, **kwargs):
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
        ParameterHandler.__init__(self, 'Error')
        self._initialize(**kwargs)
        self._mode = '2D'

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
            'Antialiassing', True ,
            tags    = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Line color', QtGui.QColor('grey') ,
            tags    = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Line width', 2,
            tags    = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Beam', 0.1 ,
            tags    = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Depth', -1,
            tags     = ['2D'],
            method  = self.refresh)

    def _setVisual(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        self.line_pen = pg.mkPen({
            'color': self['Line color'],
            'width': self['Line width']})

    def _getDictionary(self):
        '''
        Build the dictionary used for plotting
        '''
        kwargs = {}
        if self._mode == '2D':

            self._setVisual()
            data    = self.parent()._plot_data.getData()
            error   = self.parent()._plot_data.getError()

            if error is None:
                error = {'width':0, 'height':0}
                kwargs['x']         = data[0]
                kwargs['y']         = data[1]
                kwargs['pen']       = self.line_pen
                kwargs['beam']      = 0
                kwargs = {**kwargs, **error}
            else:
                kwargs['x']         = data[0]
                kwargs['y']         = data[1]
                kwargs['pen']       = self.line_pen
                kwargs['beam']      = self['Beam']
                kwargs = {**kwargs, **error}
                
        return kwargs

    def refresh(self):
        '''
        Set the data of the plot manually after the plot item 
        has been actualized
        '''
        if hasattr(self, 'draw_items'):
            if self['Visible'] and self._mode == '2D':
                kwargs = self._getDictionary()
                self.draw_items[0].setData(**kwargs)
                self.draw_items[0].setZValue(self['Depth'])
            else:
                for i in range(len(self.draw_items))[::-1]:
                    if self._mode == '2D':
                        self.default_target.draw_surface.removeItem(self.draw_items[i])
                del self.draw_items
        else:
            if self['Visible'] and self._mode == '2D':
                self.draw()

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])

        self.draw_items = []
        kwargs          = self._getDictionary()
        self.draw_items.append(SimpleErrorBarItem(**kwargs))
        self.draw_items[0].setZValue(self['Depth'])

        for curve in self.draw_items:
            self.default_target.draw_surface.addItem(curve)

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        
        if not target_view == None:
            self.default_target = target_view
            self.setCurrentTags(['3D'])

        self.draw_items = []

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)

    def processRay(self, ray):
        '''
        try to process the ray intersection
        '''
        pass
