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

#import dependencies
from PyQt5      import QtWidgets, QtGui, QtCore
from functools  import partial

class CanvasWidget(QtWidgets.QWidget): 
    drop_success = QtCore.pyqtSignal(list)
    '''
    Thi method is a custom modification of the 
    QListView widget that supports drag and 
    drop.
    '''        
    def __init__(self, parent = None):
        super(CanvasWidget, self).__init__(parent)
        
        self.setAcceptDrops(True)
        self.dropEvent = partial(NumpyFileDrop, self)
        self.check     = NumpyFileCheck

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if self.check(event):
                event.acceptProposedAction()
            else:
                super(CanvasWidget, self).dragEnterEvent(event)
        else:
            super(CanvasWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(CanvasWidget, self).dragMoveEvent(event)

def NumpyFileDrop(generator_class, event):
    '''
    This is the drop method and will support the
    drop of the files into the list. 
    '''
    if event.mimeData().hasUrls():
        if NumpyFileCheck(event):
            event.acceptProposedAction()
            generator_class.drop_success.emit([url.path() for url in event.mimeData().urls()])

def NumpyFileCheck(event):
    '''
    check if the file are numpy
    '''
    urls          = [url for url in event.mimeData().urls()]
    bool_numpy    = [False for e in urls]

    for i, url in enumerate(urls):
        if url.path().split('.')[-1] == "txt":
            bool_numpy[i] = True
        elif url.path().split('.')[-1] == "npy":
            bool_numpy[i] = True
        elif url.path().split('.')[-1] == "npz":
            bool_numpy[i] = True

    if all(bool_numpy):
        return True
    else:
        return False
        