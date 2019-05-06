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
from PyQt5 import QtGui
import numpy as np


class Measurer:
    '''
    Measure tool that allows the user to 
    investigate distances between points. 
    ———————
    Input: 
    - canvas is the parent canvas
    '''

    def __init__(self, canvas):
        self.canvas = canvas
        self._initialize()
    
    def _initialize(self):
        '''
        Set the initial parameters of the zoombox
        '''
        self.color      = 'black'
        self.thickness  = 2
        self.roundness  = 5

        self.start_pos  = [0,0]
        self.end_pos    = [0,0]

    def listen(self):
        '''
        Make the class listen to the click event 
        related to the zoom initializingevent.
        '''
        self.canvas.artist.mouse.bind('press', self.startMeasure, 'startMeasure', 1)

    def quiet(self):
        '''
        Quiet the zoom functionality.
        '''
        self.canvas.artist.mouse.unbind('press', 'startMeasure')

    def _setPen(self):
        '''
        This method will initialise the QPen as the
        the QPainter method
        '''
        self.pen = pg.mkPen({
                'color': QtGui.QColor(self.color),
                'width': self.thickness
            })

    def _setBrush(self):
        '''
        This method will initialise the QPen as the
        the QPainter method
        '''
        self.brush = pg.mkBrush(self.color)

    def startMeasure(self):
        '''
        Start to draw the zoom box. 
        ''' 
        self.start_pos     = [
            self.canvas.artist.pointer.cursor_x,
            self.canvas.artist.pointer.cursor_y]
        self.end_pos       = [
            self.canvas.artist.pointer.cursor_x,
            self.canvas.artist.pointer.cursor_y]

        #create the object
        self._setPen()

        self.line = pg.PlotCurveItem(
            x    = np.asarray([
                self.start_pos[0],
                self.end_pos[0]]), 
            y    = np.asarray([
                self.start_pos[1],
                self.end_pos[1]]),
            pen  = self.pen)

        self.dots = pg.ScatterPlotItem(
            x    = np.asarray([
                self.start_pos[0],
                self.end_pos[0]]), 
            y    = np.asarray([
                self.start_pos[1],
                self.end_pos[1]]),
            pen  = self.pen,
            size = 10)

        #put it on the draw surface
        self.canvas.draw_surface.addItem(self.line)
        self.canvas.draw_surface.addItem(self.dots)

        #link the move listener
        self.canvas.artist.mouse.bind('move', self.updateMeasure, 'updateMeasure')
        self.canvas.artist.mouse.bind('release', self.endMeasure, 'endMeasure', 1)

        #remove the pointer
        self.canvas.artist.pointer.unbindPointer()

    def updateMeasure(self,x,y):
        '''
        Update the box as the mouse moves
        ''' 
        self.canvas.artist.pointer.refreshPosition()

        self.end_pos       = [
            self.canvas.artist.pointer.cursor_x,
            self.canvas.artist.pointer.cursor_y]
        
        self.line.setData(
            np.asarray([
                self.start_pos[0],
                self.end_pos[0]]),
            np.asarray([
                self.start_pos[1],
                self.end_pos[1]]))

        self.dots.setData(
            np.asarray([
                self.start_pos[0],
                self.end_pos[0]]),
            np.asarray([
                self.start_pos[1],
                self.end_pos[1]]))

        self.canvas.multi_canvas.bottom_selector.label.setText(
            str(
                "  delta x = %."+str(self.roundness)+"f"
                "  delta y = %."+str(self.roundness)+"f"
                )%(
                    abs(self.end_pos[0] - self.start_pos[0]),
                    abs(self.end_pos[1] - self.start_pos[1])))

        self.canvas.multi_canvas.bottom_selector.label.repaint()

    def endMeasure(self):
        '''
        End the zoom method and kill all the listeners
        ''' 
        self.canvas.draw_surface.removeItem(self.line)
        self.canvas.draw_surface.removeItem(self.dots)
        del(self.line)
        del(self.dots)
        self.canvas.artist.pointer.bindPointer()

        self.canvas.multi_canvas.bottom_selector.label.setText('')

        self.canvas.artist.mouse.unbind('move', 'updateMeasure')
        self.canvas.artist.mouse.unbind('release','endMeasure')
