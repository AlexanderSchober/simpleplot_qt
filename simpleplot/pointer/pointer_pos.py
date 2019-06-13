    
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
import numpy as np
    
class PointerPosition:
        
    def __init__(self, parent):
        '''
        This is the main pointer position evaluation 
        system. In here we will define simple methods
        that will be inherited by all children. 
        '''
        self.parent = parent

    def fetch_position_data(self):
        '''
        This method will go through all plot items in 
        the canvas and map their datapoints. This will
        then allow the evaluator to access on screen 
        information. 
        '''
        self.mapping = []
        self.data    = []

        for plot_handler in self.parent.canvas._plot_root._children:
            for plot_element in plot_handler._children:
                try:
                    self.mapping.append([plot_handler.name,plot_element])
                    self.data.append([plot_element.x_data, plot_element.y_data])
                    if plot_handler.name == 'Surface':
                        self.data[-1].append(plot_element.z_data)
                except:
                    pass

    def evaluate(self):
        '''
        '''
        pass


class Type_0_Position(PointerPosition):

    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        old find_nearestY. This method aims at 
        searching successively for the nearest value in 
        all plots by first scanning the nearest X. 
        Then e find the second nearest to zero after 
        X-Nearest. This will give us back two point 
        ids which whom we can calculate the nearest Y
        '''
        point_list = []
        idx_list = []

        for i in range(len(self.data)):
            #search the first closest
            x_data = np.asarray(self.data[i][0])
            x_data = np.log10(x_data) if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else x_data

            idx_0 = (np.abs(x_data - self.parent.cursor_x)).argmin()
            try:
                if x_data[idx_0] <= self.parent.cursor_x:
                    if x_data[idx_0] < x_data[idx_0+1]:
                        idx_1 = idx_0 + 1
                    else:
                        idx_1 = idx_0 - 1
                else:
                    if x_data[idx_0] < x_data[idx_0+1]:
                        idx_0 -= 1
                        idx_1  = idx_0 + 1
                    else:
                        idx_0 += 1
                        idx_1  = idx_0 - 1
                idx_list.append(idx_0)

                #calclate the Y from these positions
                if self.mapping[i][0] == 'Scatter' and not '-' in self.mapping[i][1].getParameter('Style'):
                    point_list.append(float(
                        np.log10(self.data[i][1][idx_0]) if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else self.data[i][1][idx_0]))
                    

                else:
                    x_data_0 = np.asarray(self.data[i][0][idx_0])
                    x_data_0 = np.log10(x_data_0) if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else x_data_0
                    x_data_1 = np.asarray(self.data[i][0][idx_1])
                    x_data_1 = np.log10(x_data_1) if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else x_data_1

                    y_data_0 = np.asarray(self.data[i][1][idx_0])
                    y_data_0 = np.log10(y_data_0) if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else y_data_0
                    y_data_1 = np.asarray(self.data[i][1][idx_1])
                    y_data_1 = np.log10(y_data_1) if self.parent.canvas.draw_surface.ctrl.logYCheck.isChecked() else y_data_1

                    val = (y_data_0+(self.parent.cursor_x-x_data_0)*(y_data_1-y_data_0) /(x_data_1-x_data_0))

                    point_list.append(val)
            except:
                idx_list.append(0)
                point_list.append(np.inf)
        
        if not len(point_list) == 0:
            
            #grab the second one
            idx_2   = (np.abs(np.asarray(point_list)-self.parent.cursor_y)).argmin()
            if not self.parent.method == None:
                self.parent.method(
                    self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                    [self.parent.cursor_x,self.parent.cursor_y])

            if self.mapping[idx_2][0] == 'Scatter' and not '-' in self.mapping[idx_2][1].getParameter('Style'):
                    self.parent.cursor_x = self.data[idx_2][0][idx_list[idx_2]]
                    self.parent.cursor_x = np.log10(self.parent.cursor_x) if self.parent.canvas.draw_surface.ctrl.logXCheck.isChecked() else self.parent.cursor_x

            self.parent.cursor_y = point_list[idx_2]
        
        else:
            pass
        

class Type_1_Position(PointerPosition):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        old find_nearestX. This method aims at 
        searching successively for the nearest value in 
        all plots by first scanning the nearest X. 
        Then e find the second nearest to zero after 
        X-Nearest. This will give us back two point 
        ids which whom we can calculate the nearest Y
        '''
        #first grab closest Id to the researched value
        point_list  = []
        idx_list    = []

        for i in range(len(self.data)):
            #search the first closest
            idx_0 = (np.abs(np.asarray(self.data[i][1]) - self.parent.cursor_y)).argmin()

            try:
                if self.data[i][1][idx_0] <= self.parent.cursor_y:
                    #check for the array direction
                    if self.data[i][1][idx_0] < self.data[i][1][idx_0 + 1]:
                        idx_1 = idx_0 + 1
            
                    else:
                        idx_1 = idx_0 - 1
                else:
                    
                    #check for the array direction
                    if self.data[i][1][idx_0] < self.data[i][1][idx_0 + 1]:
                        idx_0 -= 1
                        idx_1  = idx_0 + 1

                    else:
                        idx_0 += 1
                        idx_1  = idx_0 - 1

                idx_list.append(idx_0)

                #calclate the Y from these positions
                if self.mapping[i][0] == 'Scatter' and not '-' in self.mapping[i][1].getParameter('Style'):
                    point_list.append(float(self.data[i][0][idx_0]))

                else:
                    point_list.append(
                        float(self.data[i][0][idx_0])+float((self.parent.cursor_y-self.data[i][1][idx_0]))
                        *(float(self.data[i][0][idx_1])-float(self.data[i][0][idx_0]))
                        /(float(self.data[i][1][idx_1])-float(self.data[i][1][idx_0])))
            except:
                point_list.append(np.inf)
                idx_list.append(0)
        
        if not len(point_list) == 0:
            
            #grab the second one
            idx_2   = (np.abs(np.asarray(point_list)-self.parent.cursor_x)).argmin()
        
            if not self.parent.method == None:
                
                self.parent.method(
                    self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                    [self.parent.cursor_x,self.parent.cursor_y])
            
            self.parent.cursor_x = point_list[idx_2]

            if self.mapping[idx_2][0] == 'Scatter' and not '-' in self.mapping[idx_2][1].getParameter('Style'):

                    self.parent.cursor_y = self.data[idx_2][1][idx_list[idx_2]]
        
        else:
            pass

