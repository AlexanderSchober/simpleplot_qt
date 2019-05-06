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
from pyqtgraph import PlotWidget, ImageView, PlotItem
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore

#personal imports
from ..artist.artist import Artist2DNode, Artist3DNode
from ..model.node import SessionNode
from ..model.parameter_class import ParameterHandler 

pg.setConfigOptions(antialias=True)
class Canvas2DNode(SessionNode):
    
    def __init__(self,name, parent, **kwargs):        
        '''
        The canvas _initializes as a widget and will 
        then be fed the layout of the Grid layout. 
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
        
        self.multi_canvas   = kwargs['multi_canvas']
        self.idx            = kwargs['idx']
        self.started        = False
        self.widget         = QtGui.QWidget()
        self.general_handler    = ParameterHandler(
            name = 'Canvas options', parent = self)
        self._populate()
        self._initialize()
        self._setBackground()

    def _initialize(self):
        '''
        Initialize the parameter dictionary
        '''
        self.general_handler.addParameter(
            'Background',  QtGui.QColor('white'),
            method = self._setBackground)
        self.general_handler.addParameter(
            'Horizontal spacing', 1,
            method = self._setHorizontalSpacing)
        self.general_handler.addParameter(
            'Vertical spacing', 1,
            method = self._setVerticalSpacing)

    def processAllParameters(self):
        '''
        Will run through the items and set all the 
        properties thorugh the linked method
        '''
        for key in self.parameters.keys():
            self.parameters[key][1](self.parameters[key][0])

    def _setBackground(self):
        self.plot_widget.setBackground(
            self.general_handler['Background'])
        for widget in self.artist.child_widgets:
            widget.setBackground(self.general_handler['Background'])

    def _setVerticalSpacing(self):
        self.grid_layout.setVerticalSpacing(
            self.general_handler['Vertical spacing'])

    def _setHorizontalSpacing(self):
        self.grid_layout.setHorizontalSpacing(
            self.general_handler['Horizontal spacing'])

    def _populate(self):
        '''
        _populate the ui elements on the grid
        '''
        self.grid_layout = QtWidgets.QGridLayout()
        self.plot_widget = PlotWidget()
        self.draw_surface = self.plot_widget.getPlotItem()
        self.view = self.draw_surface.getViewBox()
        self.view.setMouseMode(self.view.RectMode)
        self.draw_surface.disableAutoRange()
        
        self.plot_widget.mouseMoveEvent     = self._mouseMoveEventArtist
        self.plot_widget.mousePressEvent    = self._mousePressEventArtist
        self.plot_widget.mouseReleaseEvent  = self._mouseReleaseEventArtist
        self.view.scene().getContextMenus   = self._getContextMenus

        self.grid_layout.addWidget(self.plot_widget, 1, 1)
        self.widget.setLayout(self.grid_layout)

        self.artist = Artist2DNode(name = '2D Artist', parent = self, canvas = self)
        self.artist.setup()

    def _getContextMenus(self, event):
        self.view.scene().contextMenuItem = event
        return self.view.scene().contextMenu

    def _mouseMoveEventArtist(self, ev):
        '''
        mouse move event
        '''
        self.artist.mouse_move(ev)

    def _mousePressEventArtist(self, ev):
        '''
        mouse press event
        '''
        self.view.mouseClickEvent(ev)
        self.artist.mouse_press(ev)

    def _mouseReleaseEventArtist(self, ev):
        '''
        mouse release event
        '''
        self.artist.mouse_release(ev)