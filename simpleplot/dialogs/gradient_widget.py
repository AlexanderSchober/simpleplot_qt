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

from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal


Gradients = {
    'thermal': {'ticks': [(0.3333, QtGui.QColor(185, 0, 0, 255).name()), (0.6666, QtGui.QColor(255, 220, 0, 255).name()), (1, QtGui.QColor(255, 255, 255, 255).name()), (0, QtGui.QColor(0, 0, 0, 255).name())], 'mode': 'rgb'},
    'flame': {'ticks': [(0.2, QtGui.QColor(7, 0, 220, 255).name()), (0.5, QtGui.QColor(236, 0, 134, 255).name()), (0.8, QtGui.QColor(246, 246, 0, 255).name()), (1.0, QtGui.QColor(255, 255, 255, 255).name()), (0.0, QtGui.QColor(0, 0, 0, 255).name())], 'mode': 'rgb'},
    'yellowy': {'ticks': [(0.0, QtGui.QColor(0, 0, 0, 255).name()), (0.2328863796753704, QtGui.QColor(32, 0, 129, 255).name()), (0.8362738179251941, QtGui.QColor(255, 255, 0, 255).name()), (0.5257586450247, QtGui.QColor(115, 15, 255, 255).name()), (1.0, QtGui.QColor(255, 255, 255, 255).name())], 'mode': 'rgb'},
    'bipolar': {'ticks': [(0.0, QtGui.QColor(0, 255, 255, 255).name()), (1.0, QtGui.QColor(255, 255, 0, 255).name()), (0.5, QtGui.QColor(0, 0, 0, 255).name()), (0.25, QtGui.QColor(0, 0, 255, 255).name()), (0.75, QtGui.QColor(255, 0, 0, 255).name())], 'mode': 'rgb'},
    'spectrum': {'ticks': [(1.0, QtGui.QColor(255, 0, 255, 255).name()), (0.0, QtGui.QColor(255, 0, 0, 255).name())], 'mode': 'hsv'},
    'cyclic': {'ticks': [(0.0, QtGui.QColor(255, 0, 4, 255).name()), (1.0, QtGui.QColor(255, 0, 0, 255).name())], 'mode': 'hsv'},
    'greyclip': {'ticks': [(0.0, QtGui.QColor(0, 0, 0, 255).name()), (0.99, QtGui.QColor(255, 255, 255, 255).name()), (1.0, QtGui.QColor(255, 0, 0, 255).name())], 'mode': 'rgb'},
    'grey': {'ticks': [(0.0, QtGui.QColor(0, 0, 0, 255).name()), (1.0, QtGui.QColor(255, 255, 255, 255).name())], 'mode': 'rgb'},

    'viridis': {'ticks': [(0.0, QtGui.QColor(68, 1, 84, 255).name()), (0.25, QtGui.QColor(58, 82, 139, 255).name()), (0.5, QtGui.QColor(32, 144, 140, 255).name()), (0.75, QtGui.QColor(94, 201, 97, 255).name()), (1.0, QtGui.QColor(253, 231, 36, 255).name())], 'mode': 'rgb'},
    'inferno': {'ticks': [(0.0, QtGui.QColor(0, 0, 3, 255).name()), (0.25, QtGui.QColor(87, 15, 109, 255).name()), (0.5, QtGui.QColor(187, 55, 84, 255).name()), (0.75, QtGui.QColor(249, 142, 8, 255).name()), (1.0, QtGui.QColor(252, 254, 164, 255).name())], 'mode': 'rgb'},
    'plasma': {'ticks': [(0.0, QtGui.QColor(12, 7, 134, 255).name()), (0.25, QtGui.QColor(126, 3, 167, 255).name()), (0.5, QtGui.QColor(203, 71, 119, 255).name()), (0.75, QtGui.QColor(248, 149, 64, 255).name()), (1.0, QtGui.QColor(239, 248, 33, 255).name())], 'mode': 'rgb'},
    'magma': {'ticks': [(0.0, QtGui.QColor(0, 0, 3, 255).name()), (0.25, QtGui.QColor(80, 18, 123, 255).name()), (0.5, QtGui.QColor(182, 54, 121, 255).name()), (0.75, QtGui.QColor(251, 136, 97, 255).name()), (1.0, QtGui.QColor(251, 252, 191, 255).name())], 'mode': 'rgb'},
}

