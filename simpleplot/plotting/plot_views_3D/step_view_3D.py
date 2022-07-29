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
import OpenGL.GL as gl
from pathlib import Path

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D
from ..graphics_geometry.helper_functions   import vertexNormals

class DistributionView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "tiles",vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader(),
            geometry_shader=self._geometryShader('tiles'))

        self._createProgram(
            "edges",vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader(),
            geometry_shader=self._geometryShader('edges'))

        self._vertices  = np.zeros((100,4))
        self._colors    = np.zeros((100,4))
        
        self._updateTilesVBO()
        self.setMVP()
        self.setLight()
        self.update()

    def setProperties(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters.update(kwargs)
        self._updateTilesVBO()
        self.update()

    def setColors(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters_colors.update(kwargs)
        self.update()

    def setData(self, vertices:np.array, colors:np.array)->None:
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
        self._colors    = colors

        self._updateTilesVBO()
        self.update()

    def paint(self):
        '''
        This method will set the visual representation of 
        the opengl opbject
        '''
        self._paintTiles()

    def _updateTilesVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createVBO("tiles", self._vertices, self._colors)
        self._createVAO("tiles", {"tiles": ["4f 4f", "in_vert", "in_color"]})
        self._createVAO("edges", {"tiles": ["4f 4f", "in_vert", "in_color"]})

    def _paintTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self._parameters['drawFaces']:
            # self.context().disable(moderngl.CULL_FACE)
            self._vaos['tiles'].render(mode = moderngl.POINTS)
            # self.context().enable(moderngl.CULL_FACE)

        if self._parameters['drawEdges']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            self._vaos['edges'].render(mode = moderngl.POINTS)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'distribution_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self)->str:
        '''
        Returns the fragment shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'distribution_fragment.glsl')
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
        if key == 'tiles':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'distribution_geometry_tiles.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'edges':
            file = open(Path(__file__).resolve().parent/'shader_scripts'/'distribution_geometry_edges.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None