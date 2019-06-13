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
from ..plot_geometries.transformer  import Transformer


class IsoCurvePlot(ParameterHandler, Transformer):  
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
        ParameterHandler.__init__(self, 'Isosurface')
        Transformer.__init__(self)
        self.gradient_item = GradientEditorItem()
        self.initialize(**kwargs)
        self._mode = '2D'

    def initialize(self, **kwargs):
        '''
        This class will be the scatter plots. 
        The arguments are given as kwargs 
        '''
        position = [0,0.25,0.5,0.75,1.]
        colors = [
            [0.,1.,1., 1.],
            [0.,0.,1., 1.],
            [0.,1.,0., 1.],
            [1.,0.,0., 1.],
            [0.,1.,0., 1.]]
        state = {'ticks':[[position[i],np.array(colors)[i]*255] for i in range(len(colors))],'mode' : 'rgb'}
        self.gradient_item.restoreState(state)

        self.addParameter(
            'Visible', True, 
            method = self.setColor)

        self.addParameter(
            'Line thickness', 2, 
            method = self.setColor)
        self.addParameter(
            'Line offset', 0.2, 
            method = self.setColor)

        self.addParameter(
            'Use gradient', False, 
            method = self.setColor)
        self.addParameter(
            'Gradient', self.gradient_item, 
            method = self.setColor)
        self.addParameter(
            'Color', QtGui.QColor('blue'),
            method = self.setColor)

        self._setTransformerParameters()

        #TODO:remove
        self.parameters = {}

        self.parameters['Isocurve']         = [[True]]
        self.parameters['Levels']           = [[10]]
        self.parameters['Line color grad']  = [[False]]
        self.parameters['Line color']       = [[QtGui.QColor('blue')]]
        self.parameters['Line thickness']   = [[2]]
        self.parameters['Line offset']      = [[0.2]]

    def getParameter(self, name):
        '''
        Returns the value of the parameter requested
        '''
        return self.parameters[name][0]

    def refresh(self):
        '''
        Set the data of the image and then let the 
        program decide which procedure to target Note
        that this routine aims at updating the data only
        '''
        self.unTransform()

        if hasattr(self, 'draw_items'):
            
            #find the isocurves
            isocurves = []
            for draw_item in self.draw_items:
                if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                    isocurves.append(draw_item)

            #if we have a isocurves
            if self['Visible']:

                #if not present draw it
                if len(isocurves) == 0:
                    if self._mode == '2D':
                        self.drawIsocurves()
                        self.setColor()
                        isocurves = []
                        for draw_item in self.draw_items:
                            if isinstance(draw_item, pg.IsocurveItem):
                                isocurves.append(draw_item)
                #update if 2D
                if self._mode == '2D':
                    for i in range(self.getParameter('Levels')[0]):
                        if isinstance(self.parent()['Data'].getData()[2], np.ndarray):
                            level = (
                                (np.amax(self.parent()['Data'].getData()[2]) - np.amin(self.parent()['Data'].getData()[2]))/self.getParameter('Levels')[0] * i 
                                + np.amin(self.parent()['Data'].getData()[2]))
                        else:
                            level = 0
                        isocurves[i].setData(self.parent()['Data'].getData()[2], level = level)

                #update if 3D
                elif self._mode == '3D':
                    for i in range(len(self.draw_items))[::-1]:
                        if isinstance(self.draw_items[i], list):
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                            del self.draw_items[i]
                    self.drawGLIsocurves()
                    self.setColor()

            else:
                for i in range(len(self.draw_items))[::-1]:
                    if isinstance(self.draw_items[i], pg.IsocurveItem) or isinstance(self.draw_items[i], list):
                        if self._mode == '2D':
                            self.default_target.draw_surface.removeItem(self.draw_items[i])
                        elif self._mode == '3D':
                            for item in self.draw_items[i]:
                                self.default_target.view.removeItem(item)
                        del self.draw_items[i]

        else:
            if self._mode == '2D':
                self.draw()
            elif self._mode == '3D':
                self.drawGL()

        self.reTransform()

    def _getColors(self):
        '''
        Use outside of color loop
        '''
        state       = self['Gradient'].saveState()
        positions   = [element[0] for element in state['ticks']]
        colors      = [list(np.array(element[1])/255) for element in state['ticks']]
        colors      = np.array([c for _,c in sorted(zip(positions, colors))])
        positions   = np.array(sorted(positions))

        if self['Use gradient']:
            color_map   = pg.ColorMap(positions,colors*255)
            lookUpTable = color_map.getLookupTable(nPts = self.getParameter('Levels')[0], alpha = False)

            output = []
            for i in range(self.getParameter('Levels')[0]):
                output.append(QtGui.QColor(*lookUpTable[i].tolist()))
        else:
            output = []
            for i in range(self.getParameter('Levels')[0]):
                output.append(self['Color'])           

        return output

    def setColor(self, color = None):
        '''
        The preference implementation requires the ability to set
        colors without redrawing the entire data. As such we will 
        here allow the setting of colors either through the 
        color map or through shaders.
        '''
        if not color == None:
            self.parameters['Line color'] = [[color]]
            
        isocurves = []
        for draw_item in self.draw_items:
            if isinstance(draw_item, pg.IsocurveItem) or isinstance(draw_item, list):
                isocurves.append(draw_item)

        colors = self._getColors()

        if not len(isocurves) == 0:
            for i in range(self.getParameter('Levels')[0]):
                if isinstance(self.parent()['Data'].getData()[2], np.ndarray):
                    level = (
                        (np.amax(self.parent()['Data'].getData()[2]) - np.amin(self.parent()['Data'].getData()[2]))/self.getParameter('Levels')[0] * i 
                        + np.amin(self.parent()['Data'].getData()[2]))
                else:
                    level = 0
            
                if self._mode == '2D':
                    pen = pg.mkPen({
                        'color': colors[i], 
                        'width': self.getParameter('Line thickness')[0]})

                    isocurves[i].setPen(pen)

                elif self._mode == '3D':
                    for curve in isocurves[i]:
                        print(colors[i].getRgbF())
                        curve.setData(color = colors[i].getRgbF())


    def draw(self, target_surface = None):
        '''
        Draw the objects.
        '''
        self._mode = '2D'
        if not target_surface == None:
            self.default_target = target_surface
            
        self.draw_items = []
        
        data    = self.parent()['Data'].getData()
        bounds  = self.parent()['Data'].getBounds()

        for i in range(self.getParameter('Levels')[0]):

            pen = pg.mkPen({
                'color': self.getParameter('Line color')[0], 
                'width': self.getParameter('Line thickness')[0]})
            level = ((bounds[2][1] - bounds[2][0])/self.getParameter('Levels')[0] * i + bounds[2][0])
            self.draw_items.append(pg.IsocurveItem(data = data[2], level = level, pen = pen))
            self.default_target.draw_surface.addItem(self.draw_items[-1])

    def drawGL(self, target_view = None):
        '''
        Draw the objects.
        '''
        self._mode = '3D'
        if not target_view == None:
            self.default_target = target_view

        self.draw_items = []
        
        data    = self.parent()['Data'].getData()
        bounds  = self.parent()['Data'].getBounds()
        x_fac   = (bounds[0][1] - bounds[0][0])
        y_fac   = (bounds[1][1] - bounds[1][0])

        for i in range(self.getParameter('Levels')[0]):
            level = ((bounds[2][1] - bounds[2][0])/self.getParameter('Levels')[0] * i + bounds[2][0])
            iso_curves = self.parent()['Data'].getIsocurve(level)

            gl_iso_curve = []
            for curve in iso_curves:
                gl_iso_curve.append(
                    gl.GLLinePlotItem(
                        pos=np.vstack([
                            [(item[0]-0.5) / (data[2].shape[0]) * x_fac + bounds[0][0] for item in curve],
                            [(item[1]-0.5) / (data[2].shape[1]) * y_fac + bounds[1][0] for item in curve],
                            [level+self.getParameter('Line offset')[0] for item in curve]]).transpose(),
                        color = self.getParameter('Line color')[0],
                        width = self.getParameter('Line thickness')[0],
                        mode = 'line_strip'))
                gl_iso_curve[-1].setGLOptions('translucent')
                self.default_target.view.addItem(gl_iso_curve[-1])

            self.draw_items.append(list(gl_iso_curve))

    def removeItems(self):
        '''
        '''
        for curve in self.draw_items:
            self.default_target.draw_surface.removeItem(curve)
