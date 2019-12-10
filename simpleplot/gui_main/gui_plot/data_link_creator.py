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

from PyQt5 import QtCore, QtGui, QtWidgets

from ...models.data_axis_select_item import DataAxisItem
from ...models.data_axis_model import DataAxisModel

from ...models.project_node import DataItem
from ...models.project_node import PlotItem

class DataLinkCreator(QtWidgets.QDialog):
    '''
    This class will be create an interface between 
    data and the visual representations. This is 
    to be understood as a link from the data structure
    to the plot item by keeping in mind the chosen 
    charateristics
    '''
    def __init__(self, parent = None):
        super(DataLinkCreator, self).__init__(parent = parent)

        self._setupGui()
        self._setupModel()

        self._projects = []
        self._data = []
        self._plots = []

        self._populateProjects()

    def _setupGui(self):
        '''
        This function as the name indicates
        will generate the GUI to be placed
        onto the main window. 
        '''
        self._project_drop = QtWidgets.QComboBox()
        self._data_drop = QtWidgets.QComboBox()
        self._plot_drop = QtWidgets.QComboBox()
        self._subplot_drop = QtWidgets.QComboBox()
        self._selector = QtWidgets.QTabBar()
        self._axes_select = QtWidgets.QListView()

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel("Data source:"), 0,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Plot target:"), 1,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Subplot target:"), 2,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Select dimensionality:"), 3,0,1,1)

        layout.addWidget(self._data_drop, 0,1,1,1)
        layout.addWidget(self._plot_drop, 1,1,1,1)
        layout.addWidget(self._subplot_drop, 2,1,1,1)
        layout.addWidget(self._selector, 3,1,1,1)
        layout.addWidget(self._axes_select, 4,0,1,3)

    def _populateProjects(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        root_pointer = self.parent()._model.root()
        for i in range(root_pointer.childCount()):
            if root_pointer.child(i).descriptor == 'project':
                self._projects.append(root_pointer.child(i))

        self._project_drop.insertItems(
            [item.name() for item in self._projects])

        if len(self._projects) > 0:
            self._project_drop.setCurrentIndex(0)

    def _populateDataPlot(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        root_pointer = self.parent()._model.root()

    def _setupModel(self):
        '''
        This will be the item that sets up 
        the model component of the widget and then
        populates it
        '''

        # self._model = DataAxisModel()

        # for 
        # self._model._root_item.addChild()


        # self._axes_select.setModel(self._model)



        



        

