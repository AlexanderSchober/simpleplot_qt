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

from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import opengl as gl
import numpy as np


class RangePlot():
    
    '''
    ##############################################
    This class will be the plots. 
    ———————
    Input: 
    - parent is the parent canvas class
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, **kwargs):

        #initalise plot parameters
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        '''
        ##############################################
        This class will be the scatter plots. 
        ———————
        Input: 
        - parent is the parent canvas class
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        self.para_dict      = {}

        ##############################################
        #set the default values that will be overwritten
        self.para_dict['min']       = [0, ['float']]
        self.para_dict['max']       = [1, ['float']]
        self.para_dict['move']      = [True, ['bool']]

        ##############################################
        #run through kwargs and try to inject
        for key in kwargs.keys():
            
            self.para_dict[key][0] = kwargs[key]

    def draw(self, target_surface):
        '''
        ##############################################
        Draw the objects.
        ———————
        Input: 
        - target_surface plot objec to draw on
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.draw_items = []

        #add the element
        self.draw_items.append(
            pg.LinearRegionItem())

        for curve in self.draw_items:

            target_surface.draw_surface.addItem(curve)
