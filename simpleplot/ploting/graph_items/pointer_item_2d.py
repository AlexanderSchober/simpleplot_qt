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
from ..graph_views_3D.pointer_view_2d  import PointerView2D

class PointerItem2D(GraphicsItem): 
    def __init__(self, parent, canvas, axis_items):
        super().__init__('Pointer', transformer=False, parent=parent)
        self.canvas = canvas
        self._fonts = getFontPaths()
        self._axis_items = axis_items
        self._pointer_view = None

    def initialize(self):
        '''
        '''
        self._pointer_view = PointerView2D()
        self.canvas.view.addGraphItem(self._pointer_view)

        self.addParameter(
            'Active',  True,
            method = self.setParameters)

        self.addParameter(
            'Thickness', 2.,
            method = self.setParameters)

        self.addParameter(
            'Size', 20.,
            method = self.setParameters)
        
        self.addParameter(
            'Color', QtGui.QColor(0, 0, 0, 255),
            method = self.setParameters)
        
        self.addParameter(
            'Label',
            [True, 16, QtGui.QColor('black'), True, QtGui.QColor.fromRgbF(0,0,0,0.2)],
            names=['Draw', 'Size', 'Color','Draw Backg.', 'Background'],
            method=self.setParameters)
        
        self.addParameter(
            'Label font', self.font().family() if self.font().family() != 'MS Shell Dlg 2' else 'Arial',
            choices=[key for key in self._fonts.keys()],
            method=self.setParameters)

        self.addParameter(
            'Label scientific',
            [True, 4, True, 4],
            choices=[key for key in self._fonts.keys()],
            method=self.setParameters)

        
        self.setParameters()
        self.bindPointer()

    def setParameters(self)->None:
        '''
        '''
        parameters = {}
        parameters['draw_pointer']        = self['Active']
        parameters['pointer_thickness']   = np.array([self['Thickness']])
        parameters['pointer_size']        = np.array([self['Size']])
        parameters['pointer_color']       = np.array(self['Color'].getRgbF())
        
        parameters['draw_label']          = self['Label'][0]
        parameters['label_color']         = np.array(self['Label'][2].getRgbF())
        parameters['draw_label_box']      = np.array([int(self['Label'][3])])
        parameters['label_box_color']     = np.array(self['Label'][4].getRgbF())
        
        parameters['label_sci']            = [self['Label scientific'][0], self['Label scientific'][2]]
        parameters['label_sci_prec']       = [self['Label scientific'][1], self['Label scientific'][3]]
        
        self._pointer_view.setLabelFont(self['Label font'], self['Label'][1])
        self._pointer_view.setProperties(**parameters)

    def refreshAuto(self):
        '''
        '''
        self.setParameters()
        
    def bindPointer(self):
        '''
        Binds the cursor to the system signals of th
        mouse 
        '''
        self.canvas.mouse.bind('move', self._pointer_view.setPosition, 'pointer_move')

    def unbindPointer(self):
        '''
        Binds the cursor to the system signals of the
        mouse 
        '''
        self.canvas.mouse.unbind('move', 'pointer_move')
