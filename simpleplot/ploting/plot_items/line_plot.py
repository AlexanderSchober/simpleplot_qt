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


from ..custom_pg_items.GLLinePlotItem import GLLinePlotItem

class LinePlot(ParameterHandler): 
    '''
    This class will be the scatter plots. 
    '''

    def __init__(self,  **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.

        Parameters
        - - - - - - - - - - -
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        ParameterHandler.__init__(self, 'Line')
        
        self._initialize(**kwargs)
        self._mode = '2D'

    def _initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 

        Parameters
        - - - - - - - - - - -
        kwargs : dict
            The parameters passed on by the user that 
            will override the predefined values
        '''
        style  = kwargs['Style'] if 'Style' in kwargs.keys() else []
        color  = QtGui.QColor(kwargs['Color']) if 'Color' in kwargs.keys() else QtGui.QColor('blue')

        self.addParameter(
            'Visible', True if '-' in style else False, 
            tags    = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Antialiassing', True ,
            tags     = ['2D', '3D'],
            method  = self.refresh)
        self.addParameter(
            'Line color', color ,
            tags     = ['2D', '3D'],
            method  = self.refresh)
        self.addParameter(
            'Line width', float(kwargs['Thickness']) if 'Thickness' in kwargs.keys() else 2. ,
            tags     = ['2D', '3D'],
            method  = self.refresh)
        self.addParameter(
            'Shadow color', QtGui.QColor('black') ,
            tags     = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Shadow width', 0 ,
            tags     = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Fill', False ,
            tags     = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Fill level', 0. ,
            tags     = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Fill color', QtGui.QColor('blue') ,
            tags     = ['2D'],
            method  = self.refresh)
        self.addParameter(
            'Depth', 0.,
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

        self.shadow_pen = pg.mkPen({
            'color': self['Shadow color'],
            'width': self['Shadow width']})

        self.fill_brush = pg.mkBrush(self['Fill color'])

    def _getDictionary(self):
        '''
        Build the dictionary used for plotting
        '''
        kwargs = {}
        if self._mode == '2D':

            self._setVisual()
            data = self.parent()._plot_data.getData()

            kwargs['x']         = data[0]
            kwargs['y']         = data[1]
            kwargs['connect']   = 'all'
            kwargs['pen']       = self.line_pen
            kwargs['shadowPen'] = self.shadow_pen
            kwargs['antialias'] = True
            kwargs['brush']     = self.fill_brush if self['Fill'] else None
            kwargs['fillLevel'] = self['Fill level'] if self['Fill'] else None

        elif self._mode == '3D':
            data = self.parent()._plot_data.getData(['x','y','z'])
            
            kwargs['pos']   = np.vstack(data).transpose()
            kwargs['color'] = self['Line color'].getRgbF()
            kwargs['width'] = self['Line width']/100.

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
            elif self['Visible'] and self._mode == '3D':
                kwargs = self._getDictionary()
                self.draw_items[0].setData(**kwargs)
            else:
                for i in range(len(self.draw_items))[::-1]:
                    if self._mode == '2D':
                        self.default_target.draw_surface.removeItem(self.draw_items[i])
                    elif self._mode == '3D':
                        self.default_target.view.removeItem(self.draw_items[i])
                del self.draw_items
        else:
            if self['Visible'] and self._mode == '2D':
                self.draw()
            elif self['Visible'] and self._mode == '3D':
                self.drawGL()

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])

        self.draw_items = []
        if self['Visible']:
            kwargs          = self._getDictionary()
            self.draw_items = [SimplePlotDataItem(**kwargs)]
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
        if self['Visible']:
            kwargs = self._getDictionary()
            self.draw_items.append(GLLinePlotItem(**kwargs))
            self.draw_items[-1].setTransform(self.parent().transformer.getTransform())
            self.draw_items[-1].setGLOptions('translucent')

        for curve in self.draw_items:
            self.default_target.view.addItem(curve)

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)
