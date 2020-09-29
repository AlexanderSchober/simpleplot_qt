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
from ..models.parameter_class import ParameterHandler 
from pyrr import Matrix44, Quaternion, Vector3, vector
from pyrr.vector3 import cross, length, normalise
import numpy as np

class LightSource(ParameterHandler):
    '''
    This class will hndle the view and projection of the 
    opengl view and then process its matrices
    '''
    def __init__(self, canvas):
        super(LightSource, self).__init__('Light source', canvas)
        self._initNode()
        self._buildLight()

    def _initNode(self)->None:
        '''
        Initialize the paramters node
        so that the setup is complete
        '''
        self.addParameter(
            'Source active', True,
            method = self._buildLight)

        self.addParameter(
            'Light position', [0.0, 0.0, 0.0],
            names = ['x', 'y', 'z'],
            method = self._buildLight)

        self.addParameter(
            'Light color', QtGui.QColor('white'),
            method = self._buildLight)

        self.addParameter(
            'Position relative', True,
            method = self._buildLight)

    def _buildLight(self):
        '''
        Build the matrices that will be the 
        injected as uniforms in all vertex
        shaders lateron
        '''
        self.light_bool = np.array([self['Source active'], self['Position relative']])
        self.light_pos = np.array(self['Light position'])
        self.light_color = np.array([val/255 for val in self['Light color'].getRgb()[:3]])
        
        self.parent().view.contextClass().setLight()
