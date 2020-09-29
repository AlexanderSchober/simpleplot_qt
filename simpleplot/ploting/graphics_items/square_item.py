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
import numpy as np

# Personal imports
from .rectangle_item import RectangleItem

class SquareItem(RectangleItem):
    '''
    This is a derivative of the GrahicsItem class
    that will handle the drawing of a Sqyuare either
    on a 2D or 3D OpenGl canvas
    '''
    def __init__(self,*args, **kwargs):
        '''
        Initialisation of the class and super class

        Parameters:
        -------------------
        *args : -
            These are the arguments of the class
        **kwargs : -
            These are the keyword arguments of the class
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, **kwargs)->None:
        '''
        This initializes the ParameterClass specifictions
        in the inherited item
        
        Parameters:
        -------------------
        **kwargs : -
            These are the keyword arguments if needed
        '''
        self.addParameter(
            'Dimension', 2.,
            names  = ['x','y'],
            tags   = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Subdivisions', [2,2],
            names  = ['x','y'],
            tags   = ['2D', '3D'],
            method = self.redraw)
        self.addParameter(
            'Subdivision dimension', [True, 2.],
            names  = ['Fill', 'dimension'],
            tags   = ['2D', '3D'],
            method = self.setVisual)

    def getPositionSubItem(self, i:int, j:int)->list:
        '''
        Get the positions of the subitems depending ion their
        indices
        '''
        pos = [
            -self['Dimension']/2.+(i+0.5)*self['Dimension']
            /self['Subdivisions'][0],
            -self['Dimension']/2.+(j+0.5)*self['Dimension']
            /self['Subdivisions'][1]]

        norm = np.sqrt(pos[0]**2+pos[1]**2)
        if norm == 0.:
            return  [0,0,0]
        else:
            angle = np.arccos(pos[0]/norm)/np.pi*180.
            if np.arcsin(pos[1]/norm) < 0:
                angle = -angle 

            return [
                norm*np.cos((angle)*np.pi/180.),
                norm*np.sin((angle)*np.pi/180.),
                0]

    def getDimensionSubItem(self)->list:
        '''
        Get the dimension of the subitems depending ion their
        indices
        '''        
        if self['Subdivision dimension'][0]:
            return [
                self['Dimension']/self['Subdivisions'][0],
                self['Dimension']/self['Subdivisions'][1]]
        else:
            return [
                self['Subdivision dimension'][1],
                self['Subdivision dimension'][1]  ]