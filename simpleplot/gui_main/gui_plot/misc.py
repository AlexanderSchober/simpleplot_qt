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

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Multi_Widget(QtWidgets.QWidget):
    
    def __init__(self, num, w_type, parent = None, values = None):
        '''
        ##############################################
        Initialize the settings window. It will inherit
        from the window class of pyqt. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        super(QtWidgets.QWidget, self).__init__(parent)
        self.show()
        self.parent = parent
        self.w_type = w_type
        self.build(num)

        if not values == None:
            self.set_values(values)


    def build(self, num):
        '''
        ##############################################
        Build the widget tab view
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #initialise the widget
        self.layout = QtWidgets.QHBoxLayout()

        if self.w_type == 'check':
            self.widget_list = [QtWidgets.QCheckBox(self.parent) for i in range(num)]

        elif self.w_type == 'label':
            self.widget_list = [QtWidgets.QLabel(self.parent) for i in range(num)]

        elif self.w_type == 'input':
            self.widget_list = [QtWidgets.QLineEdit(self.parent) for i in range(num)]

        for widget in self.widget_list:

            self.layout.addWidget(widget)

        self.setLayout(self.layout)


    def set_values(self, values):
        '''
        ##############################################
        Set the 
        ———————
        Input: 
        - values list of strings or booleans that will 
        be set into the targeted field. 
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        if self.w_type == 'check':
            for i in range(len(self.widget_list)):
                self.widget_list[i].setChecked(values[i])

        elif self.w_type == 'label':
            for i in range(len(self.widget_list)):
                self.widget_list[i].setText(str(values[i]))

        elif self.w_type == 'input':
            for i in range(len(self.widget_list)):
                self.widget_list[i].setText(str(values[i]))


    def get_values(self):
        '''
        ##############################################
        get the values from the individual fields as
        a list and return them. The checkbox buttons
        will be returned as booleans.  
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        values = []

        if self.w_type == 'check':
            for i in range(len(self.widget_list)):
                values.append(self.widget_list[i].isChecked(values[i]))

        elif self.w_type == 'label':
            for i in range(len(self.widget_list)):
                values.append(self.widget_list[i].text)

        elif self.w_type == 'input':
            for i in range(len(self.widget_list)):
                values.append(self.widget_list[i].text)

        return list(values)


    def setAlignment(self, alignement):
        '''
        ##############################################
        get the values from the individual fields as
        a list and return them. The checkbox buttons
        will be returned as booleans.  
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        for element in self.widget_list:
            element.setAlignment(alignement)