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

from .io_file_methods import *
import itertools
import datetime

class IODataSave:
    '''
    This class will handle most of the saving in 
    different file formats. This includes stand 
    alone saves such as hdf5 and text but 
    eventually also saves in the project folder.
    '''

    def __init__(self, source, path:str):
        '''
        define the local elements and proceed with the 
        saving procedure.
        '''
        self._source = source
        self._path = path

    def save(self, file_format:str):
        '''
        The save entry point
        '''
        if file_format == "txt":
            self._saveToTxt()
        elif file_format == "hdf5":
            self._saveToTxt()

    def _saveToTxt(self):
        '''
        Save the dataset to text ...
        '''
        metadata_string = self._metaWriter()
        axis_string = self._axisWriter()
        subaxis_string = self._subaxisWriter()
        data_string = self._dataWriter()

        self._writeTxtFile(
            metadata_string, axis_string, 
            subaxis_string, data_string)

    def _metaWriter(self):
        '''
        This method will generate a string with the 
        input being a list of strings that are
        common to all files...
        '''
        output = ""
        output += "SimplePlot_Data_file"
        output += "\n\n################# METADATA ###################\n"
        output += "This file was created on the " + str(datetime.datetime.now()) + "\n"
        #output += "The measurement ID is: " + str(self.meas_id) + "\n"
        #output += "The sample ID is: " + str(self.sam_id) + "\n"
    
        return output

    def _axisWriter(self):
        '''
        This method will generate a string with the 
        input being a list of strings that are
        common to all files...
        '''
        output = ""
        output += "#################   AXIS   ###################\n"
        
        for i in range(self._source.axes.dim):
            temp_list = (
                "**" + self._source.axes.names[i]+ '**'
                + self._source.axes.units[i]+"**"
                + self._listToString(self._source.axes.axes[i]))

            output += temp_list + "\n"

        return output

    def _subaxisWriter(self):
        '''
        This method will generate a string with the 
        input being a list of strings that are
        common to all files...
        '''
        output = ""
        output += "################   SUBAXIS   #################\n"

        data_dummy = self._source.DataObjects[0]
        dim = len(data_dummy.data.shape)
        
        for i in range(dim):
            temp_out = "**" + str(i) + "**"
            if dim == 1 and not data_dummy.axes is None:
                temp_out += self._listToString(data_dummy.axes.tolist())
            elif dim == 1 and data_dummy.axes is None:
                temp_out += self._listToString([
                    j for j in range(data_dummy.data.shape[i])])
            elif dim == 2 and not data_dummy.axes is None:
                temp_out += self._listToString(data_dummy.axes[i].tolist())
            elif dim == 2 and data_dummy.axes is None:
                temp_out += self._listToString(
                    [j for j in range(data_dummy.data.shape[i])])
            output += temp_out + "\n"

        return output

    def _dataWriter(self):
        '''
        This method will generate a string with the 
        input being a list of strings that are
        common to all files...
        '''
        output = ""
        output += "#################   DATA   ###################\n"

        loop_elements = [
            [ l for l in range(i)] 
            for i in self._source.axes.axes_len]

        for e in itertools.product(*loop_elements):
            data_ptr = self._source[e]
            temp_list = data_ptr.flatten().tolist()
            output += self._listToString(temp_list)+ "\n"
        return output

    def _writeTxtFile(self, metadata_string, axis_string, subaxis_string, data_string):
        '''
        Finally write the file
        '''
        text_file = open(self._path+".txt", "w")

        text_file.write(metadata_string)
        text_file.write(axis_string)
        text_file.write(subaxis_string)   
        text_file.write(data_string)     

        text_file.close()

    def _saveToHdf5(self):
        '''
        Save the dataset to text ...
        '''

    def _listToString(self,list_item):
        '''
        This method returns a string from an input 
        list.
        ———————
        Input: 
        - list_item ([ints, float, str])
        '''
        output = ""

        for item in list_item:
            output += str(item) + ","

        return output[:len(output) - 1]
