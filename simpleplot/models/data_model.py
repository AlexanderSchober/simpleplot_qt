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

from .modal_items import QColorDialog, QFontDialog
from .session_node import SessionNode
import numpy as np

class DataModel(QtCore.QAbstractTableModel):
    '''
    This model was created to allow support of the 
    complexity of the multiCanvasItem. it allows a 
    treeview approach of the 
    '''
    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    
    def __init__(self, data_pointer, parent=None, col_count = 3):
        super(DataModel, self).__init__(parent)

        self._data_pointer = data_pointer
        self._data_index = []
        self._row_count = 0
        self._col_count = 0

    def rowCount(self, parent):
        '''
        Override the definition from the 
        superclass
        '''
        return self._row_count

    def columnCount(self, parent):
        '''
        Override the definition from the 
        superclass
        '''
        return self._col_count

    def setDataIndex(self, index:list):
        '''
        Grab this index as it will point towards the 
        data that has to be displayed in the current
        data pointer element.
        '''
        self.beginResetModel()
        self._data_index = list(index)
        self._data_object_data = self._data_pointer[self._data_index]
        if len(self._data_object_data.shape) == 1:
            self._col_count = 1
            self._row_count = self._data_object_data.shape[0]
        elif len(self._data_object_data.shape) == 2:
            self._col_count = self._data_object_data.shape[1]
            self._row_count = self._data_object_data.shape[0]

        self._data_object_pointer = self._data_pointer.DataObjects[
            self._data_pointer.axes.get_id_for_index(self._data_index)[0]]
        
        self.endResetModel()
    
    def data(self, index:QtCore.QModelIndex, role:QtCore.Qt.UserRole)->QtCore.QVariant:
        '''
        Override the definition from the 
        superclass
        '''
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.grabData(index)
 
        # if role == QtCore.Qt.DecorationRole:
        #     if index.column() == 0:
        #         resource = node.resource()
        #         return QtGui.QIcon(QtGui.QPixmap(resource))
            
        # if role == DataModel.sortRole:
        #     return node.typeInfo()

        # if role == DataModel.filterRole:
        #     return node.typeInfo()

        # if role == QtCore.Qt.BackgroundRole:
        #     if type(node.data(index.column())) == QtGui.QColor:
        #         return QtGui.QBrush(node.data(index.column()))

        # if role == QtCore.Qt.FontRole:
        #     if type(node.data(index.column())) == QtGui.QFont:
        #         return node.data(index.column())

    def grabData(self, index:QtCore.QModelIndex)->QtCore.QVariant:
        '''
        grab the data under the current index for the 
        display
        '''
        if len(self._data_object_data.shape) == 1:
            return QtCore.QVariant(
                float(self._data_object_data[index.row()]))
            
        elif len(self._data_object_data.shape) == 2:
            return QtCore.QVariant(
                float(self._data_object_data[index.row(), index.column()]))

    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        '''
        '''
        if index.isValid():
            node = self._root_item.child(index.row())
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True
            
        return False
    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        '''
        '''
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal and not type(self._data_object_pointer.axes) == type(None):
                if len(self._data_object_data.shape) == 1:
                    if section == 0:
                        return "values"

                elif len(self._data_object_data.shape) == 2:
                    if isinstance(self._data_object_pointer.axes[1], list):    
                        return self._data_object_pointer.axes[1][section]
                    elif isinstance(self._data_object_pointer.axes[1], (np.ndarray, np.generic)):
                        return float(self._data_object_pointer.axes[1][section])
                    else:
                        return section 

            elif orientation == QtCore.Qt.Vertical and not type(self._data_object_pointer.axes) == type(None):
                if len(self._data_object_data.shape) == 1:
                    if isinstance(self._data_object_pointer.axes, list):    
                        return self._data_object_pointer.axes[section]
                    elif isinstance(self._data_object_pointer.axes, (np.ndarray, np.generic)):
                        return float(self._data_object_pointer.axes[section])
                    else:
                        return section

                elif len(self._data_object_data.shape) == 2:
                    if isinstance(self._data_object_pointer.axes[0], list):    
                        return self._data_object_pointer.axes[0][section]
                    elif isinstance(self._data_object_pointer.axes[0], (np.ndarray, np.generic)):
                        return float(self._data_object_pointer.axes[0][section])
                    else:
                        return section                   

    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):
        return self.createIndex(row, column)

    def itemAt(self,index):
        '''
        returns the ite, associated to the model index
        '''
        if not index.parent().internalPointer() is None:
            return index.parent().internalPointer().child(index.row())
        else:
            return None

    """INPUTS: int, int, QModelIndex"""
    def insertRows(self, position, rows, items):
        success = False
        self.beginInsertRows(
            self._root_item.index(), 
            position, 
            position + rows - 1)
        
        for row in range(rows):
            items[row].referenceModel(self)
            success = self._root_item.insertChild(position, items[row])
        
        self.endInsertRows()
        self.referenceModel()

        return success

    # """INPUTS: int, int, QModelIndex"""
    def removeRows(self, position, rows):
        success = False
        self.beginRemoveRows(
            self._root_item.index(), 
            position, 
            position + rows - 1)
        
        for row in range(rows):
            success = self._root_item.removeChild(position)
            
        self.endRemoveRows()
        
        return success