class Type_2_Position(PointerPosition):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)

    def evaluate(self):
        '''
        This method aims at searching successively for 
        the nearest value in all plots by first 
        scanning the nearest X. Then e find the second 
        nearest to zero after X-Nearest. This will 
        give us back two point ids which whom we can 
        calculate the nearest Y
        
        This version will pin it to the closest point 
        also. This is particulars helpful when dealing 
        with scatter plots
        
        Note that this version also sends out the 
        function so the point editor can do it's work...
        '''
        #first grab closest Id to the researched value
        point_list = []
        idx_0 = []

        for i in range(len(self.data)):
            #search the first closest
            idx_0.append((np.abs(np.asarray(self.data[i][0]) - self.parent.cursor_x)).argmin())
            #calclate the Y from these positions
            try:
                point_list.append(float(self.data[i][1][idx_0[-1]]))
                
            except:
                point_list.append(np.inf)
        
        idx_2 = (np.abs(np.asarray(point_list) - self.parent.cursor_y)).argmin()
    
        if not self.parent.method == None:
                    
            self.parent.method(
                self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                [self.parent.cursor_x,self.parent.cursor_y])
                
        self.parent.cursor_x = self.data[idx_2][0][idx_0[idx_2]]
        self.parent.cursor_y = point_list[idx_2]

