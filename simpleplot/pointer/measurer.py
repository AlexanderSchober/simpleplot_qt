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
    ##############################################
    Measure tool that allows the user to 
    insvestigate distances between points. 
    ———————
    Input: 
    - canvas is the parent canvas
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, canvas):
            
        #Bind to the canvas.
        self.canvas = canvas
    
        #launch defaults
        self.init_parameters()
    
    def init_parameters(self):
        '''
        ##############################################
        Set the initial parameters of the zoombox
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #cursor parameters
        self.color      = 'black'
        self.thickness  = 2
        self.roundness  = 5

        self.start_pos     = [0,0]
        self.end_pos       = [0,0]


    def listen(self):
        '''
        ##############################################
        Make the class listen to the click event 
        related to the zoom initializingevent.
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.canvas.artist.mouse.bind('press', self.start_measure, 'start_measure', 1)

    def quiet(self):
        '''
        ##############################################
        Quiet the zoom functionality.
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.canvas.artist.mouse.unbind('press', 'start_measure')

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
                'color': QtGui.QColor(self.color),
                'width': self.thickness
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
        self.brush = pg.mkBrush(self.color)

    def start_measure(self):
        '''
        ##############################################
        Start to draw the zoom box. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        ''' 
        #grab the actual cursor position from the Pointer class

        
        self.start_pos     = [
            self.canvas.artist.pointer.cursor_x,
            self.canvas.artist.pointer.cursor_y]
        self.end_pos       = [
            self.canvas.artist.pointer.cursor_x,
            self.canvas.artist.pointer.cursor_y]

        #create the object
        self.set_pen()

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

        #link the move lsitener
        self.canvas.artist.mouse.bind('move', self.update_measure, 'update_measure')
        self.canvas.artist.mouse.bind('release', self.end_measure, 'end_measure', 1)

        #remove the pointer
        self.canvas.artist.pointer.unbind_pointer()

    def update_measure(self,x,y):
        '''
        ##############################################
        Updat the box as the mouse moves
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        ''' 
        self.canvas.artist.pointer.refresh_pos()

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


    def end_measure(self):
        '''
        ##############################################
        End the zoom method and kill all the listeners
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        ''' 
        
        self.canvas.draw_surface.removeItem(self.line)
        self.canvas.draw_surface.removeItem(self.dots)
        del(self.line)
        del(self.dots)
        self.canvas.artist.pointer.bind_pointer()

        self.canvas.multi_canvas.bottom_selector.label.setText('')


        #shut down the links
        self.canvas.artist.mouse.unbind('move', 'update_measure')
        self.canvas.artist.mouse.unbind('release','end_measure')

