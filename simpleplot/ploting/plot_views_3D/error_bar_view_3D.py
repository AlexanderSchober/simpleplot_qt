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

class ErrorBarView(GraphicsView3D):
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
        self._parameters = {}
        self._parameters['draw_error_bar'] = True
        self._parameters['mode'] = np.array([0.])
        self._parameters['line_width'] = np.array([5.])
        self._parameters['beam_width'] = np.array([5.])

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        print('CONTEXT:', self.context())
        self._createProgram(
            "error_bar",
            vert_shader=self._vertexShader('error_bar'),
            frag_shader=self._fragmentShader('error_bar'),
            geometry_shader=self._geometryShader('error_bar'))

        self._vertices    = np.zeros((100,4))
        self._line_colors = np.zeros((100,4))
        self._error_x = np.zeros((100,2))
        self._error_y = np.zeros((100,2))
        # self._error_z = np.zeros((100,2)) For later when implementing shaders !

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

    def setData(self, vertices:np.array, line_colors:np.array, error_x:np.array, error_y:np.array, error_z:np.array)->None:
        '''
        Set the data for display

        Parameters:
        ---------------------
        vertices : np,array
            The 3D vertices array
        faces : np.arrays
            The list of faces for the ibo
        '''
        self._vertices    = vertices
        self._line_colors = line_colors
        self._error_x = error_x
        self._error_y = error_y

        self._need_update = True

    def _updateVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createVBO("error_bar", self._vertices, self._line_colors, self._error_x, self._error_y)
        self._createVAO("error_bar", {
            "error_bar": [
                "4f 4f 2f 2f", 
                "in_vert", 
                "in_color", 
                "x_error", 
                "y_error"]})

    def paint(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self._need_update:
            self._updateVBO()
            self._need_update = False
            
        if self._parameters['draw_error_bar']:
            self._programs['error_bar']['viewport_size'].value = tuple(self.context().viewport[2:])
            self.context().disable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)
            self._vaos['error_bar'].render(mode = moderngl.POINTS)
            self.context().enable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)

    def _vertexShader(self, key:str = 'error_bar')->str:
        '''
        Returns the vertex shader for this particular item
        '''
        if key == 'error_bar':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'error_bar_vertex.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None

    def _fragmentShader(self, key:str = 'error_bar')->str:
        '''
        Returns the fragment shader for this particular item
        '''
        if key == 'error_bar':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'error_bar_fragment.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None

    def _geometryShader(self, key:str = 'error_bar')->str:
        '''
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        '''
        if key == 'error_bar':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'error_bar_geometry.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None
        