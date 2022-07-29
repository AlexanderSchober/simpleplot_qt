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
import numpy as np

from simpleplot.artist.artist import Artist
from simpleplot.artist.camera_3d import Camera3D
from simpleplot.artist.light import LightSource
from simpleplot.artist.space import SpaceRepresentation
from simpleplot.models.session_node import SessionNode
from simpleplot.plotting.graph_items.axes_item_3d import AxesItem3D
from simpleplot.plotting.graph_items.axes_orientation_item_3D import AxesOrientationItem3D
from simpleplot.plotting.graph_items.grid_item_3D import GridItem3D


class Artist3DNode(SessionNode, Artist):
    """
    This is the 2D artist manager, which can be seen as
    the subplot reference. It is linked to the drawing region
    and all plot elements.
    """

    def __init__(self, parent=None, canvas=None):
        SessionNode.__init__(self, 'Artist', parent)
        Artist.__init__(self, canvas)

        # set initial members
        self.canvas = canvas
        self.plot_handlers = []
        self.artist_type = '3D'
        self.camera = Camera3D(canvas)
        self.space = SpaceRepresentation()
        self.space.setCamera(self.camera)
        self.light = LightSource(canvas)
        self.connect()

        # Init all members in __init__
        self.axes = None
        self.orientation = None
        self.grid = None

    def setUpGraphItems(self):
        """
        this will help setting up the graph items
        after the artists has been initialised such as the
        camera dn the light
        """
        self.axes = AxesItem3D(self.canvas)
        self.orientation = AxesOrientationItem3D(self.canvas)
        self.grid = GridItem3D(self.axes._axes_list, self.canvas)

        self.addChild(self.axes)
        self.addChild(self.orientation)
        self.addChild(self.grid)

    def connect(self):
        """
        Connect the methods
        """
        self.canvas.widget.drop_success.connect(self.addFromDrop)
        self.canvas.view.rayUpdate.connect(self.processRay)
        self.canvas.plotModel().dataChanged.connect(self.dispatchPlotDataChange)

    def disconnect(self):
        """
        Disconnect the methods
        """
        self.canvas.widget.drop_success.disconnect(self.addFromDrop)
        self.canvas.view.rayUpdate.disconnect(self.processRay)
        self.canvas.plotModel().dataChanged.disconnect(self.dispatchPlotDataChange)

    def dispatchPlotDataChange(self, index):
        """
        Send to the adequate elements that the plot data has changed
        and thus the some things have to be done
        """

        if (self.canvas.plotModel().itemAt(index) is not None
                and self.canvas.plotModel().itemAt(index).name in ['Data', 'Transform']):
            self.axes.refreshAuto()
            self.grid.refreshAuto()

    def draw(self):
        """
        This method will go through the plot handlers
        and check if one of them has already the
        selected items. if not a new instance will be
        generated and then fed into the handler system
        """
        for plot_handler in self.canvas.plotModel().root().children():
            plot_handler.draw(self.canvas)

        self.axes.refreshAuto()
        self.grid.refreshAuto()

    def redrawOverlay(self):
        """
        Redraw items that have been put onto the
        overlay of the plot widget
        """
        pass

    def setOverlayElements(self):
        """
        This nethod allows to time the placement of the
        overlay elements defined within the artist. For
        now this corresponds to the legend and the
        pointer
        """
        pass
        # self.legend     = Legend(self.canvas)

    def set_mode(self, idx):
        """
        Once all elements are created it is possible
        to set up the functionalities.
        """
        pass

    def processRay(self):
        """
        Will try to Manage the items and their
        ray tracing position calculation
        """
        hits = []
        for child in self.canvas.plotModel().root().children():
            hits += child.processRay(self.canvas.view.mouse_ray)

        if not len(hits) == 0:
            distances = np.array([
                np.linalg.norm(e[0] - self.canvas.view.mouse_ray[0])
                for e in hits])

            idx = np.argmin(distances)
            hits[idx][1].dispatchCoordinate()
            hits[idx][1].parent().processProjection(
                x=hits[idx][0][0],
                y=hits[idx][0][1])
            self.canvas.mouse.transmitMotion(
                hits[idx][0][0],
                hits[idx][0][1])

            self.canvas.multi_canvas.bottom_selector.label.setText(
                str(
                    "  x = %" + str(3)
                    + "f, y = %" + str(3)
                    + "f, z = %" + str(3) + "f "
                    + hits[idx][1].parent().name) % (
                    hits[idx][0][0],
                    hits[idx][0][1],
                    hits[idx][0][2]))
