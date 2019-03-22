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

#import personal dependencies
from .canvas import Canvas_2D, Canvas_3D
from .gui.mode_select import Mode_Select

#import general
from PyQt5 import QtWidgets, QtGui, QtCore

# a subclass of Canvas for dealing with resizing of windows
class Multi_Canvas(QtWidgets.QGridLayout):
    
    def __init__(self,
                 parent,
                 grid           = [[True]],
                 element_types  = None,
                 x_ratios       = [1],
                 y_ratios       = [1],
                 no_title       = False,
                 **kwargs):
        
        '''
        ##############################################
        This method is the plot cnavas where all the 
        elements will be drawn upon. It inherits
        from the Graphocslayoutwidget library that 
        was custom built on top of qt for python. 
        ———————
        Input: 
        - parent is the parent widget 
        - grid is the amount of rows ans cols wanted
        - x_ratio is the ratios along the cols
        - y_ratio is the ratios along the rowns
        - no_title allows to set titles or not
        ———————
        Output: 
        -
        ———————
        status: active
        ##############################################
        '''

        ####################################
        #initialize the QGridLayout
        QtWidgets.QGridLayout.__init__(self,parent)
        
        ####################################
        #Default parameetrs
        self.verbose        = True
        self.parent         = parent
        self.grid           = grid
        self.x_ratios       = x_ratios
        self.y_ratios       = y_ratios
        self.no_title       = no_title
        self.icon_dim       = 25
        
        ####################################
        #Prepare the object adress array
        self.canvas_objects     = []
        self.titles             = []
        self.settings           = []
        self.link_list          = []
        self.grab_object        = []
        self.link_list          = []
        
        #prepare an index
        Index = 0
        
        #make a internal reference matrix
        for i in range(0,len(grid)):
            
            #append empty array
            self.canvas_objects.append([])
        
            for j in range(0,len(grid[i])):
        
                #check condition
                if grid[i][j]:
                    
                    if element_types == None:

                        self.canvas_objects[i].append(
                            [Canvas_2D(
                                multi_canvas    = self,
                                idx             = Index,
                                **kwargs)
                            ,i,j])

                    elif element_types[i][j] == '2D':

                        self.canvas_objects[i].append(
                            [Canvas_2D(
                                multi_canvas    = self,
                                idx             = Index,
                                **kwargs)
                            ,i,j])

                    elif element_types[i][j] == '3D':
    
                        self.canvas_objects[i].append(
                            [Canvas_3D(
                                multi_canvas    = self,
                                idx             = Index,
                                **kwargs)
                            ,i,j])
                        
                    #make a pointer list
                    self.grab_object.append(self.canvas_objects[i][-1])

                    self.canvas_objects[i][-1][0].setMinimumSize(0,0)
                
                else:
    
                    self.canvas_objects[i].append(None)
    

        # ####################################
        # #Try to place the elements
        self.place_objects()
        self.configure_grid(
            self.x_ratios,
            self.y_ratios)
        self.layout_manager()

        # ####################################
        # #Configure settings window
        # self.SettingsClass = SettingsClass(parent,self)
    
    def place_objects(self):
        '''
        ##############################################
        This method aims at placing all the Canvas 
        class widgets onto the mulitcanvas grid. It
        will therefore cycle through and use the 
        inherited addWidget method.
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
                
        #cycle through all elements
        for element_list in self.canvas_objects:
            for element in element_list:
                
                if element == None:

                    pass

                else:

                    self.addWidget(*element)

    def configure_grid(self, x_ratios, y_ratios):
        '''
        ##############################################
        This method will run through the elements and
        set the desired fractional ratios between
        cells and rows.
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''
        for i in range(len(self.canvas_objects)):
            for j in range(len(self.canvas_objects[i])):

                width  = ( self.parent.frameGeometry().width()  / len(self.canvas_objects[i]) ) / x_ratios[j]
                height = ( self.parent.frameGeometry().height() / len(self.canvas_objects) )    / y_ratios[i]

                print(width, height)

                self.canvas_objects[i][j][0].resize(width, height)


        for i in range(0,len(x_ratios)):
        
            try:
                #configure the frame
                self.setColumnStretch(i,1/x_ratios[i])
    
            except:
                if self.Verbose:
                    print('Could not set the row weight for: ',i)
        
        for j in range(0,len(y_ratios)):
            try:
                #configure the frame
                self.setRowStretch(i,1/y_ratios[j])
    
            except:
                if self.Verbose:
                    print('Could not set the row weight for: ',j)

    def layout_manager(self):
        '''
        ##############################################
        This method will process the layout of the 
        various simpleplot tools and buttons around
        the main frame. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        #create the manager frame
        self.bottom_selector = Mode_Select(self,self.parent, self.icon_dim)
        self.addItem(
            self.bottom_selector, 
            len(self.grid), 
            0,  
            columnSpan=len(self.grid[0]))
        
    def get_subplot(self,i,j):
        '''
        ##############################################
        This method allows the user to fetch the 
        sublot that he recquires. This is though to be
        used very much like the subplot function in
        matplotlib. 
        ———————
        Input: -
        ———————
        Output: -
        ———————
        status: active
        ##############################################
        '''

        return self.canvas_objects[i][j][0].artist


    def link(self, ax , bx , variableIn = 'x', variableOut = 'x'):
    
        '''
        ########################################################################
        This class is here to allow for corss listening between variables
        between different subplots...
        
        
        This will call the pointer of ax and bx and tell thel to pass on the
        coordinates to the pointer handlers each time there is a refresh. 
        
        So basically we parasite the pointer to speak to another element
        
        This will also return a link in the link list and an associated ID
        The ID will be returned and can be fed to the Unlink
        ########################################################################
        '''
        
        #set the target
        target = bx.mouse
        
        #create the array of th emethod
        link = [
            '',
            ax.mouse.link_list,
            variableIn,
            variableOut, 
            target, 
            bx.mouse]
        
        #add the element at the end of the list
        self.link_list.append(link)

        #append the ID
        ID = self.link_list[-1][0] = len(self.link_list)

        #finally send it out to the linker
        link[1].append(self.link_list[-1])
        
        return ID
