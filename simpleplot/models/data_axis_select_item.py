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
from .session_node import SessionNode

from .widget_constructors import comboBoxConstructor

class DataAxisItem(SessionNode):
    '''
    '''
    def __init__(self, name, unit, choices, axis_value, axis_choices, parent = None):
        super(DataAxisItem, self).__init__(name, parent)

        self._value = None
        
        self.kwargs = {}
        self.kwargs['name'] = name
        self.kwargs['value'] = str(choices[0])
        self.kwargs['choices'] = [str(e) for e in choices]
        self.kwargs['axis_value'] = 'None'
        self.kwargs['axis_choices'] = ['None']

        self._constructor_choice = comboBoxConstructor(
            self, keyword = 'value', choice_keyword = 'choices')
        self._constructor_axis = comboBoxConstructor(
            self, keyword = 'axis_value', choice_keyword = 'axis_choices')
        
    def data(self, column):
        '''
        '''
        if column == 0:
            return self.kwargs['name']
        if column == 1:
            return self.kwargs['value']
        if column == 2:
            return self.kwargs['axis_value']
        if column == 3:
            return self.kwargs['unit']

    def setData(self, column, value):
        '''
        '''
        if column == 0:
            self.kwargs['name'] = value
        if column == 1:
            self.kwargs['value'] = value
        if column == 1:
            self.kwargs['axis_value'] = value
        if column == 3:
            self.kwargs['unit'] = value

    def flags(self, index):
        '''
        '''
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsEnabled
        elif column == 1:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        elif column == 2:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        elif column == 3:
            return QtCore.Qt.ItemIsEnabled

    def createWidget(self, parent, index):
        '''
        '''
        if index.column() == 1:
            return self._constructor_choice.create(
                parent,index = index)
        if index.column() == 2:
            return self._constructor_axis.create(
                parent,index = index)

    def setEditorData(self, editor, index):
        '''
        '''
        if index.column() == 1:
            self._constructor_choice.setEditorData(editor)
        if index.column() == 2:
            self._constructor_axis.setEditorData(editor)

    def retrieveData(self, editor, index):
        '''
        '''
        if index.column() == 1:
            return self._constructor_choice.retrieveData(editor)
        if index.column() == 2:
            return self._constructor_axis.retrieveData(editor)
