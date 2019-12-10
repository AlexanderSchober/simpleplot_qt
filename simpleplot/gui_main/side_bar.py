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

from functools import partial

from .gui_dialogs.raw_txt_import    import RawTxtImport
from .gui_dialogs.plot_setup_dialog import PlotSetupDialog
from .gui_plot.data_link_creator    import DataLinkCreator

class Sidebar(QtWidgets.QWidget):
    '''
    This will be the main playground where the sub-windows
    will be displayed. 
    '''
    def __init__(self, model, *args, **kwargs):
        super(Sidebar, self).__init__(*args, **kwargs)

        #Set up the visuals of the widget
        self._tree_view = QtWidgets.QTreeView(parent = self)
        self._add_button = QtWidgets.QPushButton("+", parent = self)
        self._remove_button = QtWidgets.QPushButton("-", parent = self)
        self._preferences_button = QtWidgets.QPushButton("pref", parent = self)

        self._tree_view.setSelectionBehavior(
            QtWidgets.QTableView.SelectRows)
        self._tree_view.setModel(model)
        self._tree_view.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self._add_button)
        bottom_layout.addWidget(self._remove_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self._preferences_button)

        sidebar_layout.addWidget(self._tree_view)
        sidebar_layout.addLayout(bottom_layout)

        self._add_button.clicked.connect(self.selectAddAction)
        self._tree_view.customContextMenuRequested.connect(
            self.contextMenuRequested)

    def selectAddAction(self):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        temp_menu = QtWidgets.QMenu(self._add_button)

        temp_data_menu = QtWidgets.QMenu("Add Data", parent = temp_menu)
        add_data_txt = temp_data_menu.addAction("Add from text files ...")
        add_data_npy = temp_data_menu.addAction("Add from npy file ...")
        add_data_proc = temp_data_menu.addAction("Add from processed format ...")

        add_project     = temp_menu.addAction("Add Project")
        temp_menu.addMenu(temp_data_menu)
        add_analysis    = temp_menu.addAction("Add Analysis to current project")
        add_plot        = temp_menu.addAction("Add Plot of current data")

        add_project.triggered.connect(self.addProject)

        # add_data_txt.triggered.connect(
        #     partial(self.addDataTxt, data_item))
        # add_data_npy.triggered.connect(
        #     partial(self.addDataNpy, data_item))
        # add_data_proc.triggered.connect(
        #     partial(self.addDataProc, data_item))

        add_analysis.triggered.connect(self.addAnalysis)
        add_plot.triggered.connect(self.addPlot)

        position = self.mapToGlobal(self._add_button.geometry().topLeft())
        position.setY(position.y() - temp_menu.sizeHint().height())
        temp_menu.popup(position)

    def addProject(self):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'New Project Name', 'Enter the name of the project:')
            
        if ok:
            self._tree_view.model().root().addChild(text)
            
    def addDataTxt(self, item):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        data_item = item.addDataItem()
        window = RawTxtImport(data_item.data_item)
        window.show()
        return window

    def addDataNpy(self, item):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''

    def addDataProc(self, item):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''


    def addAnalysis(self, item):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''

    def addPlot(self, item):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        dialog = PlotSetupDialog()
        dialog.accepted.connect(partial(self.createPlotItem, item))
        dialog.exec()

    def createPlotItem(self,parent, item):
        '''
        Adds the item to the treeview upon completion
        '''
        self._tree_view.model().insertRows(
            parent.childCount(), 1, [item], parent)

    def launchLinkCreator(self):
        '''
        This will be the access point to the link creator 
        dialog that can be launched either by the plot or by
        the data instance
        '''
        dialog = DataLinkCreator()
        dialog.exec()

    def contextMenuRequested(self, point):
        '''
        Tell the current gui that a right click 
        has been performed on the tree view and 
        that something has to be done
        '''
        index = self._tree_view.indexAt(point)
        if index.isValid():
            item = self._tree_view.model().getNode(index)

            if item.descriptor == "project":

                temp_menu = QtWidgets.QMenu(self._add_button)
                temp_data_menu = QtWidgets.QMenu("Add Data", parent = temp_menu)
                temp_menu.addMenu(temp_data_menu)

                add_data_txt = temp_data_menu.addAction(
                    "Add from text files ...")
                add_data_npy = temp_data_menu.addAction(
                    "Add from npy file ...")
                add_data_proc = temp_data_menu.addAction(
                    "Add from processed format")

                add_analysis = temp_menu.addAction(
                    "Add Analysis to current project")
                add_plot  = temp_menu.addAction(
                    "Add Plot of current data")

                data_item = item.childFromName("data")
                analysis_item = item.childFromName("analysis")
                plot_item = item.childFromName("plot")

                add_data_txt.triggered.connect(
                    partial(self.addDataTxt, data_item))
                add_data_npy.triggered.connect(
                    partial(self.addDataNpy, data_item))
                add_data_proc.triggered.connect(
                    partial(self.addDataProc, data_item))

                add_analysis.triggered.connect(
                    partial(self.addAnalysis, analysis_item))
                add_plot.triggered.connect(
                    partial(self.addPlot, plot_item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))

            elif item.descriptor == "data":

                temp_menu = QtWidgets.QMenu(self._add_button)

                add_data_txt = temp_menu.addAction(
                    "Add from text files ...")
                add_data_npy = temp_menu.addAction(
                    "Add from npy file ...")
                add_data_proc = temp_menu.addAction(
                    "Add from processed format")
                
                add_data_txt.triggered.connect(partial(self.addDataTxt, item))
                add_data_npy.triggered.connect(partial(self.addDataNpy, item))
                add_data_proc.triggered.connect(partial(self.addDataProc, item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))

            elif item.descriptor == "data item":
                temp_menu = QtWidgets.QMenu(self._add_button)

                change_name  = temp_menu.addAction(
                    "Rename")
                show_data_MDI  = temp_menu.addAction(
                    "Show on Mdi surface")
                show_data_Window  = temp_menu.addAction(
                    "Show on external window")

                show_data_MDI.triggered.connect(partial(
                    self.parent().parent()._playground.addData, item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))

            elif item.descriptor == "analysis":

                temp_menu = QtWidgets.QMenu(self._add_button)

                add_analysis = temp_menu.addAction(
                    "Add Analysis to current project")

                add_analysis.triggered.connect(partial(self.addAnalysis, item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))

            elif item.descriptor == "plot":
                temp_menu = QtWidgets.QMenu(self._add_button)

                add_plot  = temp_menu.addAction(
                    "Add Plot of current data")

                add_plot.triggered.connect(partial(self.addPlot, item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))

            elif item.descriptor == "plot item":
                temp_menu = QtWidgets.QMenu(self._add_button)

                change_name  = temp_menu.addAction(
                    "Rename")
                show_plot_MDI  = temp_menu.addAction(
                    "Show on Mdi surface")
                show_plot_Window  = temp_menu.addAction(
                    "Show on external window")

                show_plot_MDI.triggered.connect(partial(
                    self.parent().parent()._playground.addPlot, item))

                temp_menu.popup(self._tree_view.viewport().mapToGlobal(point))
