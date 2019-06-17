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
import numpy as np

from ...pyqtgraph import pyqtgraph as pg

class SimpleErrorBarItem(pg.ErrorBarItem): 
    '''
    This class will be the scatter plots. 
    '''

    def __init__(self,*args,**kwargs):
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
        pg.ErrorBarItem.__init__(self, *args,**kwargs)

    def setLogMode(self,xMode, yMode):
        '''
        comply withe the log mode feature
        '''
        self.opts['logMode'] = [xMode, yMode]
        self.setData()

    def setFftMode(self, mode):
        '''
        comply with the fft tranform
        '''
        pass

    def drawPath(self):

        if self.opts['x'] is None or self.opts['y'] is None:
            return

        p = QtGui.QPainterPath()
        
        x = self.opts['x'] if not self.opts['logMode'][0] else np.log10(self.opts['x'])
        y = self.opts['y'] if not self.opts['logMode'][1] else np.log10(self.opts['y'])

        beam = self.opts['beam']
        
        height, top, bottom = self.opts['height'], self.opts['top'], self.opts['bottom']
        print('heigh, top, bot', height, top, bottom )

        if height is not None or top is not None or bottom is not None:
            ## draw vertical error bars
            if height is not None or height == 0:
                y1 = y-height/2. if not self.opts['logMode'][1] else np.log10(self.opts['y']-height/2.)
                y2 = y+height/2. if not self.opts['logMode'][1] else np.log10(self.opts['y']+height/2.)
            else:
                if bottom is None:
                    y1 = y
                else:
                    y1 = y - bottom if not self.opts['logMode'][1] else np.log10(self.opts['y']-bottom)
                if top is None:
                    y2 = y
                else:
                    y2 = y + top if not self.opts['logMode'][1] else np.log10(self.opts['y']+top)
            
            for i in range(len(x)):
                p.moveTo(x[i], y1[i])
                p.lineTo(x[i], y2[i])
                
            if beam is not None and beam > 0:
                x1 = x - beam/2. if not self.opts['logMode'][0] else np.log10(self.opts['x']-beam/2.)
                x2 = x + beam/2. if not self.opts['logMode'][0] else np.log10(self.opts['x']+beam/2.)
                if height is not None or top is not None:
                    for i in range(len(x)):
                        p.moveTo(x1[i], y2[i])
                        p.lineTo(x2[i], y2[i])
                if height is not None or bottom is not None:
                    for i in range(len(x)):
                        p.moveTo(x1[i], y1[i])
                        p.lineTo(x2[i], y1[i])
        
        width, right, left = self.opts['width'], self.opts['right'], self.opts['left']
        if width is not None or right is not None or left is not None:
            ## draw vertical error bars
            if width is not None:
                x1 = x - width/2. if not self.opts['logMode'][0] else np.log10(self.opts['x']-width/2.)
                x2 = x + width/2. if not self.opts['logMode'][0] else np.log10(self.opts['x']+width/2.)
            else:
                if left is None:
                    x1 = x
                else:
                    x1 = x - left if not self.opts['logMode'][0] else np.log10(self.opts['x']-left)
                if right is None:
                    x2 = x
                else:
                    x2 = x + right if not self.opts['logMode'][0] else np.log10(self.opts['x']+right)
            
            for i in range(len(x)):
                p.moveTo(x1[i], y[i])
                p.lineTo(x2[i], y[i])
                
            if beam is not None and beam > 0:
                y1 = y - beam/2. if not self.opts['logMode'][1] else np.log10(self.opts['y']-beam/2.)
                y2 = y + beam/2. if not self.opts['logMode'][1] else np.log10(self.opts['y']+beam/2.)
                if width is not None or right is not None:
                    for i in range(len(x)):
                        p.moveTo(x2[i], y1[i])
                        p.lineTo(x2[i], y2[i])
                if width is not None or left is not None:
                    for i in range(len(x)):
                        p.moveTo(x1[i], y1[i])
                        p.lineTo(x1[i], y2[i])
                    
        self.path = p
        self.prepareGeometryChange()