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
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from ..pyqtgraph import pyqtgraph as pg
from .pointer_objects import *
from .pointer_pos import * 

from ..model.parameter_class import ParameterHandler
from ..model.node import SessionNode

class Pointer(SessionNode):
    '''
    This class will manage the pointer behavior. Note 
    that it will only bin and unbind on request. This 
    method should be exited to reach the desired
    behavior
    
    - if sticky is 0 the cursor is free
    - if sticky is 1 the cursor follows the closest line
    - if sticky is 2 the cursor sticks to points
    '''
    def __init__(self, canvas):
        SessionNode.__init__(
            self,name = 'Pointer elements', parent = canvas)
        self.pointer_handler    = ParameterHandler(
            name = 'Pointer', parent = self)
        self.tick_handler       = ParameterHandler(
            name = 'Ticks', parent = self)
        self.label_handler       = ParameterHandler(
            name = 'Label', parent = self)
        self.canvas = canvas
        self.initialize()

    def initialize(self):
        '''
        This method allows to set the pointer elements
        such as the hardcoded parameters and the 
        editable variables. 

        variables will be editable in the preference
        window and will therefore be saved as dict 
        with the proper values
        '''
        self.projections    = [None, None]
        self.method         = None
        
        self.x              = 0
        self.y              = 0
        self.cursor_x       = 0.0
        self.cursor_y       = 0.0
        self.link_list      = []
        self.method         = None

        self.pointer_component  = PointerObject(self)
        self.label_component    = PointerObject(self)
        self.pointer_position   = PointerPosition(self)
    
        self.pointer_handler.addParameter(
            'Color',  QtGui.QColor('black'),
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Thickness', 3,
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Precision', 1,
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Sticky', '0',
            choices = ['0','1','2','3'],
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Type', '0',
            choices = ['0','1', '2'],
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Size', [20,20],
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Live', True,
            method = self.processParameters)
        self.pointer_handler.addParameter(
            'Locked', False,
            method = self.processParameters)

        font = QtGui.QFont()
        if os.name == 'nt':
            font.setPointSize(12)
        else:
            font.setPointSize(12)

        self.label_handler.addParameter(
            'Present', [False,False,True,True],
            method = self.processParameters)
        self.label_handler.addParameter(
            'Type', '0',
            choices = ['0','1', '2'],
            method = self.processParameters)
        self.label_handler.addParameter(
            'Color',  QtGui.QColor('black'),
            method = self.processParameters)
        self.label_handler.addParameter(
            'Scientific',  [False,False,False,False],
            method = self.processParameters)
        self.label_handler.addParameter(
            'Precision',  [2,2,2,2],
            method = self.processParameters)  
        self.label_handler.addParameter(
            'Font', font,
            method = self.processParameters)       

        self.tick_handler.addParameter(
            'Present', [False,False,True,True],
            method = self.processParameters)
        self.tick_handler.addParameter(
            'Thickness', 5,
            method = self.processParameters)
        self.tick_handler.addParameter(
            'Color',  QtGui.QColor('blue'),
            method = self.processParameters)
        self.tick_handler.addParameter(
            'Offset',  0,
            method = self.processParameters)

    def processParameters(self):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        self.unbindPointer()
        self.setPen()
        self.bindPointer()

    def setPen(self):
        '''
        This method will initialise the QPen as the
        the QPainter method
        '''
        self.pen = pg.mkPen({
            'color': self.pointer_handler['Color'],
            'width': self.pointer_handler['Thickness']})
        

    def setup(self):
        '''
        Set the environnement and select the right
        pointer label and corrector type
        '''
        exec(
            'self.pointer_component = Type_'
            +str(self.pointer_handler['Type'])
            +'_Pointer(self)')

        exec(
            'self.label_component = Type_'
            +str(self.label_handler['Type'])
            +'_Labels(self)')

        exec(
            'self.pointer_position = Type_'
            +str(self.pointer_handler['Sticky'])
            +'_Position(self)')
        
        self.live = True

    def bindPointer(self):
        '''
        Binds the cursor to the system signals of th
        mouse 
        '''
        self.setup()
        self.refreshPlotData()
        self.canvas.artist.mouse.bind('move', self.refreshPosition, 'pointer_move')
        self.draw()

    def refreshPlotData(self):
        '''
        Binds the cursor to the system signals of th
        mouse 
        '''
        self.pointer_position.fetch_position_data()

    def unbindPointer(self):
        '''
        Binds the cursor to the system signals of the
        mouse 
        '''
        self.canvas.artist.mouse.unbind('move', 'pointer_move')
        self.pointer_component.disconnect()
        self.label_component.disconnect()
        self.live = False
        
    def refreshPosition(self,x = None, y = None):
        '''
        Refresh the local position of the cursor
        '''
        if x == None or y == None:
            x = self.canvas.artist.mouse.cursor_x 
            y = self.canvas.artist.mouse.cursor_y

        if not self.pointer_handler['Locked']:
            self.cursor_x = x
            self.cursor_y = y
            self.cursor_z = 0

            try:
                self.pointer_position.evaluate()
                self.canvas.multi_canvas.bottom_selector.label.setText(
                    str(
                        "  x = %"+str(self.pointer_handler['Precision'])+"f"
                        ", y = %"+str(self.pointer_handler['Precision'])+"f"
                        ", z = %"+str(self.pointer_handler['Precision'])+"f"
                        )%(
                            self.cursor_x,
                            self.cursor_y,
                            self.cursor_z))
            except:
                pass
        
        if self.pointer_handler['Live']:
            self.draw()

    def draw(self, init = True):
        '''
        In this method we will draw the cursor onto 
        the canvas. Note that this method will
        differentiate between initialization and
        the update
        '''
        self.pointer_component.move()
        self.label_component.move()
