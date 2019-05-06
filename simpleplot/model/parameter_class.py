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

import collections.abc

from .parameter_node import ParameterNode
from .parameter_node import ParameterItem

from .widget_constructors import spinBoxConstructor
from .widget_constructors import doubleSpinBoxConstructor
from .widget_constructors import lineEditConstructor
from .widget_constructors import comboBoxConstructor
from .widget_constructors import colorWidgetConstructor
from .widget_constructors import fontWidgetConstructor
from .widget_constructors import checkBoxConstructor

class ParameterHandler(ParameterNode):
    '''
    The need for type management of parameters and 
    other things asks for a class object rather 
    then storing the data inside of lists.
    This allows also to implement more complex schemes
    '''
    
    def __init__(self, name = 'No Name',  parent = None): 
        super().__init__(name = name, parent = parent)
        self.items = {}

    def __getitem__(self, key):
        '''
        the classical getitem classmethod
        overloaded to provide simple setting 
        methodology
        '''
        if key in self.items.keys():
            return self.items[key].getValue()

    def __setitem__(self, key, value):
        '''
        the classical getitem classmethod
        overloaded to provide simple geting 
        methodology
        '''
        if key in self.items.keys():
            self.items[key].updateValue(value)

        else:
            print('Parameter '+key+' does not exist')

    def addParameter(self, key, value, **kwargs):
        '''

        '''
        if not key in self.items.keys():
            self.items[key] = self.creator(key, value, **kwargs)
        else:
            print('parameter '+key+' already exists')

    def creator(self, name, value,**kwargs):
        '''
        This method will go through the type of the
        object and then decide the nested objects
        to create
        '''
        if isinstance(value, collections.abc.Sequence) and not isinstance(value, str):
            return ParameterVector(name, value, self,**kwargs)
        else:
            return ParameterValue(name, value, self,**kwargs)

    def setString(self):
        pass

class ParameterMaster:
    '''
    This class is meant to be inherited and 
    will simply own the common sorting and
    managing options.
    '''
    def __init__(self, name, parent):
        self._base_name  = name
        self._parent     = parent
        self._active     = True
        self._value      = None

    def getValue(self):
        '''
        returns the value of the current object
        '''
        return self._value
    
class ParameterVector(ParameterMaster, ParameterNode):
    '''
    This is the parameter class for 
    a vector of values and should spawn
    into a node
    '''
    def __init__(self, name, values, parent, **kwargs):
        ParameterMaster.__init__(self, name, parent)
        ParameterNode.__init__(self, name, parent)
        self.kwargs = kwargs
        self.initialise(values)

    def initialise(self, values):
        '''
        check that each item in a vector has the
        same type. This is important as we will
        call a common delegate
        '''
        if 'names' in self.kwargs.keys():
            self._vector_elements = []
            for i, value in enumerate(values):
                self._vector_elements.append(
                    ParameterValue(self.kwargs['names'][i], value, self, **self.kwargs))
        else:
            self._vector_elements = []
            for i, value in enumerate(values):
                self._vector_elements.append(
                    ParameterValue(str(i), value, self, **self.kwargs))

        self.setString(notify=False)

    def setString(self, notify = True ):

        values = self.getValue()
        string = '('
        for i,value in enumerate(values):
            if 'names' in self.kwargs.keys():
                string+= ' '+self.kwargs['names'][i]+': '
            if type(value) == QtGui.QColor:
                string+= str(value.name())+','
            elif type(value) == QtGui.QFont:
                string+= str(value.family())+','
            else:
                string+= str(value)+','

        string = string[:-1] +' )'
        self.description = string

        if notify:
            self._model.dataChanged.emit(self.index(),self.index())

    def getValue(self):
        '''
        returns the value of the current object
        '''
        return [item.getValue() for item in self._vector_elements]

    def updateValue(self, value):
        '''
        The values here will be set manually
        '''
        for i, element in enumerate(self._vector_elements):
            element.updateValue(value[i])

class ParameterValue(ParameterMaster, ParameterItem):
    '''
    This is the parameter class for 
    a single value that should obviously 
    not spawn into a node
    '''
    def __init__(self, name, value, parent, **kwargs): 
        ParameterMaster.__init__(self, name, parent)
        ParameterItem.__init__(self, name, parent, value, None)
        self.kwargs = kwargs

        if type(value) == int:
            self._constructor = spinBoxConstructor(self)
        elif type(value) == float:
            self._constructor = doubleSpinBoxConstructor(self)
        elif type(value) == str:
            if not 'choices' in kwargs.keys():
                self._constructor = lineEditConstructor(self)
            else:
                self._constructor = comboBoxConstructor(self)
        elif type(value) == QtGui.QColor:
            self._constructor = colorWidgetConstructor(self)
        elif type(value) == QtGui.QFont:
            self._constructor = fontWidgetConstructor(self)
        elif type(value) == bool:
            self._constructor = checkBoxConstructor(self)

    def createWidget(self, parent, index):
        '''
        create the widget for the delegate
        '''
        return self._constructor.create(parent,index =  index)

    def setEditorData(self, editor):
        '''
        set the data of the editor
        '''
        self._constructor.setEditorData(editor)

    def retrieveData(self, editor):
        '''
        set the data of the editor
        '''
        if 'method' in self.kwargs.keys():
            self.kwargs['method']()
        return self._constructor.retrieveData(editor)

    def updateValue(self, value):
        '''
        The values here will be set manually
        '''
        self._value = value
        self.parent().setString()
        self._model.dataChanged.emit(self.index(),self.index())
        if 'method' in self.kwargs.keys():
            self.kwargs['method']()
       


