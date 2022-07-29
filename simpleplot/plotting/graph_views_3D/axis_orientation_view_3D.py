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

# General imports
import moderngl
from pathlib import Path
import numpy as np

# Personal imports
from ..views_3D.graphics_view_3D import GraphicsView3D

class AxisOrientationView3D(GraphicsView3D):
    def __init__(self,**opts):
        '''
        '''
        super().__init__(**opts)
        self._initParameters()

    def _initParameters(self):
        '''
        This is a placeholder for the parameter
        initialisation
        '''
        self._tick_positions_1d = np.array([0,0.5,0.7,1])
        self._offset_corners = {}
        self._offset_corners[0] = [1,-1]
        self._offset_corners[1] = [1,1]
        self._offset_corners[2] = [-1,-1]
        self._offset_corners[3] = [-1,1]

        self._parameters['draw_axis']           = True
        self._parameters['axis_length']         = np.array([-5., 5.])
        self._parameters['axis_width']          = np.array([0.05])
        self._parameters['axis_color']          = np.array([1,0,0,1])
        self._parameters['axis_direction']      = np.array([1,0,0])
        self._parameters['axis_arrow_width']    = np.array([0.1])
        self._parameters['axis_arrow_length']   = np.array([0.2])
        self._parameters['axis_scale_factor']   = np.array([10])
        self._parameters['axis_offset_corner']  = 1
        self._parameters['axis_offset_value']   = np.array([150,150], dtype = float)

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "axis",
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
        self._updateAxis()
        self.update()

    def _updateAxis(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createVBO("axis", np.array([[-1,0,0],[1,0,0]]))
        self._createVAO("axis", {"axis": ["3f", "in_vert"]})

    def paint(self):
        '''
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        '''
        self.context().disable(moderngl.CULL_FACE)

        if self._parameters['draw_axis']:
            prog                            = self._programs['axis']
            renderer                        = self.renderer()
            camera                          = renderer._camera
            select                          = self._offset_corners[self._parameters['axis_offset_corner']]
            val                             = self._parameters['axis_offset_value']
            viewport                        = tuple(self.context().viewport[2:])
            position                        = tuple([
                val[0] if select[0]==1 else viewport[0] - val[0],
                val[1] if select[1]==1 else viewport[1] - val[1]
            ])

            prog['viewport_size'].value     = viewport
            prog['near_plane'].value        = camera['Z near']
            prog['position_offset'].value   = position

            self._vaos['axis'].render(mode = moderngl.LINE_STRIP)

        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'axis_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self, key:str = 'line')->str:
        '''
        Returns the fragment shader for this particular item
        '''
        file = open(
            Path(__file__).resolve().parent/'shader_scripts'/'axis_fragment_axis.glsl')
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
            Path(__file__).resolve().parent/'shader_scripts'/'axis_geometry_axis_orientation.glsl')
        output = file.read()
        file.close()
        return output
