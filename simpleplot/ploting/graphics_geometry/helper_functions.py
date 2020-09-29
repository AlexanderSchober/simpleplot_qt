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
import math

# FIX ME TO BE UPDATED
def tubeCircleVertices(positions:np.array = np.array([[0,0,0],[1,1,1]]), width:float = 0.1, precision: int = 10, close:bool = True)->np.array:
    '''
    Get vertices for drawing the tub elements along positions

    Parameters:
    -------------------
    position : np.array
        Point positions in 3 dimensions
    width : float
        The width of the tube
    precision : int
        The number of subdivisions around the tube
    close : bool
        This boolean flag will determine if the direction of the last
        circle should be alligned with the direction of the first or not
    '''
    circle_vertices = np.zeros((positions.shape[0], precision+1, 3))
    for j in range(1,positions.shape[0]-1):
        vec = ((positions[j]-positions[j-1]) / np.linalg.norm(positions[j]-positions[j-1]) + (positions[j+1]-positions[j]) / np.linalg.norm(positions[j+1]-positions[j]))/2
        new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
        new_y = np.array([vec[1],-vec[0],0])

        for i in range(precision+1):
            circle_vertices[j,i,:] = (
                width * math.cos(2. * math.pi * (i/precision)) * new_x
                + width * math.sin(2. * math.pi * (i/precision)) * new_y
                +positions[j])

    #first circle
    if close:
        vec = ((positions[0]-positions[-1]) / np.linalg.norm(positions[0]-positions[-1]) + (positions[1]-positions[0]) / np.linalg.norm(positions[1]-positions[0]))/2
        new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
        new_y = np.array([vec[1],-vec[0],0])

    else:
        vec = (positions[1]-positions[0]) / np.linalg.norm(positions[1]-positions[0])
        new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
        new_y = np.array([vec[1],-vec[0],0])

    for i in range(precision+1):
        circle_vertices[0,i,:] = (
            width * math.cos(2 * math.pi * (i/precision)) * new_x
            + width * math.sin(2 * math.pi * (i/precision)) * new_y
            +positions[0])

    #last circle
    if close:
        vec = ((positions[-1]-positions[-2]) / np.linalg.norm(positions[-1]-positions[-2]) + (positions[0]-positions[-1]) / np.linalg.norm(positions[0]-positions[-1]))/2
        new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
        new_y = np.array([vec[1],-vec[0],0])

    else:
        vec = (positions[-1]-positions[-2]) / np.linalg.norm(positions[-1]-positions[-2]) 
        new_x = np.array([0,0,np.linalg.norm([vec[0], vec[1], 0])])
        new_y = np.array([vec[1],-vec[0],0])

    for i in range(precision+1):
        circle_vertices[-1,i,:] = (
            width * math.cos(2 * math.pi * (i/precision)) * new_x
            + width * math.sin(2 * math.pi * (i/precision)) * new_y
            +positions[-1])

    return circle_vertices

