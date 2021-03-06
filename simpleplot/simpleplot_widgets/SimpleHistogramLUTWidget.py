"""
Widget displaying an image histogram along with gradient editor. Can be used to adjust the appearance of images.
This is a wrapper around HistogramLUTItem
"""

from PyQt5 import QtGui, QtCore
from ..pyqtgraph.pyqtgraph.widgets.GraphicsView import GraphicsView
from .SimpleHistogramLUTItem import HistogramLUTItem

__all__ = ['HistogramLUTWidget']


class HistogramLUTWidget(GraphicsView):
    
    def __init__(self, parent=None,  *args, **kargs):
        background = kargs.get('background', 'default')
        GraphicsView.__init__(self, parent, useOpenGL=False, background=background)
        self.item = HistogramLUTItem(*args, **kargs)
        self.setCentralItem(self.item)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.setMinimumWidth(115)
        

    def sizeHint(self):
        return QtCore.QSize(115, 200)
    
    

    def __getattr__(self, attr):
        return getattr(self.item, attr)



