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

from ...models.data_axis_select_item import DataAxisSelectItem
from ...models.data_axis_model import DataAxisModel
from ...models.project_node import DataLinkItem
from ...models.delegates import ParameterDelegate

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

        self._projects = []
        self._data = []
        self._plots = []
        self._dim_choices = [
            ["x", "Fixed"],
            ["x", "y", "Fixed"],
            ["x", "y", "z", "Fixed"]]
        self._plot_choices = [
            ["Scatter"],
            ["Surface", "Bar", "Step"],
            ["Volume", "Distribution"]]

        self._populateProjects()
        self._populateDataPlot()

        self._setupModel()

    def _setupGui(self):
        '''
        This function as the name indicates
        will generate the GUI to be placed
        onto the main window. 
        '''
        self.setWindowTitle("Create new plot from data")

        self._project_drop = QtWidgets.QComboBox()
        self._data_drop = QtWidgets.QComboBox()
        self._plot_drop = QtWidgets.QComboBox()
        self._subplot_drop = QtWidgets.QComboBox()
        self._selector = QtWidgets.QTabBar()
        self._axes_select = QtWidgets.QTableView()
        self._plot_type = QtWidgets.QComboBox()
        self._generate = QtWidgets.QPushButton("Generate")

        self._selector.addTab("2D")
        self._selector.addTab("3D")
        self._selector.addTab("4D")
        self._selector.setCurrentIndex(0)

        self._axes_select.setItemDelegate(ParameterDelegate())

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel("Project source:"), 0,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Data source:"), 1,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Plot target:"), 2,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Subplot target:"), 3,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Select dimensionality:"), 4,0,1,1)
        layout.addWidget(QtWidgets.QLabel("Select target type:"), 6,0,1,1)

        layout.addWidget(self._project_drop, 0,1,1,1)
        layout.addWidget(self._data_drop, 1,1,1,1)
        layout.addWidget(self._plot_drop, 2,1,1,1)
        layout.addWidget(self._subplot_drop, 3,1,1,1)
        layout.addWidget(self._selector, 4,1,1,1)
        layout.addWidget(self._axes_select, 5,0,1,2)
        layout.addWidget(self._plot_type, 6,1,1,1)
        layout.addWidget(self._generate, 7,1,1,1)

        self._project_drop.currentTextChanged.connect(self._populateDataPlot)
        self._plot_drop.currentTextChanged.connect(self._populateSubplot)
        self._selector.currentChanged.connect(self._setupModel)
        self._generate.clicked.connect(self.generate)

    def _populateProjects(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        root_pointer = target._model.root()

        for i in range(root_pointer.childCount()):
            if root_pointer.child(i).descriptor == 'project':
                self._projects.append(root_pointer.child(i))

        self._project_drop.addItems(
            [item._name for item in self._projects])

        if len(self._projects) > 0:
            self._project_drop.setCurrentIndex(0)

    def _populateDataPlot(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        self._data_drop.clear()
        self._plot_drop.clear()

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        root_pointer = target._model.root()

        self._data = []
        self._plots = []
        for i in range(root_pointer.childCount()):
            if root_pointer.child(i).descriptor == 'project' and root_pointer.child(i)._name == self._project_drop.currentText():

                data_root = root_pointer.child(i).childFromName('Datasets')
                self._data = data_root._children

                plot_root = root_pointer.child(i).childFromName('Plots')
                self._plots = plot_root._children

        self._data_drop.addItems(
            [item._name for item in self._data])
        self._plot_drop.addItems(
            [item._name for item in self._plots])

        if len(self._data) > 0:
            self._data_drop.setCurrentIndex(0)
        if len(self._plots) > 0:
            self._plot_drop.setCurrentIndex(0)

        self._populateSubplot()

    def _populateSubplot(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        self._subplot_drop.clear()

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        if self._plot_drop.currentText() == "": return
        
        self._subplots  = [
            item for item in 
            self._plots[self._plot_drop.currentIndex()].canvas_item._rootNode._children[:-1]]

        self._subplot_drop.addItems(
            [item._name for item in self._subplots])

        if len(self._data) > 0:
            self._subplot_drop.setCurrentIndex(0)

    def _setupModel(self):
        '''
        This will be the item that sets up 
        the model component of the widget and then
        populates it
        '''
        if len(self._data) == 0: return 
        self._model = DataAxisModel(col_count=4)
        target = self._data[self._data_drop.currentIndex()].data_item

        axes = target.axes
        if axes == None: return
        if len(target.DataObjects) == 0: return 
        
        index = 0
        for i in range(axes.dim):
            item = DataAxisSelectItem(
                axes.names[i],
                axes.units[i],
                axes.axes[i],
                self._dim_choices[self._selector.currentIndex()],
                self._dim_choices[self._selector.currentIndex()][index] if index < len(self._dim_choices[self._selector.currentIndex()]) - 1 else 'Fixed'
            )
            self._model._root_item.addChild(item)
            index += 1

        data_dummy = target.DataObjects[0]
        for i in range(len(data_dummy.data.shape)):
            item = DataAxisSelectItem(
                "Data axis n. "+str(i),
                "-",
                data_dummy.axes if len(data_dummy.data.shape) == 1 else data_dummy.axes[i],
                self._dim_choices[self._selector.currentIndex()], 
                self._dim_choices[self._selector.currentIndex()][index] if index < len(self._dim_choices[self._selector.currentIndex()]) - 1 else 'Fixed'
            )
            self._model._root_item.addChild(item)
            index += 1

        self._model.referenceModel()
        self._axes_select.setModel(self._model)

        self._plot_type.clear()
        self._plot_type.addItems(self._plot_choices[self._selector.currentIndex()])

    def generate(self):
        '''
        Gather all the information provided in th e
        individual fields and generate the data injector
        on the side of the data and the plot item on the
        side of the plot. Then link them,6
        '''
        subplot = self._subplots[self._subplot_drop.currentIndex()]
        plot_item = subplot.artist.addPlot(self._plot_type.currentText())
        data_item = self._data[self._data_drop.currentIndex()]
        data_link_item = DataLinkItem()
        data_injector = data_link_item.data_injector

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        target_model = target._model
        target_model.insertRows(
            data_item.childCount(), 1,
            [data_link_item], data_item
        )

        data_injector.setDataSource(data_item.data_item)
        data_injector.addPlotTarget(plot_item)

        behavior = []
        for child in self._model._root_item._children:
            behavior.append([
                child.data(0),
                child.data(1),
                child.dataIndex(2)
            ])
        data_injector.setBehavior(behavior, self._dim_choices[self._selector.currentIndex()][:-1])

