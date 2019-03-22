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

        #save data locally
        self.points     = np.asarray(deepcopy(points))
        self.vertices   = np.asarray(deepcopy(vertices))
        
        #initialise plot parameters
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
        self.para_dict['Color']     = [ None, ['str', 'hex', 'list', 'int']]
        self.para_dict['Shader']    = [ None, ['str', 'hex', 'list', 'int']]
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

    def generate_shader(self,name):
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

        kwargs = {}

        kwargs['vertexes']  = self.points
        kwargs['faces']     = self.vertices
        kwargs['smooth']    = True
        kwargs['drawEdges'] = True

        if not isinstance(self.get_para("Color"), type(None)):

            if isinstance(self.get_para("Color"), np.ndarray):

                if len(self.get_para('Color'))<5:
                    kwargs['color'] = self.get_para('Color')
                else:
                    kwargs['vertexColors'] = self.get_para('Color')

            elif isinstance(self.get_para("Color"), pg.opengl.shaders.ShaderProgram):
                kwargs['shader'] = self.get_para('Color')

        else:
            kwargs['shader'] = 'heightColor'

        self.curves.append(gl.GLMeshItem(**kwargs))

        
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