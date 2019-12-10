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

from ...models.plot_layout_model import PlotLayoutModel
from ...models.project_node import PlotItem
from .plot_setup_table import PlotSetupTableView


class PlotSetupDialog(QtWidgets.QDialog):
    '''
    '''
    accepted = QtCore.pyqtSignal(PlotItem)

    def __init__(self):
        super(PlotSetupDialog, self).__init__()
        self.setUpUi()
        self.setUpModel()

    def setUpUi(self):
        """
        This is the widget setup for this part
        """
        self._main_layout = QtWidgets.QVBoxLayout(self)

        #initialise things
        self._label = QtWidgets.QLabel("Please select the plot layout:")
        self._table_view = PlotSetupTableView(parent = self)

        self._cancel_button = QtWidgets.QPushButton(self)
        self._accept_button = QtWidgets.QPushButton(self)

        self._label.setAlignment(QtCore.Qt.AlignLeft)
        self._cancel_button.setText("Cancel")
        self._accept_button.setText("Generate")

        #place things
        self._main_layout.addWidget(self._label)
        self._main_layout.addWidget(self._table_view)

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self._cancel_button)
        layout.addWidget(self._accept_button)
        self._main_layout.addLayout(layout)

        self._cancel_button.clicked.connect(super().reject)
        self._accept_button.clicked.connect(self.accept)

    def setUpModel(self):
        """
        This table view will have a rather special model as it is 
        supposed to allow design of the multiplot layout
        """
        self._model = PlotLayoutModel()
        self._selectionModel = QtCore.QItemSelectionModel(self._model)
        self._model.setUpItems(6,6)

        self._table_view.setModel(self._model)
        self._table_view.setSelectionModel(self._selectionModel)

    def accept(self):
        '''
        Override the accept mehtod from he dialog and implement
        the retrieval of the important information
        '''
        selection_model = self._table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        
        row = [1e6, -1e6]
        col = [1e6, -1e6]
        for index in selected_indexes:
            if index.row() < row[0]: row[0] = index.row()
            if index.row() > row[1]: row[1] = index.row()
            if index.column() < col[0]: col[0] = index.column()
            if index.column() > col[1]: col[1] = index.column()

        grid_layout = [
            [
                False if self._model._internal_model.item(j,i).data() == "None" else True
                for i in range(int(col[0]), int(col[1]+1))
            ]
            for j in range(int(row[0]), int(row[1]+1))]

        element_types = [
            [
                self._model._internal_model.item(j,i).data()
                for i in range(int(col[0]), int(col[1]+1))
            ]
            for j in range(int(row[0]), int(row[1]+1))]

        item = PlotItem(
            grid = grid_layout, 
            element_types = element_types, 
            x_ratios = [1 for i in range(int(col[0]), int(col[1]+1))],
            y_ratios = [1 for j in range(int(row[0]), int(row[1]+1))])

        self.accepted.emit(item)
        super().accept()
