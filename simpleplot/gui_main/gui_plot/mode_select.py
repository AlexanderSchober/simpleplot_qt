
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
from .settings import PreferenceWidget
from ...ressources.icons import icons

class ModeSelect(QtWidgets.QToolBar):

    def __init__(self, multi_canvas, parent, icon_dim):
        '''
        Selector toolbar for the mode used for the
        pointer. 
        ———————
        Input: 
        - parent is the widget parent
        - icondim is a integers
        '''
        super().__init__(parent)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setFixedHeight(36)

        self.multi_canvas = multi_canvas
        self.initialize(parent, icon_dim)
        self.selected = 0
        self.process(0)
        self.settings = PreferenceWidget(self.multi_canvas)
        self.multi_canvas.dock_widget.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, 
            self.settings.setting_widget)
        self.settings.setting_widget.hide()

    def initialize(self, parent, icon_dim):
        '''
        Setting up the button environnement
        ———————
        Input: 
        - parent is the widget parent
        - icondim is a integers
        '''
        #Modes and variables
        self.modes = [
            (r"magnify-plus" , 0),
            (r"ruler" , 1),
            (r"pencil" , 2),
            (r"cog" , 3)
            ]
        #Grab the Path
        
        self.buttons = []
        #populate buttons
        for i in range(len(self.modes)):
            self.buttons.append(QtWidgets.QToolButton(parent))
            self.buttons[i].setIcon(QtGui.QIcon(":/"+self.modes[i][0]+".svg"))
            if i < len(self.modes) - 1:
                self.buttons[i].setCheckable(True)
                self.buttons[i].clicked.connect(partial(self.process,i))
            else:
                self.buttons[i].clicked.connect(self.openSettings)
            self.addWidget(self.buttons[i])

        self.label = QtWidgets.QLabel(parent)
        self.label.setText('')
        self.addWidget(self.label)
                
    def process(self, idx):
        '''
        This method will try to resolve the click
        action and then select the current mode. Note
        that the canvas will have to grab this value
        to select the pointer method. 
        '''
        #set the variable 
        self.selected = idx

        #set all buttons inset
        for i in range(len(self.modes)):
            self.buttons[i].setChecked(False)
        self.buttons[idx].setChecked(True)

        for elements in self.multi_canvas.canvas_nodes:
            for subelement in elements:
                try:
                    subelement[0].artist().setMode(idx)
                except:
                    pass

    def openSettings(self, ev = None, mode = None, target = None):
        '''
        Open the settings window with the proper mode in
        place
        '''
        if mode == 'Save' and not target == None:
            self.settings.tabWidget.setCurrentIndex(3)
            self.settings.export_widget.ui.expSubplot.setCurrentText(target)
        self.settings.setting_widget.show()
