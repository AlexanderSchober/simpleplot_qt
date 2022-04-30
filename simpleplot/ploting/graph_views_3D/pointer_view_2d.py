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
from ..views_3D.graphics_view_3D import GraphicsView3D


class PointerView2D(GraphicsView3D):
    def __init__(self,**opts):
        """
        """
        super().__init__(**opts)
        self._initParameters()

    def _initParameters(self):
        """
        This is a placeholder for the parameter
        initialisation
        """
        self._need_update = False
        
        self._position = np.array([0,0])
        self._parameters['position'] = self._position
        self._parameters['draw_pointer'] = 'True'

        self._parameters['pointer_type'] = 'Default'
        self._parameters['pointer_size'] = 10
        self._parameters['pointer_thickness'] = 2
        self._parameters['pointer_color'] = np.array([0, 0, 0, 1])

        self._parameters['draw_label_box'] = 'False'
        self._parameters['label_box_color'] = np.array([0, 0, 0, 1])

        self._parameters['draw_label'] = 'False'
        self._parameters['label_color'] = np.array([0, 0, 0, 1])

    def initializeGL(self) -> None:
        """
        Unitialize the OpenGl states
        """
        self._createProgram(
            "pointer",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader(),
            geometry_shader=self._geometryShader())

        self.setUniforms(**self._parameters)
        self._updatePointer()
        self.setMVP()
        self.setLight()

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
        
        self._position = np.array([
            (x / screen_size[0] * 2 - 1)*1,
            ((1- y / screen_size[1])* 2 - 1)*1])

        self._parameters['position'] = self._position
        self.setUniforms(position=self._parameters['position'])
        self._need_update = True
        self.update()

    def _updatePointer(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """
        self.pointer_position = np.array([[0,0,0]], dtype='f4')
        self._createVBO("pointer", self.pointer_position)
        self._createVAO("pointer", {"pointer": ["3f", "in_vert"]})

        self.setUniforms(**self._parameters)
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
            self._vaos['pointer'].render(mode=moderngl.POINTS)
        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self) -> str:
        """
        Returns the vertex shader for this particular item
        """
        file = open(Path(__file__).resolve().parent / 'shader_scripts' / 'pointer_vertex_2d.glsl')
        output = file.read()
        file.close()
        return output

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
        