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
 
class FitNode(SessionNode):
    def __init__(self, name = 'Function', parent = None, handler = None):
        SessionNode.__init__(self, name, parent)
        self.description = ""
        self.descriptor = 'fit_node'
        self.handler = handler
        
    def data(self, column):
        if   column == 0: 
            return self._name
        elif column in range(1, 2*self.handler.func_dict[self._name][0].para_num+1): 
            if (column - 1) % 2 == 1:
                return self.handler.func_dict[self._name][0].para_name[int((column-2)/2)][0]
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def setData(self, column, value):
        pass
    
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled 
        else:
            return QtCore.Qt.NoItemFlags

class FunctionNode(SessionNode):
    def __init__(self, name = 'Function', parent = None):
        SessionNode.__init__(self, name, parent)
        self.description = ""
        self.descriptor = 'fit_function'

        self._plot_item = None
        self._plot_properties = None
        
    def data(self, column):
        if column == 0: 
            return self._name
        elif column in range(1, 2*self.parent().handler.func_dict[self.parent()._name][0].para_num+1): 
            idx = self.parent().handler.current_idx
            if (column - 1) % 2 == 0:
                return self.parent().handler.func_dict[
                    self.parent()._name][2][
                        self.parent()._children.index(self)][idx].para_fix[int((column-1)/2)]
            else:
                return self.parent().handler.func_dict[
                    self.parent()._name][2][
                        self.parent()._children.index(self)][idx].paras[int((column-2)/2)]
        else:
            return QtCore.QVariant()

    def setData(self, column, value):
        if column == 0: 
            return 
        elif column in range(1, 2*self.parent().handler.func_dict[self.parent()._name][0].para_num+1): 
            idx = self.parent().handler.current_idx
            if (column - 1) % 2 == 0:
                self.parent().handler.func_dict[
                    self.parent()._name][2][
                        self.parent()._children.index(self)][idx].para_fix[int((column-1)/2)] = value
            else: 
                self.parent().handler.func_dict[
                    self.parent()._name][2][
                        self.parent()._children.index(self)][idx].paras[int((column-2)/2)] = value
        else:
            return 
    
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        elif index.column() > 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.NoItemFlags

    def setPlotItem(self, canvas):
        '''
        Tell the item to set its plot item onto the convas
        '''
        self._plot_item = canvas.artist().addPlot(
            'Scatter',
            Name = self._name,
            Style = ['-'], 
            Log = [False,False]
        )
        canvas.artist().draw()

    def removePlotItem(self, canvas):
        '''
        Tell the item to remove itself from the canvas
        '''
        if not self._plot_item is None:
            canvas.artist().removePlot(self._plot_item)
            self._plot_item = None

    def refreshPlot(self, x):
        '''
        Tell the item to remove itself from the canvas
        '''
        if not self._plot_item is None:
            idx = self.parent().handler.current_idx
            self._plot_item.setData(
                x = x, 
                y = (
                    (self.parent().handler.func_dict['Baseline'][2][0][idx].returnData(x) if not 'Baseline' in self._name else x*0.)
                    + self.parent().handler.func_dict[
                        self.parent()._name][2][
                            self.parent()._children.index(self)][idx].returnData(x)))
