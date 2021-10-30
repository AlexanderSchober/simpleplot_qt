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

from functools import partial

import numpy as np
from PyQt5 import QtGui

from ..graph_views_3D.axis_view_2d import AxisView2D
from ..graph_views_3D.font_to_bitmap import getFontPaths
from ..graphics_items.graphics_item import GraphicsItem
from ...models.parameter_class import ParameterHandler


class AxesItem2D(GraphicsItem):
    """
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    """

    def __init__(self, parent, canvas):
        super().__init__('Axes', transformer=False, parent=parent)
        self.canvas = canvas
        self._fonts = getFontPaths()
        self._main_handler = ParameterHandler(name='Common', parent=self)
        self._handlers = [
            ParameterHandler(name='X bottom', parent=self),
            ParameterHandler(name='X top', parent=self),
            ParameterHandler(name='Y left', parent=self),
            ParameterHandler(name='Y right', parent=self),
        ]

        self._positions = ['bottom', 'top', 'left', 'right']
        self._directions = [[0, 1, 0], [0, 1, 0], [1, 0, 0], [1, 0, 0]]
        self._tick_directions = [[0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0]]
        self._colors = ['black', 'black', 'black', 'black']
        self._edge_color = 'white'
        self._angles = [0, 0, 90, -90]
        self._angles_labels = [0, 0, 0, 0]
        self._center_choices = [['Center', 'Left', 'Right'], ['Center', 'Top', 'Bottom']]
        self._center_labels = [['Center', 'Center', 'Right', 'Left'], ['Bottom', 'Top', 'Center', 'Center']]
        self._axes_list = []

    def initialize(self):
        """
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any
        default parameters.
        """
        self._main_handler.addParameter(
            'Margins (px)',
            [60, 60, 40, 40],
            names=['Left', 'Bottom', 'Right', 'Top'],
            method=self.refreshAuto)

        self._main_handler.addParameter(
            'Edge color', QtGui.QColor(self._edge_color),
            method=partial(self.refreshAuto))

        for i, pos in enumerate(self._positions):
            self._axes_list.append(AxisView2D())
            self.canvas.view.addGraphItem(self._axes_list[-1])
            self._axes_list[-1].setProperties(axis_pos=pos)

            self._handlers[i].addParameter(
                'Visible', [
                    True if pos in ['bottom', 'left'] else False,
                    True if pos in ['bottom', 'left'] else False,
                    True if pos in ['bottom', 'left'] else False,
                    True if pos in ['bottom', 'left'] else False,
                    True],
                names=['Axis', 'Ticks', 'Values', 'Title', 'edge'],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis visual',
                [QtGui.QColor(self._colors[i]), 5],
                names=['Color', 'Thickness'],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Tick visual',
                [QtGui.QColor(self._colors[i]), 3, 20, True],
                names=['Color', 'Thickness', 'Length', 'Small ticks'],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis title',
                ['No Title', 15, 20, QtGui.QColor('black'), self._angles[i]],
                names=['Title', 'Size', 'Position', 'Color', 'Angle'],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis title font', self.font().family() if self.font().family() != 'MS Shell Dlg 2' else 'Arial',
                choices=[key for key in self._fonts.keys()],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis title justify vertical', 'Center',
                choices=self._center_choices[1],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis title justify horizontal', 'Center',
                choices=self._center_choices[0],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis label',
                [11, 15, QtGui.QColor('black'), self._angles_labels[i]],
                names=['Size', 'Position', 'Color', 'Angle'],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis label font', self.font().family() if self.font().family() != 'MS Shell Dlg 2' else 'Arial',
                choices=[key for key in self._fonts.keys()],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis label justify vertical', self._center_labels[1][i],
                choices=self._center_choices[1],
                method=partial(self.setParameters, i))

            self._handlers[i].addParameter(
                'Axis label justify horizontal', self._center_labels[0][i],
                choices=self._center_choices[0],
                method=partial(self.setParameters, i))

        for i in range(len(self._handlers)):
            self.setParameters(i)

    def setParameters(self, i: int) -> None:
        """
        Set the parameters of the axis items
        """
        handler = self._handlers[i]
        parameters = {'draw_axis': handler['Visible'][0],
                      'draw_ticks': handler['Visible'][1],
                      'draw_values': handler['Visible'][2],
                      'draw_title': handler['Visible'][3],
                      'draw_edge': handler['Visible'][4],

                      'axis_widths': np.array([item['Axis visual'][1]
                                               for item in self._handlers]),
                      'axis_color': np.array(handler['Axis visual'][0].getRgbF()),
                      'axis_margins': np.array(self._main_handler['Margins (px)']),
                      'tick_length': np.array(handler['Tick visual'][2]),
                      'tick_width': np.array(handler['Tick visual'][1]),
                      'tick_color': np.array(handler['Tick visual'][0].getRgbF()),
                      'tick_direction': np.array(self._tick_directions[i]),
                      'small_ticks': np.array(self._tick_directions[i]),

                      'title_position': np.array(handler['Axis title'][2]),
                      'title_color': np.array(handler['Axis title'][3].getRgbF()),
                      'title_angle': np.array(handler['Axis title'][4]),
                      'title_v_just': np.array(self._center_choices[1].index(handler['Axis title justify vertical'])),
                      'title_h_just': np.array(self._center_choices[0].index(handler['Axis title justify horizontal'])),

                      'label_position': np.array(handler['Axis label'][1]),
                      'label_color': np.array(handler['Axis label'][2].getRgbF()),
                      'label_angle': np.array(handler['Axis label'][3]),
                      'label_v_just': np.array(self._center_choices[1].index(handler['Axis label justify vertical'])),
                      'label_h_just': np.array(self._center_choices[0].index(handler['Axis label justify horizontal'])),

                      'edge_color': np.array(self._main_handler['Edge color'].getRgbF())
                      }

        self._axes_list[i].setTitle(handler['Axis title'][0], handler['Axis title font'], handler['Axis title'][1])
        self._axes_list[i].setLabelFont(handler['Axis label font'], handler['Axis label'][0])
        self._axes_list[i].setProperties(**parameters)

    def refreshAuto(self):
        """
        refresh the axes automatically
        based on the content
        """
        for i in range(len(self._axes_list)):
            self.setParameters(i)

    def refreshAutoAxis(self, i: int):
        """
        refresh the axes automatically
        based on the content
        """
        pass
        # if self._handlers[i]['Axis range'][0]:
        #
        #     bounds = [[1.e2, -1.e2], [1.e2, -1.e2], [1.e2, -1.e2]]
        #     for child in self.canvas._plot_root._children:
        #         for plot_child in child._children:
        #             if hasattr(plot_child, '_plot_data'):
        #                 new_bounds = plot_child._plot_data.getDrawBounds()
        #                 bounds = [
        #                     [
        #                         min(bounds[0][0], new_bounds[0][0]),
        #                         max(bounds[0][1], new_bounds[0][1])],
        #                     [
        #                         min(bounds[1][0], new_bounds[1][0]),
        #                         max(bounds[1][1], new_bounds[1][1])],
        #                     [
        #                         min(bounds[2][0], new_bounds[2][0]),
        #                         max(bounds[2][1], new_bounds[2][1])]]
        #
        #     self._handlers[i].items['Axis position'].updateValue([
        #         float(bounds[0][0]),
        #         float(bounds[1][0]),
        #         float(bounds[2][0])],
        #         method=False)
        #     self._handlers[i].items['Axis range'].updateValue(
        #         [True, 0, float(bounds[i][1] - bounds[i][0])],
        #         method=False)
        #
        # self.setParameters(i)
        #
        # if not self.parent() is None:
        #     self.parent().childFromName('Grids').refreshAuto()
