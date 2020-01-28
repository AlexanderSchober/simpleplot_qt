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
import os

from ....models.data_axis_model import DataAxisModel 
from ....models.data_axis_item  import DataAxisItem
from ....models.delegates       import ParameterDelegate
from ....models.data_model      import DataModel

from ....core.io.io_data_save   import IODataSave
from ....core.io.io_data_import import IODataLoad

from ...gui_dialogs.data_save_dialog import SaveDataDialog

class DataWidget(QtWidgets.QWidget):
    '''
    '''
    def __init__(self,data_pointer, *args, **kwargs):
        super(DataWidget, self).__init__(*args, **kwargs)
        self._data_pointer = data_pointer
        self._setupLayout()
        self._connectMethods()

    def _setupLayout(self):
        '''
        This will build the layout of the current widget 
        by placing the two main components
        '''
        self._tool_bar = QtWidgets.QToolBar()
        self._splitter = QtWidgets.QSplitter()
        self._parameter_list = QtWidgets.QTableView()
        self._data_table = QtWidgets.QTableView()

        self._setupToolBar()

        self._axis_model = DataAxisModel()
        self._axis_delegate = ParameterDelegate()
        self._data_model = DataModel(self._data_pointer)

        self._parameter_list.verticalHeader().hide()
        self._parameter_list.setModel(self._axis_model)
        self._parameter_list.setItemDelegate(self._axis_delegate)

        self._data_table.setModel(self._data_model)
        self._data_table.verticalHeader().show()
        self._data_table.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self._data_table.horizontalHeader().setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self._data_table.verticalHeader().setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)

        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._splitter.addWidget(self._parameter_list)
        self._splitter.addWidget(self._data_table)
        self._main_layout.addWidget(self._tool_bar)
        self._main_layout.addWidget(self._splitter)

        self._axis_model.dataChanged.connect(self.updateDataView)

    def _setupToolBar(self):
        '''
        set up the tool bar for the data widget
        '''

        tool_button = QtWidgets.QToolButton()
        tool_button.setText("File")
        tool_button.setStyleSheet('QToolButton::menu-indicator { image: none; }')
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        file_menu = QtWidgets.QMenu(tool_button)
        item = file_menu.addAction("Load")
        item.triggered.connect(self._load)
        item = file_menu.addAction("Save")
        item.triggered.connect(self._save)
        item = file_menu.addAction("Save as ...")
        item.triggered.connect(self._saveAs)
        tool_button.setMenu(file_menu)

        self._tool_bar.addWidget(tool_button)

        tool_button = QtWidgets.QToolButton()
        tool_button.setText("Plot")
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        tool_button.clicked.connect(self._plot)
        self._tool_bar.addWidget(tool_button)

        tool_button = QtWidgets.QToolButton()
        tool_button.setText("Analyse")
        tool_button.setStyleSheet('QToolButton::menu-indicator { image: none; }')
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        analysis_menu = QtWidgets.QMenu(tool_button)
        item = analysis_menu.addAction("PCA")
        item.triggered.connect(self._load)
        item = analysis_menu.addAction("NMF")
        item.triggered.connect(self._save)
        item = analysis_menu.addAction("Fitting")
        item.triggered.connect(self._fit)
        tool_button.setMenu(analysis_menu)

        self._tool_bar.addWidget(tool_button)

    def _connectMethods(self):
        '''
        Connec the methods to their outs
        '''
        self._data_table.horizontalHeader().customContextMenuRequested.connect(
            self._colHeaderClicked)
        self._data_table.verticalHeader().customContextMenuRequested.connect(
            self._rowHeaderClicked)

    def setup(self):
        '''
        set up the models
        '''
        if self._data_pointer.axes == None:
            return

        self._axis_model.removeRows(0, self._axis_model.rowCount(None))

        axis_items = []
        for i in range(self._data_pointer.axes.dim):
            axis_items.append(DataAxisItem(
                self._data_pointer.axes.names[i], 
                self._data_pointer.axes.units[i],
                self._data_pointer.axes.axes[i]))
            
        self._axis_model.insertRows(0, len(axis_items), axis_items)
        self.updateDataView()

    def updateDataView(self):
        '''
        Upon changes int he axis model the 
        data view has to be rearranged
        '''
        names = self._data_pointer.axes.names

        index = [0 for i in names]
        for item in self._axis_model._root_item._children:
            index[names.index(item.kwargs['name'])] = item.kwargs['choices'].index(item.kwargs['value'])
            
        self._data_model.setDataIndex(index)

    def _rowHeaderClicked(self, pos):
        '''
        The user clicked the row header item
        '''
        global_pos = self._data_table.verticalHeader().mapToGlobal(pos)
        menu = QtWidgets.QMenu()
        plot_action = menu.addAction(
            "Plot row "
            +str(self._data_table.verticalHeader().logicalIndexAt(pos))
            +" ...")

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget._sidebar
        if target == None: return

        plot_action.triggered.connect(
            target.launchLinkCreator)

        menu.exec_(global_pos)
        
    def _colHeaderClicked(self, pos):
        '''
        The user clicked the row header item
        ''' 
        global_pos = self._data_table.horizontalHeader().mapToGlobal(pos)
        menu = QtWidgets.QMenu()
        plot_action = menu.addAction(
            "Plot column "
            +str(self._data_table.verticalHeader().logicalIndexAt(pos))
            +" ...")

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget._sidebar
        if target == None: return

        plot_action.triggered.connect(
            target.launchLinkCreator)

        menu.exec_(global_pos)

    def _plot(self):
        '''
        The user clicked the row header item
        ''' 
        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget._sidebar
        if target == None: return

        target.launchLinkCreator()

    def _load(self):
        '''
        The user clicked the row header item
        ''' 
        path = QtWidgets.QFileDialog.getOpenFileName(
            parent = self, filter = "Text (*.txt);;Hdf5 (*.h5)")
        
        if not path[0] == "":
            self._data_pointer.reset()
            loader = IODataLoad(self._data_pointer, path[0])
            loader.load(path[1].split("(*.")[1].split(")")[0])

    def _save(self):
        '''
        The user clicked the row header item
        ''' 

    def _saveAs(self):
        '''
        The user has requested to save the data
        ''' 
        name = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save File',"example", "Text (*.txt);;Hdf5 (*.h5)")

        if not name[0] == "":
            worker = IODataSave(self._data_pointer, name[0])
            worker.save(name[1].split("(*.")[1].split(")")[0])

    def _fit(self):
        '''
        The user has requested to fit the data
        ''' 
        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget._sidebar
        if target == None: return

        target.launchFitCreator()