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

#import dependencies
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from .pointer_objects import *
from .pointer_pos import *

class Pointer:
    '''
    ######################################################
    This class will manage the pointer behaviour. Note 
    that it will only bin and unbind on request. This 
    method should be exited to reach the desired
    bhaviour
    
    - if sticky is 0 the cursor is free
    - if sticky is 1 the cursor follows the closest line
    - if sticky is 2 the cursor sticks to points
    ######################################################
    '''

    def __init__(self, canvas):

        ##################################################
        #Bind to the canvas.
        self.canvas = canvas
        self.init_parameters()

        ##################################################
        #for debugging
        self.verbose        = False
        self.initialised    = False

    def init_parameters(self):
        '''
        ##############################################
        This method allows to set the pointer elements
        such as the hardcoded parameters and the 
        editable variables. 

        variables will be eidtable in the preference
        window and will therefore be saved as dict 
        with the proper values
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.live           = True
        self.locked         = False
        self.projections    = [None, None]
        self.method         = None
        
        self.x              = 0
        self.y              = 0
        self.cursor_x       = 0.0
        self.cursor_y       = 0.0
        self.link_list      = []
        self.method         = None


        self.pointer_component  = Pointer_Object(self)
        self.label_component    = Pointer_Object(self)
        self.pointer_position   = Pointer_Position(self)
    
        ##################################################
        #cursor parameters
        self.para_dict  = {}
        self.para_dict['Color']         = ['black', ['str', 'hex']] 
        self.para_dict['Thickness']     = [2, ['int']]
        self.para_dict['Rounding']      = [1, ['int']]
        
        ##################################################
        #sticky parameter
        self.para_dict['Sticky']    = [0, ['int']]
        self.para_dict['Type']      = [1, ['int']]
        self.para_dict['Size']      = [(20,20), ['tuple', 'int']]
        
        ##################################################
        #Do we want labels? Types:
        
        self.para_dict['Labels']            = [(False,False,True,True), ['tuple','bool', 'int'], 'Labels']
        self.para_dict['Label_Type']        = [2, ['int'], 'Type']
        self.para_dict['Label_Color']       = ['black', ['str', 'hex'], 'Color']
        self.para_dict['Label_Sci.']        = [(False,False,False,False), ['str', 'hex'], 'Scientific']
        self.para_dict['Label_Precision']   = [('.1','.1','.1','.1'), ['tuple', 'str'], 'Precision']

        if os.name == 'nt':
            self.para_dict['Label_Font']        = [('Helvetica', '9'), ['tuple', 'str', 'int']]
        else:
            self.para_dict['Label_Font']        = [('Helvetica', '11'), ['tuple', 'str', 'int']]

        self.para_dict['Ticks']             = [(False,False,True,True), ['tuple', 'bool', 'int']]
        self.para_dict['Tick_Thickness']    = [5, ['int']]
        self.para_dict['Tick_Color']        = ['blue', ['str', 'hex']]
        self.para_dict['Tick_Offset']       = [0, ['int']]

    def get_para(self, name):
        '''
        ##############################################
        Returns the value of the parameter requested
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        return self.para_dict[name][0]

    def __setitem__(self, name, value):
        '''
        ##############################################
        Returns the value of the parameter requested
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        self.para_dict[name][0] = value

    def set_pen(self):
        '''
        ##############################################
        This method will initialise the Qpen as the
        the QPainter method
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #initialise the pen
        self.pen = pg.mkPen({
                'color': QtGui.QColor(self.get_para('Color')),
                'width': self.get_para('Thickness')
            })

    def setup(self, init = True):
        '''
        ##############################################
        Set the cenvironement and select the right
        pointer label and corrector type
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        exec(
            'self.pointer_component = Type_'
            +str(self.get_para('Type'))
            +'_Pointer(self)')

        exec(
            'self.label_component = Type_'
            +str(self.get_para('Label_Type'))
            +'_Labels(self)')

        exec(
            'self.pointer_position = Type_'
            +str(self.get_para('Sticky'))
            +'_Position(self)')

        self.live = True

    def bind_pointer(self):
        '''
        ##############################################
        Binds the cursor to the system signals of the
        mouse 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.setup()

        self.pointer_position.fetch_position_data()
    
        self.canvas.artist.mouse.bind('move', self.refresh_pos, 'pointer_move')

        self.draw()

    def unbind_pointer(self):
        '''
        ##############################################
        Binds the cursor to the system signals of the
        mouse 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.canvas.artist.mouse.unbind('move', 'pointer_move')
        
        #initialise the local drawing method
        self.pointer_component.disconnect()
        self.label_component.disconnect()

        self.live = False
        
    def refresh_pos(self,x = None, y = None):
        '''
        ##############################################
        Rfresh the local position of the cursor
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #fetch them 
        if x == None or y == None:
            x = self.canvas.artist.mouse.cursor_x
            y = self.canvas.artist.mouse.cursor_y

        #grab the position
        if not self.locked:
            self.cursor_x = x 
            self.cursor_y = y 
            self.cursor_z = 0

            #correct posiiton
            self.pointer_position.evaluate()

            self.canvas.multi_canvas.bottom_selector.label.setText(
                str(
                    "  x = %"+str(self.get_para('Label_Precision')[0])+"f"
                    ", y = %"+str(self.get_para('Label_Precision')[0])+"f"
                    ", z = %"+str(self.get_para('Label_Precision')[0])+"f"
                    )%(
                        self.cursor_x,
                        self.cursor_y,
                        self.cursor_z))
        
        if self.live:
            #call the local drawing method
            self.draw()

    def draw(self, init = True):
        '''
        ##############################################
        In this method we will draw the cursor onto 
        the canvas. Note that this method will
        differenciate between initialisationa and
        the update
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #now the lines
        self.pointer_component.move()

        #now the lines
        self.label_component.move()






