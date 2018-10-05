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
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************

#import dependencies
from .multi_canvas import Multi_Canvas
from PyQt5 import QtWidgets
import numpy as np
import sys



def main():
    

    ######################################################
    #set up the app
    app 	    = QtWidgets.QApplication(sys.argv)
    widget      = QtWidgets.QWidget()
    mycanvas    = Multi_Canvas(
        widget,
        grid        = [[True,True],[True,True]],
        x_ratios    = [2,3],
        y_ratios    = [2,2],
        background  = "w",
        highlightthickness = 0)

    widget.show()

    
    delta = 3
    x = np.arange(0, 600, delta)/100
    y = np.sin(x)
    y_1 = np.cos(x)
    y_2 = np.tan(x)


    #set the ax plot
    ax = mycanvas.get_subplot(0,0)
    ax.add_plot('Scatter', x,y,   Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    ax.add_plot('Scatter', x,y_1, Name = 'cos', Thickness = 3, Style = ['-'], Log = [False,False])
    ax.add_plot('Scatter', x,y_2, Name = 'tan', Thickness = 3, Style = ['-'], Log = [False,False])
    ax.pointer['Sticky'] = 2
    ax.draw()
    ax.remove_plot('Scatter','tan')
    ax.axes.show_grid(x = True, y = True, alpha = 0.5)

    #set the bx plot
    bx = mycanvas.get_subplot(0,1)
    x_bin = np.arange(0, 100, 1)
    y_bin = np.arange(0, 100, 1)
    z_bin = np.random.rand(100,100)*100

    color_map = [
         np.array([0., 1., 0.5, 0.25, 0.75]),
         np.array(
             [
                 [  0, 255, 255, 255], 
                 [255, 255,   0, 255], 
                 [  0,   0,   0, 255], 
                 [  0,   0, 255, 255], 
                 [255,   0,   0, 255]], 
                 dtype=np.ubyte)]

    bx.add_plot('Bin', x_bin,y_bin,z_bin, Name = 'bin', Color_map = color_map , Levels = [50,70])
    bx.pointer['Sticky'] = 3
    bx.draw()
    

    cx = mycanvas.get_subplot(1,0)
    cx.add_plot('Scatter', x,y,   Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    cx.draw()

    dx = mycanvas.get_subplot(1,1)
    dx.add_plot('Scatter', x,y,   Name = 'sin', Style = ['-','s','10'], Log = [False,False])
    dx.draw()
        
    # #grab the subplot definitions
    
    # ax = mycanvas.GetSubPlot(0,0)
    
    # bx = mycanvas.GetSubPlot(1,0)
    
    # cx = mycanvas.GetSubPlot(1,1)
    # #cx.MakeGhost()
    
    # dx = mycanvas.GetSubPlot(0,1)
    
    # # dx.AddContour(X,Y,Z,
    # #               MeshStepping = 50,
    # #               Stepping  = 30,
    # #               Type      = 'Surface',
    # #               MeshThickness = 0.1)

    # dx.AddBin(x,y,Z)

    # #dx.AddCascade(X,Y,Z)
    
    # dx.Live = 2
    # dx.Pointer.Sticky = 0
    
    # ######################################################
    # # add some Plot to the Drawer
    # ax.AddiPlot([1,3,4,5,6,7,8],[1,2,3,2.5,1,0.5,0], Thickness = 5,Name = 'I am first', color = 'red'  , style = ['o',4,4])
    # ax.AddiPlot([1,3,4,4.5,6,7,8],[1,2,3,2,1,0.5,0], Thickness = 8, color = 'black', style = ['o',4,4])
    # ax.AddiPlot([i*0.01 for i in range(0,4*315)],numpy.sin([i*0.01 for i in range(0,4*315)]), color = 'blue', Thickness = 3 )
    # bx.AddPlot([i*0.01 for i in range(0,4*315)],numpy.sin([i*0.01+1 for i in range(0,4*315)]), color = 'yellow', Thickness = 3 )
    # cx.AddPlot(numpy.sin([i*0.01+1 for i in range(0,4*315)]),[i*0.01 for i in range(0,4*315)], color = 'green', Thickness = 3 )
    
    # ax.AddRange([2,3])
    # ax.AddLine(0, Type = 'horizontal',Thickness = 5,Name = 'I am first', color = 'red'  )
    # ax.AddLine(4, Type = 'vertical',Thickness = 3,Name = 'I am first', color = 'black'  )
    
    # ax.Pointer.Sticky = 1
    # #dx.ZoomBox = [0,0,10,10]
    
    # ######################################################
    # #Set some padding parameters for ax
    # ax.Axes.PaddingIn       = [0.05,0.05,0.05,0.05]
    # ax.Axes.PaddingOut      = [0.15,0.1,0.1,0.1]
    # ax.Axes.Thickness       = [2,2,2,2]
    # ax.Axes.XTickSpacing    = 1
    # ax.Axes.XTickType       = 1
    # ax.SmartResize          = True
    # ax.Axes.isYSci          = [True,True,True,True]
    # ax.Pointer.isYSci       = [True,True,True,True]
    
    # ax.Pointer.YSciPrecision = '%.1e'
    
    # ax.Title.SetTitle(text = 'Hello')

    # #link the axes
    mycanvas.link(ax, bx, variableIn = 'x', variableOut = 'x')
    mycanvas.link(ax, cx, variableIn = 'x', variableOut = 'y')
    mycanvas.link(bx, ax, variableIn = 'x', variableOut = 'x')
    mycanvas.link(dx, cx,variableIn = 'y',variableOut = 'x')

    
    # def Print(indx):
    
    #     print(indx)
    
    # #bind cursor
    # ax.Pointer.BindMethod(Print)
    # ax.Pointer.Sticky = 1
    
    # ax.UnbindZoomer()
    # #ax.BindInteractor()
    
    # start teh main loop
    sys.exit(app.exec_())


'''
I want a settings window to adjust padding and ticks and 
things like this dynamically...

class Settings:

'''

if __name__ == "__main__":
    main()