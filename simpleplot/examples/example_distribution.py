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

def exampleDistribution():
    #set upt the window and the plot widget
    app 	        = QtWidgets.QApplication(sys.argv)
    widget          = QtWidgets.QWidget()
    multi_canvas    = MultiCanvasItem(
        widget      = widget,        
        grid        = [[True]],
        element_types = [['3D']],
        x_ratios    = [1],
        y_ratios    = [1],
        background  = "k",
        highlightthickness = 0)

    #link to the subplots
    ax = multi_canvas.getSubplot(0,0)   
    x =  np.random.rand(100000)

    data = np.zeros((100000,4), dtype='f4')
    data[:,0] = x+np.random.rand(x.shape[0])*3e-1*((x-0.5)*2)**2
    data[:,1] = x+np.random.rand(x.shape[0])*3e-1*((x-0.5)*2)**2
    data[:,2] = x+np.random.rand(x.shape[0])*3e-1*((x-0.5)*2)**2
    data[:,3] = ((x-0.5)*2)**2

    data *= np.array([10,10,10,1])

    color = np.random.rand(x.shape[0],4)

    ax.addPlot(
        'Distribution',
        Name = 'Dist',
        data = data,
        color = color)

    ax.draw()

    #show widget
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    exampleDistribution()