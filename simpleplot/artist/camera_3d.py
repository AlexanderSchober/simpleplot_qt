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

import numpy as np
from pyrr import Matrix44, Vector3
from pyrr.vector3 import cross, length, normalise

from .camera import Camera


class Camera3D(Camera):
    """
    This class will handle the view and projection of the 
    opengl view and then process its matrices
    """

    def __init__(self, canvas):
        super(Camera3D, self).__init__(canvas)

    def _initValues(self) -> None:
        """
        Initialize the default values of 
        the parameters and run the first
        matrix generation
        """
        self._ratio = 2

    def _initNode(self) -> None:
        """
        Initialize the parameters node
        so that the setup is complete
        """
        self.addParameter(
            'Mode', 'Perspective',
            choices=['Perspective', 'Orthogonal'],
            method=self._buildMVP)

        self.addParameter(
            'Center position', [0.0, 0.0, 0.0],
            names=['x', 'y', 'z'],
            method=self._buildMVP)

        self.addParameter(
            'Camera position', [10., 45., 45.],
            names=['Distance', 'azimuthal', 'longitudinal'],
            method=self._buildMVP)

        self.addParameter(
            'Field of View', 60.,
            method=self._buildMVP)

        self.addParameter(
            'Z near', 0.1,
            method=self._buildMVP)

        self.addParameter(
            'Z far', 100.,
            method=self._buildMVP)

    def setRatio(self, ratio: float) -> None:
        """
        Allows the projection matrix to take into account 
        the difference of height and width of the view field

        Parameters:
        -------------------
        ratio : float
            The ratio to set
        """
        self._ratio = ratio
        self._buildMVP()

    def zoom(self, ratio: float, delta: float) -> None:
        """
        Proceed with the zoom method
        :param ratio:
        :param delta:
        :return: None
        """
        temp = self['Camera position']
        temp[0] = round(temp[0] * ratio ** delta, 4)
        self['Camera position'] = temp

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
        x_factor = 360. / self.parent().view.contextClass().context().viewport[3]
        y_factor = 360. / self.parent().view.contextClass().context().viewport[2]

        self.items['Camera position'].updateValue([
            self['Camera position'][0],
            (self['Camera position'][1] - diff_x * x_factor) % 360,
            np.clip(self['Camera position'][2] - diff_y * y_factor, 0.1, 179.9)],
            method=False)

        self._buildMVP()

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
        d, theta, gamma = self['Camera position']
        theta = np.deg2rad(theta)
        gamma = np.deg2rad(gamma)
        center_position = Vector3(self['Center position'])
        camera_position = (center_position + d * Vector3([
            np.cos(theta) * np.sin(gamma),
            np.sin(theta) * np.sin(gamma),
            np.cos(gamma)]))
        x_scale = (length(center_position - camera_position)
                   * 2. * np.tan(0.5 * self['Field of View'] * np.pi / 180.)) / width

        z_vec = Vector3([0, 0, 1])
        x_vec = normalise(cross(z_vec, center_position - camera_position))
        y_vec = normalise(cross(x_vec, z_vec))

        temp = (
                center_position
                + x_vec * x_scale * diff_x
                + y_vec * x_scale * diff_y
                + z_vec * x_scale * 0)

        self['Center position'] = (np.round(np.array(temp), decimals=4)).tolist()

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
        d, theta, gamma = self['Camera position']
        theta = np.deg2rad(theta)
        gamma = np.deg2rad(gamma)
        center_position = Vector3(self['Center position'])
        camera_position = (center_position + d * Vector3([
            np.cos(theta) * np.sin(gamma),
            np.sin(theta) * np.sin(gamma),
            np.cos(gamma)]))
        x_scale = (
                          length(center_position - camera_position)
                          * 2. * np.tan(0.5 * self['Field of View'] * np.pi / 180.)) / width

        z_vec = Vector3([0, 0, 1])
        x_vec = normalise(cross(z_vec, center_position - camera_position))
        y_vec = normalise(cross(x_vec, z_vec))

        temp = (
                center_position
                + x_vec * x_scale * diff_x
                + y_vec * x_scale * 0
                + z_vec * x_scale * diff_y)

        self['Center position'] = (np.round(np.array(temp), decimals=4)).tolist()

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
        d, theta, gamma = self['Camera position']
        theta = np.deg2rad(theta)
        gamma = np.deg2rad(gamma)
        x_y_direction = Vector3([
            np.cos(theta) * np.sin(gamma), np.sin(theta) * np.sin(gamma), 0])
        center_position = Vector3(self['Center position'])
        camera_position = (center_position + d * Vector3([
            np.cos(theta) * np.sin(gamma),
            np.sin(theta) * np.sin(gamma),
            np.cos(gamma)]))

        camera_up = Vector3([0, 0, length(x_y_direction)]) - np.cos(gamma) * normalise(x_y_direction)

        self.mat_look_at = Matrix44.look_at(
            camera_position,
            center_position,
            camera_up)

    def _buildMProjection(self):
        """
        Build the projection matrix
        """
        if self['Mode'] == 'Perspective':
            self.mat_projection = Matrix44.perspective_projection(
                self['Field of View'],
                self._ratio,
                self['Z near'],
                self['Z far'])
        else:
            self.mat_projection = Matrix44.orthogonal_projection(
                -self['Camera position'][0],
                self['Camera position'][0],
                -self['Camera position'][0] / self._ratio,
                self['Camera position'][0] / self._ratio,
                self['Z near'],
                self['Z far']
            )

    def _buildVecView(self):
        """
        Build the projection matrix
        """
        d, theta, gamma = self['Camera position']
        theta = np.deg2rad(theta)
        gamma = np.deg2rad(gamma)
        center_position = Vector3(self['Center position'])
        self.vec_view_pos = (center_position + d * Vector3([
            np.cos(theta) * np.sin(gamma),
            np.sin(theta) * np.sin(gamma),
            np.cos(gamma)]))

    def getDict(self) -> dict:
        """
        Return the dictionary of camera elements
        """
        ret_dict = {'projection_mat': self.mat_projection,
                    'view_mat': self.mat_look_at,
                    'center_pos': np.array(self['Center position']),
                    'view_pos': self.vec_view_pos}
        return ret_dict
