#--FUNCTION--#

#  -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by Alexander Schober 
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


from ..function_template import InfoClass
from ..function_template import FunctionClass

import numpy as np

class BaselineInfo(InfoClass):
    '''
    This class will contain information about 
    the function, parameters and names
    '''
    def __init__(self):
        InfoClass.__init__(self)
        
        #######################
        #name of the function
        self.name = 'Baseline'
        
        #how to order the functions(do not touch lorenz, baseline and linear)
        self.order = 0
        
        #number of parameters
        self.para_num   = 1
        
        #######################
        #parameter names
        self.para_name = [
            ['Offset', 0.]]
                                        
        #Parameter units
        self.para_unit  = [
            'Intensity']

        self.para_fix_ini   = [
            False]   
                                       
        #######################
        #Parameter Boundaries
        self.para_bound    = [
            ['-1000','1000', False],    # <- Relative shift min, max
            ['-Inf','Inf', True]         # <- Absolute shift min, max
            ]

        #######################
        #Parameter Boundaries
        self.para_proc    = [
            2,         # <- Number of iteration
            [0]]   # <- Order of Processing

class Baseline(FunctionClass):
    '''
    In this class we will store the 
    cropped data used for the calculation
    this data can be modified once the class 
    is loaded to fit the needs
    '''
    
    def __init__(self, info, source = None):
        FunctionClass.__init__(self, info, source)
    
    def function(self,para):
        '''
        This is the baseline function
        '''
        #function parameters
        x           = np.asarray(para[0])
        Offset      = para[1]
    
        #process the function
        y           = np.zeros(x.shape[0]) + Offset
        return y
    