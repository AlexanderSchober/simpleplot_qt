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

from pyqtgraph.opengl import shaders
import numpy as np

class ShaderConstructor:
    '''
    Opengl supports shaders and therefore it is 
    required to write a shader generator based 
    on the shader program of pyqtgraph
    '''

    def __init__(self):
        self._colors    = [[1.,0.,1., 1.], [0., 1., 0., 0.]]
        self._positions = [0,1] 
        self._range     = [0,1]
        self._factors   = [1,0]

    def setColors(self, colors, positions):
        '''
        Set the colors of the shader display
        
        Parameters
        ----------
        colors : list of 4d lists of color values [0. to 1.]
            The colors ar each position

        position: list of int [0. to 1.]
            The position of each color
        '''
        self._colors = list(colors)
        self._positions = list(positions)

    def setRange(self, minimum, maximum):
        '''
        Set the maximum and the the minimum of the
        data so that the factor can be processed
        
        Parameters
        ----------
        minimum : float
            The minimum of the data

        maximum: float
            The maximum of the data
        '''
        self._range = [minimum, maximum]

    def getShader(self, name):
        '''
        get the specified shader

        Parameters
        ----------
        name : string
            The name of the specified shader
        '''
        if name == 'height':
            return self.heightShader()

    def heightShader(self):
        '''
        produce the height shader
        '''
        uniforms = {}
        uniforms['position'] = self._positions
        uniforms['factor']   = [
            1./np.abs(self._range[1]-self._range[0]),
            self._range[0]]
        for i,element in enumerate(self._colors):
            uniforms['color_'+str(i)] = element

        start_text = (
            """
            uniform float position[1];
            uniform float factor[2];
            """)
        start_text = start_text.replace('position[1]', 'position['+str(len(self._positions))+']')

        for i in range(len(self._colors)):
            temp_0 = (
                """uniform float color_0[3];"""
                )
            temp_0 = temp_0.replace('color_0', 'color_'+str(i))
            start_text += str(temp_0)
    
        # out varying vec4 color;    
        fragment_text = (
            """
            varying vec4 pos;
            varying vec3 normal;
            void main() {
                vec4 color;
                float z_norm = ((pos.z-factor[1])*factor[0]);
                float z_local;
            """)

        for i in range(len(self._colors)-1):
            temp_1 = (
                """
                if (z_norm >= position[0] && z_norm <= position[1] ){
                    z_local = (z_norm-position[0])/(position[1]-position[0]);
                    color.x = (color_1[0]-color_0[0])*z_local + color_0[0];
                    color.y = (color_1[1]-color_0[1])*z_local + color_0[1];
                    color.z = (color_1[2]-color_0[2])*z_local + color_0[2];
                    color.w = 1.; 
                }
                """)
            
            temp_1 = temp_1.replace('color_1', 'color_'+str(i+1))
            temp_1 = temp_1.replace('color_0', 'color_'+str(i))
            temp_1 = temp_1.replace('position[1]', 'position['+str(i+1)+']')
            temp_1 = temp_1.replace('position[0]', 'position['+str(i)+']')

            fragment_text += str(temp_1)
        
        fragment_text += ('gl_FragColor = color;}')
        vertex  = shaders.VertexShader(
            """
            varying vec4 pos;
            varying vec3 normal;
            void main() {
                normal = normalize(gl_NormalMatrix * gl_Normal);
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                pos = gl_Vertex;
                gl_Position = ftransform();
            }
            """)
        fragment    = shaders.FragmentShader(
            start_text + fragment_text)
        to_use      = shaders.ShaderProgram(
            'height', 
            [vertex, fragment], 
            uniforms = uniforms)

        return to_use