class GradientPackage(object):
    '''
    Just a funky package
    '''
    def __init__(self, gradient) -> None:
        
        if isinstance(gradient, GradientPackage):
            self._gradient = gradient.gradientQColor()
        else:
            if len(gradient) > 0 and isinstance(gradient[0][1], list) and  isinstance(gradient[0][1][0], float):
                self._gradient = [(tick, QtGui.QColor.fromRgbF(*color)) for tick, color in gradient]
            elif len(gradient) > 0 and isinstance(gradient[0][1], list) and  isinstance(gradient[0][1][0], int):
                self._gradient = [(tick, QtGui.QColor.fromRgba(*color)) for tick, color in gradient]
            elif len(gradient) > 0 and isinstance(gradient[0][1], str):
                self._gradient = [(tick, QtGui.QColor(color)) for tick, color in gradient]
            else:
                self._gradient = gradient
            
        self._gradient_str =  [(tick, color.name()) for tick, color in self._gradient]
        self._gradient_list_float = [(tick, list(color.getRgbF())) for tick, color in self._gradient]
        self._gradient_list_int = [(tick, list([int(val*256) for val in color.getRgbF()])) for tick, color in self._gradient]
        
    def __setitem__(self, __name: str, __value: QtGui.QColor) -> None:
        self._gradient[__name] = __value
        self._gradient_str =  [(tick, color.name()) for tick, color in self._gradient]
        self._gradient_list_float = [(tick, list(color.getRgbF())) for tick, color in self._gradient]
        self._gradient_list_int = [(tick, list([int(val*256) for val in color.getRgbF()])) for tick, color in self._gradient]
    
    def __len__(self):
        return len(self._gradient)
        
    def insert(self, n, item):
        self._gradient.insert(n, item)
        self._gradient_str =  [(tick, color.name()) for tick, color in self._gradient]
        self._gradient_list_float = [(tick, list(color.getRgbF())) for tick, color in self._gradient]
        self._gradient_list_int = [(tick, list([int(val*256) for val in color.getRgbF()])) for tick, color in self._gradient]

    def gradientQColor(self):
        '''
        Sometimes we need the gradient as list of floats
        '''
        return self._gradient

    def gradientStr(self):
        '''
        Sometimes we need the gradient as list of floats
        '''
        return self._gradient_str
        
    def gradientList(self):
        '''
        Sometimes we need the gradient as list of floats
        '''
        return self._gradient_list_float
        
    def gradientListInt(self):
        '''
        Sometimes we need the gradient as list of floats
        '''
        return self._gradient_list_int
        
