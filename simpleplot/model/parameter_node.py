from .node import SessionNode
from PyQt5 import QtWidgets, QtGui, QtCore
 
class ParameterNode(SessionNode):
    def __init__(self, name = 'None', parent = None, parameters = {}, method = None):
        SessionNode.__init__(self, name, parent)
        self._vector_elements = []
        self.kwargs = {}
        self.description = ''
 
    def data(self, column):
        if   column is 0: return self._name
        elif column is 1: return self.description
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled 
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

class ParameterItem(SessionNode):
    def __init__(self, name, parent, value, method):
        SessionNode.__init__(self, name, parent)
        self._value = value
        self._method = method
         
    def data(self, column):
        if column is 0: return self._name
        elif column  == 1:
            if not type(self._value) == QtGui.QFont: 
                return self._value
            else:
                return str(self._value.family())+', '+str(self._value.pointSize())+'pt'
     
    def setData(self, column, value):
        if  column > 0: self._value = value
             
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled 
        else:
            return QtCore.Qt.ItemIsEnabled  | QtCore.Qt.ItemIsEditable
