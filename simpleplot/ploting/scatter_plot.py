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

from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import opengl as gl
from .SimplePlotDataItem import SimplePlotDataItem
from .SimpleErrorBarItem import SimpleErrorBarItem

from copy import deepcopy
from PyQt5 import QtGui
import numpy as np

from ..model.node   import SessionNode

class ScatterPlot(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''

    def __init__(self, x = None, y = None, z = None,  **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.

        Parameters
        -----------
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        SessionNode.__init__(self, 'No_name')

        self.x_data = deepcopy(x)
        self.y_data = deepcopy(y)
        self.z_data = deepcopy(z)
        self.initialize(**kwargs)
        self._mode = '2D'
        self.type  = 'Scatter'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 

        Parameters
        -----------
        kwargs : dict
            The parameters passed on by the user that 
            will override the predefined values
        '''

        
        self.parameters              = {}
        self.parameters['Color']     = [[QtGui.QColor('b')]]
        # self.parameters['Dash']      = [ None,['str', 'tuple', 'int']]

        self.parameters['Line color']       = [[QtGui.QColor('blue')]]
        self.parameters['Shadow color']     = [[QtGui.QColor('red')]]
        self.parameters['Symbol color']     = [[QtGui.QColor('blue')]]
        self.parameters['Error color']      = [[QtGui.QColor('grey')]]

        self.parameters['Line thickness']   = [[4]]
        self.parameters['Shadow thickness'] = [[4]]
        self.parameters['Symbol thickness'] = [[1]]
        self.parameters['Error thickness']  = [[2]]

        self.parameters['Active']    = [[True]]
        self.parameters['Style']     = [['']]
        self.parameters['Name']      = [['Non name']]
        self.parameters['Log']       = [[False, False]]
        self.parameters['Show error']= [[True]]
        self.parameters['Error']     = [None]

        for key in kwargs.keys():
            temp_key = key.replace('_', ' ')
            if temp_key in self.parameters.keys():
                if isinstance(kwargs[key], list) or isinstance(kwargs[key], tuple) or isinstance(kwargs[key], dict):
                    self.parameters[temp_key][0] = kwargs[key]
                else:
                    self.parameters[temp_key][0] = [kwargs[key]]

    def getParameter(self, name):
        '''
        Returns the value of the parameter requested
        '''
        return self.parameters[name][0]

    def setPens(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        self.line_pen = pg.mkPen({
                'color': QtGui.QColor(self.getParameter('Line color')[0]),
                'width': self.getParameter('Line thickness')[0]})

        self.shadow_pen = pg.mkPen({
                'color': QtGui.QColor(self.getParameter('Shadow color')[0]),
                'width': self.getParameter('Shadow thickness')[0]})

        self.symbol_pen = pg.mkPen({
                'color': QtGui.QColor(self.getParameter('Symbol color')[0]),
                'width': self.getParameter('Symbol thickness')[0]})

        self.error_pen = pg.mkPen({
                'color': QtGui.QColor(self.getParameter('Error color')[0]),
                'width': self.getParameter('Error thickness')[0]})

        self.empty_pen = pg.mkPen({ 'width': 0})

    def setBrushes(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        self.symbol_brush = pg.mkBrush(self.getParameter('Color')[0])

    def setData(self, **kwargs):
        '''
        Set the data of the plot manually after the plot item 
        has been actualized
        '''

        if 'x' in kwargs.keys():
            self.x_data = kwargs['x']
            kwargs['x'] = np.log10(kwargs['x']) if self.getParameter('Log')[0] else kwargs['x']
            
        if 'y' in kwargs.keys():
            self.y_data = kwargs['y']
            kwargs['y'] = np.log10(kwargs['y']) if self.getParameter('Log')[0] else kwargs['y']
            
        if 'z' in kwargs.keys():
            self.z_data = kwargs['z']
            kwargs['z'] = np.log10(kwargs['z']) if self.getParameter('Log')[0] else kwargs['z']
            
        if 'error' in kwargs.keys():
            self.parameters['Error']  = [kwargs['error']]
            self.draw_items[1].setData(**kwargs, **self.getParameter('Error'))

        self.draw_items[0].setData(**kwargs)
            
    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface

        self.draw_items = []
        self.setBrushes()
        self.setPens()

        #we want a scatter
        scatter_options = ['o', 'd', 's', 't']
        scatter_bool    = [
            element in scatter_options 
            for element in self.getParameter('Style')]
        
        kwargs = {}

        scatter_present = any(scatter_bool)
        line_present    = ('-' in self.getParameter('Style'))

        kwargs['x'] = np.log10(self.x_data) if self.getParameter('Log')[0] else self.x_data
        kwargs['y'] = np.log10(self.y_data) if self.getParameter('Log')[1] else self.y_data

        if scatter_present and line_present:
            scatter_option  = self.getParameter('Style')[scatter_bool.index(True)]
            kwargs['connect']     = 'all'
            kwargs['symbol']      = scatter_option
            kwargs['symbolSize']  = int(self.getParameter('Style')[-1])
            kwargs['symbolPen']   = self.symbol_pen
            kwargs['symbolBrush'] = self.symbol_brush
            kwargs['pen']         = self.line_pen
            kwargs['shadowPen']   = self.shadow_pen
            kwargs['antialias']   = True
        elif scatter_present and not line_present:
            scatter_option  = self.getParameter('Style')[scatter_bool.index(True)]
            kwargs['connect']     = 'all'
            kwargs['symbol']      = scatter_option
            kwargs['symbolSize']  = int(self.getParameter('Style')[-1])
            kwargs['symbolPen']   = self.symbol_pen
            kwargs['symbolBrush'] = self.symbol_brush
            kwargs['pen']         = self.empty_pen
            kwargs['antialias']   = True
        elif not scatter_present and line_present:
            kwargs['connect']     = 'all'
            kwargs['pen']         = self.line_pen
            kwargs['shadowPen']   = self.shadow_pen
            kwargs['antialias']   = True

        if scatter_present and line_present:
            self.draw_items = [SimplePlotDataItem(
                **kwargs)]
        elif scatter_present and not line_present:
            self.draw_items = [SimplePlotDataItem(
                **kwargs)]
        elif not scatter_present and line_present:
            self.draw_items = [SimplePlotDataItem(
                **kwargs)]
            
        if not self.getParameter('Error') == None and self.getParameter('Show error')[0]:
            self.draw_items.append(
                SimpleErrorBarItem(
                    x   = kwargs['x'], 
                    y   = kwargs['y'],
                    pen = self.error_pen,
                    **self.getParameter('Error')))

        for curve in self.draw_items:
            self.default_target.draw_surface.addItem(curve)

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []
        self.setBrushes()
        self.setPens()
        
        x_data = self.x_data
        y_data = self.y_data if not self.z_data == None else np.zeros(x_data.shape)
        z_data = self.z_data if not self.z_data == None else self.y_data 

        color  = [
            self.getParameter('Line color')[0].red()/255.,
            self.getParameter('Line color')[0].green()/255.,
            self.getParameter('Line color')[0].blue()/255.,
            self.getParameter('Line color')[0].alpha()/255.]
        
        scatter_options = ['o', 'd', 's', 't']
        scatter_bool    = [
            element in scatter_options 
            for element in self.getParameter('Style')]
        scatter_present = any(scatter_bool)
        line_present    = ('-' in self.getParameter('Style'))

        #we want a line
        if line_present:
            self.draw_items.append(
                gl.GLLinePlotItem(
                    pos=np.vstack([
                        x_data,
                        y_data,
                        z_data]).transpose(),
                    color = color,
                    width = self.getParameter('Line thickness')[0]))
            self.draw_items[-1].setGLOptions('translucent')
        
        if scatter_present:
            self.draw_items.append(
                gl.GLScatterPlotItem(
                    pos=np.vstack([
                    x_data,
                    y_data,
                    z_data]).transpose(),
                    color = color,
                    size = int(self.getParameter('Style')[-1])
                    ))
            self.draw_items[-1].setGLOptions('translucent')
            
        for curve in self.draw_items:
            self.default_target.view.addItem(curve)

    def removeItems(self):
        '''
        Remove the objects.
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)

    def processRay(self, ray):
        '''
        try to process the ray intersection
        '''
        pass