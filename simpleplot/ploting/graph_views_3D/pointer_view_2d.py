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

from pathlib import Path

# General imports
import moderngl
import numpy as np

# Personal imports
from .font_to_bitmap import getFontPaths, Font
from ..views_3D.graphics_view_3D import GraphicsView3D


class PointerView2D(GraphicsView3D):
    def __init__(self,**opts):
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
        self._need_update = True
        self._cached_label_text = None
        self._pointer_position = np.array([[0, 0, 0, 0]], dtype='f4')
        self._label_position = np.array([[0, 0, 0, 0]], dtype='f4')
        self._label_texts = ['', '']
        
        self._parameters['draw_pointer'] = True

        self._parameters['pointer_type'] = 'Default'
        self._parameters['pointer_size'] = np.array([50.])
        self._parameters['pointer_thickness'] = np.array([10.])
        self._parameters['pointer_color'] = np.array([0, 0, 0, 1])

        self._parameters['draw_label_box'] = np.array([1])
        self._parameters['label_box_color'] = np.array([0, 0, 0, 1])
        self._parameters['label_box_width'] = np.array([0])

        self._parameters['draw_label'] = True
        self._parameters['label_color'] = np.array([0, 0, 0, 1])
        self._parameters['label_font_size'] = 12
        self._parameters['label_sci'] = [True, True]
        self._parameters['label_sci_prec'] = [4, 4]

    def initializeGL(self) -> None:
        """
        Unitialize the OpenGl states
        """
        self._createProgram(
            "pointer",
            vert_shader=self._vertexShader('pointer'),
            frag_shader=self._fragmentShader('pointer'),
            geometry_shader=self._geometryShader('pointer'))

        self._createProgram(
            "label",
            vert_shader=self._vertexShader('label'),
            geometry_shader=self._geometryShader('label'),
            frag_shader=self._fragmentShader('label'))
            
        self._need_update = True

    def setProperties(self, **kwargs) -> None:
        """
        Set the properties to diplay the graph
        """
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._need_update = True

    def setPosition(self, x, y) -> None:
        """
        Set the properties to diplay the graph
        """
        screen_size = self.renderer().camera()['Screen size']
        x_range = self.renderer().camera()['Camera x range']
        y_range = self.renderer().camera()['Camera y range']
        
        self._pointer_position = np.array([[
            (x / screen_size[0] * 2 - 1),
            ((1- y / screen_size[1])* 2 - 1), 0, 0]])
        
        self._label_position = np.array([self._pointer_position[0], self._pointer_position[0]])
        start = 0
        char_widths = []
        # Do x
        if abs((((self._label_position[0, 0]+1)/2*(x_range[1]-x_range[0]))+x_range[0])) > 1e3 or self._parameters['label_sci'][0]:
            self._label_texts[0] = ("x={:."+str(self._parameters['label_sci_prec'][0])+"e}").format(((self._label_position[0, 0]+1)/2*(x_range[1]-x_range[0]))+x_range[0])
        else:
            self._label_texts[0] = str("x=%g" % (((self._label_position[0, 0]+1)/2*(x_range[1]-x_range[0]))+x_range[0]))
        self._label_position[0, 2] = start
        self._label_position[0, 3] = start + len(self._label_texts[0])
        start += len(self._label_texts[0])
        
        freefont_dict = self.label_font.render_text(self._label_texts[0])
        char_widths.append(sum(freefont_dict['char_width'][freefont_dict['char_index']]))
        
        # Do y
        if abs(((self._label_position[0, 1]+1)/2*(y_range[1]-y_range[0]))+y_range[0]) > 1e3 or self._parameters['label_sci'][1]:
            self._label_texts[1] = ("y={:."+str(self._parameters['label_sci_prec'][1])+"e}").format(((self._label_position[0, 1]+1)/2*(y_range[1]-y_range[0]))+y_range[0])
        else:
            self._label_texts[1] = str("y=%g" % (((self._label_position[0, 1]+1)/2*(y_range[1]-y_range[0]))+y_range[0]))
        self._label_position[1, 2] = start
        self._label_position[1, 3] = start + len(self._label_texts[1])
        
        freefont_dict = self.label_font.render_text(self._label_texts[1])
        char_widths.append(sum(freefont_dict['char_width'][freefont_dict['char_index']]))
        
        self._parameters['label_box_width'] = np.array([max(char_widths)])
        
        self._need_update = True
        self.update()

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
            (freefont_dict['bitmap'].shape[1], freefont_dict['bitmap'].shape[0]), 1,
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
        self.positions_width_label.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.char_width_label.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self._cached_label_text = [font, size]

    def _updatePointer(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """

        # ------------------------------------------------------------------------
        # Process the tick positions
        self._createVBO("pointer", self._pointer_position)
        self._createVAO("pointer", {"pointer": ["4f", "in_vert"]})

        # ------------------------------------------------------------------------
        # process labels
        freefont_dict = self.label_font.render_text(''.join(self._label_texts))
        self.char_index_label = self.context().texture(
            (freefont_dict['char_index'].shape[0], 1), 1,
            (freefont_dict['char_index'].astype('f4') / 1000.).tobytes(),
            dtype='f4')
        self.char_index_label.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Create the labels
        self._createVBO("label", self._label_position)
        self._createVAO("label", {"label": ["4f", "in_vert"]})
        
        self.setUniforms(
            label_texture_len=np.array([freefont_dict['positions_rows'].shape[0]]),
            label_limit=np.array([len(freefont_dict['char_index'])]),
            label_height=np.array([self.label_font.size]),
            label_factor=np.array([1 / freefont_dict['bitmap'].shape[0], 1 / freefont_dict['bitmap'].shape[1]]),
            label_box_width=self._parameters['label_box_width'])
        self._need_update = False

    def paint(self):
        """
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        """
        self.context().disable(moderngl.CULL_FACE)
        
        if self._need_update:
            self._updatePointer()
        
        if self._parameters['draw_pointer']:
            self._programs['pointer']['viewport_size'].value = tuple(self.context().viewport[2:])
            self._vaos['pointer'].render(mode=moderngl.POINTS)
            
        if self._parameters['draw_label']:
            self.positions_row_label.use(0)
            self._programs['label']['positions_rows_label'].value = 0
            self.positions_width_label.use(1)
            self._programs['label']['positions_width_label'].value = 1
            self.char_width_label.use(2)
            self._programs['label']['char_width_label'].value = 2
            self.char_index_label.use(3)
            self._programs['label']['char_index_label'].value = 3
            self.texture_label.use(4)
            self._programs['label']['label_texture'].value = 4

            self._programs['label']['viewport_size'].value = tuple(self.context().viewport[2:])
            self._vaos['label'].render(mode=moderngl.POINTS)
            
        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self, key: str = None) -> str:
        """
        Returns the vertex shader for this particular item
        """
        if key == 'pointer':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_vertex_2d.glsl')
            output = file.read()
            file.close()
            return output

        elif key == 'label':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_vertex_label_2d.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None

    def _fragmentShader(self, key: str = 'pointer') -> str:
        """
        Returns the fragment shader for this particular item
        """
        if key == 'pointer':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_fragment_2d.glsl')
            output = file.read()
            file.close()
            return output
        
        elif key == 'label':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_fragment_label_2d.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None
        
    def _geometryShader(self, key: str = 'pointer') -> str:
        """
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        """
        if key == 'pointer':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_geometry_2d.glsl')
            output = file.read()
            file.close()
            return output
        
        elif key == 'label':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_geometry_label_2d.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None
        