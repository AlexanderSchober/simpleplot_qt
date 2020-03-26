from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np

from ....pyqtgraph.pyqtgraph.Qt import QtGui, QtCore, QtSvg, QT_LIB
from ....pyqtgraph.pyqtgraph import functions as fn
from ....pyqtgraph.pyqtgraph.parametertree.Parameter import Parameter

from ....simpleplot_widgets.SimplePlotItem import SimplePlotItem as PlotItem

from .Exporter import Exporter

__all__ = ['CSVExporter']
    
    
class CSVExporter(Exporter):
    Name = "CSV from curves"
    windows = []
    def __init__(self, item, canvas_type):
        Exporter.__init__(self, item)

        self.canvas_type = canvas_type

        self.params = Parameter(name='params', type='group', children=[
            {'name': 'separator', 'type': 'list', 'value': 'comma', 'values': ['comma', 'tab']},
            {'name': 'precision', 'type': 'int', 'value': 10, 'limits': [0, None]},
            {'name': 'columnMode', 'type': 'list', 'values': ['(x,y) per plot', '(x,y,y,y) for all plots', '(x,y,e) per plot', '(x,y,e,y,e,y,e) for all plots']}
        ])
        
    def parameters(self):
        return self.params
    
    def export(self,canvas_item, fileName=None):

        if fileName is None:
            self.fileSaveDialog(canvas_item,filter=["*.csv", "*.tsv"])
            return

        if canvas_item._plot_root.childFromName("Scatter") == None: 
            return
        else:
            scatter_items = canvas_item._plot_root.childFromName("Scatter")._children

        data = []
        error = []
        names = []
        append_all_x = (
            self.params['columnMode'] == '(x,y) per plot'
            or self.params['columnMode'] == '(x,y,e) per plot')
        append_errors = (
            self.params['columnMode'] == '(x,y,e) per plot'
            or self.params['columnMode'] == '(x,y,e,y,e,y,e) for all plots'
        )
        header = []

        for i,scatter_item in enumerate(scatter_items):
            data.append(scatter_item['Data'].getData())
            names.append(" ".join(scatter_item._name.split(',')))

            if i == 0 or append_all_x:
                temp_header = [
                    names[-1] + " (x)",
                    names[-1] + " (y)"]
            else:
                temp_header = [
                    names[-1] + " (y)"]
            temp_error = []
            if append_errors and not scatter_item['Data'].getError() is None:
                get_error = scatter_item['Data'].getError()
                if 'width' in get_error.keys() and not get_error['width'] is None:
                    temp_header.append(names[-1] + " (ex)")
                    if isinstance(get_error['width'], list) or isinstance(get_error['width'], np.ndarray):
                        temp_error.append(get_error['width'])
                    else:
                        temp_error.append([get_error['width'] for e in data[-1][0]])
                if 'right' in get_error.keys() and not get_error['right'] is None:
                    temp_header.append(names[-1] + " (ex+)")
                    if isinstance(get_error['right'], list) or isinstance(get_error['right'], np.ndarray):
                        temp_error.append(get_error['right'])
                    else:
                        temp_error.append([get_error['right'] for e in data[-1][0]])
                if 'left' in get_error.keys() and not get_error['left'] is None:
                    temp_header.append(names[-1] + " (ex-)")
                    if isinstance(get_error['left'], list) or isinstance(get_error['left'], np.ndarray):
                        temp_error.append(get_error['left'])
                    else:
                        temp_error.append([get_error['left'] for e in data[-1][0]])
                if 'height' in get_error.keys() and not get_error['height'] is None:
                    temp_header.append(names[-1] + " (ey)")
                    if isinstance(get_error['height'], list) or isinstance(get_error['height'], np.ndarray):
                        temp_error.append(get_error['height'])
                    else:
                        temp_error.append([get_error['height'] for e in data[-1][0]])
                if 'top' in get_error.keys() and not get_error['top'] is None:
                    temp_header.append(names[-1] + " (ey+)")
                    if isinstance(get_error['top'], list) or isinstance(get_error['top'], np.ndarray):
                        temp_error.append(get_error['top'])
                    else:
                        temp_error.append([get_error['top'] for e in data[-1][0]])
                if 'bottom' in get_error.keys() and not get_error['bottom'] is None:
                    temp_header.append(names[-1] + " (ey-)")
                    if isinstance(get_error['bottom'], list) or isinstance(get_error['bottom'], np.ndarray):
                        temp_error.append(get_error['bottom'])
                    else:
                        temp_error.append([get_error['bottom'] for e in data[-1][0]])
                error.append(temp_error)
            else:
                error.append(None)

            header.extend(temp_header)

        if self.params['separator'] == 'comma':
            sep = ','
        else:
            sep = '\t'

        with open(fileName, 'w') as fd:
            fd.write(sep.join(header) + '\n')
            i = 0
            numFormat = '%%0.%dg' % self.params['precision']
            numRows = max([len(d[0]) for d in data])
            for i in range(numRows):
                for j, d in enumerate(data):
                    # write x value if this is the first column, or if we want
                    # x for all rows
                    if append_all_x or j == 0:
                        if d is not None and i < len(d[0]):
                            fd.write(numFormat % d[0][i] + sep)
                        else:
                            fd.write(' %s' % sep)

                    # write y value
                    if d is not None and i < len(d[1]):
                        fd.write(numFormat % d[1][i] + sep)
                    else:
                        fd.write(' %s' % sep)

                    # write error value
                    if append_errors and not error[j] is None :
                        if i < len(d[1]):
                            for e in error[j]:
                                fd.write(numFormat % e[i] + sep)
                        else:
                            for e in error[j]:
                                fd.write(' %s' % sep)
                fd.write('\n')

CSVExporter.register()        
                
        
