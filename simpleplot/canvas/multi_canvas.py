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

#import personal dependencies
from .canvas   import CanvasNode
from ..model.models import SessionModel
from ..gui.mode_select import ModeSelect
from ..model.node import SessionNode
from ..model.parameter_class import ParameterHandler 

#import general
from PyQt5 import QtWidgets, QtGui, QtCore

class Second(QtGui.QMainWindow):
    def __init__(self, model, parent=None):
        super(Second, self).__init__(parent)
        self.tree = preferenceTree(self)
        self.setCentralWidget(self.tree)
        self.tree.setModel(model)
        self.tree.collapsed.connect(self.resizeTree)
        self.tree.expanded.connect(self.resizeTree)

    def resizeTree(self):
        self.tree.resizeColumnToContents(0)

class preferenceTree(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        QtWidgets.QTreeView.__init__(self, parent = parent)
        self.clicked.connect(self.clickManager)
        
    def clickManager(self, index):
        if index.column() > 0:
            self.edit(index)

class MultiCanvasItem(QtWidgets.QGridLayout):
    
    def __init__(
        self,widget = None,grid = [[True]],element_types  = None,
        x_ratios = [1],y_ratios = [1],no_title = False,**kwargs):
        '''
        This method is the plot canvas where all the 
        elements will be drawn upon. It inherits
        from the GraphicsLayoutWidget library that 
        was custom built on top of qt for python. 

        Parameters
        ----------
        widget : QtWidgets.QWidget
            is the parent widget 

        grid : list of list of bool
            is the amount of rows ans cols wanted

        x_ratio : list of float
            is the ratios along the cols

        y_ratio : list of float
            is the ratios along the rows

        no_title allows to set titles or not
        '''
        QtWidgets.QGridLayout.__init__(self)

        self.grid       = grid
        self.x_ratios   = [float(e) for e in x_ratios]
        self.y_ratios   = [float(e) for e in y_ratios]
        self.parent     = widget
        self.icon_dim   = 25
        self.subplot_names      = []

        self._rootNode  = SessionNode("Root", None)
        
        self.canvas_nodes = [
            [None 
            for i in range(len(self.grid[0]))] 
            for j in range(len(self.grid))]

        grid_loop = [
            (i, j)
            for i in range(len(self.grid))
            for j in range(len(self.grid[0]))]

        for i,j in grid_loop:
            if not grid[i][j]:
                self.canvas_nodes[i][j]=[None, i,j]

            elif element_types  ==  None or element_types[i][j] == '2D':
                self.subplot_names.append("Subplot ("+str(i)+", "+str(j)+")")
                self.canvas_nodes[i][j]=[
                    CanvasNode(
                        "Subplot ("+str(i)+", "+str(j)+")", self._rootNode,
                        multi_canvas = self,
                        idx = len(self.canvas_nodes),
                        Type = '2D',
                        **kwargs),i,j]

            elif element_types[i][j] == '3D':
                self.subplot_names.append("Subplot ("+str(i)+", "+str(j)+")")
                self.canvas_nodes[i][j]=[
                    CanvasNode(
                        "Subplot ("+str(i)+", "+str(j)+")", self._rootNode,
                        multi_canvas = self,
                        idx = len(self.canvas_nodes),
                        Type = '3D',
                        **kwargs),i,j]

        self._initialise()

        self._proxyModel    = QtCore.QSortFilterProxyModel(self)
        self._model         = SessionModel(
            self._rootNode, self, 
            max([4,len(self.x_ratios), 
            len(self.y_ratios)])+2)

        self._placeObjects()
        self._configureGrid()
        self._layoutManager()
        self.parent.setLayout(self)

    def _initialise(self):
        self.handler        = ParameterHandler(
            name = 'Multi-canvas options', 
            parent = self._rootNode) 
            
        self.handler.addParameter(
            'x_ratios', self.x_ratios,
            method = self._configureGrid)
        self.handler.addParameter(
            'y_ratios', self.y_ratios,
            method = self._configureGrid)
        self.handler.addParameter(
            'Select', 'All',
            choices = ['All']+self.subplot_names,
            method = self._selectPlot)
        # self.handler.addParameter(
        #     'Background',  QtGui.QColor('white'),
        #     method = self._setBackground)
        # self.handler.addParameter(
        #     'Horizontal spacing', 1,
        #     method = self._setHorizontalSpacing)
        # self.handler.addParameter(
        #     'Vertical spacing', 1,
        #     method = self._setVerticalSpacing)

    def _placeObjects(self):
        '''
        This method aims at placing all the Canvas 
        class widgets onto the multiCanvas grid. It
        will therefore cycle through and use the 
        inherited addWidget method.
        '''
        grid_loop = [
            (i, j)
            for i in range(len(self.grid))
            for j in range(len(self.grid[0]))]

        for i,j in grid_loop:
            if self.canvas_nodes[i][j][0] == None:
                pass
            else:
                self.addWidget(
                    self.canvas_nodes[i][j][0].widget, 
                    self.canvas_nodes[i][j][1], 
                    self.canvas_nodes[i][j][2])

    def _configureGrid(self, zeros = False):
        '''
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        '''
        for i in range(len(self.handler['x_ratios'])):
            try:
                self.setColumnStretch(i,self.handler['x_ratios'][i] if not zeros else 0)
            except:
                pass
        
        for j in range(len(self.handler['y_ratios'])):
            try:
                self.setRowStretch(j,self.handler['y_ratios'][j] if not zeros else 0)
            except:
                if self.Verbose:
                    print('Could not set the row weight for: ',j)

    def _selectPlot(self):
        '''
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        '''
        if self.handler['Select'] == 'All':
            for child in self._rootNode._children:
                if 'Subplot'in child._name:
                    child.widget.setVisible(True)
            self._configureGrid()
        else:
            for child in self._rootNode._children:
                if 'Subplot'in child._name and not child._name == self.handler['Select']:
                    child.widget.setVisible(False)
                elif 'Subplot'in child._name and child._name == self.handler['Select']:
                    child.widget.setVisible(True)
            self._configureGrid(zeros = True)

    def _layoutManager(self):
        '''
        This method will process the layout of the 
        various simpleplot tools and buttons around
        the main frame. 
        '''
        self.bottom_selector = ModeSelect(self,self.parent, self.icon_dim)
        self.addItem(
            self.bottom_selector, 
            len(self.grid), 
            0,  
            columnSpan=len(self.grid[0]))
        
    def getSubplot(self,i,j):
        '''
        This method allows the user to fetch the 
        sublot that he recquires. This is though to be
        used very much like the subplot function in
        matplotlib. 
        '''
        return self.canvas_nodes[i][j][0].artist


    def link(self, ax , bx , variableIn = 'x', variableOut = 'x'):
        '''
        This class is here to allow for corss listening between variables
        between different subplots...
        
        
        This will call the pointer of ax and bx and tell them to pass on the
        coordinates to the pointer handlers each time there is a refresh. 
        
        So basically we parasite the pointer to speak to another element
        
        This will also return a link in the link list and an associated ID
        The ID will be returned and can be fed to the Unlink
        '''
        
        #set the target
        target = bx.mouse
        link = [
            '',
            ax.mouse.link_list,
            variableIn,
            variableOut, 
            target, 
            bx.mouse]
        #add the element at the end of the list
        self.link_list.append(link)
        #append the ID
        ID = self.link_list[-1][0] = len(self.link_list)

        #finally send it out to the linker
        link[1].append(self.link_list[-1])
        
        return ID
    
