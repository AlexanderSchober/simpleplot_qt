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

from .scatter_widget_ui import Ui_ScatterWidget
from ..models.modal_items import QColorDialog

class ScatterWidget(Ui_ScatterWidget):
    
    def __init__(self):
    
        Ui_ScatterWidget.__init__(self)
        self.local_widget = QtWidgets.QWidget()
        self.setupUi(self.local_widget)
        self.symbol_combo.addItems(['o','d','s','t'])
        self.color_picker = QColorDialog()

    def link(self, item):
        '''
        Link an item to a widget to manage the 
        signals and values
        '''
        self._current_item = item
        self._setColorButtons()
        self._setInputFields()
        self._connect()

    def unlink(self):
        '''
        Link an item to a widget to manage the 
        signals and values
        '''  
        self._disconnect()

    def _nameChanged(self):
        '''
        Connect to the emition of the 
        signal
        '''
        self._current_item._name = self.name.text()
        self._current_item._model.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex())

    def _connect(self):
        '''
        Connect the methods to the item values
        '''
        self.line_size_input.valueChanged.connect(self._redraw)
        self.symbol_combo.currentIndexChanged.connect(self._redraw)
        self.symbol_size_input.valueChanged.connect(self._redraw)
        self.line_check.stateChanged.connect(self._redraw)
        self.symbol_check.stateChanged.connect(self._redraw)
        self.error_check.stateChanged.connect(self._redraw)
        self.symbol_size_line_input.valueChanged.connect(self._redraw)

        self.line_color_button.clicked.connect(self._setLineColor)
        self.symbol_color_button.clicked.connect(self._setSymbolColor)
        self.symbol_color_button_line.clicked.connect(self._setSymbolLineColor)
        self.error_color_button.clicked.connect(self._setErrorColor)

        self.name.textChanged.connect(self._nameChanged)

    def _disconnect(self):
        '''
        Connect the methods to the item values
        '''
        self.line_size_input.valueChanged.disconnect(self._redraw)
        self.symbol_combo.currentIndexChanged.disconnect(self._redraw)
        self.symbol_size_input.valueChanged.disconnect(self._redraw)
        self.line_check.stateChanged.disconnect(self._redraw)
        self.symbol_check.stateChanged.disconnect(self._redraw)
        self.error_check.stateChanged.disconnect(self._redraw)
        self.symbol_size_line_input.valueChanged.disconnect(self._redraw)

        self.line_color_button.clicked.disconnect(self._setLineColor)
        self.symbol_color_button.clicked.disconnect(self._setSymbolColor)
        self.symbol_color_button_line.clicked.disconnect(self._setSymbolLineColor)
        self.error_color_button.clicked.disconnect(self._setErrorColor)

        self.name.textChanged.disconnect(self._nameChanged)

    def _setColorButtons(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        self.line_color      = self._current_item.parameters['Line color'][0][0]
        self.shadow_color    = self._current_item.parameters['Shadow color'][0][0]
        self.symbol_color    = self._current_item.parameters['Symbol color'][0][0]
        self.symbol_line_color    = self._current_item.parameters['Color'][0][0]
        self.error_color     = self._current_item.parameters['Error color'][0][0]
        
        self.line_color_button.setText(self.line_color.name())
        self.line_color_button.setStyleSheet(
            '''
            #line_color_button{
            background-color: rgb('''+str(self.line_color.getRgb()[0])+","+str(self.line_color.getRgb()[1])+","+str(self.line_color.getRgb()[2])+''');
            border-style: inset;
            border-width: 2px}

            #color_button:pressed{
            border-style: outset;
            border-width: 2px}
            ''')

        self.symbol_color_button.setText(self.symbol_color.name())
        self.symbol_color_button.setStyleSheet(
            '''
            #symbol_color_button{
            background-color: rgb('''+str(self.symbol_color.getRgb()[0])+","+str(self.symbol_color.getRgb()[1])+","+str(self.symbol_color.getRgb()[2])+''');
            border-style: inset;
            border-width: 2px}

            #color_button:pressed{
            border-style: outset;
            border-width: 2px}
            ''')
            
        self.symbol_color_button_line.setText(self.symbol_line_color.name())
        self.symbol_color_button_line.setStyleSheet(
            '''
            #symbol_color_button_line{
            background-color: rgb('''+str(self.symbol_line_color.getRgb()[0])+","+str(self.symbol_line_color.getRgb()[1])+","+str(self.symbol_line_color.getRgb()[2])+''');
            border-style: inset;
            border-width: 2px}

            #color_button:pressed{
            border-style: outset;
            border-width: 2px}
            ''')

        self.error_color_button.setText(self.error_color.name())
        self.error_color_button.setStyleSheet(
            '''
            #error_color_button{
            background-color: rgb('''+str(self.error_color.getRgb()[0])+","+str(self.error_color.getRgb()[1])+","+str(self.error_color.getRgb()[2])+''');
            border-style: inset;
            border-width: 2px}

            #color_button:pressed{
            border-style: outset;
            border-width: 2px}
            ''')

    def _setLineColor(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        self._grabColorPicker(self.line_color_button, 'line_color_button')

    def _setSymbolColor(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        self._grabColorPicker(self.symbol_color_button, 'symbol_color_button')

    def _setSymbolLineColor(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        self._grabColorPicker(self.symbol_color_button_line, 'symbol_color_button_line')

    def _setErrorColor(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        self._grabColorPicker(self.error_color_button, 'error_color_button')

    def _grabColorPicker(self, widget, name):
        '''
        Get the color picker to show up
        in order to select a color
        '''
        self._current_color_widget = widget
        self._current_color_name   = name
        
        self.color_picker.disconnectAll()

        if self._current_color_name == 'line_color_button':
            self.color_picker.setCurrentColor(self.line_color)
        elif self._current_color_name == 'symbol_color_button':
            self.color_picker.setCurrentColor(self.symbol_color)
        elif self._current_color_name == 'symbol_color_button_line':
            self.color_picker.setCurrentColor(self.symbol_line_color)
        elif self._current_color_name == 'error_color_button':
            self.color_picker.setCurrentColor(self.error_color)

        self.color_picker.show()
        self.color_picker.connectMethod(self._updateInternals)

    def _updateInternals(self, color):
        '''
        Update the color selections
        '''
        self._current_color_widget.setText(color.name())
        self._current_color_widget.setStyleSheet(
            '''
            #''' + self._current_color_name +'''{
            background-color: rgb('''+str(color.getRgb()[0])+","+str(color.getRgb()[1])+","+str(color.getRgb()[2])+''');
            border-style: inset;
            border-width: 2px}

            #color_button:pressed{
            border-style: outset;
            border-width: 2px}
            ''')
        if self._current_color_name == 'line_color_button':
            self.line_color = color
        elif self._current_color_name == 'symbol_color_button':
            self.symbol_color = color
        elif self._current_color_name == 'symbol_color_button_line':
            self.symbol_line_color = color
        elif self._current_color_name == 'error_color_button':
            self.error_color = color

        self._redraw()

    def _setInputFields(self):
        '''
        Set the data of the input fields
        present int he widget
        '''
        self.name.setText(self._current_item._name)

        style = self._current_item.parameters['Style'][0]

        if '-' in style:
            self.line_check.setChecked(True)
        else:
            self.line_check.setChecked(False)

        scatter_options = ['o', 'd', 's', 't']
        scatter_bool    = [
            element in scatter_options 
            for element in style]

        if any(scatter_bool):
            self.symbol_check.setChecked(True)
            self.symbol_combo.setCurrentIndex(scatter_bool.index(True))
            self.symbol_size_input.setValue(int(style[-1]))
        else:
            self.symbol_check.setChecked(False)

        self.line_size_input.setValue(self._current_item.parameters['Line thickness'][0][0])
        # self.line_size_input.setValue(self.parameters['Shadow thickness'][0][0])
        self.symbol_size_line_input.setValue(self._current_item.parameters['Symbol thickness'][0][0])
        self.error_size.setValue(self._current_item.parameters['Error thickness'][0][0])

        if self._current_item.parameters['Show error'][0][0]:
            self.error_check.setChecked(True)
        else:
            self.error_check.setChecked(False)

    def _updateValues(self):
        '''
        Pick up the values of all widgets and 
        redraw the item
        '''
        self._current_item.parameters['Line thickness'][0][0] = self.line_size_input.value()
        
        style = []
        if self.line_check.isChecked():
            style.append('-')
        if self.symbol_check.isChecked():
            style.append(self.symbol_combo.currentText())
            style.append(self.symbol_size_input.value())

        self._current_item.parameters['Style'][0] = style
        self._current_item.parameters['Show error'][0][0] = self.error_check.isChecked()
        self._current_item.parameters['Symbol thickness'][0][0] = self.symbol_size_line_input.value()

        self._current_item.parameters['Line color'][0][0]       = self.line_color
        self._current_item.parameters['Shadow color'][0][0]     = self.shadow_color
        self._current_item.parameters['Symbol color'][0][0]     = self.symbol_line_color
        self._current_item.parameters['Color'][0][0]            = self.symbol_color
        self._current_item.parameters['Error color'][0][0]      = self.error_color

    def _redraw(self):
        '''
        redraw the plot item upon update
        '''
        self._updateValues()
        self._current_item.removeItems()
        if self._current_item._mode == '2D':
            self._current_item.draw()
        elif self._current_item._mode == '3D':
            self._current_item.drawGL()
