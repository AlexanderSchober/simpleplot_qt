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

import moderngl
import numpy as np
# General imports
from PyQt5 import QtCore
from pyrr import Matrix44, Vector3

# Personal imports
from ..graphics_geometry.transform_3D import Transform3D


class GraphicsView3D(QtCore.QObject):
    """
    This will be the graphics 3d object that will be 
    used to display the shape according to coordinates
    """
    moved = QtCore.pyqtSignal(list)

    def __init__(self, **opts):
        super().__init__(opts.get('parent', None))

        # Set up the parameters
        self._parameters = {}
        self._parameters['drawFaces'] = True
        self._parameters['drawEdges'] = False
        self._parameters.update(opts)

        # These are the items
        self.__renderer = None
        self.__transform = Transform3D()
        self.__visible = True
        self.__depth_value = 0

        # Prepare the programs
        self._programs = {}
        self._vaos = {}  # vertex array buffers
        self._vbos = {}  # vertex buffer objects
        self._ibos = {}  # index buffer objects

    def setRenderer(self, renderer):
        """ setter for the renderer """
        self.__renderer = renderer

    def renderer(self):
        """ getter for the renderer """
        return self.__renderer

    def context(self) -> moderngl.Context:
        """ getter for the context """
        if self.__renderer is None:
            return None
        return self.__renderer.context()

    def _createProgram(self, name: str, vert_shader: str = None, frag_shader: str = None, geometry_shader: str = None,
                       tess_control_shader: str = None, tess_evaluation_shader: str = None, varyings: tuple = ()):
        """
        This instance will generate the shader
        program with a specific name and 
        the associated vertex and fragment shaders. 
        If none is set the local ones will be used ...

        Parameters:
        ---------------------
        name : str
            The name the program will occupy in the dictionaries
        vert_shader : str
            The vertex shader to be compiled
        frag_shader : str 
            The fragment shader to be compiled
        """
        vert_shader = self._vertexShader() if vert_shader is None else vert_shader
        fragment_shader = self._fragmentShader() if frag_shader is None else frag_shader

        self._programs[name] = self.context().program(
            vertex_shader=vert_shader,
            fragment_shader=fragment_shader,
            geometry_shader=geometry_shader,
            tess_control_shader=tess_control_shader,
            tess_evaluation_shader=tess_evaluation_shader,
            varyings=varyings
        )

        self.setTransformMatrix()

    def _createVBO(self, name: str, *data_sources):
        """
        The vbo creator for a specific shader program. 

        Parameters:
        ---------------------
        name : str
            The name the buffer will occupy in the dictionaries
        *args : [np.arrays]
            Series of numpy arrays that will consist of the data
        """
        if not all([(data_source.shape[0] == data_sources[0].shape[0]) for data_source in data_sources]):
            print("the data sources don't have all the same dims")
            return

        data = np.zeros((
            data_sources[0].shape[0], sum([data_source.shape[1]
                                           for data_source in data_sources])), dtype=np.float32)

        index = 0
        for data_source in data_sources:
            data[:, index:index + data_source.shape[1]] = data_source
            index += data_source.shape[1]

        if name in self._vbos.keys():
            self._vbos[name].orphan(data.flatten().astype('f4').nbytes)
            self._vbos[name].write(data.flatten().astype('f4').tobytes())
        else:
            self._vbos[name] = self.context().buffer(
                data.flatten().astype('f4').tobytes())

    def _createIBO(self, name: str, ibo_array: np.array):
        """
        The ibo creator for a specific shader program. 

        Parameters:
        ---------------------
        name : str
            The name the buffer will occupy in the dictionaries
        ibo_array : np.arrays
            The list of data destined for the ibo
        """
        if name in self._ibos.keys():
            self._ibos[name].orphan(ibo_array.flatten().astype('i4').nbytes)
            self._ibos[name].write(ibo_array.flatten().astype('i4').tobytes())
        else:
            self._ibos[name] = self.context().buffer(
                ibo_array.flatten().astype('i4').tobytes())

    def _createVAO(self, name: str, attr_lists: dict):
        """
        The vao creator for a specific shader program. 

        Parameters:
        ---------------------
        name : str
            The name of the programm that will be used
        attr_lists : dict
            Dictionary of content lists with the keyword
            being used to point towards a vbo definition
        """
        if not name in self._programs.keys():
            print("Program not found for creating the vao")
            return

        self._vaos[name] = self.context().vertex_array(
            self._programs[name],
            [(self._vbos[vbo_name], *attr_lists[vbo_name])
             for vbo_name in attr_lists.keys()],
            self._ibos[name] if name in self._ibos.keys() else None
        )

    def _vertexShader(self) -> str:
        """
        Returns the vertex shader for this particular item
        """
        output = """
            #version 330

            uniform mat4 u_proj_mat;
            uniform mat4 u_view_mat;
            uniform mat4 u_model_mat;
            uniform vec3 u_view_pos;

            uniform vec2 u_light_bool;
            uniform vec3 u_light_pos;
            uniform vec3 u_light_color;

            in vec3 in_vert;
            in vec3 in_norm;
            in vec4 in_color;
            
            out vec3 v_normal;
            out vec4 v_color;

            out float light_active;
            out vec3  light_pos;
            out vec3  view_pos;
            out vec3  frag_pos;
            out vec3  light_color;

            void main() {
                v_normal        = in_norm;
                v_color         = in_color;

                light_active    = u_light_bool[0];
                frag_pos        = vec3(in_vert);
                light_pos       = vec3(u_light_pos);
                view_pos        = vec3(u_view_pos);
                light_color     = vec3(u_light_color);
                if (u_light_bool[1]==1){
                    light_pos = vec3(u_proj_mat*u_view_mat*u_model_mat*vec4(light_pos, 1.0));
                }
                gl_Position = u_proj_mat*u_view_mat*u_model_mat*vec4(in_vert, 1.0);
            }"""
        return output

    def _fragmentShader(self) -> str:
        """
        Returns the fragment shader for this particular item
        """
        output = """
            #version 330

            in vec3 v_normal;
            in vec4 v_color;

            in float light_active;
            in vec3 light_pos;
            in vec3 view_pos;
            in vec3 frag_pos;
            in vec3 light_color;

            out vec4 f_color;
            void main() {

                if (light_active == 1){
                    float ambientStrength = 0.1;
                    vec3 ambient = ambientStrength * light_color;
                    vec3 norm = normalize(v_normal);
                    vec3 lightDir = normalize(light_pos - frag_pos);  
                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = diff * light_color;

                    float specularStrength = 0.5;
                    vec3 viewDir = normalize(view_pos - frag_pos);
                    vec3 reflectDir = reflect(-lightDir, norm);
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 256);
                    vec3 specular = specularStrength * spec * light_color;
                    
                    vec3 result = (ambient + diffuse + specular) * vec3(v_color);
                    f_color = vec4(result, v_color[3]);
                } else {
                    f_color = v_color;
                }

            }"""

        return output

    def setUniforms(self, **kwargs) -> None:
        """
        Set the uniforms in the programs

        Parameters:
        ---------------------
        kwargs : dict
            A dictionary of names associated to nunmpy arrays
        """
        for key in kwargs.keys():
            for program_name in self._programs.keys():
                uniform = self._programs[program_name].get(key, None)
                if not uniform is None:
                    uniform.write(kwargs[key].flatten().astype(dtype='f4').tobytes())

    def setMVP(self, projection_mat: Matrix44 = Matrix44(), view_mat: Matrix44 = Matrix44(),
               center_pos: Vector3 = Vector3(), view_pos: Vector3 = Vector3()) -> None:
        """
        Set the projection and view matrices

        Parameters:
        ---------------------
        projection_mat : Matrix44
            The world projection matric for open gl 
        view_mat : Matrix44
            The world view matric in opengl
        view_pos : Vector3
            The position of the camera in the real world
        center_pos : Vector3
            The position of the center
        """
        for program_name in self._programs.keys():
            u_proj_mat = self._programs[program_name].get('u_proj_mat', None)
            u_view_mat = self._programs[program_name].get('u_view_mat', None)
            u_view_pos = self._programs[program_name].get('u_view_pos', None)
            u_norm_mat = self._programs[program_name].get('u_norm_mat', None)
            u_center_pos = self._programs[program_name].get('u_center_pos', None)

            if u_proj_mat is not None:
                u_proj_mat.write(projection_mat.astype(dtype='f4').tobytes())
            if u_view_mat is not None:
                u_view_mat.write(view_mat.astype(dtype='f4').tobytes())
            if u_view_pos is not None:
                u_view_pos.write(view_pos.astype(dtype='f4').tobytes())
            if u_center_pos is not None:
                u_center_pos.write(center_pos.astype(dtype='f4').tobytes())
            if u_norm_mat is not None:
                if view_mat == np.zeros((4, 4)):
                    return
                u_norm_mat.write(np.transpose(np.linalg.inv(view_mat[:3, :3])).astype(dtype='f4').tobytes())

    def setLight(self, light_bool: np.array = np.zeros(2), light_pos: Vector3 = Vector3(),
                 light_color: Vector3 = Vector3()) -> None:
        """
        Set the lightening related matrices

        Parameters:
        ---------------------
        light_bool : Matrix44
            The light booleans 
        light_pos : Matrix44
            The light element position
        light_color : Vector3
            The color property for the lightning
        """
        for program_name in self._programs.keys():
            u_light_bool = self._programs[program_name].get('u_light_bool', None)
            u_light_pos = self._programs[program_name].get('u_light_pos', None)
            u_light_color = self._programs[program_name].get('u_light_color', None)

            if not u_light_bool is None:
                u_light_bool.write(light_bool.astype(dtype='f4').tobytes())
            if not u_light_pos is None:
                u_light_pos.write(light_pos.astype(dtype='f4').tobytes())
            if not u_light_color is None:
                u_light_color.write(light_color.astype(dtype='f4').tobytes())

    def setTransformMatrix(self, transform: Matrix44 = Matrix44().identity()) -> None:
        """
        Set the geometric transformation matrix

        Parameters:
        ---------------------
        transform : Matrix44
            The transformation matrix in 3d space
        """
        for program_name in self._programs.keys():
            u_model_mat = self._programs[program_name].get('u_model_mat', None)
            if not u_model_mat is None:
                u_model_mat.write(transform.astype(dtype='f4').tobytes())

    def setDepthValue(self, value):
        """
        Sets the depth value of this item. Default is 0.
        This controls the order in which items are drawn--those with a greater depth value will be drawn later.
        Items with negative depth values are drawn before their parent.
        (This is analogous to QGraphicsItem.zValue)
        The depthValue does NOT affect the position of the item or the values it imparts to the GL depth buffer.
        """
        self.__depth_value = value

    def depthValue(self):
        """Return the depth value of this item. See setDepthValue for more information."""
        return self.__depth_value

    def setTransform(self, tr):
        """Set the local transform for this object.
        Must be a :class:`Transform3D <pyqtgraph.Transform3D>` instance. This transform
        determines how the local coordinate system of the item is mapped to the coordinate
        system of its parent."""
        self.__transform = Transform3D(tr)
        self.update()

    def resetTransform(self):
        """Reset this item's transform to an identity transformation."""
        self.__transform.setToIdentity()
        self.update()

    def applyTransform(self, tr, local):
        """
        Multiply this object's transform by *tr*. 
        If local is True, then *tr* is multiplied on the right of the current transform::
        
            newTransform = transform * tr
            
        If local is False, then *tr* is instead multiplied on the left::
        
            newTransform = tr * transform
        """
        if local:
            self.setTransform(self.transform() * tr)
        else:
            self.setTransform(tr * self.transform())

    def transform(self):
        """Return this item's transform object."""
        return self.__transform

    def viewTransform(self):
        """Return the transform mapping this item's local coordinate system to the 
        view coordinate system."""
        tr = self.__transform
        p = self
        while True:
            p = p.parentItem()
            if p is None:
                break
            tr = p.transform() * tr
        return Transform3D(tr)

    def initializeGL(self):
        """
        Called after an item is added to a GLViewWidget. 
        The widget's GL context is made current before this method is called.
        (So this would be an appropriate time to generate lists, upload textures, etc.)
        """
        pass

    def hide(self):
        """Hide this item. 
        This is equivalent to setVisible(False)."""
        self.setVisible(False)

    def show(self):
        """Make this item visible if it was previously hidden.
        This is equivalent to setVisible(True)."""
        self.setVisible(True)

    def setVisible(self, vis):
        """Set the visibility of this item."""
        self.__visible = vis
        self.update()

    def visible(self):
        """Return True if the item is currently set to be visible.
        Note that this does not guarantee that the item actually appears in the
        view, as it may be obscured or outside of the current view area."""
        return self.__visible

    def paint(self):
        """
        Called by the GLViewWidget to draw this item.
        It is the responsibility of the item to set up its own modelview matrix,
        but the caller will take care of pushing/popping.
        """
        pass

    def update(self):
        """
        Indicates that this item needs to be redrawn, and schedules an update 
        with the view it is displayed in.
        """
        if self.__renderer is None:
            return
        self.__renderer.render()

    def mapToParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.map(point)

    def mapFromParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)

    def mapToView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.map(point)

    def mapFromView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)
