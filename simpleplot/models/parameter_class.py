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
import numpy as np

from .session_node import SessionNode
from .parameter_node import ParameterNode
from .parameter_node import ParameterItem

from .widget_constructors import spinBoxConstructor
from .widget_constructors import doubleSpinBoxConstructor
from .widget_constructors import lineEditConstructor
from .widget_constructors import comboBoxConstructor
from .widget_constructors import colorWidgetConstructor
from .widget_constructors import fontWidgetConstructor
from .widget_constructors import checkBoxConstructor
from .widget_constructors import gradientConstructor 

from ..simpleplot_widgets.SimplePlotGradientEditorItem import GradientEditorItem

class ParameterHandler(SessionNode):
    '''
    The need for type management of parameters and 
    other things asks for a class object rather 
    then storing the data inside of lists.
    This allows also to implement more complex schemes
    '''
    
    def __init__(self, name = 'No Name',  parent = None): 
        super().__init__(name = name, parent = parent)
        self.items = {}
        self._tags = None

    def __getitem__(self, key):
        '''
        the classical getitem classmethod
        overloaded to provide simple setting 
        methodology

        Parameters:
        - - - - - - - - - - - 
        key : string
            The name of the node we are trying to set
        '''
        if key in self.items.keys():
            return self.items[key].getValue()

    def __setitem__(self, key, value):
        '''
        the classical getitem classmethod
        overloaded to provide simple setting 
        methodology

        Parameters:
        - - - - - - - - - - - 
        key : string
            The name of the node we are trying to set

        value : Either value or list of different types
            This will be set a the value of the item through setData

        '''
        if key in self.items.keys():
            self.items[key].updateValue(value)

        else:
            print('Parameter '+key+' does not exist')

    def addParameter(self, key, value, **kwargs):
        '''
        This method is what initialises an item and then 
        puts it into the item list for secondary safekeeping

        Parameters:
        - - - - - - - - - - - 
        name : string
            The name of the node

        value : Either value or list of different types
            This will be set a the value of the item through setData

        kwargs : dictionary of parameters
            This will tell the item how to proceed

        Returns:
        - - - - - - - - - - - 
        ParameterVector or ParameterValue : python item node
        '''
        if not key in self.items.keys():
            self.items[key] = self.creator(key, value, **kwargs)
        else:
            print('parameter '+key+' already exists')

        self.freezOrder()

    def creator(self, name, value, **kwargs):
        '''
        This method will go through the type of the
        object and then decide the nested objects
        to create

        Parameters:
        - - - - - - - - - - - 
        name : string
            The name of the node

        value : Either value or list of different types
            This will be set a the value of the item through setData

        kwargs : dictionary of parameters
            This will tell the item how to proceed

        Returns:
        - - - - - - - - - - - 
        ParameterVector or ParameterValue : python item node
        '''
        if isinstance(value, collections.abc.Sequence) and not isinstance(value, str):
            return ParameterVector(name, value, self,**kwargs)
        else:
            return ParameterValue(name, value, self,**kwargs)

    def setString(self):
        pass

    def freezOrder(self):
        '''
        Thhis allows the user to save the current order of the
        items to allow the management of the tags. Items will be 
        built and inserted by order.
        '''
        self._order = []
        for child in self._children:
            if child._name in self.items.keys():
                self._order.append(child._name )

    def setCurrentTags(self, tags):
        '''
        This will allow the user to manage what is currently displayed. 
        If the tasg is None all items will be displayed.

        Parameters:
        - - - - - - - - - - - 
        tags : list of strings or None
            The tags that will then be applied
        '''
        self._tags = tags

        present = [child._name for child in self._children]
        for name in self._order:
            if name in present:
                self._model.removeRows(self.items[name].index().row(), 1, self)

        for name in self._order:
            if any([tag in self._tags for tag in self.items[name].getTags()]) or self._tags is None:
                self._model.insertRows(len(self._children),1,[self.items[name]], self)

        self._model.dataChanged.emit(self.index(), self.index())

    def runAll(self):
        '''
        Run all methods in the class
        '''
        for key in self.items.keys():
            if 'method' in self.items[key].kwargs.keys():
                self.items[key].kwargs['method']()

    def save(self):
        '''
        This will generate a dictionary of values that will
        be returned to the method asking for it. Note that this
        dictionary can be read by the load functions. 
        '''
        output = {}
        for key in self.items.keys():
            output[key] = self.items[key].getSaveFormated()
        return output

    def load(self, input_dict):
        '''
        This function allows the loading of previously 
        saved items. and the respective values

        Parameters:
        - - - - - - - - - - - 
        value_dict : dict of values to set in the items
            The dictionary should be formated in a way that the 
            different values can be set in the items. Note that for 
            special items such as gradients special loaders will be written
            within the itmes. 
        '''
        for key in self.items.keys():
            if key in input_dict.keys():
                self.items[key].load(input_dict[key])
        self.runAll()

