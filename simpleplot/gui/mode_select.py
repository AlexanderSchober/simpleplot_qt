
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

from PyQt5 import QtWidgets, QtGui, QtCore
import os
from functools import partial

class Mode_Select(QtWidgets.QHBoxLayout):


    def __init__(self, multi_canvas, parent, icon_dim):
        '''
        ##############################################
        Selector toolbar for the mode used for the
        pointer. 
        ———————
        Input: 
        - parent is the widget parent
        - icondim is a integers
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        QtWidgets.QHBoxLayout.__init__(self)
        self.multi_canvas = multi_canvas
        self.initialize(parent, icon_dim)
        self.selected = 0
        self.process(0)
        


    def initialize(self, parent, icon_dim):
        '''
        ##############################################
        Setting up the button environement
        ———————
        Input: 
        - parent is the widget parent
        - icondim is a integers
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #######################
        #Modes and variables
        self.modes = [
            ("Zoom"       , 0),
            ("Measure"    , 1),
            ("Edit"       , 2),
            ("Settings"   , 3),
            ]
    
        #######################
        #Grab the Path
        Path = os.path.join(os.path.dirname(__file__),'ressources')
        self.buttons = []

        #######################
        #populate buttons
        for i in range(len(self.modes)):

            self.buttons.append(QtWidgets.QPushButton('', parent))
            self.buttons[i].setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(Path,self.modes[i][0]+'.jpg'))))
            self.buttons[i].setIconSize(QtCore.QSize(icon_dim, icon_dim))
            self.buttons[i].setStyleSheet('background-color: silver; border-style: inset;border-width: 2px')
            self.buttons[i].setCheckable(True)
            self.buttons[i].clicked.connect(partial(self.process,i))
            self.addWidget(self.buttons[i])

        self.label = QtWidgets.QLabel(parent)
        self.label.setText('')
        self.addWidget(self.label)
        
        #######################
        #add a stretch to the selector
        self.addStretch(1)
        self.setSpacing(2)

                
    def process(self, idx):
        '''
        ##############################################
        This method will try to resolv the click
        action and then select the current mode. Note
        that the cnavas will have to grab this value
        to select the cose pointer method. 
        ———————
        Input: 
        - idx
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #set the variable 
        self.selected = idx

        #set all buttons inset
        for i in range(len(self.modes)):

            self.buttons[i].setStyleSheet('background-color: silver; border-style: inset;border-width: 2px')
            
        #se tht eselected button outset
        self.buttons[idx].setStyleSheet('background-color: grey; border-style: outset;border-width: 2px')


        for elements in self.multi_canvas.canvas_objects:
            for subelement in elements:
                subelement[0].artist.set_mode(idx)
