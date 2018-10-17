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

import pyqtgraph as pg
import numpy as np

from .scatter_plot  import Scatter_Plot
from .contour_plot  import Contour_Plot
from .bin_plot      import Bin_Plot
from.surface_plot   import Surface

def get_plot_handler(select):
    '''
    ##############################################
    Will return the right fit manager depending 
    on the initial input
    ———————
    Input: target (Data_Structure)
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    if select == 'Scatter':

        return Plot_Handler(select, Scatter_Plot)

    elif select == 'Contour':
    
        return Plot_Handler(select, Contour_Plot)

    elif select == 'Bin':

        return Plot_Handler(select, Bin_Plot)

    elif select == 'Surface':
    
        return Plot_Handler(select, Surface)

    else:

        print('Could not find the fit class you are looking for. Error...')
        
        return None


class Plot_Handler():

    '''
    ############################################## 
    This class will be the manager of all the 
    scatter plots. 
    ———————
    Input: 
    - parent is the parent canvas class
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, name, target_class):
        
        self.plot_elements  = []
        self.identifier     = 0
        self.target_class   = target_class
        self.name           = name


    def __getitem__(self,name):
        '''
        ##############################################
        This will effectively add an element to the 
        plot_elements array. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for plot_element in self.plot_elements:

            if plot_element.name == name:

                return plot_element


    def add_item(self,*args, **kwargs):
        '''
        ##############################################
        This will effectively add an element to the 
        plot_elements array. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.plot_elements.append(self.target_class(*args,**kwargs))

    def remove_item(self, name = '', idx = None, target = None):
        '''
        ##############################################
        here we will ask the element in question to 
        remove one of its items and proceed to a clean
        removale. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        if idx == None and name == '':
            print("You can't remove nothing ...")

        elif not name == '':
            
            names = [element.get_para('Name') for element in self.plot_elements]

            self.plot_elements[names.index(name)].remove_items(target)

            del self.plot_elements[names.index(name)]

        elif not idx == None:

            self.plot_elements[idx].remove_items(target)

            del self.plot_elements[idx]

    def draw(self, target):
        '''
        ##############################################
        
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #set the plot
        for plot_element in self.plot_elements:

            if target.artist.artist_type == "2D":

                plot_element.draw(target)

            elif target.artist.artist_type == "3D":
    
                plot_element.drawGL(target)

        if target.artist.artist_type == "2D":

            #set th new zoom
            target.artist.zoomer.zoom()
