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
import pyqtgraph as pg
import numpy as np

class Pointer_Object:
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.parent         = parent
        self.pointer_comp   = []
        self.label_comp     = []

    def disconnect(self):
        '''
        ##############################################
        Try to disconnect all methods
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for component in self.pointer_comp:
    
            self.parent.canvas.draw_surface.removeItem(component)

        for component in self.label_comp:
        
            self.parent.canvas.draw_surface.removeItem(component)

    def get_ranges(self):
        '''
        ##############################################
        Try to disconnect all methods
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.ranges = self.parent.canvas.draw_surface.viewRange()

class Type_0_Pointer(Pointer_Object):

    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        Pointer_Object.__init__(self,parent)
        self.parent = parent
        self.pointer_comp = []

        #set the pen
        self.parent.set_pen()

        #set the two inifinite lines
        self.pointer_comp.append(pg.InfiniteLine(
            angle   = 90, 
            movable = False,
            pen     = self.parent.pen))

        self.pointer_comp.append(pg.InfiniteLine(
            angle   = 00, 
            movable = False,
            pen     = self.parent.pen))

        #add them to the target
        for component in self.pointer_comp:

            self.parent.canvas.draw_surface.addItem(component)

    def move(self):
        '''
        ##############################################
        Move with the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.pointer_comp[0].setPos(self.parent.cursor_x)
        self.pointer_comp[1].setPos(self.parent.cursor_y)


class Type_1_Pointer(Pointer_Object):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        Pointer_Object.__init__(self,parent)
        self.parent = parent
        self.pointer_comp = []

        #set the pen
        self.parent.set_pen()
        self.get_ranges()

        #set the two inifinite lines
        self.pointer_comp.append(pg.PlotCurveItem(
            x       = np.asarray([0,1]), 
            y       = np.asarray([0,1]),
            pen     = self.parent.pen))

        self.pointer_comp.append(pg.PlotCurveItem(
            x       = np.asarray([0,1]), 
            y       = np.asarray([0,1]),
            pen     = self.parent.pen))

        p0 = pg.Point(0,0)
        p1 = pg.Point(1,1)
        ##############################################
        #add them to the target
        for component in self.pointer_comp:

            self.parent.canvas.draw_surface.addItem(component)

    def move(self):
        '''
        ##############################################
        Move with the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        self.get_ranges()

        ##############################################
        #perform the pixelsize

        try:
            p_0 = self.pointer_comp[0].mapToDevice(pg.Point(0,0))
            p_1 = self.pointer_comp[0].mapToDevice(pg.Point(1,1))

            self.pixel_size_x = 1 / abs(p_1.x() - p_0.x())
            self.pixel_size_y = 1 / abs(p_1.y() - p_0.y())

        except:
            self.pixel_size_x = 0.1
            self.pixel_size_y = 0.1

        self.pointer_comp[0].setData(
            np.asarray([
                self.parent.cursor_x - 10 * self.pixel_size_x  ,
                self.parent.cursor_x + 10 * self.pixel_size_x ]),
            np.asarray([
                self.parent.cursor_y,
                self.parent.cursor_y]))

        self.pointer_comp[1].setData(
            np.asarray([
                self.parent.cursor_x,
                self.parent.cursor_x]),
            np.asarray([    
                self.parent.cursor_y - 10 * self.pixel_size_y ,
                self.parent.cursor_y + 10 * self.pixel_size_y ]))

