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

# General imports
from PyQt5 import QtGui
import numpy as np

# Personal imports
from ..graphics_items.graphics_item import GraphicsItem
from ..plot_views_3D.isosurface_view_3D import IsoSurfaceView3D

class IsoSurfacePlot(GraphicsItem): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self,*args, **kwargs):
        '''
        Initialisation of the class and super class

        Parameters:
        -------------------
        *args : -
            These are the arguments of the class
        **kwargs : -
            These are the keyword arguments of the class
        '''
        super().__init__('Iso-surface', *args,transformer = False, **kwargs)

        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self._mode = '3D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        bounds = kwargs['data_item'].getBounds()

        self.addParameter(
            'Raycast step size', 0.5/20, 
            method = self.setColor, 
            tags = ['3D'])
        self.addParameter(
            'Surface color', QtGui.QColor('grey'),
            tags   = ['3D'],
            method = self.setColor)
        self.addParameter(
            'Surface value', 0.5,
            tags   = ['3D'],
            method = self.setColor)
        self.addParameter(
            'X range', [False, bounds[0][0], bounds[0][1],False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
            tags   = ['3D'],
            method = self.setColor)
        self.addParameter(
            'Y range', [False, bounds[1][0], bounds[1][1],False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
            tags   = ['3D'],
            method = self.setColor)
        self.addParameter(
            'Z range', [False, bounds[2][0], bounds[2][1],False, ''],
            names  = ['Constrain','min', 'max','Cut outs', 'values'],
            tags   = ['3D'],
            method = self.setColor)

    def _refreshBounds(self):
        '''
        refresh the bounds of the parameter handler 
        as the data is being refreshed
        '''
        bounds = self.parent()._plot_data.getBounds()

        targets     = ['X range', 'Y range', 'Z range']
        for j,target in enumerate(targets):
            data_range = self[target]
            if not data_range[0]:
                data_range[1] = float(bounds[j][0])
                data_range[2] = float(bounds[j][1])
                self.items[target].updateValue(data_range, method = False)

    def setColor(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return

        if self._mode == '2D':
            pass

        elif self._mode == '3D':
            bounds      = np.array(self.parent()._plot_data.getBounds()[:3])

            parameters = {}
            parameters['color']         =  np.array([val/255 for val in self['Surface color'].getRgb()])
            parameters['threshold']     = np.array(self['Surface value'])
            parameters['step_size']     = self['Raycast step size']
            parameters['top_limits'] = np.array([
                1 if not self['X range'][0] else (self['X range'][2]-bounds[0,0])/(bounds[0,1] - bounds[0,0]),
                1 if not self['Y range'][0] else (self['Y range'][2]-bounds[1,0])/(bounds[1,1] - bounds[1,0]),
                1 if not self['Z range'][0] else (self['Z range'][2]-bounds[2,0])/(bounds[2,1] - bounds[2,0])
            ])
            parameters['bot_limits'] = np.array([
                0 if not self['X range'][0] else (self['X range'][1]-bounds[0,0])/(bounds[0,1] - bounds[0,0]),
                0 if not self['Y range'][0] else (self['Y range'][1]-bounds[1,0])/(bounds[1,1] - bounds[1,0]),
                0 if not self['Z range'][0] else (self['Z range'][1]-bounds[2,0])/(bounds[2,1] - bounds[2,0])
            ])
            self.draw_items[0].setColors(**parameters)

    def setData(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        data = self.parent()._plot_data.getData()
        bounds = np.array(self.parent()._plot_data.getBounds()[:3])
        self.draw_items[0].setPlotData(bounds, data[4])

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view.view
            self.setCurrentTags(['3D'])

        if self['Visible']:
            self.draw_items = [IsoSurfaceView3D()]
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData()
            self.setColor()
            self.setVisual()
