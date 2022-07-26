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

from typing import Union
import numpy as np

from simpleplot.artist.camera_2d import Camera2D
from simpleplot.artist.camera_3d import Camera3D
from simpleplot.artist.space import SpaceRepresentation


class InteractionHandler(object):
    
    def __init__(self, canvas, context) -> None:
        self._canvas = canvas
        self._context = context
        self._camera = None
        self._space = None
        self._current_interaction_scheme = None
        self._interaction_schemes = {
            'InteractionSchemeZoom': InteractionSchemeZoom
        }
        
        self.setCurrentScheme('InteractionSchemeZoom')
        
    def setCurrentScheme(self, scheme_name: str) -> None:
        """
        Set the canmera as the local item
        """
        self._current_interaction_scheme = self._interaction_schemes[scheme_name](self._canvas, self._context)
        
        if self._camera is not None:
            self._current_interaction_scheme.setCamera(self._camera)
            
        if self._space is not None:
            self._current_interaction_scheme.setSpace(self._space)
        
    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._camera = camera
        
        if self._current_interaction_scheme is not None:
            self._current_interaction_scheme.setCamera(self._camera)
            
    def setSpace(self, space: SpaceRepresentation) -> None:
        """
        Set the canmera as the local item
        """
        self._space = space
        
        if self._current_interaction_scheme is not None:
            self._current_interaction_scheme.setSpace(self._space)
        
class InteractionScheme(object):
    
    def __init__(self, canvas, context) -> None:
        self._canvas = canvas
        self._context = context
        
        self._camera = None
        self._space = None
        self._mouse = None
        self._keys = None
        self._is_3d = False
        
        self._mouse = self._canvas.mouse
        self.setCamera(self._context.camera())
        
    def setCamera(self, camera: Union[Camera2D, Camera3D]) -> None:
        """
        Set the canmera as the local item
        """
        self._disconnect()
        self._camera = camera
        if isinstance(self._camera, Camera2D): 
            self._is_3d = False
        else:
            self._is_3d = True
        self._connect()
        
    def setSpace(self, space: SpaceRepresentation) -> None:
        """
        Set the canmera as the local item
        """
        self._disconnect()
        self._space = space
        self._connect()
        
    def _connect(self):
        '''
        Connect the methods between each other
        This needs to be implemented in the respective
        child clases.
        '''
        pass
    
    def _disconnect(self):
        '''
        Connect the methods between each other
        This needs to be implemented in the respective
        child clases.
        '''
        pass
    
    def _selector(self, x, y):
        """
        Manage the ray movement
        """
        # fix the screen
        # screens = QtWidgets.QApplication.instance().screens()
        # num = QtWidgets.QApplication.instance().desktop().sreenNumber(self)
        # ratio = QtGui.QScreen.devicePixelRatio(screens[num])
        # ray = self._context_class.getPickingRay(x * ratio, y * ratio)
        #
        # self._context_class.pickRays()

        # save the new ray and emit ray
        # self.mouse_ray = np.array([self._camera['Camera position'], ray[:3]])
        # self.rayUpdate.emit()
        
    def _contextMenu(self, ev):
        """
        Shift the view
        """
        print('show context menu')
            
class InteractionSchemeZoom(InteractionScheme):
    
    def __init__(self, canvas, context) -> None:
        super().__init__(canvas, context)
        
    def _connect(self):
        '''
        Connect the methods between each other
        This needs to be implemented in the respective
        child clases.
        '''
        if self._is_3d:
            self._mouse.bind('press', self._showAxes, 'show_center', 1)
            self._mouse.bind('release', self._hideAxes, 'hide_center', 1)
            self._mouse.bind('press', self._showAxes, 'show_center', 2)
            self._mouse.bind('release', self._hideAxes, 'hide_center', 2)
            self._mouse.bind('press', self._showAxes, 'show_center', 0)
            self._mouse.bind('release', self._hideAxes, 'hide_center', 0)
        else:
            self._mouse.bind('release', self._resetZoom, 'reset_zoom', 1, False, True)
            
        self._mouse.bind('release', self._contextMenu, 'context', 2, True, True)
        self._mouse.bind('move', self._selector, 'selector', 1)
        self._mouse.bind('drag', self._pan, 'pan', 1)
        self._mouse.bind('drag', self._moveXY, 'shift_xy', 2)
        self._mouse.bind('drag', self._moveXZ, 'shift_yz', 0)
    
    def _disconnect(self):
        '''
        Connect the methods between each other
        This needs to be implemented in the respective
        child clases.
        '''
        if self._is_3d:
            self._mouse.unbind('press', 'show_center')
            self._mouse.unbind('release', 'hide_center')
            self._mouse.unbind('press', 'show_center')
            self._mouse.unbind('release', 'hide_center')
            self._mouse.unbind('press', 'show_center')
            self._mouse.unbind('release', 'hide_center')
        else:
            self._mouse.unbind('release', 'reset_zoom')
            
        self._mouse.unbind('release', 'context')
        self._mouse.unbind('move', 'selector')
        self._mouse.unbind('drag', 'pan')
        self._mouse.unbind('drag', 'shift_xy')
        self._mouse.unbind('drag', 'shift_yz')
        
    def _resetZoom(self):
        """
        Reset the zoom
        """
        self._camera._resetToBounds()

    def _showAxes(self):
        """
        Show the movement ball
        """
        if self._canvas.childFromName('Artist').orientation is not None:
            self._canvas.childFromName('Artist').childFromName('Orientation Axes').drag_on = True
            self._canvas.childFromName('Artist').childFromName('Orientation Axes').setParameters()

    def _hideAxes(self):
        """
        Show the movement ball
        """
        if self._canvas.childFromName('Artist').orientation is not None:
            self._canvas.childFromName('Artist').childFromName('Orientation Axes').drag_on = False
            self._canvas.childFromName('Artist').childFromName('Orientation Axes').setParameters()

    def _pan(self, x, y, drag_start, drag_end):
        """
        This function will handle the panning of the
        openGl view and send it to the camera 
        in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]

        self._camera.pan(diff_x, diff_y)

    def _moveXZ(self, x, y, drag_start, drag_end):
        """
        This function will handle the moving of the
        openGl view in the x and y plane and send 
        it to the camera in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
        self._camera.moveXZ(diff_x, diff_y, self._canvas.plot_widget.width())

    def _moveXY(self, x, y, drag_start, drag_end):
        """
        This function will handle the moving of the
        openGl view in the x and y plane and send 
        it to the camera in charge

        Parameters:
        -------------------
        x : float
            x drag positions
        y : float
            y drag positions
        drag_start : float
            Not used
        drag_end : float
            Not used
        """
        diff_x = x[2] - x[1]
        diff_y = y[2] - y[1]
        self._camera.moveXY(diff_x, diff_y, self._canvas.plot_widget.width())
        

