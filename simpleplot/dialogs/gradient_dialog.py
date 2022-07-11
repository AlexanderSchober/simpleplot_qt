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
from PyQt5 import QtGui, QtWidgets, QtCore

from .gradient_widget import GradientWidget, GradientPackage


class GradientDialog(QtWidgets.QDialog):
    
    gradientChanged = QtCore.pyqtSignal(GradientPackage)
    
    def __init__(self):
        super().__init__()
        self.initialize()
        self.connect()
        self.setModal(False)
        self.methods = []
        
    def initialize(self):
        self.setWindowTitle("Gradient Editor")
        self._gradient = GradientWidget()
        
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        
        button_box = QtWidgets.QDialogButtonBox(QBtn)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        info_widget = QtWidgets.QWidget()
        self._info_r = QtWidgets.QLineEdit(parent=info_widget)
        self._info_g = QtWidgets.QLineEdit(parent=info_widget)
        self._info_b = QtWidgets.QLineEdit(parent=info_widget)
        self._info_a = QtWidgets.QLineEdit(parent=info_widget)
        self._info_p = QtWidgets.QLineEdit(parent=info_widget)

        info_layout = QtWidgets.QGridLayout(info_widget)
        info_layout.addWidget(QtWidgets.QLabel('Position'), 0,0)
        info_layout.addWidget(self._info_p, 0,1)
        info_layout.addWidget(QtWidgets.QLabel('Color r'), 1,0)
        info_layout.addWidget(self._info_r, 1,1)
        info_layout.addWidget(QtWidgets.QLabel('Color g'), 1,3)
        info_layout.addWidget(self._info_g, 1,4)
        info_layout.addWidget(QtWidgets.QLabel('Color b'), 2,0)
        info_layout.addWidget(self._info_b, 2,1)
        info_layout.addWidget(QtWidgets.QLabel('Color alpha'), 2,3)
        info_layout.addWidget(self._info_a, 2,4)

        self._menu_bar = QtWidgets.QMenuBar(self)
        select = self._menu_bar.addMenu('Select')
        self._select_widget = self._gradient.getColorMenue(select)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self._menu_bar)
        self.layout.addWidget(self._gradient)
        self.layout.addWidget(info_widget)
        self.layout.addWidget(button_box)
        self.setLayout(self.layout)
        
    def connect(self):
        '''
        Connect the widgets
        '''
        self._gradient.tick_selected.connect(self._dispatchGradientTickInfo)
        self._gradient.gradient_changed.connect(self._dispatchGradientTickInfo)
        self._info_p.textChanged.connect(self._manualChange)
        self._info_r.textChanged.connect(self._manualChange)
        self._info_g.textChanged.connect(self._manualChange)
        self._info_a.textChanged.connect(self._manualChange)

    def disconnect(self):
        '''
        Connect the widgets
        '''
        self._gradient.tick_selected.disconnect(self._dispatchGradientTickInfo)
        self._gradient.gradient_changed.disconnect(self._dispatchGradientTickInfo)
        self._info_p.textChanged.disconnect(self._manualChange)
        self._info_r.textChanged.disconnect(self._manualChange)
        self._info_g.textChanged.disconnect(self._manualChange)
        self._info_a.textChanged.disconnect(self._manualChange)

    def _dispatchGradientTickInfo(self):
        if self._gradient.current_handle is not None:
            self.disconnect()
            pos, color = self._gradient.colorPosAtTick(self._gradient.current_handle)
            color = QtGui.QColor(color).getRgbF()
            self._info_p.setText(str(pos))
            self._info_r.setText(str(color[0]))
            self._info_g.setText(str(color[1]))
            self._info_b.setText(str(color[2]))
            self._info_a.setText(str(color[3]))
            self.connect()
        self.gradientChanged.emit(self._gradient.gradient)
            
    def _manualChange(self):
        test_val =  any([
            self._info_r.text() == '',
            self._info_g.text() == '',
            self._info_b.text() == ''
        ])
        
        if test_val:
            return
        
        color = QtGui.QColor.fromRgbF(
            float(self._info_r.text()),
            float(self._info_g.text()),
            float(self._info_b.text()),
            float(self._info_a.text())).name(QtGui.QColor.HexArgb)

        self._gradient.setTick((float(self._info_p.text()), color))
        
    def connectMethod(self, method):
        '''
        '''
        self.methods.append(method)
        self.gradientChanged.connect(self.methods[-1])

    def disconnectAll(self):
        '''
        '''
        for method in self.methods:
            try:
                self.gradientChanged.disconnect(method)
            except:
                print('Could not disconnect', method)
                
    def setCurrentGradient(self, gradient_object): 
        '''
        This will propagate the color from outside
        '''
        self._gradient.setGradient(gradient_object.gradientList())
                
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = GradientDialog()
    widget.show()
    sys.exit(app.exec_())