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
from typing import Tuple
from PyQt5.QtCore import pyqtSignal

import moderngl
import numpy as np

from .font_to_bitmap import getFontPaths, Font
from ..views_3D.graphics_view_3D import GraphicsView3D

SI_PREFIXES = str('yzafpnµm kMGTPEZY')
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'


class AxisView2D(GraphicsView3D):
    ticks_updated = pyqtSignal()

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
        self._tick_values = np.array([0, 0.5, 0.7, 1])
        self.texture_title = None
        self._cached_text = None
        self._cached_label_text = None
        self._ticks_positions = None
        self._title_position = None
        self._need_update = True

        self._parameters['draw_axis'] = True
        self._parameters['draw_ticks'] = True
        self._parameters['draw_values'] = False
        self._parameters['draw_title'] = False
        self._parameters['draw_edge'] = True

        self._parameters['axis_widths'] = np.array([0.05, 0.05, 0.05, 0.05])
        self._parameters['axis_color'] = np.array([1, 0, 0, 1])
        self._parameters['axis_pos'] = 'bottom'

        self._parameters['tick_length'] = np.array([10])
        self._parameters['tick_direction'] = np.array([0, 1, 0])
        self._parameters['tick_color'] = np.array([1, 0, 0, 1])
        self._parameters['tick_width'] = np.array([10])
        self._parameters['small_ticks'] = np.array([1])

        self._parameters['title_position'] = np.array([10])
        self._parameters['title_angle'] = np.array([0])
        self._parameters['title_v_just'] = np.array([0])
        self._parameters['title_h_just'] = np.array([0])

        self._parameters['label_color'] = np.array([0, 0, 0, 1])
        self._parameters['label_angle'] = np.array([0])
        self._parameters['label_position'] = np.array([0])
        self._parameters['label_v_just'] = np.array([0])
        self._parameters['label_h_just'] = np.array([0])

        self._parameters['edge_color'] = np.array([1, 1, 1, 1])

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
            vert_shader=self._vertexShader('labels'),
            geometry_shader=self._geometryShader('labels'),
            frag_shader=self._fragmentShader('labels'))

        self._createProgram(
            "title",
            vert_shader=self._vertexShader(),
            geometry_shader=self._geometryShader('title'),
            frag_shader=self._fragmentShader('title'))

        self._createProgram(
            "edge",
            vert_shader=self._vertexShader(),
            geometry_shader=self._geometryShader('edge'),
            frag_shader=self._fragmentShader('edge'))

        self.setUniforms(**self._parameters)
        self.setLabelFont('Arial', 20)
        self.setTitle('123', 'Arial', 20)

    def setProperties(self, **kwargs) -> None:
        """
        Set the properties to display the graph
        """
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._need_update = True

    def setTitle(self, text: str, font: str, size: int) -> None:
        """
        This method will effectively build the texture for the text
        :param text: str, the text to set
        :param font: QtGui.QFont
        :return: None
        """
        if self._cached_text is not None and self._cached_text[0] == text and self._cached_text[1] == font and \
                self._cached_text[2] == size:
            return

        freetype_font = Font(self._family_to_path[font] if font != 'MS Shell Dlg 2'
                             else self._family_to_path['Arial'], size)
        freefont_dict = freetype_font.render_text(text)

        self.texture_title = self.context().texture(
            (freefont_dict['bitmap'].shape[1],
             freefont_dict['bitmap'].shape[0]), 1,
            (freefont_dict['bitmap'] / 256).astype('f4').tobytes(),
            dtype='f4')

        self.positions_row_title = self.context().texture(
            (freefont_dict['positions_rows'].shape[0], 1), 1,
            (freefont_dict['positions_rows'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.positions_width_title = self.context().texture(
            (freefont_dict['positions_width'].shape[0], 1), 1,
            (freefont_dict['positions_width'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.char_width_title = self.context().texture(
            (freefont_dict['char_width'].shape[0], 1), 1,
            (freefont_dict['char_width'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.char_index_title = self.context().texture(
            (freefont_dict['char_index'].shape[0], 1), 1,
            (freefont_dict['char_index'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.texture_title.repeat_x = False
        self.texture_title.repeat_y = False
        self.texture_title.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.positions_row_title.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.positions_width_title.filter = (
            moderngl.NEAREST, moderngl.NEAREST)
        self.char_width_title.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.char_index_title.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.setUniforms(
            title_texture_len=np.array(
                [freefont_dict['positions_rows'].shape[0]]),
            limit=np.array([len(freefont_dict['char_index'])]),
            height=np.array([freetype_font.size]),
            factor=np.array([1 / freefont_dict['bitmap'].shape[0],
                            1 / freefont_dict['bitmap'].shape[1]])
        )

        self._cached_text = [text, font, size]

    def setLabelFont(self, font: str, size: int) -> None:
        """
        This method will effectively build the texture for the text
        :param text: str, the text to set
        :param font: QtGui.QFont
        :return: None
        """

        if self._cached_label_text is not None and \
                self._cached_label_text[0] == font and self._cached_label_text[1] == size:
            return

        self.label_font = Font(self._family_to_path[font] if font != 'MS Shell Dlg 2'
                               else self._family_to_path['Arial'], size)
        freefont_dict = self.label_font.render_text("")

        self.texture_label = self.context().texture(
            (freefont_dict['bitmap'].shape[1],
             freefont_dict['bitmap'].shape[0]), 1,
            (freefont_dict['bitmap'] / 256).astype('f4').tobytes(),
            dtype='f4')

        self.positions_row_label = self.context().texture(
            (freefont_dict['positions_rows'].shape[0], 1), 1,
            (freefont_dict['positions_rows'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.positions_width_label = self.context().texture(
            (freefont_dict['positions_width'].shape[0], 1), 1,
            (freefont_dict['positions_width'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.char_width_label = self.context().texture(
            (freefont_dict['char_width'].shape[0], 1), 1,
            (freefont_dict['char_width'].astype('f4') / 1000.).tobytes(),
            dtype='f4')

        self.texture_label.repeat_x = False
        self.texture_label.repeat_y = False
        self.texture_label.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.positions_row_label.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.positions_width_label.filter = (
            moderngl.NEAREST, moderngl.NEAREST)
        self.char_width_label.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self._cached_label_text = [font, size]

    def _updateAxis(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """
        self.tick_values, ticks_positions_temp, self.label_positions, label_string = self.renderer(
        ).space().getTicksAndLabels('x' if self._parameters['axis_pos'] in ('bottom', 'top') else 'y')

        self.label_positions = self._getLabelPositions(self.label_positions)
        ticks_positions_temp = self._getTickPositions(ticks_positions_temp)

        # ------------------------------------------------------------------------
        # process the axis
        self._createVBO("axis", self.getAxisPositions())
        self._createVAO("axis", {"axis": ["3f", "in_vert"]})

        # ------------------------------------------------------------------------
        # Process the tick positions
        if not np.array_equal(ticks_positions_temp, self._ticks_positions):
            self._ticks_positions = ticks_positions_temp
            self._createVBO("ticks", self._ticks_positions)
            self._createVAO("ticks", {"ticks": ["3f", "in_vert"]})

        # ------------------------------------------------------------------------
        # Process the title
        title_positions_temp = self._getTitleParameters()
        if not np.array_equal(title_positions_temp, self._title_position):
            self._title_position = title_positions_temp
            self._createVBO("title", self._title_position)
            self._createVAO("title", {"title": ["3f", "in_vert"]})
        self._createVBO("edge", self._getEdgePositions())
        self._createVAO("edge", {"edge": ["3f", "in_vert"]})

        # ------------------------------------------------------------------------
        # process labels
        freefont_dict = self.label_font.render_text(label_string)
        self.char_index_label = self.context().texture(
            (freefont_dict['char_index'].shape[0], 1), 1,
            (freefont_dict['char_index'].astype('f4') / 1000.).tobytes(),
            dtype='f4')
        self.char_index_label.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Create the labels
        self._createVBO("labels", self.label_positions)
        self._createVAO("labels", {"labels": ["4f", "in_vert"]})

        # ------------------------------------------------------------------------
        # Finnaly process some cosmethiques and send off uniforms
        pixel_size = self.renderer().camera().getPixelSize()
        if self._parameters['axis_pos'] in ['bottom', 'top']:
            axis_thickness = self._parameters['axis_widths'][self._orientations.index(self._parameters['axis_pos'])] \
                * float(pixel_size[1])
            tick_thickness = self._parameters['tick_width'] * \
                float(pixel_size[0])
            tick_length = self._parameters['tick_length'] * \
                float(pixel_size[1])

        else:
            axis_thickness = self._parameters['axis_widths'][self._orientations.index(self._parameters['axis_pos'])] \
                * float(pixel_size[0])
            tick_thickness = self._parameters['tick_width'] * \
                float(pixel_size[1])
            tick_length = self._parameters['tick_length'] * \
                float(pixel_size[0])

        self.setUniforms(
            axis_thickeness=axis_thickness,
            tick_thickness=tick_thickness,
            tick_length=tick_length,
            label_texture_len=np.array(
                [freefont_dict['positions_rows'].shape[0]]),
            label_limit=np.array([len(freefont_dict['char_index'])]),
            label_height=np.array([self.label_font.size]),
            label_factor=np.array(
                [1 / freefont_dict['bitmap'].shape[0], 1 / freefont_dict['bitmap'].shape[1]])
        )

        self._need_update = False

    def _getLabelPositions(self, label_positions):
        """
        This will correct the default label position 
        """
        label_pos = self._parameters['label_position']
        axis_pos = self._parameters['axis_pos']
        axis_margins = self.renderer().camera()['Margins (px)']
        screen_size = self.renderer().camera()['Screen size']

        if axis_pos == 'bottom':
            label_positions[:, 1] = (axis_margins[1] - label_pos) / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'top':
            label_positions[:, 1] = (screen_size[1] - axis_margins[3] + label_pos) / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'left':
            label_positions[:, 0] = (axis_margins[0] - label_pos) / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0
        elif axis_pos == 'right':
            label_positions[:, 0] = (screen_size[0] - axis_margins[2] + label_pos) / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0
        
        return label_positions

    def _getTitleParameters(self) -> Tuple[np.array, np.array]:
        """
        :return: Tuple[np.array, np.array]
        """
        center = self._getTitleCenter()

        positions = np.array([
            [center[0], center[1], -1]
        ], dtype='f4')

        return positions

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
        axis_margins = self.renderer().camera()['Margins (px)']
        cam_method = self.renderer().camera().getPixelScreenValue

        if axis_pos == 'bottom':
            return np.array([
                list(cam_method(
                    axis_margins[0] - self._parameters['axis_widths'][0] / 2, axis_margins[1])) + [0],
                list(
                    cam_method(-axis_margins[2] + self._parameters['axis_widths'][2] / 2, axis_margins[1])) + [0]
            ])
        elif axis_pos == 'top':
            return np.array([
                list(cam_method(
                    axis_margins[0] - self._parameters['axis_widths'][0] / 2, -axis_margins[3])) + [0],
                list(
                    cam_method(-axis_margins[2] + self._parameters['axis_widths'][2] / 2, -axis_margins[3])) + [0]
            ])
        elif axis_pos == 'left':
            return np.array([
                list(cam_method(
                    axis_margins[0], -axis_margins[3] - self._parameters['axis_widths'][3] / 2)) + [0],
                list(cam_method(
                    axis_margins[0], axis_margins[1] + self._parameters['axis_widths'][0] / 2)) + [0]
            ])
        elif axis_pos == 'right':
            return np.array([
                list(cam_method(-axis_margins[2], -axis_margins[3] -
                     self._parameters['axis_widths'][3] / 2)) + [0],
                list(cam_method(-axis_margins[2], axis_margins[1] +
                     self._parameters['axis_widths'][0] / 2)) + [0]
            ])
        else:
            return np.array([
                list(cam_method(0, 0)) + [0],
                list(cam_method(1, 1)) + [0]
            ])

    def _getTickPositions(self, ticks_positions):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """
        axis_pos = self._parameters['axis_pos']
        axis_margins = self.renderer().camera()['Margins (px)']
        screen_size = self.renderer().camera()['Screen size']

        if axis_pos == 'bottom':
            ticks_positions[:, 1] = axis_margins[1] / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'top':
            ticks_positions[:, 1] = (screen_size[1] - axis_margins[3]) / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        elif axis_pos == 'left':
            ticks_positions[:, 0] = axis_margins[0] / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0
        elif axis_pos == 'right':
            ticks_positions[:, 0] = (screen_size[0] - axis_margins[2]) / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0

        return ticks_positions

    def _getEdgePositions(self):
        """
        This will determine the appropriate tick positioning on screen
        :return: np.array(float), 3d array of float positions
        """
        axis_pos = self._parameters['axis_pos']
        axis_margins = self.renderer().camera()['Margins (px)']
        cam_method = self.renderer().camera().getPixelScreenValue
        if axis_pos == 'bottom':
            pos = cam_method(None, axis_margins[1])
            return np.array([
                [-1, pos, 0], [1, pos, 0], [-1, -1, 0],
                [-1,  -1, 0], [1, pos, 0], [1, -1, 0]
            ])
        elif axis_pos == 'top':
            pos = cam_method(None, -axis_margins[3])
            return np.array([
                [-1, pos, 0], [1, pos, 0], [-1,  1, 0],
                [-1,   1, 0], [1, pos, 0], [1,  1, 0]
            ])
        elif axis_pos == 'left':
            pos = cam_method(axis_margins[0], None)
            return np.array([
                [pos, -1, 0], [pos, 1, 0], [-1, -1, 0],
                [-1,  -1, 0], [pos, 1, 0], [-1,  1, 0]
            ])
        elif axis_pos == 'right':
            pos = cam_method(-axis_margins[2], None)
            return np.array([
                [pos, -1, 0], [pos, 1, 0], [1, -1, 0],
                [1,  -1, 0], [pos, 1, 0], [1,  1, 0]
            ])
        else:
            return np.array([
                list(cam_method(0, 0)) + [0],
                list(cam_method(1, 1)) + [0]
            ])

    def paint(self):
        """
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the labels
        """
        self.context().disable(moderngl.CULL_FACE)

        if self._need_update:
            self._updateAxis()

        if self._parameters['draw_axis']:
            self._vaos['axis'].render(mode=moderngl.LINE_STRIP)

        if self._parameters['draw_ticks']:
            self._vaos['ticks'].render(mode=moderngl.POINTS)

        if self._parameters['draw_edge']:
            self._vaos['edge'].render(mode=moderngl.TRIANGLE_STRIP)

        if self._parameters['draw_values']:
            self.positions_row_label.use(0)
            self._programs['labels']['positions_rows_label'].value = 0
            self.positions_width_label.use(1)
            self._programs['labels']['positions_width_label'].value = 1
            self.char_width_label.use(2)
            self._programs['labels']['char_width_label'].value = 2
            self.char_index_label.use(3)
            self._programs['labels']['char_index_label'].value = 3
            self.texture_label.use(4)
            self._programs['labels']['label_texture'].value = 4

            self._programs['labels']['viewport_size'].value = tuple(
                self.context().viewport[2:])
            self._vaos['labels'].render(mode=moderngl.POINTS)

        if self._parameters['draw_title']:
            self.positions_row_title.use(0)
            self._programs['title']['positions_rows_title'].value = 0
            self.positions_width_title.use(1)
            self._programs['title']['positions_width_title'].value = 1
            self.char_width_title.use(2)
            self._programs['title']['char_width_title'].value = 2
            self.char_index_title.use(3)
            self._programs['title']['char_index_title'].value = 3
            self.texture_title.use(4)
            self._programs['title']['text_texture'].value = 4

            self._programs['title']['viewport_size'].value = tuple(
                self.context().viewport[2:])
            self._vaos['title'].render(mode=moderngl.POINTS)

        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self, key: str = None) -> str:
        """
        Returns the vertex shader for this particular item
        """
        if key == 'labels':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_vertex_labels.glsl')
            output = file.read()
            file.close()
            return output

        file = open(Path(__file__).resolve().parent /
                    'shader_scripts' / 'axis_vertex.glsl')
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
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_label_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'title':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_title_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'edge':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_fragment_edge_2d.glsl')
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
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_label_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'title':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_title_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'edge':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'axis_geometry_edge_2d.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None
