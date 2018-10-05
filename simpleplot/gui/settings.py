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


import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import sys

from misc import Multi_Widget

class Pref_Window(QtGui.QMainWindow):

    def __init__(self, parent = None):
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
        super(Pref_Window, self).__init__(parent)
        self.main_widget  = Pref_Widget(self)
        self.setCentralWidget(self.main_widget)
        self.show()


class Pref_Widget(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
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
        self.build()

    def build(self):
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

        #initialise the tab
        self.layout = QtWidgets.QVBoxLayout()
        self.tabs	= QtWidgets.QTabWidget()


        #set the individual widgets
        self.tab_1	= QtWidgets.QWidget()	
        self.tab_2	= Pointer_Tab()
        self.tab_3	= QtWidgets.QWidget()
        self.tab_4	= Save_Tab()

            
        # Add the tabs
        self.tabs.addTab(self.tab_1,"Layout")
        self.tabs.addTab(self.tab_2,"Pointer")
        self.tabs.addTab(self.tab_3,"Items")
        self.tabs.addTab(self.tab_4,"Export") 

        #add the tabs
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        

class Pointer_Tab(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
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

        #build the widget view
        self.build()


    def build(self):
        '''
        ##############################################
        Build the widget tab widget for the actual
        export options. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        ##############################################
        #initialise the tab
        self.container      = QtWidgets.QVBoxLayout()

        self.group_1        = QtWidgets.QGroupBox('Pointer')
        self.grid_layout    = QtWidgets.QGridLayout()
        self.widget_list    = []

        ##############################################
        #populate it
        
        #0
        self.widget_list.append([
            Multi_Widget(
                4, 
                'label', 
                parent = self,
                values = ['Top', 'Bot', 'Left', 'Right']),
            0, 1, None])

        self.widget_list.append([
            QtWidgets.QLabel('Labels:', parent = self),
            1, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter])

        #2
        self.widget_list.append([
            Multi_Widget(
                4, 
                'check', 
                parent = self,
                values = [True, True, True, True ]),
            1, 1, None])

        self.widget_list.append([
            QtWidgets.QLabel('Ticks:', parent = self),
            2, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter])

        #4
        self.widget_list.append([
            Multi_Widget(4, 'check', parent = self),
            2, 1, None])

        self.widget_list.append([
            QtWidgets.QLabel('Scientific:', parent = self),
            3, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter])

        #6
        self.widget_list.append([
            Multi_Widget(4, 'check', parent = self),
            3, 1, None])

        self.widget_list.append([
            QtWidgets.QLabel('Precision:', parent = self),
            4, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter])

        #6
        self.widget_list.append([
            Multi_Widget(4, 'input', parent = self),
            4, 1, None])


        ##############################################
        #add the tabs
        for element in self.widget_list:

            self.grid_layout.addWidget(element[0], element[1], element[2])
            
            #manage alignement
            if not element[3] == None:
                element[0].setAlignment(element[3])

        ##############################################
        #set the methods and data


        ##############################################
        #set up the end

        self.group_1.setLayout(self.grid_layout)
        self.container.addWidget(self.group_1)
        self.container.addStretch(1)
        self.setLayout(self.container)

    def get_export_path(self, i):
        '''
        ##############################################
        Set the file export path
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.path, self.allowed = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        self.widget_list[1][0].setText(self.path)

    def set_export_format(self, idx):
        '''
        ##############################################
        Set the file export format
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.format = self.widget_list[3][0]


    def export(self):
        '''
        ##############################################
        The export function
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass

class Save_Tab(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
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

        #variabmes
        self.path       = ''
        self.format     = 'PNG'
        self.formats    = ['PNG', 'SVG', 'CSV', 'Matplotlib', 'Print', 'Text']
        self.allowed    = None

        #build the widget view
        self.build()


    def build(self):
        '''
        ##############################################
        Build the widget tab widget for the actual
        export options. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        ##############################################
        #initialise the tab
        self.container      = QtWidgets.QVBoxLayout()
        self.group_1        = QtWidgets.QGroupBox('Save options')
        self.grid_layout    = QtWidgets.QGridLayout()
        self.widget_list    = []
        ##############################################
        #populate it
        
        #0
        self.widget_list.append([
            QtWidgets.QPushButton('Select path', parent = self),
            0, 1, None])

        #1
        self.widget_list.append([
            QtWidgets.QLineEdit('Nothing selected', parent = self),
            0, 0, None])
 
        #2
        self.widget_list.append([
            QtWidgets.QLabel('Format:', parent = self),
            1, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter])

        #3
        self.widget_list.append([
            QtWidgets.QComboBox(parent = self),
            1,1, None])

        #4
        self.widget_list.append([
            QtWidgets.QCheckBox('Invert X and Y (text save)', parent = self),
            2,0, None])

        self.widget_list.append([
            QtWidgets.QPushButton('Save', parent = self),
            3,1, None])

        ##############################################
        #add the tabs
        for element in self.widget_list:

            self.grid_layout.addWidget(element[0], element[1], element[2])
            
            #manage alignement
            if not element[3] == None:
                element[0].setAlignment(element[3])

        ##############################################
        #set the methods and data
        self.widget_list[0][0].clicked.connect(self.get_export_path)
        self.widget_list[3][0].currentIndexChanged.connect(self.set_export_format)
        self.widget_list[3][0].addItems(self.formats)
        self.widget_list[5][0].clicked.connect(self.export)


        ##############################################
        #set up the end
        
        self.group_1.setLayout(self.grid_layout)
        self.container.addWidget(self.group_1)
        self.container.addStretch(1)
        self.setLayout(self.container)


    def get_export_path(self, i):
        '''
        ##############################################
        Set the file export path
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.path, self.allowed = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        self.widget_list[1][0].setText(self.path)

    def set_export_format(self, idx):
        '''
        ##############################################
        Set the file export format
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.format = self.widget_list[3][0]


    def export(self):
        '''
        ##############################################
        The export function
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass



if __name__ == "__main__":

    app 	    = QtWidgets.QApplication(sys.argv)
    widget      = QtWidgets.QWidget()
    widget.show()

    new = Pref_Window(widget)


    sys.exit(app.exec_())