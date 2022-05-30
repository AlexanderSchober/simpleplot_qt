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

# import general
from PyQt5 import QtWidgets, QtGui, QtCore
import time

# import personal dependencies
from .canvas import CanvasNode
from ..models.plot_model import SessionModel
from ..gui_main.gui_plot.mode_select import ModeSelect
from ..models.session_node import SessionNode
from ..models.parameter_class import ParameterHandler


class MultiCanvasItem(QtWidgets.QGridLayout):
    add_plot_requested = QtCore.pyqtSignal(list)
    del_plot_requested = QtCore.pyqtSignal(list)

    def __init__(
            self, widget=None, grid=[[True]], element_types=None,
            x_ratios=[1], y_ratios=[1], no_title=False, **kwargs):
        """
        This method is the plot canvas where all the 
        elements will be drawn upon. It inherits
        from the GraphicsLayoutWidget library that 
        was custom built on top of qt for python. 

        Parameters
        ----------
        widget : QtWidgets.QWidget
            is the parent widget 

        grid : list of list of bool
            is the amount of rows ans cols wanted

        x_ratio : list of float
            is the ratios along the cols

        y_ratio : list of float
            is the ratios along the rows

        no_title allows to set titles or not
        """
        QtWidgets.QGridLayout.__init__(self)
        self._verbose = True
        self._time = None
        if self._verbose:
            self._time = time.time()
        self.grid = grid
        if self._verbose:
            print('MultiCanvas: Set up Grid: %s' % (time.time()-self._time))
            self._time = time.time()
        self.element_types = element_types
        self.x_ratios = [float(e) for e in x_ratios]
        self.y_ratios = [float(e) for e in y_ratios]
        self.parent = widget
        self.link_list = []

        self._setUp()
        if self._verbose:
            print('MultiCanvas: Set up : %s' % (time.time()-self._time))
            self._time = time.time()
        self._processSubPlots(**kwargs)
        if self._verbose:
            print('MultiCanvas: Process Subplots: %s' % (time.time()-self._time))
            self._time = time.time()
        self._initialise()
        if self._verbose:
            print('MultiCanvas: Init: %s' % (time.time()-self._time))
            self._time = time.time()

        self._placeObjects()
        if self._verbose:
            print('MultiCanvas: Place_objects: %s' % (time.time()-self._time))
            self._time = time.time()

        self._configureGrid()
        if self._verbose:
            print('MultiCanvas: Configure: %s' % (time.time()-self._time))
            self._time = time.time()
        self._layoutManager()
        if self._verbose:
            print('MultiCanvas: Layout manager: %s' % (time.time()-self._time))
            self._time = time.time()

        self._model.referenceModel()
        if self._verbose:
            print('MultiCanvas: Reference Model: %s' % (time.time()-self._time))
            self._time = time.time()

    def setup(self):
        """
        set up the models
        """
        pass

    def _setUp(self):
        """
        set up the pyqt part of the elements
        """
        self.widget_layout = QtWidgets.QGridLayout()
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.parent.setLayout(self.widget_layout)
        self.dock_widget = QtWidgets.QMainWindow()
        self.dock_widget.setDockOptions(
            QtGui.QMainWindow.AnimatedDocks
            | QtGui.QMainWindow.AllowNestedDocks)
        self.plot_dock = QtWidgets.QDockWidget()
        self.plot_dock.setFeatures(
            QtGui.QDockWidget.DockWidgetFloatable
            | QtGui.QDockWidget.DockWidgetMovable)
        self.plot_dock.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea
            | QtCore.Qt.RightDockWidgetArea
            | QtCore.Qt.TopDockWidgetArea
            | QtCore.Qt.BottomDockWidgetArea)
        self.plot_widget = QtWidgets.QWidget()
        self.plot_dock.setWidget(self.plot_widget)
        self.dock_widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.plot_dock)
        self.setContentsMargins(0, 0, 0, 0)
        self.plot_widget.setLayout(self)
        self.widget_layout.addWidget(self.dock_widget)

    def _processSubPlots(self, **kwargs):
        """
        set up the pyqt part of the elements
        """
        self.icon_dim = 25
        self.subplot_names = []
        self._rootNode = SessionNode('Root', None)
        self._model = SessionModel(self._rootNode, self, 2)

        self.canvas_nodes = [
            [None
             for i in range(len(self.grid[0]))]
            for j in range(len(self.grid))]

        grid_loop = [
            (i, j)
            for i in range(len(self.grid))
            for j in range(len(self.grid[0]))]

        for i, j in grid_loop:
            if not self.grid[i][j]:
                self.canvas_nodes[i][j] = [None, i, j]

            elif self.element_types is None or self.element_types[i][j] == '2D':
                self.subplot_names.append("Subplot (" + str(i) + ", " + str(j) + ")")
                temp_node = CanvasNode(
                    name="Subplot (" + str(i) + ", " + str(j) + ")",
                    multi_canvas=self,
                    idx=len(self.canvas_nodes),
                    Type='2D',
                    **kwargs)
                self._model.appendRow(temp_node, self._rootNode)
                self.canvas_nodes[i][j] = [temp_node, i, j]
                temp_node.buildGraph()

            elif self.element_types[i][j] == '3D':
                self.subplot_names.append("Subplot (" + str(i) + ", " + str(j) + ")")
                temp_node = CanvasNode(
                    name="Subplot (" + str(i) + ", " + str(j) + ")",
                    multi_canvas=self,
                    idx=len(self.canvas_nodes),
                    Type='3D',
                    **kwargs)
                self._model.appendRow(temp_node, self._rootNode)
                self.canvas_nodes[i][j] = [temp_node, i, j]
                temp_node.buildGraph()

        self._forceConfigurations()

    def _initialise(self):
        """
        Build the parameter class linked to 
        the session model
        """
        self.handler = ParameterHandler(
            name='Multi-canvas options')

        self.handler.addParameter(
            'x_ratios', self.x_ratios,
            method=self._configureGrid)
        self.handler.addParameter(
            'y_ratios', self.y_ratios,
            method=self._configureGrid)
        self.handler.addParameter(
            'Select', 'All',
            choices=['All'] + self.subplot_names,
            method=self._selectPlot)

        self._model.appendRow(self.handler, self._rootNode)

    def _forceConfigurations(self):
        """
        Force al the default configurations on the 
        sub canvas items
        """
        pass
        # grid_loop = [
        #     (i, j)
        #     for i in range(len(self.grid))
        #     for j in range(len(self.grid[0]))]

        # for i, j in grid_loop:
        #     if not self.canvas_nodes[i][j][0] is None:
        #         self.canvas_nodes[i][j][0].manageDefaultConfiguration()

    def _placeObjects(self):
        """
        This method aims at placing all the Canvas 
        class widgets onto the multiCanvas grid. It
        will therefore cycle through and use the 
        inherited addWidget method.
        """
        grid_loop = [
            (i, j)
            for i in range(len(self.grid))
            for j in range(len(self.grid[0]))]

        for i, j in grid_loop:
            if not self.canvas_nodes[i][j][0] is None:
                self.addWidget(
                    self.canvas_nodes[i][j][0].widget,
                    self.canvas_nodes[i][j][1],
                    self.canvas_nodes[i][j][2])

    def _configureGrid(self, zeros=False):
        """
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        """
        for i in range(len(self.handler['x_ratios'])):
            try:
                self.setColumnStretch(
                    i, self.handler['x_ratios'][i]
                    if not zeros else 0)
            except:
                pass

        for j in range(len(self.handler['y_ratios'])):
            try:
                self.setRowStretch(
                    j, self.handler['y_ratios'][j]
                    if not zeros else 0)
            except:
                if self.Verbose:
                    print('Could not set the row weight for: ', j)

    def _selectPlot(self):
        """
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        """
        if self.handler['Select'] == 'All':
            for child in self._rootNode.children():
                if 'Subplot' in child.name:
                    child.widget.setVisible(True)
            self._configureGrid()
        else:
            for child in self._rootNode.children():
                if 'Subplot' in child.name and child.name != self.handler['Select']:
                    child.widget.setVisible(False)
                elif 'Subplot' in child.name and child.name == self.handler['Select']:
                    child.widget.setVisible(True)
            self._configureGrid(zeros=True)

    def _layoutManager(self):
        """
        This method will process the layout of the 
        various simpleplot tools and buttons around
        the main frame. 
        """
        self.bottom_selector = ModeSelect(self, self.plot_widget, self.icon_dim)
        self.addWidget(
            self.bottom_selector,
            len(self.grid), 0, 1, len(self.grid[0]))

    def getSubplot(self, i, j):
        """
        Return the artist of a subplot
        similar to matplotlib
        """
        return self.canvas_nodes[i][j][0].artist()

    def link(self, ax, bx, var_in='x', var_out='x'):
        """

        """
        target = bx.canvas.mouse
        link = [
            '',
            ax.canvas.mouse.link_list,
            var_in,
            var_out,
            target,
            bx.canvas.mouse]
        self.link_list.append(link)
        identification = self.link_list[-1][0] = len(self.link_list)
        link[1].append(self.link_list[-1])

        return identification

    def addPlot(self, subplot_num):
        """
        This is simply a transfer for convenience
        when a subplot registers the request
        for a new plot
        """
        print("add_request")
        self.add_plot_requested.emit([
            self._rootNode.children()[subplot_num]])

    def removePlot(self, subplot_num, plot_item):
        """
        This is simply a transfer for convenience
        when a subplot registers the request
        for a new plot
        """
        self.add_plot_requested.emit([
            self._rootNode.children()[subplot_num],
            plot_item])
