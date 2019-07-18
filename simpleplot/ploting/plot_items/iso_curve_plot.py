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
from copy import deepcopy
import numpy as np
from scipy.spatial.distance import pdist

from ...pyqtgraph                   import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph         import opengl as gl
from ...pyqtgraph.pyqtgraph.graphicsItems.GradientEditorItem import GradientEditorItem

from ..plot_geometries.shaders      import ShaderConstructor
from ...model.parameter_class       import ParameterHandler

class IsoCurvePlot(ParameterHandler):  
    '''
    This class will be the scatter plots. 
    '''
    def __init__(self, **kwargs):
        '''
        This class serves as envelope for the 
        PlotDataItem. Note that the axis of y will be
        changed to z in case of a 3D representation while the 
        y axis will be set to 0. This seems more
        natural.

        Parameters
        -----------
        x : 1D numpy array
            the x data
        y : 1D numpy array
            the y data
        z : 1D numpy array
            the z data
        error: dict of float arrays
            The error of each point
        '''
        ParameterHandler.__init__(self, 'Iso curves')

        self.addChild(ShaderConstructor())
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        self.addParameter(
            'Visible', False, 
            tags    = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Line thickness', 2, 
            tags    = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Line offset', 0.2, 
            tags    = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Levels', 10, 
            tags    = ['2D', '3D'],
            method = self.refresh)
        self.addParameter(
            'Use shader', False, 
            tags    = ['2D', '3D'],
            method = self.setColor)
        self.addParameter(
            'Color', QtGui.QColor('blue'),
            tags    = ['2D', '3D'],
            method = self.setColor)

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        if hasattr(self, 'draw_items'):
            isocurves = []
            for draw_item in self.draw_items:
                if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                    isocurves.append(draw_item)

            if self['Visible']:
                if len(isocurves) == 0:
                    if self._mode == '2D':
                        self.draw()
                        self.childFromName('Shader').runShader()
                        isocurves = []
                        for draw_item in self.draw_items:
                            if isinstance(draw_item, pg.IsocurveItem):
                                isocurves.append(draw_item)

                if self._mode == '2D':
                    for i,level in enumerate(self._processLevels()):
                        isocurves[i].setData(self.parent()['Data'].getData()[2], level = level)
                        self.childFromName('Shader').runShader()
                        
                elif self._mode == '3D':
                    for i in range(len(self.draw_items))[::-1]:
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                    self.draw_items = []
                    self.drawGL()
                    self.childFromName('Shader').runShader()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.IsocurveItem) or isinstance(self.draw_items[i], list):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                self.draw_items = []

        else:
            if self._mode == '2D':
                self.draw()
            elif self._mode == '3D':
                self.drawGL()

    def _getColors(self):
        '''
        Use outside of color loop
        '''
        if self['Use shader']:
            color_map = pg.ColorMap(
                self.childFromName('Shader')._positions,
                np.array(self.childFromName('Shader')._colors, dtype=np.uint)*255)
            lookUpTable = color_map.getLookupTable(nPts = self['Levels'], alpha = False)

            output = []
            for i in range(self['Levels']):
                output.append(QtGui.QColor(*lookUpTable[i].tolist()))
        else:
            output = []
            for i in range(self['Levels']):
                output.append(self['Color'])           

        return output

    def setColor(self):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        isocurves = []
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                isocurves.append(draw_item)

        colors = self._getColors()

        if not len(isocurves) == 0:
            for i in range(self['Levels']):
                if self._mode == '2D':
                    pen = pg.mkPen({
                        'color': colors[i], 
                        'width': self['Line thickness']})
                    isocurves[i].setPen(pen)

                elif self._mode == '3D':
                    for curve in isocurves[i]:
                        curve.setData(color = colors[i].getRgbF())

    def _processLevels(self):
        '''
        Redundant calculation of the levelsS
        '''
        bounds  = self.parent()['Data'].getBounds()

        return [((bounds[2][1] - bounds[2][0])/self['Levels'] * i + bounds[2][0]) for i in range(self['Levels'])]

    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            self.setCurrentTags(['2D'])
            
        self.draw_items = []
        if self['Visible']:
            data    = self.parent()['Data'].getData()
            for level in self._processLevels():
                self.draw_items.append(pg.IsocurveItem(data = data[2], level = level))
                self.default_target.draw_surface.addItem(self.draw_items[-1])
            
            self.setColor()

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view
            self.setCurrentTags(['3D'])

        self.draw_items = []
        if self['Visible']:
            data    = self.parent()['Data'].getData()
            bounds  = self.parent()['Data'].getBounds()
            x_fac   = (bounds[0][1] - bounds[0][0])
            y_fac   = (bounds[1][1] - bounds[1][0])

            for level in self._processLevels():
                iso_curves = self.parent()['Data'].getIsocurve(level)

                gl_iso_curve = []
                for curve in iso_curves:
                    gl_iso_curve.append(
                        gl.GLLinePlotItem(
                            pos=np.vstack([
                                [(item[0]-0.5) / (data[2].shape[0]-1) * x_fac + bounds[0][0] for item in curve],
                                [(item[1]-0.5) / (data[2].shape[1]-1) * y_fac + bounds[1][0] for item in curve],
                                [level+self['Line offset'] for item in curve]]).transpose(),
                            color = self['Color'],
                            width = self['Line thickness'],
                            mode = 'line_strip'))
                    gl_iso_curve[-1].setGLOptions('opaque')
                    gl_iso_curve[-1].setTransform(self.parent().transformer.getTransform())
                    self.default_target.view.addItem(gl_iso_curve[-1])

                self.draw_items.append(list(gl_iso_curve))

    def removeItems(self):
        '''
        Remove the objects.
        '''
        if hasattr(self, 'draw_items'):
            for curve in self.draw_items:
                self.default_target.draw_surface.removeItem(curve)

