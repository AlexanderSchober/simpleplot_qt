
from PyQt5 import QtCore,QtGui

from ...pyqtgraph.pyqtgraph.graphicsItems.ScatterPlotItem import drawSymbol
from ...pyqtgraph.pyqtgraph import fn

from ...ploting.plot_items.line_plot     import LinePlot
from ...ploting.plot_items.scatter_plot  import ScatterPlot

class SimpleItemSample():
    '''
    '''
    def __init__(self, items):
        self._items = items
        self._size  = 20

    def setSize(self, size : int):
        '''
        Set the size of the total draw region

        Input
        -------------------
        size : int
            The size of the element

        '''
        self._size = size
        
    def size(self)->int:
        '''
        getter for the size
        '''
        return int(self._size)

    def itemHeight(self)->int:
        '''
        getter for the height parameter
        '''
        return self.size()

    def itemWidth(self)->int:
        '''
        getter for the width parameter
        '''
        return self.size()

    def paint(self, painter : QtGui.QPainter , *args):
        '''
        The painter that will be told where to paint
        '''
        for item in self._items:
            if isinstance(item, LinePlot) and item['Visible']:
                opts    = item.getLegendDictionary()
                painter.setPen(fn.mkPen(opts['pen']))
                painter.drawLine( 2, self._size - 2, self._size - 2, 2 )

            elif isinstance(item, ScatterPlot) and item['Visible']:
                opts    = item.getLegendDictionary()
                pen     = fn.mkPen(opts['symbolPen'])
                brush   = fn.mkBrush(opts['symbolBrush'])
                size    = opts['symbolSize']
                painter.translate(self._size / 2, self._size / 2)
                drawSymbol(painter, opts['symbol'], size, pen, brush)

class SimpleItemText():
    '''
    '''
    def __init__(self, text:str = ' '):
        self._item  = QtGui.QGraphicsTextItem()
        self._item.setZValue(11)

        self._color = QtGui.QColor('k')
        self._opts = {
            'color': QtGui.QColor('k'),
            'justify': 'center'
        }

        self.setText(text)

    def setText(self, text, **kwargs):
        '''
        Set the text of the item

        Input
        ----------------------
        color : str 
            example: 'CCFF00'
        size : str 
            example: '8pt'
        bold : bool
            bold boolean flag
        italic : bool
            italic boolean flag
        
        '''
        self._text = text
        opts = self._opts
        for k in kwargs:
            opts[k] = kwargs[k]
        
        optlist = []
        color = fn.mkColor(self._opts['color'])
        optlist.append('color: #' + fn.colorStr(color)[:6])
        if 'size' in opts:
            optlist.append('font-size: ' + opts['size'])
        if 'bold' in opts and opts['bold'] in [True, False]:
            optlist.append('font-weight: ' + {True:'bold', False:'normal'}[opts['bold']])
        if 'italic' in opts and opts['italic'] in [True, False]:
            optlist.append('font-style: ' + {True:'italic', False:'normal'}[opts['italic']])
        if 'align' in opts and opts['align'] in ['left', 'right', 'center']:
            optlist.append('text-align: ' + opts['align'] )
        full = "<span style='%s'>%s</span>" % ('; '.join(optlist), text)

        self._item.setHtml(full)
        
    def text(self):
        '''
        getter for the size
        '''
        return self._text

    def setSize(self, size:int):
        '''
        Set the size of the item
        '''
        self._opts['size'] = size

    def size(self)->int:
        '''
        get the size
        '''
        return self._opts.get(['size'],None)

    def itemHeight(self)->int:
        '''
        getter for the height parameter
        '''
        return self._item.document().size().height()

    def itemWidth(self)->int:
        '''
        getter for the width parameter
        '''
        return self._item.document().size().width()

    def setParent(self, parent):
        '''
        Set the parent of the item
        '''
        parent.addItem(self._item)
        
    def _itemRect(self):
        '''
        rectangle of the item
        '''
        return self._item.boundingRect()