class ParameterMaster:
    '''
    This class is meant to be inherited and 
    will simply own the common sorting and
    managing options.
    '''
    def __init__(self, name, parent, **kwargs):
        self._base_name  = name
        self._name       = None
        self._parent     = parent
        self._active     = True
        self._value      = None
        self._live       = True
        self._tags       = []
        if 'tags' in kwargs.keys():
            self._tags = kwargs['tags']
    
    def getTags(self):
        '''
        getter for the tags

        Returns:
        - - - - - - - - - - - 
        tags : list of strings
            the current item tags
        '''
        return self._tags

    def getValue(self):
        '''
        returns the value of the current object
        '''
        return self._value

    def getLive(self):
        '''
        return if an item is live
        '''
        return self._live
        
    def getFormated(self,name, value):
        '''

        '''
        if type(value) == int or isinstance(value, np.integer):
            return [name, 'int', value]
        elif type(value) == float or isinstance(value, np.floating):
            return [name, 'float', value]
        elif type(value) == str:
            return [name, 'str', value]
        elif type(value) == QtGui.QColor:
            return [name, 'color', value.getRgb()]
        elif type(value) == QtGui.QFont:
            return [name, 'font', value.styleName()]
        elif type(value) == bool:
            return [name, 'bool', value]
        elif type(value) == GradientEditorItem:
            return [name, 'gradient', value.saveState]

    def getValueFormat(self, value_array):
        '''

        '''
        if value_array[1] == 'int':
            return value_array[2]
        elif value_array[1] == 'float':
            return value_array[2]
        elif value_array[1] == 'str':
            return value_array[2]
        elif value_array[1] == 'color':
            return QtGui.QColor(*value_array[2])
        elif value_array[1] == 'font':
            return QtGui.QFont(value_array[2])
        elif value_array[1] == 'bool':
            return value_array[2]
        elif value_array[1] == 'gradient':
            item = GradientEditorItem()
            item.restoreState(value_array[2])
            return item

class ParameterVector(ParameterMaster, ParameterNode):
    def __init__(self, name, values, parent, **kwargs):
        '''
        This is the parameter class for 
        a vector of values and should spawn
        into a node

        Parameters:
        - - - - - - - - - - - 
        name : string
            The name of the node

        value : Either value or list of different types
            This will be set a the value of the item through setData

        parent : parent SessionNode class
            This will be initialised as the parent in the model

        kwargs : dictionary of parameters
            This will tell the item how to proceed
        '''
        ParameterMaster.__init__(self, name, parent, **kwargs)
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

    def updateValue(self, value, method = True):
        '''
        The values here will be set manually
        '''
        for i, element in enumerate(self._vector_elements):
            element.updateValue(value[i], method = False)

        if 'method' in self.kwargs.keys() and method:
            self.kwargs['method']()

    def getSaveFormated(self):
        '''
        return the current value but as 
        a comprehensive string in case the value is 
        a gradient or a color for example

        Returns:
        - - - - - - - - - - - 
        output : list of elements 
        '''
        output = {}

        for element in self._vector_elements:
            output[element._name] = element.getFormated(element._name, element.getValue())
        
        return output

    def load(self, value_dict):
        '''
        This is the load routine
        '''
        for element in self._vector_elements:
            if element._name in value_dict.keys():
                element.load(value_dict[element._name])

class ParameterValue(ParameterMaster, ParameterItem):
    def __init__(self, name, value, parent, **kwargs): 
        '''
        This is the parameter class for 
        a vector of values and should spawn
        into a node

        Parameters:
        - - - - - - - - - - - 
        name : string
            The name of the node

        value : Either value or list of different types
            This will be set a the value of the item through setData

        parent : parent SessionNode class
            This will be initialized as the parent in the model

        kwargs : dictionary of parameters
            This will tell the item how to proceed
        '''
        ParameterMaster.__init__(self, name, parent, **kwargs)
        ParameterItem.__init__(self, name, parent, value, None)
        self.kwargs = kwargs
        
        if type(value) == int or isinstance(value, np.integer):
            self._constructor = spinBoxConstructor(self)
            self._value = int(self._value)
        elif type(value) == float or isinstance(value, np.floating):
            self._constructor = doubleSpinBoxConstructor(self)
            self._value = float(self._value)
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
        elif type(value) == GradientEditorItem:
            self._constructor = gradientConstructor(self)

    def createWidget(self, parent, index):
        '''
        The create widget call will create the widget
        for the delegate system of the view

        Parameters:
        - - - - - - - - - - - 
        parent : QWidget
            The widget parent

        index : QModelIndex
            The index of the call
        '''
        return self._constructor.create(parent,index =  index)

    def setEditorData(self, editor, index):
        '''
        Set the data of the editor. This method is
        propagated to our _contructor loaded with the
        approriate widget

        Parameters:
        - - - - - - - - - - - 
        editor : QWidget
            The editor widget
        '''
        self._constructor.setEditorData(editor)

    def retrieveData(self, editor, index):
        '''
        Get the data of the editor. This method is
        propagated to our constructor loaded with the
        appropriate widget

        Parameters:
        - - - - - - - - - - - 
        editor : QWidget
            The editor widget
        '''
        if 'method' in self.kwargs.keys():
            self.kwargs['method']()
        return self._constructor.retrieveData(editor)

    def updateValue(self,value,method = True):
        '''
        Update the value of the item manually and 
        decide wether to call or not the method 
        associated to it

        Parameters:
        - - - - - - - - - - - 
        value : Either value or list of different types
            This will be set a the value of the item through setData

        method : bool
            Do th emethod linke dto this object
        '''
        self._value = value
        if hasattr(self.parent(),'setString'):
            self.parent().setString()
        self._model.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex())

        if 'method' in self.kwargs.keys() and method:
            self.kwargs['method']()

    def getSaveFormated(self):
        '''
        return the current value but as 
        a comprehensive string in case the value is 
        a gradient or a color for example

        Returns:
        - - - - - - - - - - - 
        output : list of elements 
        '''
        return self.getFormated(self._name, self.getValue())

    def load(self,value_array):
        '''
        This is the load routine
        '''
        self.updateValue(
            self.getValueFormat(value_array),
            method=False)
