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
from PyQt5 import QtWidgets
import sys
import numpy as np

# The local imports
from ..canvas.multi_canvas import MultiCanvasItem

def exampleVolume():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "k",
        highlightthickness = 0)

    #link to the subplots
    ax      = multi_canvas.getSubplot(0,0)    

    def calc(i,j,k):
        return np.sin(np.cos(i/10)+np.sin(j/10)+np.sin(k/10))
    data_0 = np.fromfunction(calc, (200,200,200))
    data_0 += np.random.rand(*data_0.shape)*0.1
    ax.addPlot(
        'Volume', 
        Name = 'The Volume',
        x = np.linspace(0,1,200) ,
        y = np.linspace(-4,-1,200) , 
        z = np.linspace(0,1,200) ,
        data = data_0)

    ax.draw()

    #show widget
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    exampleVolume()