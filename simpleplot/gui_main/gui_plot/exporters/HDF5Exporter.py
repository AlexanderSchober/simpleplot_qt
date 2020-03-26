from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np

from ....pyqtgraph.pyqtgraph.Qt import QtGui, QtCore, QtSvg, QT_LIB
from ....pyqtgraph.pyqtgraph import functions as fn
from ....pyqtgraph.pyqtgraph.parametertree.Parameter import Parameter

from ....simpleplot_widgets.SimplePlotItem import SimplePlotItem as PlotItem

from .Exporter import Exporter

try:
    import h5py
    HAVE_HDF5 = True
except ImportError:
    HAVE_HDF5 = False
    
__all__ = ['HDF5Exporter']

    
class HDF5Exporter(Exporter):
    Name = "HDF5 Export: plot (x,y)"
    windows = []
    allowCopy = False

    def __init__(self, item, canvas_type):
        Exporter.__init__(self, item)

        self.canvas_type = canvas_type
        if self.canvas_type == '2D':
            self.params = Parameter(name='params', type='group', children=[
                {'name': 'Name', 'type': 'str', 'value': 'Export',},
                {'name': 'columnMode', 'type': 'list', 'values': ['(x,y) per plot', '(x,y,y,y) for all plots']},
            ])
        elif self.canvas_type == '3D':
            self.params = Parameter(name='params', type='group', children=[
                {'name': 'Name', 'type': 'str', 'value': 'Export',},
                {'name': 'columnMode', 'type': 'list', 'values': ['(x,y) per plot', '(x,y,y,y) for all plots']},
            ])

    def parameters(self):
        return self.params
    
    def export(self,canvas_item, fileName=None):
        if not HAVE_HDF5:
            raise RuntimeError("This exporter requires the h5py package, "
                               "but it was not importable.")
        
        if not isinstance(self.item, PlotItem):
            raise Exception("Must have a PlotItem selected for HDF5 export.")
        
        if fileName is None:
            self.fileSaveDialog(canvas_item, filter=["*.h5", "*.hdf", "*.hd5"])
            return
        dsname = self.params['Name']
        fd = h5py.File(fileName, 'a') # forces append to file... 'w' doesn't seem to "delete/overwrite"
        data = []

        appendAllX = self.params['columnMode'] == '(x,y) per plot'
        #print dir(self.item.curves[0])
        tlen = 0
        for i, c in enumerate(self.item.curves):
            d = c.getData()
            if i > 0 and len(d[0]) != tlen:
                raise ValueError ("HDF5 Export requires all curves in plot to have same length")
            if appendAllX or i == 0:
                data.append(d[0])
                tlen = len(d[0])
            data.append(d[1])


        fdata = numpy.array(data).astype('double')
        dset = fd.create_dataset(dsname, data=fdata)
        fd.close()

if HAVE_HDF5:
    HDF5Exporter.register()
