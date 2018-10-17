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
import pyqtgraph.opengl as gl

from copy import deepcopy
from PyQt5 import QtGui
import numpy as np


class Surface(): 
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

    def __init__(self, points, vertices, **kwargs):

        #save data localy
        self.points     = np.asarray(deepcopy(points))
        self.vertices   = np.asarray(deepcopy(vertices))
        
        #initalise plot parameters
        self.initialize(**kwargs)

        #post process
        self.process()

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
        self.para_dict['Color']     = [ 'b', ['str', 'hex', 'list', 'int']]
        self.para_dict['Name']      = [ 'No Name', ['str']]
        self.para_dict['Error']     = [ None, ['None', 'dict', 'float']]

        ##############################################
        #run through kwargs and try to inject
        for key in kwargs.keys():
            self.para_dict[key][0] = kwargs[key]

    def process(self):
        '''
        ##############################################
        One parameters re set some processing can be 
        performed...
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass

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

    def drawGL(self, target_view):
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
        self.curves = []

        self.curves.append(gl.GLMeshItem(
            vertexes    = self.points,
            faces       = self.vertices,
            smooth      = False, 
            drawEdges   = True,
            color       = self.get_para('Color')))

        
        
        for curve in self.curves:

            #curve.setGLOptions('opaque')

            target_view.view.addItem(curve)


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

        for curve in self.curves:
    
            target_surface.draw_surface.removeItem(curve)

        target_surface.draw_surface.setLogMode(*self.get_para('Log'))