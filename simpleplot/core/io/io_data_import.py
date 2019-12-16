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


from ..io import io_file_methods as file_methods 
import itertools
import os
import datetime
import numpy as np

class IODataLoad:
    '''
    '''
    def __init__(self, target, path:str):
        '''
        define the local elements and proceed with the 
        saving procedure.
        '''
        self._target = target
        self._path = path

    def load(self, file_format:str):
        '''
        The save entry point
        '''
        if file_format == "txt":
            self._loadFromTxt()
        elif file_format == "hdf5":
            self._loadFromHdf5()

    def previewFromNumpy(self):
        '''
        This will in fact load the file through 
        the numpy channel.
        '''
        extension = self._path.split(".")[-1]

        if extension == 'npy' or extension == 'npz':
            data = np.load(self._path)
        elif extension == 'txt':
            data = np.loadtxt(self._path)

        return data.shape

    def loadFromNumpy(self, data_axes):
        '''
        This will in fact load the file through 
        the numpy channel.
        '''
        extension = self._path.split(".")[-1]

        if extension == 'npy' or extension == 'npz':
            data = np.load(self._path)
        elif extension == 'txt':
            data = np.loadtxt(self._path)

        loop_elements = [
            [ l for l in range(i)] 
            for i in data.shape]

        get_index = []
        for i, element in enumerate(data_axes):
            if not element:
                get_index.append(slice(len(loop_elements[i])))
            else:
                get_index.append(None)

        loop_elements = itertools.compress(loop_elements, data_axes)
        for e in itertools.product(*loop_elements):
            print(e)
            local_index = list(get_index)
            idx = 0
            for i, element in enumerate(data_axes):
                if element:
                    local_index[i] = e[idx]
                    idx += 1
            print(local_index)
            self._target.addDataObject(
                data.__getitem__(tuple(local_index)), e)
        
        self._target.validate()

    def _loadFromTxt(self):
        '''
        load from txt files
        '''
        with open(self._path, 'r') as f:
            lines = f.readlines()
            line_idx = self._getLines(lines)

            self._dimAnalyser(lines, line_idx[1], line_idx[2])
            self._subdimAnalyser(lines, line_idx[2], line_idx[3])
            self._subaxisReader(lines, line_idx[2], line_idx[3])

            self._dataReader(lines,line_idx[3])
            self._axisReader(lines,line_idx[1], line_idx[2])

    def _getLines(self, lines):
        '''
        This routine will determine the lines at
        which individual data is written down. 
        '''
        for i, line in enumerate(lines[:100]):
            if ' METADATA ' in line[:50]:
                line_meta = i
            elif ' DATA ' in line[:50]:
                line_data = i
            elif ' AXIS ' in line[:50]:
                line_axis = i
            elif ' SUBAXIS ' in line[:50]:
                line_subaxis = i

        return [line_meta, line_axis, line_subaxis, line_data]
 
    def _dimAnalyser(self,lines, start_line, end_line):
        '''
        This routine will read through the axis
        information and try to set it in the 
        datastructure. The datastructure needs to be 
        already validated for this effect to be 
        meaningfull.
        '''
        self._dims = []
        for idx, axis_str in enumerate(lines[start_line+1:end_line]):
            self._dims.append(
                len(axis_str.strip('\n').split('**')[3].split(',')))

    def _subdimAnalyser(self, lines, start_line, end_line):
        '''
        '''
        self._subdims = []
        for idx, axis_str in enumerate(lines[start_line+1:end_line]):
            self._subdims.append(
                len(axis_str.strip('\n').split('**')[2].split(',')))

    def _axisReader(self,lines, start_line, end_line):
        '''
        '''
        for idx, axis_str in enumerate(lines[start_line+1:end_line]):
            self._target.axes.set_name(
                idx, name = axis_str.strip('\n').split('**')[1])
            self._target.axes.set_unit(
                idx, unit = axis_str.strip('\n').split('**')[2])
            self._target.axes.set_axis(
                idx, axis = [
                    float(e) for e in 
                    axis_str.strip('\n').split('**')[3].split(',')])

    def _subaxisReader(self,lines, start_line, end_line):
        '''
        '''
        self._subaxis = []
        for idx, axis_str in enumerate(lines[start_line+1:end_line]):
            self._subaxis.append([
                float(e) for e in 
                axis_str.strip('\n').split('**')[2].split(',')])

    def _dataReader(self, lines, start_line):
        '''
        This routine will read in the data and then 
        send it immediately to the datastructures.
        '''
        loop_elements = [
            [ l for l in range(i)] 
            for i in self._dims]

        line_num = start_line + 1
        for e in itertools.product(*loop_elements):
            self._target.addDataObject(
                np.asarray(
                    lines[line_num].strip('\n').split(',')).reshape(
                        tuple(self._subdims)),
                e, axes = np.asarray(self._subaxis) 
                if len(self._subaxis)>1 
                else np.asarray(self._subaxis[0])
            )
            line_num += 1

        self._target.validate()

