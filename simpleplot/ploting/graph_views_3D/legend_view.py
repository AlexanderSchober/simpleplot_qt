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
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************

# General imports
import moderngl
import numpy as np
from pathlib import Path
from typing import List
from PyQt5 import QtGui

# Personal imports
from .font_to_bitmap import getFontPaths, Font
from ..views_3D.graphics_view_3D import GraphicsView3D


class LegendView(GraphicsView3D):
    def __init__(self,**opts):
        """
        """
        super().__init__(**opts)
        self._family_to_path = getFontPaths()
        self._initParameters()

    def _initParameters(self):
        """
        This is a placeholder for the parameter
        initialisation
        """
        self._need_update = False
        self.width = 0
        self.height = 0
        
        self._parameters['draw_legend'] = True
        self._parameters['legend_empty'] = True
        self._parameters['legend_font'] = 'Arial'
        self._parameters['legend_font_size'] = 12
        self._parameters['legend_margins'] = (5, 5, 5, 5)
        self._parameters['legend_margin_h'] = 5
        self._parameters['legend_margin_v'] = 2
        self._parameters['legend_back_color'] = np.array([200, 200, 200, 256], dtype=np.uint16)
        self._parameters['legend_text_color'] = np.array([0, 0, 0, 256], dtype=np.uint16)
        self._parameters['legend_dist_edge']  = [10, 10]

    def initializeGL(self) -> None:
        """
        Unitialize the OpenGl states
        """
        self._createProgram(
            "legend",
            vert_shader=self._vertexShader('legend'),
            geometry_shader=self._geometryShader('legend'),
            frag_shader=self._fragmentShader('legend'))

        self.setUniforms(**self._parameters)
        self.setLegend([], [])
        self._updateLegend()
        self.setMVP()
        self.setLight()

    def setProperties(self, **kwargs) -> None:
        """
        Set the properties to diplay the graph
        """
        self._parameters.update(kwargs)
        self.setUniforms(**self._parameters)
        self._need_update = True
        
    def setLegendFont(self, font: str, size: int) -> None:
        """
        his method will effectively set the font used for 
        managing the labels
        """
        self.legend_font = Font(self._family_to_path[font] if font != 'MS Shell Dlg 2'
                             else self._family_to_path['Arial'], size)
        
    def QPixmapToArray(self, pixmap):
        ## Get the size of the current pixmap
        size = pixmap.size()
        h = size.width()
        w = size.height()

        ## Get the QImage Item and convert it to a byte string
        qimg = pixmap.toImage()
        byte_str = qimg.bits().asstring(w*h*4)

        ## Using the np.frombuffer function to convert the byte string into an np array
        img = np.frombuffer(byte_str, dtype=np.uint8).reshape((w,h,4))

        return img

    def setLegend(self, icons:List[QtGui.QPixmap], titles:List[str])->None:
        '''
        Here we are getting all the icons and titles to
        generate a new legend bitmap. The generatiomn of a 
        bitmap is essential as it avoids that the legend is 
        perpetually redrawn on every call.
        '''
        
        if len(icons) == 0 or len(titles) == 0:
            self._parameters['legend_empty'] = True
            return
        elif len(icons) != len(titles):
            self._parameters['legend_empty'] = True
            return
        else:
            self._parameters['legend_empty'] = False
            
        
        self.setLegendFont(
            self._parameters['legend_font'],
            self._parameters['legend_font_size'])
        
        icons = [self.QPixmapToArray(icon) for icon in icons]
        
        title_texts = []
        for text in titles:
            render_output = self.legend_font.renderTextBitmap(text)
            temp_bitmap = np.repeat(render_output[:, :, np.newaxis], 4, axis=2)
            temp_fullmap = np.zeros(temp_bitmap.shape, dtype=np.uint16)
            temp_fullmap[:, :, :] = (temp_bitmap/256)*self._parameters['legend_text_color']+(1-(temp_bitmap/256))*self._parameters['legend_back_color']

            title_texts.append(temp_fullmap)
            
        self.width = sum([
            max([icon.shape[1] for icon in icons]),
            self._parameters['legend_margin_h'],
            max([title_text.shape[1] for title_text in title_texts]),
            self._parameters['legend_margins'][0],
            self._parameters['legend_margins'][1]])
        self.height = sum([
            sum([max([icons[i].shape[0],title_texts[i].shape[0]]) for i in range(len(icons))]),
            (len(icons) - 1) * self._parameters['legend_margin_v'],
            self._parameters['legend_margins'][2],
            self._parameters['legend_margins'][3]])
        
        self.legend_bitmap = np.zeros((self.height, self.width, 4), dtype=np.uint16)
        self.legend_bitmap[:, :, :] = self._parameters['legend_back_color']
        self.start = [self._parameters['legend_margins'][2], self._parameters['legend_margins'][0]]
        for icon, text in zip(icons, title_texts):
            
            baseline = self.start[0] + int(max([icon.shape[0], text.shape[0]])/2) 
            addition_icon = int(icon.shape[0]/2)%2
            addition_text = int(text.shape[0]/2)%2
            
            self.legend_bitmap[
                baseline-int(icon.shape[0]/2):baseline+int(icon.shape[0]/2)+addition_icon,
                self.start[1]:self.start[1]+icon.shape[1]] = icon
           
            self.start = [
                self.start[0],
                self.start[1] + icon.shape[1] + self._parameters['legend_margin_h']]
            
            self.legend_bitmap[
                baseline-int(text.shape[0]/2):baseline+int(text.shape[0]/2)+addition_text,
                self.start[1]:self.start[1]+text.shape[1]] = text
            
            self.start = [
                self.start[0] + max([icon.shape[0], text.shape[0]]) + self._parameters['legend_margin_v'],
                self._parameters['legend_margins'][0]]
            
        self.texture_legend = self.context().texture3d(
            (self.legend_bitmap.shape[2], self.legend_bitmap.shape[1], self.legend_bitmap.shape[0]), 1,
            (self.legend_bitmap / 256).astype('f4').tobytes(),
            dtype='f4')
        
        # print(self._parameters['legend_back_color'], self.legend_bitmap.flatten().tolist())
        # from PIL import Image
        # im = Image.fromarray(self.legend_bitmap)
        # im.save("your_file.png")
        
    def _updateLegend(self) -> None:
        """
        Here we will order the software to inject the main data into
        the present buffers
        """

        self._createVBO("legend", np.array([[
            self._parameters['legend_dist_edge'][0],
            self._parameters['legend_dist_edge'][1],
            self.width,
            self.height]], dtype='f4'))
        self._createVAO("legend", {"legend": ["4f", "in_vert"]})
        
        self.setUniforms(
            legend_width=np.array([self.width], dtype='f4'),
            legend_heigh=np.array([self.height], dtype='f4')
            )

    def paint(self):
        """
        Paint the elements of the axis.
        This includes the axis line,
        the ticks and the lables
        """
        self.context().disable(moderngl.CULL_FACE)
        
        if self._need_update:
            self._updateLegend()
        
        if self._parameters['draw_legend'] and not self._parameters['legend_empty']:
            self.texture_legend.use(0)
            self._programs['legend']['legend_texture'].value = 0
            self._programs['legend']['viewport_size'].value = tuple(self.context().viewport[2:])
            self._vaos['legend'].render(mode=moderngl.POINTS)
            
        self.context().enable(moderngl.CULL_FACE)

    def _vertexShader(self, key: str = None) -> str:
        """
        Returns the vertex shader for this particular item
        """
        if key == 'legend':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'legend_vertex.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None

    def _fragmentShader(self, key: str = 'legend') -> str:
        """
        Returns the fragment shader for this particular item
        """
        if key == 'legend':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'legend_fragment.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None
        
    def _geometryShader(self, key: str = 'legend') -> str:
        """
        Returns the fragment shader for this particular item

        Parameters:
        ---------------------
        key : str
            The shader to return
        """
        if key == 'legend':
            file = open(
                Path(__file__).resolve().parent / 'shader_scripts' / 'legend_geometry.glsl')
            output = file.read()
            file.close()
            return output
        
        else:
            return None
        