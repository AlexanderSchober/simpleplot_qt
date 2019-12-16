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


class SaveDataDialog(QtWidgets.QDialog):
    '''
    This little dialog is intended to 
    chose the save path and then tell 
    the save worker all the right 
    procedures to implement
    '''
    def __init__(self, parent = None):
        super(SaveDataDialog, self).__init__(parent = parent)

        self._path_text = QtWidgets.QLineEdit(self)
        self._path_select = QtWidgets.QPushButton("...", self)
        self._type_select = QtWidgets.QComboBox(self)
        self._accept_btn = QtWidgets.QPushButton("Accept", self)
        self._cancel_btn = QtWidgets.QPushButton("Cancel", self)

        select_layout = QtWidgets.QHBoxLayout()
        select_layout.addWidget(self._path_text)
        select_layout.addWidget(self._path_select)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Select save format:"))
        type_layout.addWidget(self._type_select)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self._cancel_btn)
        btn_layout.addWidget(self._accept_btn)

        _main_layout = QtWidgets.QVBoxLayout(self)
        _main_layout.addLayout(select_layout)
        _main_layout.addLayout(type_layout)
        _main_layout.addLayout(btn_layout)
