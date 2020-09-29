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
from PyQt5 import QtGui
import moderngl
from moderngl import context
from moderngl.program_members import uniform
import numpy as np
import OpenGL.GL as gl

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D
from ..graphics_geometry.helper_functions   import getInterpolatedNormals

class PlotView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

        self._parameters['diameters']       = [1.,2., 3.]
        self._parameters['positions']       = [2.,2., 3.]
        self._parameters['colors']          = np.array([[0.,0.,0.,1.0],[0.5,0.5,1.0,1.0],[0.5,0.5,0.5,1]])
        self._parameters['color_positions'] = np.array([0.,0.5,1.])
        self._parameters['pen_color']       = QtGui.QColor("black")
        self._parameters['pen_thickness']   = 0.1

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "tiles",vert_shader=self._vertexShader(),
            frag_shader=self._fragmentShader())
        self._vertices  = np.zeros((100,3))
        self._normals   = np.ones((100,3))
        self._faces     = np.zeros((100,3))
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
        self._vertices  = vertices
        self._faces     = faces
        self._normals   = np.ones(vertices.shape) #getInterpolatedNormals(self._vertices, self._faces)
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
        self._createVAO("tiles", {"tiles": ["3f 3f 2f", "in_vert", "in_norm"]})

    def _paintTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        if self._parameters['drawFaces']:
            self.context().disable(moderngl.CULL_FACE)
            self._vaos['tiles'].render()
            self.context().error()
            self.context().enable(moderngl.CULL_FACE)

        if self._parameters['drawEdges']:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            self._vaos['tiles'].render()
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def _vertexShader(self)->str:
        '''
        Returns the vertex shader for this particular item
        '''
        output =  '''
            #version 330

            uniform mat4 u_proj_mat;
            uniform mat4 u_view_mat;
            uniform vec3 u_view_pos;

            uniform vec2 u_light_bool;
            uniform vec3 u_light_pos;
            uniform vec3 u_light_color;
            '''
        start_text = '''
            uniform float positions[1];
            uniform matnxm colors;
            uniform vec2 min_max;
            '''
        start_text = start_text.replace(
            'position[1]', 'position['+str(self._parameters['color_positions'].shape[0])+']')
        start_text = start_text.replace(
            'matnxm', 'mat'+str(self._parameters['color_positions'].shape[0])+'x4')
        output += start_text
        output +=  '''
            in vec3 in_vert;
            in vec3 in_norm;
            
            out vec3 v_normal;
            out vec4 v_color;

            out float light_active;
            out vec3  light_pos;
            out vec3  view_pos;
            out vec3  frag_pos;
            out vec3  light_color;

            '''
        mid_text = '''
            vec4 getColor(vec3 vertex) {
                float z_norm = (vertex.z - min_max.x) / (min_max.y-min_max.x);
                vec4 color = (0,0,0,0);
                for (int i = 0; i < --CHANGE--; ++i){
                    if (z_norm >= positions[0] && z_norm <= positions[1] ){
                        float z_local = (z_norm-positions[0])/(positions[1]-positions[0]);
                        for (int j = 0; j < 4; ++j){
                            color[j] = (colors[i+1][j]-colors[i][j])*z_local + colors[i][j];
                        }
                    }
                return color;
                }
            '''
        start_text = start_text.replace(
            '--CHANGE--', str(self._parameters['color_positions'].shape[0])+'-1')
        output += mid_text

        output +=  '''
            }

            void main() {
                v_normal        = in_norm;
                v_color         = getColor(in_vert);

                light_active    = u_light_bool[0];
                frag_pos        = vec3(in_vert);
                light_pos       = vec3(u_light_pos);
                view_pos        = vec3(u_view_pos);
                light_color     = vec3(u_light_color);
                if (u_light_bool[1]==1){
                    light_pos = vec3(u_proj_mat*u_view_mat*vec4(light_pos, 1.0));
                }
                gl_Position = u_proj_mat*u_view_mat*vec4(in_vert, 1.0);
            }'''
        return output

    def _fragmentShader(self)->str:
        '''
        Returns the fragment shader for this particular item
        '''
        output =  '''
            #version 330

            in vec3 v_normal;
            in vec4 v_color;

            in float light_active;
            in vec3 light_pos;
            in vec3 view_pos;
            in vec3 frag_pos;
            in vec3 light_color;

            out vec4 f_color;
            void main() {

                if (light_active == 1){
                    float ambientStrength = 0.1;
                    vec3 ambient = ambientStrength * light_color;
                    vec3 norm = normalize(v_normal);
                    vec3 lightDir = normalize(light_pos - frag_pos);  
                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = diff * light_color;

                    float specularStrength = 0.5;
                    vec3 viewDir = normalize(view_pos - frag_pos);
                    vec3 reflectDir = reflect(-lightDir, norm);
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 256);
                    vec3 specular = specularStrength * spec * light_color;
                    
                    vec3 result = (ambient + diffuse + specular) * vec3(v_color);
                    f_color = vec4(result, v_color[3]);
                } else {
                    f_color = v_color;
                }

            }'''

        return output
