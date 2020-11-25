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
from typing import Union

import json
import os

from PyQt5 import QtGui, QtCore


class SessionNode(QtGui.QStandardItem):
    """
    This class inherits the StandardItem of Qt to create a custom python
    model view system.
    """

    def __init__(self, name: str, parent: SessionNode = None):
        super().__init__(parent)

        self._name = name
        self._value = None
        self._children = []
        self._parent = parent
        self._model = None

        if parent is not None:
            parent.addChild(self)

    def referenceModel(self, model) -> None:
        """
        This function is used to propagate the model pointer
        within the items. This allows then a quick access
        :param model: SessionModel
        :return: None
        """
        self._model = model
        for child in self._children:
            child.referenceModel(self._model)

    def model(self):
        """
        Return the referenced model
        :return: SessionModel
        """
        return self._model

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def addChild(self, child: SessionNode) -> None:
        """
        Adds an element to the children list and sets self as a parent
        :param child: SessionNode type item
        :return: None
        """
        self._children.append(child)
        child._parent = self
        child._model = self.model()

    def insertChild(self, position: int, child: SessionNode) -> bool:
        """
        Inserts a child at a particular position
        :param position: int, future position of the item
        :param child: SessionNode type item
        :return: bool, success or failure of the insert
        """
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        child._model = self.model()

        return True

    def removeChild(self, position: int) -> bool:
        """
        Removes the item at given position
        :param position: int, position to remove
        :return: bool, success or failure of the removal
        """
        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None
        child._model = None

        return True

    def children(self) -> list:
        """
        Retrieve the children of the current node
        :return: list(SessionNode)
        """
        return self._children

    def childFromName(self, name: str) -> Union[SessionNode, None]:
        """
        Get the child item corresponding to a name
        :param name: str, name of the item
        :return: SessionNode, item
        """
        for child in self._children:
            if name == child.name:
                return child
        return None

    # noinspection PyMethodOverriding
    def child(self, row: int) -> Union[SessionNode, None]:
        """
        Return the child at a given row
        :param row: the row at which to look
        :return: SessionNode item
        """
        if row >= self.childCount():
            return None
        return self._children[row]

    def childCount(self) -> int:
        """
        Return the amount of children present
        :return: int amount of children
        """
        return len(self._children)

    def parent(self) -> SessionNode:
        """
        Returns the parent of the current item
        :return: SessionNode
        """
        return self._parent

    def row(self) -> int:
        """
        Returns the row of the current item
        :return: int
        """
        if self.parent() is not None:
            return self._parent.children().index(self)

    # noinspection PyMethodOverriding
    def data(self, column):

        if column == 0:
            return self._name
        # elif column is 1: return self.typeInfo()

    # noinspection PyMethodOverriding
    def setData(self, column, value):
        if column is 0:
            self._name = value.toPyObject()
        elif column is 1:
            self._value = value

    # noinspection PyMethodOverriding
    def flags(self, index):
        """
        This will set the flags for an Item
        :return:
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable  # | QtCore.Qt.ItemIsEditable

    def setString(self):
        pass

    def resource(self):
        return None

    def index(self):
        if not self.row() is None:
            return self._model.createIndex(self.row(), 0, self)
        else:
            return QtCore.QModelIndex()

    def save(self):
        """
        returns the formatted dictionary with the children
        """
        output = {}
        for child in self._children:
            output[child.name] = child.save()

        return output

    def saveToFile(self, path):
        """
        saves the tree to a json format
        """
        output = self.save()
        with open(path, 'w') as f:
            json.dump(output, f)
        os.chmod(path, 0o777)

    def load(self, input_dict):
        """
        reads the input dictionary
        """
        for child in self._children:
            if child.name in input_dict.keys():
                child.load(input_dict[child.name])

    def loadFromFile(self, path):
        """
        saves the tree to a json format
        """
        with open(path, 'r') as f:
            input_dict = json.load(f)
        self.load(input_dict)
