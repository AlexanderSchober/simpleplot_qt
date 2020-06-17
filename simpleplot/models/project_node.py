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

from .session_node import SessionNode
from PyQt5 import QtWidgets, QtGui, QtCore
from functools import partial

from ..core.data.data_structure import DataStructure
from ..core.data.plot_data_injector import PlotDataInjector
from ..core.data.fit_data_injector import FitDataInjector
from ..core.fit.fit_handler import FitHandler

from ..canvas.multi_canvas import MultiCanvasItem
from ..gui_main.gui_subwindows.subwindow_data.data_widget import DataWidget
from ..gui_main.gui_subwindows.subwindow_analysis.fit_widget import FitWidget
from ..core.io.io_data_import import IODataLoad
from ..gui_main.gui_dialogs.raw_txt_import import RawTxtImport

class ProjectNode(SessionNode):
    def __init__(self, name = 'New Project', parent = None, parameters = {}, method = None):
        SessionNode.__init__(self, name, parent)
        self.description = ""
        self.descriptor = 'project'
        
        self.addChild(DatasetsNode())
        self.addChild(AnalysisNode())
        self.addChild(PlotNode())
 
    def data(self, column):
        if   column == 0: return self._name
        elif column == 1: return self.description

    def setData(self, column, value):
        pass
    
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled 
        elif index.column() == 1:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.NoItemFlags

    def contextMenuRequested(self, parent = None):
        """
        This method starts when the context menu is requested. 
        It will generate it on the fly and then return it.
        """
        temp_menu = QtWidgets.QMenu(self._name, parent)
        for child in self._children:
            if hasattr(child, "contextMenuRequested"):
                temp_menu.addMenu(child.contextMenuRequested(parent = temp_menu))

        return temp_menu

