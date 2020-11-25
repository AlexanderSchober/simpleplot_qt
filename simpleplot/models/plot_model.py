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
from __future__ import annotations

from typing import Union, List

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QVariant

from .modal_items import QColorDialog, QFontDialog
from .session_node import SessionNode


class SessionModel(QtCore.QAbstractItemModel):
    """
    This is a general plot model interface. it is built with the
    SessionItem and its derivatives in mind and might not be able
    to accept other model type instances. This model is tailored
    to interface with a tree-view and might perform poorly with
    other interfaces.
    """
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root: SessionNode, parent: QtCore.QObject = None, col_count: int = 2):
        super(SessionModel, self).__init__(parent)
        self._root_node = root
        self._col_count = col_count
        self.color_picker = QColorDialog()
        self.font_picker = QFontDialog()
        self.referenceModel()

    def referenceModel(self) -> None:
        """
        This method starts a cascade of referencing so every
        item within the model is aware of it.
        :return: None
        """
        self._root_node.referenceModel(self)

    def root(self) -> SessionNode:
        return self._root_node

    # noinspection PyMethodOverriding
    def rowCount(self, parent):
        if not parent.isValid():
            return self._root_node.childCount()
        else:
            return parent.internalPointer().childCount()

    # noinspection PyMethodOverriding
    def columnCount(self, parent) -> int:
        return self._col_count

    # noinspection PyMethodOverriding
    def data(self, index: QModelIndex, role: int) -> Union[QVariant, None, QtGui.QIcon, QtGui.QBrush]:
        """
        This manages what to do when the data method is called within the model.
        Note that unlike the data method of the standard item this one has to also 
        handle different visual aspects. This method will mostly be called by the
        view and should not be to important for the user.
        :param index: QModelIndex, index of the targeted item
        :param role: int, the targeted role
        :return: Union[QVariant, None, QtGui.QIcon, QtGui.QBrush]
        """
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))

        if role == SessionModel.sortRole:
            return node.typeInfo()

        if role == SessionModel.filterRole:
            return node.typeInfo()

        if role == QtCore.Qt.BackgroundRole:
            if type(node.data(index.column())) == QtGui.QColor:
                return QtGui.QBrush(node.data(index.column()))

        if role == QtCore.Qt.FontRole:
            if type(node.data(index.column())) == QtGui.QFont:
                return node.data(index.column())

    def setData(self, index: QModelIndex, value: QVariant, role=QtCore.Qt.EditRole) -> bool:
        """
        The set data method override
        :param index: QModelIndex, index of the target item
        :param value: QVariant, the value to set
        :param role: int, the role targeted (usually edit role)
        :return: bool, reports about the success of the operation
        """
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True

        return False

    # noinspection PyMethodOverriding
    def headerData(self, section: int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Properties"
            else:
                return ""

    def flags(self, index: QModelIndex) -> QtCore.Qt.ItemFlags:
        """
        Returns the flags of the targeted item
        :param index: QModelIndex
        :return: QtCore.Qt.ItemFlag
        """
        item = self.getNode(index)
        return item.flags(index)

    def parent(self, index: QModelIndex) -> QModelIndex:
        """
        Return the parent index of a provided index
        :param index: QModelIndex, the given index
        :return: QModelIndex, the parent index
        """
        node = self.getNode(index)
        parent_node = node.parent()

        if parent_node == self._root_node or parent_node is None or parent_node.row() is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    # noinspection PyMethodOverriding
    def index(self, row: int, column: int, parent: QModelIndex):
        """
        This method builds a QModelIndex item for a given parent, row and column.
        :param row: int
        :param column: column
        :param parent: QModelIndex, the parent node
        :return: QModelIndex
        """
        parent_node = self.getNode(parent)
        child_item = parent_node.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def getNode(self, index: QModelIndex) -> SessionNode:
        node = index.internalPointer()
        if node:
            return node
        return self._root_node

    def itemAt(self, index: QModelIndex) -> SessionNode:
        """
        Return the item associated to the given index
        :param index: QModelIndex, the index of the item to retrieve
        :return: SessionNode
        """
        if not index.parent().internalPointer() is None:
            return index.parent().internalPointer().child(index.row())
        else:
            return self.getNode(index)

    # noinspection PyMethodOverriding
    def insertRows(self, position: int, rows: int, items: List[SessionNode], parent: SessionNode) -> bool:
        """
        The override of the insert method
        :param position: int, the target insert row number
        :param rows: int, the number of rows to insert
        :param items: List[SessionNode], the list of items to insert
        :param parent: SessionNode, the target parent to insert into
        :return: bool, return the success of the insert
        """
        success = False
        self.beginInsertRows(
            parent.index(), position,
            position + rows - 1)

        for row in range(rows):
            items[row].referenceModel(self)
            success = parent.insertChild(position, items[row])

        self.endInsertRows()
        self.referenceModel()

        return success

    def appendRow(self, item: SessionNode, parent: SessionNode) -> bool:
        """
        Append an item as the last position of a parent
        :param item: SessionNode, the item to insert
        :param parent: SessionNode, the parent to insert into
        :return: bool, the success of the insert
        """
        position = len(parent.children())
        self.beginInsertRows(
            parent.index(),
            position, position)

        item.referenceModel(self)
        success = parent.insertChild(position, item)

        self.endInsertRows()
        self.referenceModel()

        return success

    # noinspection PyMethodOverriding
    def removeRows(self, position, rows, parent: SessionNode):
        """
        Remove the child rows from a parent item
        :param position: int, the target position to delete
        :param rows: int, how many rows to remove
        :param parent: SessionNode
        :return: bool, return if removal successful
        """
        success = False
        self.beginRemoveRows(
            parent.index(), position,
            position + rows - 1)

        for row in range(rows):
            success = parent.removeChild(position)

        self.endRemoveRows()

        return success
