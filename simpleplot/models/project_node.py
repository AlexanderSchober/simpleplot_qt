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

from .session_node import SessionNode
from PyQt5 import QtWidgets, QtGui, QtCore

from ..core.data.data_structure import DataStructure
from ..core.data.data_injector import DataInjector

from ..canvas.multi_canvas import MultiCanvasItem
from ..gui_main.gui_subwindows.subwindow_data.data_widget import DataWidget
 
class ProjectNode(SessionNode):
    def __init__(self, name = 'New Project', parent = None, parameters = {}, method = None):
        SessionNode.__init__(self, name, parent)
        self.description = ""
        self.descriptor = 'project'
        
        self.addChild(DatasetsNode())
        self.addChild(AnalysisNode())
        self.addChild(PlotNode())
 
    def data(self, column):
        if   column is 0: return self._name
        elif column is 1: return self.description

    def setData(self, column, value):
        pass
    
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled 
        elif index.column() == 1:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.NoItemFlags

class DatasetsNode(SessionNode):
    def __init__(self, name = 'Datasets', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "data"
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def addDataItem(self):
        temp = DataItem(name = 'Dataset ' + str(self.childCount()))
        self.model().insertRows(self.childCount(), 1, [temp], self)
        return temp

class DataItem(SessionNode):
    def __init__(self, name = 'Dataset', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "data item"
        self.data_item = DataStructure()
        self.data_widget = DataWidget(self.data_item)
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        if  column is 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column is 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

class DataLinkItem(SessionNode):
    def __init__(self, name = 'Data link', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "data link item"
        self.data_injector = DataInjector()
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        if  column is 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column is 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

class AnalysisNode(SessionNode):
    def __init__(self, name = 'Analysis', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "analysis"
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

class PlotNode(SessionNode):
    def __init__(self, name = 'Plots', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "plot"
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

class PlotItem(SessionNode):
    def __init__(self, name = 'Plot', parent = None, **kwargs):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "plot item"
        self.canvas_widget = QtWidgets.QWidget()
        self.canvas_item = MultiCanvasItem(widget=self.canvas_widget, **kwargs)

        self._window = None
 
    def data(self, column):
        if column is 0: return self._name
 
    def setData(self, column, value):
        if  column is 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column is 0: return QtCore.Qt.ItemIsEnabled

        else: return QtCore.Qt.ItemIsEnabled
