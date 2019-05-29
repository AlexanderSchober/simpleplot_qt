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

from copy import deepcopy
import numpy as np

#personal imports
from ..artist.artist import Artist2DNode, Artist3DNode
from ..model.node import SessionNode
from ..model.parameter_class import ParameterHandler 
from ..model.models import SessionModel

from .SimplePlotGLViewWidget import MyGLViewWidget
from .SimplePlotWidget import SimplePlotWidget

from OpenGL import GL

class CanvasNode(SessionNode):

    def __init__(self, name, parent, **kwargs):        
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
        
        #set the locals from keywords
        self.multi_canvas   = kwargs['multi_canvas']
        self._initialize(**kwargs)
        self._buildSupport()
        self._buildGraph()

    def _initialize(self, **kwargs):
        '''
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        '''
        self.handler        = ParameterHandler(
            name = 'Canvas options', 
            parent = self) 

        self.handler.addParameter(
            'Type', kwargs['Type'],
            choices = ['2D', '3D'],
            method = self.switch)
        self.handler.addParameter(
            'Show', True,
            method = self._hideCanvas)
        self.handler.addParameter(
            'Background',  QtGui.QColor('white'),
            method = self._setBackground)
        self.handler.addParameter(
            'Horizontal spacing', 1,
            method = self._setHorizontalSpacing)
        self.handler.addParameter(
            'Vertical spacing', 1,
            method = self._setVerticalSpacing)

        self._plot_root  = SessionNode('Root', None) 
        self._plot_model = SessionModel(self._plot_root, self.multi_canvas)

    def _hideCanvas(self):
        '''
        Hides the canvas from the subplot view
        '''
        self.widget.setVisible(self.handler['Show'])
        self.multi_canvas.update()

    def _buildSupport(self):
        '''
        build the support base of the code
        '''
        self.widget         = QtGui.QWidget()
        self.widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.grid_layout = QtWidgets.QGridLayout()
        self.widget.setLayout(self.grid_layout)

    def _buildGraph(self):
        '''
        build the graph depending on the type
        '''
        try:
            self.para_group.deleteLater()
        except:
            pass

        self._populate()
        self._setBackground()

    def switch(self):
        self._model.removeRows(1,self.childCount()-1, self)
        self.plot_widget.deleteLater()
        self._populate()
        self._setBackground()
        self.artist.draw()
        self.multi_canvas._model.referenceModel()

    def _populate(self):
        '''
        General populate method that will check the 
        chosen state and try to redraw all.
        '''
        if self.handler['Type'] == '2D':
            self._populate2D()

        elif self.handler['Type'] == '3D':
            self._populate3D()

    def _populate2D(self):
        '''
        _populate the ui elements on the grid
        '''
        self.plot_widget = SimplePlotWidget(self)
        self.draw_surface = self.plot_widget.getPlotItem()
        self.view = self.draw_surface.getViewBox()
        self.view.setMouseMode(self.view.RectMode)
        
        
        # self.plot_widget.mouseMoveEvent     = self._mouseMoveEventArtist
        # self.plot_widget.mousePressEvent    = self._mousePressEventArtist
        # self.plot_widget.mouseReleaseEvent  = self._mouseReleaseEventArtist
        # self.view.scene().getContextMenus   = self._getContextMenus

        self.grid_layout.addWidget(self.plot_widget, 1, 1)

        self.artist = Artist2DNode(name = '2D Artist', parent = self, canvas = self)
        self.artist.setup()

    def _populate3D(self):
        '''
        populate the ui elements on the grid
        '''
        self.view = MyGLViewWidget(parent = self)
        self.grid_layout.addWidget(self.view, 1, 1)
        self.plot_widget = self.view

        self.artist = Artist3DNode('3D Artist', parent = self, canvas = self)
        self.artist.setup()

    def _setBackground(self):
        self.plot_widget.setBackground(
            self.handler['Background'])
        for widget in self.artist.child_widgets:
            widget.setBackground(self.handler['Background'])

    def _setVerticalSpacing(self):
        self.grid_layout.setVerticalSpacing(
            self.handler['Vertical spacing'])

    def _setHorizontalSpacing(self):
        self.grid_layout.setHorizontalSpacing(
            self.handler['Horizontal spacing'])

