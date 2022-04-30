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

#import general
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import numpy as np

# The local imports
from simpleplot.canvas.multi_canvas import MultiCanvasItem
from simpleplot.gui_main.main_window import MainWindow
from simpleplot.models.project_node import ProjectNode
from simpleplot.models.project_node import PlotItem

def startPlayGround():
    #set upt the window and the plot widget
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    project_item = ProjectNode(name = "hey")
    window._sidebar._tree_view.model().insertRows(
        0,1,[project_item], 
        window._sidebar._tree_view.model().root())
    
    data_node = project_item.childFromName('Datasets')
    data_item = data_node.addDataItem()

    # from .core.io.io_data_import import IODataLoad
    # loader = IODataLoad(data_item.data_item, r"~/home/alexander/Desktop/example.txt")
    # loader.load("txt")

    # behavior = [
    #     ['[ dim_1 ]', 'Variable 0', 0], 
    #     ['[ dim_2 ]', 'Variable 1', 0], 
    #     ['Data axis n. 0', 'x', 0]]

    # from .models.project_node import FitLinkItem, FitItem
    # data_link_item  = FitLinkItem()
    # data_injector   = data_link_item.data_injector
    # data_injector.setDataSource(data_item.data_item)
    # data_injector.setBehavior(
    #     behavior, 
    #     ['x','Variable 0', 'Variable 1'])
    # new_fit_item    = FitItem(link_item = data_injector) 

    # target = None
    # for widget in QtWidgets.QApplication.topLevelWidgets():
    #     if widget.__class__.__name__ == "MainWindow":
    #         target = widget
    # if target == None: return

    # target_model = target._model
    # target_model.insertRows(
    #     data_item.childCount(), 1,
    #     [data_link_item], data_item
    # )
    # target_model.insertRows(
    #     project_item.childFromName("Analysis").childCount(), 
    #     1, [new_fit_item], 
    #     project_item.childFromName("Analysis")
    # )
    
    # data_injector.addFitTarget(new_fit_item)

    #set the import
    # import_window = window._sidebar.addDataTxt(target.childFromName("Datasets"))

    # # import_window.io_input_in.setText(r"/Users/alexanderschober/Desktop/DemoRawImport")

    # import_window.io_input_in.setText(r"/home/alexander/Google Drive/Work/2014:2017 Lipp (PhD)/software/R-DATA/Demo/DemoRawImport")
    # import_window.scan_folder_in()

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][0][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(0,0))

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][2][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(2,0))
    # import_window._process_export()
    # import_window.close()

    # import_window = window._sidebar.addDataTxt(target.childFromName("Datasets"))
    # import_window.io_input_in.setText(r"/home/alexander/test")
    # import_window.scan_folder_in()

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][0][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(0,0))

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][3][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(3,0))
    # import_window._process_export()
    # import_window.close()

    #set the plot
    plot = PlotItem(
        grid = [[True, True], [True, True]], 
        element_types = [["2D","2D"],["2D","3D"]], 
        x_ratios = [1,1],
        y_ratios = [1,1])
    window._sidebar.createPlotItem(project_item.childFromName("Plots"), plot)
    sys.exit(app.exec_())

def exampleLinePlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['2D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    #set the ax plot
    first = ax.addPlot(
        'Scatter', 
        Name        = 'sin', 
        Style       = ['-','d','r', '10'], 
        Log         = [False,False])
    second = ax.addPlot(
        'Scatter', 
        Name        = 'cos', 
        Style       = ['d','r','20'], 
        Log         = [False,False])
    third = ax.addPlot(
        'Scatter', 
        Name        = 'tan', 
        Line_thickness   = 3, 
        Style       = ['-'], 
        Log         = [False,False])

    ax.draw()

    x_2 = np.linspace(np.pi, 4*np.pi, 100)
    y = np.sin(x_2)
    y_1 = np.cos(x_2+0.5)
    y_2 = np.cos(x_2)+2*np.sin(x_2)

    first.setData(x = x_2, y = y+2)
    second.setData(x = x_2, y = y_1+3, error = {'width' : 0.1,'height': 0.5})
    third.setData(x = x_2, y = y_2+4)
    ax.zoomer.zoom()

    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleMultiLinePlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid            = [[True, True], [True, True]],
        element_types   = [['2D', '2D'], ['2D', '2D']],
        x_ratios        = [1,1],
        y_ratios        = [1,1],
        background      = "b")
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)  
    bx = multi_canvas.getSubplot(0,1)  
    cx = multi_canvas.getSubplot(1,0)  
    dx = multi_canvas.getSubplot(1,1)    

    ax.pointer.pointer_handler['Sticky'] = 3
    bx.pointer.pointer_handler['Sticky'] = 3
    cx.pointer.pointer_handler['Sticky'] = 4
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    #set the ax plot
    first = ax.addPlot(
        'Scatter', 
        Name        = 'sin', 
        Style       = ['-','d','r', '10'], 
        Log         = [False,False])
    second = bx.addPlot(
        'Scatter', 
        Name        = 'cos', 
        Style       = ['d','r','20'], 
        Log         = [False,False])
    third = cx.addPlot(
        'Scatter', 
        Name        = 'tan', 
        Line_thickness   = 3, 
        Style       = ['-'], 
        Log         = [False,False])

    ax.draw()
    bx.draw()
    cx.draw()
    dx.draw()

    x_2 = np.linspace(np.pi, 4*np.pi, 100)
    y = np.sin(x_2)
    y_1 = np.cos(x_2+0.5)
    y_2 = np.cos(x_2)+2*np.sin(x_2)

    first.setData(x = x_2, y = y+2)
    second.setData(x = x_2, y = y_1+3, error = {'width' : 0.1,'height': 0.5})
    third.setData(x = y_2+4, y = x_2)
    ax.zoomer.zoom()

    multi_canvas.link(ax,bx, 'x', 'x')
    multi_canvas.link(ax,cx, 'x', 'y')
    multi_canvas.link(bx,ax, 'x', 'x')

    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleProjectionPlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True, False], [True, True]],
        element_types = [['2D', '2D'], ['2D', '2D']],
        x_ratios    = [5, 1],
        y_ratios    = [1, 5],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)  
    cx = multi_canvas.getSubplot(1,0)  
    dx = multi_canvas.getSubplot(1,1)        
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    #set the ax plot
    surface = cx.addPlot(
        'Surface', 
        z = np.cos(xv)+np.sin(yv+xv),
        Name        = 'key',
        Colors      = Colors,
        Positions   = Positions)
    
    # histogram = surface.childFromName('Surface').childFromName('Shader').getHistogramItem()
    # cx.addItem('right', histogram)
    
    first = ax.addPlot(
        'Scatter', 
        Name        = 'sin', 
        Style       = ['-','d','r', '10'], 
        Log         = [False,False])
    second = dx.addPlot(
        'Scatter', 
        Name        = 'cos', 
        Style       = ['-','d','r','20'], 
        Log         = [False,False])

    surface.addProjectionItem(first, direction = 'x')
    surface.addProjectionItem(second, direction = 'y')

    multi_canvas.link(cx,ax, 'x', 'x')
    multi_canvas.link(cx,dx, 'x', 'x')

    ax.pointer.pointer_handler['Sticky'] = 3
    dx.pointer.pointer_handler['Sticky'] = 4

    cx.draw()
    ax.draw()
    dx.draw()
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleSurfacePlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    
    
    x = np.linspace(-4*np.pi,4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    for j in range(0,4):
        for i in range(0,4):

            surface = ax.addPlot(
                'Surface', 
                x = x + i*4*np.pi*2+1,
                y = x + j*4*np.pi*2+1,
                z = np.cos(np.sqrt(xv**2+yv**2)+((j*4)+i)*np.pi/8)*0.0001,
                Name        = 'key',
                Colors      = Colors,
                Positions   = Positions)


    ax.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = -np.cos(xv)-np.sin(yv)+2,
        Name        = 'key',
        Colors      = Colors[::-1],
        Positions   = Positions)

    ax.draw()
    histogram = surface.childFromName('Surface').childFromName('Shader').getHistogramItem()
    ax.addHistogramItem('right', histogram)
    
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleStepPlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    
    
    x = np.linspace(-4*np.pi,4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    surface = ax.addPlot(
        'Step', 
        x = x,
        y = x,
        z = (-np.cos(xv)-np.sin(yv)-2),
        Name        = 'key',
        Colors      = Colors[::-1],
        Positions   = Positions)


    ax.addPlot(
        'Step', 
        x = x,
        y = x,
        z = -np.cos(xv)-np.sin(yv)+2,
        Name        = 'key',
        Colors      = Colors[::-1],
        Positions   = Positions)

    ax.draw()
    # histogram = surface.childFromName('Surface').childFromName('Shader').getHistogramItem()
    # ax.addItem('right', histogram)
    
    # multi_canvas.canvas_nodes[0][0][0].generateDefaultConfiguration()
    multi_canvas.canvas_nodes[0][0][0].loadDefaultConfiguration()
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleVolumePlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    def calc(i,j,k):
        return np.sin(np.cos(i/10)+np.sin(j/10)+np.sin(k/10))
    data_0 = np.fromfunction(calc, (100,100,100))
    data_0 += np.random.rand(*data_0.shape)*0.1
    volume = ax.addPlot(
        'Volume', 
        Name = 'The Volume',
        x = np.linspace(5,15,100) ,
        y = np.linspace(0,10,100) , 
        z = np.linspace(0,10,100) ,
        data = data_0)

    data = np.zeros(4, [("position_vec", np.float32, 3),
                    ("color_vec",    np.float32, 4)])
    data['position_vec'] = (-1,+1,0), (+1,+1,0), (-1,-1,0), (+1,-1,0)
    data['color_vec']    = (0,1,0,1), (1,1,0,1), (1,0,0,1), (0,0,1,1)
    # volume = ax.addPlot(
    #     'Vector field', 
    #     Name = 'The field',
    #     x = np.linspace(5,15,100) ,
    #     y = np.linspace(0,10,100) , 
    #     z = np.linspace(0,10,100) ,
    #     vec = data)

    surface = ax.addPlot(
        'Surface',
        Name = 'Surface bot', 
        x = x,
        y = x,
        z = np.cos(xv)+np.sin(yv)-2,
        Colors      = Colors,
        Positions   = Positions)

    ax.addPlot(
        'Surface',
        Name = 'Surface top', 
        x = x,
        y = x,
        z = -np.cos(xv)-np.sin(yv)+2,
        Colors      = Colors[::-1],
        Positions   = Positions)

    ax.draw()
    
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleDistPlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['2D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)   
    x =  np.random.rand(1000)

    data = np.array([np.array([
        x[i]+np.random.random()*3e-1*((x[i]-0.5)*2)**2, 
        x[i]+np.random.random()*3e-1*((x[i]-0.5)*2)**2, 
        x[i]+np.random.random()*3e-1*((x[i]-0.5)*2)**2,
        ((x[i]-0.5)*2)**2])
        for i in range(1000)])
    data *= np.array([10,10,10,1])

    color = np.array([np.random.rand(4) for i in range(1000)])

    ax.addPlot(
        'Distribution',
        Name = 'Dist',
        data = data,
        color = color)

    ax.draw()
    
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleCrystalPlot():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    

    data = np.array([np.random.rand(4) for i in range(100)])
    data *= np.array([10,10,10,1])

    color = np.array([np.random.rand(4) for i in range(100)])

    ax.addPlot(
        'Crystal',
        Name = 'Dist',
        data = data,
        color = color)

    ax.draw()
    
    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleItems():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['2D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "w",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)    
    circle = ax.addItem("Circle")
    ellipse = ax.addItem("Ellipse")
    square = ax.addItem("Square")
    rectangle = ax.addItem("Rectangle")
    pie = ax.addItem("Pie")
    pie = ax.addItem("Triangle")


    plot = ax.addPlot('Scatter', Style = ['d','r','20'])

    ax.draw()

    ellipse['Position'] = [0.,0.,0.]
    ellipse['Diameters'] = [0.5,1,0.]
    
    square['Position'] = [0.,3.,0.]
    square['Dimension'] = 0.5
    
    rectangle['Position'] = [-2.,-1.,0.]
    rectangle['Dimensions'] = [1.,1.]
    plot.setData(
        x = np.array([i for i in range(100)])/10,
        y = np.sin(np.array([i for i in range(100)])/10))

    #show widget
    widget.show()
    sys.exit(app.exec_())

def exampleScientificComboBox():

    from .gui_main.widgets.scientific_combobox import ScientificComboBox
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = ScientificComboBox()

    widget.addItem(0.54)
    widget.addItem('1.54')
    widget.addItem(02.54424523453453)
    widget.addItem(4534534530.54)
    widget.addItem(0.000000000000005)

    def showProperties():
        print(widget.currentIndex(),widget.currentText(),widget.currentData())
    widget.currentIndexChanged.connect(showProperties)
    #show widget
    widget.show()
    sys.exit(app.exec_())

def example():

    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True, True, True], [True, True, True]],
        element_types = [['3D', '2D', '3D'], ['3D', '2D', '3D']],
        x_ratios    = [1,1,1],
        y_ratios    = [1,1],
        background  = "b",
        highlightthickness = 0)
    
    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)
    bx = multi_canvas.getSubplot(0,1)
    cx = multi_canvas.getSubplot(0,2)
    dx = multi_canvas.getSubplot(1,0)
    ex = multi_canvas.getSubplot(1,1)
    fx = multi_canvas.getSubplot(1,2)

    #set the generalized plot data
    x_bin = np.arange(0, 100, 1)
    y_bin = np.arange(0, 100, 1)
    z_bin = np.random.rand(100,100)*100
    
    x = np.linspace(-4*np.pi, 4*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x+0.5)
    y_2 = np.cos(x)+2*np.sin(x)

    Colors = [
            [0.,1.,1.],
            [0.,0.,1.],
            [0.,1.,0.],
            [1.,0.,0.],
            [0.,1.,0.],
        ]
    Positions = [0,0.25,0.5,0.75,1.]

    #Example of 2D data as bin
    surf = bx.addPlot(
        'Surface', 
        Name = 'bin')
    bx.draw()

    surf.setData(       
        x = x_bin,
        y = x_bin, 
        z = np.cos(xv)+np.sin(yv)-2 )

    bx.axes['bottom'].setScale(8*np.pi/100)
    bx.axes['left'].setScale(8*np.pi/100)
    # bx.setHistogram('right', surf)
    bx.zoomer.zoom()
    
    #set the ax plot
    first = ex.addPlot(
        'Scatter', 
        Name        = 'sin', 
        Style       = ['-','d','r', '10'], 
        Log         = [False,False])
    second = ex.addPlot(
        'Scatter', 
        Name        = 'cos', 
        Style       = ['d','r','20'], 
        Log         = [False,False],
        Error       = {})
    third = ex.addPlot(
        'Scatter', 
        Name        = 'tan', 
        Line_thickness   = 3, 
        Style       = ['-'], 
        Log         = [False,False])

    ex.draw()

    x_2 = np.linspace(np.pi, 4*np.pi, 100)
    y = np.sin(x_2)
    y_1 = np.cos(x_2+0.5)
    y_2 = np.cos(x_2)+2*np.sin(x_2)

    first.setData(x = x_2, y = y+2)
    second.setData(x = x_2, y = y_1+3, error = {'width' : 0.1,'height': 0.1})
    third.setData(x = x_2, y = y_2+4)
    ex.zoomer.zoom()

    #example of 3D data
    ax.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = np.cos(xv)+np.sin(yv)-2,
        Name        = 'key',
        Colors      = Colors,
        Positions   = Positions)
    
    # ax.addPlot(
    #     'Surface', 
    #     x = x,
    #     y = x,
    #     z = -np.cos(xv)-np.sin(yv)+2,
    #     Name        = 'key',
    #     Colors      = Colors[::-1],
    #     Positions   = Positions)

    ax.draw()

    #Example of volume data
    def calc(i,j,k):
        return np.sin(np.cos(i/10)+np.sin(j/10)+np.sin(k/10))
    data_0 = np.fromfunction(calc, (100,100,100))
    data_0 += np.random.rand(*data_0.shape)*0.1
    volume = dx.addPlot(
        'Volume', 
        x = np.linspace(5,15,100) ,
        y = np.linspace(0,10,100) , 
        z = np.linspace(0,10,100) ,
        data = data_0)

    data = np.zeros(4, [("position_vec", np.float32, 3),
                    ("color_vec",    np.float32, 4)])
    data['position_vec'] = (-1,+1,0), (+1,+1,0), (-1,-1,0), (+1,-1,0)
    data['color_vec']    = (0,1,0,1), (1,1,0,1), (1,0,0,1), (0,0,1,1)
    volume = dx.addPlot(
        'Vector field', 
        x = np.linspace(5,15,100) ,
        y = np.linspace(0,10,100) , 
        z = np.linspace(0,10,100) ,
        vec = data)

    dx.draw()

    #example of 3D bar graphs
    bar = fx.addPlot('Bar')
    fx.draw()
    bar.setData( x = np.arange(100)/5., y = np.arange(100)/5., upper =  np.cos(xv)+np.sin(yv)+2, lower = np.cos(xv)+np.sin(yv)-2)

    #show widget
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # exampleScientificComboBox()
    # startPlayGround()
    # exampleItems()
    # exampleMultiLinePlot()
    # exampleProjectionPlot()
    # exampleLinePlot()
    # example()
    exampleSurfacePlot()
    # exampleVolumePlot()
    # exampleDistPlot()
    # exampleCrystalPlot()
    # exampleStepPlot()