class DatasetsNode(SessionNode):
    def __init__(self, name = 'Datasets', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "data"
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def addDataItem(self):
        temp = DataItem(name = 'Dataset ' + str(self.childCount()))
        self.model().insertRows(self.childCount(), 1, [temp], self)
        return temp

    def addDataTxt(self):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        data_item = self.addDataItem()
        window = RawTxtImport(data_item.data_item)
        window.show()
        return window

    def addDataNpy(self):
        '''
        Tell the current main Session node
        of the current model to add a new
        project with the name determined 
        from the dialog
        '''
        path = QtWidgets.QFileDialog.getOpenFileName(
            parent = self, filter = "Numpy binary (*.npy) ;; Numpy text (*.txt)")
        
        if not path[0] == "":
            data_item = self.addDataItem()
            loader = IODataLoad(
                data_item.data_item, 
                path[0])
            shape = loader.previewFromNumpy()
            loader.loadFromNumpy([
                True if not i == len(shape) - 1 
                else False for i in range(len(shape))])

    def addDataProcTxt(self):
        '''
        '''
        path = QtWidgets.QFileDialog.getOpenFileName(
            parent = None, filter = "Text (*.txt)")
        
        if not path[0] == "":
            data_item = self.addDataItem()
            loader = IODataLoad(data_item.data_item, path[0])
            loader.load(path[1].split("(*.")[1].split(")")[0])

    def addDataProcHDF(self):
        '''
        '''

    def contextMenuRequested(self, parent = None):
        """
        This method starts when the context menu is requested. 
        It will generate it on the fly and then return it.
        """
        temp_menu = QtWidgets.QMenu(self._name, parent)

        add_data_raw_txt = temp_menu.addAction("Add from raw text files ...")
        add_data_raw_npy = temp_menu.addAction("Add from npy file ...")
        temp_menu.addSeparator()
        add_data_proc_txt = temp_menu.addAction("Add from processed text file ...")
        add_data_proc_hdf = temp_menu.addAction("Add from processed Hdf5 file ...")
        
        add_data_raw_txt.triggered.connect(self.addDataTxt)
        add_data_raw_npy.triggered.connect(self.addDataNpy)
        add_data_proc_txt.triggered.connect(self.addDataProcTxt)
        add_data_proc_hdf.triggered.connect(self.addDataProcHDF)

        return temp_menu

    def localContextMenuGenerator(self, parent):
        '''
        Set the local context menu just in case
        '''
        self.contextMenuRequested(parent = parent).popup(parent.parent().mapToGlobal(parent.pos()))

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/plus-circle.svg"))
        button_list[0].clicked.connect(
            partial(self.localContextMenuGenerator, button_list[0]))
        button_list[0].setToolTip("Add data")

class DataItem(SessionNode):
    def __init__(self, name = 'Dataset', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "data item"

        self.data_item = DataStructure()
        self.display_widget = DataWidget(self.data_item)
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        if  column == 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column == 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

    def contextMenuRequested(self, parent = None):
        """
        This method starts when the context menu is requested. 
        It will generate it on the fly and then return it.
        """
        temp_menu = QtWidgets.QMenu(self._name, parent)

        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return temp_menu

        change_name  = temp_menu.addAction("Rename")
        show_plot_MDI  = temp_menu.addAction("Show on MDI surface")
        show_plot_Window  = temp_menu.addAction("Show on external window")

        show_plot_MDI.triggered.connect(partial(
            target._playground.displaySubwindow, self))
        show_plot_Window.triggered.connect(partial(
            target.displaySubwindow, self))

        return temp_menu

    def localContextMenuGenerator(self, parent):
        '''
        Set the local context menu just in case
        '''
        self.contextMenuRequested(parent = parent).popup(parent.parent().mapToGlobal(parent.pos()))

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/microsoft-xbox-controller-view.svg"))
        button_list[0].clicked.connect(
            partial(self.localContextMenuGenerator, button_list[0]))
        button_list[0].setToolTip("Show the data")

        button_list[1].setVisible(True)
        button_list[1].setText("")
        button_list[1].setIcon(QtGui.QIcon(":/information.svg"))
        button_list[0].setToolTip("Show the data information")

        button_list[2].setVisible(True)
        button_list[2].setText("")
        button_list[2].setIcon(QtGui.QIcon(":/minus-circle.svg"))
        button_list[0].setToolTip("Remove the data")

class PlotLinkItem(SessionNode):
    def __init__(self, name = 'Plot link', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "plot link item"
        self.data_injector = PlotDataInjector()
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        if  column == 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column == 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

class FitLinkItem(SessionNode):
    def __init__(self, name = 'Fit link', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "fit link item"
        self.data_injector = FitDataInjector()

    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        if  column == 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column == 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

class AnalysisNode(SessionNode):
    def __init__(self, name = 'Analysis', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "analysis"
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def addFitItem(self):
        temp = FitItem(name = 'Fit ' + str(self.childCount()))
        self.model().insertRows(self.childCount(), 1, [temp], self)
        return temp

class FitItem(SessionNode):
    def __init__(self, link_item = None, name = 'Fit item', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "fit item"
        self.handler  = FitHandler(link_item, gui = True)
        self.display_widget = FitWidget(handler = self.handler)
        
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        if  column == 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column == 0: return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        else: return QtCore.Qt.ItemIsEnabled

    def contextMenuRequested(self, parent = None):
        """
        This method starts when the context menu is requested. 
        It will generate it on the fly and then return it.
        """
        temp_menu = QtWidgets.QMenu(self._name, parent)

        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return temp_menu

        change_name  = temp_menu.addAction("Rename")
        show_plot_MDI  = temp_menu.addAction("Show on MDI surface")
        show_plot_Window  = temp_menu.addAction("Show on external window")

        show_plot_MDI.triggered.connect(partial(
            target._playground.displaySubwindow, self))
        show_plot_Window.triggered.connect(partial(
            target.displaySubwindow, self))

        return temp_menu

    def localContextMenuGenerator(self, parent):
        '''
        Set the local context menu just in case
        '''
        self.contextMenuRequested(parent = parent).popup(parent.parent().mapToGlobal(parent.pos()))

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/microsoft-xbox-controller-view.svg"))
        button_list[0].clicked.connect(
            partial(self.localContextMenuGenerator, button_list[0]))
        button_list[0].setToolTip("Show the fit manager")

        button_list[2].setVisible(True)
        button_list[2].setText("")
        button_list[2].setIcon(QtGui.QIcon(":/minus-circle.svg"))
        button_list[0].setToolTip("Remove the fit manager")

class PlotNode(SessionNode):
    def __init__(self, name = 'Plots', parent = None):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "plot"
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        pass
     
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def createPlot(self):
        '''
        Call the plot creator
        '''
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        target._sidebar.addPlot(self)

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/plus-circle.svg"))
        button_list[0].clicked.connect(self.createPlot)
        button_list[0].setToolTip("Add data")

class PlotItem(SessionNode):
    def __init__(self, name = 'Plot', parent = None, **kwargs):
        SessionNode.__init__(self, name, parent)
        self.descriptor = "plot item"
        self.display_widget = QtWidgets.QWidget()
        self.canvas_item = MultiCanvasItem(widget=self.display_widget, **kwargs)

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget._sidebar
        if not target == None: 
            self.canvas_item.add_plot_requested.connect(
                target.launchLinkCreator)
 
    def data(self, column):
        if column == 0: return self._name
 
    def setData(self, column, value):
        if  column == 0: self._name = value
        
    def flags(self, index):
        column = index.column()

        if column == 0: return QtCore.Qt.ItemIsEnabled

        else: return QtCore.Qt.ItemIsEnabled
        
    def contextMenuRequested(self, parent = None):
        """
        This method starts when the context menu is requested. 
        It will generate it on the fly and then return it.
        """
        temp_menu = QtWidgets.QMenu(self._name, parent)

        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: temp_menu

        change_name  = temp_menu.addAction("Rename")
        show_plot_MDI  = temp_menu.addAction("Show on MDI surface")
        show_plot_Window  = temp_menu.addAction("Show on external window")

        show_plot_MDI.triggered.connect(partial(
            target._playground.displaySubwindow, self))
        show_plot_Window.triggered.connect(partial(
            target.displaySubwindow, self))

        return temp_menu

    def localContextMenuGenerator(self, parent):
        '''
        Set the local context menu just in case
        '''
        self.contextMenuRequested(parent = parent).popup(parent.parent().mapToGlobal(parent.pos()))

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/microsoft-xbox-controller-view.svg"))
        button_list[0].clicked.connect(
            partial(self.localContextMenuGenerator, button_list[0]))
        button_list[0].setToolTip("Show the plot")

        button_list[2].setVisible(True)
        button_list[2].setText("")
        button_list[2].setIcon(QtGui.QIcon(":/minus-circle.svg"))
        button_list[0].setToolTip("Remove the plot")
