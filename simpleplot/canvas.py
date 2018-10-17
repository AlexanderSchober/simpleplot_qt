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
from pyqtgraph import PlotWidget, ImageView, PlotItem
import pyqtgraph.opengl as gl
import pyqtgraph as pg

from .artist import Artist2D, Artist3D
from PyQt5 import QtWidgets, QtGui, QtCore

pg.setConfigOptions(antialias=True)

class Canvas_2D(QtGui.QWidget):

    def __init__(self, multi_canvas = None, idx = 0 , background = 'k', **kwargs):        
        '''
        ##############################################
        The canvas initializes as a widget and will 
        then be fed the layout of the Qgrid layout. 
        After this the widget will have a central
        drawsurface and other items can be fed around
        widget. 
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
        self.background     = background

        #initialize grid layout
        QtGui.QWidget.__init__(self)

        #initialize build
        self.populate()
        

    def populate(self):
        '''
        ##############################################
        populate the ui elements on the grid
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #create the layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)

        #create the center plot widget
        self.plot_widget = PlotWidget()
        self.draw_surface = self.plot_widget.getPlotItem()
        self.draw_surface.disableAutoRange()
        self.plot_widget.setBackground(self.background)

        self.plot_widget.mouseMoveEvent     = self.mouseMoveEvent_artist
        self.plot_widget.mousePressEvent    = self.mousePressEvent_artist
        self.plot_widget.mouseReleaseEvent  = self.mouseReleaseEvent_artist

        #put it into the layout
        self.grid_layout.addWidget(self.plot_widget, 1, 1)

        #set the layout to local widget
        self.setLayout(self.grid_layout)

        #wake up the artist
        self.artist = Artist2D(self)
        self.artist.setup()

    def mouseMoveEvent_artist(self, ev):
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

    def mousePressEvent_artist(self, ev):
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

    def mouseReleaseEvent_artist(self, ev):
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


class Canvas_3D(QtGui.QWidget):
    
    def __init__(self, multi_canvas = None, idx = 0 , background = 'k', **kwargs):        
        '''
        ##############################################
        The canvas initializes as a widget and will 
        then be fed the layout of the Qgrid layout. 
        After this the widget will have a central
        drawsurface and other items can be fed around
        widget. 
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
        self.background     = background

        #initialize grid layout
        QtGui.QWidget.__init__(self)

        #initialize build
        self.populate()

    def populate(self):
        '''
        ##############################################
        populate the ui elements on the grid
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #create the layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)

        #create the center plot widget
        self.view    = gl.GLViewWidget()
        # xgrid = gl.GLGridItem()
        # ygrid = gl.GLGridItem()
        # zgrid = gl.GLGridItem()
        # self.plot_widget.addItem(xgrid)
        # self.plot_widget.addItem(ygrid)
        # self.plot_widget.addItem(zgrid)
        # ## rotate x and y grids to face the correct direction
        # xgrid.rotate(90, 0, 1, 0)
        # ygrid.rotate(90, 1, 0, 0)

        # ## scale each grid differently
        # xgrid.scale(0.2, 0.1, 0.1)
        # ygrid.scale(0.2, 0.1, 0.1)
        # zgrid.scale(0.1, 0.2, 0.1)

        # import numpy as np
        # md = gl.MeshData.sphere(rows=10, cols=20)
        # #colors = np.random.random(size=(md.faceCount(), 4))
        # #colors[:,3] = 0.3
        # #colors[100:] = 0.0
        # colors = np.ones((md.faceCount(), 4), dtype=float)
        # colors[::2,0] = 0
        # colors[:,1] = np.linspace(0, 1, colors.shape[0])
        # md.setFaceColors(colors)
        # m3 = gl.GLMeshItem(meshdata=md, smooth=False)#, shader='balloon')

        # m3.translate(0, 0, 0)

        # self.plot_widget.addItem(m3)
        # self.draw_surface   = self.plot_widget.getPlotItem()
        # self.draw_surface.disableAutoRange()
        # self.plot_widget.setBackground(self.background)

        # self.plot_widget.mouseMoveEvent     = self.mouseMoveEvent_artist
        # self.plot_widget.mousePressEvent    = self.mousePressEvent_artist
        # self.plot_widget.mouseReleaseEvent  = self.mouseReleaseEvent_artist

        #put it into the layout
        self.grid_layout.addWidget(self.view, 1, 1)

        #set the layout to local widget
        self.setLayout(self.grid_layout)

        #wake up the artist
        self.artist = Artist3D(self)
        #self.artist.setup()