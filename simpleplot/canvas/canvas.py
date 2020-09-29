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
import os

from ..pyqtgraph.pyqtgraph.graphicsItems.ViewBox import ViewBox

#personal imports
from ..artist.artist          import Artist2DNode, Artist3DNode
from ..models.session_node    import SessionNode
from ..models.parameter_class import ParameterHandler 
from ..models.plot_model      import PlotModel
from ..io.mouse               import Mouse

from ..simpleplot_widgets.SimplePlotGLViewWidget    import MyGLViewWidget
from ..simpleplot_widgets.SimplePlotWidget          import SimplePlotWidget
from ..simpleplot_widgets.SimpleCanvasWidget        import CanvasWidget
from ..simpleplot_widgets.SimplePlotOverlayView     import SimplePlotOverlayView

class CanvasNode(SessionNode):

    def __init__(self, name = '', parent = None, **kwargs):        
        '''
        The canvas _initializes as a widget and will 
        then be fed the layout of the Grid layout. 
        After this the widget will have a central
        drawsurface and other items can be fed around
        widget. 
        ———————
        Input: 
        - parent is the parent widget to inherit from
        - multi_canvas is the Mutli_Canvas instance 
        - idx is simply the reference
        - width is the width of the element
        - heigh is the heigh of the element
        '''
        SessionNode.__init__(self,name, parent)
        self.multi_canvas = kwargs['multi_canvas']
        self._ignore_path_change = False
        self._initialize(**kwargs)
        self._buildSupport()

    def _initialize(self, **kwargs):
        '''
        Initialise the canvas options
        and the plot model that will then be
        sued to edit plot data
        '''
        self._current_mode = kwargs['Type']
        self.mouse = Mouse(self)

        self.handler = ParameterHandler(
            name = 'Canvas options', 
            parent = self) 
        self.handler.addParameter(
            'Type', kwargs['Type'],
            choices = ['2D', '3D'],
            method = self.switch)
        self.handler.addParameter(
            'Show', True,
            method = self._hideCanvas)
        self.handler.addParameter(
            'Background',  QtGui.QColor('white'),
            method = self._setBackground)
        self.handler.addParameter(
            'Horizontal spacing', 1,
            method = self._setHorizontalSpacing)
        self.handler.addParameter(
            'Vertical spacing', 1,
            method = self._setVerticalSpacing)
        self.handler.addParameter(
            'Config. path', '',
            filetypes = ['JSON (*.json)'],
            mode = 'getFile',
            method = self._configurationPathSet)
        self.handler.addParameter(
            'Actively write config.', False,
            method = self._configurationActiveSet)

        self._plot_root  = SessionNode('Root', None) 
        self._plot_model = PlotModel(self._plot_root, self.multi_canvas)
        self._item_root  = SessionNode('Root', None) 
        self._item_model = PlotModel(self._item_root, self.multi_canvas)

    def artist(self)->Artist2DNode:
        '''
        returns the artist to the asker
        '''
        return self._artist

    def _hideCanvas(self):
        '''
        Hides the canvas from the subplot view
        '''
        self.widget.setVisible(self.handler['Show'])
        self.multi_canvas.update()

    def _buildSupport(self):
        '''
        This will build the Qt support widget, including the 
        transparent scene used to place objects on top and avoid
        excessive redrawing.
        '''
        self.widget = CanvasWidget()
        self.widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.grid_layout)

    def buildGraph(self):
        '''
        build the graph depending on the type
        '''
        try:
            self.para_group.deleteLater()
        except:
            pass

        self._populate()
        self._setBackground()

    def switch(self):
        '''
        Switch from 2D to 3D and vice versa
        '''
        if self._current_mode == self.handler['Type']:
            return 
        if hasattr(self, '_artist'):
            self._artist.disconnect()

        self._artist.removeItems()
        self._model.removeRows(1,self.childCount()-1, self)
        self.plot_widget.deleteLater()
        self.mouse.clear()
        self.buildGraph()
        self._setBackground()
        self._artist.draw()
        self._model.referenceModel()
        self._current_mode = self.handler['Type']

    def _populate(self):
        '''
        General populate method that will check the 
        chosen state and try to redraw all.
        '''

        if self.handler['Type'] == '2D':
            self._populate2D()

        elif self.handler['Type'] == '3D':
            self._populate3D()

    def _populate2D(self):
        '''
        _populate the ui elements on the grid
        '''
        # Set up the plot widget
        self.plot_widget = SimplePlotWidget(self)
        self.plot_widget.setContentsMargins(0, 0, 0, 0)
        self.plot_widget.setViewportMargins(0, 0, 0, 0)
        self.plot_widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Reference the elements
        self.draw_surface = self.plot_widget.getPlotItem()
        self.view = self.draw_surface.getViewBox()
        self.grid_layout.addWidget(self.plot_widget, 1, 1)

        #insert the artist
        self._artist = Artist2DNode(name = '2D Artist', canvas = self)
        self.model().appendRow(self._artist, self)
        self._buildOverlay()
        self._artist.setOverlayElements()
        self.resizeOverlaySpace()

    def _populate3D(self):
        '''
        populate the ui elements on the grid
        '''
        # Set up the plot widget
        self.plot_widget = MyGLViewWidget(self)
        self.plot_widget.setContentsMargins(0, 0, 0, 0)
        self.plot_widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.plot_widget.show()

        # Reference the elements
        self.view = self.plot_widget
        self.grid_layout.addWidget(self.view, 1, 1)
        self.draw_surface = self.view

        #insert the artist
        self._artist = Artist3DNode('3D Artist', canvas = self)
        self.model().appendRow(self._artist, self)
        self._buildOverlay()
        self._artist.setOverlayElements()
        self.resizeOverlaySpace()

        self.plot_widget.setCamera(self._artist.camera)
        self.plot_widget.setLightSource(self._artist.light)
        self._artist.setUpGraphItems()

    def _buildOverlay(self):
        '''
        This method will build an overlay over the current
        plot widget and then make its dimensions fit
        '''
        # Create the QGraphics overlay view
        self._overlay_view = SimplePlotOverlayView()

        # Create the QGraphics scene to go with it
        self._overlay_scene = QtWidgets.QGraphicsScene()
        self._overlay_scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self._overlay_view.setScene(self._overlay_scene)

        #connect it all
        self._overlay_view.setParent(self.plot_widget)

        self.plot_widget.resized_signal.connect(self.resizeOverlaySpace)
        self._overlay_view.sigTakenMouse.connect(self._artist.handleOverlayMouseTaken)
        self._overlay_view.sigReleasedMouse.connect(self._artist.handleOverlayMouseReleased)

    def resizeOverlaySpace(self):
        '''
        The dimensions of the overlay should be adapted at this point
        '''
        self._overlay_view.setFixedSize(self.plot_widget.size())
        self._overlay_view.setSceneRect(
            QtCore.QRectF(0,0,self.plot_widget.size().width(),self.plot_widget.size().height()))

        if hasattr(self, '_artist'):
            self._artist.redrawOverlay()

    def overlayView(self):
        '''
        The getter method for the overlay view
        '''
        return self._overlay_view

    def overlayScene(self):
        '''
        The getter method for the overlay scene
        '''
        return self._overlay_scene

    def _setBackground(self):
        '''
        Set the background of the elements present in the
        current grid layout of the canvas
        '''
        for i in range(self.grid_layout.count()):
            if hasattr(self.grid_layout.itemAt(i).widget(), 'setBackground'):
                self.grid_layout.itemAt(i).widget().setBackground(self.handler['Background'])

    def _setVerticalSpacing(self):
        self.grid_layout.setVerticalSpacing(
            self.handler['Vertical spacing'])

    def _setHorizontalSpacing(self):
        self.grid_layout.setHorizontalSpacing(
            self.handler['Horizontal spacing'])

    def _configurationPathSet(self):
        '''
        Checks what to do with the cofiguration path
        This will be usefull when reloading graphs and
        saving their visual state and setting the default
        '''
        if os.path.exists(self.handler['Config. path']) and not self._ignore_path_change:
            self._ignore_path_change = True
            temp_path = self.handler['Config. path']
            self.loadFromFile(self.handler['Config. path'])
            self.handler.items['Config. path'].updateValue(temp_path, False)
            self._ignore_path_change = False
        
    def _configurationActiveSet(self):
        '''
        This will tell the model to either follow the
        changes of the active configuration and write them 
        on file or not
        '''
        if self.handler['Actively write config.']:
            self.model().dataChanged.connect(self._saveToCurrent)
        else:
            try:
                self.model().dataChanged.disconnect(self._saveToCurrent)
            except:
                pass

    def _saveToCurrent(self):
        '''
        Saves to the current file
        '''
        self.saveToFile(self.handler['Config. path'])

    def _manageDefaultConfiguration(self):
        '''
        This method will have a look if the default configuration is present
        for this Canavas type and then generate it if need be
        '''
        path_default  = os.path.sep.join(
            os.path.dirname(__file__).split(os.path.sep)[:-1]
            + ['ressources'] + ['settings'] + ['canvas']
            + ['default'] + [self.handler['Type']+'_canvas.json'])
        
        if not os.path.exists(path_default):
            self.generateDefaultConfiguration()

        path_user  = os.path.sep.join(
            os.path.dirname(__file__).split(os.path.sep)[:-1]
            + ['ressources'] + ['settings'] + ['canvas']
            + ['user_defined'] + [self.handler['Type']+'_canvas.json'])
        
        if not os.path.exists(path_user):
            self.generateUserConfiguration()

        self.handler['Config. path'] = path_user

    def generateDefaultConfiguration(self):
        '''
        Saves the general default configuration for the plot 
        type that we ghave here. Note that the default
        configuration gets generated once on the first launch 
        and is then fixed
        '''
        path_default  = os.path.sep.join(
            os.path.dirname(__file__).split(os.path.sep)[:-1]
            + ['ressources'] + ['settings'] + ['canvas']
            + ['default'] + [self.handler['Type']+'_canvas.json'])

        self.saveToFile(path_default)

    def generateUserConfiguration(self):
        '''
        Saves the current configuration as the user configuration 
        to be used for all future plots. This can be usefull if
        somone like all th ebackgrounds to be black for example
        '''
        path_user  = os.path.sep.join(
            os.path.dirname(__file__).split(os.path.sep)[:-1]
            + ['ressources'] + ['settings'] + ['canvas']
            + ['user_defined'] + [self.handler['Type']+'_canvas.json'])

        self.saveToFile(path_user)
        self.handler['Config. path'] = path_user

    def saveConfiguration(self):
        '''
        Saves the configuration to file 
        while the path depends on the type
        '''
        path_external  = QtWidgets.QFileDialog.getSaveFileName(
            None, 'Set the output file', '', 'JSON (*.json)')[0]

        if not path_external == '':
            self.saveToFile(path_external)
            self.handler['Config. path'] = path_external

    def loadConfiguration(self):
        '''
        Loads a configuration
        '''
        path_external  = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Set the output file', '', 'JSON (*.json)')[0]

        if not path_external == '':
            self.handler['Config. path'] = path_external

    def loadDefaultConfiguration(self):
        '''
        Loads the default user configuration to clean 
        all current editing
        '''
        path_user  = os.path.sep.join(
            os.path.dirname(__file__).split(os.path.sep)[:-1]
            + ['ressources'] + ['settings'] + ['canvas']
            + ['user_defined'] + [self.handler['Type']+'_canvas.json'])

        self.handler['Config. path'] = path_user

    def setHoverButtons(self, button_list):
        '''
        Set up all the hover button functionalities
        '''
        button_list[0].setVisible(True)
        button_list[0].setText("")
        button_list[0].setIcon(QtGui.QIcon(":/file-download.svg"))
        button_list[0].clicked.connect(self.saveConfiguration)
        button_list[0].setToolTip("Save configuration")

        button_list[1].setVisible(True)
        button_list[1].setText("")
        button_list[1].setIcon(QtGui.QIcon(":/file-upload.svg"))
        button_list[1].clicked.connect(self.loadConfiguration)
        button_list[1].setToolTip("Load configuration")

        button_list[2].setVisible(True)
        button_list[2].setText("")
        button_list[2].setIcon(QtGui.QIcon(":/reload.svg"))
        button_list[2].clicked.connect(self.loadDefaultConfiguration)
        button_list[2].setToolTip("Reset configuration")
