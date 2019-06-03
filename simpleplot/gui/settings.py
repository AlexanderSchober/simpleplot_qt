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


from ..pyqtgraph import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from .setting_window_ui import Ui_preference_window
from ..model.delegates  import ParameterDelegate

from .scatter_widget    import ScatterWidget
from .surface_widget    import SurfaceWidget
from .bar_widget        import BarWidget
from .volume_widget     import VolumeWidget

import sys
import numpy as np

class PreferenceWindow(QtGui.QMainWindow, Ui_preference_window):
    def __init__(self, multi_canvas, parent=None):
        super(PreferenceWindow, self).__init__(parent)
        self.setupUi(self)

        self.multi_canvas = multi_canvas
        self._initialize()

        self.canvas_tree_view.setModel(multi_canvas._model)
        self.canvas_tree_view.collapsed.connect(self._resizeTree)
        self.canvas_tree_view.expanded.connect(self._resizeTree)
        self.delegate = ParameterDelegate()
        self.canvas_tree_view.setItemDelegate(self.delegate)
        
        self.canvas_select.setModel(multi_canvas._model)
        self.canvas_select.currentIndexChanged.connect(self._selectCanvas)

        self.plot_tree_view.clicked.connect(self._updateTable)
        self.plot_tree_view.clicked.connect(self._setWidget)

        self._selectCanvas(0)

        self.plot_tree_view.collapsed.connect(self._resizePlotTree)
        self.plot_tree_view.expanded.connect(self._resizePlotTree)

        self.plot_data_view.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        self._resizePlotTree()
        self._resizeTree()

    def _initialize(self):
        '''
        Load the widgets
        '''
        self._scatter_class     = ScatterWidget()
        self._surface_class     = SurfaceWidget()
        self._bar_class         = BarWidget()
        self._volume_class      = VolumeWidget()

        self._scatter_widget    = self._scatter_class.local_widget
        self._surface_widget    = self._surface_class.local_widget
        self._bar_widget        = self._bar_class.local_widget
        self._volume_widget     = self._volume_class.local_widget

        self.editor_layout.addWidget(self._scatter_widget)
        self.editor_layout.addWidget(self._surface_widget)
        self.editor_layout.addWidget(self._bar_widget)
        self.editor_layout.addWidget(self._volume_widget)

        self._scatter_widget.hide()
        self._surface_widget.hide()
        self._bar_widget.hide()
        self._volume_widget.hide()

        self._current_widget = None
        self._current_class  = None
        

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
        '''
        self.plot_tree_view.setModel(self.multi_canvas._rootNode._children[index]._plot_model)

    def _setWidget(self):
        '''
        Set the right widget into the view to allow the edition 
        of the elements.
        '''
        if not self._current_widget == None:
            self._current_widget.hide()
            self._current_class.unlink()
            self._current_widget =  None

        index = self.plot_tree_view.selectedIndexes()[0]
        item  = index.model().getNode(index)

        if item.type == 'Scatter':
            self._current_widget = self._scatter_widget
            self._current_class = self._scatter_class
            self._current_class.link(item)
            self._current_widget.show()

        elif item.type == 'Surface':
            self._current_widget = self._surface_widget
            self._current_class = self._surface_class
            self._current_class.link(item)
            self._current_widget.show()

        elif item.type == 'Bar':
            self._current_widget = self._bar_widget
            self._current_class = self._bar_class
            self._current_class.link(item)
            self._current_widget.show()

        elif item.type == 'Volume':
            self._current_widget = self._volume_widget
            self._current_class = self._volume_class
            self._current_class.link(item)
            self._current_widget.show()

        else:
            pass
            
    def _updateTable(self):
        '''
        Put the elements into the table widget
        '''
        index = self.plot_tree_view.selectedIndexes()[0]
        item  = index.model().getNode(index)

        if item.type == 'Scatter':
            self.header     = []
            self.data_list  = []

            if not isinstance(item.x_data, type(None)):
                self.header.append('x')
                self.data_list.append(item.x_data.tolist())
            if not isinstance(item.y_data, type(None)):
                self.header.append('y')
                self.data_list.append(item.y_data.tolist())
            if not isinstance(item.z_data, type(None)):
                self.header.append('z')
                self.data_list.append(item.z_data.tolist())
            if not isinstance(item.parameters['Error'][0], type(None)):
                for key in item.parameters['Error'][0].keys():
                    if key in ['top', 'bottom', 'width', 'height']:
                        self.header.append(key)
                        values = item.parameters['Error'][0][key]
                        if isinstance(values, float) or isinstance(values, int):
                            self.data_list.append([item.parameters['Error'][0][key] for i in range(len(self.data_list[0]))])
                        else:
                            self.data_list.append(item.parameters['Error'][0][key])

            self.data_list = np.array(self.data_list).transpose().tolist()
            self.rows = [e for e in range(len(self.data_list))]

        elif item.type == 'Surface':
            self.header     = []
            self.data_list  = []

            if not isinstance(item.x_data, type(None)):
                self.header = np.around(item.x_data, 4).tolist()
            else:
                self.header = [i for i in range(item.z_data.shape[0])]

            if not isinstance(item.y_data, type(None)):
                self.rows = np.around(item.y_data, 4).tolist()
            else:
                self.rows = [i for i in range(item.z_data.shape[1])]

            self.data_list = item.z_data.tolist()

        else:
            self.header     = []
            self.data_list  = []
            self.rows       = []

        self.data_model = DataTableModel(
            self,self.data_list, 
            self.header,self.rows)

        self.plot_data_view.setModel(self.data_model)

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
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.data_list = sorted(self.data_list,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.data_list.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))