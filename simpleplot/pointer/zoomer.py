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

from ..models.parameter_node import ParameterNode
from ..models.parameter_class import ParameterHandler 

import numpy as np


class Zoomer(ParameterHandler):
    '''
    This class will manage the zoom functionality.
    This is that the graph will be resized onto
    the area selected through the rectangular
    selection tool. 
    '''
    
    def __init__(self, canvas):
        ParameterHandler.__init__(self,name = 'Zoom / Pan', parent = canvas)

        self.canvas = canvas
        self._initialize()
        self._initRect()
    
    def _initialize(self):
        '''
        initialise the legend parameter structure
        '''
        self.addParameter(
            'Mode', 'Zoom',
            choices = ['Zoom', 'Pan'],
            method = self._setMode)
        self.addParameter(
            'Zoom fixed', [False, False],
            names = ['X', 'Y'],
            method = self.zoom)
        self.addParameter(
            'Zoom fixed range', [0.0, 1.0,0.0,1.0],
            names = ['X min','X max', 'Y min','Y max'],
            method = self.zoom)
        self.addParameter(
            'Zoom precision', 3)
        self.addParameter(
            'Zoom box', [QtGui.QColor(50,50,50,255),QtGui.QColor(50,50,50,100),1],
            names = ['Pen color','Brush color', 'Pen thickness'],
            method = self._initRect)

        self.start_pos     = [0,0]
        self.end_pos       = [0,0]
        self.reset_pos     = [0,0]

    def _initRect(self):
        '''
        Initialise the zoom rectangle upon changes of the 
        parameters
        '''
        self.rbScaleBox = QtGui.QGraphicsRectItem(0, 0, 1, 1)
        self.rbScaleBox.setPen(fn.mkPen(
            self['Zoom box'][0].getRgb(), 
            width=self['Zoom box'][2]))
        self.rbScaleBox.setBrush(fn.mkBrush(self['Zoom box'][1].getRgb()))
        self.rbScaleBox.setZValue(1e9)
        self.rbScaleBox.hide()
        self.canvas.view.addItem(self.rbScaleBox, ignoreBounds=True)

    def _setMode(self):
        pass

    def listen(self):
        '''
        Make the class listen to the click event 
        related to the zoom initializingevent.
        '''
        self.canvas.mouse.bind('press', self.resetStart, 'reset_start', 1, True)
        self.canvas.mouse.bind('release', self.resetEnd, 'reset_end', 1, True)
        self.canvas.mouse.bind('drag', self.zoomHandler, 'zoom_handler', 1)
        self.canvas.mouse.bind('drag', self.scaleHandler, 'start_scale', 2)

    def quiet(self):
        '''
        Quiet the zoom functionality.]
        '''
        self.canvas.mouse.unbind('press', 'reset_start')
        self.canvas.mouse.unbind('release', 'reset_end')
        self.canvas.mouse.unbind('drag', 'zoom_handler')
        self.canvas.mouse.unbind('drag', 'start_scale')

    def zoomHandler(self, x, y, drag_start, drag_end):
        '''
        Start to draw the zoom box. 
        ''' 
        r = QtCore.QRectF(QtCore.QPointF(x[0], y[0]),QtCore.QPointF(x[-1], y[-1]))
        self.rbScaleBox.setPos(r.topLeft())
        self.rbScaleBox.resetTransform()
        self.rbScaleBox.scale(r.width(), r.height())
        self.rbScaleBox.show()

        self.canvas.multi_canvas.bottom_selector.label.setText(
            str(
                "  x 0 = %."+str(self['Zoom precision'])+"f"
                ", x 1 = %."+str(self['Zoom precision'])+"f"
                ", y 0 = %."+str(self['Zoom precision'])+"f"
                ", y 1 = %."+str(self['Zoom precision'])+"f"
                )%(
                    self.start_pos[0],
                    self.end_pos[0],
                    self.start_pos[1],
                    self.end_pos[1] ))

        self.canvas.multi_canvas.bottom_selector.label.repaint()

        if drag_start:
            self.canvas.artist.pointer.unbindPointer()

        if drag_end:
            self.start_pos  = [x[0], y[0]]
            self.end_pos    = [x[-1], y[-1]]
            self.endZoom()
        
    def scaleHandler(self,x, y, drag_start, drag_end):
        '''
        ''' 
        pos     = pg.Point(x[2], y[2])
        last    = pg.Point(x[1], y[1])
        pos     =  self.canvas.draw_surface.vb.mapViewToDevice(pos)
        last    =  self.canvas.draw_surface.vb.mapViewToDevice(last)

        dif = np.array([
            pos.x() - last.x(), 
            pos.y() - last.y()])

        dif[0] *= -1
        s = (np.array([1.,1.])*0.02+1.) ** dif
        
        tr = self.canvas.view.childGroup.transform()
        tr = fn.invertQTransform(tr)
        
        x_new = s[0] 
        y_new = s[1]
        
        center = pg.Point(x[0],y[0])
        self.canvas.view._resetTarget()
        self.canvas.view.scaleBy(x=x_new, y=y_new, center=center)
        self.canvas.view.sigRangeChangedManually.emit(self.canvas.view.state['mouseEnabled'])

    def resetStart(self, ev):
        '''
        End the zoom method and kill all the listeners
        ''' 
        self.reset_pos     = [ev.x(),ev.y()]

    def resetEnd(self, ev):
        '''
        End the zoom method and kill all the listeners
        ''' 
        if self.reset_pos[0] == ev.x() or self.reset_pos[1] == ev.y():
            self.canvas.artist.pointer.unbindPointer()
            self.canvas.draw_surface.autoRange()

            #check for fixed
            if self['Zoom fixed'][0]:
                self.canvas.draw_surface.setXRange(
                    self['Zoom fixed range'][0], 
                    self['Zoom fixed range'][1])
            
            if self['Zoom fixed'][1]:
                self.canvas.draw_surface.setYRange(
                    self['Zoom fixed range'][2], 
                    self['Zoom fixed range'][3])

            self.canvas.artist.pointer.bindPointer()
            self.start_pos = self.reset_pos
            self.end_pos   = [ev.x(), ev.y()]

    def endZoom(self, quiet = False):
        '''
        End the zoom method and kill all the listeners
        ''' 
        self.rbScaleBox.hide()
        if not quiet:
            self.zoom()
        self.canvas.multi_canvas.bottom_selector.label.setText('')

    def zoom(self):
        '''
        This processes the zoom method
        ''' 
        if self.start_pos[0] == self.end_pos[0] or self.start_pos[1] == self.end_pos[1]: 
            self.canvas.draw_surface.autoRange()
            #check for fixed
            if self['Zoom fixed'][0]:
                self.canvas.draw_surface.setXRange(
                    self['Zoom fixed range'][0], 
                    self['Zoom fixed range'][1])
            
            if self['Zoom fixed'][1]:
                self.canvas.draw_surface.setYRange(
                    self['Zoom fixed range'][2], 
                    self['Zoom fixed range'][3])

        else:
            #set possible ranges
            xRange = (self.start_pos[0], self.end_pos[0])
            yRange = (self.start_pos[1], self.end_pos[1])

            #check for fixed
            if self['Zoom fixed'][0]:
                xRange = (
                    self['Zoom fixed range'][0], 
                    self['Zoom fixed range'][1])
            
            if self['Zoom fixed'][1]:
                xRange = (
                    self['Zoom fixed range'][2], 
                    self['Zoom fixed range'][3])

            #finally zoom
            self.canvas.draw_surface.setRange(
                xRange = xRange,
                yRange = yRange)
