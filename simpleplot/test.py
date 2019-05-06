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

#import dependencies
from simpleplot.canvas.multi_canvas import MultiCanvasItem
from PyQt5 import QtWidgets
import numpy as np
import sys

def test_normal():

    ######################################################
    #set up the app
    app 	    = QtWidgets.QApplication(sys.argv)
    widget      = QtWidgets.QWidget()
    mycanvas    = MultiCanvasItem(
        widget,
        grid        = [[True,True],[True,True]],
        element_types = [['2D', '3D'],['3D','2D']],
        x_ratios    = [2,3],
        y_ratios    = [2,2],
        background  = "w",
        highlightthickness = 0)

    widget.show()

    delta = 3
    x = np.arange(-600, 600, delta)/100
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x)
    y_2 = np.tan(x)

    #set the ax plot
    ax = mycanvas.get_subplot(0,0)
    ax.add_plot('Scatter', x,y,   Name = 'sin', Style = ['d','r', '10'], Log = [False,False])
    ax.add_plot('Scatter', x,y_1, Name = 'cos', Thickness = 3, Style = ['-'], Log = [False,False])
    ax.add_plot('Scatter', x,y_2, Name = 'tan', Thickness = 3, Style = ['-'], Log = [False,False])
    ax.pointer['Sticky'] = 0
    ax.draw()
    ax.remove_plot('Scatter','tan')
    ax.axes.show_grid(x = True, y = True, alpha = 0.5)

    #set the bx plot
    bx = mycanvas.get_subplot(0,1)
    bx.add_plot('Scatter', x, y, z =  z, Color = 'r', Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    bx.add_plot('Scatter', x, y, z = -z, Color = 'b', Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    bx.add_plot('Scatter', x, z, z =  y, Color = 'g', Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    bx.add_plot('Scatter', x, z, z = -y, Color = 'w', Name = 'sin', Style = ['-','s','10'], Log = [False,False])


    bx.draw()


    cx = mycanvas.get_subplot(1,0)
    cx.add_plot('Scatter', x,y,   Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    cx.draw()

    dx = mycanvas.get_subplot(1,1)
    dx.add_plot('Scatter', x,y,   Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    dx.draw()
        

    # #link the axes
    #mycanvas.link(ax, bx, variableIn = 'x', variableOut = 'x')
    #mycanvas.link(ax, cx, variableIn = 'x', variableOut = 'y')
    # mycanvas.link(bx, ax, variableIn = 'x', variableOut = 'x')
    #mycanvas.link(dx, cx,variableIn = 'y',variableOut = 'x')



    # color_map = [
    #      np.array([0., 1., 0.5, 0.25, 0.75]),
    #      np.array(
    #          [
    #              [  0, 255, 255, 255], 
    #              [255, 255,   0, 255], 
    #              [  0,   0,   0, 255], 
    #              [  0,   0, 255, 255], 
    #              [255,   0,   0, 255]], 
    #              dtype=np.ubyte)]


    
    # start teh main loop
    sys.exit(app.exec_())


'''
I want a settings window to adjust padding and ticks and 
things like this dynamically...

class Settings:

'''

def test_3D():

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

    ax = multi_canvas.getSubplot(0,1)
    ax.addPlot('Bin', x_bin,y_bin,z_bin, Name = 'bin')
    ax.draw()

    x = np.linspace(-2*np.pi, 2*np.pi, 100)
    xv, yv = np.meshgrid(x, x)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x)
    y_2 = np.cos(x)*np.sin(x)

    #set the ax plot
    bx = multi_canvas.getSubplot(1,1)
    bx.addPlot('Scatter', x,y,   Name = 'sin', Style = ['-','d','r', '10'], Log = [False,False])
    bx.addPlot('Scatter', x,y_1, Name = 'cos', Thickness = 3, Style = ['-'], Log = [False,False])
    bx.addPlot('Scatter', x,y_2, Name = 'tan', Thickness = 3, Style = ['-'], Log = [False,False])
    bx.draw()

    cx = multi_canvas.getSubplot(0,0)
    cx.addPlot(
        'Surface', 
        x = x,
        y = x,
        z = np.sin(xv+yv),
        Name    = 'key')
        #$Color = meas.sample.elements[sam_key].geometry.strucutre_surfaces[key].color)
    cx.draw()
    # cx.grid.pointer_handler['Grid'] = 3('Grid active', [True, False, False])

    widget.show()
    multi_canvas.launchSettings()
    multi_canvas.settings.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_3D()
    