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
import numpy as np

class PointerObject:
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        self.parent         = parent
        self.pointer_comp   = []
        self.label_comp     = []

    def disconnect(self):
        '''
        Try to disconnect all methods
        '''
        for component in self.pointer_comp:
            if not component.scene() is None:
                component.scene().removeItem(component)

        for component in self.label_comp:
            if not component.scene() is None:
                component.scene().removeItem(component)

    def getRanges(self):
        '''
        Try to disconnect all methods
        '''
        self.ranges = self.parent.canvas.draw_surface.viewRange()

        pos_min = QtCore.QPointF(self.ranges[0][0],self.ranges[1][0])
        pos_min = self.parent.canvas.view.mapViewToDevice(pos_min)
        pos_min = QtCore.QPoint(pos_min.x(), pos_min.y()-2)
        pos_min = self.parent._pointer_view.mapToScene(pos_min)

        pos_max = QtCore.QPointF(self.ranges[0][1],self.ranges[1][1])
        pos_max = self.parent.canvas.view.mapViewToDevice(pos_max)
        pos_max = QtCore.QPoint(pos_max.x(), pos_max.y())
        pos_max = self.parent._pointer_view.mapToScene(pos_max)

        self.view_ranges = [[pos_min.x(),pos_max.x()],[pos_min.y(),pos_max.y()]]

    def getPosition(self):
        '''
        Process the drawing position
        '''
        pos = QtCore.QPointF(
            self.parent.cursor_x,
            self.parent.cursor_y)
        pos = self.parent.canvas.view.mapViewToDevice(pos)
        pos = QtCore.QPoint(pos.x()-2, pos.y()-2)
        pos = self.parent._pointer_view.mapToScene(pos)
        return pos
        
    def move(self):
        pass

class Type_0_Pointer(PointerObject):

    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerObject.__init__(self,parent)
        self.parent = parent
        self.pointer_comp = []
        self.getRanges()
        self.parent.setPen()
        self.pointer_comp.append(QtGui.QGraphicsLineItem())
        self.pointer_comp.append(QtGui.QGraphicsLineItem())

        #add them to the target
        for component in self.pointer_comp:
            component.setPen(self.parent.pen)
            self.parent._pointer_scene.addItem(component)

    def move(self):
        '''
        Move with the cursor
        '''
        pos = self.getPosition()

        self.pointer_comp[0].setLine(
            pos.x(),self.view_ranges[1][0],
            pos.x(),self.view_ranges[1][1])

        self.pointer_comp[1].setLine(
            self.view_ranges[0][0],pos.y(),
            self.view_ranges[0][1],pos.y())

class Type_1_Pointer(PointerObject):
    
    def __init__(self, parent):
        '''
        Type_1 cursor init
        '''
        PointerObject.__init__(self,parent)
        self.parent = parent
        self.pointer_comp = []
        self.getRanges()
        self.parent.setPen()
        self.pointer_comp.append(QtGui.QGraphicsLineItem())
        self.pointer_comp.append(QtGui.QGraphicsLineItem())

        #add them to the target
        for component in self.pointer_comp:
            component.setPen(self.parent.pen)
            self.parent._pointer_scene.addItem(component)

    def move(self):
        '''
        Move with the cursor
        '''
        pos = self.getPosition()

        self.pointer_comp[0].setLine(
            pos.x()-self.parent.pointer_handler['Size'][0],pos.y(),
            pos.x()+self.parent.pointer_handler['Size'][0],pos.y())

        self.pointer_comp[1].setLine(
            pos.x(),pos.y()-self.parent.pointer_handler['Size'][1],
            pos.x(),pos.y()+self.parent.pointer_handler['Size'][1])

class Type_0_Labels(PointerObject):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerObject.__init__(self,parent)
        self.parent = parent
        self.getRanges()

        self.label_comp = []
        self.label_comp.append(QtGui.QGraphicsTextItem())

        #add them to the target
        for component in self.label_comp:
            component.setDefaultTextColor(self.parent.label_handler['Color'])
            component.setFont(self.parent.label_handler['Font'])
            self.parent._pointer_scene.addItem(component)
            
    def move(self):
        '''
        Move with the cursor
        '''
        values = [
            10**self.parent.cursor_x if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() 
            else self.parent.cursor_x,
            10**self.parent.cursor_y if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() 
            else self.parent.cursor_y]

        text    = 'x = %0.'+str(self.parent.label_handler['Precision'][0])+'f'
        text   += ' y = %0.'+str(self.parent.label_handler['Precision'][2])+'f'

        #set the text to set the width
        self.label_comp[0].setPlainText(str(text)%(values[0],values[1]))
        
        rect = self.label_comp[0].boundingRect()
        delta = [0,0]
        if self.parent.cursor_x > ( (self.ranges[0][1] - self.ranges[0][0]) / 2 + self.ranges[0][0]):
            delta[0] = rect.width()

        if self.parent.cursor_y < ( (self.ranges[1][1] - self.ranges[1][0]) / 2 + self.ranges[1][0]):
            delta[1] = rect.height()

        #do the move
        pos = self.getPosition()
        self.label_comp[0].setPos(pos.x()-delta[0], pos.y()-delta[1])

