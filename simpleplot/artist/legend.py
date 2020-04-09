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

from ..models.parameter_node import ParameterNode
from ..models.parameter_class import ParameterHandler 

class Legend(ParameterHandler): 
    '''
    This will allow an axis management system. 
    Ans will be linked to the sublass of 
    Axis()
    '''
    def __init__(self, canvas):
        ParameterHandler.__init__(self,name = 'Legend', parent = canvas)

        self.canvas = canvas
        self.legend_item = SimplePlotLegendItem()
        self._initialize()
        self.putLegend()
        self.legend_item.pos_updated.connect(self._putPos)

    def _initialize(self):
        '''
        initialise the legend parameter structure
        '''
        self.addParameter(
            'Active', True,
            method  = self._manageLegend)
        self.addParameter(
            'Anchor point', 'top-right',
            choices = [ 'top-left', 'top-right', 'bot-left', 'bot-right'],
            method  = self._setPosition)
        self.addParameter(
            'Relative position', [10, 10],
            names   = ['x', 'y'],
            method  = self._setPosition)
        self.addParameter(
            'Text length',  130,
            method  = self._setTextLength)
        self.addParameter(
            'Text justify',  'left',
            choices = ['left', 'center', 'right'],
            method  = self._setTextJustify)
        self.addParameter(
            'Pen color',QtGui.QColor(100,100,100,alpha = 255),
            method  = self._setPen)
        self.addParameter(
            'Brush color',QtGui.QColor(100,100,100,alpha = 50),
            method  = self._setBrush)
        self.addParameter(
            'Text color',QtGui.QColor(0,0,0,alpha = 50),
            method  = self._setTextColor)
        self.addParameter(
            'Text size',  9,
            method  = self._setTextSize)
        self.addParameter(
            'Icon size',  20,
            method  = self._setIconSize)
        self.addParameter(
            'Margins',  [5, 5, 5, 5, 2, 2],
            names   = ['left-outer', 'right-outer', 'top-outer', 'bot-outter', 'between-h.','between-v.'],
            method  = self._setMargins)

    def _putPos(self, position:QtCore.QPoint):
        '''
        Receive the point position from the item and then
        inject it into the parameter model
        '''
        self.items['Relative position'].updateValue([position.x(),position.y()], method = False)

    def putLegend(self):
        '''
        '''
        self.canvas.overlayScene().addItem(self.legend_item)
        self.runAll()

    def buildLegend(self):
        '''
        Build the legend item
        '''
        self.tearLegendDown()
        for plot_handler in self.canvas._plot_root._children:
            for element in plot_handler._children:
                if hasattr(element, 'legendItems'):
                    self.legend_item.addItem(element.legendItems(), element._name)

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

    def _setPosition(self):
        '''
        Set the position of the whole element at 
        the same time ans the anchor position
        '''
        self.legend_item.setPosition(
            self['Anchor point'],
            self['Relative position']
        )

    def _setPen(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setPen(self['Pen color'].getRgb())

    def _setBrush(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setBrush(self['Brush color'].getRgb())

    def _setTextLength(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextLength(self['Text length'])

    def _setTextColor(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextColor(self['Text color'].name())

    def _setTextSize(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextSize(self['Text size'])

    def _setIconSize(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setIconSize(self['Icon size'])

    def _setMargins(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setMargins(self['Margins'])

    def _setTextJustify(self):
        '''
        Set the legend offset
        '''
        self.legend_item.setTextJusitfy(self['Text justify'])

