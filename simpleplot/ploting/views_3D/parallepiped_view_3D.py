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

# Personal imports
from .graphics_view_3D import GraphicsView3D
from ..graphics_geometry.helper_functions import createTubes
from ..graphics_geometry.helper_functions import assembleFaces
from ..graphics_geometry.helper_functions import createSphere
from ..graphics_geometry.helper_functions import faceNormals
        
class ParallepipedView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

        self._parameters['dimensions']      = [1.,1., 1.]
        self._parameters['angles']          = [90., 90., 90.]
        self._parameters['positions']       = [0,0,0]
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

    def _generateBases(self)->None:
        '''
        Generate the bases used geenrating the elements
        easier afterwards
        '''
        self._tube_precision = 10

    def _processTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        a = np.array([
            self._parameters['dimensions'][0],0 , 0], dtype=np.float32)
        b = np.array([
            self._parameters['dimensions'][1]*np.cos(self._parameters['angles'][0]*np.pi/180),
            self._parameters['dimensions'][1]*np.sin(self._parameters['angles'][0]*np.pi/180), 0], dtype=np.float32)
        v = (
            np.cos(self._parameters['angles'][1]*np.pi/180)*a/np.linalg.norm(a) 
            + np.cos(self._parameters['angles'][2]*np.pi/180)*b/np.linalg.norm(b))
        angle = np.arccos(np.linalg.norm(v)/ np.linalg.norm(a+b))

        c = (
            np.cos(angle)*self._parameters['dimensions'][2]
            *(a+b)/np.linalg.norm(a+b)
            +np.sin(angle)*self._parameters['dimensions'][2]
            *np.array([0,0,1], dtype=np.float32))

        pos = np.array([0,0,0], dtype=np.float32)
        a /= 2
        b /= 2
        c /= 2

        self._edges = np.array([
            pos-a-b-c, pos-a-b+c, pos-a+b-c, pos-a+b+c,
            pos+a-b-c, pos+a-b+c, pos+a+b-c, pos+a+b+c],
            dtype=np.float32)

        self._faces = np.array([
            [0,1,3],[3,2,0], [6,7,5],[5,4,6],
            [4,5,1],[1,0,4], [2,3,7],[7,6,2],
            [0,2,6],[6,4,0], [5,7,3],[3,1,5]],
            dtype=np.uint).flatten()

        self._vertices  = self._edges[self._faces]
        self._faces     = np.array([i for i in range(self._vertices.shape[0])], dtype=np.uint)
        self._normals   = faceNormals(self._vertices, self._faces, primitive_size = 3)
        self._colors    = np.zeros((self._vertices.shape[0], 4))
        self._colors[:] = np.array([val/255 for val in self._parameters['brush_color'].getRgb()])

    def _updateTilesVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createVBO("tiles", self._vertices, self._normals, self._colors)

    def _processBorders(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        pos = self._edges[np.array([
            [0,1],[1,3],[3,2],[2,0],
            [4,5],[5,7],[7,6],[6,4],
            [0,4],[1,5],[2,6],[3,7]],
            dtype=np.uint).flatten()]

        tubes   = createTubes(
            pos, width = self._parameters['pen_thickness'], 
            precision = self._tube_precision, close = False)
        sphere  = createSphere(
            radius = self._parameters['pen_thickness'],
            precision = self._tube_precision)
        spheres = [[sphere[0]+vert, sphere[1]] for vert in self._vertices]

        self._tube_vertices, self._tube_faces = assembleFaces([tubes]+spheres)
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
            self._vaos['tiles'].render()

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