class GradientWidget(QtWidgets.QWidget):

    gradient_changed = Signal()
    tick_selected = Signal()

    def __init__(self, gradient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        if gradient:
            self._gradient = GradientPackage(gradient)

        else:
            self._gradient = GradientPackage([
                (0.0, '#000000'),
                (1.0, '#ffffff'),
            ])

        # Stop point handle sizes.
        self._dim = 15
        self._line_width = 1
        self._selected_line_width = 4

        self._drag_position = None
        self.current_handle = None
        
    @property
    def gradient(self):
        return self._gradient
    
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        width = painter.device().width()
        height = painter.device().height()

        colors = [QtGui.QColor('white'), QtGui.QColor('grey')]
        x_idx = 0
        y_idx = 0
        y = 0
        while y < height+0.001:
            
            x = 0
            x_idx = y_idx%2
            while x < width+0.001:
                rect = QtCore.QRect(x, y, self._dim, self._dim)
                painter.fillRect(rect, colors[x_idx%2])
                x += self._dim
                x_idx += 1
            y += self._dim
            y_idx+=1

        # Draw the linear horizontal gradient.
        gradient = QtGui.QLinearGradient(0, 0, width, 0)

        for stop, color in self._gradient.gradientQColor():
            gradient.setColorAt(stop, color)

        rect = QtCore.QRect(0, 0, width, height-self._dim-self._selected_line_width)
        painter.fillRect(rect, gradient)

        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)
        
        # Draw the stop handles.
        for i, (stop, color) in enumerate(self._gradient.gradientQColor()):
            
            if i == self.current_handle:
                pen.setWidth(self._selected_line_width)
                painter.setPen(pen)
            else:
                pen.setWidth(self._line_width)
                painter.setPen(pen)
                
            # Draw the line
            painter.setBrush(color)
            painter.drawLine(stop * width, 0, stop * width, height-self._dim-self._selected_line_width)

            # Draw the triangle
            symbol = QtGui.QPainterPath()
            symbol.moveTo(stop * width - self._dim/2, height-self._dim/2 - self._selected_line_width + self._dim/2)
            symbol.lineTo(stop * width, height-self._dim/2 - self._selected_line_width - self._dim/2)
            symbol.lineTo(stop * width + self._dim/2, height-self._dim/2 - self._selected_line_width + self._dim/2)
            symbol.closeSubpath()
            painter.drawPath(symbol)

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(200, 50)

    def _sort_gradient(self):
        if self.current_handle is not None: 
            info = self._gradient.gradientQColor()[self.current_handle]
        self._gradient = GradientPackage(sorted(self._gradient.gradientQColor(), key=lambda g:g[0]))
        if self.current_handle is not None: 
            self.current_handle = self._gradient.gradientQColor().index(info)
            
    def _constrain_gradient(self):
        self._gradient = GradientPackage([
            # Ensure values within valid range.
            (max(0.0, min(1.0, stop)), color)
            for stop, color in self._gradient.gradientQColor()
        ])

    def setGradient(self, gradient):
        
        self._gradient = GradientPackage(gradient)
        
        self._constrain_gradient()
        self._sort_gradient()
        self.repaint()
        self.gradient_changed.emit()

    def colorPosAtTick(self, n):
        return self._gradient.gradientQColor()[n]

    def setTick(self, info):
        if self.current_handle is None:
            return
        self._gradient[self.current_handle] = info
        self._sort_gradient()
        self.update()

    @property
    def _end_stops(self):
        return [0, len(self._gradient.gradientQColor())-1]

    def addStop(self, stop, color=None):
        # Stop is a value 0...1, find the point to insert this stop
        # in the list.
        assert 0.0 <= stop <= 1.0

        for n, g in enumerate(self._gradient.gradientQColor()):
            if g[0] > stop:
                # Insert before this entry, with specified or next color.
                self._gradient.insert(n, (stop, color or g[1]))
                self.current_handle = n
                self.tick_selected.emit()
                break
        self._constrain_gradient()
        self.gradient_changed.emit()
        self.update()

    def removeStopAtPosition(self, n):
        if n not in self._end_stops:
            items = self._gradient.gradientQColor()
            del items[n]
            self._gradient = GradientPackage(items)
            self.gradient_changed.emit()
            self.update()

    def setColorAtPosition(self, n, color):
        if n < len(self._gradient):
            stop, _ = self._gradient.gradientQColor()[n]
            self._gradient[n] = stop, color
            self.gradient_changed.emit()
            self.update()

    def chooseColorAtPosition(self, n, current_color=None):
        dlg = QtWidgets.QColorDialog(self)
        if current_color:
            dlg.setCurrentColor(QtGui.QColor(current_color))

        if dlg.exec_():
            self.setColorAtPosition(n, dlg.currentColor())

    def _find_stop_handle_for_event(self, e, to_exclude=None):
        width = self.width()
        height = self.height()

        # Are we inside a stop point? First check y.
        if (
            e.y() >=  height-self._dim and
            e.y() <=  height
        ):

            for n, (stop, color) in enumerate(self._gradient.gradientQColor()):

                if (
                    e.x() >= stop * width - self._dim/2 and
                    e.x() <= stop * width + self._dim/2
                ):
                    return n
        return None

    def mousePressEvent(self, e):
        # We're in this stop point.
        if e.button() == Qt.RightButton:
            n = self._find_stop_handle_for_event(e)
            self.current_handle = n
            if n is not None:
                self.tick_selected.emit()
                _, color = self._gradient.gradientQColor()[n]
                self.chooseColorAtPosition(n, color)

        elif e.button() == Qt.LeftButton:
            n = self._find_stop_handle_for_event(e, to_exclude=self._end_stops)
            self.current_handle = n
            
            if n is not None:
                self.tick_selected.emit()
                # Activate drag mode.
                if self._end_stops and n not in self._end_stops:
                    self._drag_position = n
                self.update()

    def mouseReleaseEvent(self, e):
        self._drag_position = None
        self._sort_gradient()

    def mouseMoveEvent(self, e):
        # If drag active, move the stop.
        if self._drag_position:
            stop = e.x() / self.width()
            _, color = self._gradient.gradientQColor()[self._drag_position]
            self._gradient[self._drag_position] = stop, color
            self._constrain_gradient()
            self.tick_selected.emit()
            self.update()

    def mouseDoubleClickEvent(self, e):
        # Calculate the position of the click relative 0..1 to the width.
        n = self._find_stop_handle_for_event(e)
        if n:
            self._sort_gradient() # Ensure ordered.
            # Delete existing, if not at the ends.
            if n > 0 and n < len(self._gradient) - 1:
                self.removeStopAtPosition(n)

        else:
            stop = e.x() / self.width()
            self.addStop(stop)

    def getColorMenue(self, menu):
        
        ## build context menu of gradients
        global Gradients
        for g, ticks in Gradients.items():
            px = QtGui.QPixmap(100, 15)
            p = QtGui.QPainter(px)
            grad = self._getGradient(ticks['ticks'], 100)
            brush = QtGui.QBrush(grad)
            p.fillRect(QtCore.QRect(0, 0, 100, 15), brush)
            p.end()
            label = QtWidgets.QLabel()
            label.setPixmap(px)
            label.setContentsMargins(1, 1, 1, 1)
            labelName = QtWidgets.QLabel(g)
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(labelName)
            hbox.addWidget(label)
            widget = QtWidgets.QWidget()
            widget.setLayout(hbox)
            act = QtWidgets.QWidgetAction(self)
            act.setDefaultWidget(widget)
            act.name = g
            act.triggered.connect(partial(self._setGradientAction, g))
            menu.addAction(act)
        
    def _getGradient(self, ticks, length):
        g = QtGui.QLinearGradient(QtCore.QPointF(0,0), QtCore.QPointF(length,0))
        g.setStops([(x, QtGui.QColor(t)) for x,t in ticks])
        return g
    
    def _setGradientAction(self, gradient_name):
        global Gradients
        self.setGradient([(pos, QtGui.QColor(color)) for pos, color in Gradients[gradient_name]['ticks']])
        