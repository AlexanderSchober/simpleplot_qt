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

from .gui_dialogs.plot_setup_dialog import PlotSetupDialog
from .gui_plot.data_link_creator    import DataLinkCreator
from .gui_dialogs.fit_link_creator  import FitLinkCreator
from .side_bar_tree_view            import SidebarTreeView

class Sidebar(QtWidgets.QWidget):
    '''
    This will be the main playground where the sub-windows
    will be displayed. 
    '''
    def __init__(self, model, *args, **kwargs):
        super(Sidebar, self).__init__(*args, **kwargs)

        #Set up the visuals of the widget
        self._tree_view = SidebarTreeView(parent = self)
        self._add_button = QtWidgets.QPushButton("+", parent = self)
        self._remove_button = QtWidgets.QPushButton("-", parent = self)
        self._preferences_button = QtWidgets.QPushButton("pref", parent = self)

        self._tree_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self._tree_view.setModel(model)
        self._tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tree_view.expanded.connect(partial(self._tree_view.resizeColumnToContents,0))
        self._tree_view.collapsed.connect(partial(self._tree_view.resizeColumnToContents,0))

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
        # add_analysis    = temp_menu.addAction("Add Analysis to current project")
        add_plot        = temp_menu.addAction("Add Plot of current data")

        add_project.triggered.connect(self.addProject)

        # add_data_txt.triggered.connect(
        #     partial(self.addDataTxt, data_item))
        # add_data_npy.triggered.connect(
        #     partial(self.addDataNpy, data_item))
        # add_data_proc.triggered.connect(
        #     partial(self.addDataProc, data_item))

        # add_analysis.triggered.connect(self.addAnalysis)
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

    def addFit(self, item):
        '''
        '''

    def addPCA(self, item):
        '''
        '''

    def addPlot(self, item):
        '''
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

    def launchFitCreator(self):
        '''
        This will be the access point to the link creator 
        dialog that can be launched either by the plot or by
        the data instance
        '''
        dialog = FitLinkCreator()
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

            if hasattr(item, "contextMenuRequested"):
                item.contextMenuRequested(parent = self._add_button).popup(
                self._tree_view.viewport().mapToGlobal(point))
