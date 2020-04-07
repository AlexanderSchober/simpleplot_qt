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

from PyQt5 import QtGui, QtCore, QtWidgets

from ..pointer.pointer  import Pointer
from ..pointer.zoomer   import Zoomer
from ..pointer.measurer import Measurer
from .axes              import Axes
from .axes_gl           import Axes3D
from .legend            import Legend
from .grid_gl           import GridGl
from ..models.session_node import SessionNode

from ..ploting.main_handler import get_main_handler
from ..pyqtgraph import pyqtgraph as pg

from copy import deepcopy
import numpy as np
import os

class Artist():
    '''
    '''
    def __init__(self, canvas = None):

        self.canvas         = canvas
        self.artist_type    = '2D'
        self.child_widgets  = []
        self.draw_surface   = None
        
    def connect(self):
        '''
        Template to be overwritten
        '''

    def disconnect(self):
        '''
        Template to be overwritten
        '''

    def addPlot(self, name_type, *args, **kwargs):
        '''
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        '''
        active_handlers = [
            child._name for child in 
            self.canvas._plot_root._children]

        if not name_type in active_handlers:
            new_child = get_main_handler(name_type)
            self.canvas._plot_model.insertRows(
                len(self.canvas._plot_root._children), 1, 
                [new_child], self.canvas._plot_root)

        active_handlers = [
            child._name for child in 
            self.canvas._plot_root._children]

        output = self.canvas._plot_root._children[
            active_handlers.index(name_type)].addChild(*args, **kwargs)

        self.canvas._plot_model.referenceModel()

        return output

    def addItem(self, name_type, *args, **kwargs):
        '''
        '''
        active_handlers = [
            child._name for child in 
            self.canvas._plot_root._children]

        if not "Items" in active_handlers:
            new_child = get_main_handler("Items")
            self.canvas._plot_model.insertRows(0, 1, [new_child], self.canvas._plot_root)

        active_handlers = [
            child._name for child in 
            self.canvas._plot_root._children]

        output = self.canvas._plot_root._children[
            active_handlers.index("Items")].addChild(name_type,*args, **kwargs)

        self.canvas._plot_model.referenceModel()

        return output

    def addFromDrop(self, file_paths):
        '''
        '''
        for file_path in file_paths:
            if file_path.split('.')[-1] == 'txt':
                data = np.loadtxt(file_path).transpose()
            elif file_path.split('.')[-1] == "npy":
                data = np.fromfile(file_path).transpose()

            shape = data.shape
            if len(shape) == 1:
                item = self.addPlot(
                    'Scatter',
                    Name = file_path.split('.')[-2].split(os.path.sep)[-1], 
                    y = data[0],
                    Style = ['-','o',10])

            elif len(shape) == 2:
                item = self.addPlot(
                    'Scatter',
                    Name = file_path.split('.')[-2].split(os.path.sep)[-1], 
                    x = data[0], y = data[1],
                    Style = ['-','o',10])

            elif len(shape) == 1:
                item = self.addPlot('Scatter',
                Name = file_path.split('.')[-2].split(os.path.sep)[-1], 
                x = data[0], y = data[1], error = data[2],
                    Style = ['-','o',10])

        
            if self.artist_type == '2D':
                item.draw(self.canvas)
            elif self.artist_type == '3D':
                item.drawGL(self.canvas)

    def removePlot(self,plot_item):
        '''
        Remove an item from the handlers
        '''
        plot_item.removeItems()
        self.canvas._plot_model.removeRows(
            plot_item.parent()._children.index(plot_item),
            1, plot_item.parent())

    def removeItem(self,plot_item):
        '''
        Remove an item from the handlers
        '''
        plot_item.removeItems()
        self.canvas._plot_model.removeRows(
            plot_item.parent()._children.index(plot_item),
            1, plot_item.parent())

    def dispatchPlotDataChange(self, index):
        '''

        '''

    def draw(self):
        '''
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        '''
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.removeItems()
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.draw(self.canvas)

    # def redraw(self):
    #     '''
    #     This method will go through the plot handlers
    #     and check if one of them has already the 
    #     selected items. if not a new instance will be
    #     generated and then fed into the handler system
    #     '''
    #     for plot_handler in self.plot_handlers:
    #         plot_handler.draw(self.canvas)

    def clear(self):
        '''
        Interactive plotting software needs the
        ability to clear the current content. This is 
        done here by asking everyone to be deleted...
        '''
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.clear(self.canvas)

    def addHistogramItem(self, location, item):
        '''
        Put a histogram on the layout
        The location is a string that will 
        indicate the four possible options.

        Parameters
        ----------
        location : str
            The location of the hist, left, right top, bottom

        item: Q item
            The item that should be linked 
        '''
        locations = {
            'left'  : [1,0],
            'top'   : [0,1],
            'bottom': [2,1],
            'right' : [1,2]}

        self.canvas.grid_layout.addWidget(
            item,
            locations[location][0],
            locations[location][1])

        self.canvas._setBackground()
        
