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
from ..graphics_geometry.helper_functions import createSphere

class EllipsoidView3D(GraphicsView3D):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''
    def __init__(self, **opts):
        super().__init__(**opts)

        self._parameters['diameters']       = [1.,2., 3.]
        self._parameters['positions']       = [0,0,0]
        self._parameters['brush_color']     = QtGui.QColor("black")
        self._parameters['pen_color']       = QtGui.QColor("black")
        self._parameters['pen_thickness']   = 0.1

    def initializeGL(self)->None:
        '''
        IUnitialize the OpenGl states
        '''
        self._createProgram("tiles")
        self._createVBO("tiles", np.zeros((100,3)), np.zeros((100,3)), np.zeros((100,4)))
        self._createIBO("tiles", np.zeros((300)))
        self._createVAO("tiles", {"tiles": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

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

    def _processTiles(self)->None:
        '''
        This will paint the tiles of the shape onto the canvas
        '''
        self._vertices, self._faces, self._normals = createSphere(
            precision = self._ellipse_precision)
        self._vertices      *= np.array(self._parameters['diameters'])
        self._vertices      += np.array(self._parameters['positions'])
        self._colors        = np.zeros((self._vertices.shape[0], 4))
        self._colors[:]     = np.array([val/255 for val in self._parameters['brush_color'].getRgb()])
        
        self._createIBO("tiles", self._faces)
        self._createVBO("tiles", self._vertices, self._normals, self._colors)
        self._createVAO("tiles", {"tiles": ["3f 3f 4f", "in_vert", "in_norm", "in_color"]})

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
