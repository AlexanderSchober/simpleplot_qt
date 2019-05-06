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
from .canvas2d import Canvas2DNode
from .canvas3d import Canvas3DNode
from .canvas   import CanvasNode

from ..model.models import SessionModel
from ..gui.mode_select import ModeSelect
from ..model.node import SessionNode

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

        self._rootNode  = SessionNode("Root", None)

        self.grid       = grid
        self.x_ratios   = x_ratios
        self.y_ratios   = y_ratios
        self.parent     = widget
        self.icon_dim   = 25

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
                self.canvas_nodes[i][j]=[
                    CanvasNode(
                        "Subplot ("+str(i)+", "+str(j)+")", self._rootNode,
                        multi_canvas = self,
                        idx = len(self.canvas_nodes),
                        Type = '2D',
                        **kwargs),i,j]

            elif element_types[i][j] == '3D':
                self.canvas_nodes[i][j]=[
                    CanvasNode(
                        "Subplot ("+str(i)+", "+str(j)+")", self._rootNode,
                        multi_canvas = self,
                        idx = len(self.canvas_nodes),
                        Type = '3D',
                        **kwargs),i,j]

        self._proxyModel    = QtCore.QSortFilterProxyModel(self)
        self._model         = SessionModel(
            self._rootNode, self, 
            max([4,len(self.x_ratios), 
            len(self.y_ratios)])+2)

        self._placeObjects()
        self._configureGrid()
        self._layoutManager()
        self.parent.setLayout(self)

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

    def _configureGrid(self):
        '''
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        '''
        grid_loop = [
            (i, j)
            for i in range(len(self.grid))
            for j in range(len(self.grid[0]))]

        for i,j in grid_loop:
            width  = ( 
                self.parent.frameGeometry().width()
                /len(self.canvas_nodes[i]))/ self.x_ratios[j]
            height = (
                self.parent.frameGeometry().height() 
                / len(self.canvas_nodes) )/ self.y_ratios[i]
            self.canvas_nodes[i][j][0].widget.resize(width, height)

        for i in range(len(self.x_ratios)):
            try:
                self.setColumnStretch(i,1/self.x_ratios[i])
            except:
                pass
        
        for j in range(len(self.y_ratios)):
            try:
                self.setRowStretch(j,1/self.y_ratios[j])
            except:
                if self.Verbose:
                    print('Could not set the row weight for: ',j)

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
    
if __name__ == '__main__':
    import sys
    import numpy as np
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True, True], [True, True]],
        element_types = [['3D', '2D'], ['3D', '2D']],
        x_ratios    = [1,1],
        y_ratios    = [1,1],
        background  = "w",
        highlightthickness = 0)

    x_bin = np.arange(0, 100, 1)
    y_bin = np.arange(0, 100, 1)
    z_bin = np.random.rand(100,100)*100
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    ax = multi_canvas.getSubplot(0,1)
    surf = ax.addPlot(
        'Surface', 
        Name = 'bin')
    ax.draw()
    surf.setData(       
        x = x_bin,
        y = x_bin, 
        z = np.cos(xv)+np.sin(yv)-2 )


    ax.axes['bottom'].setScale(8*np.pi/100)
    ax.axes['left'].setScale(8*np.pi/100)
    ax.setHistogram('right', surf)
    ax.pointer
    ax.zoomer.zoom()
    
    #set the ax plot
    bx = multi_canvas.getSubplot(1,1)
    first = bx.addPlot(
        'Scatter', 
        Name        = 'sin', 
        Style       = ['-','d','r', '10'], 
        Log         = [False,False])
    second = bx.addPlot(
        'Scatter', 
        Name        = 'cos', 
        Style       = ['d','r','20'], 
        Log         = [False,False],
        Error       = {})
    third = bx.addPlot(
        'Scatter', 
        Name        = 'tan', 
        Line_thickness   = 3, 
        Style       = ['-'], 
        Log         = [False,False])
    bar = bx.addPlot('Bar', x = x, y = x, z =  np.cos(xv)+np.sin(yv)+2)
    bx.draw()

    first.setData(x = x, y = y)
    second.setData(x = x, y = y_1, error = {'width' : 0.1,'height': 0.1})
    third.setData(x = x, y = y_2)

    bx.zoomer.zoom()

    cx = multi_canvas.getSubplot(0,0)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    cx.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = np.cos(xv)+np.sin(yv)-2,
        Name        = 'key',
        Colors      = Colors,
        Positions   = Positions)
    
    cx.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = -np.cos(xv)-np.sin(yv)+2,
        Name        = 'key',
        Colors      = Colors[::-1],
        Positions   = Positions)

    cx.draw()

    dx = multi_canvas.getSubplot(1,0)
    bar = dx.addPlot('Bar')
    bar_2 = dx.addPlot('Bar')
    dx.draw()
    bar.setData( x = x, y = x, z =  np.cos(xv)+np.sin(yv)+2, z_lower = np.cos(xv)+np.sin(yv)-2)
    bar_2.setData( x = x, y = x, z =  np.cos(xv)+np.sin(yv)+6, Lower = [[7]])
    widget.show()
    sys.exit(app.exec_())