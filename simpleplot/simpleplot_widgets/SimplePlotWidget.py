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

#public dependencies
from PyQt5 import QtWidgets, QtGui, QtCore
from .SimplePlotItem import SimplePlotItem
from ..pyqtgraph.pyqtgraph import PlotWidget
from ..pyqtgraph.pyqtgraph.WidgetGroup import WidgetGroup

#private dependencies
from .plotConfigTemplate import *

class SimplePlotWidget(PlotWidget):
    resized_signal = QtCore.pyqtSignal()

    def __init__(self, canvas):
        PlotWidget.__init__(self)

        self._setCtrlMenu()
        self._menuEnabled = True

        self.plotItem.sigRangeChanged.disconnect(self.viewRangeChanged)
        self.plotItem = SimplePlotItem(canvas, parent = self)
        self.setCentralItem(self.plotItem)
        ## Explicitly wrap methods from plotItem
        ## NOTE: If you change this list, update the documentation above as well.
        for m in ['addItem', 'removeItem', 'autoRange', 'clear', 'setXRange', 
                  'setYRange', 'setRange', 'setAspectLocked', 'setMouseEnabled', 
                  'setXLink', 'setYLink', 'enableAutoRange', 'disableAutoRange', 
                  'setLimits', 'register', 'unregister', 'viewRect']:
            setattr(self, m, getattr(self.plotItem, m))
        #QtCore.QObject.connect(self.plotItem, QtCore.SIGNAL('viewChanged'), self.viewChanged)
        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)
        self.setAntialiasing(True)
        self.canvas = canvas

        self.sceneObj.contextMenu[0].triggered.disconnect(self.sceneObj.showExportDialog)
        self.sceneObj.contextMenu[0].triggered.connect(self._showExportDialog)
        self.plotItem.getViewBox().mouseDragEvent = self.mouseDragEvent
        self.plotItem.getViewBox().sigStateChanged.connect(self.resized_signal.emit)
        
    def mouseMoveEvent(self, ev):
        '''
        mouse move event
        '''
        self.canvas.mouseMove(ev)
        super().mouseMoveEvent(ev)

    def mousePressEvent(self, ev):
        '''
        mouse press event
        '''
        self.canvas.mousePress(ev)
        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        '''
        mouse release event
        '''
        self.canvas.mouseRelease(ev)
        super().mouseReleaseEvent(ev)

    def mouseDragEvent(self, ev):
        '''
        mouse release event
        '''
        self.canvas.mouseDrag(ev)
        # super(PlotWidget, self).mouseReleaseEvent(ev)

    def _setCtrlMenu(self):
        '''
        Overwrites the custom provided menu by the 
        pyqtgraph library and adds a small specific
        touch to implement simpleplot particularities
        '''
        w = QtGui.QWidget()
        self.ctrl = c = Ui_Form()
        c.setupUi(w)
        dv = QtGui.QDoubleValidator(self)

        self.ctrlMenu = QtGui.QMenu()

        self.ctrlMenu.setTitle('Layout')
        act = QtGui.QWidgetAction(self)
        act.setDefaultWidget(c.layoutGroup)
        self.ctrlMenu.addAction(act)

        c.maximizeRadio.stateChanged.connect(self.maximize)

    def _showExportDialog(self):
        self.canvas.multi_canvas.bottom_selector.openSettings(
            mode = 'Save', target = self.canvas._name)

    def maximize(self):
        '''
        Update the state of the plot depending on the
        current state
        '''
        if self.ctrl.maximizeRadio.isChecked():
            self.canvas.multi_canvas.handler['Select'] = self.canvas._name
        else:
            self.canvas.multi_canvas.handler['Select'] = 'All'       

    def getContextMenus(self, event):
        ## called when another item is displaying its context menu; we get to add extras to the end of the menu.
        if self._menuEnabled:
            return self.ctrlMenu
        else:
            return None
        
    def menuEnabled(self):
        return self._menuEnabled

    def getMenu(self):
        return self.ctrlMenu

    def setMenuEnabled(self, enableMenu=True):
        """
        Enable or disable the context menu for this PlotItem.
        """
        self._menuEnabled = enableMenu

    def resizeEvent(self, ev):
        # self.resized_signal.emit()
        return super().resizeEvent(ev)
