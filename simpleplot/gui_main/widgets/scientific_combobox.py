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

class ScientificComboBox(QtWidgets.QComboBox):
    '''

    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_modes = ['Float', 'Scientific', 'S.I.']
        self._current_mode  = 'Scientific'
        self.setModel(QtGui.QStandardItemModel())
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def addItem(self, display_value):
        '''
        This functionality should set the data
        '''
        item = ScientificComboBoxItem(display_value)
        self.model().insertRow(
            self.model().rowCount(),
            item)
        self.setModes()

    def addItems(self, data_value):
        '''
        This functionality should set the data
        '''
        for data in data_value:
            self.addItem(data)

    def currentData(self):
        return super().currentData(role=QtCore.Qt.UserRole)

    def setModes(self, mode = None):
        '''
        This functionality should set the data
        '''
        if not mode is None:
            self._current_mode = mode

        for i in range(self.model().rowCount()):
            self.model().item(i).setMode(self._current_mode)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.customContextMenuRequested(event.pos())
        else:
            return super().mousePressEvent(event)

    def customContextMenuRequested(self, pos):
        '''
        Implement the option dropdown
        '''
        temp_menu = QtWidgets.QMenu()

        menu_type = QtWidgets.QMenu("Type")
        action_list = []
        for action_name in self._allowed_modes:
            action = QtWidgets.QAction(action_name)
            action.triggered.connect(partial(self.setModes, action_name))
            action_list.append(action)
        menu_type.addActions(action_list)
        
        temp_menu.addMenu(menu_type)
        temp_menu.exec(self.mapToGlobal(pos))

class ScientificComboBoxItem(QtGui.QStandardItem):
    def __init__(self,value, *args, **kwargs):
        super().__init__(**kwargs)

        self._allowed_modes = ['Float', 'Scientific', 'S.I.']
        self._current_mode = 'S.I.'

        self._magnitude_positive = ['','k','M','G','T', 'P']
        self._magnitude_negative = ['','m','\u03BC','n','p', 'f']

        self._precision = 3
        self._value = value
        self._unit = ""

    def setMode(self, mode):
        '''
        set the appropriate mode
        '''
        self._current_mode = mode

    def getUnit(self):
        num = float(self._value)
        magnitude = 0
        if abs(num) < 1.:
            target = self._magnitude_negative
            factor = 1/1000.0
            while abs(num) <= factor:
                magnitude += 1
                num /= factor

        else:
            target = self._magnitude_positive
            factor = 1000.0
            while abs(num) >= factor:
                magnitude += 1
                num /= factor

        return num, target[magnitude]

    def data(self,role = QtCore.Qt.DisplayRole):
        '''
        Reimplement the display of data
        '''
        if role == QtCore.Qt.DisplayRole:
            if isinstance(self._value, str):
                return self._value+self._unit

            idx = self._allowed_modes.index(self._current_mode)
            if idx == 0:
                return str(self._value)+self._unit
            elif idx == 1:
                val, suffix =self.getUnit()
                return format(self._value, '.'+str(self._precision)+'e')+self._unit
            elif idx == 2:
                val, suffix =self.getUnit()
                return ("%."+str(self._precision)+"f%s")%(val, suffix)+self._unit
        elif role == QtCore.Qt.UserRole:
            return self._value
        else:
            return super().data(role)

    def setItemData(self,value, role = QtCore.Qt.DisplayRole):
        '''
        Reimplement the display of data
        '''
        if role == QtCore.Qt.DisplayRole:
            self._value = value

        else:
            return super().setItemData(role)
            