def createTubes(positions:np.array = np.array([[0,0,0],[1,1,1]]), width:float = 0.1, precision: int = 10, close:bool = True, connect:list([bool,bool]) = [False, False])->list([np.array,np.array]):
    '''
    This function will create a triangular mesh of points 
    that will be mostly used to project onto spheres

    Parameters:
    -------------------
    positions : np.array(2*n,3)
        The point positions. The points will be used in pairs
        to allow for segment formation in a single go.
    width : float
        Set the float number of the width
    precision : int
        This is the subdicions precision of the tube
    close : bool
        This is the closing of the tube by appending the 
        triangular fans
    connect : list([bool,bool])
        The first boolean indicates if the elements have to be
        interconnected. And the second bool specifies if the 
        last item should connected to the first one. Note that
        if close is set true than these parameters have no effect

    Returns:
    -------------------
    np.arrays of the mesh array and the face lists
    '''
    base_circle     = np.array([[ 0, 
        width * math.cos(2 * math.pi * (j/precision)), 
        width * math.sin(2 * math.pi * (j/precision))]
        for j in range(precision+1)], 
        dtype=np.float32)
    vertices_num    = 2*(precision+1)+(2*close)
    faces_num       = 2*precision+(2*precision*close)
    vertices        = np.zeros((positions.shape[0]//2, vertices_num,3), dtype=np.float32) 
    faces           = np.zeros((positions.shape[0]//2, faces_num, 3), dtype=np.uint)
    
    for i in range(positions.shape[0]//2):
        index = 0
        offset_init = i*faces_num
        offset_end  = (i+1)*faces_num

        if close:
            vertices[i, 0,:] = positions[2*i,:]
            vertices[i, -1,:] = positions[2*i+1,:]
            faces[i, :precision,:] = offset_init + np.array([[0, j+1, j+2] for j in range(precision)])
            faces[i, faces_num-precision:faces_num,:] = offset_end + np.array([[-1, -j-1, -j-2] for j in range(precision)])
            index = 1
            
        roatiation_matrix = rotationMatrixFromVectors(
            np.array([1,0,0]), positions[2*i+1]-positions[2*i])

        vertices[i,index:index+precision+1, :] = [
            roatiation_matrix.dot(base_circle[l])+positions[2*i] 
            for l in range(base_circle.shape[0])]
        vertices[i,index+precision+1:index+2*(precision+1), :] = [
            roatiation_matrix.dot(base_circle[l])+positions[2*i+1] 
            for l in range(base_circle.shape[0])]

        face_offset = precision * close
        faces[i, face_offset:face_offset + faces_num, :] = i*vertices_num + np.array(
            [[j, j+1, j+precision+2] for j in range(precision)]
            + [[j+precision+1,j, j+precision+2] for j in range(precision)]
        )
    
    if not close and connect[0]:
        connect_faces = np.zeros((positions.shape[0]//2-1, 2*precision, 3), dtype=np.uint)
        for i in range(positions.shape[0]//2-1):
            connect_faces[i, 0:2*precision, :] = i*2*(precision+1)+precision+1 + np.array(
                [[j, j+1, j+precision+2] for j in range(precision)]
                + [[j+precision+1,j, j+precision+2] for j in range(precision)]
            )
        faces = np.concatenate((faces, connect_faces))
    if not close and connect[1]:
        first   = [i for i in range(precision+1)]
        last    = [i + (positions.shape[0]*(precision+1))-(precision+1) for i in range(precision+1)]
        loop_faces = np.zeros((1, 2*precision, 3), dtype=np.uint)
        loop_faces[0, 0:2*precision, :] =  np.array(
            [[last[j], last[j+1], first[j+1]] for j in range(precision)]
            + [[first[j+1], first[j], last[j]] for j in range(precision)])
        loop_faces 
        faces = np.concatenate((faces, loop_faces))

    return [
        np.reshape(vertices, (vertices.shape[0]*vertices.shape[1],3)),
        np.reshape(faces, (faces.shape[0]*faces.shape[1],3))]

def rotationMatrixFromVectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    found in https://stackoverflow.com/questions/45142959/calculate-rotation-matrix-to-align-two-vectors-in-3d-space
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    if all(a==b): return np.eye(3)
    if all(a==-b):
        rotation_matrix = np.eye(3)
        rotation_matrix[1,1] = -1
        return rotation_matrix
    else:
        v = np.cross(a, b)
        c = np.dot(a, b)
        s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def faceNormals(vertices:np.array, faces:np.array, primitive_size:int = 3)->np.array:
    '''
    This function will manage the creation of normals by face.

    Parameters:
    -------------------
    vertices : np.array
        The vertices n by 3
    faces : np.array
        The faces m by k
    primitive_size : int
        This is the repetition to consider per face

    Returns:
    -------------------
    [np.array, np.array] final single pair of vertices and arrays

    '''
    face_normals = np.zeros((faces.shape[0],3), dtype=np.float32)
    
    for i in range(faces.shape[0]//primitive_size):
        face_normals[i*primitive_size, :] = np.cross(
            vertices[faces[i*primitive_size+1]]-vertices[faces[i*primitive_size]], 
            vertices[faces[i*primitive_size+2]]-vertices[faces[i*primitive_size]])
        face_normals[i*primitive_size+1:(i+1)*primitive_size] = face_normals[i*primitive_size]

    face_normals = face_normals / np.linalg.norm(face_normals, axis=1, keepdims=True)
    return face_normals


def assembleFaces(vertices_face_pairs:list([list([np.array, np.array])]))->list([np.array, np.array]):
    '''
    This function is meant to take pairs of vertices and faces 
    and then assembles them into two single vertices and faces
    arrays to allow easier buffer loading

    Parameters:
    -------------------
    vertices_face_pairs : [np.array, np.array]
        pais of vertices and faces

    Returns:
    -------------------
    [np.array, np.array] final single pair of vertices and arrays

    '''
    output_vertices = np.zeros(
        (sum([pair[0].shape[0] for pair in vertices_face_pairs]),3),
        dtype=np.float32)
    output_faces = np.zeros(
        (sum([pair[1].shape[0] for pair in vertices_face_pairs]),3),
        dtype=np.uint)
    
    vertices_offset = 0
    face_offset = 0
    for pair in vertices_face_pairs:
        output_vertices[vertices_offset:vertices_offset+pair[0].shape[0]] = pair[0]
        output_faces[face_offset:face_offset+pair[1].shape[0]] = pair[1]+vertices_offset

        vertices_offset += pair[0].shape[0]
        face_offset += pair[1].shape[0]

    return output_vertices, output_faces

def tubeTriangleStripVertices(circle_vertices:np.array)->np.array:
    '''
    Process the circle vertives into veretex triangle strip

    Parameters:
    -------------------
    position : np.array
        Point positions in 3 dimensions
    '''
    tube_triangle_vertices = np.zeros((circle_vertices.shape[0],2*circle_vertices.shape[1], circle_vertices.shape[2]))
    for i in range(circle_vertices.shape[0]-1):
        for j in range(circle_vertices.shape[1]):
            tube_triangle_vertices[i, j*2] = circle_vertices[i, j]
            tube_triangle_vertices[i, j*2 + 1] = circle_vertices[i+1, j]

    for j in range(circle_vertices.shape[1]):
        tube_triangle_vertices[-1, j*2] = tube_triangle_vertices[-2, j*2+1]
        tube_triangle_vertices[-1, j*2+1] = tube_triangle_vertices[0, j*2]

    return tube_triangle_vertices

def createTriangleMesh(precision:int = 100)->tuple([np.array,np.array]):
    '''
    This function will create a triangular mesh of points 
    that will be mostly used to project onto spheres

    Parameters:
    -------------------
    precision : int
        The number of subdivisions per axis

    Returns:
    -------------------
    np.arrays of the meshe  s to be used as strip
    '''
    mesh    = np.zeros(
        (int((precision*(precision+1))/2),3), 
        dtype=np.float32)
    points  = np.zeros((
        int(((precision-2)*(precision-1))/2)
        +int(((precision-1)*(precision))/2),3), 
        dtype=np.uint)
        
    magic   = 1. / (precision-1)
    offset  = np.array([1.,0.])
    vect    = np.array([-2*magic, 0])
    index   = 0
    for i in range(precision):
        for j in range(precision-i):
            mesh[index][0] = offset[0]-magic*j
            mesh[index][1] = offset[1]+magic*j
            mesh[index][2] = i * magic
            index += 1
        offset += vect / 2.

    index   = 0
    line    = 0
    for i in range(precision-1):
        for j in range(precision-1-i):
            points[line][0] = index
            points[line][1] = index + 1
            points[line][2] = index + precision-i
            line += 1
            
            #inverted triangle
            if j > 0:
                points[line][0] = index
                points[line][2] = index + precision-i-1
                points[line][1] = index + precision-i
                line += 1     

            index += 1
        index += 1
    
    return mesh, points

def projectOnSphere(vertices:np.array, radius:float = 1.)->tuple([np.array,np.array]):
    '''
    This function takes the vertices and projects them onto a sphere

    Parameters:
    -------------------
    vertices : np.array
        Vertices (n,3)
    radius : float
        Radius of the sphere taken for projection

    Returns:
    -------------------
    np.arrays vertices projected and the normals
    '''
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)

    return radius * vertices, vertices

def createSphere(precision:int = 100, radius:float = 1.0)->list([np.array, np.array, np.array]):
    '''
    This function will create the sphere using the oabove mesh genration 

    Parameters:
    -------------------
    precision : int
        The number of subdivisions per axis
    redius : float
        The radius of the spehere (default is unity)

    Returns:
    -------------------
    np.arrays of the meshes and point lists
    '''
    base_mesh, base_list = createTriangleMesh(precision=precision)
    base_mesh, base_normals = projectOnSphere(base_mesh, radius=radius)

    sphere_mesh = np.array([
        np.array(base_mesh) 
        for i in range(8)], dtype=np.float32)
    sphere_mesh[1,:,0]      = -1 * sphere_mesh[0,:,1]
    sphere_mesh[1,:,1]      =  1 * sphere_mesh[0,:,0]
    sphere_mesh[2,:,0]      = -1 * sphere_mesh[1,:,1]
    sphere_mesh[2,:,1]      =  1 * sphere_mesh[1,:,0]
    sphere_mesh[3,:,0]      = -1 * sphere_mesh[2,:,1]
    sphere_mesh[3,:,1]      =  1 * sphere_mesh[2,:,0]
    sphere_mesh[4,:,1]      = -1 * sphere_mesh[0,:,1]
    sphere_mesh[4,:,2]      = -1 * sphere_mesh[0,:,2]
    sphere_mesh[5,:,0]      = -1 * sphere_mesh[4,:,1]
    sphere_mesh[5,:,1]      =  1 * sphere_mesh[4,:,0]
    sphere_mesh[5,:,2]      = -1 * sphere_mesh[0,:,2]
    sphere_mesh[6,:,0]      = -1 * sphere_mesh[5,:,1]
    sphere_mesh[6,:,1]      =  1 * sphere_mesh[5,:,0]
    sphere_mesh[6,:,2]      = -1 * sphere_mesh[0,:,2]
    sphere_mesh[7,:,0]      = -1 * sphere_mesh[6,:,1]
    sphere_mesh[7,:,1]      =  1 * sphere_mesh[6,:,0]
    sphere_mesh[7,:,2]      = -1 * sphere_mesh[0,:,2]
    

    sphere_normals = np.array([
        np.array(base_normals) 
        for i in range(8)], dtype=np.float32)
    sphere_normals[1,:,0]      = -1 * sphere_normals[0,:,1]
    sphere_normals[1,:,1]      =  1 * sphere_normals[0,:,0]
    sphere_normals[2,:,0]      = -1 * sphere_normals[1,:,1]
    sphere_normals[2,:,1]      =  1 * sphere_normals[1,:,0]
    sphere_normals[3,:,0]      = -1 * sphere_normals[2,:,1]
    sphere_normals[3,:,1]      =  1 * sphere_normals[2,:,0]
    sphere_normals[4,:,1]      = -1 * sphere_normals[0,:,1]
    sphere_normals[4,:,2]      = -1 * sphere_normals[0,:,2]
    sphere_normals[5,:,0]      = -1 * sphere_normals[4,:,1]
    sphere_normals[5,:,1]      =  1 * sphere_normals[4,:,0]
    sphere_normals[5,:,2]      = -1 * sphere_normals[0,:,2]
    sphere_normals[6,:,0]      = -1 * sphere_normals[5,:,1]
    sphere_normals[6,:,1]      =  1 * sphere_normals[5,:,0]
    sphere_normals[6,:,2]      = -1 * sphere_normals[0,:,2]
    sphere_normals[7,:,0]      = -1 * sphere_normals[6,:,1]
    sphere_normals[7,:,1]      =  1 * sphere_normals[6,:,0]
    sphere_normals[7,:,2]      = -1 * sphere_normals[0,:,2]

    sphere_list = np.array([
        np.array(base_list)+i*base_mesh.shape[0] 
        for i in range(8)], dtype=np.uint)

    sphere_mesh = np.reshape(sphere_mesh, (base_mesh.shape[0]*8, base_mesh.shape[1]))
    sphere_list = np.reshape(sphere_list,(base_list.shape[0]*8,3))
    sphere_normals = np.reshape(sphere_normals,(base_normals.shape[0]*8,3))

    return [sphere_mesh, sphere_list, sphere_normals]

def faceNormalsTriangle(vertices:np.array, faces:np.array):
    """
    Return an array (Nf, 3) of normal vectors for each face.
    If indexed='faces', then instead return an indexed array
    (Nf, 3, 3)  (this is just the same array with each vector
    copied three times).
    """
    local_vertices  = vertices[faces]
    faceNormals     = np.cross(
        local_vertices[:,1]-local_vertices[:,0], 
        local_vertices[:,2]-local_vertices[:,0])
    return faceNormals
    
def vertexFaces(vertices:np.array, faces:np.array):
    """
    Return list mapping each vertex index to a list of face indexes that use the vertex.
    """
    vertexFaces = [[] for i in range(vertices.shape[0])]
    for i in range(faces.shape[0]):
        for ind in faces[i]:
            vertexFaces[ind].append(i)
    return vertexFaces

def vertexNormals(vertices:np.array, faces:np.array):
    """
    Return an array of normal vectors.
    By default, the array will be (N, 3) with one entry per unique vertex in the mesh.
    If indexed is 'faces', then the array will contain three normal vectors per face
    (and some vertexes may be repeated).
    """
    faceNorms       = faceNormalsTriangle(vertices, faces)
    vertFaces       = vertexFaces(vertices, faces)
    vertexNormals   = np.empty(vertices.shape, dtype=float)
    for vindex in range(vertices.shape[0]):
        local_faces = vertFaces[vindex]
        if len(local_faces) == 0:
            vertexNormals[vindex] = (0,0,0)
            continue
        norms   = faceNorms[local_faces]  ## get all face normals
        norm    = norms.sum(axis=0)       ## sum normals
        norm    /= (norm**2).sum()**0.5  ## and re-normalize
        vertexNormals[vindex] = norm
            
    return vertexNormals
    
if __name__ == '__main__':
    tube = createTubes()
    sphere = createSphere()
