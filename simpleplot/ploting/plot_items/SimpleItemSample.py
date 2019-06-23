
from PyQt5 import QtCore,QtGui

from ...pyqtgraph.pyqtgraph.graphicsItems.LegendItem import ItemSample
from ...pyqtgraph.pyqtgraph.graphicsItems.ScatterPlotItem import drawSymbol
from ...pyqtgraph.pyqtgraph import fn

from ...ploting.plot_items.line_plot     import LinePlot
from ...ploting.plot_items.scatter_plot  import ScatterPlot
from ...ploting.plot_items.error_plot    import ErrorPlot

class SimpleItemSample(ItemSample):
    """ Class responsible for drawing a single item in a LegendItem (sans label).
    
    This may be subclassed to draw custom graphics in a Legend.
    """
    ## Todo: make this more generic; let each item decide how it should be represented.
    def __init__(self, items):
        ItemSample.__init__(self,items)
    
    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)
        
    def paint(self, p, *args):
        # opts = self.item.opts
        
        # if opts.get('fillLevel',None) is not None and opts.get('fillBrush',None) is not None:
        #     p.setBrush(fn.mkBrush(opts['fillBrush']))
        #     p.setPen(fn.mkPen(None))
        #     p.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(2,18), QtCore.QPointF(18,2), QtCore.QPointF(18,18)]))
        
        for item in self.item:
            if isinstance(item, LinePlot) and item['Visible']:
                opts    = item._getDictionary()
                p.setPen(fn.mkPen(opts['pen']))
                p.drawLine(2, 18, 18, 2)

        for item in self.item:
            if isinstance(item, ScatterPlot) and item['Visible']:
                opts    = item._getDictionary()
                pen     = fn.mkPen(opts['symbolPen'])
                brush   = fn.mkBrush(opts['symbolBrush'])
                size    = opts['symbolSize']
                p.translate(10,10)
                drawSymbol(p, opts['symbol'], size, pen, brush)