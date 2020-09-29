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
import decimal
from pathlib import Path
import numpy as np

SI_PREFIXES = str('yzafpnµm kMGTPEZY')
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'

# Personal imports
from ..views_3D.graphics_view_3D            import GraphicsView3D

class AxisView3D(GraphicsView3D):
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

        self._parameters['draw_axis']           = True
        self._parameters['draw_ticks']          = True
        self._parameters['draw_values']         = False
        self._parameters['draw_title']          = False

        self._parameters['axis_length']         = np.array([-5., 5.])
        self._parameters['axis_width']          = np.array([0.05])
        self._parameters['axis_color']          = np.array([1,0,0,1])
        self._parameters['axis_direction']      = np.array([1,0,0])
        self._parameters['axis_center']         = np.array([0,0,0])
        self._parameters['axis_arrow_width']    = np.array([0.1])
        self._parameters['axis_arrow_length']   = np.array([0.2])

        self._parameters['tick_length']         = np.array([0.5])
        self._parameters['tick_direction']      = np.array([0,1,0])
        self._parameters['tick_color']          = np.array([1,0,0,1])
        self._parameters['tick_width']          = np.array([0.05])

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram(
            "axis",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader('axis'),
            geometry_shader = self._geometryShader('axis'))

        self._createProgram(
            "ticks",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader('ticks'),
            geometry_shader = self._geometryShader('ticks'))

        self._createProgram(
            "values",
            vert_shader     = self._vertexShader(),
            frag_shader     = self._fragmentShader('labels'),
            geometry_shader = self._geometryShader('labels'))

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
        self._updateAutoSIPrefix(
            self._parameters['axis_length'][0], 
            self._parameters['axis_length'][1])

        self._tick_positions_1d = self._tickValues(
            self._parameters['axis_length'][0], 
            self._parameters['axis_length'][1], 
            self._parameters['axis_length'][1] 
            - self._parameters['axis_length'][0])

        ticks_positions_3d = np.zeros((self._tick_positions_1d.shape[0], 3))
        ticks_positions_3d[:,0] = self._tick_positions_1d

        self._createVBO("axis", np.array([[-1,0,0],[1,0,0]]))
        self._createVAO("axis", {"axis": ["3f", "in_vert"]})
        self._createVBO("ticks", ticks_positions_3d)
        self._createVAO("ticks", {"ticks": ["3f", "in_vert"]})
        self._createVAO("values", {"ticks": ["3f", "in_vert"]})

    def paint(self):
        '''
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        '''
        self.context().disable(moderngl.CULL_FACE)

        if self._parameters['draw_axis']:
            self._vaos['axis'].render(mode = moderngl.LINE_STRIP)

        if self._parameters['draw_ticks']:
            self._vaos['ticks'].render(mode = moderngl.POINTS)

        if self._parameters['draw_values']:
            self._vaos['values'].render(mode = moderngl.LINE_STRIP)
            
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
        if key == 'axis':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_fragment_axis.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'ticks':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_fragment_ticks.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'labels':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_fragment_labels.glsl')
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
        if key == 'axis':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_geometry_axis.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'ticks':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_geometry_ticks.glsl')
            output = file.read()
            file.close()
            return output
        elif key == 'labels':
            file = open(
                Path(__file__).resolve().parent/'shader_scripts'/'axis_geometry_labels.glsl')
            output = file.read()
            file.close()
            return output
        else:
            return None


    def _tickValues(self, minVal, maxVal, size):
        """
        Return the values and spacing of ticks to draw::
        
            [  
                (spacing, [major ticks]), 
                (spacing, [minor ticks]), 
                ... 
            ]
        
        By default, this method calls tickSpacing to determine the correct tick locations.
        This is a good method to override in subclasses.
        """
        minVal, maxVal = sorted((minVal, maxVal))
            
        ticks = []
        tickLevels = self._tickSpacing(minVal, maxVal, size)
        allValues = np.array([])
        for i in range(len(tickLevels)):
            spacing, offset = tickLevels[i]
            start = (np.ceil((minVal-offset) / spacing) * spacing) + offset
            num = int((maxVal-start) / spacing) + 1
            values = (np.arange(num) * spacing + start) / self.scale
            values = list(filter(lambda x: all(np.abs(allValues-x) > spacing*0.01), values) )
            allValues = np.concatenate([allValues, values])
            ticks.append((spacing/self.scale, values))
        return allValues

    def _tickSpacing(self, minVal, maxVal, size):
        """
        Return values describing the desired spacing and offset of ticks.
        
        This method is called whenever the axis needs to be redrawn and is a 
        good method to override in subclasses that require control over tick locations.
        
        The return value must be a list of tuples, one for each set of ticks::
        
            [
                (major tick spacing, offset),
                (minor tick spacing, offset),
                (sub-minor tick spacing, offset),
                ...
            ]
        """
        minVal *= self.scale
        maxVal *= self.scale

        dif = abs(maxVal - minVal)
        if dif == 0:
            return []
        
        ## decide optimal minor tick spacing in pixels (this is just aesthetics)
        optimalTickCount = max(4., np.log(max(size,1e-8)))
        ## optimal minor tick spacing 
        optimalSpacing = dif / optimalTickCount
        ## the largest power-of-10 spacing which is smaller than optimal
        p10unit = 10 ** np.floor(np.log10(optimalSpacing))
        ## Determine major/minor tick spacings which flank the optimal spacing.
        intervals = np.array([1., 2., 10., 20., 100.]) * p10unit
        minorIndex = 0
        while intervals[minorIndex+1] <= optimalSpacing:
            minorIndex += 1
            
        levels = [
            (intervals[minorIndex+2], 0),
            (intervals[minorIndex+1], 0),
            #(intervals[minorIndex], 0)    ## Pretty, but eats up CPU
        ]
        ## decide whether to include the last level of ticks
        minSpacing = min(size / 20., 30.)
        maxTickCount = size / minSpacing
        if dif / intervals[minorIndex] <= maxTickCount:
            levels.append((intervals[minorIndex], 0))
        return levels


    def _updateAutoSIPrefix(self, minVal, manVal):
        self.scale  = self.siScale(max(abs(minVal), abs(manVal)))[0]
        return self.scale

    def siScale(self, x, minVal=1e-25, allowUnicode=True):
        """
        Return the recommended scale factor and SI prefix string for x.
        
        Example::
        
            siScale(0.0001)   # returns (1e6, 'μ')
            # This indicates that the number 0.0001 is best represented as 0.0001 * 1e6 = 100 μUnits
        """
        
        if isinstance(x, decimal.Decimal):
            x = float(x)
            
        try:
            if np.isnan(x) or np.isinf(x):
                return(1, '')
        except:
            print(x, type(x))
            raise
        if abs(x) < minVal:
            m = 0
            x = 0
        else:
            m = int(np.clip(np.floor(np.log(abs(x))/np.log(1000)), -9.0, 9.0))
        
        if m == 0:
            pref = ''
        elif m < -8 or m > 8:
            pref = 'e%d' % (m*3)
        else:
            if allowUnicode:
                pref = SI_PREFIXES[m+8]
            else:
                pref = SI_PREFIXES_ASCII[m+8]
        p = .001**m
        
        return (p, pref)
