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

from PyQt5 import QtWidgets, QtGui, QtCore
import os


class PCAWidget(QtWidgets.QWidget):
    '''
    '''
    def __init__(self,data_pointer, *args, **kwargs):
        super(PCAWidget, self).__init__(*args, **kwargs)
        self._setupLayout()
        self._connectMethods()

    def _setupLayout(self):
        '''
        This will build the layout of the current widget 
        by placing the two main components
        '''

    def _connectMethods(self):
        '''
        Connec the methods to their outs
        '''
 