class Type_0_Labels(Pointer_Object):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Object.__init__(self,parent)
        self.parent = parent
        self.label_comp = []

        self.label_comp.append(pg.TextItem())

        #add them to the target
        for component in self.label_comp:

            component.setColor(QtGui.QColor(self.parent.get_para('Label_Color')))

            self.parent.canvas.draw_surface.addItem(component)

    def move(self):
        '''
        ##############################################
        Move with the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        text    = 'x = %'+str(self.parent.get_para('Label_Precision')[0])+'f'
        text   += ' y = %'+str(self.parent.get_para('Label_Precision')[2])+'f'

        #set the text to set the width
        self.label_comp[0].setText(str(text)%(self.parent.cursor_x,self.parent.cursor_y))

        #get the current view rnage
        self.get_ranges()
        anchor = [0,0]

        #do the checks and move the label around
        if self.parent.cursor_x > ( (self.ranges[0][1] - self.ranges[0][0]) / 2 + self.ranges[0][0]):
            anchor[0] = 1

        if self.parent.cursor_y < ( (self.ranges[1][1] - self.ranges[1][0]) / 2 + self.ranges[1][0]):
            anchor[1] = 1
            
        #set the anchor
        self.label_comp[0].anchor = pg.Point(anchor)

        #do the move
        self.label_comp[0].setPos(self.parent.cursor_x, self.parent.cursor_y)

class Type_1_Labels(Pointer_Object):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Object.__init__(self,parent)
        self.parent = parent
        self.label_comp = []

        self.label_comp.append(pg.TextItem())
        self.label_comp[-1].setAngle(90)

        self.label_comp.append(pg.TextItem())
        self.label_comp[-1].setAngle(90)

        self.label_comp.append(pg.TextItem())

        self.label_comp.append(pg.TextItem())

        #add them to the target
        for component in self.label_comp:

            component.setColor(QtGui.QColor(self.parent.get_para('Label_Color')))

            self.parent.canvas.draw_surface.addItem(component)

    def move(self):
        '''
        ##############################################
        Move with the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #set the text to set the width
        self.label_comp[0].setText(str('%'+str(self.parent.get_para('Label_Precision')[0])+'f ')%(self.parent.cursor_x))
        self.label_comp[1].setText(str('%'+str(self.parent.get_para('Label_Precision')[1])+'f ')%(self.parent.cursor_x))
        self.label_comp[2].setText(str('%'+str(self.parent.get_para('Label_Precision')[2])+'f ')%(self.parent.cursor_y))
        self.label_comp[3].setText(str('%'+str(self.parent.get_para('Label_Precision')[3])+'f ')%(self.parent.cursor_y))

        #get the current view rnage
        self.get_ranges()

        anchor_top      = [0,0]
        anchor_bot      = [1,0]
        anchor_left     = [0,0]
        anchor_right    = [1,0]

        #do the checks and move the label around
        if self.parent.cursor_x > ( (self.ranges[0][1] - self.ranges[0][0]) / 2 + self.ranges[0][0]):
            anchor_top[1] = 1
            anchor_bot[1] = 1

        if self.parent.cursor_y < ( (self.ranges[1][1] - self.ranges[1][0]) / 2 + self.ranges[1][0]):
            anchor_left[1] = 1
            anchor_right[1] = 1

        #do the move
        self.label_comp[0].anchor = pg.Point(anchor_top)
        self.label_comp[0].setPos(self.parent.cursor_x, self.ranges[1][0])

        self.label_comp[1].anchor = pg.Point(anchor_bot)
        self.label_comp[1].setPos(self.parent.cursor_x, self.ranges[1][1])

        self.label_comp[2].anchor = pg.Point(anchor_left)
        self.label_comp[2].setPos(self.ranges[0][0], self.parent.cursor_y)

        self.label_comp[3].anchor = pg.Point(anchor_right)
        self.label_comp[3].setPos(self.ranges[0][1], self.parent.cursor_y)


class Type_2_Labels(Pointer_Object):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Object.__init__(self,parent)
        self.parent = parent
        self.label_comp = []

        self.label_comp.append(pg.TextItem())

        self.label_comp.append(pg.TextItem())

        self.label_comp.append(pg.TextItem())
        self.label_comp[-1].setAngle(90)

        self.label_comp.append(pg.TextItem())
        self.label_comp[-1].setAngle(90)

        #add them to the target
        for component in self.label_comp:

            component.setColor(QtGui.QColor(self.parent.get_para('Label_Color')))

            self.parent.canvas.draw_surface.addItem(component)

    def move(self):
        '''
        ##############################################
        Move with the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #set the text to set the width
        self.label_comp[0].setText(str('%'+str(self.parent.get_para('Label_Precision')[0])+'f ')%(self.parent.cursor_x))
        self.label_comp[1].setText(str('%'+str(self.parent.get_para('Label_Precision')[1])+'f ')%(self.parent.cursor_x))
        self.label_comp[2].setText(str('%'+str(self.parent.get_para('Label_Precision')[2])+'f ')%(self.parent.cursor_y))
        self.label_comp[3].setText(str('%'+str(self.parent.get_para('Label_Precision')[3])+'f ')%(self.parent.cursor_y))

        #get the current view rnage
        self.get_ranges()

        anchor_top      = [0,1]
        anchor_bot      = [0,0]

        anchor_left     = [1,0]
        anchor_right    = [1,1]

        #do the checks and move the label around
        if self.parent.cursor_x > ( (self.ranges[0][1] - self.ranges[0][0]) / 2 + self.ranges[0][0]):
            anchor_top[0] = 1
            anchor_bot[0] = 1

        if self.parent.cursor_y < ( (self.ranges[1][1] - self.ranges[1][0]) / 2 + self.ranges[1][0]):
            anchor_left[0] = 0
            anchor_right[0] = 0

        #do the move
        self.label_comp[0].anchor = pg.Point(anchor_top)
        self.label_comp[0].setPos(self.parent.cursor_x, self.ranges[1][0])

        self.label_comp[1].anchor = pg.Point(anchor_bot)
        self.label_comp[1].setPos(self.parent.cursor_x, self.ranges[1][1])

        self.label_comp[2].anchor = pg.Point(anchor_left)
        self.label_comp[2].setPos(self.ranges[0][0], self.parent.cursor_y)

        self.label_comp[3].anchor = pg.Point(anchor_right)
        self.label_comp[3].setPos(self.ranges[0][1], self.parent.cursor_y)
