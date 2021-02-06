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
# external dependencies
from PyQt5 import QtGui

from ..graph_views_3D.axis_view_2d import AxisView2D
# import dependencies
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
        self._axes_list = []

        # self.initialize()

    def initialize(self):
        """
        This method will initialize the axes. Note that
        unlike other methods the axes don't take any
        default parameters.
        """
        self._main_handler.addParameter(
            'Margins (px)',
            [40, 40, 20, 20],
            names=['Left', 'Bottom', 'Right', 'Top'],
            method=self.refreshAuto)

        for i, pos in enumerate(self._positions):
            self._axes_list.append(AxisView2D())
            self.canvas.view.addGraphItem(self._axes_list[-1])
            self._axes_list[-1].setProperties(axis_pos=pos)

            self._handlers[i].addParameter(
                'Visible', [
                    True if pos in ['bottom', 'left'] else False,
                    True if pos in ['bottom', 'left'] else False,
                    False,
                    True if pos in ['bottom', 'left'] else False],
                names=['Axis', 'Ticks', 'Values', 'Title'],
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
                ['No Title', QtGui.QFont(), 20, QtGui.QColor('black')],
                names=['Title', 'Font', 'Position', 'Color'],
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
                      'title_color': np.array(handler['Axis title'][3].getRgbF())
                      }

        self._axes_list[i].setTitle(*handler['Axis title'])
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
