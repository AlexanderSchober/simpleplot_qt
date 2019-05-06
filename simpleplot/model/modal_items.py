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

class QColorDialog(QtWidgets.QColorDialog):
    
    def __init__(self, parent = None): 
        super().__init__(parent = parent)
        self.setModal(False)
        self.methods = []

    def connectMethod(self, method):
        '''
        '''
        self.methods.append(method)
        self.currentColorChanged.connect(self.methods[-1])

    def disconnectAll(self):
        '''
        '''
        for method in self.methods:
            try:
                self.currentColorChanged.disconnect(method)
            except:
                print('Could not disconnect', method)

class QFontDialog(QtWidgets.QFontDialog):
    
    def __init__(self, parent = None): 
        super().__init__(parent = parent)
        self.setModal(False)
        self.methods = []

    def connectMethod(self, method):
        '''
        '''
        self.methods.append(method)
        self.currentFontChanged.connect(self.methods[-1])

    def disconnectAll(self):
        '''
        '''
        for method in self.methods:
            try:
                self.currentFontChanged.disconnect(method)
            except:
                print('Could not disconnect', method)