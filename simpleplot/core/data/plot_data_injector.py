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

class PlotDataInjector:
    '''
    This class is responsible for genrating the adequate numpy 
    arrays to combine a multi dimensional dataset into a 
    the axes and the data structure.
    '''
    def __init__(self):

        self._data_source       = None
        self._axes_instructions = []
        self._plot_targets      = []

        self._behavior_list     = None
        self._target_dim        = None
        
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

    def setBehavior(self, behavior_list:list, target_dim:list):
        '''
        This is the behavior setter. He will save the 
        current list and then memorize how to gather
        the data from the datastructure and send it
        to the plot item
        '''
        self._behavior_list = behavior_list
        self._target_dim = target_dim
        self.dataChanged()
    
    def dataChanged(self):
        '''
        The changes in the data have to be 
        reprocessed. This method has to be linked 
        to the dataset item on change.  
        '''
        if self._data_source == None: return 
        if self._data_source.axes == None: return 
        if self._behavior_list == None: return 
        if self._target_dim == None: return 

        shape = [[] for i in self._target_dim]
        axis_index = [None for i in self._target_dim]

        retrieval_index = []
        index = 0
        for i,behavior in enumerate(self._behavior_list):
            if behavior[1] == "Fixed":
                retrieval_index.append(behavior[2])
            else:
                if i < self._data_source.axes.dim:
                    shape[self._target_dim.index(behavior[1])] = self._data_source.axes.axes[i]
                else:
                    data_dummy = self._data_source.DataObjects[0]
                    if len(data_dummy.data.shape) == 1 and not data_dummy.axes is None:
                        shape[self._target_dim.index(behavior[1])] = data_dummy.axes
                    elif len(data_dummy.data.shape) == 1 and data_dummy.axes is None:
                        shape[self._target_dim.index(behavior[1])] = [
                            j for j in range(
                                data_dummy.data.shape[
                                    j - len(self._behavior_list) + 1])]
                    elif len(data_dummy.data.shape) == 2 and not data_dummy.axes is None:
                        shape[self._target_dim.index(behavior[1])] = data_dummy.axes[i - len(self._behavior_list) + 1]
                    elif len(data_dummy.data.shape) == 2 and data_dummy.axes is None:
                        shape[self._target_dim.index(behavior[1])] = [
                            j for j in range(
                                data_dummy.data.shape[
                                    j - len(self._behavior_list) + 1])]

                axis_index[self._target_dim.index(behavior[1])] = index
                retrieval_index.append(slice(len(shape[self._target_dim.index(behavior[1])])))

                index +=1

        data_slice = self._data_source.returnAsNumpy().__getitem__(
            tuple(retrieval_index))

        right = ("->" + "ijklmnopqrst")[:-(12-len(self._target_dim))]
        left = "".join([
            ['i','j','k','l','m','n','o','p','q','r','s','t'][e] 
            for e in axis_index])
        data = np.einsum(left+right, data_slice)

        keywords = ['x','y','z','data']
        data_dict = {}
        for key in keywords:
            if key in self._target_dim:
                data_dict[key] = shape[self._target_dim.index(key)]
            else:
                data_dict[key] = data
                break

        for plot_target in self._plot_targets:
            plot_target.setData(**data_dict)
