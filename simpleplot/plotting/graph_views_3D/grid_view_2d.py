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


class GridView2D(GraphicsView3D):
    def __init__(self, axis_items, **opts):
        """
        """
        super().__init__(**opts)
        self._axis_items = axis_items
        self._initParameters()

    def _initParameters(self):
        """
        This is a placeholder for the parameter
        initialisation
        """
        self._need_update = True

        self._tick_values = np.array([0, 0.5, 0.7, 1])
        self._orientations = {
            'vertical': np.array([0, 1, 0]),
            'horizontal': np.array([1, 0, 0])}

        self._parameters['draw_grid'] = True
        self._parameters['draw_small_grid'] = True

        # main grid
        self._parameters['grid_periodicity'] = np.array([6, 2, 2, 2])
        self._parameters['grid_color'] = np.array([0, 0, 0, 1])
        self._parameters['grid_thickness'] = np.array(2)
        self._parameters['grid_periodicty_length'] = np.array(1)

        # small grid
        self._parameters['small_grid_periodicity'] = np.array([6, 2, 2, 2])
        self._parameters['small_grid_color'] = np.array([0.5, 0.5, 0.5, 1])
        self._parameters['small_grid_thickness'] = np.array(1)
        self._parameters['small_grid_periodicty_length'] = np.array(1)
        self._parameters['small_grid_multiplicity'] = 4

        # common
        self._parameters['grid_orientation'] = 'vertical'
        self._parameters['grid_direction'] = np.array([0, 1, 0])
        self._parameters['grid_length'] = np.array(1)
        self._parameters['grid_z'] = np.array(0.99)

    def initializeGL(self) -> None:
        """
        Unitialize the OpenGl states
        """
        self._createProgram(
            "grid",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader(),
            geometry_shader=self._geometryShader())

        self._createProgram(
            "small_grid",
            vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader('small_grid'),
            geometry_shader=self._geometryShader('small_grid'))

        self._need_update = True

    def setProperties(self, **kwargs) -> None:
        """
        Set the properties to diplay the graph
        """
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._need_update = True

    def _updateGrid(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """
        self._generatePeriodicityTextures()
        self._tick_values, self.grids_positions, _ = self.renderer().space().getTicks(
            'x' if self._parameters['grid_orientation'] == 'vertical' else 'y')
        self.grids_length_temp = self._getGridLengths()
        self.grids_positions = self._getGridPositions(self.grids_positions)

        # main grid
        self._createVBO("grid", self.grids_positions)
        self._createVAO("grid", {"grid": ["3f", "in_vert"]})

        self._parameters['grid_length'] = np.array([self.grids_length_temp])
        pixel_size = self.renderer().camera().getPixelSize()
        if self._parameters['grid_orientation'] == 'vertical':
            grid_thickness = np.array(
                self._parameters['grid_thickness'] * float(pixel_size[0]))
            small_grid_thickness = np.array(
                self._parameters['small_grid_thickness'] * float(pixel_size[0]))
        else:
            grid_thickness = np.array(
                self._parameters['grid_thickness'] * float(pixel_size[1]))
            small_grid_thickness = np.array(
                self._parameters['small_grid_thickness'] * float(pixel_size[0]))

        # small grid
        if self.grids_positions.shape[0] > 2:
            small_grid_positions = np.zeros(
                ((self._parameters['small_grid_multiplicity']-1)*(self.grids_positions.shape[0] + 1), 3))
            if self._parameters['grid_orientation'] == 'vertical':
                step = self.grids_positions[1][0] - self.grids_positions[0][0]
                small_step = step / self._parameters['small_grid_multiplicity']
                fill_index = 0
                small_grid_positions[:, 1] = self.grids_positions[0, 1]
                position = self.grids_positions[0][0] - step
            else:
                step = self.grids_positions[1][1] - self.grids_positions[0][1]
                small_step = step / self._parameters['small_grid_multiplicity']
                fill_index = 1
                small_grid_positions[:, 0] = self.grids_positions[0, 0]
                position = self.grids_positions[0][1] - step

            for i in range(self.grids_positions.shape[0] + 1):
                position += small_step
                for j in range(self._parameters['small_grid_multiplicity']-1):
                    small_grid_positions[i*(
                        self._parameters['small_grid_multiplicity']-1)+j, fill_index] = position
                    position += small_step

            self.small_grids_positions = small_grid_positions
        else:
            self.small_grids_positions = self.grids_positions

        self._createVBO("small_grid", self.small_grids_positions)
        self._createVAO("small_grid", {"small_grid": ["3f", "in_vert"]})

        if self._parameters['grid_orientation'] == 'vertical':
            small_grid_thickness = np.array(
                self._parameters['small_grid_thickness'] * float(pixel_size[0]))
        else:
            small_grid_thickness = np.array(
                self._parameters['small_grid_thickness'] * float(pixel_size[1]))

        self.setUniforms(
            grid_length=self._parameters['grid_length'],
            grid_color=self._parameters['grid_color'],
            grid_thickness=grid_thickness,
            grid_direction=self._orientations[self._parameters['grid_orientation']],
            grid_periodicty_length=self._parameters['grid_periodicty_length'],
            small_grid_thickness=small_grid_thickness,
            small_grid_periodicty_length=self._parameters['small_grid_periodicty_length']

        )

        self._need_update = False

    def _generatePeriodicityTextures(self) -> np.array:
        """
        This will generate the necessary texture from the peridocty
        parameter.
        """
        grid_orientation = self._parameters['grid_orientation']
        pixel_size = self.renderer().camera().getPixelSize()

        # main grid
        if grid_orientation == 'vertical':
            self._parameters['grid_periodicty_length'] = np.array(
                np.sum(self._parameters['grid_periodicity']) * pixel_size[1])
        else:
            self._parameters['grid_periodicty_length'] = np.array(
                np.sum(self._parameters['grid_periodicity']) * pixel_size[0])

        grid_texture = []
        current_bool = True
        for value in self._parameters['grid_periodicity']:
            for i in range(value):
                grid_texture.append(current_bool)
            current_bool = not current_bool

        grid_texture = np.array(grid_texture, dtype=np.int8)
        self.grid_texture = self.context().texture(
            (grid_texture.shape[0], 1), 1,
            (grid_texture).astype('f4').tobytes(),
            dtype='f4')

        self.grid_texture.repeat_x = True
        self.grid_texture.repeat_y = True
        self.grid_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # small grid
        if grid_orientation == 'vertical':
            self._parameters['small_grid_periodicty_length'] = np.array(
                np.sum(self._parameters['small_grid_periodicity']) * pixel_size[1])
        else:
            self._parameters['small_grid_periodicty_length'] = np.array(
                np.sum(self._parameters['small_grid_periodicity']) * pixel_size[0])

        small_grid_texture = []
        current_bool = True
        for value in self._parameters['small_grid_periodicity']:
            for i in range(value):
                small_grid_texture.append(current_bool)
            current_bool = not current_bool

        small_grid_texture = np.array(grid_texture, dtype=np.int8)
        self.small_grid_texture = self.context().texture(
            (small_grid_texture.shape[0], 1), 1,
            (small_grid_texture).astype('f4').tobytes(),
            dtype='f4')

        self.small_grid_texture.repeat_x = True
        self.small_grid_texture.repeat_y = True
        self.small_grid_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

    def _getGridPositions(self, grid_positions):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """
        grid_orientation = self._parameters['grid_orientation']
        axis_margins = self.renderer().camera()['Margins (px)']
        screen_size = self.renderer().camera()['Screen size']

        if grid_orientation == 'vertical':
            grid_positions[:, 1] = axis_margins[1] / screen_size[1] * 2 - 1 \
                if screen_size[1] != 0 else 0
        else:
            grid_positions[:, 0] = axis_margins[0] / screen_size[0] * 2 - 1 \
                if screen_size[0] != 0 else 0

        return grid_positions

    def _getGridLengths(self):
        """
        This will determine the appropriate tick positioning on screen
        :param tick_values: np.array(float), array of float values
        :return: np.array(float), 3d array of float positions
        """
        grid_orientation = self._parameters['grid_orientation']
        grid_margins = self.renderer().camera()['Margins (px)']
        screen_size = self.renderer().camera()['Screen size']

        if grid_orientation == 'vertical':
            grids_length = (
                ((screen_size[1] - grid_margins[3]) / screen_size[1] * 2 - 1)
                - (grid_margins[1] / screen_size[1] * 2 - 1)) if screen_size[1] != 0 else 0

        else:
            grids_length = (
                ((screen_size[0] - grid_margins[2]) / screen_size[0] * 2 - 1)
                - (grid_margins[0] / screen_size[0] * 2 - 1)) if screen_size[0] != 0 else 0

        return grids_length

    def paint(self):
        """
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        """
        self.context().disable(moderngl.CULL_FACE)

        if self._need_update:
            self._updateGrid()

        if self._parameters['draw_grid']:
            self.grid_texture.use(0)
            self._programs['grid']['grid_texture'].value = 0
            self._vaos['grid'].render(mode=moderngl.POINTS)

        if self._parameters['draw_small_grid']:
            self.small_grid_texture.use(0)
            self._programs['small_grid']['grid_small_texture'].value = 0
            self._vaos['small_grid'].render(mode=moderngl.POINTS)

        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self) -> str:
        """
        Returns the vertex shader for this particular item
        """
        file = open(Path(__file__).resolve().parent /
                    'shader_scripts' / 'grid_vertex_2d.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self, key: str = 'grid') -> str:
        """
        Returns the fragment shader for this particular item
        """
        if key == 'grid':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'grid_fragment_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'small_grid':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'grid_small_fragment_2d.glsl')
            output = file.read()
            file.close()
            return output

    def _geometryShader(self, key: str = 'grid') -> str:
        """
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        """
        if key == 'grid':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'grid_geometry_2d.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'small_grid':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'grid_small_geometry_2d.glsl')
            output = file.read()
            file.close()
            return output
