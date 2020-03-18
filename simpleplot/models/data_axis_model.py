'''
Created on 3 maj 2011

@author: Yasin
'''

from PyQt5 import QtCore, QtGui, QtWidgets

from .modal_items import QColorDialog, QFontDialog
from .session_node import SessionNode

class DataAxisModel(QtCore.QAbstractTableModel):
    '''
    This model was created to allow support of the 
    complexity of the multiCanvasItem. it allows a 
    treeview approach of the 
    '''
    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    
    """INPUTS: Node, QObject"""
    def __init__(self, parent=None, col_count = 3):
        super(DataAxisModel, self).__init__(parent)
        self._root_item     = SessionNode("root")
        self._col_count     = col_count
        self.referenceModel()

    def referenceModel(self):
        self._root_item.referenceModel(self)

    def root(self):
        return self._root_item

    def rowCount(self, parent):
        return self._root_item.childCount()

    def columnCount(self, parent):
        return self._col_count
    
    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = self._root_item.child(index.row())

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())
 
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
            
        if role == DataAxisModel.sortRole:
            return node.typeInfo()

        if role == DataAxisModel.filterRole:
            return node.typeInfo()

        if role == QtCore.Qt.BackgroundRole:
            if type(node.data(index.column())) == QtGui.QColor:
                return QtGui.QBrush(node.data(index.column()))

        if role == QtCore.Qt.FontRole:
            if type(node.data(index.column())) == QtGui.QFont:
                return node.data(index.column())

    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):
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
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "Name"
                elif section == 1:
                    return "Value"
                elif section == 2:
                    return "Unit"
                else:
                    return None

    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        item = self.getNode(index)
        return item.flags(index)

    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):
        child_item = self._root_item.child(row)
        if child_item:
            return self.createIndex(row, column, self._root_item)
        else:
            return QtCore.QModelIndex()

    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index): 
        return self._root_item.child(index.row())

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


