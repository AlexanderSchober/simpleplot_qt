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
import numpy as np
from pathlib import Path

# Personal imports
from ..views_3D.graphics_view_3D import GraphicsView3D

class LineView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)
        self._initParameters()
        self._need_update = True

    def _initParameters(self):
        """
        This is a placeholder for the parameter
        initialisation
        """
        self._vertices  = np.zeros((100,3))
        self._faces     = np.zeros((100,3), dtype=np.int)

        self._parameters['line_draw']   = True
        self._parameters['line_color']  = np.array([1,1,1,1])
        self._parameters['line_width']  = np.array([0.1])

        self._parameters['fill_draw']   = True
        self._parameters['fill_color']  = np.array([1,1,1,1])
        self._parameters['fill_level']  = np.array([0])
        self._parameters['fill_axis_start']   = np.array([0,0,0])
        self._parameters['fill_axis_end']   = np.array([1,0,0])

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "line",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader('line'),
            geometry_shader = self._geometryShader('line'))

        self._createProgram(
            "fill",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader('fill'),
            geometry_shader = self._geometryShader('fill'))

        self._need_update = True

    def setProperties(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._need_update = True

    def setColors(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters_colors.update(kwargs)
        self._need_update = True

    def setData(self, vertices:np.array)->None:
        '''
        Set the data for display

        Parameters:
        ---------------------
        vertices : np,array
            The 3D vertices array
        faces : np.arrays
            The list of faces for the ibo
        '''
        self._vertices  = vertices
        self._faces     = np.array(
            [[i, i+1,i+2] for i in range(self._vertices.shape[0]-2)], dtype=np.int)
        self._need_update = True

    def paint(self):
        '''
        This method will set the visual representation of 
        the opengl opbject
        '''
        if self._need_update:
            self._updateLineVBO()
            self._need_update = False
            
        self._paintTiles()

    def _updateLineVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createIBO("line", self._faces)
        self._createVBO("line", self._vertices)
        self._createVAO("line", {"line": ["3f", "in_vert"]})
        self._createVAO("fill", {"line": ["3f", "in_vert"]})

    def _paintTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self._parameters['line_draw']:
            self.context().disable(moderngl.CULL_FACE)
            self._vaos['line'].render()
            self.context().enable(moderngl.CULL_FACE)

        if self._parameters['fill_draw']:
            self.context().disable(moderngl.CULL_FACE)
            self._vaos['fill'].render(mode = moderngl.LINE_STRIP)
            self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'line_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self, key:str = 'line')->str:
        '''
        Returns the fragment shader for this particular item
        '''
        if key == 'line':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'line_fragment_line.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'fill':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'line_fragment_fill.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None

    def _geometryShader(self, key:str = 'tiles')->str:
        '''
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        '''
        if key == 'line':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'line_geometry_line.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'fill':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'line_geometry_fill.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None