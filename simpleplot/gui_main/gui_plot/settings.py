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

from PyQt5 import QtGui,QtCore,QtWidgets
from functools import partial

from ...pyqtgraph           import pyqtgraph as pg
from .setting_widget_ui     import Ui_settings_widget
from ...models.delegates    import ParameterDelegate
from .export_dialog         import ExportDialog
from ..side_bar_tree_view   import SidebarTreeView

import sys
import numpy as np

class PreferenceWidget(Ui_settings_widget):
    def __init__(self, multi_canvas, parent=None):
        self.multi_canvas = multi_canvas
        self._initialize()

        self.canvas_tree_view = SidebarTreeView(self.canvas_tab)
        self.canvas_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.verticalLayout_2.addWidget(self.canvas_tree_view)

        self.canvas_tree_view.setModel(multi_canvas._model)
        self.canvas_tree_view.collapsed.connect(self._resizeTree)
        self.canvas_tree_view.expanded.connect(self._resizeTree)

        self.delegate = ParameterDelegate()
        self.canvas_tree_view.setItemDelegate(self.delegate)
        self.plot_tree_view.setItemDelegate(self.delegate)

        self.canvas_select.setModel(multi_canvas._model)
        self.canvas_select.currentIndexChanged.connect(self._selectCanvas)
        self._selectCanvas(0)
        self.plot_tree_view.collapsed.connect(self._resizePlotTree)
        self.plot_tree_view.expanded.connect(self._resizePlotTree)
        self._resizePlotTree()
        self._resizeTree()

        self.add_plot.clicked.connect(partial(
            self.multi_canvas.addPlot,
            self.canvas_select.currentIndex()))
        # self.remove_plot.clicked.connect(
        #     partial(
        #         self.multi_canvas.deletePlot,
        #         self.canvas_select.index(),
        #         self. ))

        self.export_widget = ExportDialog()
        self.export_widget.ui.expSubplot.setModel(
            multi_canvas._model)
        self.export_widget.ui.expSubplot.currentIndexChanged.connect(
            self._selectExportCanvas)
        self._selectExportCanvas(0)
        self.io_layout.addWidget(self.export_widget)

        
        # self._save_canvas_button = QtWidgets.QPushButton("Save")
        # self._load_canvas_button = QtWidgets.QPushButton("Load")
        # temp_horizontal_layout = QtWidgets.QHBoxLayout()
        # temp_horizontal_layout.addWidget(self._save_canvas_button)
        # temp_horizontal_layout.addWidget(self._load_canvas_button)
        

    def _initialize(self):
        '''
        Load the widgets
        '''
        self.setting_widget = QtWidgets.QDockWidget()
        self.setting_widget.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea 
            | QtCore.Qt.RightDockWidgetArea
            | QtCore.Qt.TopDockWidgetArea
            | QtCore.Qt.BottomDockWidgetArea)
        self.dummy_widget   = QtWidgets.QWidget()
        self.setupUi(self.dummy_widget)
        self.setting_widget.setWidget(self.dummy_widget)

    def _resizeTree(self):
        '''
        Resize the tree on select
        '''
        self.canvas_tree_view.resizeColumnToContents(0)
        self.canvas_tree_view.resizeColumnToContents(1)

    def _resizePlotTree(self):
        '''
        Resize the tree on select
        '''
        self.plot_tree_view.resizeColumnToContents(0)
        self.plot_tree_view.resizeColumnToContents(1)

    def _selectCanvas(self, index):
        '''
        When the combobox is activated the selected canvas
        plot items should be displayed in the treeview

        Parameters:
        - - - - - - - - - - - 
        index : int
            The value of the cnvas in the index to export
        '''
        try:
            self.plot_tree_view.setModel(
                self.multi_canvas._rootNode._children[index]._plot_model)
        except:
            pass

    def _selectExportCanvas(self, index):
        '''
        send the currently selected subplot top the 
        export manager

        Parameters:
        - - - - - - - - - - - 
        index : int
            The value of the cnvas in the index to export
        '''
        self.export_widget.refreshSubplot(
            self.multi_canvas._rootNode._children[index])

class DataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, data_list, col_header,row_header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.data_list = data_list
        self.col_header = col_header
        self.row_header = row_header

    def rowCount(self, parent):
        return len(self.data_list)

    def columnCount(self, parent):
        if len(self.data_list) > 0:
            return len(self.data_list[0])
        else:
            return 0
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.data_list[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.col_header[col]
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self.row_header[col]
        else:
            return None
            