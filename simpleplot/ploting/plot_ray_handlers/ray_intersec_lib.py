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

def rayTriangleIntersection(ray_near, ray_dir, v123):
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

    return True, linPlaneCollision([v1,v2,v3], ray_dir, ray_near)

def linPlaneCollision(planePoints, rayDirection, rayPoint, epsilon=1e-6):

    planeNormal = np.cross(planePoints[1] - planePoints[0], planePoints[2]- planePoints[0])
    planeNormal = planeNormal/np.linalg.norm(planeNormal)
    ndotu       = planeNormal.dot(rayDirection)

    if abs(ndotu) < epsilon:
        raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - planePoints[0]
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoints[0]
    return Psi
    
def closestPointOnLine(a, b, p):
    ap = p-a
    ab = b-a
    result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    return np.linalg.norm(result - p)

def checkBoundingBox(ray, data_handler):
    '''
    Check if the bounding box is hit
    '''
    bounding_box = data_handler.getBoundingBox()

    intersec = []
    for i in range(bounding_box.shape[0]):
        val  = rayTriangleIntersection(
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

def retrievePositionSurface(ray, intersec, data_handler, mode):
    '''
    Check if the bounding box is hit
    '''
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
        
    if mode in ('Fast','Mixed'): 
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
            distance[i] = closestPointOnLine(ray[1], ray[0],points[i])

        idx = np.argpartition(distance, 3)

        triangle = np.array([
                points[idx[0]],
                points[idx[1]],
                points[idx[2]]])
        test = rayTriangleIntersection(ray[0], ray[1], triangle)

        if test[1] is None and mode == 'Mixed':
            for face in vert_data[1][flat_index]:
                triangle    = vert_data[0][np.array([face[0],face[1],face[2]])]
                test        = rayTriangleIntersection(ray[0], ray[1], triangle)
                if test[0]:
                    return test[1]
        else:
            return test[1]
        
    if mode == 'Precise':
        points = []
        for face in vert_data[1][flat_index]:
            triangle    = vert_data[0][np.array([face[0],face[1],face[2]])]
            z_values    = [triangle[i,2]>minima[2] and triangle[i,2]<maxima[2] for i in range(3)]
            if any(z_values):
                test        = rayTriangleIntersection(ray[0], ray[1], triangle)
                if test[0]:
                    points.append(test[1])

        if not len(points) == 0:
            points_scalar = np.array([np.linalg.norm(point-ray[0]) for point in points ])
            return points[np.argmin(points_scalar)]
        else:
            return None

