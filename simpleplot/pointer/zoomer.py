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


from ..pyqtgraph import pyqtgraph as pg
from ..pyqtgraph.pyqtgraph import functions as fn
from PyQt5 import QtGui,QtCore

import numpy as np


class Zoomer:
    '''
    This class will manage the zoom functionality.
    This is that the graph will be resized onto
    the area selected through the rectangular
    selection tool. 
    '''
    
    def __init__(self, canvas):
        
        #Bind to the canvas.
        self.canvas = canvas
    
        #launch defaults
        self.init_parameters()
    
    def init_parameters(self):
        '''
        Set the initial parameters of the zoombox
        '''
        #cursor parameters
        self.color      = 'black'
        self.thickness  = 2
        self.roundness  = 5
        self.fixed      = [False, False]
        self.fixed_range= [None, None, None, None]

        self.start_pos     = [0,0]
        self.end_pos       = [0,0]

        self.rbScaleBox = QtGui.QGraphicsRectItem(0, 0, 1, 1)
        self.rbScaleBox.setPen(fn.mkPen((50,50,50), width=1))
        self.rbScaleBox.setBrush(fn.mkBrush(50,50,50,100))
        self.rbScaleBox.setZValue(1e9)
        self.rbScaleBox.hide()
        self.canvas.view.addItem(self.rbScaleBox, ignoreBounds=True)

    def listen(self):
        '''
        Make the class listen to the click event 
        related to the zoom initializingevent.
        '''
        self.canvas.artist.mouse.bind('press', self.start_zoom, 'start_zoom', 1)

    def quiet(self):
        '''
        Quiet the zoom functionality.]
        '''
        self.canvas.artist.mouse.unbind('press', 'start_zoom')

    def set_pen(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        #initialise the pen
        self.pen = pg.mkPen({
                'color': QtGui.QColor(self.color),
                'width': self.thickness
            })

    def set_fixed(self, fixed = False, fixed_range= [None, None, None, None]):
        '''
        Sometimes the user wants to lock the zoom in
        place. 
        ''' 
        self.fixed = fixed
        self.fixed_range = fixed_range

    def set_brush(self):
        '''
        This method will initialise the Qpen as the
        the QPainter method
        '''
        #initialise the pen
        self.brush = pg.mkBrush(self.color)

    def start_zoom(self):
        '''
        Start to draw the zoom box. 
        ''' 
        #grab the actual cursor position from the Pointer class
        x,y = self.canvas.artist.mouse.get_pos()
        
        self.start_pos     = [x,y]
        self.end_pos       = [x,y]

        r = QtCore.QRectF(QtCore.QPointF(*self.start_pos),QtCore.QPointF(*self.end_pos))
        self.rbScaleBox.setPos(r.topLeft())
        self.rbScaleBox.resetTransform()
        self.rbScaleBox.scale(r.width(), r.height())
        self.rbScaleBox.show()

        #link the move lsitener
        self.canvas.artist.mouse.bind('move', self.update_zoom, 'update_zoom')
        self.canvas.artist.mouse.bind('release', self.end_zoom, 'end_zoom', 1)

        #remove the pointer
        self.canvas.artist.pointer.unbindPointer()
        
    def update_zoom(self,x,y):
        '''
        Updat the box as the mouse moves
        ''' 

        self.end_pos       = [x,y]

        r = QtCore.QRectF(QtCore.QPointF(*self.start_pos),QtCore.QPointF(*self.end_pos))
        self.rbScaleBox.setPos(r.topLeft())
        self.rbScaleBox.resetTransform()
        self.rbScaleBox.scale(r.width(), r.height())
        self.rbScaleBox.show()
        
        self.canvas.multi_canvas.bottom_selector.label.setText(
            str(
                "  x 0 = %."+str(self.roundness)+"f"
                ", x 1 = %."+str(self.roundness)+"f"
                ", y 0 = %."+str(self.roundness)+"f"
                ", y 1 = %."+str(self.roundness)+"f"
                )%(
                    self.start_pos[0],
                    self.end_pos[0],
                    self.start_pos[1],
                    self.end_pos[1] ))

        self.canvas.multi_canvas.bottom_selector.label.repaint()

    def end_zoom(self):
        '''
        End the zoom method and kill all the listeners
        ''' 
        
        self.rbScaleBox.hide()

        self.zoom()

        #shut down the links
        self.canvas.artist.mouse.unbind('move', 'update_zoom')
        self.canvas.artist.mouse.unbind('release','end_zoom')
        
        #try to project the information onto the first two free
        #fields of the main canvas
        self.canvas.multi_canvas.bottom_selector.label.setText('')

    def zoom(self):
        '''
        This processes the zoom method
        ''' 

        if (self.start_pos[0] == self.end_pos[0]) or (self.start_pos[1] == self.end_pos[1]): 
            self.canvas.artist.pointer.unbindPointer()
            self.canvas.draw_surface.autoRange()

            #check for fixed
            if self.fixed[0]:
                self.canvas.draw_surface.setXRange(self.fixed_range[0], self.fixed_range[1])
            
            if self.fixed[1]:
                self.canvas.draw_surface.setYRange(self.fixed_range[2], self.fixed_range[3])

            self.canvas.artist.pointer.bindPointer()


        else:

            #set possible rnages
            xRange = (self.start_pos[0], self.end_pos[0])
            yRange = (self.start_pos[1], self.end_pos[1])

            #check for fixed
            if self.fixed[0]:

                xRange = (self.fixed_range[0], self.fixed_range[1])
            
            if self.fixed[1]:
    
                xRange = (self.fixed_range[2], self.fixed_range[3])

            #finally zoom
            self.canvas.artist.pointer.unbindPointer()
            self.canvas.draw_surface.setRange(
                xRange = xRange,
                yRange = yRange)
            self.canvas.artist.pointer.bindPointer()
