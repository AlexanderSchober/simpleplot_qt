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
from typing import List

from pyrr import Vector3, Matrix44

from simpleplot.models.parameter_class import ParameterHandler


class Camera(ParameterHandler):
    """
    This is the subclass that will handle the common
    methods between the 2d and 3d camera
    """

    def __init__(self, canvas):
        super(Camera, self).__init__('Camera', canvas)

        self.mat_look_at = Matrix44.identity()
        self.vec_view_pos = Vector3([0, 0, 0])
        self.mat_projection = Matrix44.identity()

        self._initValues()
        self._initNode()
        self.__initCommonNode()
        self._buildMVP()

    def _initNode(self) -> None:
        """
        Initialize the parameters node
        so that the setup is complete
        """
        pass

    def __initCommonNode(self) -> None:
        """
        Initialize the common parameter node.
        """
        self.addParameter(
            'Mouse position', [0.0, 0.0],
            names=['x', 'y'])

        self.addParameter(
            'Screen size', [0.0, 0.0],
            names=['x', 'y'])

    def _initValues(self) -> None:
        """
        Initialize the default values of
        the parameters and run the first
        matrix generation
        """
        pass

    def setRatio(self, ratio: float) -> None:
        """
        Placeholder
        """
        self._buildMVP()

    def setMousePos(self, x: float = 0, y: float = 0) -> None:
        """
        Set the mouse position in pixel. This will also allow other
        classes the access this position.
        :param x: float, Mouse position on the canvas (pixels)
        :param y: float, Mouse position on the canvas (pixels)
        :return: None
        """
        self['Mouse position'] = [x, y]

    def setScreenSize(self, x: float = 0, y: float = 0) -> None:
        """
        Set the mouse position in pixel. This will also allow other
        classes the access this position.
        :param x: float, Mouse position on the canvas (pixels)
        :param y: float, Mouse position on the canvas (pixels)
        :return: None
        """
        self['Screen size'] = [x, y]

    def getPixelScreenValue(self, x: int = None, y: int = None) -> List[float]:
        """
        This will return a position on the screen from
        a given pixel position. This can be useful
        to draw invariant positions
        :param x: int, the x position (negative values start from max)
        :param y: int, the y position (negative values start from max)
        :return: List[float]
        """
        size = self['Screen size']

        # process x
        if x is not None:
            pos_x = x if x >= 0 else size[0] + x
            out_x = (pos_x / size[0]) * 2. - 1 if size[0] != 0 else 0.
            if y is None:
                return out_x

        # process y
        if y is not None:
            pos_y = y if y >= 0 else size[1] + y
            out_y = (pos_y / size[1]) * 2. - 1 if size[1] != 0 else 0.
            if x is None:
                return out_y
        return [out_x,out_y]

    def getPixelSize(self) -> List[float]:
        """
        This will return a position on the screen from
        a given pixel position. This can be useful
        to draw invariant positions
        :return: List[float]
        """
        size = self['Screen size']

        return [
            2. / size[0] if size[0] != 0 else 0,
            2. / size[1] if size[1] != 0 else 0
        ]

    def zoom(self, ratio: float = 0, delta: float = 0) -> None:
        """
        This function will handle the zooming of the
        openGl view and then reprocess the matrices

        Parameters:
        -------------------
        ratio : float
            The speed at which the zoom occurs
        delta : float
            The amount of zoom
        """
        pass

    def pan(self, diff_x: float, diff_y: float) -> None:
        """
        This function will handle the panning of the
        openGl view and then reprocess the matrices

        Parameters:
        -------------------
        diff_x : float
            The x difference on screen
        diff_y : float
            The y difference on screen
        """
        pass

    def moveXY(self, diff_x: float, diff_y: float, width: float) -> None:
        """
        This function will handle the panning of the
        openGl view and then reprocess the matrices

        Parameters:
        -------------------
        diff_x : float
            The x difference on screen
        diff_y : float
            The y difference on screen
        """
        pass

    def moveXZ(self, diff_x: float, diff_y: float, width: float) -> None:
        """
        This function will handle the panning of the
        openGl view and then reprocess the matrices

        Parameters:
        -------------------
        diff_x : float
            The x difference on screen
        diff_y : float
            The y difference on screen
        """
        pass

    def _buildMVP(self):
        """
        Build the matrices that will be the
        injected as uniforms in all vertex
        shaders later on
        """
        self._buildVecView()
        self.buildMView()
        self._buildMProjection()
        self.parent().view.contextClass().setMVP()

    def buildMView(self):
        """
        Build the view matrix
        """
        self.mat_look_at = Matrix44.identity()

    def _buildMProjection(self):
        """
        Build the projection matrix
        """
        self.mat_projection = Matrix44.identity()

    def _buildVecView(self):
        """
        Build the projection matrix
        """
        self.vec_view_pos = Vector3([0, 0, 0])

    def getDict(self) -> dict:
        """
        Return the dictionary of camera elements
        """
        ret_dict = {}
        return ret_dict
