
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
from ..pyqtgraph.pyqtgraph.graphicsItems.PlotItem import *
from ..pyqtgraph.pyqtgraph.WidgetGroup import WidgetGroup

#private dependencies
from .plotConfigTemplate import *

class SimplePlotItem(PlotItem):

    def __init__(self, canvas, parent = None):
        PlotItem.__init__(self)
        self.canvas     = canvas
        self.parentSubstitute  = parent
        self._overwriteCtrlMenu()
        self.disableAutoRange()
        self.hideButtons()
        
    def _overwriteCtrlMenu(self):
        '''
        Overwrites the custom provided menu by the 
        pyqtgraph library and adds a small specific
        touch to implement simpleplot particularities
        '''
        w = QtGui.QWidget()
        self.ctrl = c = Ui_Form()
        c.setupUi(w)
        dv = QtGui.QDoubleValidator(self)

        menuItems = [
            ('Transforms', c.transformGroup),
            ('Downsample', c.decimateGroup),
            ('Average', c.averageGroup),
            ('Alpha', c.alphaGroup),
            ('Grid', c.gridGroup),
            ('Points', c.pointsGroup),
        ]

        self.ctrlMenu = QtGui.QMenu()
        
        self.ctrlMenu.setTitle('Plot Options')
        self.subMenus = []
        for name, grp in menuItems:
            sm = QtGui.QMenu(name)
            act = QtGui.QWidgetAction(self)
            act.setDefaultWidget(grp)
            sm.addAction(act)
            self.subMenus.append(sm)
            self.ctrlMenu.addMenu(sm)
        
        self.stateGroup = WidgetGroup()
        for name, w in menuItems:
            self.stateGroup.autoAdd(w)
        
        self.fileDialog = None

        c.alphaGroup.toggled.connect(self.updateAlpha)
        c.alphaSlider.valueChanged.connect(self.updateAlpha)
        c.autoAlphaCheck.toggled.connect(self.updateAlpha)

        c.xGridCheck.toggled.connect(self.updateGrid)
        c.yGridCheck.toggled.connect(self.updateGrid)
        c.gridAlphaSlider.valueChanged.connect(self.updateGrid)

        c.fftCheck.toggled.connect(self.updateSpectrumMode)
        c.logXCheck.toggled.connect(self._updateLogModeproxy)
        c.logYCheck.toggled.connect(self._updateLogModeproxy)

        c.downsampleSpin.valueChanged.connect(self.updateDownsampling)
        c.downsampleCheck.toggled.connect(self.updateDownsampling)
        c.autoDownsampleCheck.toggled.connect(self.updateDownsampling)
        c.subsampleRadio.toggled.connect(self.updateDownsampling)
        c.meanRadio.toggled.connect(self.updateDownsampling)
        c.clipToViewCheck.toggled.connect(self.updateDownsampling)

        self.ctrl.avgParamList.itemClicked.connect(self.avgParamListClicked)
        self.ctrl.averageGroup.toggled.connect(self.avgToggled)
        
        self.ctrl.maxTracesCheck.toggled.connect(self.updateDecimation)
        self.ctrl.maxTracesSpin.valueChanged.connect(self.updateDecimation)

    def _updateLogModeproxy(self):
        '''
        Set the logarythmic mode
        '''
        self.canvas.artist.axes.general_handler.items['Log'].updateValue(
            [self.ctrl.logXCheck.isChecked(),self.ctrl.logYCheck.isChecked()],
            method = False)
        self.updateLogMode()

    def updateLogMode(self):
        '''
        Update the log mode
        '''
        x = self.ctrl.logXCheck.isChecked()
        y = self.ctrl.logYCheck.isChecked()
        for i in self.items:
            if hasattr(i, 'setLogMode'):
                i.setLogMode(x,y)
        self.getAxis('bottom').setLogMode(x)
        self.getAxis('top').setLogMode(x)
        self.getAxis('left').setLogMode(y)
        self.getAxis('right').setLogMode(y)
        self.canvas.artist.zoomer.zoom()
        self.recomputeAverages()

    def updateSpectrumMode(self, b=None):
        if b is None:
            b = self.ctrl.fftCheck.isChecked()
        for c in self.curves:
            c.setFftMode(b)
        self.canvas.artist.zoomer.zoom()
        self.recomputeAverages()

    def mouseMoveEvent(self, ev):
        if self.lastMousePos is None:
            self.lastMousePos = Point(ev.pos())
        delta = Point(ev.pos() - QtCore.QPoint(*self.lastMousePos))
        self.lastMousePos = Point(ev.pos())

        QtGui.QGraphicsView.mouseMoveEvent(self, ev)
        
        if not self.mouseEnabled:
            return
        self.sigSceneMouseMoved.emit(self.mapToScene(ev.pos()))
            
        if self.clickAccepted:  ## Ignore event if an item in the scene has already claimed it.
            return
        
        if ev.buttons() == QtCore.Qt.RightButton:
            delta = Point(np.clip(delta[0], -50, 50), np.clip(-delta[1], -50, 50))
            scale = 1.01 ** delta
            self.scale(scale[0], scale[1], center=self.mapToScene(self.mousePressPos))
            self.sigDeviceRangeChanged.emit(self, self.range)

        elif ev.buttons() in [QtCore.Qt.MidButton, QtCore.Qt.LeftButton]:  ## Allow panning by left or mid button.
            px = self.pixelSize()
            tr = -delta * px
            
            self.translate(tr[0], tr[1])
            self.sigDeviceRangeChanged.emit(self, self.range)
