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
from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import opengl as gl
from .custome_grid_item import GLGridItem

from ..models.parameter_node import ParameterNode
from ..models.parameter_class import ParameterHandler 

class GridGl(ParameterNode): 
    def __init__(self, canvas):
        ParameterNode.__init__(self,name = '3D Grids', parent = canvas)
        self.canvas = canvas
        self.initialize()

    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self.grid_items = [
            GLGridItem(), 
            GLGridItem(), 
            GLGridItem()]

        self.xy_handler = ParameterHandler(
            name = 'xy Grid', parent = self)
        self.xz_handler = ParameterHandler(
            name = 'xz Grid', parent = self)
        self.yz_handler = ParameterHandler(
            name = 'yz Grid', parent = self)
        
        self.xy_handler.addParameter(
            'Active',  True,
            method = self.setGrids)
        self.xz_handler.addParameter(
            'Active',  True,
            method = self.setGrids)
        self.yz_handler.addParameter(
            'Active',  True,
            method = self.setGrids)

        self.xy_handler.addParameter(
            'Auto',  True,
            method = self.refreshAuto)
        self.xz_handler.addParameter(
            'Auto',  True,
            method = self.refreshAuto)
        self.yz_handler.addParameter(
            'Auto',  True,
            method = self.refreshAuto)

        self.xy_handler.addParameter(
            'Scale',  [1., 1.],
            names  = ['x', 'y'],
            method = self.scaleGrids)
        self.xz_handler.addParameter(
            'Scale',  [1., 1.],
            names  = ['x', 'y'],
            method = self.scaleGrids)
        self.yz_handler.addParameter(
            'Scale',  [1., 1.],
            names  = ['x', 'y'],
            method = self.scaleGrids)

        self.xy_handler.addParameter(
            'Size', [0., 10., 0., 10.],
            names  = ['x min', 'x max', 'y min', 'y max'],
            method = self.sizeGrids)
        self.xz_handler.addParameter(
            'Size', [0., 10., 0., 10.],
            names  = ['x min', 'x max', 'y min', 'y max'],
            method = self.sizeGrids)
        self.yz_handler.addParameter(
            'Size', [0., 10., 0., 10.],
            names  = ['x min', 'x max', 'y min', 'y max'],
            method = self.sizeGrids)

        self.xy_handler.addParameter(
            'Angle', [0., 0., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)
        self.xz_handler.addParameter(
            'Angle', [90., 0., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)
        self.yz_handler.addParameter(
            'Angle', [0., -90., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)

        self.xy_handler.addParameter(
            'Position', [0., 0., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)
        self.xz_handler.addParameter(
            'Position', [0., 0., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)
        self.yz_handler.addParameter(
            'Position', [0., 0., 0.],
            names  = ['x', 'y', 'z'],
            method = self.processGrids)

        self.xy_handler.addParameter(
            'Color', QtGui.QColor(0, 0, 0, 255),
            method = self.setColors)
        self.xz_handler.addParameter(
            'Color', QtGui.QColor(0, 0, 0, 255),
            method = self.setColors)
        self.yz_handler.addParameter(
            'Color', QtGui.QColor(0, 0, 0, 255),
            method = self.setColors)

        self.handlers = [
            self.xy_handler, 
            self.xz_handler, 
            self.yz_handler]

        self.setGrids()
        self.scaleGrids()
        self.sizeGrids()
        self.processGrids()
        self.setColors()

    def setGrids(self):
        '''
        Turn grids on and off
        '''
        for i,grid in enumerate(self.grid_items):
            if self.handlers[i]['Active'] and not grid in self.canvas.view.items:
                self.canvas.view.addItem(grid)
            elif not self.handlers[i]['Active'] and grid in self.canvas.view.items:
                self.canvas.view.removeItem(grid)

        self.scaleGrids()

    def scaleGrids(self):
        '''
        Scale the grids in the area
        '''
        for i,grid in enumerate(self.grid_items):
            if grid in self.canvas.view.items:
                grid.setSpacing(
                    self.handlers[i]['Scale'][0],
                    self.handlers[i]['Scale'][1])

    def sizeGrids(self):
        '''
        Scale the grids in the area
        '''
        for i,grid in enumerate(self.grid_items):
            if grid in self.canvas.view.items:
                grid.setSize(
                    [self.handlers[i]['Size'][0],self.handlers[i]['Size'][1]],
                    [self.handlers[i]['Size'][2],self.handlers[i]['Size'][3]])

    def processGrids(self):
        '''
        Scale the grids in the area
        '''
        for i in range(len(self.grid_items)):
            if self.grid_items[i] in self.canvas.view.items:
                self.canvas.view.removeItem(self.grid_items[i])
                self.grid_items[i] = GLGridItem()
                self.canvas.view.addItem(self.grid_items[i])
            else:
                self.grid_items[i] = GLGridItem()

            self.sizeGrids()
            self.scaleGrids()

            self.grid_items[i].rotate(self.handlers[i]['Angle'][0],1,0,0)
            self.grid_items[i].rotate(self.handlers[i]['Angle'][1],0,1,0)
            self.grid_items[i].rotate(self.handlers[i]['Angle'][2],0,0,1)

            self.grid_items[i].translate(*self.handlers[i]['Position'])

    def setColors(self):
        '''
        set the colors of the grid
        '''
        self.grid_items[0].setColor(*self.handlers[0]['Color'].getRgbF())
        self.grid_items[1].setColor(*self.handlers[1]['Color'].getRgbF())
        self.grid_items[2].setColor(*self.handlers[2]['Color'].getRgbF())

    def refreshAuto(self):
        '''
        refresh the axes automatically 
        based on the content
        '''
        if any([self.xy_handler['Auto'], self.xz_handler['Auto'], self.xz_handler['Auto']]):
            bounds = [[1.e2, -1.e2], [1.e2, -1.e2], [1.e2, -1.e2]]
            for child in self.canvas._plot_root._children:
                for plot_child in child._children:
                    if hasattr(plot_child, '_plot_data'):
                        new_bounds = plot_child._plot_data.getDrawBounds()
                        bounds = [
                            [min(bounds[0][0], new_bounds[0][0]), max(bounds[0][1], new_bounds[0][1])],
                            [min(bounds[1][0], new_bounds[1][0]), max(bounds[1][1], new_bounds[1][1])],
                            [min(bounds[2][0], new_bounds[2][0]), max(bounds[2][1], new_bounds[2][1])]]

            if self.xy_handler['Auto']:
                self.xy_handler['Position'] = [bounds[0][0], bounds[1][0], bounds[2][0]]
                self.xy_handler['Size'] = [0, bounds[0][1] - bounds[0][0], 0, bounds[1][1] - bounds[1][0]]

            if self.xz_handler['Auto']:
                self.xz_handler['Position'] = [bounds[0][0], bounds[1][0], bounds[2][0]]
                self.xz_handler['Size'] = [0, bounds[0][1] - bounds[0][0], 0, bounds[2][1] - bounds[2][0]]

            if self.xz_handler['Auto']:
                self.yz_handler['Position'] = [bounds[0][0], bounds[1][0], bounds[2][0]]
                self.yz_handler['Size'] = [0, bounds[2][1] - bounds[2][0], 0, bounds[1][1] - bounds[1][0]]

            self.setColors()
