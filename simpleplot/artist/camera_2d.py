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
from pyrr import Matrix44, Vector3

from .camera import Camera


class Camera2D(Camera):
    """
    This class will handle the view and projection of the
    opengl view and then process its matrices
    """

    def __init__(self, canvas):
        super(Camera2D, self).__init__(canvas)

    def _initNode(self) -> None:
        """
        Initialize the parameters node
        so that the setup is complete
        """
        self.addParameter(
            'Camera x range', [0.0, 1.0],
            names=['x min', 'x max'],
            method=self._buildMVP)

        self.addParameter(
            'Camera y range', [0.0, 1.0],
            names=['y min', 'y max'],
            method=self._buildMVP)

        self.addParameter(
            'Z near', -100,
            method=self._buildMVP)

        self.addParameter(
            'Z far', 100.,
            method=self._buildMVP)

        self.addParameter(
            'Move Factor', 1,
            method=self._buildMVP)

        self.addParameter(
            'Natural move', True,
            method=self._buildMVP)

        self.addParameter(
            'Zoom follow mouse', False,
            method=self._buildMVP)

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
        mouse_pos = self['Mouse position']
        screen_size = self['Screen size']
        x_corners = self['Camera x range']
        y_corners = self['Camera y range']

        if self['Zoom follow mouse']:
            cursor_pos = [
                mouse_pos[0] / screen_size[0] * (x_corners[1] - x_corners[0]) + x_corners[0],
                (screen_size[1] - mouse_pos[1]) / screen_size[1] * (y_corners[1] - y_corners[0]) + y_corners[0],
            ]
        else:
            cursor_pos = [
                0.5 * (x_corners[1] - x_corners[0]) + x_corners[0],
                0.5 * (y_corners[1] - y_corners[0]) + y_corners[0],
            ]

        x_range = (x_corners[1] - x_corners[0]) * ratio ** delta
        y_range = (y_corners[1] - y_corners[0]) * ratio ** delta

        self.items['Camera x range'].updateValue(
            [cursor_pos[0] - x_range / 2,
             cursor_pos[0] + x_range / 2],
            method=False)
        self.items['Camera y range'].updateValue(
            [cursor_pos[1] - y_range / 2,
             cursor_pos[1] + y_range / 2],
            method=False)

        self.parent().view.contextClass().setGraphItemsUpdatable()
        self._buildMVP()

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
        x_corners = self['Camera x range']
        y_corners = self['Camera y range']
        x_range = (x_corners[1] - x_corners[0])
        y_range = (y_corners[1] - y_corners[0])
        screen_size = self['Screen size']

        direction = -1 if self['Natural move'] else 1
        direction *= self['Move Factor']

        self.items['Camera x range'].updateValue(
            [x_corners[0] + direction * x_range * diff_x / screen_size[0],
             x_corners[1] + direction * x_range * diff_x / screen_size[0]],
            method=False)
        self.items['Camera y range'].updateValue(
            [y_corners[0] - direction * y_range * diff_y / screen_size[1],
             y_corners[1] - direction * y_range * diff_y / screen_size[1]],
            method=False)

        self.parent().view.contextClass().setGraphItemsUpdatable()
        self._buildMVP()

    def moveXY(self, diff_x: float, diff_y: float, width: float) -> None:
        """
        This function will handle the scaling of the ranges

        Parameters:
        -------------------
        diff_x : float
            The x difference on screen
        diff_y : float
            The y difference on screen
        """
        screen_size = self['Screen size']
        x_corners = self['Camera x range']
        y_corners = self['Camera y range']
        x_range = (x_corners[1] - x_corners[0])
        y_range = (y_corners[1] - y_corners[0])

        self.items['Camera x range'].updateValue(
            [x_corners[0] - x_range * diff_x / screen_size[0],
             x_corners[1] + x_range * diff_x / screen_size[0]],
            method=False)
        self.items['Camera y range'].updateValue(
            [y_corners[0] + y_range * diff_y / screen_size[1],
             y_corners[1] - y_range * diff_y / screen_size[1]],
            method=False)

        self.parent().view.contextClass().setGraphItemsUpdatable()
        self._buildMVP()

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
        self.mat_projection = Matrix44.orthogonal_projection(
            self['Camera x range'][0], self['Camera x range'][1],
            self['Camera y range'][0], self['Camera y range'][1],
            self['Z near'], self['Z far']
        )

    def _buildVecView(self):
        """
        Build the projection matrix
        """
        self.vec_view_pos = Vector3([0, 0, 0])

    def getDict(self) -> dict:
        """
        Return the dictionary of camera elements
        """
        ret_dict = {'projection_mat': self.mat_projection,
                    'view_mat': self.mat_look_at,
                    'view_pos': self.vec_view_pos}
        return ret_dict
