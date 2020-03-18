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
from functools import partial

class PlotSetupTableView(QtWidgets.QTableView):
    '''
    '''
    def __init__(self, **kwargs):
        super(PlotSetupTableView, self).__init__(**kwargs)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customMenuRequested)

    def customMenuRequested(self, position:QtGui.QMouseEvent):
        '''
        This will be the custom menu request to 
        change the item. 
        '''
        index = self.indexAt(position)
        
        if not index.isValid():
            return

        item = self.model().itemAt(index)
        value = item.data()

        temp_menu = QtWidgets.QMenu(self)
        if not value == "2D":
            action_2D = temp_menu.addAction("2D")
            action_2D.triggered.connect(partial(item.setData,0,0, "2D"))
        if not value == "3D":
            action_3D = temp_menu.addAction("3D")
            action_3D.triggered.connect(partial(item.setData,0,0, "3D"))
        if not value == "None":
            action_None = temp_menu.addAction("None")
            action_None.triggered.connect(partial(item.setData,0,0, "None"))

        temp_menu.popup(self.viewport().mapToGlobal(position))

    def editSelection(self, selected_items, deselected_items):
        '''
        Read the current selection pattern and then adapt
        the items
        '''
        for index in selected_items.indexes():
            self.model().itemAt(index)._selected = True
        for index in deselected_items.indexes():
            self.model().itemAt(index)._selected = False

    def setSelectionModel(self, QItemSelectionModel):
        super().setSelectionModel(QItemSelectionModel)
        QItemSelectionModel.selectionChanged.connect(self.editSelection)
        