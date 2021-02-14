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

from pathlib import Path

# General imports
from typing import Tuple

import moderngl
import numpy as np
# Personal imports
from PyQt5 import QtGui
from PyQt5.QtGui import QGuiApplication

from .font_to_bitmap import getFontPaths, Font
from .management.tick_management import tickValues, updateAutoSIPrefix
from ..views_3D.graphics_view_3D import GraphicsView3D

SI_PREFIXES = str('yzafpnµm kMGTPEZY')
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'


class AxisView2D(GraphicsView3D):
    def __init__(self, **opts):
        """
        """
        super().__init__(**opts)
        self._family_to_path = getFontPaths()
        self._initParameters()

    def _initParameters(self):
        """
        This is a placeholder for the parameter
        initialisation
        """
        self._orientations = ['bottom', 'top', 'right', 'left']
        self._tick_positions_1d = np.array([0, 0.5, 0.7, 1])
        self.texture_title = None
        self._cached_text = None

        self._parameters['draw_axis'] = True
        self._parameters['draw_ticks'] = True
        self._parameters['draw_values'] = False
        self._parameters['draw_title'] = False

        self._parameters['axis_widths'] = np.array([0.05, 0.05, 0.05, 0.05])
        self._parameters['axis_color'] = np.array([1, 0, 0, 1])
        self._parameters['axis_margins'] = np.array([20, 20, 20, 20])
        self._parameters['axis_pos'] = 'bottom'

        self._parameters['tick_length'] = np.array([10])
        self._parameters['tick_direction'] = np.array([0, 1, 0])
        self._parameters['tick_color'] = np.array([1, 0, 0, 1])
        self._parameters['tick_width'] = np.array([10])
        self._parameters['small_ticks'] = np.array([1])

        self._parameters['title_position'] = np.array([10])

    def initializeGL(self) -> None:
        """
        Initialize the OpenGl states
        """
        self._createProgram(
            "axis",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader('axis'),
            geometry_shader=self._geometryShader('axis'))

        self._createProgram(
            "ticks",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader('ticks'),
            geometry_shader=self._geometryShader('ticks'))

        self._createProgram(
            "labels",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader('labels'),
            geometry_shader=self._geometryShader('labels'))

        self._createProgram(
            "title",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader('title'))

        self.setUniforms(**self._parameters)
        self.setTitle('No title', QtGui.QFont())
        self._updateAxis()
        self.setMVP()
        self.setLight()

    def setProperties(self, **kwargs) -> None:
        """
        Set the properties to display the graph
        """
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._updateAxis()
        self.update()

    def setTitle(self, text: str, font: QtGui.QFont, *args) -> None:
        """
        This method will effectively build the texture for the text
        :param text: str, the text to set
        :param font: QtGui.QFont
        :return: None
        """
        font.setPixelSize(int(50))
        font_info = font.key().split(',')
        if self._cached_text is not None and self._cached_text[0] == text and self._cached_text[1] == font_info[0]:
            return

        freetype_font = Font(self._family_to_path[font_info[0]] if font_info[0] != 'MS Shell Dlg 2'
                             else self._family_to_path['Arial'], int(font_info[2]))
        freefont_dict = freetype_font.render_text(text)

        self.texture_title = self.context().texture(
            freefont_dict['bitmap'].shape, 1,
            (freefont_dict['bitmap'].astype('f4')/256).tobytes(),
            dtype='f4')

        self.texture_title.repeat_x = False
        self.texture_title.repeat_y = False
        self.texture_title.filter = (moderngl.LINEAR, moderngl.LINEAR)

        self._cached_text = [text, font_info[0]]

        self.setUniforms(
            position_row_title=freefont_dict['positions_rows'],
            positions_width_title=freefont_dict['positions_width'],
            char_width_title=freefont_dict['char_width'],
            char_index=freefont_dict['char_index'],
            limit=np.array([len(freefont_dict['char_index'])]),
            height=np.array([freetype_font.size]),
            factor_x=np.array([1/freefont_dict['bitmap'].shape[0], 1/freefont_dict['bitmap'].shape[1]])
        )

    def setTickFont(self, font: QtGui.QFont):
        """
        This will generate the font texture for the tick values.
        Only the following is required:
        0123456789
        -+_,()[]
        abcdefghijklm
        nopqrstuvwxyz
        ABCDEFGHIJKLM
        NOPQRSTUVWXYZ

        :param font:
        :return: None
        """

    def _updateAxis(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """
        tick_range = self._getTickValues()
        updateAutoSIPrefix(tick_range[0], tick_range[1])
        self._tick_positions_1d = tickValues(
            tick_range[0], tick_range[1],
            tick_range[1] - tick_range[0], 1)
        self.ticks_positions_3d = self._getTickPositions(self._tick_positions_1d)
        title_positions, title_parameters = self._getTitleParameters()

        self._createVBO("axis", self.getAxisPositions())
        self._createVAO("axis", {"axis": ["3f", "in_vert"]})
        self._createVBO("ticks", self.ticks_positions_3d)
        self._createVAO("ticks", {"ticks": ["3f", "in_vert"]})
        # self._createVAO("labels", {"ticks": ["3f", "in_vert"]})
        self._createVBO("title", title_positions)
        self._createVAO("title", {"title": ["3f", "in_vert"]})

        if self._parameters['axis_pos'] in ['bottom', 'top']:
            axis_thickness = self._parameters['axis_widths'][self._orientations.index(self._parameters['axis_pos'])] \
                             * float(self.renderer().camera().getPixelSize()[1])
            tick_thickness = self._parameters['tick_width'] * float(self.renderer().camera().getPixelSize()[0])
            tick_length = self._parameters['tick_length'] * float(self.renderer().camera().getPixelSize()[1])

        else:
            axis_thickness = self._parameters['axis_widths'][self._orientations.index(self._parameters['axis_pos'])] \
                             * float(self.renderer().camera().getPixelSize()[0])
            tick_thickness = self._parameters['tick_width'] * float(self.renderer().camera().getPixelSize()[1])
            tick_length = self._parameters['tick_length'] * float(self.renderer().camera().getPixelSize()[0])
        self.setUniforms(axis_thickeness=axis_thickness,
                         tick_thickness=tick_thickness,
                         tick_length=tick_length,
                         title_parameters=title_parameters)

    def _getTitleParameters(self) -> Tuple[np.array, np.array]:
        """

        :return: Tuple[np.array, np.array]
        """
        center = self._getTitleCenter()
        screen_size = self.renderer().camera()['Screen size']
        width = (self.texture_title.width) / screen_size[0] if screen_size[0] != 0 else 0
        height = (self.texture_title.height) / screen_size[1] if screen_size[1] != 0 else 0

        half_height = height / 2
        half_width = width / 2
        positions = np.array([
            [center[0] - half_width, center[1] - half_height, -1],
            [center[0] - half_width, center[1] + half_height, -1],
            [center[0] + half_width, center[1] - half_height, -1],
            [center[0] + half_width, center[1] + half_height, -1]
        ], dtype='f4')

        return positions, np.array([center[0], center[1], width, height], dtype="object")

    def _getTitleCenter(self) -> np.array:
        """
        Get the center position of the title depending
        on the axis location.
        :return:
        """
        axis_pos = self._parameters['axis_pos']
        cam_method = self.renderer().camera().getPixelScreenValue
        if axis_pos == 'bottom':
            return np.array([0., cam_method(0, self._parameters['title_position'])[1]], dtype="object")
        elif axis_pos == 'top':
            return np.array([0., cam_method(0, -self._parameters['title_position'])[1]], dtype="object")
        elif axis_pos == 'left':
            return np.array([cam_method(self._parameters['title_position'], 0)[0], 0.], dtype="object")
        elif axis_pos == 'right':
            return np.array([-cam_method(self._parameters['title_position'], 0)[0], 0.], dtype="object")
        else:
            return np.array([0., 0.])

    def getAxisPositions(self) -> np.array:
        """
        Gets the axis positions depending on the self._parameters['axis_pos']
        variable in the parameters
        :return: np.array
        """
        axis_pos = self._parameters['axis_pos']
        axis_margins = self._parameters['axis_margins']
        cam_method = self.renderer().camera().getPixelScreenValue
        if axis_pos == 'bottom':
            return np.array([
                list(cam_method(axis_margins[0] - self._parameters['axis_widths'][0] / 2, axis_margins[1])) + [0],
                list(cam_method(-axis_margins[2] + self._parameters['axis_widths'][2] / 2, axis_margins[1])) + [0]
            ])
        elif axis_pos == 'top':
            return np.array([
                list(cam_method(axis_margins[0] - self._parameters['axis_widths'][0] / 2, -axis_margins[3])) + [0],
                list(cam_method(-axis_margins[2] + self._parameters['axis_widths'][2] / 2, -axis_margins[3])) + [0]
            ])
        elif axis_pos == 'left':
            return np.array([
                list(cam_method(axis_margins[0], -axis_margins[3] - self._parameters['axis_widths'][3] / 2)) + [0],
                list(cam_method(axis_margins[0], axis_margins[1] + self._parameters['axis_widths'][0] / 2)) + [0]
            ])
        elif axis_pos == 'right':
            return np.array([
                list(cam_method(-axis_margins[2], -axis_margins[3] - self._parameters['axis_widths'][3] / 2)) + [0],
                list(cam_method(-axis_margins[2], axis_margins[1] + self._parameters['axis_widths'][0] / 2)) + [0]
            ])
        else:
            return np.array([
                list(cam_method(0, 0)) + [0],
                list(cam_method(1, 1)) + [0]
            ])

    def _getTickValues(self) -> np.array:
        """
        This function will determine the tick values to consider using
        the camera values and margins and return the limits
        :return:
        """
        axis_pos = self._parameters['axis_pos']
        axis_margins = self._parameters['axis_margins']
        x_range = self.renderer().camera()['Camera x range']
        y_range = self.renderer().camera()['Camera y range']
        screen_size = self.renderer().camera()['Screen size']

        if axis_pos in ['top', 'bottom']:
            return np.array([
                x_range[0] + (x_range[1] - x_range[0]) * axis_margins[0] / screen_size[0],
                x_range[1] - (x_range[1] - x_range[0]) * axis_margins[2] / screen_size[0]
            ]) if screen_size[0] > 0 else np.array([0, 1])
        else:
            return np.array([
                y_range[0] + (y_range[1] - y_range[0]) * axis_margins[1] / screen_size[1],
                y_range[1] - (y_range[1] - y_range[0]) * axis_margins[3] / screen_size[1]
            ]) if screen_size[1] > 0 else np.array([0, 1])

    def _getTickPositions(self, tick_values):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """
        axis_pos = self._parameters['axis_pos']
        axis_margins = self._parameters['axis_margins']
        x_range = self.renderer().camera()['Camera x range']
        y_range = self.renderer().camera()['Camera y range']
        delta_x = x_range[1] - x_range[0]
        delta_y = y_range[1] - y_range[0]
        screen_size = self.renderer().camera()['Screen size']

        ticks_positions_3d = np.zeros((tick_values.shape[0], 3))

        if axis_pos == 'bottom':
            ticks_positions_3d[:, 0] = (tick_values - x_range[0]) / delta_x * 2 - 1
            ticks_positions_3d[:, 1] = axis_margins[1] / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'top':
            ticks_positions_3d[:, 0] = (tick_values - x_range[0]) / delta_x * 2 - 1
            ticks_positions_3d[:, 1] = (screen_size[1] - axis_margins[3]) / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'left':
            ticks_positions_3d[:, 1] = (tick_values - y_range[0]) / delta_y * 2 - 1
            ticks_positions_3d[:, 0] = axis_margins[0] / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0
        elif axis_pos == 'right':
            ticks_positions_3d[:, 1] = (tick_values - y_range[0]) / delta_y * 2 - 1
            ticks_positions_3d[:, 0] = (screen_size[0] - axis_margins[2]) / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0

        return ticks_positions_3d

    def paint(self):
        """
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the labels
        """
        self.context().disable(moderngl.CULL_FACE)
        self._updateAxis()
        if self._parameters['draw_axis']:
            self._vaos['axis'].render(mode=moderngl.LINE_STRIP)

        if self._parameters['draw_ticks']:
            self._vaos['ticks'].render(mode=moderngl.POINTS)

        if self._parameters['draw_values']:
            self._vaos['values'].render(mode=moderngl.LINE_STRIP)

        if self._parameters['draw_title']:
            self.texture_title.use(0)
            self._programs['title']['text_texture'].value = 0
            self._programs['title']['viewport_size'].value = tuple(self.context().viewport[2:])
            self._vaos['title'].render(mode=moderngl.LINE_STRIP)

        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self) -> str:
        """
        Returns the vertex shader for this particular item
        """
        file = open(Path(__file__).resolve().parent / 'shader_scripts' / 'axis_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self, key: str = 'line') -> str:
        """
        Returns the fragment shader for this particular item
        """
        if key == 'axis':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_axis.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'ticks':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_ticks.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'labels':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_labels.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'title':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_title_2d.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None

    def _geometryShader(self, key: str = 'tiles') -> str:
        """
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        """
        if key == 'axis':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_axis_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'ticks':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_ticks_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'labels':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_labels.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'title':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_title_2d.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None
