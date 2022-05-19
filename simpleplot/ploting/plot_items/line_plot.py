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
from ..plot_views_3D.line_view_3D   import LineView3D

class LinePlot(GraphicsItem): 
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
        super().__init__('Line', *args, transformer = False, **kwargs)
        
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
        style  = kwargs['Style'] if 'Style' in kwargs.keys() else ['-']
        color  = QtGui.QColor(kwargs['Color']) if 'Color' in kwargs.keys() else QtGui.QColor('blue')
        self.items['Visible'].updateValue('-' in style, method = False)

        self.addParameter(
            'Line color', color ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Line width', float(kwargs['Thickness']) if 'Thickness' in kwargs.keys() else 0.3 ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Shadow color', QtGui.QColor('black') ,
            tags     = ['2D'],
            method  = self.setVisual)
        self.addParameter(
            'Shadow width', 0 ,
            tags     = ['2D'],
            method  = self.setVisual)
        self.addParameter(
            'Fill', False ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Fill level', 0. ,
            tags     = ['2D'],
            method  = self.setVisual)
        self.addParameter(
            'Fill line start', [0.,0.,0.],
            names   = ['x','y','z'], 
            tags    = ['3D'],
            method  = self.setVisual)
        self.addParameter(
            'Fill line end', [1.,0.,0.],
            names   = ['x','y','z'], 
            tags    = ['3D'],
            method  = self.setVisual)
        self.addParameter(
            'Fill color', QtGui.QColor('blue') ,
            tags     = ['2D', '3D'],
            method  = self.setVisual)
        self.addParameter(
            'Depth', 0.,
            tags     = ['2D'],
            method  = self.setVisual)
            
    def setPens(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        self.line_pen = mkPen({
            'color': self['Line color'],
            'width': self['Line width']})

        self.shadow_pen = mkPen({
            'color': self['Shadow color'],
            'width': self['Shadow width']})

        self.fill_brush = mkBrush(self['Fill color'])

    def getLegendDictionary(self)->dict:
        '''
        Send out the dictionary for the legend
        '''
        self.setVisual()
        kwargs = {}
        kwargs['pen']   = self.line_pen
        return kwargs

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return

        
        kwargs = {}
        kwargs['line_draw'] = self['Visible']
        kwargs['fill_draw'] = self['Fill']
        
        kwargs['line_color'] = np.array(self['Line color'].getRgbF())
        kwargs['line_width'] = np.array([self['Line width']/100.])

        kwargs['fill_color'] = np.array(self['Fill color'].getRgbF())
        kwargs['fill_axis_start'] = np.array([self['Fill line start']])
        kwargs['fill_axis_end'] = np.array([self['Fill line end']])

        self.draw_items[0].setProperties(**kwargs)

    def setPlotData(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        data = self.parent()._plot_data.getData(['x','y','z'])
        self.draw_items[0].setData(vertices = np.vstack(data).transpose())

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
            self.draw_items = [LineView3D()]
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData()
            self.setVisual()
            
    def drawLegendIcon(self, size_w, size_h, pixmap):
        '''
        This will draw the symbol on a pixmap of size given by
        the current 
        '''
        self.setPens()
        self.line_pen = mkPen({
            'color': self['Line color'],
            'width': self['Line width']*10})
        
        size   = size_w
        painter = QtGui.QPainter(pixmap)
        
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        
        fill_path = QtGui.QPainterPath()
        fill_path.moveTo(0,1)
        fill_path.lineTo(1,0)
        fill_path.lineTo(1,1)
        fill_path.lineTo(0,1)
        
        line_path = QtGui.QPainterPath()
        line_path.moveTo(0,1)
        line_path.lineTo(1,0)

        painter.scale(size, size)
        
        if self['Fill']:
            painter.setPen(mkPen({'color': (0,0,0,0)}))
            painter.setBrush(self.fill_brush)
            painter.drawPath(fill_path)
        
        painter.setPen(self.line_pen)
        painter.setBrush(mkBrush((0,0,0,0)))
        painter.drawPath(line_path)
    
        painter.end()
