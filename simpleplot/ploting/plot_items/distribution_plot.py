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

# Personal imports
from ..graphics_items.graphics_item import GraphicsItem
from ..plot_views_3D.distribution_view_3D import DistributionView3D

class DistributionPlot(GraphicsItem): 
    '''
    This class will be the scatter plots. 
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
        super().__init__('Surface', *args,transformer = False, **kwargs)

        self.initializeMain(**kwargs)
        self.initializeVisual2D(**kwargs)
        self.initializeVisual3D(**kwargs)
        self._mode = '3D'

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        if not hasattr(self, 'draw_items'):
            self.redraw()
            return

        if self._mode == '2D':
            pass

        elif self._mode == '3D':
            parameters = {}
            parameters['drawFaces']     = self['Draw faces']
            parameters['drawEdges']     = self['Draw edges']
            
            self.draw_items[0].setProperties(**parameters)

    def setPlotData(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        data = self.parent()._plot_data.getData()
        self.draw_items[0].setData(
            vertices    = data[0],
            colors      = data[1])

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self.removeItems()
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface.draw_surface.vb
            self.setCurrentTags(['2D'])

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
            self.draw_items = [DistributionView3D()]
            self.default_target.addItem(self.draw_items[-1])
            self.setPlotData()
            self.setVisual()
