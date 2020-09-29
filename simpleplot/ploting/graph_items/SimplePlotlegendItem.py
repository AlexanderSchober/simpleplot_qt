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
from ...pyqtgraph.pyqtgraph import LegendItem
from ...pyqtgraph.pyqtgraph import functions as fn

from ...ploting.plot_items.SimpleItemSample  import SimpleItemText
from ...ploting.plot_items.SimpleItemSample  import SimpleItemSample

class SimplePlotLegendItem(QtWidgets.QGraphicsObject): 
    '''
    This is the axis management system. It inherits the parameter
    node as it is a parameter collection.
    '''
    pos_updated = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, size=None, offset=None):
        super().__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setZValue(10)

        self._draw_rectangle = QtCore.QRectF(0,0,50,50)
        self._pos            = QtCore.QPoint(0,0)
        self._last_pos       = None

        self._items          = []
        
        self._pen_color      = (255,255,255,100)
        self._brush_color    = (100,100,100, 50)
        self._text_color     = (0,0,0,255)
        self._text_width     = 0
        self._text_size      = '8pt'
        self._text_justify   = 'left'
        self._anchore_pos    = 'top-left'

        self._auto_width     = True
        self._box_width      = 0
        self._auto_height    = True
        self._box_height     = 0

        #margins left,right,top,bot,between-side,between-top
        self._margins        = [5, 5, 5, 5, 2, 2]

    def _getAnchorPoint(self)->QtCore.QPoint:
        '''
        Retun the anchor point relative to the 
        scene rectangle
        '''
        pos_anchor = None

        view = self.scene().views()[0]
        scene_rect = view.mapToScene(view.viewport().geometry()).boundingRect()

        if self._anchore_pos == 'top-left':
            pos_anchor   = QtCore.QPoint(
                scene_rect.x(),scene_rect.y())
        elif self._anchore_pos == 'top-right':
            pos_anchor   = QtCore.QPoint(
                scene_rect.x()+scene_rect.width(),
                scene_rect.y())
        elif self._anchore_pos == 'bot-left':
            pos_anchor   = QtCore.QPoint(
                scene_rect.x(),
                scene_rect.y()+scene_rect.height())
        elif self._anchore_pos == 'bot-right':
            pos_anchor   = QtCore.QPoint(
                scene_rect.x()+scene_rect.width(),
                scene_rect.y()+scene_rect.height())

        return pos_anchor

    def _getPositionModifier(self)->list:
        '''
        Retun the anchor point relative to the 
        scene rectangle
        '''
        pos_modifier = None

        if self._anchore_pos == 'top-left':
            pos_modifier = [1,1]
        elif self._anchore_pos == 'top-right':
            pos_modifier = [-1,1]
        elif self._anchore_pos == 'bot-left':
            pos_modifier = [1,-1]
        elif self._anchore_pos == 'bot-right':
            pos_modifier = [-1,-1]

        return pos_modifier

    def _getOffsetModifier(self)->QtCore.QPoint:
        '''
        Retun the anchor point relative to the 
        scene rectangle
        '''
        offset_modifier = None

        if self._anchore_pos == 'top-left':
            offset_modifier   = QtCore.QPoint(0,0)
        elif self._anchore_pos == 'top-right':
            offset_modifier   = QtCore.QPoint(self._rect_width,0)
        elif self._anchore_pos == 'bot-left':
            offset_modifier   = QtCore.QPoint(0,self._rect_height)
        elif self._anchore_pos == 'bot-right':
            offset_modifier   = QtCore.QPoint(self._rect_width,self._rect_height)

        return offset_modifier

    def _getRelativePosition(self, pos:QtCore.QPoint)->QtCore.QPoint:
        '''
        converts a point in the relative coordinates
        '''
        pos_anchor = self._getAnchorPoint()
        pos_modifier = self._getPositionModifier()
        offset_modifier = self._getOffsetModifier()
        display_pos = QtCore.QPoint(
            pos_anchor.x() + pos_modifier[0] * (pos.x() + offset_modifier.x()),
            pos_anchor.y() + pos_modifier[1] * (pos.y() + offset_modifier.y())
        )
        return display_pos

    def _getAbsolutePosition(self, pos:QtCore.QPoint)->QtCore.QPoint:
        '''
        converts a point in the relative coordinates
        '''
        pos_anchor = self._getAnchorPoint()
        pos_modifier = self._getPositionModifier()
        offset_modifier = self._getOffsetModifier()
        display_pos = QtCore.QPoint(
            pos_modifier[0] * (pos.x() + offset_modifier.x() - pos_anchor.x()),
            pos_modifier[1] * (pos.y() + offset_modifier.y() - pos_anchor.y())
        )
        return display_pos

    def paint(self, painter, *args):
        '''
        overwrite with custom color
        '''
        if not len(self._items) == 0:
            display_pos = self._getAbsolutePosition(self._pos)

            painter.setPen(fn.mkPen(*self._pen_color))
            painter.setBrush(fn.mkBrush(*self._brush_color))
            painter.drawRect(self._draw_rectangle)

            painter.resetTransform()
            painter.translate(display_pos.x()+self._margins[0], display_pos.y()+self._margins[2])
            for i,items in enumerate(self._items):
                painter.save()
                painter.translate(
                    int((self._widths[0]-items[0].itemWidth())/2),
                    int((self._heights[i]-items[0].itemHeight())/2))
                items[0].paint(painter,*args)
                painter.restore()
                painter.translate(0,self._heights[i]+self._margins[5])

            x = display_pos.x()+self._margins[0]+self._widths[0]+self._margins[4]
            y = display_pos.y()+self._margins[2]
            for i,items in enumerate(self._items):
                y_offset = int((self._heights[i]-items[1].itemHeight())/2)

                if items[1]._opts['justify'] == 'right': 
                    x_offset = int((self._widths[1]-items[1].itemWidth()))
                elif items[1]._opts['justify'] == 'center': 
                    x_offset = int((self._widths[1]-items[1].itemWidth())/2)
                else: 
                    x_offset = 0

                items[1]._item.setPos(
                    x + x_offset, 
                    y + y_offset)
                y += self._heights[i] + self._margins[5] 

    def boundingRect(self):
        '''
        The overriding of the bounding rect for the 
        management of the logic later on
        '''
        return self._draw_rectangle

    def shape(self):
        '''
        Return the shape of the item
        '''
        path = QtGui.QPainterPath()
        path.addRect(self._draw_rectangle)
        return path

    def setBrush(self, color):
        '''
        set the brush color from outside
        '''
        self._brush_color = color

    def setPosition(self, anchor:str, relative_position:list):
        '''
        set the pen color from outside
        '''
        self._anchore_pos = anchor
        self._pos = QtCore.QPoint(relative_position[0], relative_position[1])
        self.updateSize()

    def setPen(self, color):
        '''
        set the pen color from outside
        '''
        self._pen_color = color

    def setTextColor(self, color:str):
        '''
        set the pen color from outside
        '''
        self._text_color = color
        self._refreshText()

    def setMargins(self, margins:list):
        '''
        set the pen color from outside
        '''
        self._margins = margins
        self.updateSize()

    def setTextSize(self, size:float):
        '''
        set the pen color from outside
        '''
        self._text_size = str(size)+'pt'
        self._refreshText()

    def setTextJusitfy(self, justify:str):
        '''
        set the pen color from outside
        '''
        self._text_justify = justify
        self._refreshText()

    def setIconSize(self, size:int):
        '''
        Set the size of the icon
        '''
        for item in self._items:
            item[0].setSize(size)
        self.updateSize()

    def _refreshText(self):
        '''
        Refresh the text after update
        '''
        for item in self._items:
            item[1].setText(
                item[1].text(),
                color = self._text_color,
                size = self._text_size,
                justify = self._text_justify)
        self.updateSize()

    def setTextLength(self, value):
        '''
        set the pen color from outside
        '''
        self.text_width = value
        self.updateSize()

    def mousePressEvent(self, event):
        '''
        Overwrite and send a signal
        '''
        if event.button() == QtCore.Qt.LeftButton:
            self._last_pos = event.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        '''
        Overwrite and send a signal
        '''
        if event.buttons() == QtCore.Qt.LeftButton:
            pos_modifier = self._getPositionModifier()
            diff = event.pos() - self._last_pos
            self._pos += QtCore.QPoint(
                    diff.x()*pos_modifier[0],
                    diff.y()*pos_modifier[1])
            self.updateSize()
            self._last_pos = event.pos()
            self.pos_updated.emit(self._pos)
        event.accept()

    def updateSize(self):
        '''
        Overwrite base class
        '''
        if len(self._items) == 0:
            return

        self.prepareGeometryChange()

        icon_widths     = [sample.itemWidth() for sample, label in self._items]
        icon_heights    = [sample.itemHeight() for sample, label in self._items]
        label_widths    = [label.itemWidth() for sample, label in self._items]
        label_heights   = [label.itemHeight() for sample, label in self._items]

        self._heights   = [max(icon_heights[i], label_heights[i]) for i in range(len(self._items))]
        self._widths    = [max(icon_widths), max(max(label_widths),self._text_width)]

        self._rect_width = (
            sum(self._widths) + (len(self._widths)-1)*self._margins[4]
            +self._margins[0]+self._margins[1])
        self._rect_height = (
            sum(self._heights) + (len(self._heights)-1)*self._margins[5]
            +self._margins[2]+self._margins[3])

        display_pos = self._getAbsolutePosition(self._pos)
        self._draw_rectangle = QtCore.QRectF(
            display_pos.x(),display_pos.y(),
            self._rect_width,self._rect_height)

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
        label = SimpleItemText(text = name)
        label.setParent(self.scene())

        if isinstance(item, SimpleItemSample):
            sample = item
        else:
            sample = SimpleItemSample(item)
            
        self._items.append((sample, label))
        self._refreshText()

    def removeAllItems(self):
        """
        Removes one item from the legend. 

        ==============  ========================================================
        **Arguments:**
        item            The item to remove or its name.
        ==============  ========================================================
        """
        for sample, label in self._items[::-1]:
            self.scene().removeItem(label._item)
            self._items.remove( (sample, label) )    # remove from itemlist
            # self.layout.removeItem(sample)          # remove from layout
            # sample.close()                          # remove from drawing
            # self.layout.removeItem(label)
            # label.close() 