class Type_1_Labels(PointerObject):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerObject.__init__(self,parent)
        self.parent = parent
        self.getRanges()

        self.label_comp = []
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())

        self.label_comp[0].rotate(90)
        self.label_comp[1].rotate(90)

        #add them to the target
        for component in self.label_comp:
            component.setDefaultTextColor(self.parent.label_handler['Color'])
            component.setFont(self.parent.label_handler['Font'])
            self.parent._pointer_scene.addItem(component)

    def move(self):
        '''
        Move with the cursor
        '''
        values = [
            10**self.parent.cursor_x if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else self.parent.cursor_x,
            10**self.parent.cursor_y if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else self.parent.cursor_y]
            
        #set the text to set the width
        self.label_comp[0].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][0])+'f ')%(values[0]))
        self.label_comp[1].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][1])+'f ')%(values[0]))
        self.label_comp[2].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][2])+'f ')%(values[1]))
        self.label_comp[3].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][3])+'f ')%(values[1]))

        pos = self.getPosition()

        rect = self.label_comp[0].boundingRect()
        delta = [0,0]
        if self.parent.cursor_x >((self.ranges[0][1]-self.ranges[0][0])/2+self.ranges[0][0]):
            delta[0] = 0
        else: 
            delta[0] = rect.width()

        self.label_comp[0].setPos(pos.x()+delta[0], self.view_ranges[1][0]-rect.width())
        self.label_comp[1].setPos(pos.x()+delta[0], self.view_ranges[1][1])

        rect = self.label_comp[2].boundingRect()
        delta = [0,0]
        if self.parent.cursor_y <((self.ranges[1][1]-self.ranges[1][0])/2+self.ranges[1][0]):
            delta[1] = rect.height()

        self.label_comp[2].setPos(self.view_ranges[0][0], pos.y()-delta[1])
        self.label_comp[3].setPos(self.view_ranges[0][1]-rect.width(), pos.y()-delta[1])


class Type_2_Labels(PointerObject):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerObject.__init__(self,parent)
        self.parent = parent
        self.getRanges()

        self.label_comp = []
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())
        self.label_comp.append(QtGui.QGraphicsTextItem())

        self.label_comp[2].rotate(90)
        self.label_comp[3].rotate(90)

        #add them to the target
        for component in self.label_comp:
            component.setDefaultTextColor(self.parent.label_handler['Color'])
            component.setFont(self.parent.label_handler['Font'])
            self.parent._pointer_scene.addItem(component)

    def move(self):
        '''
        Move with the cursor
        '''
        values = [
            10**self.parent.cursor_x if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else self.parent.cursor_x,
            10**self.parent.cursor_y if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else self.parent.cursor_y]
            
        #set the text to set the width
        self.label_comp[0].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][0])+'f ')%(values[0]))
        self.label_comp[1].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][1])+'f ')%(values[0]))
        self.label_comp[2].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][2])+'f ')%(values[1]))
        self.label_comp[3].setPlainText(
            str('%0.'+str(self.parent.label_handler['Precision'][3])+'f ')%(values[1]))

        pos = self.getPosition()

        rect = self.label_comp[0].boundingRect()
        delta = [0,0]
        if self.parent.cursor_x >((self.ranges[0][1]-self.ranges[0][0])/2+self.ranges[0][0]):
            delta[0] = rect.width()

        self.label_comp[0].setPos(pos.x()-delta[0], self.view_ranges[1][0]-rect.height())
        self.label_comp[1].setPos(pos.x()-delta[0], self.view_ranges[1][1])

        rect = self.label_comp[2].boundingRect()
        delta = [0,0]
        if self.parent.cursor_y >((self.ranges[1][1]-self.ranges[1][0])/2+self.ranges[1][0]):
            delta[1] = 0
        else:
            delta[1] = -rect.width()

        self.label_comp[2].setPos(self.view_ranges[0][0]+rect.height(), pos.y()+delta[1])
        self.label_comp[3].setPos(self.view_ranges[0][1], pos.y()+delta[1])
