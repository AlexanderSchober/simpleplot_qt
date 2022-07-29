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
import numpy as np
import OpenGL.GL as gl
import moderngl

# Personal imports
from .graphics_view_3D import GraphicsView3D
from ..graphics_geometry.helper_functions import createTubes
from ..graphics_geometry.helper_functions import assembleFaces

class PieView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

        self._parameters['positions']       = [0,0,0]
        self._parameters['angle_range']     = [[0,180]]
        self._parameters['radial_range']    = [[1,2]]
        self._parameters['brush_color']     = QtGui.QColor("black")
        self._parameters['pen_color']       = QtGui.QColor("black")
        self._parameters['pen_thickness']   = 0.1

    def initializeGL(self)->None:
        '''
        Initialize the OpenGl vbo objects as well as the 
        first data components
        '''
        self._createProgram("tiles")
        self._createVBO("tiles", np.zeros((36,3)), np.zeros((36,3)), np.zeros((36,4)))
        self._createVAO("tiles", {"tiles": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

        self._createProgram("border")
        self._createVBO("border", np.zeros((100,3)), np.zeros((100,3)), np.zeros((100,4)))
        self._createIBO("border", np.zeros((300)))
        self._createVAO("border", {"border": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

        self.setMVP()
        self.setLight()
        self.setData()

    def setData(self, **kwargs)->None:
        '''
        Set the data for display
        '''
        self._parameters.update(kwargs)
        self._generateBases()
        self._processTiles()
        self._updateTilesVBO()
        if self._parameters['pen_thickness']>0:
            self._processBorders()
            self._updateBordersVBO()
        self.update()

    def paint(self)->None:
        '''
        This method will set the visual representation of 
        the opengl opbject
        '''
        self._paintTiles()
        self._paintBorders()

    def _generateBases(self):
        '''
        Generate the bases used geenrating the elements
        easier afterwards
        '''
        self._multiplication = 10

    def _processTiles(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        packet          = self._multiplication*2
        rad_num         = len(self._parameters['radial_range'])
        angle_num       = len(self._parameters['angle_range'])
        angles          = np.array(self._parameters['angle_range']) * np.pi / 180.
        radial          = np.array(self._parameters['radial_range'])
        
        self._vertices  = np.zeros((packet * rad_num * angle_num,3))
        for i in range(angle_num):
            angle_sub_division  = np.linspace(
                angles[i,0], angles[i,1], self._multiplication, dtype= np.float32)
            norm_positions      = np.zeros(
                (angle_sub_division.shape[0],3), dtype= np.float32)
            norm_positions[:,0] = np.cos(angle_sub_division)
            norm_positions[:,1] = np.sin(angle_sub_division)

            for j in range(rad_num):
                indice = i*packet*rad_num
                self._vertices[indice+j*packet:indice+(j+1)*packet:2] = norm_positions*radial[j,0]
                self._vertices[indice+j*packet+1:indice+(j+1)*packet:2] =  norm_positions*radial[j,1]
                
        self._faces = np.zeros((3*2*(self._multiplication-1)*rad_num*angle_num), dtype=np.int)
        fact_6 = 6*(self._multiplication-1)
        fact_2 = 2*(self._multiplication-1)
        for i in range(angle_num):
            for j in range(rad_num):
                for k in range(self._multiplication-1):
                    offset_i = (fact_6*rad_num*i + fact_6*j + 6*k)
                    offset_f = (fact_6*rad_num*i + fact_6*j + 6*(k+1))
                    step = (fact_2*rad_num*i + fact_2*j + 2*k +2*(i*rad_num+j))
                    self._faces[offset_i:offset_f] = np.array([0,1,2,1,3,2])+step

        self._colors        = np.zeros((self._vertices.shape[0], 4))
        self._colors[:]     = np.array([val/255 for val in self._parameters['brush_color'].getRgb()])
        self._normals        = np.zeros((self._vertices.shape[0], 3))
        self._normals[:]     = np.array([0,0,1])

    def _updateTilesVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createIBO("tiles", self._faces)
        self._createVBO("tiles", self._vertices, self._normals, self._colors)
        self._createVAO("tiles", {"tiles": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

    def _processBorders(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        packet          = self._multiplication*2
        rad_num         = len(self._parameters['radial_range'])
        angle_num       = len(self._parameters['angle_range'])
        angles          = np.array(self._parameters['angle_range']) * np.pi / 180.
        radial          = np.array(self._parameters['radial_range'])
        
        tube_array = []
        for i in range(angle_num):
            angle_sub_division  = np.linspace(
                angles[i,0], angles[i,1], self._multiplication, dtype= np.float32)
            norm_positions      = np.zeros(
                (angle_sub_division.shape[0],3), dtype= np.float32)
            norm_positions[:,0] = np.cos(angle_sub_division)
            norm_positions[:,1] = np.sin(angle_sub_division)

            for j in range(rad_num):
                positions = np.concatenate(
                    (norm_positions*radial[j,0],norm_positions[::-1]*radial[j,1]))
                line_base = np.array(list([[i,i+1] for i in range(packet-1)]+[[packet-1,0]]), dtype=np.int).flatten()
                tube_array.append(createTubes(
                    positions[line_base], 
                    width = self._parameters['pen_thickness'],
                    close = False, connect = [True, True]))
            
        self._tube_vertices, self._tube_faces = assembleFaces(tube_array)
        self._tube_colors    = np.zeros(
            (self._tube_vertices.shape[0], 4))
        self._tube_colors[:] = np.array(
            [val/255 for val in self._parameters['pen_color'].getRgb()])

    def _updateBordersVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createIBO(
            "border", self._tube_faces)
        self._createVBO(
            "border", self._tube_vertices, 
            np.zeros(self._tube_vertices.shape), self._tube_colors)
        self._createVAO(
            "border", {"border": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

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

    def _paintBorders(self)->None:
        '''
        This will paint the lines around the items.
        '''
        if self._parameters['pen_thickness']>0:
            self._vaos['border'].render()

