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
import os

class FitWidget(QtWidgets.QWidget):
    '''
    '''
    def __init__(self, *args, handler = None,  **kwargs):
        super(FitWidget, self).__init__(*args, **kwargs)

        self._handler = handler

        self._setupLayout()
        self._initialize()
        self._connectMethods()

    def _setupLayout(self):
        '''
        This will build the layout of the current widget 
        by placing the two main components
        '''
        self.setupUi()

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
        self.pushButton = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.label = QtWidgets.QLabel(self.tabWidgetPage1)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.pushButton_4 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(self.tabWidgetPage1)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_4.addWidget(self.listWidget)
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
        self.pushButton.setText(_translate("self.", "<<"))
        self.pushButton_2.setText(_translate("self.", "<"))
        self.label.setText(_translate("self.", "TextLabel"))
        self.pushButton_4.setText(_translate("self.", ">"))
        self.pushButton_5.setText(_translate("self.", ">>"))
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

