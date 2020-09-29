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
from pyrr import Matrix44

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D

class VolumeView3D(GraphicsView3D):
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
        self._parameters_colors['step_size'] = 0.5/20
        self._parameters_colors['bot_limits'] = np.array([0,0,0,0])
        self._parameters_colors['top_limits'] = np.array([1,1,1,1])
        self._transform = Matrix44().identity()
        self._bounds = np.zeros((3,2))

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "raycast",vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader())

        self.setData(np.zeros((3,2)),np.zeros((5,5,5)))
        self.setMVP()
        self.setLight()

    def setCubeVertices(self):
        '''
        Create the cube in which the projection will happen

        Parameters:
        ---------------------
        bounds : np,array
            The 3D bounds of the cube 
        '''
        self._faces = np.array([            
            1,5,7,
            7,3,1,
            0,2,6,
            6,4,0,
            0,1,3,
            3,2,0,
            7,5,4,
            4,6,7,
            2,3,7,
            7,6,2,
            1,0,4,
            4,5,1
            ])

        self._vertices = np.reshape(np.array([
            0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, 1.0, 1.0,
            0.0, 1.0, 0.0, 1.0,
            0.0, 1.0, 1.0, 1.0,
            1.0, 0.0, 0.0, 1.0,
            1.0, 0.0, 1.0, 1.0,
            1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0
        ]), (8,4))
        
        self._vertices[:,:3] *= self._bounds[:,1] - self._bounds[:,0]
        self._vertices[:,:3] += self._bounds[:,0]
        for i in range(8):
            self._vertices[i] = self._transform.dot(self._vertices[i])
        self._createIBO("raycast", self._faces)
        self._createVBO("raycast", self._vertices[:,:3])
        self._createVAO("raycast", {"raycast": ["3f", "in_vert"]})

    def setProperties(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters.update(kwargs)
        self.update()

    def setColors(self, **kwargs)->None:
        '''
        Set the properties to diplay the graph
        '''
        self._parameters_colors.update(kwargs)
        input_dict = {
            'min_max': np.array([0,1]),
            'top_limits': self._parameters_colors['top_limits'],
            'bot_limits': self._parameters_colors['bot_limits'],
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
        
    def setData(self, bounds:np.array, data:np.array)->None:
        '''
        Set the data for display

        Parameters:
        ---------------------
        data : np,array
            The 4D data (x,y,z, four colors)
        '''
        self.texture_3D = self.context().texture3d(
            data.shape,1,data.astype(dtype='f4').tobytes(), dtype = 'f4')
        self.texture_3D.repeat_x = False 
        self.texture_3D.repeat_y = False
        self.texture_3D.repeat_z = False
        self.texture_3D.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._bounds = bounds
        self.setCubeVertices()
        self.update()

    def setTransformMatrix(self, transform:Matrix44 = Matrix44().identity())->None:
        '''
        Set the geometric transformation matrix

        Parameters:
        ---------------------
        transform : Matrix44
            The transformation matrix in 3d space
        '''
        for program_name in self._programs.keys():
            u_model_mat = self._programs[program_name].get('u_model_mat', None)
            if not u_model_mat is None: 
                u_model_mat.write(Matrix44().identity().astype(dtype='f4').tobytes())
                self._transform = transform.transpose()
                self.setCubeVertices()

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

    def _paintTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self.context().viewport[2:] == (0,0):
            return

        self.texture_3D.use(0)
        prog                            = self._programs['raycast']
        renderer                        = self.renderer()
        camera                          = renderer._camera
        deg2rad                         = (np.pi/180)
        prog['viewport_size'].value     = tuple(self.context().viewport[2:])
        prog['focal_length'].value      = 1/np.tan(deg2rad*camera['Field of View']/2)
        prog['aspect_ratio'].value      = self.renderer()._camera._ratio
        prog['step_length'].value       = self._parameters_colors['step_size']
        prog['background_colour'].value = tuple(renderer._background_color[:3])
        prog['top'].value               = tuple([
            np.amax(self._vertices[:,0]), 
            np.amax(self._vertices[:,1]), 
            np.amax(self._vertices[:,2])])
        prog['bottom'].value            = tuple([
            np.amin(self._vertices[:,0]), 
            np.amin(self._vertices[:,1]), 
            np.amin(self._vertices[:,2])])
        prog['volume'].value            = 0
        self._vaos['raycast'].render(moderngl.TRIANGLES)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item

        Parameters:
        ---------------------
        select : str
            Selection string
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'volume_vert_raycasting.glsl')
        output = file.read()
        file.close()
        return output

    def _fragmentShader(self)->str:
        '''
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        select : str
            Selection string
        '''
        file = open(Path(__file__).resolve().parent/'shader_scripts'/'volume_frag_raycasting.glsl')
        output = file.read()
        file.close()
        return output
