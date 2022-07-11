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

from PyQt5 import QtCore, QtGui, QtWidgets
from simpleplot.dialogs.gradient_dialog import GradientPackage

class ParameterDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        item    = index.model().getNode(index) 
        editor  = item.createWidget(parent, index)
        return editor

    def setEditorData(self, editor, index):
        item  = index.model().getNode(index) 
        item.setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        item    = index.model().getNode(index) 

        if hasattr(item, 'getLive') and not item.getLive():
            value   = item.retrieveData(editor, index)
            model.setData(index, value, QtCore.Qt.EditRole)
        elif not hasattr(item, 'getLive'):
            value   = item.retrieveData(editor,index)
            model.setData(index, value, QtCore.Qt.EditRole)
        else:
            pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        item    = index.model().getNode(index) 
        if type(item.data(index.column())) == bool:
            checked = item.data(index.column())
            check_box_style_option = QtWidgets.QStyleOptionButton()
    
            if checked:
                check_box_style_option.state |= QtWidgets.QStyle.State_On
            else:
                check_box_style_option.state |= QtWidgets.QStyle.State_Off
    
            check_box_style_option.rect = self.getCheckBoxRect(option)
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
            QtWidgets.QApplication.style().drawControl(
                QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)
        elif type(item.data(index.column())) == GradientPackage:
            rect = option.rect
            rect.setWidth(rect.width())

            gradient = QtGui.QLinearGradient(0, 0, rect.width(), 0)
            for stop, color in item.data(index.column()).gradientQColor():
                gradient.setColorAt(stop, color)

            gradient.setStart(rect.x(), rect.y())
            gradient.setFinalStop(rect.x()+rect.width(), rect.y())
            painter.fillRect(rect, gradient)
            
        else:
            super().paint(painter, option, index)

    def getCheckBoxRect(self, option):
        '''
        Get the rectangle for the drawing of the
        checkbox
        '''
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (
            option.rect.x(), 
            option.rect.y() + option.rect.height() / 2 
            - check_box_rect.height() / 2)

        return QtCore.QRect(check_box_point, check_box_rect.size())

    def sizeHint(self, option, index):
        '''
        Process the sizehint and prepare 
        for the gradient issue
        '''
        item    = index.model().getNode(index) 
        size    = super(ParameterDelegate, self).sizeHint(option, index)
        if type(item.data(index.column())) == GradientPackage:
            size = super(ParameterDelegate, self).sizeHint(option, index)
            size.setHeight(27)
        return size


class FitDelegate(QtWidgets.QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        item    = index.model().getNode(index) 
        if isinstance(item.data(index.column()),bool):
            editor = QtWidgets.QCheckBox(parent)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor, index):
        item  = index.model().getNode(index) 
        if isinstance(item.data(index.column()),bool):
            editor.setChecked(not item.data(index.column()))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        item    = index.model().getNode(index) 
        if isinstance(item.data(index.column()),bool):
            model.setData(index, editor.isChecked(), QtCore.Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        item    = index.model().getNode(index) 
        if isinstance(item.data(index.column()),bool):
            checked = item.data(index.column())
            check_box_style_option = QtWidgets.QStyleOptionButton()
    
            if checked:
                check_box_style_option.state |= QtWidgets.QStyle.State_On
            else:
                check_box_style_option.state |= QtWidgets.QStyle.State_Off
    
            check_box_style_option.rect = self.getCheckBoxRect(option)
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
            QtWidgets.QApplication.style().drawControl(
                QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)

        else:
            super().paint(painter, option, index)

    def getCheckBoxRect(self, option):
        '''
        Get the rectangle for the drawing of the
        checkbox
        '''
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (
            option.rect.x(), 
            option.rect.y() + option.rect.height() / 2 
            - check_box_rect.height() / 2)

        return QtCore.QRect(check_box_point, check_box_rect.size())

