#import general
from PyQt5 import QtWidgets, QtGui, QtCore
import json
import os

class SessionNode(QtGui.QStandardItem):
    
    def __init__(self, name , parent = None):
        QtGui.QStandardItem.__init__(self, parent)

        self._name      = name
        self._children  = []
        self._parent    = parent
        self._model     = None
        
        if parent is not None:
            parent.addChild(self)

    def referenceModel(self,model):
        self._model = model
        for child in self._children:
            child.referenceModel(self._model)

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        child._model = self.model()

        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None
        child._model = None
        return True

    def name(self):
        def fget(self): return self._name
        def fset(self, value): self._name = value
        return locals()

    def childFromName(self, name):
        '''
        Get the child item corresponding to a name
        '''
        for child in self._children:
            if name == child._name:
                return child 
        return None

    def child(self, row):
        if row >= self.childCount():
            return None
        return self._children[row]
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self.parent() is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
        
        output += "|------" + self._name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += "\n"
        
        return output

    def __str__(self):
        return self.log()

    def data(self, column):
        
        if column == 0: return self._name
        # elif column is 1: return self.typeInfo()
    
    def setData(self, column, value):
        if   column is 0: self._name = value.toPyObject()
        elif column is 1: self._value = value
    
    def resource(self):
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable #| QtCore.Qt.ItemIsEditable

    def setString(self):
        pass

    def model(self):
        return self._model
        
    def index(self):
        if not self.row() is None:
            return self._model.createIndex(self.row(),0,self)
        else:
            return QtCore.QModelIndex()

    def save(self):
        '''
        returns the formated dictionary with the children
        '''
        output = {}
        for child in self._children:
            output[child._name] = child.save()

        return output

    def saveToFile(self, path):
        '''
        saves the tree to a json format
        '''
        output = self.save()
        with open(path, 'w') as f:
            json.dump(output, f)
        os.chmod(path, 0o777)

    def load(self, input_dict):
        '''
        reads the input dictionary
        '''
        for child in self._children:
            if child._name in input_dict.keys():
                child.load(input_dict[child._name])

    def loadFromFile(self, path):
        '''
        saves the tree to a json format
        '''
        with open(path, 'r') as f:
            input_dict = json.load(f)
        self.load(input_dict)
