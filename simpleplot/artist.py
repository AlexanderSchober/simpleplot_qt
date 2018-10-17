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

from .pointer.pointer    import Pointer
from .pointer.zoomer     import Zoomer
from .pointer.measurer   import Measurer
from .mouse              import Mouse
from .axes               import Axes

from .ploting.plot_handler import get_plot_handler


class Artist():
    '''
    ##############################################
    This class is here to perform the managing of
    drawing and displaying. This part should be
    much easier thanks to the use of the qtgraph
    lubrary which has most tools already built 
    in except the management of the pointer
    (for example).

    The canvas inherits all methods from pyqtgraph
    and will the target for ploting.
    ———————
    Input: 
    - parent is the parent canvas class
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, canvas):

        ##########################################
        #internal element indentifier

        self.canvas         = canvas
        self.plot_handlers  = []
        self.artist_type    = '2D'

    def add_plot(self, name_type, *args, **kwargs):
        '''
        ##############################################
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new isntance will be
        generated and then fed into the handler system
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        active_handlers = [handler.name for handler in self.plot_handlers]

        if not name_type in active_handlers:

            self.plot_handlers.append(get_plot_handler(name_type))

            self.plot_handlers[-1].add_item(*args, **kwargs)

        else:

            self.plot_handlers[active_handlers.index(name_type)].add_item(*args, **kwargs)


    def remove_plot(self,name_type, name = '', idx = None):
        '''
        ##############################################
        Remove an item fromt he handlers
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        active_handlers = [handler.name for handler in self.plot_handlers]

        if idx == None and name == '':
            print("You can't remove nothing ...")

        else:
            self.plot_handlers[active_handlers.index(name_type)].remove_item(
                name    = name, 
                idx     = idx,
                target  = self.canvas )
            
    def draw(self):
        '''
        ##############################################
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new isntance will be
        generated and then fed into the handler system
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for plot_handler in self.plot_handlers:

            plot_handler.draw(self.canvas)

    def redraw(self):
        '''
        ##############################################
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new isntance will be
        generated and then fed into the handler system
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for plot_handler in self.plot_handlers:

            plot_handler.draw(self.canvas)

    def clear(self):
        '''
        ##############################################
        Interactive plotting software needs the
        ability to clear the current content. This is 
        done here by asking everyone to be deleted...
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for handler in self.plot_handlers:

            for element in handler.plot_elements:

                element.remove_items(self.canvas)

            handler.plot_elements = []

class Artist2D(Artist):
    '''
    ##############################################
    This class is here to perform the managing of
    drawing and displaying. This part should be
    much easier thanks to the use of the qtgraph
    lubrary which has most tools already built 
    in except the management of the pointer
    (for example).

    The canvas inherits all methods from pyqtgraph
    and will the target for ploting.
    ———————
    Input: 
    - parent is the parent canvas class
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, canvas):


        ##########################################
        #internal element indentifier
        Artist.__init__(self, canvas)

        self.canvas         = canvas
        self.plot_handlers  = []
        self.artist_type    = '2D'
        
        ##########################################
        #Initialise different elements of the plot
        
        #The axes
        self.axes       = Axes(self.canvas)
        
        # #Set the mouse
        self.mouse      = Mouse(self.canvas)
        
        # #Set the keyboard
        # self.Keyboard   = KeyboardClass.Keyboard(self.Canvas,Multi = self.Multi)
        
        # #The pointer
        self.pointer    = Pointer(self.canvas)
        
        # #The zoomer
        self.zoomer     = Zoomer(self.canvas)
        
        # #the measurement Tool
        self.measurer   = Measurer(self.canvas)
        
        # #The Modifier
        # self.Modifier   = ModificationClass.Modify(self.Canvas)
        
        # #the title
        # self.Title      = None #TitleClass.TitleClass(self.Canvas)

    def draw(self):
        '''
        ##############################################
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new isntance will be
        generated and then fed into the handler system
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for plot_handler in self.plot_handlers:

            plot_handler.draw(self.canvas)

        self.setup()

        self.zoomer.zoom()

    def redraw(self):
        '''
        ##############################################
        This method will go through the plot handlers
        and check if one of them has already the 
        selected items. if not a new isntance will be
        generated and then fed into the handler system
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for plot_handler in self.plot_handlers:

            plot_handler.draw(self.canvas)

        self.zoomer.zoom()

    def clear(self):
        '''
        ##############################################
        Interactive plotting software needs the
        ability to clear the current content. This is 
        done here by asking everyone to be deleted...
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        for handler in self.plot_handlers:

            for element in handler.plot_elements:

                element.remove_items(self.canvas)

            handler.plot_elements = []

        self.zoomer.zoom()

    def setup(self):
        '''
        ##############################################
        Once all elements are created it is possible 
        to set up the functionalities. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        try:
            self.pointer.unbind_pointer()
        except:
            pass

        try:
            self.zoomer.quiet()
        except:
            pass

        self.pointer.bind_pointer()
        self.zoomer.listen()

    def set_mode(self, idx):
        '''
        ##############################################
        Once all elements are created it is possible 
        to set up the functionalities. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        self.zoomer.quiet()
        self.measurer.quiet()

        if idx == 0:
            self.zoomer.listen()

        elif idx == 1:
            self.measurer.listen()
        

    def mouse_move(self,event):

        self.mouse.move(event)

    def mouse_press(self,event):

        self.mouse.press(event)

    def mouse_release(self,event):

        self.mouse.release(event)


class Artist3D(Artist):
    '''
    ##############################################
    This class is here to perform the managing of
    drawing and displaying. This part should be
    much easier thanks to the use of the qtgraph
    lubrary which has most tools already built 
    in except the management of the pointer
    (for example).

    The canvas inherits all methods from pyqtgraph
    and will the target for ploting.
    ———————
    Input: 
    - parent is the parent canvas class
    ———————
    Output: -
    ———————
    status: active
    ##############################################
    '''

    def __init__(self, canvas):

        ##########################################
        #internal element indentifier
        Artist.__init__(self, canvas)

        self.canvas         = canvas
        self.plot_handlers  = []
        self.artist_type    = '3D'

        ##########################################
        #internal element indentifier
        
        ##########################################
        #Initialise different elements of the plot

    def setup(self):
        '''
        ##############################################
        Once all elements are created it is possible 
        to set up the functionalities. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass

    def set_mode(self, idx):
        '''
        ##############################################
        Once all elements are created it is possible 
        to set up the functionalities. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass