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

from ..pyqtgraph import pyqtgraph as pg
from PyQt5 import QtCore, Qt, QtGui
import numpy as np

class Mouse:
    '''
    In this class we aim at having a mouse ev
    listener always active that will then allow
    the other objects to directly fetch the 
    parameters from here. This avoids many 
    listeners.
    '''

    def __init__(self, canvas):

        #make the local reference
        self.canvas     = canvas
        self.verbose    = False
        
        #Bound mouse method list
        self.move_methods       = []
        self.press_methods      = []
        self.release_methods    = []
        self.drag_methods       = []
        
        #the list of mouses to communicate to
        self.link_list = []
    
        #initialise
        self.cursor_x = 0
        self.cursor_y = 0
        self.pressed  = []
        self.released = []

    def get_pos(self):
        '''
        Get the current mouse position. 
        '''
        return self.cursor_x, self.cursor_y

    def bind(self, motion_type, method, id_string, button = None, send_ev = False):
        '''
        This methods allows the developer to bind 
        methods to the mouse evs. The move ev 
        will trigger the mouse motion ev based 
        routines wand call them with the corrdinatess
        etc...
        ———————
        Input: 
        - motion_type 
        - the method to bind
        - the id string to identify it
        '''
        if motion_type == 'move':
            self.move_methods.append([method, id_string, send_ev])

        elif motion_type == 'drag':
            self.drag_methods.append([method, id_string, button, send_ev])

        elif motion_type.split('-')[0] == 'press':
            self.press_methods.append([method, id_string, button, send_ev])

        elif motion_type.split('-')[0] == 'release':
            self.release_methods.append([method, id_string, button, send_ev])
        
        else:
            print('Motion type not found')
        
    def unbind(self, motion_type, id_string):
        '''
        This method is the counterpart to the bind 
        method ans serves to remove methods. 
        ———————
        Input: 
        - motion_type 
        - the id string to identify it
        '''
        #normal mouse move
        if motion_type == 'move':
            for i in range(len(self.move_methods)):
                if self.move_methods[i][1] == id_string:
                    del self.move_methods[i]
                    break

        if motion_type == 'drag':
            for i in range(len(self.drag_methods)):
                if self.drag_methods[i][1] == id_string:
                    del self.drag_methods[i]
                    break

        elif motion_type == 'press':
            for i in range(len(self.press_methods)):
                if self.press_methods[i][1] == id_string:
                    del self.press_methods[i]
                    break

        elif motion_type == 'release':
            for i in range(len(self.release_methods)):
                if self.release_methods[i][1] == id_string:
                    del self.release_methods[i]
                    break

    def move(self,ev):
        '''
        This method will manage the motion of the 
        mouse and send it out.
        ———————
        Input: 
        - Qt based mouse ev
        '''
        pos             = ev.pos()
        mousePoint      = self.canvas.draw_surface.vb.mapSceneToView(pos)
        self.cursor_x   = mousePoint.x()
        self.cursor_y   = mousePoint.y()
        self.transmit_motion()
        self.evaluateMotion()

    def drag(self,ev):
        '''
        This method will manage the drag of the 
        mouse and send it out.
        ———————
        Input: 
        - Qt based mouse ev
        '''
        ev.accept()

        start = self.canvas.draw_surface.vb.mapToView(ev.buttonDownPos())
        last  = self.canvas.draw_surface.vb.mapToView(ev.lastPos())
        pos   = self.canvas.draw_surface.vb.mapToView(ev.pos())
        
        self.cursor_x_init = start.x()
        self.cursor_y_init = start.y()

        self.cursor_x_last = last.x()
        self.cursor_y_last = last.y()

        self.cursor_x = pos.x()
        self.cursor_y = pos.y()

        self.drag_start = ev.isStart()
        self.drag_end   = ev.isFinish()

        self.evaluateDrag(ev)

    def press(self,ev):
        '''
        This method will manage the pressing of the 
        mouse and send it out.
        
        Input: 
        - Qt based mouse ev
        '''
        
        try:
            self.released.remove(ev.button())
        except:
            pass
        self.pressed.append(ev.button())
        self.evaluatePress(ev)
    
    def release(self,ev):
        '''
        This method will manage the release of the 
        mouse and send it out.
        ———————
        Input: 
        - Qt based mouse ev
        '''
        try:
            self.pressed.remove(ev.button())
        except:
            pass
        self.released.append(ev.button())
        self.evaluateRelease(ev)

    def evaluateMotion(self):
        '''
        Evaluate the motion of the mouse onto the 
        linked methods.
        '''
        for method in self.move_methods:
            method[0](self.cursor_x,self.cursor_y)

    def evaluateDrag(self, ev):
        '''
        Evaluate the motion of the mouse onto the 
        linked methods.
        '''
        for method in self.drag_methods:
            if method[2] == ev.button():
                method[0](
                    [
                        self.cursor_x_init,
                        self.cursor_x_last,
                        self.cursor_x],
                    [
                        self.cursor_y_init,
                        self.cursor_y_last,
                        self.cursor_y],
                    self.drag_start,
                    self.drag_end)

    def evaluatePress(self, ev):
        '''
        Evaluate the motion of the mouse onto the 
        linked methods.
        '''
        for method in self.press_methods:
            if method[2] == ev.button():
                if method[3]:
                    method[0](ev)
                else:
                    method[0]()

    def evaluateRelease(self, ev):
        '''
        Evaluate the motion of the mouse onto the 
        linked methods.
        '''
        for method in self.release_methods:
            if method[2] == ev.button():
                if method[3]:
                    method[0](ev)
                else:
                    method[0]()

    def transmit_motion(self):
        '''
        This is a feature where the cursor motion in 
        a canvas can be transmitted to the counter-
        parts another canvases. 
        '''
        for link in self.link_list:
            if link[2] == 'x':
                if link[3] == 'x':
                    link[4].cursor_x = np.copy(self.canvas.artist.pointer.cursor_x)
                if link[3] == 'y':
                    link[4].cursor_y = np.copy(self.canvas.artist.pointer.cursor_x)
            if link[2] == 'y':
                if link[3] == 'x':
                    link[4].cursor_x = np.copy(self.canvas.artist.pointer.cursor_y)
                if link[3] == 'y':
                    link[4].cursor_y = np.copy(self.canvas.artist.pointer.cursor_y)

            link[5].evaluateMotion()
    