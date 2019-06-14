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
from ...pyqtgraph.pyqtgraph     import opengl as gl
from ...model.parameter_class   import ParameterHandler 

class SurfaceRayHandler(ParameterHandler): 
    '''
    This will be the main data class purposed
    to be inherited by variations with different
    variations.
    '''
    def __init__(self):
        ParameterHandler.__init__(self,'Ray handler')
        self.pointer_elements = []
        self._initialize()

    def _initialize(self):
        '''
        '''
        self.addParameter(
            'Mode', 'Projection', 
            choices = ['IsoCurve', 'Projection'],
            method = self._dispatchCoordinate)

    def drawGL(self,target):
        self.default_target = target

    def _dispatchCoordinate(self):
        '''
        '''
        if self['Mode'] == 'IsoCurve' and not self.point is None:
            self._isoCurve(self.point[2])
        elif self['Mode'] == 'Projection' and not self.point is None:
            self._dataCurve(self.point[0], self.point[1])

    def _dataCurve(self,x,y):
        '''
        '''
        for element in self.pointer_elements:
            self.default_target.view.removeItem(element)
        self.pointer_elements = []

        data = self.parent()['Data'].getData()
        index_x = np.argmin(np.abs(x-data[0]))
        index_y = np.argmin(np.abs(y-data[1]))

        data_xx = [data[0][index_x] for e in range(data[1].shape[0])]
        data_xy = data[1]
        data_xz = data[2][index_x,:]

        self.pointer_elements.append(
            gl.GLLinePlotItem(
                pos   = np.vstack([data_xx, data_xy, data_xz]).transpose(),
                color = [1,1,1,1],
                width = 3,
                mode  = 'line_strip'))
        self.pointer_elements[-1].setGLOptions('opaque')
        self.default_target.view.addItem(self.pointer_elements[-1])

        data_yx = data[0]
        data_yy = [data[1][index_y] for e in range(data[0].shape[0])]
        data_yz = data[2][:,index_y]

        self.pointer_elements.append(   
            gl.GLLinePlotItem(
                pos = np.vstack([data_yx,data_yy,data_yz]).transpose(),
                color = [1,1,1,1],
                width = 3,
                mode = 'line_strip'))
        self.pointer_elements[-1].setGLOptions('opaque')
        self.default_target.view.addItem(self.pointer_elements[-1])

    def _isoCurve(self,level):
        '''
        '''
        for element in self.pointer_elements:
            self.default_target.view.removeItem(element)
        self.pointer_elements = []

        iso_curves = self.parent()['Data'].getIsocurve(level)
        data    = self.parent()['Data'].getData()
        bounds  = self.parent()['Data'].getBounds()
        x_fac   = (bounds[0][1] - bounds[0][0])
        y_fac   = (bounds[1][1] - bounds[1][0])

        for curve in iso_curves:
            self.pointer_elements.append(
                gl.GLLinePlotItem(
                    pos=np.vstack([
                        [(item[0]-0.5) / (data[2].shape[0]-1) * x_fac + bounds[0][0] for item in curve],
                        [(item[1]-0.5) / (data[2].shape[1]-1) * y_fac + bounds[1][0] for item in curve],
                        [level+0.01 for item in curve]]).transpose(),
                    color = [1,1,1,1],
                    width = 3,
                    mode = 'line_strip'))
            self.pointer_elements[-1].setGLOptions('opaque')
            self.default_target.view.addItem(self.pointer_elements[-1])

    def closestPointOnLine(self, a, b, p):
        ap = p-a
        ab = b-a
        result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
        return np.linalg.norm(result - p)

    def processRay(self, ray):
        '''
        Process an input ray by the 
        canvas widget and perform necessary
        operations
        '''
        temp        = self.parent().childFromName('Surface').draw_items[0].viewTransform().inverted()[0]
        transform   = np.reshape(np.array(temp.data()),(4,4)).transpose()
        new_ray     = [np.dot(transform,np.hstack((e,1)))[:3] for e in ray]
        intersec    = self._checkBoundingBox(new_ray)
        if not intersec is None:
            self.point = self._retrievePosition(new_ray, intersec)
            self._dispatchCoordinate()
        
    def _checkBoundingBox(self, ray):
        '''
        Check if the bounding box is hit
        '''
        data_handler = self.parent().childFromName('Data')
        bounding_box = data_handler.getBoundingBox()

        intersec = []
        for i in range(bounding_box.shape[0]):
            val  = self.rayTriangleIntersection(
                ray[0], ray[1], [
                    bounding_box[i,0],
                    bounding_box[i,1],
                    bounding_box[i,2]])
            if val[0]:
                intersec.append(val[1])

        if len(intersec) == 0:
            return None
        elif len(intersec) == 1:
            intersec.insert(0,ray[0])

        return intersec

    def _retrievePosition(self, ray, intersec):
        '''
        Check if the bounding box is hit
        '''
        data_handler    = self.parent().childFromName('Data')
        vert_data       = data_handler.getMesh()
        data            = data_handler.getData()

        x_step = data[0][1] - data[0][0]
        y_step = data[1][1] - data[1][0]

        intersec = np.array(intersec)

        maxima = [
            np.amax(intersec[:,0])+x_step,
            np.amax(intersec[:,1])+y_step,
            np.amax(intersec[:,2])]

        minima = [
            np.amin(intersec[:,0])-x_step,
            np.amin(intersec[:,1])-y_step,
            np.amin(intersec[:,2])]

        index_x = np.argwhere((data[0] > minima[0])&((data[0] < maxima[0])))[:,0]
        index_y = np.argwhere((data[1] > minima[1])&((data[1] < maxima[1])))[:,0]

        if index_x.shape[0] < 2:
            val = np.argmin(np.abs(data[0] - minima[0]))
            index_x = np.arange(val-1, val + 1)
        if index_y.shape[0] < 2:
            val = np.argmin(np.abs(data[1] - minima[1]))
            index_y = np.arange(val-1, val + 1)

        flat_x_2 = np.arange(index_x[0]*2-2, index_x[-1]*2+2)
        flat_y_1 = np.arange(index_y[0]-1, index_y[-1]+1)

        flat_x_2 = flat_x_2[np.where(flat_x_2>=0)]
        flat_x_2 = flat_x_2[np.where(flat_x_2<data[0].shape[0]*2)]
        flat_y_1 = flat_y_1[np.where(flat_y_1>=0)]
        flat_y_1 = flat_y_1[np.where(flat_y_1<data[1].shape[0])]

        flat_index = np.array([flat_x_2 + e*(data[0].shape[0]-1)*2 for e in index_y])
        flat_index = np.reshape(flat_index,(flat_index.shape[0]*flat_index.shape[1]) )
        flat_index = flat_index[np.where(flat_index<vert_data[1].shape[0])]
            
        points = []
        for face in vert_data[1][flat_index]:
            points.append(face[0])
            points.append(face[1])
            points.append(face[2])
        points = vert_data[0][np.array(list(set(points)))]
        
        ray_norm = np.linalg.norm(ray[1] - ray[0])
        distance = np.zeros(points.shape[0])

        point_vectors = points - ray[0]
        for i in range(distance.shape[0]):
            distance[i] = self.closestPointOnLine(ray[1], ray[0],points[i])

        idx = np.argpartition(distance, 3)

        transform   = np.array([self.parent().childFromName('Surface').draw_items[0].viewTransform().data()[0+i*4:4+i*4]for i in range(4)])
        triangle = np.array([
                np.dot(np.array(points[idx[0]].tolist()+[1]) , transform)[0:3],
                np.dot(np.array(points[idx[1]].tolist()+[1]) , transform)[0:3],
                np.dot(np.array(points[idx[2]].tolist()+[1]) , transform)[0:3]])

        test = self.rayTriangleIntersection(ray[0], ray[1], triangle)
        return test[1]

    def rayTriangleIntersection(self, ray_near, ray_dir, v123):
        """
        Möller–Trumbore intersection algorithm in pure python
        Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
        """
        v1, v2, v3 = v123
        eps = 0.000000001
        edge1 = v2 - v1
        edge2 = v3 - v1
        p_vec = np.cross(ray_dir, edge2)
        det = edge1.dot(p_vec)
        if abs(det) < eps:
            return False, None
        inv_det = 1. / det
        t_vec = ray_near - v1
        u = t_vec.dot(p_vec) * inv_det
        if u < 0. or u > 1.:
            return False, None
        q_vec = np.cross(t_vec, edge1)
        v = ray_dir.dot(q_vec) * inv_det
        if v < 0. or u + v > 1.:
            return False, None

        t = edge2.dot(q_vec) * inv_det
        if t < eps:
            return False, None

        return True, self.linPlaneCollision([v1,v2,v3], ray_dir, ray_near)

    def linPlaneCollision(self, planePoints, rayDirection, rayPoint, epsilon=1e-6):
    
        planeNormal = np.cross(planePoints[1] - planePoints[0], planePoints[2]- planePoints[0])
        planeNormal = planeNormal/np.linalg.norm(planeNormal)
        ndotu       = planeNormal.dot(rayDirection)

        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")
    
        w = rayPoint - planePoints[0]
        si = -planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + planePoints[0]
        return Psi