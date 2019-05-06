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
import pyqtgraph as pg
import numpy as np
import sys,os

from ..model.node import SessionNode
from ..model.parameter_class import ParameterHandler 

class Axes(SessionNode): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    def __init__(self, canvas):
        SessionNode.__init__(self,name = 'Axes', parent = canvas)
        self.general_handler    = ParameterHandler(
            name = 'General', parent = self)
        self.tick_handler       = ParameterHandler(
            name = 'Ticks', parent = self)
        self.label_handler       = ParameterHandler(
            name = 'Label', parent = self)
        self.canvas = canvas
        self.initialize()

    def initialize(self):
        '''
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any 
        default parameters.
        '''
        self.axes_list = []
        self.locations = ['left','bottom','right', 'top']
        for location in self.locations:
            self.axes_list.append(self.canvas.draw_surface.getAxis(location))

        self.general_handler.addParameter(
            'Active',  [True, True, False, False],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.activateAxes)
        self.general_handler.addParameter(
            'Grids', [False, False, 1.0],
            names  = ['x', 'y', 'alpha'],
            method = self.setGrid)
        self.general_handler.addParameter(
            'Log', [False, False],
            names  = ['x', 'y'],
            method = self.setLog)
        self.general_handler.addParameter(
            'Thickness', [2, 2, 2, 2],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setAxisStyle)
        self.general_handler.addParameter(
            'Color', [
                QtGui.QColor('b'),QtGui.QColor('b'),
                QtGui.QColor('b'),QtGui.QColor('b')],
            method = self.setAxisStyle)

        self.tick_handler.addParameter(
            'Active', [True, True, False, False],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setAxisStyle)
        self.tick_handler.addParameter(
            'Font', [
                QtGui.QFont(),QtGui.QFont(),
                QtGui.QFont(),QtGui.QFont()],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setAxisStyle)
        self.tick_handler.addParameter(
            'Offset',  [10, 10, 10, 10],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setAxisStyle)
        self.tick_handler.addParameter(
            'Length',  [-5, -5, -5, -5],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setAxisStyle)

        self.label_handler.addParameter(
            'Active', [False,False,False,False],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.showLabel)
        self.label_handler.addParameter(
            'Text', ['None','None','None','None'],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setLabel)
        self.label_handler.addParameter(
            'Unit', ['','','',''],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setLabel)
        self.label_handler.addParameter(
            'Font', [
                QtGui.QFont(),QtGui.QFont(),
                QtGui.QFont(),QtGui.QFont()],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setLabel)
        self.label_handler.addParameter(
            'Color',  [
                QtGui.QColor('b'),QtGui.QColor('b'),
                QtGui.QColor('b'),QtGui.QColor('b')],
            names  = ['left', 'bottom', 'right', 'top'],
            method = self.setLabel)   

    def processAllParameters(self):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        self.activateAxes()
        self.showLabel()
        self.setAxisStyle()
        self.setGrid()
        self.setLog()
        self.setLabel()

    def __getitem__(self, location):
        '''
        return the axis of the specified location
        '''
        return self.axes_list[self.locations.index(location)] 

    def activateAxes(self):
        '''
        Run through the locations and turn the 
        axes on or off
        '''
        for i in range(len(self.general_handler['Active'])):
            self.canvas.draw_surface.showAxis(
                self.locations[i], 
                show = self.general_handler['Active'][i])
        self.setAxisStyle()

    def setGrid(self):
        '''
        activate the grid or not
        '''
        self.canvas.draw_surface.showGrid( 
            self.general_handler['Grids'][0],
            self.general_handler['Grids'][1],
            self.general_handler['Grids'][2])

    def setLog(self):
        '''
        Set an axis to log. 
        '''
        self.canvas.draw_surface.setLogMode(
            x = self.general_handler['Log'][0],
            y = self.general_handler['Log'][1])

    def showLabel(self):
        '''
        This method decides to show the label
        '''
        for i in range(len(self.label_handler['Active'])):
            self.canvas.draw_surface.showLabel(
                self.locations[i], 
                show = self.label_handler['Active'][i])
        self.setLabel()

    def setLabel(self):
        '''
        This method will take care of the properties
        of the axis label
        '''
        for i in range(len(self.label_handler['Active'])):
            if self.label_handler['Active'][i]:
                labelStyle = {
                    'color': self.label_handler['Color'][i].name(), 
                    'font-size': str(self.label_handler['Font'][i].pointSize())+'pt',
                    'font-family':self.label_handler['Font'][i].family()}
                if self.label_handler['Font'][i].bold():
                    labelStyle['font-weight'] = 'bold'
                if self.label_handler['Font'][i].bold():
                    labelStyle['font-style'] = 'italic'
                
                self.axes_list[i].setLabel(
                    self.label_handler['Text'][i],
                    self.label_handler['Unit'][i],
                    **labelStyle)
        
    def setAxisStyle(self):
        '''
        This method will set the style of the axis like
        the color, the tick length, the tick and axis thickness
        and the tick offset.
        '''
        for i in range(len(self.tick_handler['Active'])):
            if self.general_handler['Active'][i]:
                self.axes_list[i].setPen(
                    color = self.general_handler['Color'][i],
                    width = self.general_handler['Thickness'][i])
            else:
                pass

            if self.tick_handler['Active'][i]:
                self.axes_list[i].setStyle(
                    tickLength = self.tick_handler['Length'][i],
                    tickTextOffset = self.tick_handler['Offset'][i])
                self.axes_list[i].tickFont = self.tick_handler['Font'][i]
            else:
                self.axes_list[i].setStyle( tickLength = 1 )

        self.setLabel()
        