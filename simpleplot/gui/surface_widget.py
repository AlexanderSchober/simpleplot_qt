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
from ..model.modal_items import QColorDialog

from .surface_widget_ui import Ui_SurfaceWidget
from pyqtgraph import GradientWidget
import numpy as np

class SurfaceWidget(Ui_SurfaceWidget):
    
    name_changed = QtCore.pyqtSignal()

    def __init__(self):
    
        Ui_SurfaceWidget.__init__(self)
        self.local_widget = QtWidgets.QWidget()
        self.setupUi(self.local_widget)
        self.gradient_widget = GradientWidget(orientation = 'bottom')
        self.gradient_layout.addWidget(self.gradient_widget)
        self.color_picker = QColorDialog()

    def link(self, item):
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
        self.gradient_widget.sigGradientChanged.connect(self._updateColors)

        self.position_x.valueChanged.connect(self._updatePosition)
        self.position_y.valueChanged.connect(self._updatePosition)
        self.position_z.valueChanged.connect(self._updatePosition)

        self.scale_x.valueChanged.connect(self._updateScale)
        self.scale_y.valueChanged.connect(self._updateScale)
        self.scale_z.valueChanged.connect(self._updateScale)

        self.rot_x.valueChanged.connect(self._updateRotation)
        self.rot_y.valueChanged.connect(self._updateRotation)
        self.rot_z.valueChanged.connect(self._updateRotation)
        self.axis_x.textChanged.connect(self._updateRotation)
        self.axis_y.textChanged.connect(self._updateRotation)
        self.axis_z.textChanged.connect(self._updateRotation)

        self.surface_check.stateChanged.connect(self._updatePlot)
        self.iso_check.stateChanged.connect(self._updatePlot)
        self.iso_levels.valueChanged.connect(self._updatePlot)
        self.iso_gradient_check.stateChanged.connect(self._updateColors)
        self.iso_width.valueChanged.connect(self._updatePlot)
        self.iso_offset.valueChanged.connect(self._updatePlot)

        self.iso_color.clicked.connect(self._setLineColor)

        self.name.textChanged.connect(self._nameChanged)

    def _disconnect(self):
        '''
        Connect the methods to the item values
        '''
        self.gradient_widget.sigGradientChanged.disconnect(self._updateColors)

        self.position_x.valueChanged.disconnect(self._updatePosition)
        self.position_y.valueChanged.disconnect(self._updatePosition)
        self.position_z.valueChanged.disconnect(self._updatePosition)

        self.scale_x.valueChanged.disconnect(self._updateScale)
        self.scale_y.valueChanged.disconnect(self._updateScale)
        self.scale_z.valueChanged.disconnect(self._updateScale)

        self.rot_x.valueChanged.disconnect(self._updateRotation)
        self.rot_y.valueChanged.disconnect(self._updateRotation)
        self.rot_z.valueChanged.disconnect(self._updateRotation)
        self.axis_x.textChanged.disconnect(self._updateRotation)
        self.axis_y.textChanged.disconnect(self._updateRotation)
        self.axis_z.textChanged.disconnect(self._updateRotation)

        self.surface_check.stateChanged.disconnect(self._updatePlot)
        self.iso_check.stateChanged.disconnect(self._updatePlot)
        self.iso_levels.valueChanged.disconnect(self._updatePlot)
        self.iso_gradient_check.stateChanged.disconnect(self._updateColors)
        self.iso_width.valueChanged.disconnect(self._updatePlot)
        self.iso_offset.valueChanged.disconnect(self._updatePlot)

        self.iso_color.clicked.disconnect(self._setLineColor)

        self.name.textChanged.disconnect(self._nameChanged)

    def _setInputFields(self):
        '''
        Set the data of the input fields
        present int he widget
        '''
        self.name.setText(self._current_item._name)

        self.position_x.setValue(self._current_item._position[0])
        self.position_y.setValue(self._current_item._position[1])
        self.position_z.setValue(self._current_item._position[2])

        self.scale_x.setValue(self._current_item._scale[0])
        self.scale_y.setValue(self._current_item._scale[1])
        self.scale_z.setValue(self._current_item._scale[2])

        self.rot_x.setValue(self._current_item._rotate_angle[0])
        self.rot_y.setValue(self._current_item._rotate_angle[0])
        self.rot_z.setValue(self._current_item._rotate_angle[0])
        self.axis_x.setText(
            str(self._current_item._rotate_axis[0,0]) + ', '
            + str(self._current_item._rotate_axis[0,1]) + ', '
            + str(self._current_item._rotate_axis[0,2]))
        self.axis_y.setText(
            str(self._current_item._rotate_axis[1,0]) + ', '
            + str(self._current_item._rotate_axis[1,1]) + ', '
            + str(self._current_item._rotate_axis[1,2]))
        self.axis_z.setText(
            str(self._current_item._rotate_axis[2,0]) + ', '
            + str(self._current_item._rotate_axis[2,1]) + ', '
            + str(self._current_item._rotate_axis[2,2]))

        self.surface_check.setChecked(self._current_item.parameters['Surface'][0][0])
        self.iso_check.setChecked(self._current_item.parameters['Isocurve'][0][0])
        self.iso_levels.setValue(self._current_item.parameters['Levels'][0][0])
        self.iso_gradient_check.setChecked(self._current_item.parameters['Line color grad'][0][0])
        self.iso_width.setValue(self._current_item.parameters['Line thickness'][0][0])
        self.iso_offset.setValue(self._current_item.parameters['Line offset'][0][0])

    def _setColorButtons(self):
        '''
        Set the color of the input fields
        present int he widget
        '''
        state = {
            'mode':'rgb', 
            'ticks':[
                tuple(
                    [self._current_item.getParameter('Positions')[i], 
                    tuple(np.array((np.array(self._current_item.getParameter('Colors')[i])*255), dtype=np.ubyte).tolist())])
                for i in range(len(self._current_item.getParameter('Positions')))]}
        self.gradient_widget.restoreState(state)

        self.iso_line_color  = self._current_item.parameters['Line color'][0][0]

        self.iso_color.setStyleSheet(
            '''
            #iso_color{
            background-color: rgb('''+str(self.iso_line_color.getRgb()[0])+","+str(self.iso_line_color.getRgb()[1])+","+str(self.iso_line_color.getRgb()[2])+''');
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
        self._grabColorPicker(self.iso_color, 'iso_color')

    def _grabColorPicker(self, widget, name):
        '''
        Get the color picker to show up
        in order to select a color
        '''
        self._current_color_widget = widget
        self._current_color_name   = name
        
        self.color_picker.disconnectAll()

        if self._current_color_name == 'iso_color':
            self.color_picker.setCurrentColor(self.iso_line_color)

        self.color_picker.show()
        self.color_picker.connectMethod(self._updateColors)

    def _updatePlot(self):
        '''
        Tell the plot item to update the colors
        of the surface plot item
        '''
        self._current_item.parameters['Surface'][0][0]           = self.surface_check.isChecked()
        self._current_item.parameters['Isocurve'][0][0]          = self.iso_check.isChecked()
        self._current_item.parameters['Levels'][0][0]            = self.iso_levels.value()
        self._current_item.parameters['Line thickness'][0][0]    = self.iso_width.value()
        self._current_item.parameters['Line offset'][0][0]       = self.iso_offset.value()

        self._current_item.setData()

    def _updateColors(self, color = None):
        '''
        Tell the plot item to update the colors
        of the surface plot item
        '''
        if color == None:
            state = self.gradient_widget.saveState()
            positions = [element[0] for element in state['ticks']]
            colors    = [list(np.array(element[1])/255) for element in state['ticks']]

            colors = [c for _,c in sorted(zip(positions, colors))]
            positions = sorted(positions)

            self._current_item.setColor(colors, positions)
        
        else:
            if isinstance(color, int):
                self._current_item.parameters['Line color grad'][0][0]   = self.iso_gradient_check.isChecked()
                self._current_item.setIsoColor()
            else:
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
                if self._current_color_name == 'iso_color':
                    self.iso_line_color = color

                self._current_item.setIsoColor(color)

    def _updatePosition(self):
        '''
        Tell the plot item to update the positions
        of the surface plot item
        '''
        position = np.array([
            self.position_x.value(),
            self.position_y.value(),
            self.position_z.value()
        ])
        self._current_item.translate(position)

    def _updateScale(self):
        '''
        Tell the plot item to update the positions
        of the surface plot item
        '''
        position = np.array([
            self.scale_x.value(),
            self.scale_y.value(),
            self.scale_z.value()
        ])
        self._current_item.scale(position)

    def _updateRotation(self):
        '''
        Tell the plot item to update the positions
        of the surface plot item
        '''
        try:
            angles = np.array([
                self.rot_x.value(),
                self.rot_y.value(),
                self.rot_z.value()
            ])
            axes = np.array([
                [float(e) for e in self.axis_x.text().split(',')],
                [float(e) for e in self.axis_y.text().split(',')],
                [float(e) for e in self.axis_z.text().split(',')]
            ])
        except:
            return

        self._current_item.rotate(angles, axes)