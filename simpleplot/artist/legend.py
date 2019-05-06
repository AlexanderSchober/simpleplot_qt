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
import pyqtgraph as pg
import numpy as np
import sys

from ..model.parameter_node import ParameterNode

class Legend(ParameterNode): 
    '''
    This will allow an axis management system. 
    Ans will be linked to the sublass of 
    Axis()
    '''
    def __init__(self, canvas):
        ParameterNode.__init__(self,name = 'Legend', parent = canvas)
        self.legend_item = pg.LegendItem(offset=[-30,-30])
        self.legend_item.setParentItem(canvas.draw_surface)
        self.canvas = canvas
        self.initialize()
        
    def initialize(self):
        '''
        '''
        self.parameters = {}

    def setParameter(self, key, value):
        '''
        Set a single parameter
        '''
        self.parameters[key][0] = value
        self.processParameters(key)

    def processParameters(self, key):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        self.parameters[key][1]()

    def processAllParameters(self):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        for key in self.parameters.keys():
            self.parameters[key][1]()