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
from ..simpleplot_widgets.SimplePlotGradientEditorItem import GradientEditorItem

class ParameterDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        item    = index.model().getNode(index) 
        editor  = item.createWidget(parent, index)
        return editor

    def setEditorData(self, editor, index):
        item  = index.model().getNode(index) 
        item.setEditorData(editor)

    def setModelData(self, editor, model, index):
        item    = index.model().getNode(index) 
        value   = item.retrieveData(editor)
        model.setData(index, value, QtCore.Qt.EditRole)

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
        elif type(item.data(index.column())) == GradientEditorItem:
            rect    = self.getGradRect(option)
            grad    = item.data(index.column()).getGradient()

            grad.setStart(rect.x(), rect.y())
            grad.setFinalStop(rect.x() + rect.width(), rect.y())

            brush   = QtGui.QBrush(grad)
            painter.fillRect(rect, brush)

        else:
            super().paint(painter, option, index)

    def getGradRect(self, option):
        rect = option.rect
        rect.setWidth(min([rect.width(), 200]))
        return option.rect

    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (
            option.rect.x(), 
            option.rect.y() + option.rect.height() / 2 
            - check_box_rect.height() / 2)

        return QtCore.QRect(check_box_point, check_box_rect.size())

    def sizeHint(self, option, index):
        item    = index.model().getNode(index) 
        size    = super(ParameterDelegate, self).sizeHint(option, index)
        if type(item.data(index.column())) == GradientEditorItem:
            size = super(ParameterDelegate, self).sizeHint(option, index)
            size.setHeight(27)
        return size

if __name__ == '__main__':

    import sys
    from .models import SessionModel
    from .node import SessionNode
    from .parameter_class import ParameterHandler 
    handler = ParameterHandler()
    handler.addParameter('parameter_int', 0)
    # handler.addParameter('parameter_vector',[1,2,3])
    # handler.addParameter('parameter_string','lol')
    # handler.addParameter('parameter_combo','1', choices = ['1','2','3','4'])
    # handler.addParameter('parameter_float',3.3)
    # handler.addParameter('parameter_color',QtGui.QColor('red'))
    # handler.addParameter('parameter_color_1',QtGui.QColor('blue'))
    # handler.addParameter('parameter_font',QtGui.QFont())
    # handler.addParameter('parameter_font_1',QtGui.QFont())


    app = QtWidgets.QApplication(sys.argv)
    root = SessionNode('main')
    root.addChild(handler)
    model = SessionModel(handler)
    tableView = QtWidgets.QTreeView()
    tableView.setModel(model)

    delegate = ParameterDelegate()
    tableView.setItemDelegate(delegate)

    tableView.setWindowTitle("Spin Box Delegate")
    tableView.show()
    sys.exit(app.exec_())