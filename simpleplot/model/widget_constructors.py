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

from PyQt5 import QtCore, QtGui, QtWidgets


class spinBoxConstructor:

    def __init__(self, parent = None): 
        self.manager = parent

    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        item = QtWidgets.QSpinBox(parent)
        
        if 'min' in self.manager.kwargs.keys():
            item.setMinimum(self.manager.kwargs['min'])
        else:
            item.setMinimum(-1000)
        if 'max' in self.manager.kwargs.keys():
            item.setMaximum(self.manager.kwargs['max'])
        else:
            item.setMaximum(1000)

        item.valueChanged.connect(self.updateInternals)
        return item

    def updateInternals(self, value):
        '''
        '''
        self.manager._value = value
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def setEditorData(self, editor):
        editor.setValue(self.manager._value)

    def retrieveData(self, editor):
        return editor.value()

class doubleSpinBoxConstructor:

    def __init__(self, parent = None): 
        self.manager = parent

    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        item = QtWidgets.QDoubleSpinBox(parent)

        if 'min' in self.manager.kwargs.keys():
            item.setMinimum(self.manager.kwargs['min'])
        else:
            item.setMinimum(-1000)
        if 'max' in self.manager.kwargs.keys():
            item.setMaximum(self.manager.kwargs['max'])
        else:
            item.setMaximum(1000)

        item.valueChanged.connect(self.updateInternals)
        return item

    def updateInternals(self, value):
        '''
        '''
        self.manager._value = value
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def setEditorData(self, editor):
        editor.setValue(self.manager._value)

    def retrieveData(self, editor):
        return editor.value()

class lineEditConstructor:

    def __init__(self, parent = None): 
        self.manager = parent

    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        item = QtWidgets.QLineEdit(parent)
        item.textChanged.connect(self.updateInternals)
        return item

    def updateInternals(self, value):
        '''
        '''
        self.manager._value = value
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def setEditorData(self, editor):
        editor.setText(self.manager._value)

    def retrieveData(self, editor):
        return editor.text()

class checkBoxConstructor:

    def __init__(self, parent = None): 
        self.manager = parent

    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        self._item = QtWidgets.QCheckBox(parent)
        self._item.stateChanged.connect(self.updateInternals)
        return self._item

    def updateInternals(self, value):
        '''
        '''
        self.manager._value = self._item.isChecked()
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def setEditorData(self, editor):
        editor.setChecked(self.manager._value)

    def retrieveData(self, editor):
        return editor.isChecked()

class comboBoxConstructor:

    def __init__(self, parent = None): 
        self.manager = parent

    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.manager.kwargs['choices'])
        
        return editor

    def updateInternals(self, value):
        '''
        '''
        self.manager._value = value
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def setEditorData(self, editor):
        editor.setCurrentIndex(
            self.manager.kwargs['choices'].index(self.manager._value))
        editor.currentTextChanged.connect(self.updateInternals)

    def retrieveData(self, editor):
        return editor.currentText()

class colorWidgetConstructor:

    def __init__(self, parent = None): 
        self.manager = parent
        
    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        item = QtWidgets.QWidget(parent)
        self.colorChoice()
        return item

    def setEditorData(self,editor):
        self.manager._model.color_picker.setCurrentColor(self.manager._value)

    def colorChoice(self):
        self.manager._model.color_picker.disconnectAll()
        self.manager._model.color_picker.show()
        self.manager._model.color_picker.connectMethod(self.updateInternals)

    def updateInternals(self, color):
        self.manager._value = color
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def retrieveData(self, editor):
        return self.manager._model.color_picker.currentColor()

class fontWidgetConstructor:
    '''
    '''
    def __init__(self, parent = None): 
        self.manager = parent
        
    def create(self,parent, value = None, index = None):
        self._index = QtCore.QModelIndex(index)
        item = QtWidgets.QWidget(parent)
        self.fontChoice()
        return item

    def setEditorData(self,editor):
        self.manager._model.font_picker.setCurrentFont(self.manager._value)

    def fontChoice(self):
        self.manager._model.font_picker.disconnectAll()
        self.manager._model.font_picker.show()
        self.manager._model.font_picker.connectMethod(self.updateInternals)

    def updateInternals(self, font):
        '''
        '''
        self.manager._value = font
        self.manager._model.dataChanged.emit(
            self._index,
            self._index)

        if 'method' in self.manager.kwargs.keys():
            self.manager.kwargs['method']()

        self.manager.parent().setString()

    def retrieveData(self, editor):
        '''
        '''
        return self.manager._model.font_picker.currentFont()

