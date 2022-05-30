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

import os

import numpy as np

from ..ploting.graph_items.legend import Legend
from ..ploting.main_handler import get_main_handler
from ..pointer.pointer import Pointer


class Artist:
    """
    The artist is the manager of all canvas instances such as the plot
    area and the overlay, the pointers and the rulers etc ...
    This class will be inherited by the 2d and 3d artist counterparts.
    """

    def __init__(self, canvas=None):

        self.canvas = canvas
        self.artist_type = '2D'
        self.child_widgets = []

        self.draw_surface = None
        self.pointer = None
        self.legend = None

    def connect(self):
        """
        Template to be overwritten
        """
        pass

    def disconnect(self):
        """
        Template to be overwritten
        """
        pass

    def setOverlayElements(self):
        """
        This method allows to time the placement of the 
        overlay elements defined within the artist. For 
        now this corresponds to the legend and the 
        pointer
        """
        self.pointer = Pointer(self.canvas)
        self.legend = Legend(self.canvas)

    def handleOverlayMouseTaken(self):
        """
        Manage the overlay owning the mouse. This can be interesting
        for removing obstructing visual elements in this case
        """
        pass

    def handleOverlayMouseReleased(self):
        """
        Manage the overlay owning the mouse. This can be interesting
        for removing obstructing visual elements in this case
        """
        pass

    def addPlot(self, name_type, *args, **kwargs):
        """
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        """
        active_handlers = [
            child.name for child in
            self.canvas.plotModel().root().children()]

        if name_type not in active_handlers:
            new_child = get_main_handler(name_type)
            self.canvas.plotModel().insertRows(
                len(self.canvas.plotModel().root().children()), 1,
                [new_child], self.canvas.plotModel().root())

        active_handlers = [
            child.name for child in
            self.canvas.plotModel().root().children()]

        output = self.canvas.plotModel().root().children()[
            active_handlers.index(name_type)].addChild(*args, **kwargs)

        self.canvas.plotModel().referenceModel()

        # if self.artist_type == '2D':
        #     output.draw(self.canvas)
        # elif self.artist_type == '3D':
        #     output.drawGL(self.canvas)

        return output

    def addItem(self, name_type, *args, **kwargs):
        """
        """
        active_handlers = [
            child.name for child in
            self.canvas.plotModel().root().children()]

        if not "Items" in active_handlers:
            new_child = get_main_handler("Items")
            self.canvas.plotModel().insertRows(0, 1, [new_child], self.canvas.plotModel().root())

        active_handlers = [
            child.name for child in
            self.canvas.plotModel().root().children()]

        output = self.canvas.plotModel().root().children()[
            active_handlers.index("Items")].addChild(name_type, *args, **kwargs)

        self.canvas.plotModel().referenceModel()

        return output

    def addFromDrop(self, file_paths):
        """
        """
        for file_path in file_paths:
            if file_path.split('.')[-1] == 'txt':
                data = np.loadtxt(file_path).transpose()
            elif file_path.split('.')[-1] == "npy":
                data = np.fromfile(file_path).transpose()

            shape = data.shape
            if len(shape) == 1:
                item = self.addPlot(
                    'Scatter',
                    Name=file_path.split('.')[-2].split(os.path.sep)[-1],
                    y=data[0],
                    Style=['-', 'o', 10])

            elif len(shape) == 2:
                item = self.addPlot(
                    'Scatter',
                    Name=file_path.split('.')[-2].split(os.path.sep)[-1],
                    x=data[0], y=data[1],
                    Style=['-', 'o', 10])

            elif len(shape) == 1:
                item = self.addPlot('Scatter',
                                    Name=file_path.split('.')[-2].split(os.path.sep)[-1],
                                    x=data[0], y=data[1], error=data[2],
                                    Style=['-', 'o', 10])

            if self.artist_type == '2D':
                item.draw(self.canvas)
            elif self.artist_type == '3D':
                item.drawGL(self.canvas)

    def removePlot(self, plot_item):
        """
        Remove an item from the handlers
        """
        plot_item.removeItems()
        self.canvas.plotModel().removeRows(
            plot_item.parent().children().index(plot_item),
            1, plot_item.parent())

    def removeItem(self, plot_item):
        """
        Remove an item from the handlers
        """
        plot_item.removeItems()
        self.canvas.plotModel().removeRows(
            plot_item.parent().children().index(plot_item),
            1, plot_item.parent())

    def dispatchPlotDataChange(self, index):
        """

        """

    def draw(self):
        """
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        """
        self.removeItems()
        for plot_handler in self.canvas.plotModel().root().children():
            plot_handler.draw(self.canvas)

    def removeItems(self):
        """
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        """
        for plot_handler in self.canvas.plotModel().root().children():
            plot_handler.removeItems()

    def clear(self):
        """
        Interactive plotting software needs the
        ability to clear the current content. This is 
        done here by asking everyone to be deleted...
        """
        for plot_handler in self.canvas.plotModel().root().children():
            plot_handler.clear(self.canvas)

    def addHistogramItem(self, location, item):
        """
        Put a histogram on the layout
        The location is a string that will 
        indicate the four possible options.

        Parameters
        ----------
        location : str
            The location of the hist, left, right top, bottom

        item: Q item
            The item that should be linked 
        """
        locations = {
            'left': [1, 0],
            'top': [0, 1],
            'bottom': [2, 1],
            'right': [1, 2]}

        self.canvas.grid_layout.addWidget(
            item,
            locations[location][0],
            locations[location][1])

        self.canvas._setBackground()
