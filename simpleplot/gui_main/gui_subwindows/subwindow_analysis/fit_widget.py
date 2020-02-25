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
import os

from ....models.session_node import SessionNode
from ....models.plot_model import PlotModel
from ....models.fit_node import FitNode, FunctionNode
from ....models.delegates import FitDelegate

class FitWidget(QtWidgets.QWidget):
    '''
    '''
    def __init__(self, *args, handler = None,  **kwargs):
        super(FitWidget, self).__init__(*args, **kwargs)

        self._handler = handler
        self._root_node = None
        self._model = None
        self._rays = 1
        self._subplot = None
        self._main_plot = None
        self._sum_plot = None

        self._setupLayout()
        self._initialize()
        self._setFunctionModel()
        self._setNavigator()
        self._populateProjects()
        self._populatePlots()
        self._buildFunctionModel()
        self._connectMethods()

    def _setupLayout(self):
        '''
        This will build the layout of the current widget 
        by placing the two main components
        '''
        self.setupUi()

    def _setNavigator(self):
        '''
        Here we are setting once and for all the navigator
        for the fitting 
        '''
        for i in range(len(self._handler.current_ray)):
            temp_widget = QtWidgets.QWidget()
            temp_layout = QtWidgets.QHBoxLayout(temp_widget)
            temp_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
            
            temp_m  = QtWidgets.QPushButton("-")
            temp_mm = QtWidgets.QPushButton("--")
            temp_p  = QtWidgets.QPushButton("+")
            temp_pp = QtWidgets.QPushButton("++")

            temp_drop = QtWidgets.QComboBox()
            temp_drop.addItems([
                str(e) for e in self._handler._data_link.getVariableAxes()[i]])
            temp_drop.setObjectName("drop_item")

            self._rays *= len(self._handler._data_link.getVariableAxes()[i])
            
            temp_layout.addWidget(temp_mm)
            temp_layout.addWidget(temp_m)
            temp_layout.addWidget(temp_drop)
            temp_layout.addWidget(temp_p)
            temp_layout.addWidget(temp_pp)

            temp_item = QtWidgets.QListWidgetItem()
            temp_item.setSizeHint(temp_widget.sizeHint())
            self._navigator_list.addItem(temp_item)
            self._navigator_list.setItemWidget(temp_item,temp_widget)

            temp_m.clicked.connect(partial(self._move,i,-1))
            temp_mm.clicked.connect(partial(self._move,i,-10))
            temp_p.clicked.connect(partial(self._move,i,1))
            temp_pp.clicked.connect(partial(self._move,i,10))
            temp_drop.currentIndexChanged.connect(self._refreshIndex)
            

    def _move(self, index, amount):
        '''
        
        '''
        placeholder_widget = self._navigator_list.itemWidget(
            self._navigator_list.item(index))
        widget = placeholder_widget.findChild(
            QtWidgets.QComboBox, "drop_item"
        )

        count = widget.count()
        current_idx = widget.currentIndex()
        
        out = 0
        if current_idx + amount >= count:
            out = count -1
        elif current_idx + amount < 0:
            out = 0
        else:
            out = current_idx + amount

        widget.setCurrentIndex(out)

    def _refreshIndex(self):
        '''
        This will read all the elements from the navigator
        and feed them to the fit handler
        '''
        ray = []
        for i in range(self._navigator_list.count()):
            placeholder_widget = self._navigator_list.itemWidget(
                self._navigator_list.item(i))
            widget = placeholder_widget.findChild(
                QtWidgets.QComboBox, "drop_item"
            )
            ray.append(widget.currentIndex())

        self._handler.setCurrentRay(ray)
        if not self._model is None:
            self._model.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

        self._refreshPlots()
        
    def _setFunctionModel(self):
        '''
        This will initialize the model for the 
        functions
        '''
        self._function_model = QtGui.QStandardItemModel()
        self._function_model.setHorizontalHeaderItem(0, QtGui.QStandardItem('Name'))
        self._function_model.setHorizontalHeaderItem(1, QtGui.QStandardItem('Num.'))

        for i,key in enumerate(self._handler.func_dict.keys()):
            self._function_model.setItem(i,0,QtGui.QStandardItem(key))
            num_temp = QtGui.QStandardItem()
            if key == 'Baseline':
                num_temp.setEditable(False)
                num_temp.setData(QtCore.QVariant(1), 0)
            else:   
                num_temp.setData(QtCore.QVariant(0), 0)
            self._function_model.setItem(i,1,num_temp)

        self._function_selection_view.setModel(self._function_model)
        self._function_selection_view.verticalHeader().hide()

    def _populateProjects(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        self._function_selection_project.clear()

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        root_pointer = target._model.root()

        self._projects = []
        for i in range(root_pointer.childCount()):
            if root_pointer.child(i).descriptor == 'project':
                self._projects.append(root_pointer.child(i))

        self._function_selection_project.addItems(
            [item._name for item in self._projects])

        if len(self._projects) > 0:
            self._function_selection_project.setCurrentIndex(0)

        self._populatePlots()

    def _populatePlots(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        self._function_selection_plots.clear()

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        root_pointer = target._model.root()

        self._plots = []
        for i in range(root_pointer.childCount()):
            if root_pointer.child(i).descriptor == 'project' and root_pointer.child(i)._name == self._function_selection_project.currentText():
                plot_root = root_pointer.child(i).childFromName('Plots')
                self._plots = plot_root._children

        self._function_selection_plots.addItems(
            [item._name for item in self._plots])

        if len(self._plots) > 0:
            self._function_selection_plots.setCurrentIndex(0)

        self._populateSubplot()

    def _populateSubplot(self):
        '''
        The data and subplot comboboxes 
        can be populated immediately
        '''
        self._function_selection_subplots.clear()

        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if target == None: return

        if self._function_selection_plots.currentText() == "": 
            self._subplots = []
            return
        
        self._subplots  = [
            item for item in 
            self._plots[self._function_selection_plots.currentIndex()].canvas_item._rootNode._children[:-1]]

        self._function_selection_subplots.addItems(
            [item._name for item in self._subplots])

        if len(self._subplots) > 0:
            self._function_selection_subplots.setCurrentIndex(0)

    def setup(self):
        '''
        set up the models
        '''
        pass

    def setupUi(self):
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_6.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_2.setObjectName("groupBox_2")

        # The part of the selector
        self._function_selection_layout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self._function_selection_view = QtWidgets.QTableView()
        self._function_selection_load = QtWidgets.QPushButton("Load")
        self._function_selection_set = QtWidgets.QPushButton("Set")
        self._function_selection_project = QtWidgets.QComboBox()
        self._function_selection_plots = QtWidgets.QComboBox()
        self._function_selection_subplots = QtWidgets.QComboBox()


        self._function_selection_layout.addWidget(self._function_selection_view)
        temp_layout  = QtWidgets.QVBoxLayout()
        temp_layout.addWidget(QtWidgets.QLabel("Project:"))
        temp_layout.addWidget(self._function_selection_project)
        temp_layout.addWidget(QtWidgets.QLabel("Plot:"))
        temp_layout.addWidget(self._function_selection_plots)
        temp_layout.addWidget(QtWidgets.QLabel("Subplot:"))
        temp_layout.addWidget(self._function_selection_subplots)
        temp_layout.addStretch()
        temp_layout.addWidget(self._function_selection_load)
        temp_layout.addWidget(self._function_selection_set)
        self._function_selection_layout.addLayout(temp_layout)


        self.verticalLayout_7.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_7.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_7.addWidget(self.groupBox_4)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget1 = QtWidgets.QTabWidget(self.tab_3)
        self.tabWidget1.setObjectName("tabWidget1")
        self.tabWidgetPage1 = QtWidgets.QWidget()
        self.tabWidgetPage1.setObjectName("tabWidgetPage1")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tabWidgetPage1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self._navigator_list = QtWidgets.QListWidget(self.tabWidgetPage1)
        self._main_tree_view = QtWidgets.QTreeView(self.tabWidgetPage1)
        self._main_tree_view.setItemDelegate(FitDelegate())
        self._main_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.verticalLayout_4.addWidget(self._navigator_list)
        self.verticalLayout_4.addWidget(self._main_tree_view)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.fit_bar_progress = QtWidgets.QProgressBar(self.tabWidgetPage1)
        self.fit_bar_progress.setProperty("value", 24)
        self.fit_bar_progress.setObjectName("fit_bar_progress")
        self.horizontalLayout_4.addWidget(self.fit_bar_progress)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_9 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout_3.addWidget(self.pushButton_9)
        self.pushButton_10 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_10.setObjectName("pushButton_10")
        self.horizontalLayout_3.addWidget(self.pushButton_10)
        self.fit_button_fit = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.fit_button_fit.setDefault(True)
        self.fit_button_fit.setObjectName("fit_button_fit")
        self.horizontalLayout_3.addWidget(self.fit_button_fit)
        self.pushButton_11 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_11.setObjectName("pushButton_11")
        self.horizontalLayout_3.addWidget(self.pushButton_11)
        self.pushButton_12 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_12.setObjectName("pushButton_12")
        self.horizontalLayout_3.addWidget(self.pushButton_12)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.tabWidget1.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QtWidgets.QWidget()
        self.tabWidgetPage2.setObjectName("tabWidgetPage2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tabWidgetPage2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.listWidget_2 = QtWidgets.QListWidget(self.tabWidgetPage2)
        self.listWidget_2.setObjectName("listWidget_2")
        self.verticalLayout_5.addWidget(self.listWidget_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.pushButton_13 = QtWidgets.QPushButton(self.tabWidgetPage2)
        self.pushButton_13.setDefault(True)
        self.pushButton_13.setObjectName("pushButton_13")
        self.horizontalLayout_5.addWidget(self.pushButton_13)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.tabWidget1.addTab(self.tabWidgetPage2, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget1.addTab(self.tab_4, "")
        self.verticalLayout_2.addWidget(self.tabWidget1)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_5)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_8.addWidget(self.groupBox_5)
        self.tabWidget.addTab(self.tab_5, "")
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(2)
        self.tabWidget1.setCurrentIndex(0)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("fit", "Form"))
        self.groupBox.setTitle(_translate("self", "Data Information"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("self.", "Data"))
        self.groupBox_2.setTitle(_translate("self.", "Initialize Functions"))
        self.groupBox_3.setTitle(_translate("self.", "Load fit from file"))
        self.groupBox_4.setTitle(_translate("self.", "Fit range parameters"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("self", "Set"))

        self.pushButton_9.setText(_translate("self.", "< Fit"))
        self.pushButton_10.setText(_translate("self.", "< Copy"))
        self.fit_button_fit.setText(_translate("self.", "Fit"))
        self.pushButton_11.setText(_translate("self.", "Copy >"))
        self.pushButton_12.setText(_translate("self.", "Fit >"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage1), _translate("self.", "Fit Functions"))
        self.pushButton_13.setText(_translate("self.", "Set"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tabWidgetPage2), _translate("self.", "Function Bounds"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tab_4), _translate("self.", "Edit Fit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("self.", "Fit"))
        self.groupBox_5.setTitle(_translate("self.", "Save Fit Files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("self.", "Save"))

    def _connectMethods(self):
        '''
        Connec the methods to their outs
        '''
        self.fit_button_fit.clicked.connect(self.setFit)
        self._handler.progress_int.connect(self.setProgress)
        self._handler.progress_finished.connect(self._refreshPlots)

        self._function_selection_set.clicked.connect(self._buildFitSetup)
        self._function_selection_project.currentTextChanged.connect(self._populatePlots)
        self._function_selection_plots.currentTextChanged.connect(self._populateSubplot)
        
        target = None
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.__class__.__name__ == "MainWindow":
                target = widget
        if not target == None: 
            target._model.rowsInserted.connect(self._populateProjects)
            target._model.rowsMoved.connect(self._populateProjects)
            target._model.rowsRemoved.connect(self._populateProjects)

    def _initialize(self):
        '''
        This method checks if the data has been set
        in a previous instance.
        '''
        self.fit_bar_progress.setMaximum(100)
        self.fit_bar_progress.setMinimum(0)

    def setFit(self):
        '''
        Tell the system to set up the fit and 
        then run
        '''
        self._handler.performFit()

    def setProgress(self, value):
        self.fit_bar_progress.setValue(value)

    def _buildFitSetup(self):
        '''
        This function will manage the build of the setup of the 
        function model and the setup of the plot outputs in the 
        said model.
        '''
        self._buildFunctionModel()

        if not len(self._subplots) == 0:
            self._removePlots()
            self._subplot = self._subplots[self._function_selection_subplots.currentIndex()]
            self._addPlots()
            self._refreshPlots()
        else:
            return

    def _removePlots(self):
        '''

        '''
        if not self._subplot is None:
            if not self._main_plot is None:
                self._subplot.artist.removePlot(self._main_plot)

            if not self._sum_plot is None:
                self._subplot.artist.removePlot(self._sum_plot)

            for function_node in self._root_node._children:
                for function in function_node._children:
                    function.removePlotItem(self._subplot)

    def _addPlots(self):
        '''

        '''
        self._main_plot =  self._subplot.artist.addPlot(
            'Scatter',
            Name = 'Data',
            Color = 'red',
            Style = ['-'], 
            Log = [False,False]
        )

        self._sum_plot =  self._subplot.artist.addPlot(
            'Scatter',
            Name = 'Fit sum',
            Color = 'black',
            Style = ['-'], 
            Log = [False,False]
        )

        for function_node in self._root_node._children:
            for function in function_node._children:
                function.setPlotItem(self._subplot)

    def _refreshPlots(self):
        '''
        This function is called when the data in the plots should 
        be refreshed and merely serves as bridge
        '''
        self._model.dataChanged.emit(
            QtCore.QModelIndex(), QtCore.QModelIndex()
        )

        if not self._main_plot is None:
            self._main_plot.setData(
                x = self._handler.getDataX(),
                y = self._handler.getDataY()
            )
            
        if not self._sum_plot is None:
            self._sum_plot.setData(
                x = self._handler.getDataX(),
                y = self._handler.getFitSumY()
            )

        for function_node in self._root_node._children:
            for function in function_node._children:
                function.refreshPlot(self._handler.getDataX())


    def _buildFunctionModel(self):
        '''
        This will populate the function model adequately and then 
        display it on the main manager.
        '''
        plot_dict = {}

        col_count = 0
        for i in range(self._function_model.rowCount()):
            if not self._function_model.item(i,0).data(QtCore.Qt.DisplayRole) is None:
                plot_dict[self._function_model.item(i,0).data(QtCore.Qt.DisplayRole)] = self._function_model.item(i,1).data(QtCore.Qt.DisplayRole)
                para_count = self._handler.func_dict[self._function_model.item(i,0).data(QtCore.Qt.DisplayRole)][0].para_num

                if para_count > col_count:
                    col_count = para_count

        if self._root_node is None:
            self._root_node = SessionNode("Root")
        self._model = PlotModel(self._root_node, col_count = 2*col_count + 2)

        idx = 0
        for i,key in enumerate(plot_dict.keys()):
            if self._root_node.childFromName(key) is None and not plot_dict[key] == 0: 
                element = FitNode(name = key, handler = self._handler)
                self._model.insertRows(idx, 1,[element],self._root_node)
                idx += 1

            elif not plot_dict[key] == 0:
                idx += 1
            else:
                continue

            for l in range(self._root_node.childFromName(key).childCount(), plot_dict[key]):
                element = FunctionNode(str(key)+ " "+str(l))
                self._model.insertRows(l, 1, [element],self._root_node.childFromName(key))
                self._handler.addFunction(key, rays = self._rays)

        self._main_tree_view.setModel(self._model)

        self._main_tree_view.header().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        for i in range(2*col_count):
            if i%2==0:
                self._main_tree_view.header().setSectionResizeMode(
                    i+1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents) 
        