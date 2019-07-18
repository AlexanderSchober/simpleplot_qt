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
import numpy as np
import sys

from .custome_axis_item import GLAxisItem
from .custome_tick_item import GLTickItem
from .custome_label_item import GLLabelItem
from ..model.node import SessionNode
from ..model.parameter_class import ParameterHandler 

class Axes3D(SessionNode): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    def __init__(self, canvas):
        SessionNode.__init__(self,name = 'Axes', parent = canvas)
        self.canvas = canvas
        self.x_direction= ParameterHandler(
            name = 'X direction', parent = self)
        self.y_direction   = ParameterHandler(
            name = 'Y direction', parent = self)
        self.z_direction  = ParameterHandler(
            name = 'Z direction', parent = self)
        self.initialize()
            
    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self.axes_list = []
        self.tick_list = []
        self.label_list = []
        self.locations = ['x','y','z']
        for location in self.locations:
            self.axes_list.append(
                GLAxisItem(location = location)) 
            self.tick_list.append(
                GLTickItem(location = location)) 
            # self.label_list.append(
            #     GLLabelItem(location = location)) 

            self.axes_list[-1]._preprocess()
            self.tick_list[-1]._preprocess()
            # self.label_list[-1]._preprocess()

            self.canvas.view.addItem(self.axes_list[-1])
            self.canvas.view.addItem(self.tick_list[-1])
            # self.canvas.view.addItem(self.label_list[-1])

        self.x_direction.addParameter(
            'Auto',  True,
            method = self.refreshAuto)
        self.y_direction.addParameter(
            'Auto',  True,
            method = self.refreshAuto)
        self.z_direction.addParameter(
            'Auto',  True,
            method = self.refreshAuto)

        self.x_direction.addParameter(
            'Axis',  True,
            method = self.setAxes)
        self.y_direction.addParameter(
            'Axis',  True,
            method = self.setAxes)
        self.z_direction.addParameter(
            'Axis',  True,
            method = self.setAxes)

        self.x_direction.addParameter(
            'Ticks',  True,
            method = self.setTicks)
        self.y_direction.addParameter(
            'Ticks',  True,
            method = self.setTicks)
        self.z_direction.addParameter(
            'Ticks',  True,
            method = self.setTicks)

        # self.x_direction.addParameter(
        #     'Labels',  True,
        #     method = self.setLabels)
        # self.y_direction.addParameter(
        #     'Labels',  True,
        #     method = self.setLabels)
        # self.z_direction.addParameter(
        #     'Labels',  True,
        #     method = self.setLabels)

        self.x_direction.addParameter(
            'Position', [0.,0.,0.],
            names  = ['x', 'y', 'z'],
            method = self.changePosition)
        self.y_direction.addParameter(
            'Position', [0.,0.,0.],
            names  = ['x', 'y', 'z'],
            method = self.changePosition)
        self.z_direction.addParameter(
            'Position', [0.,0.,0.],
            names  = ['x', 'y', 'z'],
            method = self.changePosition)

        self.x_direction.addParameter(
            'Length', [-5., 5.],
            names  = ['min', 'max'],
            method = self.changeLength)
        self.y_direction.addParameter(
            'Length', [-5., 5.],
            names  = ['min', 'max'],
            method = self.changeLength)
        self.z_direction.addParameter(
            'Length', [-5., 5.],
            names  = ['min', 'max'],
            method = self.changeLength)

    def processAllParameters(self):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        self.setAxes()
        self.setTicks()
        # self.setLabels()
        self.changeLength()
        self.changePosition()

    def changePosition(self):
        '''
        '''
        self.axes_list[0].setPosition(self.x_direction['Position'])
        self.axes_list[1].setPosition(self.y_direction['Position'])
        self.axes_list[2].setPosition(self.z_direction['Position'])
        self.tick_list[0].setPosition(self.x_direction['Position'])
        self.tick_list[1].setPosition(self.y_direction['Position'])
        self.tick_list[2].setPosition(self.z_direction['Position'])

    def changeLength(self):
        '''
        '''
        self.axes_list[0].setLength(*self.x_direction['Length'])
        self.axes_list[1].setLength(*self.y_direction['Length'])
        self.axes_list[2].setLength(*self.z_direction['Length'])
        self.tick_list[0].setLength(*self.x_direction['Length'])
        self.tick_list[1].setLength(*self.y_direction['Length'])
        self.tick_list[2].setLength(*self.z_direction['Length'])

    def setAxes(self):
        '''
        '''
        array = [self.x_direction, self.y_direction, self.z_direction]
        for i,direction in enumerate(array):
            if direction['Axis'] and not self.axes_list[i] in self.canvas.view.items:
                self.canvas.view.addItem(self.axes_list[i])
            elif not direction['Axis'] and self.axes_list[i] in self.canvas.view.items:
                self.canvas.view.removeItem(self.axes_list[i])
            else:
                pass

    def setTicks(self):
        '''
        '''
        array = [self.x_direction, self.y_direction, self.z_direction]
        for i,direction in enumerate(array):
            if direction['Ticks'] and not self.tick_list[i] in self.canvas.view.items:
                self.canvas.view.addItem(self.tick_list[i])
            elif not direction['Ticks'] and self.tick_list[i] in self.canvas.view.items:
                self.canvas.view.removeItem(self.tick_list[i])
            else:
                pass

    def setLabels(self):
        '''
        '''
        array = [self.x_direction, self.y_direction, self.z_direction]
        for i,direction in enumerate(array):
            if direction['Labels'] and not self.label_list[i] in self.canvas.view.items:
                self.canvas.view.addItem(self.label_list[i])
            elif not direction['Labels'] and self.label_list[i] in self.canvas.view.items:
                self.canvas.view.removeItem(self.label_list[i])
            else:
                pass

    def refreshAuto(self):
        '''
        refresh the axes automatically 
        based on the content
        '''
        bounds = [[-1.e2, 1.e2], [-1.e2, 1.e2], [-1.e2, 1.e2]]
        for child in self.canvas._plot_root._children:
            for plot_child in child._children:
                if hasattr(plot_child, '_plot_data'):
                    new_bounds = plot_child._plot_data.getDrawBounds()
                    bounds = [
                        [max(bounds[0][0], new_bounds[0][0]), min(bounds[0][1], new_bounds[0][1])],
                        [max(bounds[1][0], new_bounds[1][0]), min(bounds[1][1], new_bounds[1][1])],
                        [max(bounds[2][0], new_bounds[2][0]), min(bounds[2][1], new_bounds[2][1])]]
                    
        items = [self.x_direction,self.y_direction,self.z_direction]
        for i,item in enumerate(items):
            if item['Auto']:
                item.items['Position'].updateValue([
                    float(bounds[0][0]),
                    float(bounds[1][0]), 
                    float(bounds[2][0])], method = True)
                item.items['Length'].updateValue(
                    [0, float(bounds[i][1] - bounds[i][0])], method = True)
        