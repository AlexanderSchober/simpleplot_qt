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

# import pyopencl as cl
# import pyopencl.array as cl_array

from pathlib import Path

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D
from ..graphics_geometry.helper_functions   import vertexNormals

class SurfaceView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)
        self._parameters_colors = {}
        self._parameters_colors['colors']          = np.array([
            [0.,0.,0.,1.0],[0.5,0.5,1.0,1.0],[0.5,0.5,0.5,1]])
        self._parameters_colors['color_positions'] = np.array(
            [0.,0.5,1.])

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "tiles",vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader())

        self._vertices  = np.zeros((100,3))
        self._faces     = np.zeros((100,3), dtype=np.int)
        self._normals   = vertexNormals(self._vertices, self._faces)
        # self._ctx       = cl.create_some_context()
        # self._queue     = cl.CommandQueue(self._ctx)
        # self._mf        = cl.mem_flags
        
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
        input_dict = {
            'min_max': np.array([
                np.min(self._vertices[:,2]),
                np.max(self._vertices[:,2])]),
            'positions': np.concatenate((
                self._parameters_colors['color_positions'],
                np.zeros(100-self._parameters_colors['color_positions'].shape[0]))),
            'colors':  np.concatenate((
                self._parameters_colors['colors'].flatten(),
                np.zeros(400-self._parameters_colors['colors'].flatten().shape[0]))),
            'dimensions': np.array([
                self._parameters_colors['color_positions'].shape[0],
                self._parameters_colors['colors'].shape[1]])
        }
        self.setUniforms(**input_dict)
        self.update()

    def setData(self, vertices:np.array, faces:np.array)->None:
        '''
        Set the data for display

        Parameters:
        ---------------------
        vertices : np,array
            The 3D vertices array
        faces : np.arrays
            The list of faces for the ibo
        '''
        self._vertices      = vertices
        self._faces         = faces.astype(np.int)
        self._normals       = vertexNormals(self._vertices, self._faces)

        # self._vertices_dev  = cl_array.to_device(
        #     self._queue, self._vertices[self._faces.flatten()].astype(np.float))
        # self._dest_bool     = cl_array.to_device(
        #     self._queue,np.zeros((self._faces.shape[0]), dtype=np.bool))
        # self._dest_vert     = cl_array.to_device(
        #     self._queue,np.zeros((self._faces.shape[0],3), dtype=np.float))

        # self._prg = cl.Program(self._ctx, """
        #     __kernel void intersect(
        #         __global const float *vertices, __global bool *bool_holder, __global float *pos_holder)
        #     {
        #     int gid = get_global_id(0);

        #     // Get the position out of the bufer
        #     float4 p1 = (float4){
        #         vertices[3 * gid + 0],
        #         vertices[3 * gid + 1],
        #         vertices[3 * gid + 2],
        #         1
        #     }; 

        #     float4 p2 = (float4){
        #         vertices[3 * gid + 3],
        #         vertices[3 * gid + 4],
        #         vertices[3 * gid + 5],
        #         1
        #     }; 

        #     float4 p3 = (float4){
        #         vertices[3 * gid + 6],
        #         vertices[3 * gid + 7],
        #         vertices[3 * gid + 8],
        #         1
        #     }; 

        #     bool_holder[gid] = true;
        #     pos_holder[3 * gid + 0] = p1[0];
        #     pos_holder[3 * gid + 1] = p1[1];
        #     pos_holder[3 * gid + 2] = p1[2];
        #     }
        #     """).build()

        self._updateTilesVBO()
        self.update()

    def paint(self):
        '''
        This method will set the visual representation of 
        the opengl opbject
        '''
        self._paintTiles()

    def _generateBases(self)->None:
        '''
        Generate the bases used geenrating the elements
        easier afterwards
        '''
        self._ellipse_precision = 100
        self._tube_precision = 10

    def _updateTilesVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''

        self._createIBO("tiles", self._faces)
        self._createVBO("tiles", self._vertices, self._normals)
        self._createVAO("tiles", {"tiles": ["3f 3f", "in_vert", "in_norm"]})

    def _paintTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self._parameters['drawFaces']:
            self.context().disable(moderngl.CULL_FACE)
            self._vaos['tiles'].render()
            self.context().enable(moderngl.CULL_FACE)

        if self._parameters['drawEdges']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            self._vaos['tiles'].render()
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def pickRay(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        
        self._prg.intersect(
            self._queue, (self._faces.shape[0],), None, 
            self._vertices_dev.data, self._dest_bool.data, self._dest_vert.data)

        print('-------------------------------')
        print(self._faces.shape)
        print(self._vertices.shape)
        print(self._dest_vert.shape)
        print(self._dest_bool)
        print(self._dest_vert)
        print(self._vertices)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'surface_vertex.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self)->str:
        '''
        Returns the fragment shader for this particular item
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'surface_fragment.glsl')
        output = file.read()
        file.close()
        return output
