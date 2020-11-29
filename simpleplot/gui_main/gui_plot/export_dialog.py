
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
from . import exporters as exporters
from ...pyqtgraph.pyqtgraph import functions as fn
from ...pyqtgraph.pyqtgraph.graphicsItems.ViewBox import ViewBox
from ...simpleplot_widgets.SimplePlotItem import SimplePlotItem as PlotItem
from . import exportDialogTemplate_ui as exportDialogTemplate

class ExportDialog(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Export")
        self.currentExporter = None
            
        self.selectBox = QtGui.QGraphicsRectItem()
        self.selectBox.setPen(fn.mkPen('y', width=3, style=QtCore.Qt.DashLine))
        self.selectBox.hide()
        
        self.ui = exportDialogTemplate.Ui_Form()
        self.ui.setupUi(self)
        self.ui.exportBtn.clicked.connect(self.exportClicked)
        self.ui.copyBtn.clicked.connect(self.copyClicked)
        self.ui.itemTree.currentItemChanged.connect(self.exportItemChanged)
        self.ui.formatList.currentItemChanged.connect(self.exportFormatChanged)

        self.ui.closeBtn.hide()
        
    def refreshSubplot(self,item):
        if not hasattr(item, 'handler'):
            return
        # if item.handler['Type'] == '2D':
        #     self.current_type = '2D'
        #     self.canvas_item = item
        #     self.scene = item.plot_widget
        #     scene_item = self.scene
        #
        #     if scene_item is not None:
        #         ## Select next exportable parent of the item originally clicked on
        #         while not isinstance(scene_item, ViewBox) and not isinstance(scene_item, PlotItem) and scene_item is not None:
        #             scene_item = scene_item.parentItem()
        #         ## if this is a ViewBox inside a PlotItem, select the parent instead.
        #         if isinstance(scene_item, ViewBox) and isinstance(scene_item.parentItem(), PlotItem):
        #             scene_item = scene_item.parentItem()
        #         self.updateItemList(select=scene_item)
        #
        #     # self.scene.addItem(self.selectBox)
        #     # self.selectBox.setVisible(True)
        #
        # elif item.handler['Type'] == '3D':
        #     self.current_type = '3D'
        #     self.canvas_item = item
        #     self.scene = item.view
        #     # self.updateItemList(select=self.scene)

    def updateItemList(self, select=None):
        self.ui.itemTree.clear()
        si = QtGui.QTreeWidgetItem(["Entire Scene"])
        si.gitem = self.scene
        self.ui.itemTree.addTopLevelItem(si)
        self.ui.itemTree.setCurrentItem(si)
        si.setExpanded(True)
        for child in self.scene.items():
            if child.parentItem() is None:
                self.updateItemTree(child, si, select=select)
                
    def updateItemTree(self, item, treeItem, select=None):
        si = None
        if isinstance(item, ViewBox):
            si = QtGui.QTreeWidgetItem(['ViewBox'])
        elif isinstance(item, PlotItem):
            si = QtGui.QTreeWidgetItem(['Plot'])
            
        if si is not None:
            si.gitem = item
            treeItem.addChild(si)
            treeItem = si
            if si.gitem is select:
                self.ui.itemTree.setCurrentItem(si)
            
        for ch in item.childItems():
            self.updateItemTree(ch, treeItem, select=select)
            
    def exportItemChanged(self, item, prev):
        if item is None:
            return
        if item.gitem is self.scene and self.current_type == '2D':
            newBounds = self.canvas_item.view.viewRect()
            # self.selectBox.setRect(newBounds)
        elif self.current_type == '2D':
            newBounds = item.gitem.sceneBoundingRect()
            # self.selectBox.setRect(newBounds)
        # self.selectBox.show()
        self.updateFormatList()
        
    def updateFormatList(self):
        current = self.ui.formatList.currentItem()
        if current is not None:
            current = str(current.text())
        self.ui.formatList.clear()
        self.exporterClasses = {}
        gotCurrent = False
        for exp in exporters.listExporters():
            self.ui.formatList.addItem(exp.Name)
            self.exporterClasses[exp.Name] = exp
            if exp.Name == current:
                self.ui.formatList.setCurrentRow(self.ui.formatList.count()-1)
                gotCurrent = True
                
        if not gotCurrent:
            self.ui.formatList.setCurrentRow(0)
        
    def exportFormatChanged(self, item, prev):
        if item is None:
            self.currentExporter = None
            self.ui.paramTree.clear()
            return
        expClass = self.exporterClasses[str(item.text())]
        exp = expClass(self.ui.itemTree.currentItem().gitem, self.current_type)
        params = exp.parameters()
        if params is None:
            self.ui.paramTree.clear()
        else:
            self.ui.paramTree.setParameters(params)
        self.currentExporter = exp
        self.ui.copyBtn.setEnabled(exp.allowCopy)
        
    def exportClicked(self):
        # self.selectBox.hide()
        self.currentExporter.export(self.canvas_item)
        
    def copyClicked(self):
        # self.selectBox.hide()
        self.currentExporter.export(copy=True)