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
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
import sys


class Axes(): 
    '''
    ##############################################
    This will allow an axis management system. 
    Ans will be linked to the sublass of 
    Axis()
    ———————
    Input: -
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, canvas):
    
        self.axes_list = {}
        self.canvas = canvas
        self.initialize()

    def __getitem__(self, location):
        '''
        ##############################################
        return the axis of the specified location
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        return self.axes_list[location] 

    def initialize(self):
        '''
        ##############################################
        Remove all the axes in the first place which
        were dranw on the scene creation. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        # #first check if the axis exists and remove
        for location in ['top','bottom','left', 'right']:
            self.axes_list[location] = self.canvas.draw_surface.getAxis(location)

    def show_axis(self, location):
        '''
        ##############################################
        Remove all the axes in the first place which
        were dranw on the scene creation. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        # #first check if the axis exists and remove
        self.canvas.draw_surface.showAxis(location)

    def hide_axis(self, location):
        '''
        ##############################################
        Remove all the axes in the first place which
        were dranw on the scene creation. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        # #first check if the axis exists and remove
        self.canvas.draw_surface.hideAxis(location)

    def show_grid(self, x = None, y = None , alpha = None):
        '''
        ##############################################
        Remove all the axes in the first place which
        were dranw on the scene creation. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        # #first check if the axis exists and remove
        self.canvas.draw_surface.showGrid( x , y , alpha)


# class Axis(): 
#     '''
#     ##############################################
#     This will allow an axis management system. 
#     Ans will be linked to the sublass of 
#     Axis()
#     ———————
#     Input: -
#     ———————
#     Output: -
#     ———————
#     status: active
#     ##############################################
#     '''

#     def __init__(self,canvas , *args, **kwargs):
        
#         self.canvas = canvas
#         self.args = args
        
#         #initalise plot parameters
#         self.initialize(**kwargs)

#         #now draw the axis
#         self.draw()

#     def initialize(self, **kwargs):
#         '''
#         ##############################################
#         This class will be the scatter plots. 
#         ———————
#         Input: 
#         - parent is the parent canvas class
#         ———————
#         Output: -
#         ———————
#         status: active
#         ##############################################
#         '''
#         self.para_dict      = {}

#         ##############################################
#         #set the default values that will be overwritten
#         self.tick_keys = [
#             'text',
#             'units',
#             'linkView']
#         self.para_dict['Color']                 = [ 'black', ['str', 'hex']]
#         self.para_dict['enableAutoSIPrefix']    = [ True, ['bool']]
#         self.para_dict['log']                   = [ False, ['bool']]
#         self.para_dict['grid']                  = [ 100, ['int']]
#         self.para_dict['linkView']              = [ self.canvas.draw_surface, []]
#         print(self.canvas.draw_surface.vb)

#         ##############################################
#         #default label parameters for set label
#         self.label_keys = [
#             'text',
#             'units',
#             'css']

#         self.para_dict['text']                  = [ None, ['str']]
#         self.para_dict['units']                 = [ None, ['str']]
#         self.para_dict['css']                   = [ None, ['dict', 'str']]

#         ##############################################
#         #default tick parametersfor set style
#         self.tick_keys = [
#             'tickLength',
#             'tickTextOffset',
#             'tickTextWidth',
#             'tickTextHeight',
#             'autoExpandTextSpace',
#             'tickFont',
#             'showValues']

#         self.para_dict['tickLength']            = [ 10, ['int']]
#         self.para_dict['tickTextOffset']        = [  5, ['int']]
#         self.para_dict['tickTextWidth']         = [ 50, ['int']]
#         self.para_dict['tickTextHeight']        = [ 15, ['int']]
#         self.para_dict['autoExpandTextSpace']   = [ True, ['bool']]
#         self.para_dict['tickFont']              = [ None, ['None', 'str', 'int']]
#         self.para_dict['showValues']            = [ True, ['bool']]
        

#         ##############################################
#         #run through kwargs and try to inject
#         for key in kwargs.keys():
            
#             self.para_dict[key][0] = kwargs[key]


#     def draw(self, **kwargs):
#         '''
#         ##############################################
#         Draw the axis onto the canvas
#         ———————
#         Input: 
#         - parent is the parent canvas class
#         ———————
#         Output: -
#         ———————
#         status: active
#         ##############################################
#         '''


        