class Artist2DNode(SessionNode, Artist):
    '''
    This is the 2D artist manager, which can be seen as
    the subplot reference. It is linked to the drawing region
    and all plot elements.
    '''

    def __init__(self,name = '', parent = None,  canvas = None):

        #internal element identifier
        SessionNode.__init__(self, name, parent)
        Artist.__init__(self)

        self.canvas         = canvas
        self.plot_handlers  = []
        self.artist_type    = '2D'

        self.axes       = Axes(self.canvas)
        # self.mouse      = Mouse(self.canvas)
        # self.Keyboard   = KeyboardClass.Keyboard(self.Canvas,Multi = self.Multi)
        self.pointer    = Pointer(self.canvas)
        self.zoomer     = Zoomer(self.canvas)
        self.measurer   = Measurer(self.canvas)
        self.legend     = Legend(self.canvas)
        # self.Modifier   = ModificationClass.Modify(self.Canvas)
        # self.Title      = None #TitleClass.TitleClass(self.Canvas)
        self.connect()
        
    def connect(self):
        '''
        Connect the methods
        '''
        self.canvas._plot_model.dataChanged.connect(self.dispatchPlotDataChange)
        self.canvas.widget.drop_success.connect(self.addFromDrop)

    def disconnect(self):
        '''
        Disconnect the methods
        '''
        self.canvas._plot_model.dataChanged.disconnect(self.dispatchPlotDataChange)
        self.canvas.widget.drop_success.disconnect(self.addFromDrop)

    def dispatchPlotDataChange(self, index):
        '''
        Send to the adequate elements that the plot data has changed
        and thus the some things have to be done
        '''
        if not self.canvas._plot_model.itemAt(index) is None and self.canvas._plot_model.itemAt(index)._name == 'Data':
            self.pointer.refreshPlotData()
            self.zoomer.zoom()
            self.legend.buildLegend()

    def draw(self):
        '''
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        '''
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.draw(self.canvas)

        self.legend.tearLegendDown()
        self.legend.buildLegend()
        self.zoomer.zoom()

    def redraw(self):
        '''
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        '''
        for plot_handler in self.plot_handlers:
            plot_handler.draw(self.canvas)
        self.zoomer.zoom()

    def clear(self):
        '''
        Interactive plotting software needs the
        ability to clear the current content. This is 
        done here by asking everyone to be deleted...
        '''
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.clear(self.canvas)

        self.legend.tearLegendDown()

    def setup(self):
        '''
        Once all elements are created it is possible 
        to set up the functionalities. 
        '''
        try:
            self.pointer.unbindPointer()
        except:
            pass

        try:
            self.zoomer.quiet()
        except:
            pass

        self.pointer.bindPointer()
        self.zoomer.listen()

    def setMode(self, idx):
        '''
        Once all elements are created it is possible 
        to set up the functionalities. 
        '''
        self.zoomer.quiet()
        self.measurer.quiet()

        if idx == 0:
            self.zoomer.listen()

        elif idx == 1:
            self.measurer.listen()
        
    def _updateColors(self):
        '''
        Tell the plot item to update the colors
        of the surface plot item
        '''
        state       = self.gradient_widget.saveState()
        positions   = [element[0] for element in state['ticks']]
        colors      = [list(np.array(element[1])/255) for element in state['ticks']]
        colors      = [c for _,c in sorted(zip(positions, colors))]
        positions   = sorted(positions)

        self.canvas._plot_root.childFromName('Surface')
        for child in self.canvas._plot_root.childFromName('Surface')._children:
            child.setColor(colors, positions)

