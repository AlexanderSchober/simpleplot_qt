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

import pyqtgraph as pg
import numpy as np


class Bin_Plot():
    
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

    def __init__(self, x, y, z, **kwargs):
    
        #save data localy
        self.x_data = x
        self.y_data = y
        self.z_data = z
        
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

        color_map = [
            np.array([0., 1., 0.5, 0.25, 0.75]),
            np.array(
                [
                    [  0,   0,   0,   0], 
                    [255, 255,   0, 255], 
                    [  0,   0,   0, 255], 
                    [  0,   0, 255, 255], 
                    [255,   0,   0, 255]], 
                    dtype=np.ubyte)]

        ##############################################
        #set the default values that will be overwritten
        self.para_dict['Color_map'] = [color_map, ['list', 'np.array']]
        self.para_dict['Levels']    = [[0,100], ['list', 'float']]
        self.para_dict['Name']      = ['No Name', ['str']]

        #the labels
        self.para_dict['XLabel']      = [None, ['None', 'str']]
        self.para_dict['YLabel']      = [None, ['None', 'str']]
        self.para_dict['ZLabel']      = [None, ['None', 'str']]

        ##############################################
        #run through kwargs and try to inject
        for key in kwargs.keys():
            
            self.para_dict[key][0] = kwargs[key]

    def get_para(self, name):
        '''
        ##############################################
        Returns the value of the parameter requested
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        return self.para_dict[name][0]

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

        #initialise the widgets
        self.image  = pg.ImageItem()
        
        #initialise the parameters and apply to image
        color_map   = pg.ColorMap(*self.get_para('Color_map'))
        look_up     = color_map.getLookupTable(0.0, 1.0, 256)
        self.image.setLookupTable(look_up)
        self.image.setLevels(self.get_para('Levels'))
        self.image.setImage(self.z_data)

        #add the image itself onto drawsurface
        target_surface.draw_surface.addItem(self.image)


        #to rethink and rewrite our own range engine

        # #place histogram on the graph
        # self.histo  = pg.HistogramLUTWidget(
        #     image   = self.image, 
        #     parent  = target_surface,
        #     rgbHistogram = True
        #     )
        # self.histo.setBackground(target_surface.background)
        # self.histo.axis.setStyle(showValues = False)

        # target_surface.grid_layout.addWidget(self.histo,1,2)
        # target_surface.grid_layout.setColumnMinimumWidth(2,100)

    def remove_items(self, target_surface):
        '''
        ##############################################
        Remove the objects.
        ———————
        Input: 
        - parent is the parent canvas class
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        target_surface.draw_surface.removeItem(self.image)

