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
import itertools

from .plot_layout_item import PlotLayoutItem
from .plot_model import SessionModel

class PlotLayoutModel(QtCore.QAbstractTableModel): 
    def __init__(self, parent=None, *args): 
        super(PlotLayoutModel, self).__init__()
        self._internal_model = QtGui.QStandardItemModel()

    def setUpItems(self, rows:int, columns:int):
        """
        This will be the method in charge of seting up
        all the elements int he _internal model
        """
        for i,j in itertools.product(range(rows), range(columns)):
            self._internal_model.setItem(
                i,j, PlotLayoutItem())

    def rowCount(self, parent)->int:
        return self._internal_model.rowCount()

    def columnCount(self, parent)->int:
        return self._internal_model.columnCount()
    
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = self._internal_model.item(index.row(), index.column())

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data()
 
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
            
        if role == SessionModel.sortRole:
            return node.typeInfo()

        if role == SessionModel.filterRole:
            return node.typeInfo()

        if role == QtCore.Qt.BackgroundRole:
            if type(node.data()) == QtGui.QColor:
                return QtGui.QBrush(node.data(index.column()))

    def flags(self, index):
        item = self.itemAt(index)
        return item.flags(index)

    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            node = self._internal_model.item(index.row(), index.column())
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True
            
        return False

    def itemAt(self, index:QtCore.QModelIndex)->PlotLayoutItem:
        return self._internal_model.item(index.row(), index.column())
