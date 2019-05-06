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
#   Alexander Schober <alex.schober@mac.com>
#
# *****************************************************************************

#import dependencies
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore

#personal imports
from ..artist.artist import  Artist3DNode
from ..model.node import SessionNode
from ..model.parameter_node import ParameterNode

pg.setConfigOptions(antialias=True)

class Canvas3DNode(SessionNode):
    
    def __init__(self,name, parent, multi_canvas = None, idx = 0 , background = 'k', **kwargs):        
        '''
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
        '''
        SessionNode.__init__(self,name, parent)
        #hierarchy
        self.multi_canvas   = multi_canvas
        self.started        = False
        self.idx            = idx
        self.background     = background
        self.widget         = QtGui.QWidget()

        #initialize build
        self.populate()

    def populate(self):
        '''
        populate the ui elements on the grid
        '''

        #create the layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)

        #create the center plot widget
        self.view = MyGLViewWidget()
        # xgrid = gl.GLGridItem()
        # ygrid = gl.GLGridItem()
        # zgrid = gl.GLGridItem()
        # self.view.addItem(xgrid)
        # self.view.addItem(ygrid)
        # self.view.addItem(zgrid)
        # ## rotate x and y grids to face the correct direction
        # xgrid.rotate(90, 0, 1, 0)
        # ygrid.rotate(90, 1, 0, 0)

        # ## scale each grid differently
        # xgrid.scale(0.2, 0.1, 0.1)
        # ygrid.scale(0.2, 0.1, 0.1)
        # zgrid.scale(0.1, 0.2, 0.1)

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
        self.widget.setLayout(self.grid_layout)

        #wake up the artist

        self.artist = Artist3DNode('3D Artist', parent = self, canvas = self)
        self.artist.setup()

class MyGLViewWidget(gl.GLViewWidget):

    """ Override GLViewWidget with enhanced behavior and Atom integration.
    
    """
    #: Fired in update() method to synchronize listeners.
    sigUpdate = QtCore.pyqtSignal()
    
    def mousePressEvent(self, ev):
        """ Store the position of the mouse press for later use.
        
        """
        super(MyGLViewWidget, self).mousePressEvent(ev)
        self._downpos = self.mousePos
            
    def mouseReleaseEvent(self, ev):
        """ Allow for single click to move and right click for context menu.
        
        Also emits a sigUpdate to refresh listeners.
        """
        super(MyGLViewWidget, self).mouseReleaseEvent(ev)
        if self._downpos == ev.pos():
            if ev.button() == 2:
                print('show context menu')
            elif ev.button() == 1:
                x = ev.pos().x() - self.width() / 2
                y = ev.pos().y() - self.height() / 2
                self.pan(-x, -y, 0, relative=True)

        self._prev_zoom_pos = None
        self._prev_pan_pos = None
        self.sigUpdate.emit()

    def evalKeyState(self):
        speed = 2.0
        if len(self.keysPressed) > 0:
            for key in self.keysPressed:
                if key == QtCore.Qt.Key_Right:
                    self.orbit(azim=-speed, elev=0)
                elif key == QtCore.Qt.Key_Left:
                    self.orbit(azim=speed, elev=0)
                elif key == QtCore.Qt.Key_Up:
                    self.orbit(azim=0, elev=-speed)
                elif key == QtCore.Qt.Key_Down:
                    self.orbit(azim=0, elev=speed)
                elif key == QtCore.Qt.Key_PageUp:
                    pass
                elif key == QtCore.Qt.Key_PageDown:
                    pass
                self.keyTimer.start(16)
        else:
            self.keyTimer.stop()

    def mouseMoveEvent(self, ev):
        diff = ev.pos() - self.mousePos
        self.mousePos = ev.pos()
        
        if ev.buttons() == QtCore.Qt.LeftButton:
            self.orbit(-diff.x(), diff.y())
            
        elif ev.buttons() == QtCore.Qt.MidButton:
            self.pan(diff.x(), diff.y(), 0, relative=True)

        elif ev.buttons() == QtCore.Qt.RightButton:
            self.pan(diff.x(), 0, diff.y(), relative=True)
