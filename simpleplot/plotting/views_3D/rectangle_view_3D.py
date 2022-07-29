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

class RectangleView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

        self._parameters['dimensions']      = [1.,1.]
        self._parameters['positions']       = [[0,0,0]]
        self._parameters['brush_color']     = QtGui.QColor("black")
        self._parameters['pen_color']       = QtGui.QColor("black")
        self._parameters['pen_thickness']   = 0.1

    def initializeGL(self):
        '''
        IUnitialize the OpenGl states
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

    def setData(self, **kwargs):
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

    def paint(self):
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
        dims = np.array(self._parameters['dimensions'])
        self._base = np.array([
            [-0.5*dims[0], -0.5*dims[1], 0],
            [-0.5*dims[0],  0.5*dims[1], 0],
            [ 0.5*dims[0],  0.5*dims[1], 0],
            [ 0.5*dims[0], -0.5*dims[1], 0]],
            dtype=np.float)
        self._face_base = np.array((0,1,2,2,3,0), dtype=np.uint32)
        self._line_base = np.array((0,1,1,2,2,3,3,0), dtype=np.uint32)
        self._tube_precision = 10

    def _processTiles(self):
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        mult = np.tile(self._base, (len(self._parameters['positions']),1))
        mult = np.reshape(mult, (self._base.shape[0]*len(self._parameters['positions']),3))
        pos = np.tile(np.array(self._parameters['positions']), (self._base.shape[0]))
        pos = np.reshape(pos, (self._base.shape[0]*len(self._parameters['positions']),3))
        
        self._vertices  = pos+mult
        self._normals   = np.zeros(
            (self._base.shape[0]*len(self._parameters['positions']),3))
        self._normals[:,2] = 1
        self._faces     = np.array(
            [self._face_base+4*i for i in range(len(self._parameters['positions']))])
        self._colors    = np.zeros((self._vertices.shape[0], 4))
        self._colors[:] = np.array([val/255 for val in self._parameters['brush_color'].getRgb()])

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
        base_vertices, base_faces = createTubes(
            self._base[self._line_base], 
            width = self._parameters['pen_thickness'],
            close = False, connect = [True, True])
        
        items = []
        for position in self._parameters['positions']:
            items.append([base_vertices+position, base_faces])

        self._tube_vertices, self._tube_faces = assembleFaces(items)
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

