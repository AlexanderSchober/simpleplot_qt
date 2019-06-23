'''
Created on 3 maj 2011

@author: Yasin
'''

from PyQt5 import QtCore, QtGui, QtWidgets

from .modal_items import QColorDialog, QFontDialog

class SessionModel(QtCore.QAbstractItemModel):
    '''
    This model was created to allow support of the 
    complexity of the multiCanvasItem. it allows a 
    treeview approach of the 
    '''
    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    
    """INPUTS: Node, QObject"""
    def __init__(self, root, parent=None, col_count = 2):
        super(SessionModel, self).__init__(parent)
        self._rootNode = root
        self._col_count = col_count
        self.color_picker = QColorDialog()
        self.font_picker = QFontDialog()
        self.referenceModel()

    def referenceModel(self):
        self._rootNode.referenceModel(self)

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def columnCount(self, parent):
        return self._col_count
    
    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())
 
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
            
        if role == SessionModel.sortRole:
            return node.typeInfo()

        if role == SessionModel.filterRole:
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
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True
            
        return False
    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Properties"
            else:
                return "Values"

    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        item = self.getNode(index)
        return item.flags(index)

    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""
    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        
        if parentNode == self._rootNode or parentNode == None or parentNode.row() == None:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        node = index.internalPointer()
        if node:
            return node
            
        return self._rootNode

    def itemAt(self,index):
        '''
        returns the ite, associated to the model index
        '''
        if not index.parent().internalPointer() is None:
            return index.parent().internalPointer().child(index.row())
        else:
            return None

    """INPUTS: int, int, QModelIndex"""
    def insertRows(self, position, rows, items, parentNode):

        success = False
        self.beginInsertRows(
            parentNode.index(), position, 
            position + rows - 1)
        
        for row in range(rows):
            items[row].referenceModel(self)
            success = parentNode.insertChild(position, items[row])
        
        self.endInsertRows()

        return success
    

    # """INPUTS: int, int, QModelIndex"""
    def removeRows(self, position, rows, parentNode):
        success = False
        self.beginResetModel()
        self.beginRemoveRows(
            parentNode.index(), position, 
            position + rows - 1)
        
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        self.endResetModel()
        
        return success


