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

from PyQt5 import QtGui
import numpy as np
from ...pyqtgraph.pyqtgraph     import opengl as gl
from ...pyqtgraph.pyqtgraph.opengl   import GLMeshItem
from ...pyqtgraph.pyqtgraph.opengl.MeshData     import MeshData
from ...model.parameter_class   import ParameterHandler 

from ..plot_geometries.shaders      import ShaderConstructor

from .ray_intersec_lib import rayTriangleIntersection
from .ray_intersec_lib import closestPointOnLine
from .ray_intersec_lib import checkBoundingBox
from .ray_intersec_lib import retrievePositionSpheres

class DistributionRayHandler(ParameterHandler): 
    ''' 
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self,'Ray handler')
        self.pointer_elements = []
        self.addChild(ShaderConstructor())
        self._initialize()
        self.reset()

    def _initialize(self):
        '''
        '''
        self.addParameter(
            'Active', True, 
            method = self._setActive)
        self.addParameter(
            'Color', QtGui.QColor('red'), 
            method = self.dispatchCoordinate)
        self.addParameter(
            'Offset', 0.001, 
            method = self.dispatchCoordinate)
        self.addParameter(
            'GL options', 'opaque', 
            choices = ['opaque','translucent', 'additive'],
            method = self.dispatchCoordinate)
        self.addParameter(
            'Antialiasing', True,
            method = self.dispatchCoordinate)

    def drawGL(self,target):
        '''
        Dummy draw that sets the target of the 
        pointer element
        '''
        self.default_target = target

    def reset(self):
        '''
        reprocess pointer
        '''
        self.point  = None
        self._idx   = None
        self.dispatchCoordinate()

    def processRay(self, ray, dispatch = True):
        '''
        Process an input ray by the 
        canvas widget and perform necessary
        operations
        '''
        self._destroyPointer()

        if hasattr(self.parent().childFromName('Distribution'), 'draw_items'):
            temp        = self.parent().transformer.getTransform().inverted()[0]
            transform   = np.reshape(np.array(temp.data()),(4,4)).transpose()
            new_ray     = [np.dot(transform,np.hstack((e,1)))[:3] for e in ray]
            intersec    = checkBoundingBox(new_ray, self.parent().childFromName('Data'))
            
            if not intersec is None:
                self.point, self._idx = retrievePositionSpheres(
                    new_ray, 
                    self.parent().childFromName('Data'))
            else:
                self.point = None
                self._idx = None

    def _setActive(self):
        '''
        '''
        if not self['Active']:
            self._destroyPointer()

    def _destroyPointer(self):
        '''
        '''
        for element in self.pointer_elements:
            if element in self.default_target.view.items:
                self.default_target.view.removeItem(element)
        self.pointer_elements = []

    def dispatchCoordinate(self):
        '''
        '''
        if self['Active'] and not self.point is None:
            self._drawContainer()
        else:
            self._destroyPointer()

    def _drawContainer(self):
        '''
        '''
        self._destroyPointer()

        data = self.parent().childFromName('Data').getData()

        mesh = MeshData.sphere(100,100, radius=data[0][self._idx,3]+self['Offset'])
        kwargs = {}
        kwargs['vertexes']  = mesh._vertexes+self.point
        kwargs['faces']     = mesh._faces
        kwargs['color']     = self['Color']
        kwargs['antialias'] = self['Antialiassing']

        self.pointer_elements.append(GLMeshItem(**kwargs))
        self.pointer_elements[-1].setGLOptions(self['GL options'])
        self.default_target.view.addItem(self.pointer_elements[-1])
        self.childFromName('Shader').runShader()

    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        colors = self.parent()._plot_data.getData()[1]
        for i,element in enumerate(self.pointer_elements):
            element.setShader(self.childFromName('Shader').getShader('light'))
