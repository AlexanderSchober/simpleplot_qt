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

#import general
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import numpy as np

# The local imports
from simpleplot.canvas.multi_canvas import MultiCanvasItem
from simpleplot.gui_main.main_window import MainWindow
from simpleplot.models.project_node import ProjectNode
from simpleplot.models.project_node import PlotItem
from simpleplot.core.io.io_data_import import IODataLoad
from simpleplot.models.project_node import FitLinkItem, FitItem

def startPlayGround():
    '''
    This is the function which will initiate the example
    '''
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    project_item = ProjectNode(name = "hey")
    window._sidebar._tree_view.model().insertRows(
        0,1,[project_item], 
        window._sidebar._tree_view.model().root())
    
    data_node = project_item.childFromName('Datasets')
    data_item = data_node.addDataItem()
    
    loader = IODataLoad(data_item.data_item, r"/Users/alexanderschober/Desktop/Desktop/example.txt")
    loader.load("txt")

    #Set the fit behaviour
    behavior = [
        ['[ dim_1 ]', 'Variable 0', 0],
        ['Data axis n. 0', 'x', 0]]

    data_link_item  = FitLinkItem()
    data_injector   = data_link_item.data_injector
    data_injector.setDataSource(data_item.data_item)
    data_injector.setBehavior(
        behavior, 
        ['x','Variable 0'])
    new_fit_item    = FitItem(link_item = data_injector) 

    target = None
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.__class__.__name__ == "MainWindow":
            target = widget
    if target == None: return

    target_model = target._model
    target_model.insertRows(
        data_item.childCount(), 1,
        [data_link_item], data_item
    )
    target_model.insertRows(
        project_item.childFromName("Analysis").childCount(), 
        1, [new_fit_item], 
        project_item.childFromName("Analysis")
    )
    
    data_injector.addFitTarget(new_fit_item)

    #set the import
    # import_window = window._sidebar.addDataTxt(target.childFromName("Datasets"))

    # # import_window.io_input_in.setText(r"/Users/alexanderschober/Desktop/DemoRawImport")

    # import_window.io_input_in.setText(r"/home/alexander/Google Drive/Work/2014:2017 Lipp (PhD)/software/R-DATA/Demo/DemoRawImport")
    # import_window.scan_folder_in()

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][0][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(0,0))

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][2][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(2,0))
    # import_window._process_export()
    # import_window.close()

    # import_window = window._sidebar.addDataTxt(target.childFromName("Datasets"))
    # import_window.io_input_in.setText(r"/home/alexander/test")
    # import_window.scan_folder_in()

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][0][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(0,0))

    # import_window.list_dictionary[
    #     "type"].dictionary["items"][3][0].setCheckState(
    #         QtCore.Qt.Unchecked)
    # import_window._dimension_changed(
    #     import_window.list_dictionary['type'].dictionary['model'].index(3,0))
    # import_window._process_export()
    # import_window.close()

    #set the plot
    plot = PlotItem(
        grid = [[True, True], [True, True]], 
        element_types = [["2D","2D"],["2D","3D"]], 
        x_ratios = [1,1],
        y_ratios = [1,1])
    window._sidebar.createPlotItem(project_item.childFromName("Plots"), plot)
    sys.exit(app.exec_())

if __name__ == '__main__':
    startPlayGround()