class Artist3DNode(SessionNode, Artist):
    '''
    This is the 2D artist manager, which can be seen as
    the subplot reference. It is linked to the drawing region
    and all plot elements.
    '''
    def __init__(self, name = '', parent = None,  canvas = None):
        SessionNode.__init__(self, name, parent)
        Artist.__init__(self, canvas)

        self.canvas         = canvas
        self.plot_handlers  = []
        self.artist_type    = '3D'

        self.grid = GridGl(canvas)
        self.axes = Axes3D(canvas)
        
        self.connect()

    def connect(self):
        '''
        Connect the methods
        '''
        self.canvas.widget.drop_success.connect(self.addFromDrop)
        self.canvas.view.rayUpdate.connect(self.processRay)
        self.canvas._plot_model.dataChanged.connect(self.dispatchPlotDataChange)

    def disconnect(self):
        '''
        Disconnect the methods
        '''
        self.canvas.widget.drop_success.disconnect(self.addFromDrop)
        self.canvas.view.rayUpdate.disconnect(self.processRay)
        self.canvas._plot_model.dataChanged.disconnect(self.dispatchPlotDataChange)

    def dispatchPlotDataChange(self, index):
        '''
        Send to the adequate elements that the plot data has changed
        and thus the some things have to be done
        '''

        if not self.canvas._plot_model.itemAt(index) is None and self.canvas._plot_model.itemAt(index)._name in ['Data', 'Transform']:
            self.axes.refreshAuto()
            self.grid.refreshAuto()

    def draw(self):
        '''
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new instance will be
        generated and then fed into the handler system
        '''
        for plot_handler in self.canvas._plot_root._children:
            plot_handler.draw(self.canvas)

        self.axes.refreshAuto()
        self.grid.refreshAuto()

    def setup(self):
        '''
        Once all elements are created it is possible 
        to set up the functionalities. 
        '''
        pass

    def set_mode(self, idx):
        '''
        Once all elements are created it is possible 
        to set up the functionalities. 
        '''
        pass

    def processRay(self):
        '''
        Will try to Manage the items and their 
        ray tracing position calculation
        '''
        hits = []
        for child in self.canvas._plot_root._children:
            hits += child.processRay(self.canvas.view.mouse_ray)
        
        if not len(hits) == 0:
            distances = np.array([
                np.linalg.norm(e[0] - self.canvas.view.mouse_ray[0]) 
                for e in hits])

            idx = np.argmin(distances)
            hits[idx][1].dispatchCoordinate()
            hits[idx][1].parent().processProjection(
                x = hits[idx][0][0], 
                y = hits[idx][0][1])
            self.canvas.mouse.transmitMotion(
                hits[idx][0][0], 
                hits[idx][0][1])

            self.canvas.multi_canvas.bottom_selector.label.setText(
                str(
                    "  x = %"+str(3)+"f"
                    ", y = %"+str(3)+"f"
                    ", z = %"+str(3)+"f"
                    " "+hits[idx][1].parent()._name)%(
                        hits[idx][0][0],
                        hits[idx][0][1],
                        hits[idx][0][2]))
        