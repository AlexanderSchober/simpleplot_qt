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
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************

#import dependencies
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import sys

from ..pyqtgraph import pyqtgraph as pg

from .SimplePlotlegendItem import SimplePlotLegendItem
from ..ploting.custom_pg_items.SimpleErrorBarItem import SimpleErrorBarItem

from ..model.parameter_node import ParameterNode
from ..model.parameter_class import ParameterHandler 

class Legend(ParameterHandler): 
    '''
    This will allow an axis management system. 
    Ans will be linked to the sublass of 
    Axis()
    '''
    def __init__(self, canvas):
        ParameterHandler.__init__(self,name = 'Legend', parent = canvas)

        self.legend_item = SimplePlotLegendItem()
        self.legend_item.setParentItem(canvas.draw_surface)
        self.canvas = canvas
        self._initialize()
        self.legend_item.pos_updated.connect(self._updatePos)
        self.canvas._plot_model.dataChanged.connect(self.buildLegend)
        
    def _initialize(self):
        '''
        initialise the legend parameter structure
        '''
        self.addParameter(
            'Active', True,
            method = self._manageLegend)
        self.addParameter(
            'Position', [10, 10],
            names  = ['x', 'y'],
            method = self._setOffset)
        self.addParameter(
            'Text length',  100,
            method = self._setTextLength)
        self.addParameter(
            'Pen color',QtGui.QColor(100,100,100,alpha = 255),
            method = self._setPen)
        self.addParameter(
            'Brush color',QtGui.QColor(100,100,100,alpha = 50),
            method = self._setBrush)
        self.addParameter(
            'Text color',QtGui.QColor(0,0,0,alpha = 50),
            method = self._setTextColor)
        self.addParameter(
            'Text size',  8,
            method = self._setTextSize)

        self.runAll()
        self.legend_item._refreshText()
        self.canvas.plot_widget.sceneObj.update()

    def buildLegend(self):
        '''
        Build the legend item
        '''
        self.tearLegendDown()
        for plot_handler in self.canvas._plot_root._children:
            for element in plot_handler._children:
                if hasattr(element, 'legendItems'):
                    items = element.legendItems()
                    for item in items:
                        if hasattr(item, 'draw_items'):
                            for draw_item in item.draw_items:
                                if not isinstance(draw_item, pg.ImageItem) and not isinstance(draw_item, SimpleErrorBarItem):
                                    self.legend_item.addItem(draw_item, element._name)

    def tearLegendDown(self):
        '''
        Build the legend item
        '''
        self.legend_item.removeAllItems()

    def _manageLegend(self):
        '''
        Build the legend item
        '''
        if self['Active']:
            self.buildLegend()
        else:
            self.tearLegendDown()

    def _setOffset(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setOffset(self['Position'])
        self.canvas.plot_widget.sceneObj.update()

    def _setPen(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setPen(self['Pen color'].getRgb())
        self.canvas.plot_widget.sceneObj.update()

    def _setBrush(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setBrush(self['Brush color'].getRgb())
        self.canvas.plot_widget.sceneObj.update()

    def _updatePos(self, x, y):
        '''
        Set the legend offset
        '''
        self.items['Position'].updateValue([x,y], method = False)

    def _setTextLength(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextLength(self['Text length'])
        self.canvas.plot_widget.sceneObj.update()

    def _setTextColor(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextColor(self['Text color'].name())
        self.canvas.plot_widget.sceneObj.update()

    def _setTextSize(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextSize(self['Text size'])
        self.canvas.plot_widget.sceneObj.update()
