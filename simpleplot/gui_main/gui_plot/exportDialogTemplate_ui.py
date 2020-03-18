# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'exportDialogTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from ...pyqtgraph.pyqtgraph.parametertree import ParameterTree

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(604, 1047)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.paramTree = ParameterTree(Form)
        self.paramTree.setObjectName("paramTree")
        self.paramTree.headerItem().setText(0, "1")
        self.paramTree.header().setVisible(False)
        self.gridLayout.addWidget(self.paramTree, 7, 1, 1, 3)
        self.formatList = QtWidgets.QListWidget(Form)
        self.formatList.setObjectName("formatList")
        self.gridLayout.addWidget(self.formatList, 5, 1, 1, 3)
        self.closeBtn = QtWidgets.QPushButton(Form)
        self.closeBtn.setObjectName("closeBtn")
        self.gridLayout.addWidget(self.closeBtn, 8, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 6, 1, 1, 3)
        self.copyBtn = QtWidgets.QPushButton(Form)
        self.copyBtn.setObjectName("copyBtn")
        self.gridLayout.addWidget(self.copyBtn, 8, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 1, 1, 3)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 1, 1, 3)
        self.itemTree = QtWidgets.QTreeWidget(Form)
        self.itemTree.setObjectName("itemTree")
        self.itemTree.headerItem().setText(0, "1")
        self.itemTree.header().setVisible(False)
        self.gridLayout.addWidget(self.itemTree, 3, 1, 1, 3)
        self.exportBtn = QtWidgets.QPushButton(Form)
        self.exportBtn.setObjectName("exportBtn")
        self.gridLayout.addWidget(self.exportBtn, 8, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 1, 1, 1)
        self.expSubplot = QtWidgets.QComboBox(Form)
        self.expSubplot.setObjectName("expSubplot")
        self.gridLayout.addWidget(self.expSubplot, 1, 2, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Export"))
        self.closeBtn.setText(_translate("Form", "Close"))
        self.label_3.setText(_translate("Form", "Export options"))
        self.copyBtn.setText(_translate("Form", "Copy"))
        self.label_2.setText(_translate("Form", "Export format"))
        self.label.setText(_translate("Form", "Item to export:"))
        self.exportBtn.setText(_translate("Form", "Export"))
        self.label_4.setText(_translate("Form", "Subplot"))


