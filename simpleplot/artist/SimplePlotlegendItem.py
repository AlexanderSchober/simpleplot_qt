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
#   Alexander Schober <alexander.schober@mac.com>
#
# *****************************************************************************

from PyQt5 import QtWidgets, QtCore, QtGui
from ..pyqtgraph.pyqtgraph import LegendItem, LabelItem
from ..pyqtgraph.pyqtgraph.graphicsItems.LegendItem import ItemSample
from ..pyqtgraph.pyqtgraph import functions as fn

class SimplePlotLegendItem(LegendItem): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    pos_updated = QtCore.pyqtSignal(int,int)

    def __init__(self, size=None, offset=None):
        LegendItem.__init__(self, size=size, offset=offset)
        self.pen_color      = (255,255,255,100)
        self.brush_color    = (100,100,100, 50)
        self.text_color     = (0,0,0,255)
        self.text_width     = 100
        self.text_size      = '8pt'
        self.box_width      = 0
        self.box_height     = 0

    def paint(self, p, *args):
        '''
        overwrite with custom color
        '''
        if not len(self.items) == 0:
            p.setPen(fn.mkPen(*self.pen_color))
            p.setBrush(fn.mkBrush(*self.brush_color))
            p.drawRect(self.boundingRect())

    def setBrush(self, color):
        '''
        set the brush color from outside
        '''
        self.brush_color = color

    def setPen(self, color):
        '''
        set the pen color from outside
        '''
        self.pen_color = color

    def setTextColor(self, color):
        '''
        set the pen color from outside
        '''
        self.text_color = color
        self._refreshText()

    def setTextSize(self, size):
        '''
        set the pen color from outside
        '''
        self.text_size = str(size)+'pt'
        self._refreshText()

    def _refreshText(self):
        '''
        Refresh the text after update
        '''
        for item in self.items:
            item[1].setText(
                item[1].text,
                color = self.text_color,
                size = self.text_size)
        self.updateSize()

    def setTextLength(self, value):
        '''
        set the pen color from outside
        '''
        self.text_width = value
        self.updateSize()

    def setOffset(self, offset):
        '''
        set the new position
        '''
        self.offset = offset
        self.autoAnchor(offset)

    def mouseDragEvent(self, ev):
        '''
        Overwrite and send a signal
        '''
        if ev.button() == QtCore.Qt.LeftButton:
            dpos = ev.pos() - ev.lastPos()
            self.autoAnchor(self.pos() + dpos)
            self.pos_updated.emit((self.pos() + dpos).x(), (self.pos() + dpos).y())

    def updateSize(self):
        '''
        Overwrite base class
        '''
        if self.size is not None:
            return
            
        height = 0
        width = 0
        for sample, label in self.items:
            height += max(sample.height(), label.height()) + 3
            width = max(width, sample.width()+label.width())
            
        self.box_width = max(width, self.text_width) + 20
        self.box_height = height

        self.setGeometry(0, 0,self.box_width, self.box_height)

    def addItem(self, item, name):
        """
        Add a new entry to the legend. 

        ==============  ========================================================
        **Arguments:**
        item            A PlotDataItem from which the line and point style
                        of the item will be determined or an instance of
                        ItemSample (or a subclass), allowing the item display
                        to be customized.
        title           The title to display for this item. Simple HTML allowed.
        ==============  ========================================================
        """
        label = LabelItem(name,color = self.text_color,size = self.text_size, align = 'left')

        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item)
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()

    def removeAllItems(self):
        """
        Removes one item from the legend. 

        ==============  ========================================================
        **Arguments:**
        item            The item to remove or its name.
        ==============  ========================================================
        """
        for sample, label in self.items[::-1]:
            self.items.remove( (sample, label) )    # remove from itemlist
            self.layout.removeItem(sample)          # remove from layout
            sample.close()                          # remove from drawing
            self.layout.removeItem(label)
            label.close()
        # self.updateSize()    

