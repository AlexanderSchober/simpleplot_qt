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

# General imports
import moderngl
import numpy as np
from pathlib import Path

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D

class GridView3D(GraphicsView3D):
    def __init__(self, axis_items, **opts):
        '''
        '''
        super().__init__(**opts)
        self._modes = [
            [axis_items[0], axis_items[1]],
            [axis_items[1], axis_items[2]],
            [axis_items[0], axis_items[2]]
            ]
        self._initParameters()

    def _initParameters(self):
        '''
        This is a placeholder for the parameter
        initialisation
        '''
        self._parameters['draw_grid']   = True
        self._parameters['grid_mode']   = 0
        self._parameters['grid_color']  = np.array([1,1,1,1])
        self._parameters['grid_thickness'] = np.array(0.05)

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "grid",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader(),
            geometry_shader = self._geometryShader())

        self.setProperties()
        self.setMVP()
        self.setLight()
        self.update()

    def setProperties(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._updateGrid()
        self.update()

    def _updateGrid(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        axes = self._modes[self._parameters['grid_mode']]

        x_axis = np.array(
            [axes[0]._parameters['axis_direction'] * val 
            for val in np.sort(axes[0]._tick_positions_1d).tolist()])
        y_axis = np.array(
            [axes[1]._parameters['axis_direction'] * val 
            for val in np.sort(axes[1]._tick_positions_1d).tolist()])

        grid_input = np.zeros(((x_axis.shape[0]+y_axis.shape[0]),2,3))

        grid_input[:x_axis.shape[0], 0, :] = x_axis + axes[0]._parameters['axis_center']
        grid_input[:x_axis.shape[0], 1, :] = x_axis + y_axis[-1] + axes[0]._parameters['axis_center']

        grid_input[x_axis.shape[0]:, 0, :] = y_axis + axes[1]._parameters['axis_center']
        grid_input[x_axis.shape[0]:, 1, :] = y_axis + x_axis[-1] + axes[1]._parameters['axis_center']

        self._createVBO("grid", np.reshape(grid_input, (grid_input.shape[0]*2,3)))
        self._createVAO("grid", {"grid": ["3f", "in_vert"]})

    def paint(self):
        '''
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        '''

        if self._parameters['draw_grid']:
            self.context().disable(moderngl.CULL_FACE)
            self._vaos['grid'].render(mode = moderngl.LINES)
            self.context().enable(moderngl.CULL_FACE)


    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'grid_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self, key:str = 'line')->str:
        '''
        Returns the fragment shader for this particular item
        '''
        file = open(
            Path(__file__).resolve().parent/'shader_scripts'/'grid_fragment.glsl')
        output = file.read()
        file.close()
        return output

    def _geometryShader(self, key:str = 'tiles')->str:
        '''
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        '''
        file = open(
            Path(__file__).resolve().parent/'shader_scripts'/'grid_geometry.glsl')
        output = file.read()
        file.close()
        return output
