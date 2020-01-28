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

from PyQt5 import QtWidgets, QtGui, QtCore
from .gui_subwindows.subwindow_main import SubwindowMain

class Playground(QtWidgets.QMdiArea):
    '''
    This will be the main playground where the sub-windows
    will be displayed. 
    '''
    def __init__(self, *args, **kwargs):
        super(Playground, self).__init__(*args, **kwargs)
        child = SubwindowMain(self)
        child.setHidden(True)

    def displaySubwindow(self, item):
        '''
        Create the plot subwindow and return it for 
        the caller to register it into the model
        '''
        if not item.display_widget.parent() == None:
            item.display_widget.parent().close()

        child = SubwindowMain(self)
        item.display_widget.setup()
        child.setWidget(item.display_widget)
        child.show()
