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

from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl

from .rectangle_item import RectangleItem

class SquareItem(RectangleItem):
    '''
    This item will be the graph item that is
    put an managed on its own
    '''

    def __init__(self,*args, **kwargs):
        '''
        Arrows can be initialized with any keyword arguments accepted by 
        the setStyle() method.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
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
            method = self.resetSubdivision)

    def setVisual(self):
        '''
        Set the visual of the given shape element
        '''
        parameters = {
            'angle' : self['Angle'], 
            'pen' : super().getPen(),
            'brush' : super().getBrush(),
            'Z' : self['Z'],
            'movable' : self['Movable'],
            'rot_center' : self['Position']}

        for i in range(self['Subdivisions'][0]):
            for j in range(self['Subdivisions'][1]):
                parameters['positions'] = [
                    (self['Position'][0]-self['Dimension']/2.)
                    +(i+0.5)*self['Dimension']/self['Subdivisions'][0],
                    (self['Position'][1]-self['Dimension']/2.)
                    +(j+0.5)*self['Dimension']/self['Subdivisions'][1]]
                parameters['dimensions'] = [
                        self['Dimension']/self['Subdivisions'][0],
                        self['Dimension']/self['Subdivisions'][1]]
                self.draw_items[i][j].setData(**parameters)

        parameters = {
            'angle' : self['Angle'], 
            'pen' : super().getPen(),
            'brush' : super().getBrush(),
            'Z' : self['Z'],
            'movable' : self['Movable'],
            'rot_center' : self['Position'],
            'positions' : [],
            'dimensions' : []}

        for i in range(self['Subdivisions'][0]):
            for j in range(self['Subdivisions'][1]):
                pos = [
                    -self['Dimension']/2.+(i+0.5)*self['Dimension']
                    /self['Subdivisions'][0],
                    -self['Dimension']/2.+(j+0.5)*self['Dimension']
                    /self['Subdivisions'][1]]

                norm = np.sqrt(pos[0]**2+pos[1]**2)
                if norm == 0.:
                    parameters['positions'] = [
                        self['Position'][0],
                        self['Position'][1]]
                    parameters['dimensions'] = [
                        self['Dimension']/self['Subdivisions'][0],
                        self['Dimension']/self['Subdivisions'][1]]
                else:
                    angle = np.arccos(pos[0]/norm)/np.pi*180.
                    if np.arcsin(pos[1]/norm) < 0:
                        angle = -angle 

                    parameters['positions'] = [
                        norm*np.cos((self['Angle']+angle)*np.pi/180.)+self['Position'][0],
                        norm*np.sin((self['Angle']+angle)*np.pi/180.)+self['Position'][1]]
                        
                    parameters['dimensions'] = [
                        self['Dimension']/self['Subdivisions'][0],
                        self['Dimension']/self['Subdivisions'][1]]

                self.draw_items[i][j].setData(**dict(parameters))