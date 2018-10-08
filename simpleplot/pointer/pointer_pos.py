    
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
    
class Pointer_Position:
        
    def __init__(self, parent):
        '''
        ##############################################
        This is the main pointer position evaluation 
        system. In here we will define simple methods
        that will be inherited by all children. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        self.parent         = parent

    def fetch_position_data(self):
        '''
        ##############################################
        This method will go through all plot items in 
        the canvas and map their datapoints. This will
        then allow the evaluater to access on screen 
        information. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        self.mapping = []
        self.data    = []

        for plothandler in self.parent.canvas.artist.plot_handlers:

            for plot_element in plothandler.plot_elements:

                self.mapping.append([
                    plothandler.name,
                    plot_element
                ])

                self.data.append([plot_element.x_data, plot_element.y_data])


    def evaluate(self):
        '''
        ##############################################
        Defaul do nothng
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        pass


class Type_0_Position(Pointer_Position):

    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Position.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        ##############################################
        old find_nearestY. This method aims at 
        searching sucessively for the nearest value in 
        all plots by first scanning the nearest X. 
        Then e find the second nearest to zero after 
        X-Nearest. This will give us back two point 
        ids which whome we can calculate the nearest Y
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #first grab closest Id to the researched value
        point_list = []

        for i in range(len(self.data)):
        
            #search the first closest
            idx_0 = (np.abs(np.asarray(self.data[i][0]) - self.parent.cursor_x)).argmin()

            try:
                if self.data[i][0][idx_0] <= self.parent.cursor_x:
                    
                    #check for the array direction
                    if self.data[i][0][idx_0] < self.data[i][0][idx_0+1]:
                        idx_1 = idx_0 + 1
            
                    else:
                        idx_1 = idx_0 - 1
                else:
                    
                    #check for the array direction
                    if self.data[i][0][idx_0] < self.data[i][0][idx_0+1]:

                        idx_0 -= 1
                    
                        idx_1  = idx_0 + 1

                    else:
                        
                        idx_0 += 1
                    
                        idx_1  = idx_0 - 1

                #calclate the Y from these positions
                if self.mapping[i][0] == 'Scatter' and not '-' in self.mapping[i][1].get_para('Style'):
                    point_list.append(float(self.data[i][1][idx_0]))

                else:
                    point_list.append(
                        float(self.data[i][1][idx_0])+float((self.parent.cursor_x-self.data[i][0][idx_0]))
                        *(float(self.data[i][1][idx_1])-float(self.data[i][1][idx_0]))
                        /(float(self.data[i][0][idx_1])-float(self.data[i][0][idx_0])))
            except:
                point_list.append(np.inf)
        
        if not len(point_list) == 0:
            
            #grab the second one
            idx_2   = (np.abs(np.asarray(point_list)-self.parent.cursor_y)).argmin()
        
            if not self.parent.method == None:
            
                self.parent.method(
                    self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                    [self.parent.cursor_x,self.parent.cursor_y])

            if self.mapping[idx_2][0] == 'Scatter' and not '-' in self.mapping[idx_2][1].get_para('Style'):
                    
                    self.parent.cursor_x = self.data[idx_2][0][idx_0]

            self.parent.cursor_y = point_list[idx_2]
        
        else:
            pass
        

class Type_1_Position(Pointer_Position):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Position.__init__(self,parent)
        self.parent = parent


    def evaluate(self):
        '''
        ##############################################
        old find_nearestX. This method aims at 
        searching sucessively for the nearest value in 
        all plots by first scanning the nearest X. 
        Then e find the second nearest to zero after 
        X-Nearest. This will give us back two point 
        ids which whome we can calculate the nearest Y
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #first grab closest Id to the researched value
        point_list = []

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

                #calclate the Y from these positions
                if self.mapping[i][0] == 'Scatter' and not '-' in self.mapping[i][1].get_para('Style'):
                    point_list.append(float(self.data[i][0][idx_0]))

                else:
                    point_list.append(
                        float(self.data[i][0][idx_0])+float((self.parent.cursor_y-self.data[i][1][idx_0]))
                        *(float(self.data[i][0][idx_1])-float(self.data[i][0][idx_0]))
                        /(float(self.data[i][1][idx_1])-float(self.data[i][1][idx_0])))
            except:
                point_list.append(np.inf)
        
        if not len(point_list) == 0:
            
            #grab the second one
            idx_2   = (np.abs(np.asarray(point_list)-self.parent.cursor_x)).argmin()
        
            if not self.parent.method == None:
                
                self.parent.method(
                    self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                    [self.parent.cursor_x,self.parent.cursor_y])
        
            
            self.parent.cursor_x = point_list[idx_2]

            if self.mapping[idx_2][0] == 'Scatter' and not '-' in self.mapping[idx_2][1].get_para('Style'):

                    self.parent.cursor_y = self.data[idx_2][1][idx_0]
        
        else:
            pass


class Type_2_Position(Pointer_Position):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Position.__init__(self,parent)


    def evaluate(self):
        '''
        ##############################################
        This method aims at searching sucessively for 
        the nearest value in all plots by first 
        scanning the nearest X. Then e find the second 
        nearest to zero after X-Nearest. This will 
        give us back two point ids which whome we can 
        calculate the nearest Y
        
        This version will pin it to the closest point 
        also. This is particulary helpful when dealing 
        with scatter plots
        
        Note that this version also sends out the 
        function so the point editor can do it's work...
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
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

class Type_3_Position(Pointer_Position):
    
    def __init__(self, parent):
        '''
        ##############################################
        Type_0 cursor init
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        Pointer_Position.__init__(self,parent)
        self.parent = parent

    def evaluate(self):
        '''
        ##############################################
        This tries to find the closest X and Y of the 
        a the first contour plots...
        Multiple contours are not supporte yet abd 
        frankly don't make to much sense therefore we
        will simply grab contour [0].
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        #first grab closest Id to the researched value
        idx_0 = (np.abs(np.asarray(self.data[0][0]) - self.parent.cursor_x)).argmin()
        idx_1 = (np.abs(np.asarray(self.data[0][1]) - self.parent.cursor_y)).argmin()

        if not self.parent.method == None:
                    
            self.parent.method(
                self.parent.canvas.plot_handlers[self.mapping[idx_2][0]][self.mapping[idx_2][1]], 
                [self.parent.cursor_x,self.parent.cursor_y])
                
        self.parent.cursor_x = self.data[0][0][idx_0]
        self.parent.cursor_y = self.data[0][1][idx_1]


# class Type_4_Position(Pointer_Position):
    
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
#         Pointer_Position.__init__(self,parent)
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