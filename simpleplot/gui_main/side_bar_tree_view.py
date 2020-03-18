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

class SidebarTreeView(QtWidgets.QTreeView):
    '''
    This will be the main playground where the sub-windows
    will be displayed. 
    '''
    def __init__(self, *args, **kwargs):
        super(SidebarTreeView, self).__init__(*args, **kwargs)

        self.setMouseTracking(True)
        
        self._hover_buttons = [
            QtWidgets.QPushButton(self.viewport()),
            QtWidgets.QPushButton(self.viewport()),
            QtWidgets.QPushButton(self.viewport()),
        ]
        self._hideAllHoverButtons()

        self._current_item = None

    def mouseMoveEvent(self, event):
        '''
        override the mouse move event
        '''
        if self.indexAt(event.pos()).row() == -1:
            self._current_item = None
            self._hideAllHoverButtons()
            super().mouseMoveEvent(event)
        else:
            if not self.model().itemAt(self.indexAt(event.pos())) == self._current_item:
                self._hideAllHoverButtons()
                self._current_item = self.model().itemAt(self.indexAt(event.pos()))
                self._processHoverButtons(event)
            super().mouseMoveEvent(event)

    def _processHoverButtons(self, event):
        '''
        Manage the overlay buttons
        '''
        if hasattr(self._current_item, "setHoverButtons"):
            self._current_item.setHoverButtons(self._hover_buttons)
        else:
            return

        rect = self.visualRect(self.indexAt(event.pos()))

        position  = QtCore.QPoint(rect.x()+rect.width(), rect.y())
        for button in self._hover_buttons[::-1]:
            if button.isVisible():
                position = QtCore.QPoint(position.x() - rect.height(), position.y())
                button.setGeometry(position.x(), position.y(), rect.height(), rect.height())

    def _hideAllHoverButtons(self):
        '''
        Hide all the buttons
        '''
        for button in self._hover_buttons:
            button.setVisible(False)
            try: button.disconnect()
            except: pass

        self._current_item = None

    def leaveEvent(self, QEvent):
        '''
        Reimplement the leave event
        '''
        self._hideAllHoverButtons()
        return super().leaveEvent(QEvent)
