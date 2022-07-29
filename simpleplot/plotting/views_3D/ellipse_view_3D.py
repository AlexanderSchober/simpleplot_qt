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

class EllipseView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)
        self._parameters['diameters']       = [1.,1.]
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
        self._createVBO("tiles", np.zeros((101,3)), np.zeros((101,3)), np.zeros((101,3)))
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
        x = np.linspace(0, 2*np.pi, 100)
        self._base = np.zeros((101,3),dtype=np.float)
        self._base[1:,0] = np.cos(x)
        self._base[1:,1] = np.sin(x)
        self._line_base = np.array([[0,i,i+1] for i in range(1,self._base.shape[0]-1)]).flatten()
        self._tube_line_base = np.array([[i,i+1] for i in range(1,self._base.shape[0]-1)]+[[self._base.shape[0]-1, 1]]).flatten()
        self._tube_precision = 10

    def _processTiles(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        self._vertices = (self._base[:] * (self._parameters['diameters']+[1])+self._parameters['positions'])[self._line_base]
        self._normals   = np.array([[0,0,1] for i in range(self._vertices.shape[0])])
        self._colors    = np.zeros((self._vertices.shape[0], 4))
        self._colors[:] = np.array([val/255 for val in self._parameters['brush_color'].getRgb()])

    def _updateTilesVBO(self)->None:
        '''
        Here we will order the software to inject the main data into
        the present buffers
        '''
        self._createVBO("tiles", self._vertices, self._normals, self._colors)
        self._createVAO("tiles", {"tiles": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

    def _processBorders(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        self._tube_vertices, self._tube_faces = createTubes(
            (self._base[:] * (self._parameters['diameters']+[1])+self._parameters['positions'])[self._tube_line_base],
            width = self._parameters['pen_thickness'],
            close = False, connect = [True, True])
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
            self._vaos['border'].render( )
