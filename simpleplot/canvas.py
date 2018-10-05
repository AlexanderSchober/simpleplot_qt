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
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
from .artist import Artist

pg.setConfigOptions(antialias=True)

class Canvas_2D(GraphicsLayoutWidget):

    #initialise the signals

    
    def __init__(self, multi_canvas = None, idx = 0 , background = 'k', **kwargs):        
        '''
        ##############################################
        This method is the plot cnavas where all the 
        elements will be drawn upon. It inherits
        from the Graphocslayoutwidget library that 
        was custom built on top of qt for python. 

        We want to override the event from the default
        graphicslayout of Qt. This is why the prensent
        function will make the events respond directly
        to the mouse and keyboard handlers.  
        ———————
        Input: 
        - parent is the parent widget to inherit from
        - multi_canvas is the Mutli_Canvas instance 
        - idx is simply the reference
        - width is the width of the element
        - heigh is the heigh of the element
        ———————
        Output: 
        -
        ———————
        status: active
        ##############################################
        '''
        
        #hirarchy
        self.multi_canvas   = multi_canvas
        self.started        = False
        self.idx            = idx
        
        #initialise the canvas
        GraphicsLayoutWidget.__init__(self)
        self.draw_surface = self.addPlot()
        self.draw_surface.disableAutoRange()
        self.setBackground(background)

        #initialise the drawer
        self.artist = Artist(self)
        self.artist.setup()

    def mouseMoveEvent(self, ev):
        '''
        ##############################################
        mouse move event
        ———————
        Input: 
        - Qt mouse event
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.artist.mouse_move(ev)

    def mousePressEvent(self, ev):
        '''
        ##############################################
        mouse press event
        ———————
        Input: 
        - Qt mouse event
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.artist.mouse_press(ev)

    def mouseReleaseEvent(self, ev):
        '''
        ##############################################
        mouse release event
        ———————
        Input: 
        - Qt mouse event
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.artist.mouse_release(ev)
        
    