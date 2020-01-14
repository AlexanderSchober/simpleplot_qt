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

from PyQt5 import QtWidgets, QtGui, QtCore

from .play_ground import Playground
from .side_bar import Sidebar

from ..models.project_class import ProjectHandler
from ..models.plot_model import PlotModel

from .gui_subwindows.subwindow_data.mainwindow_data import MainWindowData
from .gui_subwindows.subwindow_plot.mainwindow_plot import MainWindowPlot
from .gui_subwindows.subwindow_analysis.mainwindow_fit import MainWindowFit
from .gui_subwindows.subwindow_analysis.mainwindow_pca import MainWindowPCA

class MainWindow(QtWidgets.QMainWindow):
    '''
    This will be the gui anchor point of the 
    whole application and basically represents
    the initial sandbox to place items
    '''
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self._rootNode = ProjectHandler("Root", None)
        self._model = PlotModel(self._rootNode, self,  2)
        self._model.referenceModel()

        #Set up the visuals of the widget
        self._sidebar = Sidebar(self._model, parent = self)
        self._playground = Playground(parent = self)
        
        self._main_widget = QtWidgets.QSplitter(parent = self)
        self._main_widget.addWidget(self._sidebar)
        self._main_widget.addWidget(self._playground)

        self.setCentralWidget(self._main_widget)

    def displayData(self, item):
        '''
        Display data as an external window
        '''
        if not item.data_widget.parent() == None:
            item.data_widget.parent().close()

        window = MainWindowData(parent = self)
        item.data_widget.setupModels()
        window.setCentralWidget(item.data_widget)
        window.setWindowTitle(item._name)
        window.show()

    def displayPlot(self, item):
        '''
        Display plot as an external window
        '''
        if not item.canvas_widget.parent() == None:
            item.canvas_widget.parent().close()

        window = MainWindowPlot(parent = self)
        window.setCentralWidget(item.canvas_widget)
        window.setWindowTitle(item._name)
        window.show()

    def displayFit(self, item):
        '''
        Display data as an external window
        '''
        if not item.fit_widget.parent() == None:
            item.fit_widget.parent().close()

        window = MainWindowFit(parent = self)
        item.fit_widget.setupModels()
        window.setCentralWidget(item.fit_widget)
        window.setWindowTitle(item._name)
        window.show()

    def displayPCA(self, item):
        '''
        Display plot as an external window
        '''
        if not item.canvas_widget.parent() == None:
            item.canvas_widget.parent().close()

        window = MainWindowPCA(parent = self)
        window.setCentralWidget(item.canvas_widget)
        window.setWindowTitle(item._name)
        window.show()
