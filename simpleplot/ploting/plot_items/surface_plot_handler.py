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

from PyQt5 import QtGui
from copy import deepcopy
import numpy as np
from scipy.spatial.distance import pdist

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl
from ..plot_geometries.shaders      import ShaderConstructor
from ..plot_data_types.surface_data import SurfaceData
from ...model.node                  import SessionNode

from .surface_plot      import SurfacePlot
from .isosurface_plot   import IsoCurvePlot

class SurfacePlotHandler(SessionNode): 
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, x = None, y = None, z = None, **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.

        Parameters
        -----------
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        SessionNode.__init__(self, 'No_name')
        self.add_options    = ['Isocurve', 'Projection']

        self._plot_data     = SurfaceData(x = x, y = y, z = z)
        self.addChild(self._plot_data)

        self.addChild(SurfacePlot(**kwargs))
        self.addChild(IsoCurvePlot(**kwargs))

    def __getitem__(self, value):
        '''
        return the items that are in the 
        current base.
        '''
        return self.childFromName(value)

    def setData(self, **kwargs):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        self['Data'].setData(**kwargs)
        
        for child in self._children:
            if hasattr(child, 'refresh'):
                child.refresh()

    def draw(self, target_surface = None):
        '''
        Draw the objects on a 2D canvas
        '''
        for child in self._children:
            if hasattr(child, 'draw'):
                child.draw(target_surface)

    def drawGL(self, target_view = None):
        '''
        Draw the objects on a 3D canvas
        '''
        for child in self._children:
            if hasattr(child, 'drawGL'):
                child.drawGL(target_view)

    def removeItems(self):
        '''
        '''
        for child in self._children:
            if hasattr(child, 'removeItems'):
                child.removeItems()