class Type_3_Position(PointerPosition):
    
    def __init__(self, parent):
        '''
        Type_0 cursor init
        '''
        PointerPosition.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        This tries to find the closest X and Y of the 
        a the first contour plots...
        Multiple contours are not supported yet and 
        frankly don't make to much sense therefore we
        will simply grab contour [0].
        '''
        idx_0 = (np.abs(np.asarray(self.data[0][0]) - self.parent.cursor_x)).argmin()
        idx_1 = (np.abs(np.asarray(self.data[0][1]) - self.parent.cursor_y)).argmin()

        if not self.parent.method == None:
                    
            self.parent.method(
                self.parent.canvas.plot_handlers[self.mapping[0][0]][self.mapping[0][1]], 
                [self.parent.cursor_x,self.parent.cursor_y])
                
        self.parent.cursor_x = self.data[0][0][idx_0]
        self.parent.cursor_y = self.data[0][1][idx_1]
        self.parent.cursor_z = self.data[0][2][idx_0, idx_1]

# class Type_4_Position(PointerPosition):
    
#     def __init__(self, parent):
#         '''
#         ##############################################
#         Type_0 cursor init
#         ———————
#         Input: -
#         ———————
#         Output: -
#         ———————
#         status: active
#         ##############################################
#         '''
#         PointerPosition.__init__(self,parent)
#         self.parent = parent

#     def find_nearestXCascade(self, X, Y):
        
#         '''
#         ##########################################################################################
#         This tries to find the closest X and Y of the a the first contour plots...
#         Multiple contours are not supporte yet abd frankly don't make to much sense therefore we
#         will simply grab contour [0]
#         ##########################################################################################
#         '''

#         if not self.Initialise:
            
#             try:
            
#                 #set variable
#                 self.Target = self.Canvas.Drawer.Cascades[0]
                
#                 #set variable
#                 self.Target_X = np.asarray(self.Target[0][0])
#                 self.Target_Z = np.asarray(self.Target.Z)
            
#                 #set variable
#                 self.Initialise = True
                
#             except:
#                 print('Could not intialise')
#                 return 0,0
                    
#         List = []
    
#         #search the first closest
#         idx_0 = (np.abs(self.Target_X- X)).argmin()
    
#         #search the second closest (obviously our value will be in between)
#         for i in range(0,len(self.Target.Z)):
            
#             try:
#                 if self.Canvas.Drawer.Plots[i][0][idx_0] <= X:
                    
#                     #check for the array direction
#                     if self.Canvas.Drawer.Plots[i][0][idx_0]<self.Canvas.Drawer.Plots[i][0][idx_0+1]:
                        
#                         idx_1 = idx_0+1
            
#                     else:
                        
#                         idx_1 = idx_0-1
#                 else:
                    
#                     #check for the array direction
#                     if self.Canvas.Drawer.Plots[i][0][idx_0]<self.Canvas.Drawer.Plots[i][0][idx_0+1]:

#                         idx_0 -= 1
                    
#                         idx_1  = idx_0+1

#                     else:
                        
#                         idx_0 += 1
                    
#                         idx_1  = idx_0-1

        
#                 #calclate the Y from these positions
#                 List.append(float(self.Canvas.Drawer.Plots[i][1][idx_0])+float((X-self.Canvas.Drawer.Plots[i][0][idx_0]))*
#                             (float(self.Canvas.Drawer.Plots[i][1][idx_1])-float(self.Canvas.Drawer.Plots[i][1][idx_0]))/
#                             (float(self.Canvas.Drawer.Plots[i][0][idx_1])-float(self.Canvas.Drawer.Plots[i][0][idx_0])))
#             except:
#                 List.append(np.inf)
    
#         if self.Verbose:
#             print(List)
        
#         idx_2 = (np.abs(List-Y)).argmin()
    
#         if not self.Method == None:
        
#             self.Method(idx_2, [X,Y])
        
#         return X,List[idx_2],idx_2