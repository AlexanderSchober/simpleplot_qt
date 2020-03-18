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

import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore
from ...core.io.io_raw_import import IORawHandler

from .list_container   import ListContainer
from simpleplot.canvas.multi_canvas import MultiCanvasItem

class RawTxtImport(QtWidgets.QDialog):
    '''
    '''
    def __init__(self, target_data_structure):
        super(RawTxtImport, self).__init__()

        self.io_handler = IORawHandler()
        self.io_handler.init_raw_import()

        self._target_data_structure = target_data_structure

        self.setUpUi()
        self.connectMethods()
        self.buildListContainers()
        self.initialiseGraph()

    def setUpUi(self):
        """
        Set up the items of the UI This was taken 
        over from a rewrite of R-Data
        """
        self.setWindowTitle("Import dataset from single files")
        
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, 
            QtWidgets.QSizePolicy.Preferred)

        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setSizePolicy(sizePolicy)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(11, 11, 11, 11)
        self.main_layout.setSpacing(6)

        self.raw_import_tab = QtWidgets.QTabWidget(self)

        self.setUpFileLoad()
        self.setUpVisualLoad()
        self.setUpMetaTab()
        self.setUpDialog()

    def setUpFileLoad(self):
        """
        Set up the tab used to load the files
        """
        self.files_tab = QtWidgets.QWidget()
        self.files_layout = QtWidgets.QVBoxLayout(self.files_tab)

        #The identified section
        self.type_group_identified = QtWidgets.QGroupBox(self.files_tab)
        self.type_layout_identified = QtWidgets.QHBoxLayout(
            self.type_group_identified)

        self._setFileGroupUp()
        self._setDimGroupUp()
        self._setResultGroupUp()

        self.file_button_accept = QtWidgets.QPushButton("Accept", self.files_tab)
        self.file_button_reset = QtWidgets.QPushButton("Reset", self.files_tab)
        self.file_button_accept.setDefault(True)

        self.file_layout_nav = QtWidgets.QHBoxLayout()
        self.file_layout_nav.setSpacing(6)
        spacer = QtWidgets.QSpacerItem(
            40, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.file_layout_nav.addItem(spacer)
        self.file_layout_nav.addWidget(self.file_button_reset)
        self.file_layout_nav.addWidget(self.file_button_accept)
        self.files_layout.addLayout(self.file_layout_nav)
        self.raw_import_tab.addTab(self.files_tab, "Files")

    def _setFileGroupUp(self):
        ##################################################################
        #Set up the groupbox
        self.io_group_in = QtWidgets.QGroupBox(
            "File inputs", 
            parent = self.files_tab)
        self.io_layout_in = QtWidgets.QVBoxLayout(self.io_group_in)

        ##################################################################
        #Set the widgets up
        self.io_label_in_header = QtWidgets.QLabel(self.io_group_in)
        self.io_label_in_body = QtWidgets.QLabel(self.io_group_in)
        self.io_input_in = QtWidgets.QLineEdit(self.io_group_in)
        self.io_tool_select_in = QtWidgets.QToolButton(self.io_group_in)
        self.io_button_scan = QtWidgets.QPushButton( self.io_group_in)
        self.file_list_view = QtWidgets.QListView(self.io_group_in)

        ##################################################################
        #properties of the widgets
        self.io_label_in_header.setText("Select the input Path:")
        self.io_label_in_header.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, 
                QtWidgets.QSizePolicy.Fixed))

        self.io_label_in_body.setText(
            "This consist of telling the software in which folder the Raman spectra are located. Note that nothing else should be contained in this folder as it might result in an error when reading the information from the filename.")
        self.io_label_in_body.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, 
                QtWidgets.QSizePolicy.Fixed))
        self.io_label_in_body.setTextFormat(QtCore.Qt.PlainText)
        self.io_label_in_body.setWordWrap(True)

        self.io_tool_select_in.setText("...")
        self.io_button_scan.setText("Scan")
        
        self.io_button_scan.setAutoDefault(False)
        self.io_button_scan.setDefault(False)

        ##################################################################
        #place it all
        self.io_in_horizontal_layout = QtWidgets.QHBoxLayout()
        self.io_in_horizontal_layout.setSpacing(6)

        self.io_in_horizontal_layout.addWidget(self.io_input_in)
        self.io_in_horizontal_layout.addWidget(self.io_tool_select_in)
        self.io_in_horizontal_layout.addWidget(self.io_button_scan)

        self.io_layout_in.addWidget(self.io_label_in_header)
        self.io_layout_in.addWidget(self.io_label_in_body)
        self.io_layout_in.addLayout(self.io_in_horizontal_layout)
        self.io_layout_in.addWidget(self.file_list_view)

        self.files_layout.addWidget(self.io_group_in)
        
    def _setDimGroupUp(self):

        ##################################################################
        #Set up the groupbox
        self.type_group_identifier = QtWidgets.QGroupBox(
            "Identified the dimensions",
            parent = self.files_tab)
        self.type_layout_identifier = QtWidgets.QVBoxLayout(
            self.type_group_identifier)

        ##################################################################
        #Set the widgets up
        self.type_label_path = QtWidgets.QLabel(self.type_group_identifier)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Fixed)
        self.type_label_path.setSizePolicy(sizePolicy)
        self.type_label_path.setText("None")
        self.type_label_path.setTextFormat(QtCore.Qt.RichText)
        self.type_label_path.setWordWrap(False)
        self.type_label_path.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse|
            QtCore.Qt.TextSelectableByMouse)

        ##################################################################
        #place it all
        self.type_layout_identifier.addWidget(self.type_label_path)
        self.files_layout.addWidget(self.type_group_identifier)

    def _setResultGroupUp(self):

        ##################################################################
        #Set up the groupbox
        self.type_group_identified = QtWidgets.QGroupBox(
            "Validate the dimensions", 
            parent = self.files_tab)
        self.type_layout_identified = QtWidgets.QHBoxLayout(
            self.type_group_identified)

        ##################################################################
        #Set the widgets up
        self.type_list_dims = QtWidgets.QListView(self.type_group_identified)
        self.type_label_name = QtWidgets.QLabel(self.type_group_identified)
        self.type_input_name = QtWidgets.QLineEdit(self.type_group_identified)
        self.type_label_unit = QtWidgets.QLabel(self.type_group_identified)
        self.type_input_label = QtWidgets.QLineEdit(self.type_group_identified)
        self.type_list_single_dim = QtWidgets.QListView(self.type_group_identified)
        self.type_button_set = QtWidgets.QPushButton(self.type_group_identified)

        ##################################################################
        #properties of the widgets
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Expanding)
        self.type_list_dims.setSizePolicy(sizePolicy)

        self.type_label_name.setText("Name")
        self.type_label_unit.setText("Unit")
        self.type_button_set.setText("Set")

        ##################################################################
        #place it all

        self.type_layout_identified.addWidget(self.type_list_dims)
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        
        self.verticalLayout_2.addWidget(self.type_label_name)
        self.verticalLayout_2.addWidget(self.type_input_name)
        self.verticalLayout_2.addWidget(self.type_label_unit)
        self.verticalLayout_2.addWidget(self.type_input_label)

        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(6)
        
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem)
        
        self.horizontalLayout_10.addWidget(self.type_button_set)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        spacer = QtWidgets.QSpacerItem(
            20, 40, 
            QtWidgets.QSizePolicy.Minimum, 
            QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacer)
        self.type_layout_identified.addLayout(self.verticalLayout_2)

        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.addWidget(self.type_list_single_dim)
        self.type_layout_identified.addLayout(self.horizontalLayout_12)

        self.files_layout.addWidget(self.type_group_identified)

    def setUpVisualLoad(self):
        """
        Set up the visual tab to inspect the data to load
        """
        self.visual_tab = QtWidgets.QWidget()
        self.visual_tab.setObjectName("visual_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.visual_tab)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.visual_layout_selector = QtWidgets.QHBoxLayout()
        self.visual_layout_selector.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.visual_layout_selector.setSpacing(6)
        self.visual_layout_selector.setObjectName("visual_layout_selector")
        self.visual_label_selector = QtWidgets.QLabel(self.visual_tab)
        self.visual_label_selector.setObjectName("visual_label_selector")
        self.visual_layout_selector.addWidget(self.visual_label_selector)
        self.visual_combo_selector = QtWidgets.QComboBox(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_combo_selector.sizePolicy().hasHeightForWidth())
        self.visual_combo_selector.setSizePolicy(sizePolicy)
        self.visual_combo_selector.setMaxVisibleItems(20)
        self.visual_combo_selector.setDuplicatesEnabled(False)
        self.visual_combo_selector.setObjectName("visual_combo_selector")
        self.visual_layout_selector.addWidget(self.visual_combo_selector)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.visual_layout_selector.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.visual_layout_selector)
        self.visual_layout_plot = QtWidgets.QVBoxLayout()
        self.visual_layout_plot.setSpacing(6)
        self.visual_layout_plot.setObjectName("visual_layout_plot")
        self.visual_widget_plot = QtWidgets.QWidget(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_widget_plot.sizePolicy().hasHeightForWidth())
        self.visual_widget_plot.setSizePolicy(sizePolicy)
        self.visual_widget_plot.setObjectName("visual_widget_plot")
        self.visual_layout_plot.addWidget(self.visual_widget_plot)
        self.verticalLayout_3.addLayout(self.visual_layout_plot)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.visual_label_x = QtWidgets.QLabel(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_label_x.sizePolicy().hasHeightForWidth())
        self.visual_label_x.setSizePolicy(sizePolicy)
        self.visual_label_x.setObjectName("visual_label_x")
        self.horizontalLayout_6.addWidget(self.visual_label_x)
        self.visual_input_x = QtWidgets.QLineEdit(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_input_x.sizePolicy().hasHeightForWidth())
        self.visual_input_x.setSizePolicy(sizePolicy)
        self.visual_input_x.setObjectName("visual_input_x")
        self.horizontalLayout_6.addWidget(self.visual_input_x)
        self.lineEdit = QtWidgets.QLineEdit(self.visual_tab)
        self.lineEdit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_6.addWidget(self.lineEdit)
        self.visual_check_mergex = QtWidgets.QCheckBox(self.visual_tab)
        self.visual_check_mergex.setObjectName("visual_check_mergex")
        self.horizontalLayout_6.addWidget(self.visual_check_mergex)
        spacerItem4 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.visual_label_y = QtWidgets.QLabel(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_label_y.sizePolicy().hasHeightForWidth())
        self.visual_label_y.setSizePolicy(sizePolicy)
        self.visual_label_y.setObjectName("visual_label_y")
        self.horizontalLayout_2.addWidget(self.visual_label_y)
        self.visual_input_y = QtWidgets.QLineEdit(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual_input_y.sizePolicy().hasHeightForWidth())
        self.visual_input_y.setSizePolicy(sizePolicy)
        self.visual_input_y.setObjectName("visual_input_y")
        self.horizontalLayout_2.addWidget(self.visual_input_y)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.visual_layout_nav = QtWidgets.QHBoxLayout()
        self.visual_layout_nav.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.visual_layout_nav.setSpacing(6)
        self.visual_layout_nav.setObjectName("visual_layout_nav")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.visual_layout_nav.addItem(spacerItem6)
        self.visual_button_previous = QtWidgets.QPushButton(self.visual_tab)
        self.visual_button_previous.setObjectName("visual_button_previous")
        self.visual_layout_nav.addWidget(self.visual_button_previous)
        self.visual_button_next = QtWidgets.QPushButton(self.visual_tab)
        self.visual_button_next.setDefault(True)
        self.visual_button_next.setObjectName("visual_button_next")
        self.visual_layout_nav.addWidget(self.visual_button_next)
        self.verticalLayout_3.addLayout(self.visual_layout_nav)
        self.raw_import_tab.addTab(self.visual_tab, "Visualize")

        self.visual_label_selector.setText("Select a file: ")
        self.visual_label_x.setText("X Axis")
        self.visual_input_x.setText("Wavenumber")
        self.lineEdit.setText("cm-1")
        self.visual_check_mergex.setText("Merge X")
        self.visual_label_y.setText("Y Axis")
        self.visual_input_y.setText("Intensity")
        self.lineEdit_2.setText("a.u.")
        self.visual_button_previous.setText("Previous")
        self.visual_button_next.setText("Next")

    def setUpMetaTab(self):
        """
        Set up the visual tab to inspect the data to load
        """
        ##################################################################
        #Set up the groupbox
        self.meta_tab = QtWidgets.QWidget()
        self.meta_group_general = QtWidgets.QGroupBox(self.meta_tab)

        ##################################################################
        #Set the widgets up
        self.meta_label_name = QtWidgets.QLabel(self.meta_group_general)
        self.meta_input_name = QtWidgets.QLineEdit(self.meta_group_general)
        self.meta_label_meas_date = QtWidgets.QLabel(self.meta_group_general)
        self.meta_input_meas_date = QtWidgets.QLineEdit(self.meta_group_general)
        self.meta_label_code = QtWidgets.QLabel(self.meta_tab)
        self.meta_text_code = QtWidgets.QPlainTextEdit(self.meta_tab)
        self.meta_button_run = QtWidgets.QPushButton(self.meta_tab)
        self.meta_button_vis = QtWidgets.QPushButton(self.meta_tab)
        self.meta_button_load = QtWidgets.QPushButton(self.meta_tab)
        self.meta_button_save = QtWidgets.QPushButton(self.meta_tab)
        self.meta_button_previous = QtWidgets.QPushButton(self.meta_tab)
        self.meta_button_accept = QtWidgets.QPushButton(self.meta_tab)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, 
            QtWidgets.QSizePolicy.Fixed)
        self.meta_group_general.setSizePolicy(
            sizePolicy)

        self.meta_label_name.setAlignment(
            QtCore.Qt.AlignRight|
            QtCore.Qt.AlignTrailing|
            QtCore.Qt.AlignVCenter)

        self.meta_label_meas_date.setAlignment(
            QtCore.Qt.AlignRight|
            QtCore.Qt.AlignTrailing|
            QtCore.Qt.AlignVCenter)

        self.meta_group_general.setTitle("General information")
        self.meta_label_name.setText("Name")
        self.meta_input_name.setText("No Name")
        self.meta_label_meas_date.setText("Date")
        self.meta_label_code.setText("Sample script")
        self.meta_button_run.setText("Run")
        self.meta_button_vis.setText("Vis")
        self.meta_button_load.setText("Load")
        self.meta_button_save.setText("Save")
        self.meta_button_previous.setText("Previous")
        self.meta_button_accept.setText("Accept")

        self.meta_button_accept.setDefault(True)

        ##################################################################
        #place it all
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.meta_tab)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
    
        self.gridLayout = QtWidgets.QGridLayout(self.meta_group_general)
        self.gridLayout.addWidget(self.meta_label_name, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.meta_input_name, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.meta_label_meas_date, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.meta_input_meas_date, 0, 3, 1, 1)

        self.horizontalLayout.addWidget(self.meta_group_general)
        spacer = QtWidgets.QSpacerItem(
            40, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer)
        self.verticalLayout_9.addLayout(self.horizontalLayout)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.addWidget(self.meta_label_code)
        self.verticalLayout.addWidget(self.meta_text_code)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.addWidget(self.meta_button_run)
        self.horizontalLayout_4.addWidget(self.meta_button_vis)
        spacer = QtWidgets.QSpacerItem(
            40, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacer)
        self.horizontalLayout_4.addWidget(self.meta_button_load)
        self.horizontalLayout_4.addWidget(self.meta_button_save)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_9.addLayout(self.verticalLayout)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(
            200, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacer)
        self.horizontalLayout_8.addWidget(self.meta_button_previous)
        self.horizontalLayout_8.addWidget(self.meta_button_accept)
        self.verticalLayout_9.addLayout(self.horizontalLayout_8)
        self.raw_import_tab.addTab(self.meta_tab, "Metadata")

    def setUpDialog(self):
        """
        Set up the visual tab to inspect the data to load
        """
        ##################################################################
        #Set up the groupbox
        self.dialog_tab = QtWidgets.QWidget()
        self.io_group_out = QtWidgets.QGroupBox(self.dialog_tab)
        self.io_group_out.setMinimumSize(QtCore.QSize(600, 150))

        ##################################################################
        #Set the widgets up
        self.io_label_out_header = QtWidgets.QLabel(self.io_group_out)
        self.io_label_out_body = QtWidgets.QLabel(self.io_group_out)
        self.io_input_out = QtWidgets.QLineEdit(self.io_group_out)
        self.io_tool_select_out = QtWidgets.QToolButton(self.io_group_out)
        self.dialog_textinput_text = QtWidgets.QTextBrowser(self.dialog_tab)
        self.dialog_progressbar = QtWidgets.QProgressBar(self.dialog_tab)
        self.dialog_label_progess = QtWidgets.QLabel(self.dialog_tab)
        self.dialog_button_process = QtWidgets.QPushButton(self.dialog_tab)

        
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, 
            QtWidgets.QSizePolicy.Fixed)
        self.io_label_out_header.setSizePolicy(sizePolicy)
        self.io_label_out_body.setTextFormat(QtCore.Qt.PlainText)
        self.io_label_out_body.setWordWrap(True)
        self.io_group_out.setTitle("Output")
        self.io_label_out_header.setText("Select the output Path:")
        self.io_label_out_body.setText(
            "This is the folder in which the resulting single file processed Raman signal will be stored. If no Path is selected the folder of the input path will be used.")
        self.io_tool_select_out.setText("...")
        self.dialog_label_progess.setText("TextLabel")
        self.dialog_button_process.setText("Process")

        ##################################################################
        #place it all
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.dialog_tab)
        self.verticalLayout_16.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_16.setSpacing(6)
        
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.io_group_out)
        self.verticalLayout_8.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_8.setSpacing(6)
    
        self.io_layout_out = QtWidgets.QVBoxLayout()
        self.io_layout_out.addWidget(self.io_label_out_header)
        self.io_layout_out.addWidget(self.io_label_out_body)

        self.io_out_horizontal_layout = QtWidgets.QHBoxLayout()
        self.io_out_horizontal_layout.addWidget(self.io_input_out)
        self.io_out_horizontal_layout.addWidget(self.io_tool_select_out)
        self.io_layout_out.addLayout(self.io_out_horizontal_layout)
        self.verticalLayout_8.addLayout(self.io_layout_out)
        self.verticalLayout_16.addWidget(self.io_group_out)
        self.verticalLayout_16.addWidget(self.dialog_textinput_text)
        self.dialog_layout_progress = QtWidgets.QHBoxLayout()
        self.dialog_layout_progress.addWidget(self.dialog_progressbar)
        self.dialog_layout_progress.addWidget(self.dialog_label_progess)
        self.verticalLayout_16.addLayout(self.dialog_layout_progress)
        self.dialog_layout_navigation = QtWidgets.QHBoxLayout()
        spacerItem10 = QtWidgets.QSpacerItem(
            40, 20, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum)
        self.dialog_layout_navigation.addItem(spacerItem10)
        
        self.dialog_layout_navigation.addWidget(self.dialog_button_process)
        self.verticalLayout_16.addLayout(self.dialog_layout_navigation)

        self.raw_import_tab.addTab(self.dialog_tab, "Import")
        self.main_layout.addWidget(self.raw_import_tab)

    def _set_meas(self):
        '''
        This method will connect all click events to
        the right handlers. 
        '''
        self.meta_text_code.setPlainText(self.io_handler.meas_string)
        self.meta_button_load.clicked.connect(self.run_code)

    def run_code(self):
        '''
        This method will connect all click events to
        the right handlers. 
        '''
        exec(self.meta_text_code.toPlainText())

    def initialiseGraph(self):
        '''
        This method will connect all click events to
        the right handlers. 
        '''
        self.my_canvas    = MultiCanvasItem(
            self.visual_widget_plot,
            grid        = [[True]],
            x_ratios    = [1],
            y_ratios    = [1],
            background  = "w",
            highlightthickness = 0)

        self.ax = self.my_canvas.getSubplot(0,0)
        self.plot_line = self.ax.addPlot(
            'Scatter', 
            Name        = 'data', 
            Style       = ['-','d','r', '10'], 
            Log         = [False,False])
        self.ax.draw()  

    def connectMethods(self):
        '''
        This method will connect all click events to
        the right handlers. 
        '''
        self.io_button_scan.clicked.connect(self.scan_folder_in)
        self.file_button_accept.clicked.connect(self.process_files)
        #self.file_button_reset.clicked.connect(self.reset_list_files)
        self.type_button_set.clicked.connect(self._set_dim)
        
        self.io_tool_select_in.clicked.connect(self.open_folder_in)
        self.io_tool_select_out.clicked.connect(self.open_file_out)

        self.visual_combo_selector.currentIndexChanged.connect(self._plot_file)
        self.dialog_button_process.clicked.connect(self._process_export)

    def buildListContainers(self):
        '''
        This method will manage the list elements to 
        child containers for them including, their name
        as a dictionary pointer, the list Qt item,
        the model, and the element list
        '''
        self.list_dictionary = {}

        list_elements = [
            [
                'file', self.file_list_view, True, True, 
                self._file_changed, None],
            [
                'type', self.type_list_dims, True, True, 
                self._dimension_changed, None],
            [
                'dim' , self.type_list_single_dim, 
                False, False, None, None]
        ]

        for element in list_elements:
            self.list_dictionary[element[0]] = ListContainer(element[1])
            self.list_dictionary[element[0]].build_container(
                check       = element[2],
                true        = element[3],
                clicked     = element[4],
                itemchanged = element[5])

    def open_folder_in(self):
        self.io_handler.set_import_directory(
            QtWidgets.QFileDialog.getExistingDirectory(
                parent = self, 
                caption = "Select directory"))
                
        self.io_input_in.setText(self.io_handler.directory_path)

    def open_file_out(self):
        self.io_handler.set_save_file(
            QtWidgets.QFileDialog.getSaveFileName(
                self.window, 
                'Select file')[0])

        self.io_input_out.setText(self.io_handler.save_file_path)

    def scan_folder_in(self):
        '''
        This method will scan the directory provided
        by the user and try to 
        '''
        if not self.io_handler.directory_path == self.io_input_in.text():
            self.io_handler.set_import_directory(self.io_input_in.text())
            self.io_handler.evaluate_files()
            
        self.list_dictionary['file'].reset_list()
        self.list_dictionary['type'].reset_list()
        self.list_dictionary['dim'].reset_list()

        self.type_input_name.setText('')
        self.type_input_label.setText('')
        self.type_label_path.setText(self.io_handler.visual_string)
        self.visual_combo_selector.clear()
        
        for item in self.io_handler.scan_directory(): 

            self.list_dictionary['file'].add_item_to_list(item)

        self.visual_combo_selector.addItems(
            [element.split(os.path.sep)[-1] for element in self.io_handler.file_list])
        self.visual_combo_selector.setStyleSheet(
            "QComboBox { combobox-popup: 0; }")

        self.process_files()

    def process_files(self):
        '''
        This method will handle the add item routine
        '''
        self.io_handler.evaluate_files()
        self.type_label_path.setText(self.io_handler.visual_string)
        self._build_list_dimensions()

    def _process_export(self):
        '''
        This method will handle the add item routine
        '''
        self.io_handler.save_file_path = self.io_input_out.text()
        self.io_handler.process_import(self._target_data_structure)

    def _build_list_dimensions(self):
        '''
        This method will handle the add item routine
        '''
        self.list_dictionary['type'].reset_list()

        for item in self.io_handler.dimension_list: 
            self.list_dictionary['type'].add_item_to_list(item[0])

        self.list_dictionary['type'].dictionary['view'].setCurrentIndex(
            self.list_dictionary['type'].dictionary['model'].index(0,0))

        try:
            self._dimension_changed(self.list_dictionary['type'].dictionary['model'].index(0,0))
        except:
            self._dimension_changed(None)

    def _dimension_changed(self, index):
        '''
        This method will handle the add item routine
        '''
        if index == None:
            self.list_dictionary['type'].reset_list()
            self.type_input_name.setText('')
            self.type_input_label.setText('')

        else:
            if self.list_dictionary['type'].dictionary['model'].item(index.row()).checkState() == QtCore.Qt.Checked:
                self.io_handler.dimension_list[index.row()][4] = True

            else:
                self.io_handler.dimension_list[index.row()][4] = False
                
            self.io_handler.build_string()
            self.type_label_path.setText(self.io_handler.visual_string)

            self.type_input_name.setText(
                self.io_handler.dimension_list[index.row()][0])
            self.type_input_label.setText(
                self.io_handler.dimension_list[index.row()][1])
                
            self.list_dictionary['dim'].reset_list()
            
            for item in self.io_handler.dimension_list[index.row()][-1]: 
                self.list_dictionary['dim'].add_item_to_list(str(item))

    def _file_changed(self, index):
        '''
        This method will handle the add item routine
        '''
        if self.list_dictionary['file'].dictionary['model'].item(index.row()).checkState() == QtCore.Qt.Checked:
            check = True

        else:
            check = False
            
        self.io_handler.toggle_mask(
            index.row(),
            check)

        self.process_files()
        self.visual_combo_selector.clear()
        self.visual_combo_selector.addItems(
            [element.split(os.path.sep)[-1] for element in self.io_handler.file_list])
        self._plot_file(0)

    def _set_dim(self):
        '''
        This method will handle the add item routine
        '''
        row = self.list_dictionary['type'].dictionary['view'].selectedIndexes()[0].row()

        name = self.type_input_name.text()
        unit = self.type_input_label.text()
        
        self.io_handler.set_dim_meta(row ,name = name, unit = unit)
        self.list_dictionary['type'].dictionary['model'].item(row).setText(name)
        self.type_label_path.setText(self.io_handler.visual_string)

    def _plot_file(self, index):
        '''
        This method will handle the add item routine
        '''
        x, y = self.io_handler.grab_data_from_file(index)
        self.plot_line.setData(x = x, y = y)
        
    def next_tab(self):
        pass

    def previous_tab(self):
        pass


if __name__ == "__main__":
    pass

    # from ..io  import io_raw_import
    # from ..io  import io_data_import
    # from ..data import datastructure
    
    # #initialize an io_handler
    # handler = io_raw_import.IORawHandler()
    
    # #set up the app
    # app         = QtWidgets.QApplication(sys.argv)
    # window      = QtWidgets.QMainWindow()
    # interface   = RawWindow(window, handler)

    # #fast input for debugging
    # interface.io_input_in.setText('/Users/alexanderschober/Dropbox/software/R-DATA/Demo/DemoRawImport')
    # interface.io_input_out.setText('/Users/alexanderschober/Dropbox/software/R-DATA/Demo/test.txt')
    # interface.scan_folder_in()
    # interface.process_files()
    # interface._process_export()
    # window.show()

    # data = datastructure.Data_Structure()
    # handler_2 = io_data_import.IOImportHandler()
    # handler_2.readDataFile('/Users/alexanderschober/Dropbox/software/R-DATA/Demo/test.txt', data)



    # sys.exit(app.exec_())
