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
from PyQt5 import QtGui
import numpy as np

#import personal dependencies
from ..graphics_items.graphics_item import GraphicsItem
from ..graph_views_3D.font_to_bitmap import getFontPaths
from ..graph_views_3D.legend_view  import LegendView

class LegendItem(GraphicsItem): 
    def __init__(self, parent, canvas):
        super().__init__('Legend', transformer=False, parent=parent)
        self.artist = parent
        self.canvas = canvas
        self._fonts = getFontPaths()

    def initialize(self):
        '''
        '''
        self._legend_view = LegendView()
        self.canvas.view.addGraphItem(self._legend_view)

        self.addParameter(
            'Active', True,
            method = self.setParameters)
        
        self.addParameter(
            'Position (edge)',
            [100, 100],
            method = self.setParameters)

        self.addParameter(
            'Icon size',
            [15, 15],
            names=['width', 'heigh'],
            method = self.setParameters)

        self.addParameter(
            'Font',
            self.font().family() if self.font().family() != 'MS Shell Dlg 2' else 'Arial',
            choices=[key for key in self._fonts.keys()],
            method = self.setParameters)
        
        self.addParameter(
            'Font size',
            12,
            method = self.setParameters)
        
        self.addParameter(
            'Text color', 
            QtGui.QColor('black'),
            method = self.setParameters)
        
        self.addParameter(
            'Background color',
            QtGui.QColor.fromRgbF(0.8,0.8,0.8,0.8),
            method = self.setParameters)
        
        self.addParameter(
            'Outer margins',
            [5, 5, 5, 5],
            names=['Left', 'Top', 'Right', 'Bottom'],
            method = self.setParameters)

        self.addParameter(
            'Grid margin h',
            5,
            method = self.setParameters)
        
        self.addParameter(
            'Grid margin v',
            2,
            method = self.setParameters)

    def setParameters(self)->None:
        '''
        '''
        parameters = {}
        parameters['draw_legend']        = self['Active']
        parameters['legend_font']        = self['Font']
        parameters['legend_font_size']   = self['Font size']
        parameters['legend_margins']     = self['Outer margins']
        parameters['legend_margin_h']    = self['Grid margin h']
        parameters['legend_margin_v']    = self['Grid margin v']
        parameters['legend_back_color']  = np.array(self['Background color'].getRgbF())*256
        parameters['legend_text_color']  = np.array(self['Text color'].getRgbF())*256
        parameters['legend_dist_edge']   = self['Position (edge)']

        self._legend_view.setProperties(**parameters)
        self.buildLegend()

    def refreshAuto(self):
        '''
        '''
        self.setParameters()
        
    def bindPointer(self):
        '''
        Binds the cursor to the system signals of th
        mouse 
        '''
        self.canvas.mouse.bind('move', self._legend_view.setPosition, 'pointer_move')

    def unbindPointer(self):
        '''
        Binds the cursor to the system signals of the
        mouse 
        '''
        self.canvas.mouse.unbind('move', 'pointer_move')

    def buildLegend(self):
        '''
        Build the legend item
        '''
        icons = []
        titles = []
    
        for plot_handler in self.canvas._plot_root._children:
            for element in plot_handler._children:
                if hasattr(element, 'legendItems'):
                    icon_val = element.legendItems(*self['Icon size'])
                    if icon_val is None:
                        continue
                    icons.append(icon_val)
                    titles.append(element._name)

        self._legend_view.setLegend(icons, titles)
        

            