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

# General imports
import numpy as np

from simpleplot.dialogs.gradient_dialog import GradientPackage

# Personal imports
from ..graphics_items.graphics_item import GraphicsItem
from ..plot_views_3D.surface_view_3D import SurfaceView3D

class SurfacePlot(GraphicsItem): 
    '''
    This is a derivative of the GrahicsItem class
    that will handle the drawing of a surface plot 
    either on a 2D or 3D OpenGl canvas
    '''
    def __init__(self,*args, **kwargs):
        '''
        Initialisation of the class and super class

        Parameters:
        -------------------
        *args : -
            These are the arguments of the class
        **kwargs : -
            These are the keyword arguments of the class
        '''
        super().__init__('Surface', *args, transformer = False,**kwargs)

        self.initializeMain(**kwargs)
        self.initialize(**kwargs)
        self.initializeVisual2D(**kwargs)
        self.initializeVisual3D(**kwargs)
        self._mode = '2D'
        self.draw_items = [SurfaceView3D()]

    def initialize(self, **kwargs):
        '''
        This initializes the ParameterClass specifictions
        in the inherited item
        
        Parameters:
        -------------------
        **kwargs : -
            These are the keyword arguments if needed
        '''
        positions = [0,.25,0.5,0.75,1.]
        colors = [
            [0.,1.,1., 1.],
            [0.,0.,1., 1.],
            [0.,1.,0., 1.],
            [1.,0.,0., 1.],
            [1.,0.,1., 1.]
            ]
        state = [[positions[i], colors[i]] 
            for i in range(len(colors))]
        self._gradient_item  = GradientPackage(state)

        self.addParameter(
            'Gradient', self._gradient_item, 
            method = self.setColor, 
            tags = ['3D'])
        
    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        parameters = {}
        parameters['drawFaces']     = self['Draw faces']
        parameters['drawEdges']     = self['Draw edges']
        self.draw_items[0].setProperties(**parameters)

    def setColor(self):
        '''
        Set the visual of the given shape element
        '''
        state       = self['Gradient'].gradientList()
        positions   = [element[0] for element in state]
        colors      = [element[1] for element in state]

        parameters = {}
        parameters['colors']            = np.array(
            [c for _,c in sorted(zip(positions, colors))])
        parameters['color_positions']   = np.array(
            sorted(positions))

        self.draw_items[0].setColors(**parameters)

    def setPlotData(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        data = self.parent()._plot_data.getMesh()
        self.draw_items[0].setData(vertices = data[0], faces = data[1])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view.view
            self.setCurrentTags(['3D'])

        if self['Visible']:
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData()
            self.setColor()
            self.setVisual()
