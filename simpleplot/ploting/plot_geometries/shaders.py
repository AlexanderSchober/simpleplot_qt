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
from PyQt5 import QtGui
import numpy as np
from OpenGL.GL import glUseProgram, glGetUniformLocation, glCreateProgram, glAttachShader

from ...pyqtgraph.pyqtgraph.opengl.shaders  import initShaders
from ...pyqtgraph.pyqtgraph.opengl          import shaders
from ...simpleplot_widgets.SimpleHistogramLUTWidget import HistogramLUTWidget
from ...simpleplot_widgets.SimplePlotGradientEditorItem import GradientEditorItem

from OpenGL import GL
from ...model.parameter_class       import ParameterHandler 

class ShaderConstructor(ParameterHandler):
    '''
    Opengl supports shaders and therefore it is 
    required to write a shader generator based 
    on the shader program of pyqtgraph
    '''
    def __init__(self):
        ParameterHandler.__init__(self, 'Shader')

        self._gradient_item  = GradientEditorItem()
        self._positions      = [0,0.25,0.5,0.75,1.]
        self._colors        = [
            [0.,1.,1., 1.],
            [0.,0.,1., 1.],
            [0.,1.,0., 1.],
            [1.,0.,0., 1.],
            [1.,0.,1., 1.]]
        state = {
            'ticks':[[self._positions[i],np.array(self._colors)[i]*255] 
            for i in range(len(self._colors))],
            'mode' : 'rgb'}
        self._gradient_item.restoreState(state)

        self._range_auto        = [True,True,True]
        self._range             = [[0.,1.],[0.,1.],[0.,1.]]
        self._factors           = [1.,0.]
        self._epsilon           = 1.e-6
        self._light_active      = True
        self._light_direction   = [20,0,-20]
        self._link_widget       = None

        self._setShaderParameters()

    def _setShaderParameters(self):
        '''
        set the parameters
        '''
        self.addParameter(
            'Gradient', self._gradient_item, 
            method = self.runShader)

        self.addParameter(
            'Range auto', [True,True,True],
            names = ['x', 'y', 'z'],
            method = self.runShader)

        self.addParameter(
            'Range x values', [0.,1.],
            names = ['min', 'max'],
            method = self.runShader)

        self.addParameter(
            'Range y values', [0.,1.],
            names = ['min', 'max'],
            method = self.runShader)

        self.addParameter(
            'Range z values', [0.,1.],
            names = ['min', 'max'],
            method = self.runShader)

        self.addParameter(
            'Range factors', [1.0,0.],
            names = ['factor max', 'factor min'],
            method = self.runShader)

        self.addParameter(
            'Range epsilon',  1.e-6,
            method = self.runShader)

        self.addParameter(
            'Light active', True,
            names = ['factor max', 'factor min'],
            method = self.runShader)

        self.addParameter(
            'Light direction', [20.,0.,+20.],
            names = ['x', 'y', 'z'],
            method = self.runShader)

    def runShader(self):
        '''
        Set the colors of the shader display
        '''
        self._setColors()
        self._setRangeAuto()
        self._setLight()
        self.parent().setColor()

        if not self._link_widget is None:
            self._link_widget.sigLookupTableChanged.disconnect(self._externalGradientChange)
            self._link_widget.sigLevelsChanged.disconnect(self._externalLevelChange)
            self._link_widget.restoreState({
                'mode'      : 'mono',
                'gradient'  : self['Gradient'].saveState(),
                'levels'    : self.parent().parent()._plot_data.getBounds()[2] + [None]})

            self._link_widget.sigLookupTableChanged.connect(self._externalGradientChange)
            self._link_widget.sigLevelsChanged.connect(self._externalLevelChange)

    def getHistogramItem(self):
        '''
        generates and returns the linked histogram item
        '''
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, 
            QtGui.QSizePolicy.Expanding)

        histogram  = HistogramLUTWidget()

        histogram.axis.setStyle(autoExpandTextSpace = False)
        histogram.setSizePolicy(sizePolicy)
        self._linkWidget(histogram)

        return histogram

    def _linkWidget(self, widget):
        '''
        This allows the shader editor to be linked to 
        a Histogram LUT item and vice versa
        '''
        self._link_widget = widget
        self._link_widget.restoreState({
            'mode'      : 'mono',
            'gradient'  : self._gradient_item.saveState(),
            'levels'    : self.parent().parent()._plot_data.getBounds()[2] + [None]})
        self.items['Range auto'].updateValue(
            [True, True, False],
            method = False)
        self._externalLevelChange()

        self._link_widget.sigLookupTableChanged.connect(self._externalGradientChange)
        self._link_widget.sigLevelsChanged.connect(self._externalLevelChange)
        
    def _unlinkWidget(self):
        '''
        This allows the shader editor to be unlinked from 
        a Histogram LUT item and vice versa
        '''
        if not self._link_widget is None:
            self._link_widget.sigLookupTableChanged.disconnect(self._externalGradientChange)
            self._link_widget.sigLevelsChanged.disconnect(self._externalLevelChange)
            self._link_widget = None

    def _externalLevelChange(self):
        '''
        Allows to change the local gradient item from an 
        external source
        '''
        self._link_widget.plots[0].setVisible(True)
        self.items['Range z values'].updateValue(
            self._link_widget.getLevels(),
            method = False)
            
        self._link_widget.plots[0].setData(
            *self.parent().parent().childFromName('Data').getHistogram())
        self._setColors()
        self._setRangeAuto()
        self._setLight()
        self.parent().setColor()

    def _externalGradientChange(self):
        '''
        Allows to change the local gradient item from an 
        external source
        '''
        self.items['Gradient'].updateValue(
            self._link_widget.gradient, 
            method = False)
        self._setColors()
        self._setRangeAuto()
        self._setLight()
        self.parent().setColor()

    def _setColors(self):
        '''
        Set the colors of the shader display
        
        Parameters
        ----------
        colors : list of 4d lists of color values [0. to 1.]
            The colors ar each position

        position: list of int [0. to 1.]
            The position of each color
        '''
        state       = self['Gradient'].saveState()
        positions   = [element[0] for element in state['ticks']]
        colors      = [list(np.array(element[1])/255) for element in state['ticks']]
        self._colors      = np.array([c for _,c in sorted(zip(positions, colors))])
        self._positions   = np.array(sorted(positions))

    def _setRangeAuto(self):
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
        self._range_auto = self['Range auto']
        self._factors    = self['Range factors']
        self._epsilon    = self['Range epsilon']
        self._setRangeValue()

    def _setRangeValue(self):
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
        bounds = self.parent().parent()._plot_data.getBounds()

        if self._range_auto[0]:
            self._range[0] = [float(bounds[0][0])-self._epsilon, float(bounds[0][1])+self._epsilon]
            # self.items['Range x values'].updateValue(
            # [float(bounds[0][0])-self._epsilon, float(bounds[0][1])+self._epsilon],
            # method = False)
        else:
            self._range[0] = list(self['Range x values'])

        if self._range_auto[1]:
            self._range[1] = [float(bounds[1][0])-self._epsilon, float(bounds[1][1])+self._epsilon]
            # self.items['Range y values'].updateValue(
            # [float(bounds[1][0])-self._epsilon, float(bounds[1][1])+self._epsilon],
            # method = False)
        else:
            self._range[1] = list(self['Range y values'])

        if self._range_auto[2]:
            self._range[2] = [float(bounds[2][0])-self._epsilon, float(bounds[2][1])+self._epsilon]
            # self.items['Range z values'].updateValue(
            # [float(bounds[2][0])-self._epsilon, float(bounds[2][1])+self._epsilon],
            # method = False)
        else:
            self._range[2] = list(self['Range z values'])

    def _setLight(self):
        '''
        Set the colors of the shader display
        
        Parameters
        ----------
        active : Bool
            Should the light be turned on

        direction: list 
            What is the direction of the light
        '''
        self._light_active      = self['Light active']
        self._light_direction   = self['Light direction']

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
        elif name == 'orientation':
            return self.orientationShader()
        elif name == 'length':
            return self.vecLengthShader()
        elif name == 'edgeShader':
            return self.edgeShader()
        elif name == 'light':
            return self.lightShader()

    def edgeShader(self):
        '''
        produce the height shader
        '''
        # out varying vec4 color;    
        fragment_text = (
            """
            varying vec3 normal;
            void main() {
                vec4 color = gl_Color;
                float s = pow(normal.x*normal.x + normal.y*normal.y, 2.0);
                color.x = color.x + s * (1.0-color.x);
                color.y = color.y + s * (1.0-color.y);
                color.z = color.z + s * (1.0-color.z);

            """)

        if self._light_active:
            fragment_text += ("""
                float p = dot(normalize(vec3("""
                +str(self._light_direction[0])+","
                +str(self._light_direction[1])+","
                +str(self._light_direction[2])+""")),normal);
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);""")

        fragment_text += ("""gl_FragColor = color;}""")

        # make the vertex
        vertex  = shaders.VertexShader(
            """
            varying vec3 normal;
            void main() {
                // compute here for use in fragment shader
                normal = normalize(gl_NormalMatrix * gl_Normal);
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                gl_Position = ftransform();
            }
            """)

        #set shader up
        fragment    = shaders.FragmentShader(fragment_text)

        #set shader up
        to_use = shaders.ShaderProgram(
            'edgeShader', 
            [vertex, fragment])
            
        return to_use

    def lightShader(self):
        '''
        produce the height shader
        '''
        uniforms = {}

        start_text = '' 
        fragment_text = (
            """
            varying vec3 pos;
            varying vec3 normal;
            varying vec4 color;
            void main() {
                float z_local;
            """)

        if self._light_active:
            fragment_text += ("""
                float p = dot(normalize(vec3("""
                +str(self._light_direction[0])+","
                +str(self._light_direction[1])+","
                +str(self._light_direction[2])+""")),normal);
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);""")

        fragment_text += ("""gl_FragColor = color;}""")

        # make the vertex
        vertex  = shaders.VertexShader(
            """
            varying vec3 pos;
            varying vec3 normal;
            varying vec4 color;
            void main() {
                normal = normalize(gl_NormalMatrix * gl_Normal);
                pos = vec3(gl_Vertex);
                color = gl_Color;
                gl_Position = ftransform();
            }""")

        #set shader up
        fragment    = shaders.FragmentShader(
            start_text + fragment_text)

        #set shader up
        to_use = shaders.ShaderProgram(
            'light', 
            [vertex, fragment], 
            uniforms = uniforms)
            
        return to_use

    def heightShader(self):
        '''
        produce the height shader
        '''
        uniforms = {}

        uniforms['position'] = self._positions
        uniforms['factor']   = [
            1./np.abs(
                self._range[2][1] - self._range[2][0] 
                if not self._range[2][1] == self._range[2][0] else 1.),
            self._range[2][0]]
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
            varying vec3 pos;
            varying vec3 normal;
            void main() {
                vec4 color = gl_Color;
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
                    color.w = 1.0; 
                }
                """)
            
            temp_1 = temp_1.replace('color_1', 'color_'+str(i+1))
            temp_1 = temp_1.replace('color_0', 'color_'+str(i))
            temp_1 = temp_1.replace('position[1]', 'position['+str(i+1)+']')
            temp_1 = temp_1.replace('position[0]', 'position['+str(i)+']')

            fragment_text += str(temp_1)
        
        #the start
        temp_1 = (
            """
            if (z_norm < position[0]){;
                color.x = 0.;
                color.y = 0.;
                color.z = 0.;
                color.w = 0.; 
            }""")

        fragment_text += str(temp_1)

        #the end
        temp_1 = (
            """
            if (z_norm > position[0]){
                color.x = 0.;
                color.y = 0.;
                color.z = 0.;
                color.w = 0.; 
            }""")

        temp_1 = temp_1.replace('position[0]', 'position['+str(len(self._colors)-1)+']')
        fragment_text += str(temp_1)

        if self._light_active:
            fragment_text += ("""
                float p = dot(normalize(vec3("""
                +str(self._light_direction[0])+","
                +str(self._light_direction[1])+","
                +str(self._light_direction[2])+""")),normal);
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);""")

        fragment_text += ("""gl_FragColor = color;}""")

        # make the vertex
        vertex  = shaders.VertexShader(
            """
            varying vec3 pos;
            varying vec3 normal;
            void main() {
                normal = normalize(gl_NormalMatrix * gl_Normal);
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                pos = vec3( gl_Vertex);
                gl_Position = ftransform();
            }""")

        #set shader up
        fragment    = shaders.FragmentShader(
            start_text + fragment_text)

        #set shader up
        to_use = shaders.ShaderProgram(
            'height', 
            [vertex, fragment], 
            uniforms = uniforms)
            
        return to_use

    def orientationShader(self):
        '''
        produce the orientation shader
        '''
        uniforms = {}
        uniforms['position'] = self._positions
        for i,element in enumerate(self._colors):
            uniforms['color_'+str(i)] = element

        fragment_text = ''

        fragment_text+=(
            """
            uniform float position[1];
            """)
        fragment_text = fragment_text.replace('position[1]', 'position['+str(len(self._positions))+']')

        for i in range(len(self._colors)):
            temp_0 = (
                """uniform float color_0[3];"""
                )
            temp_0 = temp_0.replace('color_0', 'color_'+str(i))
            fragment_text += str(temp_0)

    
        # out varying vec4 color;    
        fragment_text += (
            """
            varying vec4 pos;
            varying vec3 normal;
            void main() {
                float o = position[0];
                vec4 color;
                color.x = color_0[0];
                color.y = color_0[1];
                color.z = color_0[2];
                color.w = 1.;

                vec3 x = vec3(1,0,0);
                vec3 y = vec3(0,1,0);
                vec3 z = vec3(0,0,1);

                float altitude_scalar = dot(normal, z) / length(z);
                float altitude_angle  = acos( altitude_scalar / length(normal) );

                vec3 plane_normal = normalize(normal - altitude_scalar * z);

                float plane_scalar_0 = dot(plane_normal, x) / length(x);
                float plane_angle_0  = acos( plane_scalar_0 / length(plane_normal) );

                float plane_scalar_1 = dot(plane_normal, y) / length(y);
                float plane_angle_1  = acos( plane_scalar_1 / length(plane_normal) );

                float azimuth = radians(90.) - altitude_angle;
                float orbit   = plane_angle_0;
                if(plane_angle_0 > radians(90.) ){
                    orbit = orbit + radians(180.);
                }
                orbit = orbit / radians(360.);
                float z_local;
            """)

        for i in range(len(self._colors)-1):
            temp_1 = (
                """
                if (orbit >= position[0] && orbit <= position[1]){
                    z_local = (orbit-position[0])/(position[1]-position[0]);
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
            fragment_text += temp_1
        
        if self._light_active:
            fragment_text += ("""
                float p = dot(normalize(vec3("""
                +str(self._light_direction[0])+","
                +str(self._light_direction[1])+","
                +str(self._light_direction[2])+""")),normal);
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);""")

        fragment_text += ("""gl_FragColor = color;}""")

        # make the vertex
        vertex  = shaders.VertexShader(
            """
            varying vec4 pos;
            varying vec3 normal;
            void main() {
                normal = gl_Normal;
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                pos = gl_Vertex;
                gl_Position = ftransform();
            }
            """)

        #set shader up
        fragment    = shaders.FragmentShader(fragment_text)

        #set shader up
        to_use      = shaders.ShaderProgram(
            'orientation', 
            [vertex, fragment], 
            uniforms = uniforms)

        return to_use

    def vecLengthShader(self):
        '''
        produce the height shader
        '''
        uniforms = {}

        # uniforms['position'] = self._positions
        # uniforms['factor']   = [
        #     1./np.abs(self._range[1]-self._range[0]),
        #     self._range[0]]
        # for i,element in enumerate(self._colors):
        #     uniforms['color_'+str(i)] = element

        # start_text = (
        #     """
        #     uniform float position[1];
        #     uniform float factor[2];
        #     """)
        # start_text = start_text.replace('position[1]', 'position['+str(len(self._positions))+']')

        # for i in range(len(self._colors)):
        #     temp_0 = (
        #         """uniform float color_0[3];"""
        #         )
        #     temp_0 = temp_0.replace('color_0', 'color_'+str(i))
        #     start_text += str(temp_0)
        start_text = ''

        fragment_text = (
            """
            varying vec4 v_color;
            void main() {
            """)

        # for i in range(len(self._colors)-1):
        #     temp_1 = (
        #         """
        #         if (z_norm >= position[0] && z_norm <= position[1] ){
        #             z_local = (z_norm-position[0])/(position[1]-position[0]);
        #             color.x = (color_1[0]-color_0[0])*z_local + color_0[0];
        #             color.y = (color_1[1]-color_0[1])*z_local + color_0[1];
        #             color.z = (color_1[2]-color_0[2])*z_local + color_0[2];
        #             color.w = 1.0; 
        #         }
        #         """)
            
        #     temp_1 = temp_1.replace('color_1', 'color_'+str(i+1))
        #     temp_1 = temp_1.replace('color_0', 'color_'+str(i))
        #     temp_1 = temp_1.replace('position[1]', 'position['+str(i+1)+']')
        #     temp_1 = temp_1.replace('position[0]', 'position['+str(i)+']')

        #     fragment_text += str(temp_1)
        
        fragment_text += ('gl_FragColor = v_color;}')

        # make the vertex
        vertex  = shaders.VertexShader(
            """
            attribute vec3 position_vec;
            attribute vec4 color_vec;
            varying vec4 v_color;
            void main() {
                gl_Position = vec4(position_vec,1);
                v_color= color_vec;
            }
            """)

        #set shader up
        fragment    = shaders.FragmentShader(
            start_text + fragment_text)

        #set shader up
        to_use = shaders.ShaderProgram(
            'length', 
            [vertex, fragment])

        return to_use

