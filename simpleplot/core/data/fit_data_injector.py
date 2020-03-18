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

class FitDataInjector:
    '''
    This class is responsible for genrating the adequate numpy 
    arrays to combine a multi dimensional dataset into a 
    the axes and the data structure.
    '''
    def __init__(self):

        self._data_source       = None
        self._axes_instructions = []
        self._fit_targets       = []

        self._behavior_list     = None
        self._target_dim        = ['x']
        
    def setDataSource(self, source):
        '''
        replace the source of the data
        '''
        self._data_source = source

    def addFitTarget(self, target):
        '''
        Add a plot target to the list
        '''
        self._fit_targets.append(target)

    def removeFitTarget(self, target):
        '''
        Add a plot target to the list
        '''
        self._fit_targets.remove(target)

    def setBehavior(self, behavior_list:list, target_dim:list):
        '''
        This is the behavior setter. He will save the 
        current list and then memorize how to gather
        the data from the datastructure and send it
        to the fit item
        '''
        self._behavior_list = behavior_list
        self._target_dim = target_dim
        self._prepare_data()

    def getVariableAxes(self):
        '''
        This method is supposed to notify the fit manager the axes 
        so he can initialize the navigoator. 
        '''
        if self._data_source == None: return None
        if self._data_source.axes == None: return None
        
        shape = [None for i in self._target_dim]
        index = 0
        for i,behavior in enumerate(self._behavior_list):
            if not behavior[1] == "Fixed" and 'Variable' in behavior[1]:
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

                index +=1
                
        return [i for i in shape if not i is None] 

    def getFitAxes(self):
        '''
        This method is supposed to notify the fit manager the axes 
        so he can initialize the navigator. 
        '''
        if self._data_source == None: return None
        if self._data_source.axes == None: return None
        
        shape = [None for i in self._target_dim]
        index = 0
        for i,behavior in enumerate(self._behavior_list):
            if not behavior[1] == "Fixed" and not 'Variable' in behavior[1]:
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

                index +=1
                
        return [i for i in shape if not i is None] 

    def getData(self, index):
        '''
        This method will give the data at the given index. 
        '''
        if self._data_source == None: return None
        if self._data_source.axes == None: return None
        
        return self._data.__getitem__(tuple([slice(0,len(e)) for e in self.getFitAxes()] + index )) 

    def _prepare_data(self):
        '''
        The changes in the data have to be 
        reprocessed. This method has to be linked 
        to the dataset item on change.  
        '''
        if self._data_source is None: return 
        if self._data_source.axes is None: return 
        if self._behavior_list is None: return 
        if self._target_dim is None: return 

        shape = [[] for i in self._target_dim]
        self._axis_index = [None for i in self._target_dim]

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

                self._axis_index[self._target_dim.index(behavior[1])] = index
                retrieval_index.append(slice(len(shape[self._target_dim.index(behavior[1])])))

                index +=1
                
        data_slice = self._data_source.returnAsNumpy().__getitem__(tuple(retrieval_index))
        
        right = ("ijklmnopqrst")[:-(12-len(self._target_dim))]
        left = "".join([
            ['i','j','k','l','m','n','o','p','q','r','s','t'][e] 
            for e in self._axis_index])
            
        self._data = np.einsum(right+"->"+left, data_slice)
