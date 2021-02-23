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

# import general
from PyQt5 import QtWidgets
import sys
import numpy as np

# The local imports
from PyQt5.QtGui import QFont

from simpleplot.canvas.multi_canvas import MultiCanvasItem


def exampleLine():
    # set upt the window and the plot widget
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    multi_canvas = MultiCanvasItem(
        widget=widget,
        grid=[[True]],
        element_types=[['2D']],
        x_ratios=[1],
        y_ratios=[1],
        background="k",
        highlightthickness=0)

    # link to the subplots
    ax = multi_canvas.getSubplot(0, 0)

    x = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    y = np.sin(x)
    z = np.cos(x)
    y_1 = np.cos(x + 0.5)
    y_2 = np.cos(x) + 2 * np.sin(x)

    # set the ax plot
    first = ax.addPlot(
        'Scatter',
        Name='sin',
        Style=['-', 'd', 'r', 0.2],
        Log=[False, False],
        Color='red')
    second = ax.addPlot(
        'Scatter',
        Name='cos',
        Style=['d', 'r', 0.1],
        Log=[False, False])
    third = ax.addPlot(
        'Scatter',
        Name='tan',
        Line_thickness=3,
        Style=['-'],
        Log=[False, False])
    fourth = ax.addPlot(
        'Scatter',
        Name='tan',
        Line_thickness=3,
        Style=['-'],
        Log=[False, False])
    ax.draw()

    x_2 = np.linspace(0, 4 * np.pi, 100)
    y = np.sin(x_2)
    y_1 = np.cos(x_2 + 0.5)
    y_2 = np.sin(x_2)  # +2*np.sin(x_2)

    first.setPlotData(x=x_2, y=y + 2)
    second.setPlotData(x=x_2, y=y_1 + 3, error={'width': 0.1, 'height': 0.5})
    third.setPlotData(x=x_2, y=y_2 + 1)
    fourth.setPlotData(x=x_2, z=y_2)

    # show widget
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    exampleLine()
