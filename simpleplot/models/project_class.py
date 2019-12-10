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

from PyQt5 import QtCore, QtGui, QtWidgets

import collections.abc
import numpy as np

from .session_node import SessionNode
from .project_node import ProjectNode

class ProjectHandler(SessionNode):
    '''
    The need for type management of parameters and 
    other things asks for a class object rather 
    then storing the data inside of lists.
    This allows also to implement more complex schemes
    ''' 
    def __init__(self, name = 'No Name',  parent = None): 
        super().__init__(name = name, parent = parent)

    def addChild(self, name):
        '''
        Add a specific project child with the 
        right type
        '''
        new = ProjectNode(name = name)
        self._model.insertRows(
            self.childCount(),
            1,[new],self)
