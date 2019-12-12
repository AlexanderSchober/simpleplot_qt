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


#import general components
import numpy as np

class DataInjector:
    '''
    This class is responsible for genrating the adequate numpy 
    arrays to combine a multi dimensional dataset into a 
    the axes and the data structure.
    '''
    def __init__(self):

        self._data_source = None
        self._axes_instructions = []
        self._plot_targets = []
        
    def setDataSource(self, source):
        '''
        replace the source of the data
        '''
        self._data_source = source

    def addPlotTarget(self, target):
        '''
        Add a plot target to the list
        '''
        self._plot_targets.append(target)

    def removePlotTarget(self, target):
        '''
        Add a plot target to the list
        '''
        self._plot_targets.remove(target)
