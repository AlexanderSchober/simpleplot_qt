    
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
import numpy as np
from scipy.spatial import distance

class PointerPosition:
        
    def __init__(self, parent):
        '''
        This is the main pointer position evaluation 
        system. In here we will define simple methods
        that will be inherited by all children. 
        '''
        self.parent = parent
        self.point_list = np.zeros(0)

    def fetch_position_data(self):
        '''
        This method will go through all plot items in 
        the canvas and map their datapoints. This will
        then allow the evaluator to access on screen 
        information. 
        '''
        self.mapping = []
        self.data    = []

        for plot_handler in self.parent.canvas._plot_root._children:
            for plot_element in plot_handler._children:
                if hasattr(plot_element, '_plot_data'):
                    self.mapping.append([
                        plot_element, 
                        plot_element._plot_data.getData(), 
                        False])

    def evaluate(self):
        '''
        '''
        pass


class Type_0_Position(PointerPosition):

    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        old find_nearestY. This method aims at 
        searching successively for the nearest value in 
        all plots by first scanning the nearest X. 
        Then e find the second nearest to zero after 
        X-Nearest. This will give us back two point 
        ids which whom we can calculate the nearest Y
        '''
        cursor_x = 10**self.parent.cursor_x if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else self.parent.cursor_x
        cursor_y = 10**self.parent.cursor_y if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else self.parent.cursor_y
        
        points  = []
        node    = np.array([cursor_x, cursor_y])
        for element in self.mapping:
            nodes       = np.zeros((len(element[1][0]),2)) 
            nodes[:,0] = element[1][0]
            nodes[:,1] = element[1][1]
            points.append(nodes[distance.cdist([node], nodes).argmin()])

        nodes   = points
        deltas  = nodes - node
        select  = closest_index = distance.cdist([node], nodes).argmin()
        point   = nodes[select]

        self.parent.cursor_x = np.log10(point[0]) if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else point[0]
        self.parent.cursor_y = np.log10(point[1]) if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else point[1]

class Type_3_Position(PointerPosition):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        This tries to find the closest X and Y of the 
        a the first contour plots...
        Multiple contours are not supported yet and 
        frankly don't make to much sense therefore we
        will simply grab contour [0].
        '''
        cursor_x = 10**self.parent.cursor_x if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else self.parent.cursor_x
        cursor_y = 10**self.parent.cursor_y if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else self.parent.cursor_y

        idx_0 = (np.abs(np.asarray(self.mapping[0][1][0]) - cursor_x)).argmin()
        idx_1 = (np.abs(np.asarray(self.mapping[0][1][1]) - cursor_y)).argmin()
                
        self.parent.cursor_x = self.mapping[0][1][0][idx_0]
        self.parent.cursor_y = self.mapping[0][1][1][idx_1]
        self.parent.cursor_z = self.mapping[0][1][2][idx_0, idx_1]
