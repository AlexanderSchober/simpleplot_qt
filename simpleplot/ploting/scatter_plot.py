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


class Scatter_Plot(): 
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

    def __init__(self, x, y, z = None, **kwargs):

        #save data localy
        self.x_data = deepcopy(x)
        self.y_data = deepcopy(y)

        if not isinstance(z,np.ndarray):
            self.z_data = [0. for element in self.x_data]

        else:
            self.z_data = deepcopy(z)
        
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
        self.para_dict['Color']     = [ 'b', ['str', 'hex']]
        self.para_dict['Dash']      = [ None,['str', 'tuple', 'int']]
        self.para_dict['Thickness'] = [ 1, ['int']]
        self.para_dict['Active']    = [ True, ['bool']]
        self.para_dict['Style']     = [ '',['tuple','str']]
        self.para_dict['Name']      = [ 'No Name', ['str']]
        self.para_dict['Log']       = [ [False, False], ['list', 'tuple', 'bool']]
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
        #x processing
        if self.get_para('Log')[0]:
            self.x_data = np.log10(self.x_data)

        self.x_min = np.min(self.x_data)
        self.x_max = np.max(self.x_data)
        self.x_mean = np.mean(self.x_data)

        #y processing
        if self.get_para('Log')[1]:
            self.y_data = np.log10(self.y_data)

        self.y_min = np.min(self.y_data)
        self.y_max = np.max(self.y_data)
        self.y_mean = np.mean(self.y_data)

        self.z_min = np.min(self.z_data)
        self.z_max = np.max(self.z_data)
        self.z_mean = np.mean(self.z_data)

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

    def set_pen(self):
        '''
        ##############################################
        This method will initialise the Qpen as the
        the QPainter method
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #initialise the pen
        self.pen = pg.mkPen({
                'color': QtGui.QColor(self.get_para('Color')),
                'width': self.get_para('Thickness')
            })

    def set_brush(self):
        '''
        ##############################################
        This method will initialise the Qpen as the
        the QPainter method
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #initialise the pen
        self.brush = pg.mkBrush(self.get_para('Color'))

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
        self.curves = []

        #we want a line
        if '-' in self.get_para('Style'):

            #generate the pen
            self.set_pen()

            #add the element
            self.curves.append(
                pg.PlotCurveItem(
                    self.x_data, 
                    self.y_data,
                    pen = self.pen))

        #we want a scatter
        scatter_options = ['o', 'd', 's', 't']
        scatter_bool    = [element in scatter_options for element in self.get_para('Style')]
        
        if any(scatter_bool):
            
            #grab the shape
            scatter_option = self.get_para('Style')[scatter_bool.index(True)]

            #generate the pen
            self.set_pen()
            self.set_brush()

            #add the element
            self.curves.append(
                pg.ScatterPlotItem(
                    self.x_data, 
                    self.y_data,
                    symbol  = scatter_option,
                    pen     = self.pen,
                    brush   = self.brush,
                    size    = int(self.get_para('Style')[-1])))

        if not self.get_para('Error') == None:

            #generate the pen
            self.set_pen()
            
            self.curves.append(
                pg.ErrorBarItem(
                    x   = self.x_data, 
                    y   = self.y_data,
                    pen = self.pen,
                    **self.get_para('Error')
                    ))

        for curve in self.curves:

            target_surface.draw_surface.addItem(curve)

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

        #we want a line
        if '-' in self.get_para('Style'):

            #add the element
            self.curves.append(
                gl.GLLinePlotItem(
                    pos=np.vstack([
                        self.x_data,
                        self.y_data,
                        self.z_data]).transpose(),
                    color = pg.glColor(self.get_para('Color')),
                    width = self.get_para('Thickness')
                ))

        #we want a scatter
        scatter_options = ['o', 'd', 's', 't']
        scatter_bool    = [element in scatter_options for element in self.get_para('Style')]
        
        if any(scatter_bool):

            #generate the pen
            self.set_pen()
            self.set_brush()

            #add the element
            self.curves.append(
                gl.GLScatterPlotItem(
                    pos=np.vstack([
                        self.x_data,
                        self.y_data,
                        self.z_data]).transpose(),
                        color = pg.glColor(self.get_para('Color')),
                        size = int(self.get_para('Style')[-1])
                        ))

        # if not self.get_para('Error') == None:

        #     #generate the pen
        #     self.set_pen()
            
        #     self.curves.append(
        #         pg.ErrorBarItem(
        #             x   = self.x_data, 
        #             y   = self.y_data,
        #             pen = self.pen,
        #             **self.get_para('Error')
        #             ))

        for curve in self.curves:

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