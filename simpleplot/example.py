

from .canvas.multi_canvas import MultiCanvasItem
#import general
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import numpy as np

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
    surface = ax.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = np.cos(xv)+np.sin(yv)-2,
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
    ax.addItem('right', histogram)
    
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
    # exampleMultiLinePlot()
    exampleProjectionPlot()
    # exampleLinePlot()
    # example()
    # exampleSurfacePlot()