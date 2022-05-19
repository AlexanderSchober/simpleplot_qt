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
from http.server import BaseHTTPRequestHandler
from PyQt5 import QtGui, QtCore
import numpy as np
from .plot_items_helpers import mkPen, mkBrush

# Personal imports
from ..graphics_items.graphics_item import GraphicsItem
from ..plot_views_3D.distribution_view_3D import DistributionView3D

class ScatterPlot(GraphicsItem): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self,*args, **kwargs):
        '''
        Initialisation of the class and super class

        Parameters:
        -------------------
        *args : -
            These are the arguments of the class
        **kwargs : -
            These are the keyword arguments of the class
        '''
        super().__init__('Scatter', *args, transformer = False, **kwargs)
        
        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 

        Parameters
        - - - - - - - - - - -
        kwargs : dict
            The parameters passed on by the user that 
            will override the predefined values
        '''
        style           = kwargs.get('Style', [])
        options         = ['o', 's', 't', 't1', 't2', 't3','d', '+', 'x', 'p', 'h', 'star']
        scatter_bool    = [option in style for option in options]

        symbol = options[scatter_bool.index(True)] if any(scatter_bool) else 'o'
        color  = QtGui.QColor(kwargs.get('Color', QtGui.QColor('blue')))

        if any(scatter_bool):
            if isinstance(style[-1], int) or isinstance(style[-1], float):
                size   = style[-1]
            else:
                size = 0.01
        else:
            size = 0.01

        self.items['Visible'].updateValue(any(scatter_bool), method = False)

        self.addParameter(
            'Type', symbol ,
            choices = options,
            names   = options,
            tags     = ['2D'],
            method  = self.setVisual)
        self.addParameter(
            'Size', float(size) ,
            tags     = ['2D', '3D'],
            method  = self.setPlotData)
        self.addParameter(
            'Fill color', color ,
            tags     = ['2D', '3D'],
            method  = self.setPlotData)
        self.addParameter(
            'Line color', QtGui.QColor('black') ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Line width', 3 ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Antialiassing', True ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Depth', 1.,
            tags     = ['2D'],
            method  = self.setVisual)

    def _setPens(self):
        '''
        Set the visual of the given shape element
        '''
        self.symbol_pen = mkPen({
            'color': self['Line color'],
            'width': self['Line width']})
        self.symbol_brush = mkBrush(
            self['Fill color'])

    def _getDictionary(self):
        '''
        Set the visual of the given shape element
        '''
        self._setPens()
        data = self.parent()._plot_data.getData()
        kwargs                  = {}
        kwargs['x']             = data[0]
        kwargs['y']             = data[1]
        kwargs['pen']           = None
        kwargs['symbol']        = self['Type']
        kwargs['symbolSize']    = self['Size']
        kwargs['symbolPen']     = self.symbol_pen
        kwargs['symbolBrush']   = self.symbol_brush
        kwargs['antialias']     = self['Antialiassing']
        return kwargs

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return
        
        self._setPens()
        parameters = {}
        parameters['drawFaces']     = True
        parameters['drawEdges']     = False
        parameters['drawEdges']     = False

        self.draw_items[0].setProperties(**parameters)

    def getLegendDictionary(self)->dict:
        '''
        Send out the dictionary for the legend
        '''
        self.setVisual()
        kwargs = {}
        kwargs['symbolPen']     = self.symbol_pen
        kwargs['symbolBrush']   = self.symbol_brush
        kwargs['symbolSize']    = self['Size']
        kwargs['symbol']        = self['Type']
        return kwargs

    def setPlotData(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        data = self.parent()._plot_data.getData(['x','y','z'])
        data = np.vstack(data).transpose()
        vertices = np.ones((data.shape[0],4), dtype=np.float)
        vertices *= self['Size']
        vertices[:,:3] = data
        colors = np.ones((data.shape[0],4))
        colors *= np.array(self['Fill color'].getRgbF())

        self.draw_items[0].setData(
            vertices = vertices,
            colors = colors)

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view.view
            self.setCurrentTags(['3D'])

        if self['Visible']:
            self.draw_items = [DistributionView3D()]
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData()
            self.setVisual()
            
    def drawLegendIcon(self, size_w, size_h, pixmap):
        '''
        This will draw the symbol on a pixmap of size given by
        the current 
        '''
        self._setPens()

        opts    = self.getLegendDictionary()
        pen     = mkPen(opts['symbolPen'])
        brush   = mkBrush(opts['symbolBrush'])
        size    = 2*size_w/3
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        painter.translate(size_w / 2, size_h / 2)
        drawSymbol(painter, opts['symbol'], size, pen, brush)
        painter.end()
        
            
## Build all symbol paths
Symbols = {name: QtGui.QPainterPath() for name in ['o', 's', 't', 't1', 't2', 't3','d', '+', 'x', 'p', 'h', 'star']}
Symbols['o'].addEllipse(QtCore.QRectF(-0.5, -0.5, 1, 1))
Symbols['s'].addRect(QtCore.QRectF(-0.5, -0.5, 1, 1))
coords = {
    't': [(-0.5, -0.5), (0, 0.5), (0.5, -0.5)],
    't1': [(-0.5, 0.5), (0, -0.5), (0.5, 0.5)],
    't2': [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0)],
    't3': [(0.5, 0.5), (0.5, -0.5), (-0.5, 0)],
    'd': [(0., -0.5), (-0.4, 0.), (0, 0.5), (0.4, 0)],
    '+': [
        (-0.5, -0.05), (-0.5, 0.05), (-0.05, 0.05), (-0.05, 0.5),
        (0.05, 0.5), (0.05, 0.05), (0.5, 0.05), (0.5, -0.05),
        (0.05, -0.05), (0.05, -0.5), (-0.05, -0.5), (-0.05, -0.05)
    ],
    'p': [(0, -0.5), (-0.4755, -0.1545), (-0.2939, 0.4045),
          (0.2939, 0.4045), (0.4755, -0.1545)],
    'h': [(0.433, 0.25), (0., 0.5), (-0.433, 0.25), (-0.433, -0.25),
          (0, -0.5), (0.433, -0.25)],
    'star': [(0, -0.5), (-0.1123, -0.1545), (-0.4755, -0.1545),
             (-0.1816, 0.059), (-0.2939, 0.4045), (0, 0.1910),
             (0.2939, 0.4045), (0.1816, 0.059), (0.4755, -0.1545),
             (0.1123, -0.1545)]
}
for k, c in coords.items():
    Symbols[k].moveTo(*c[0])
    for x,y in c[1:]:
        Symbols[k].lineTo(x, y)
    Symbols[k].closeSubpath()
tr = QtGui.QTransform()
tr.rotate(45)
Symbols['x'] = tr.map(Symbols['+'])


def drawSymbol(painter, symbol, size, pen, brush):
    if symbol is None:
        return
    
    painter.scale(size, size)
    painter.setPen(pen)
    painter.setBrush(brush)
    if isinstance(symbol, str):
        symbol = Symbols[symbol]
    if np.isscalar(symbol):
        symbol = list(Symbols.values())[symbol % len(Symbols)]
    painter.drawPath(symbol)