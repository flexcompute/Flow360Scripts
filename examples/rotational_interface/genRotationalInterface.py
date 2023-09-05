# ==================================================================
# This script is written to generate concentric ring-based 
# rotational interface for Flow360.
#===================================================================
# written by Payam Dehpanah
# last update: Sep 2023
#===================================================================

import os
import argparse
import json
import numpy as np
import math
import meshio
from scipy import linalg
from scipy.interpolate import make_interp_spline
from matplotlib import pyplot as plt

#read json configuration file
def read_config_parameters(configF):
    with open(configF,'r') as jconfig:
        config_data = jconfig.read()
    config = json.loads(config_data)
    return config
#end

# returns the value if defined or default if not
def dict_read_or_default (dictionary, entryName, defaultValue):
    try:
        return dictionary[entryName]
    except:
        return defaultValue
#end

# rotational matrix around an axis
def Mrotate (axis,theta):
    return linalg.expm(np.cross(np.eye(3), axis/linalg.norm(axis)*theta))
#end

#rotates around Z from origin
def rotatePointZ (points,theta):
    rotCoords = []
    for i in range(len(points)):
        rotCoords.append(np.dot(Mrotate(np.array([0,0,1]),theta),points[i]).tolist())
    return rotCoords
#end

#rotates around Y from origin
def rotatePointY (points,theta):
    rotCoords = []
    for i in range(len(points)):
        rotCoords.append(np.dot(Mrotate(np.array([0,1,0]),theta),points[i]).tolist())
    return rotCoords
#end

#translates points with dx dy dz
def translatePoints (points,dx,dy,dz):
    return (points + np.array([dx,dy,dz])).tolist()
#end

#scale points with a factor
def scalePoints(points,scale_f):
    return (np.array(points)*scale_f).tolist()
#end

#calculates angles to align the interface axis
def rotationalAngles (intAxis):
    thetaY = math.asin(intAxis[2]/linalg.norm(intAxis))
    thetaZ = math.asin(intAxis[1]/linalg.norm(intAxis))
    return [thetaY,thetaZ]
#end

#transform mesh points according to interface axis
def transformMesh(mesh, rotAngles, centerInterface):
    meshTranslate = translatePoints(mesh[0][0],-centerInterface[0],-centerInterface[1],-centerInterface[2])
    meshRotY = rotatePointY(meshTranslate,rotAngles[0])
    meshRotZ = rotatePointZ(meshRotY,rotAngles[1])
    meshTranslateBack = translatePoints(meshRotZ,centerInterface[0],centerInterface[1],centerInterface[2])
    return [meshTranslateBack,mesh[1][0]]
#end

def read_interface_profile(p_file):
    f = open(p_file,'r')
    lines = f.readlines()
    # profile segment dict
    segments = {}
    # temp coords in each segment
    temp_coords = []
    # for bearks between segments
    isBreak = False
    # is a segment is self-intersecting
    isExist = False
    # segmentId in the dict
    iSeg = 0
    # loop over lines
    for i in range(len(lines)):
        # fetch coordinates as an array
        coord = np.array(lines[i].strip().split(), float)
        # detect breaks between segments
        if len(coord) == 0: isBreak = True
        # if there is a break go to the next segment - empty temp coordinates
        if isBreak: 
            segments[iSeg]= temp_coords
            temp_coords = []
            isBreak = False
            iSeg += 1
        # if not check if it is self intersecting
        else:
            for p in range(len(temp_coords)): 
                if (coord == temp_coords[p]).all(): isExist = True
            # if self-intersect print and exit
            if isExist:
                print('There is a self-intersecting segment in the profile. Aborted!')
                exit()
            # if not self-intersect append to temp
            else:
                temp_coords.append(coord)

    # add the temp coordinates for the last segment
    segments[iSeg]= temp_coords
    
    # check if segments are connected
    for segId in list(segments.keys())[:-1]:
        end_coord = segments[segId][-1]
        if not (end_coord == segments[segId+1][0]).all():
            print('Segments are disconnected in the interface profile. Aborted!')
            exit()
    return segments
#end

# evaluates the spacing input values
def eval_stretching_layers(start,ds,gr,max_edge):
    dist = [start,start+ds]
    layer_count = 1
    cur_edge_length = dist[-1]-dist[-2]
    while abs(cur_edge_length) <= max_edge:
        next_edge_length = dist[-1] + cur_edge_length * gr
        cur_edge_length = cur_edge_length * gr
        if next_edge_length > 0 and next_edge_length <= 1:
            dist.append(next_edge_length)
            layer_count += 1
        else:
            break
    return [layer_count,dist]

# generates stretching spacing from start w n layers
def gen_stretching_layers(start,ds,gr,n_layers):
    dist =[start,start+ds]
    for i in range(n_layers):
        cur_edge_length = dist[-1] - dist[-2]
        next_edge_length = dist[-1] + cur_edge_length * gr
        dist.append(next_edge_length)
    return dist
#end

# creates growth mesh distribution between 0 and 1
def get_growth_distribution(d_s,s_ds,s_gr,n_s,d_e,e_ds,e_gr,n_e,max_length):
    # beginning distribution
    start_dist = gen_stretching_layers(0.0,s_ds,s_gr,n_s-1)

    # middle distribution
    mid_dim = int(np.floor((d_e - d_s) / max_length))
    if mid_dim == 0: mid_dim = 1

    mid_spc = (d_e - d_s) / mid_dim
    mid_dist = gen_stretching_layers(start_dist[-1],mid_spc,1,mid_dim-1)

    # ending distribution
    end_dist = gen_stretching_layers(1.0,-e_ds,e_gr,n_e-1)
    end_dist.reverse()

    distribution = start_dist+mid_dist[1:]+end_dist[1:]
    return distribution
#end

# calculate target max edge length when begin and end spacing intersecting
def cal_target_max_edge_length(eval_spc,spc_gr):
    target_max_spc = eval_spc[1] - eval_spc[0]
    if target_max_spc > 0:
        for i in range(len(eval_spc)):
            if eval_spc[i] >= 0.5:
                target_max_spc = ((1/spc_gr)**3)*(eval_spc[i] - eval_spc[i-1])
                break
    else:
        for i in range(len(eval_spc)):
            if eval_spc[i] <= 0.5:
                target_max_spc = ((1/spc_gr)**3)*(eval_spc[i-1] - eval_spc[i])
                break
    return abs(target_max_spc)
#end

# evaluates spacing input and generates growth distribution between 0 and 1
def gen_line_distribution(length,dist,iseg):
    start_ds = dist[0] / length
    start_gr = dist[1]
    end_ds = dist[2] / length
    end_gr = dist[3]
    max_edge_length = dist[4] / length

    # evaluating the stretching input
    n_start,eval_start = eval_stretching_layers(0.0,start_ds,start_gr,max_edge_length)
    n_end,eval_end = eval_stretching_layers(1.0,-end_ds,end_gr,max_edge_length)
    d_start = eval_start[-1]
    d_end = eval_end[-1]

    # if growth spacing from start and end don't intersect to meet max edge length
    if d_start + (1 - d_end) < 1:
        distribution = get_growth_distribution(d_start,start_ds,start_gr,n_start,d_end,end_ds,end_gr,n_end,max_edge_length)
    # if growth spacing from start and end intersect to meet max edge length
    else:
        # calculating target max edge length after mid point
        s_target_max_spc = cal_target_max_edge_length(eval_start,start_gr)
        e_target_max_spc = cal_target_max_edge_length(eval_end,end_gr)
        mean_edge_length = 0.5 * (s_target_max_spc+e_target_max_spc)

        # re-evaluating spacing from the start and the end
        n_start,re_eval_start = eval_stretching_layers(0.0,start_ds,start_gr,s_target_max_spc)
        n_end,re_eval_end = eval_stretching_layers(1.0,-end_ds,end_gr,e_target_max_spc)
        d_start_re = re_eval_start[-1]
        d_end_re = re_eval_end[-1]

        # when spacing don't intersect with target max spacing
        if d_start_re + (1 - d_end_re) < 1:
            print(f'Max edge length cannot be applied. Target edge length at mid point is used for segment {iseg}!')
            distribution = get_growth_distribution(d_start_re,start_ds,start_gr,n_start,d_end_re,end_ds,end_gr,n_end,mean_edge_length)
        else:
            print(f'Stretching cannot be applied. Uniform distribution is used for segment {iseg}!')
            dim = int(np.ceil(1 / max_edge_length))
            uniform_spc = 1 / dim
            distribution = np.linspace(0,1,dim+1,endpoint=True)
    return distribution
#end

# cumulative distance for points on a curve line
def get_cumulative_distance(points):
    return np.cumsum( np.sqrt(np.sum( np.diff(points, axis=0)**2, axis=1 )) )
#end

# defines a b-spline or linear pieceweise for lines and curves and returns their mesh
def apply_distribution(points,dist,seg_type):
    distance = get_cumulative_distance(points)
    distance = np.insert(distance, 0, 0)/distance[-1]
    # cubic b-spline to curve segments
    if seg_type == 'curve':
        bspl = make_interp_spline(distance, points, k=3)
        mesh = bspl(dist)
    else:
        # linear piecewise for line segments
        mesh_points = np.interp(dist,np.array(points)[:,0],np.array(points)[:,1])
        mesh = np.column_stack((dist,mesh_points,np.zeros(len(dist))))
    return mesh
#end

# generates the mesh for segments based on their spacing
def define_segment_mesh(iseg,seg_type,points,dist):
# def gen_mesh(points,dist,iseg,seg_type):
    # adding the third zero dimension to 2d points and converting them to array
    points_3d = np.append(np.array(points),np.zeros([len(points),1]),1)
    # starting and ending points of a segment
    start_p = points_3d[0]
    end_p = points_3d[-1]
    # translate the start to origin
    points_t = translatePoints(points_3d,-start_p[0],-start_p[1],0)
    # calculate the theta between the start and end
    theta = np.rad2deg(np.arctan2((end_p[1]-start_p[1]),(end_p[0]-start_p[0])))
    # rotate the points to have horizontal line between start and the end
    points_rt = rotatePointZ(points_t,-np.deg2rad(theta))
    # scale factor to have distance of 1 between the start and the end
    scale_one = 1/points_rt[-1][0]
    points_srt = scalePoints(points_rt,scale_one)
    # linear distribution between 0 and 1
    line_dist = gen_line_distribution(1,dist,iseg)
    # apply the distribution to the curve
    line_mesh = apply_distribution(points_srt,line_dist,seg_type)
    # undo scaling
    points_rt = scalePoints(line_mesh,1/scale_one)
    # undo rotation
    points_t = rotatePointZ(points_rt,np.deg2rad(theta))
    # undo translate
    mesh_points = translatePoints(points_t,start_p[0],start_p[1],0)
    # plt.plot(np.array(mesh_points)[:,0],np.array(mesh_points)[:,1],'ob')
    # plt.show()
    return mesh_points
#end

# check if it is a line?!
def check_line(coords):
    tol = 1e-10
    (x0, y0), (x1, y1) = coords[0], coords[1]
    for i in range(2, len(coords)):
        x, y = coords[i]
        if (abs((x0 - x1) * (y1 - y) - (x1 - x) * (y0 - y1))) > tol:
            return False
    return True
#end

# returns types of segments
def define_segment_type(seg_points):
    isLine = check_line(np.array(seg_points))
    x_coords = list(np.array(seg_points)[:,0])
    y_coords = list(np.array(seg_points)[:,1])
    isvLine = x_coords.count(x_coords[0]) == len(x_coords)
    ishLine = y_coords.count(y_coords[0]) == len(y_coords)
    if isvLine:
        seg_type = 'vline'
    elif ishLine:
        seg_type = 'hline'
    elif isLine:
        seg_type = 'line'
    else:
        seg_type = 'curve'
    return seg_type
#end

def define_segment_box(seg_points):
    min_x = min(list(np.array(seg_points)[:,0]))
    max_x = max(list(np.array(seg_points)[:,0]))
    min_y = min(list(np.array(seg_points)[:,1]))
    max_y = max(list(np.array(seg_points)[:,1]))
    return [min_x,max_x,min_y,max_y]
#end

# returns the profile dict including their mesh
def gen_segment_dict(p_file,gen_spc,spc_in):
    # define segments in profile
    profile_segments = read_interface_profile(p_file)
    # number of segments
    num_segments = len(profile_segments.keys())
    # profile spacing dict
    profile_spacing = {}
    for iseg in range(num_segments):
        # tries to fetch spacing per segment
        try:
            profile_spacing[iseg] = [spc_in[f'{iseg}']['cellType'],spc_in[f'{iseg}']['stretching']]
        except:
            # applies the general spacing when not provided
            print(f'General spacing is applied. Spacing is not defined for segment {iseg}!')
            profile_spacing[iseg] = ["tri", [gen_spc,1,gen_spc,1,gen_spc]]
    # generates a dict for segments: type,points,spacing,mesh
    segment_dict = {}
    for iseg in range(num_segments):
        # identifies the type
        iseg_type = define_segment_type(profile_segments[iseg])
        # defines the segment box
        iseg_box = define_segment_box(profile_segments[iseg])
        # generates the mesh on segments
        segment_mesh_dict = define_segment_mesh(iseg,iseg_type,profile_segments[iseg],profile_spacing[iseg][-1])
        # defines a dictionary per segment with their info
        segment_dict[iseg] = iseg_type,profile_segments[iseg],iseg_box,profile_spacing[iseg],segment_mesh_dict
    return segment_dict
#end

# identifies if a segment is front, side or back
def gen_profile_dict(seg_dict):
    profile_dict = {}
    x_min_box = []
    x_max_box = []
    y_min_box = []
    y_max_box = []
    num_seg = len(seg_dict.keys())
    for iseg in range(num_seg):
        x_min_box.append(seg_dict[iseg][2][0])
        x_max_box.append(seg_dict[iseg][2][1])
        y_min_box.append(seg_dict[iseg][2][2])
        y_max_box.append(seg_dict[iseg][2][3])
    p_x_min = min(x_min_box)
    p_x_max = max(x_max_box)
    p_y_min = min(y_min_box)
    p_y_max = max(y_max_box)
    p_x_mid = 0.5 * (p_x_max+p_x_min)
    p_y_mid = 0.5 * (p_y_max+p_y_min)
    p_y_75 = 0.75 * (p_y_max-p_y_min) + p_y_min
    for iseg in range(num_seg):
        seg_x_max = seg_dict[iseg][2][1]
        seg_x_min = seg_dict[iseg][2][0]
        seg_y_min = seg_dict[iseg][2][2]
        seg_y_max = seg_dict[iseg][2][3]
        seg_y_mid = 0.5 * (seg_y_max + seg_y_min)
        if seg_x_max <= p_x_mid and seg_y_mid <= p_y_75:
            profile_dict[iseg] = ["front",seg_dict[iseg]]
        elif seg_y_mid >= p_y_75:
            profile_dict[iseg] = ["side",seg_dict[iseg]]
        try:
            profile_dict[iseg][0]
        except KeyError:
            profile_dict[iseg] = ["back",seg_dict[iseg]]
    return profile_dict
#end

# connectivity for ring elements with respect to pervious ring
def get_ring_connection(ringId,ring_delta,cent_status,m_index,m_points,m_type):
    global mesh_size
    # pervious ring
    p_ring_point = m_points[ringId-1]
    # number of points in pervious ring
    p_ring_dim = len(p_ring_point)
    # number of edges in pervious ring
    p_ring_num_edgs = p_ring_dim - 1
    p_edgs_per_segment = int(p_ring_num_edgs / ring_delta)
    
    # current ring
    c_ring_point = m_points[ringId]
    # number of points in current ring
    c_ring_dim = len(c_ring_point)
    # number of edges in current ring
    c_ring_num_edgs = c_ring_dim - 1
    c_edgs_per_segment = int(c_ring_num_edgs / ring_delta)
    
    # points growing or not
    if p_ring_dim < c_ring_dim:
        growth = 'grow'
    elif p_ring_dim > c_ring_dim:
        growth = 'shrink'
    else:
        growth = 'constant'
    
    # mesh point indices when there is a center point or not
    id_diff = 1
    if cent_status: id_diff = 0
    p_ring_id = [id - id_diff for id in m_index[ringId-1]]
    c_ring_id = [id - id_diff for id in m_index[ringId]]
    # groups for connectives or pervious and current rings
    grp_A_id = {}
    grp_B_id = {}

    # grouping ids for current and pervious rings based on delta points
    for i in range(1,ring_delta+1):
        temp_id_A = []
        temp_id_B = []
        growth_factor_A = p_edgs_per_segment
        growth_factor_B = c_edgs_per_segment
        
        for j in range(0,p_edgs_per_segment+1):
            temp_id_A.append(p_ring_id[growth_factor_A * (i - 1) + j])
        
        for k in range(0,c_edgs_per_segment+1):
            temp_id_B.append(c_ring_id[growth_factor_B * (i - 1) + k])

        grp_A_id[i] = temp_id_A
        grp_B_id[i] = temp_id_B
    # generating element ids based on the two group ids above
    for gId in range(1,ring_delta+1):
        if growth == 'grow':
            index_range_A = p_edgs_per_segment + 1
            index_range_B = p_edgs_per_segment
            for i in range(index_range_A):
                nodeId_1 = grp_A_id[gId][i]
                nodeId_2 = grp_B_id[gId][i]
                nodeId_3 = grp_B_id[gId][i+1]
                mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                mesh_size += 1
            for i in range(index_range_B):
                nodeId_1 = grp_A_id[gId][i]
                nodeId_2 = grp_A_id[gId][i+1]
                nodeId_3 = grp_B_id[gId][i+1]
                mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                mesh_size += 1
        elif growth == 'shrink':
            index_range_B = c_edgs_per_segment + 1
            for i in range(index_range_B):
                nodeId_1 = grp_B_id[gId][i]
                nodeId_2 = grp_A_id[gId][i]
                nodeId_3 = grp_A_id[gId][i+1]
                mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                mesh_size += 1
            for i in range(index_range_B-1):
                nodeId_1 = grp_B_id[gId][i]
                nodeId_2 = grp_B_id[gId][i+1]
                nodeId_3 = grp_A_id[gId][i+1]
                mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                mesh_size += 1
        else:
            if m_type == "quad":
                index_range_A = p_edgs_per_segment
                for i in range(index_range_A):
                    nodeId_1 = grp_A_id[gId][i]
                    nodeId_2 = grp_B_id[gId][i]
                    nodeId_3 = grp_B_id[gId][i+1]
                    nodeId_4 = grp_A_id[gId][i+1]
                    mesh_quad_elements.append([nodeId_1, nodeId_2, nodeId_3, nodeId_4])
                    mesh_size += 1
            else:
                index_range_A = p_edgs_per_segment
                for i in range(index_range_A):
                    nodeId_1 = grp_A_id[gId][i]
                    nodeId_2 = grp_A_id[gId][i+1]
                    nodeId_3 = grp_B_id[gId][i+1]
                    mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                    mesh_size += 1
                    nodeId_1 = grp_A_id[gId][i]
                    nodeId_2 = grp_B_id[gId][i]
                    nodeId_3 = grp_B_id[gId][i+1]
                    mesh_tri_elements.append([nodeId_1, nodeId_2, nodeId_3])
                    mesh_size += 1
    # consecutive distance per edge for the current ring
    for i in range(len(c_ring_point)-1):
        consecutive_dist.append(math.dist(c_ring_point[i+1],c_ring_point[i]))
        # the reference distance from the first element to check tolerance
        if i == 0: ref_distance = consecutive_dist[-1]
    return ref_distance
#end

# checks consecutive mesh distance
def check_consecutive_mesh_distance(ringId,ref_distance):
    # diff between ref consecutive distance and consecutive mesh distance
    consecutive_dist_tol = []
    # checking the consecutive distance between mesh nodes
    for dis in consecutive_dist:
        consecutive_dist_tol.append(abs(dis - ref_distance))
    # when min consecutive distance is greater than 1 - equivalent of 1e-12 based on scale factor
    if min(consecutive_dist_tol) > 1:
        print(f"Distance between two consecutive nodes exceeds at {ringId} radial ring. Min Tol: {min(consecutive_dist_tol)}")
#end

# puts points and cell types of a face from profile dict
def get_face_distribution(pdict,f):
    # number of profile segments
    num_segs = len(pdict.keys())
    # first point of the first segment
    for iseg in range(num_segs):
        if pdict[iseg][0] == f:
            p_first_point = [coord*scale_factor for coord in pdict[iseg][1][-1][0]]
            break
    
    # list of points for the face from all segments skipping the first point
    face_points = [p_first_point]
    face_cellType = ['tri']
    for iseg in range(num_segs):
        if pdict[iseg][0] == f:
            # loop over mesh points per segment 
            for pt in pdict[iseg][1][-1][1:]:
                face_points.append([coord * scale_factor for coord in pt])
                face_cellType.append(pdict[iseg][1][-2][0])
    return [face_points,face_cellType]
#end

def cal_ring_max_edge(r,n_slice,r_dim):
    # circumference of the current ring
    ring_circum = 2 * np.pi * r
    # circumferential edge length for the current ring
    return (ring_circum / n_slice) / (r_dim)
#end

# calculate a list of ring numbers over which shrinking happens
def get_shrink_list(start_dim,end_dim,r_delta,i_ring,n_rings):
    shrink_num = int(np.floor((end_dim - start_dim) / r_delta))
    if shrink_num >= 0 or n_rings < 1:
        return [False,[0]]
    else:
        shrink_freq = int(np.floor(-n_rings / shrink_num))
        shrink_ring_ids = [i for i in range(i_ring,n_rings-shrink_freq,shrink_freq)]
        if len(shrink_ring_ids) !=0:
            return [True,shrink_ring_ids]
        else:
            return [False,[0]]
#end

# generates the rotational interface mesh
def gen_interface_face_mesh(side,f_center,f_status,f_dist,f_start_ring,n_fixed,m_edge,shrink,i_tri):

    global mesh_tri_elements, mesh_quad_elements
    global consecutive_dist

    # mesh points dict and list
    mesh_points = {}
    list_points = []
    # ring indexes dict and list
    mesh_points_index = {}
    list_index = []
    
    # mesh element list of indexes for triangle and quad
    mesh_tri_elements = []
    mesh_quad_elements = []
    # last point mesh index
    last_point_index = 0

    # number of slices and slice theta
    slice_theta = interface_theta
    num_slice = interface_slices

    # mesh slice sign to support top and bottom 
    if side == "top":
        slice_sign = 1
    else:
        slice_sign = -1

    # profile points for this face and their cell type
    face_points = f_dist[0]
    face_cellType = f_dist[1]
    # number of points - left
    mesh_size_boundaries[0] = len(f_dist[0])
    # number of points - right
    mesh_size_boundaries[1] = len(f_dist[0])

    # first ring mesh
    first_ring_points = f_start_ring[0]
    first_ring_indices = [i for i in range(len(first_ring_points))]
    
    # adding the first point to first ring dict and list
    mesh_points[0] = first_ring_points
    list_points = list_points + mesh_points[0]
    
    # first point indices are recorded for the first ring
    mesh_points_index[0] = first_ring_indices
    list_index = list_index + mesh_points_index[0]
    
    # number of mesh points added per one ring progress from the center
    dim_ring_delta = i_tri
    # number of the mesh points on the first ring
    dim_ring = f_start_ring[2]

    # checks if input fixed layers exceed the number of rings
    num_rings = len(face_points)
    if n_fixed > num_rings:
        print('Number of layers with fixed circumferential distribution \
              cannot exceed the number of rings. Fixed layers are set to 1!')
        n_fixed =1

    # calculating shrink parameters
    shrink_list = get_shrink_list(dim_ring,1+dim_ring_delta,dim_ring_delta,1,num_rings-n_fixed)
    
    # looping over concentric rings
    for i_ring in range(1,num_rings):
        # per ring checks
        # checks consecutive dist between mesh points
        consecutive_dist = []
        # initial ref distance
        ref_distance = 0

        # per ring properties
        # radius of the mesh ring
        y_i = face_points[i_ring][1]
        ring_radius = abs(y_i - f_center[1])
        edge_length_ring = cal_ring_max_edge(ring_radius,num_slice,dim_ring)

        if shrink and shrink_list[0]:
            # shrinking and growing in back face
            if i_ring in shrink_list[1]:
                dim_ring -= dim_ring_delta
        else:
            # fixes circum distribution over n number of layers
            if i_ring > n_fixed:
                # if edge length on mesh ring exceed input max edge length add points; otherwise constant
                if edge_length_ring > m_edge:
                    dim_ring += dim_ring_delta

        # theta per mesh point in radians
        theta_per_point = np.deg2rad(slice_theta / (dim_ring - 1))
        # fetching id of last mesh point in the list
        last_point_index = list_index[-1]
        
        # generates ring mesh points
        for pt in range(dim_ring):
            # mesh point coordinates
            x_cord = face_points[i_ring][0]
            y_cord = f_center[1] + ring_radius * np.cos(theta_per_point * pt)
            z_cord = f_center[2] + slice_sign * (ring_radius * np.sin(theta_per_point * pt))
            # point list
            list_points.append([x_cord, y_cord, z_cord])
            # index list
            list_index.append(int(last_point_index + pt + 1))
        # ring mesh points dict for ring ids
        mesh_points[i_ring] = list_points[-dim_ring:]
        # ring index dict for ring ids
        mesh_points_index[i_ring] = list_index[-dim_ring:]

        # element connectivities for the current ring based on dicts of points and indices
        ref_distance = get_ring_connection(i_ring,dim_ring_delta,f_status,mesh_points_index,\
                                           mesh_points,face_cellType[i_ring])
        # checking consecutive distance within scale of e+12 not exceeds 1
        check_consecutive_mesh_distance(i_ring,ref_distance)
    
    # list of element connectivity
    connectivity = []
    
    # when there are tri adds them to connectivity
    if len(mesh_tri_elements) !=0:
        # when face is a donut excludes center
        if not f_status: 
            list_points = list_points[1:]
            connectivity.append(("triangle", mesh_tri_elements[dim_ring_delta:]))
            mesh_size_boundaries[2] = len(mesh_points[1])
        else:
            connectivity.append(("triangle", mesh_tri_elements))
            mesh_size_boundaries[2] = 0
    
    # when there quads adds them to connectivity
    if len(mesh_quad_elements) !=0:
            connectivity.append(("quad", mesh_quad_elements))
    mesh_size_boundaries[3] = len(mesh_points[i_ring])
    index_range = [list_index[0],list_index[-1]]
    points_list = [list_points]
    elements_list = [connectivity]
    ring_dict = [mesh_points,mesh_points_index]
    return [points_list,elements_list,ring_dict,index_range]
#end

def cal_min_initial_tri(s_point,f_center,n_slice,m_edge,max_tri,min_tri):
    start_radius = abs(s_point[1] - f_center[1])
    f_circum = 2 * np.pi * (start_radius) / n_slice
    standard_num_edges = int(np.floor(f_circum / m_edge))
    min_tri_cal = (standard_num_edges- 0.5 * max_tri)
    if min_tri_cal < min_tri: min_tri_cal = min_tri
    return min_tri_cal
#end

# calculates initial number of edges when profiles starts from axis or rotation or not
def cal_starting_elements(ref,m_edge,s_point,e_point,f_center,b_center):
    n_slice = interface_slices
    # scaling the starting and ending point coordinates
    s_point_coords = [coord*scale_factor for coord in s_point]
    e_point_coords = [coord*scale_factor for coord in e_point]
    # status of centers at front and back
    f_starts_center = False
    b_starts_center = False
    # max tri and min tri added 
    max_tri_added = 18
    min_tri_added = 4
    if (np.array(s_point_coords) == np.array(f_center)).all():
        f_starts_center = True
    if (np.array(e_point_coords) == np.array(b_center)).all():
        b_starts_center = True
    # initial number of edges calculation for front
    if f_starts_center:
        f_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri_added) * (1/interface_slices)))
    else:
        min_tri = cal_min_initial_tri(s_point_coords,f_center,n_slice,m_edge,max_tri_added,min_tri_added)
        f_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri) * (1/interface_slices)))
    # initial number of edges calculation for back
    if b_starts_center:
        b_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri_added) * (1/interface_slices)))
    else:
        min_tri = cal_min_initial_tri(e_point_coords,b_center,n_slice,m_edge,max_tri_added,min_tri_added)
        b_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri) * (1/interface_slices)))
    return [f_num_initial_edges,b_num_initial_edges, f_starts_center, b_starts_center]
#end

# generates concentric rotational interface mesh for a profile
def gen_interface_mesh(p_dict,params,side,theta):
    global scale_factor
    global interface_theta, interface_slices
    global mesh_size, mesh_size_boundaries

    # general parameters
    scale_factor = 1e+12
    interface_theta = theta
    interface_slices = 360/interface_theta
    mesh_size = 0
    mesh_size_boundaries = [0,0,0,0]

    # interface length based on starting and ending points
    num_p_segments = len(p_dict.keys())
    first_seg_point = p_dict[0][1][-1][0]
    last_seg_point = p_dict[num_p_segments-1][1][-1][-1]
    interface_length = abs(last_seg_point[0]-first_seg_point[0])
    
    # interface properties
    interface_properties = params["properties"]
    center_interface_position = dict_read_or_default(interface_properties,"center",[0,0,0])
    axis_interface = dict_read_or_default(interface_properties,"axis",[1,0,0])
    angles_interface = rotationalAngles(axis_interface)
    max_edge_length = dict_read_or_default(interface_properties,"maxEdgeLength",0.1)
    ring_ref_factor = dict_read_or_default(interface_properties,"refinementFactor",0)
    f_fixed_layers = dict_read_or_default(interface_properties,"frontFixedDistributionLayers",1)
    b_fixed_layers = dict_read_or_default(interface_properties,"backFixedDistributionLayers",1)

    # scaling interface parameters
    center_interface = [0.5 * abs(last_seg_point[0]-first_seg_point[0]) + first_seg_point[0], center_interface_position[1], 0]
    center_interface = [coord * scale_factor for coord in center_interface]
    interface_length = interface_length * scale_factor
    max_edge_length = max_edge_length * scale_factor

    # center of front and back mesh faces
    front_center = [center_interface[0] - interface_length * 0.5, center_interface[1], center_interface[2]]
    back_center = [center_interface[0] + interface_length * 0.5, center_interface[1], center_interface[2]]

    # calculating first ring number of elements and face status
    f_init_tri,b_init_tri, f_center, b_center = cal_starting_elements(ring_ref_factor,max_edge_length,\
                                                                      first_seg_point,last_seg_point,front_center,back_center)
    
    # profile points and their cell type for the front face from profile dict
    front_dist = get_face_distribution(p_dict,"front")
    side_dist = get_face_distribution(p_dict,"side")
    back_dist = get_face_distribution(p_dict,"back")

    # if the profile starting point is on rotational axis or not
    if f_center:
        front_mesh_first_ring_pts = [front_dist[0][0]]
    else:
        front_mesh_first_ring_pts = [front_center]
    # starting id
    front_mesh_first_ring_ids = [0]
    # first ring dimension
    first_ring_dim = 1 + f_init_tri
    # inputs for the first ring
    front_mesh_first_ring = [front_mesh_first_ring_pts,front_mesh_first_ring_ids,first_ring_dim]

    # generating the front face mesh
    front_mesh = gen_interface_face_mesh(side,front_center,f_center,front_dist,front_mesh_first_ring,\
                                             f_fixed_layers,max_edge_length,False,f_init_tri)

    # number of rings on the front face - points and ids
    front_mesh_num_rings = len(front_mesh[2][0].keys())
    front_mesh_last_ring_pts = front_mesh[2][0][front_mesh_num_rings-1]
    front_mesh_last_ring_ids = front_mesh[2][1][front_mesh_num_rings-1]
    # first ring dim for the side face
    first_ring_dim = len(front_mesh_last_ring_pts)
    # inputs for the first ring
    side_mesh_first_ring = [front_mesh_last_ring_pts,front_mesh_last_ring_ids,first_ring_dim]

    # generating the side face mesh
    side_mesh = gen_interface_face_mesh(side,center_interface,True,side_dist,side_mesh_first_ring,\
                                                 0,max_edge_length,False,f_init_tri)
    
    # number of rings on the front face - points and ids
    side_mesh_num_rings = len(side_mesh[2][0].keys())
    side_mesh_last_ring_pts = side_mesh[2][0][side_mesh_num_rings-1]
    side_mesh_last_ring_ids = side_mesh[2][1][side_mesh_num_rings-1]
    # first ring dim for the side face
    first_ring_dim = len(side_mesh_last_ring_pts)
    # inputs for the first ring
    back_mesh_first_ring = [side_mesh_last_ring_pts,side_mesh_last_ring_ids,first_ring_dim]

    # generating the front face mesh
    back_mesh = gen_interface_face_mesh(side,back_center,True,back_dist,back_mesh_first_ring,\
                                             b_fixed_layers,max_edge_length,True,f_init_tri)

    #transforming front face mesh according to the axis
    front_mesh_transform = transformMesh(front_mesh,angles_interface,center_interface)
    #transforming side face mesh according to axis
    side_mesh_transform = transformMesh(side_mesh,angles_interface,center_interface)
    #transforming side face mesh according to axis
    back_mesh_transform = transformMesh(back_mesh,angles_interface,center_interface)
    #list of mesh points per face
    points_list = [front_mesh_transform[0],side_mesh_transform[0],back_mesh_transform[0]]
    #list of mesh indices per face
    element_list = [front_mesh_transform[1],side_mesh_transform[1],back_mesh_transform[1]]
    index_range_list = [front_mesh[-1],side_mesh[-1],back_mesh[-1],f_center]
    
    # scaling back all float values
    for all_points in points_list:
        for pt, i in zip(all_points,range(len(all_points))): all_points[i]=(np.array(pt)/scale_factor).tolist()
    
    return [points_list,element_list,index_range_list]
#end

def gen_profile_mesh(profile_dict,params):
    interface_top = gen_interface_mesh(profile_dict,params,"top",180)
    interface_bottom = gen_interface_mesh(profile_dict,params,"bottom",180)
    interface_mesh_points = interface_top[0] + interface_bottom[0]
    interface_mesh_elements = interface_top[1] + interface_bottom[1]
    interface_mesh_index = interface_top[2][:-1] + interface_bottom[2][:-1]
    
    # combining srf mesh indices 
    index_list = np.cumsum(interface_mesh_index)
    index_combined = []
    index_diff = [0,0,1,2,2,3]
    for i in range(0,len(index_list),2): index_combined.append(index_list[i])
    if interface_top[2][-1]:
        for i in range(len(index_combined)):
            index_combined[i]+=i
    else:
        index_combined = list(np.array(index_combined)+np.array(index_diff))
    return [interface_mesh_points,interface_mesh_elements,index_combined]
#end

# generates the interface mesh based on input profile
def gen_profile_interface(params):
    # input file
    profile_file = params['general']['inputProfile']
    general_spacing = params['properties']['maxEdgeLength']
    # segment spacings
    spacing_input = params['spacing']['profileSegments']
    segment_dict = gen_segment_dict(profile_file,general_spacing,spacing_input)
    profile_dict = gen_profile_dict(segment_dict)
    profile_mesh = gen_profile_mesh(profile_dict,params)
    return profile_mesh
#end

# to be added later
def gen_cylindrical_interface(params):
    print('Not supported yet')
#end

# to be added later
def gen_spherical_interface(params):
    print('Not supported yet')
#end

def gen_rotational_interface(params):
    int_dict = params["interface"]

    #setting default in case they are not defined
    int_type = dict_read_or_default(int_dict['general'],"type","cylinder")

    if int_type == 'cylinder':
        int_mesh = gen_cylindrical_interface(int_dict)
    elif int_type == 'sphere':
        int_mesh = gen_spherical_interface(int_dict)
    elif int_type == 'profile':
        int_mesh = gen_profile_interface(int_dict)
    return int_mesh
#end

# combines surface meshes and their element ids
def combine_domains(mesh):
    pt_list = mesh[0]
    elm_list = mesh[1]
    ind_list = mesh[2]
    
    # checks element ids and points agree
    try:
        assert len(pt_list) == len(elm_list)
    except AssertionError:
        print("Number of surface mesh points doesn't match the number surface mesh connectivities. Aborted!")
        exit()

    #combines element ids for quad and tri
    d = 1
    dom_elem_data = []
    for l,n in zip(elm_list,ind_list):
        # tri elements are not empty
        if len(l[0][1]) != 0:
            for p_id in range(len(l[0][1])):
                l[0][1][p_id] = [i+n for i in l[0][1][p_id]]
                dom_elem_data.append(d)
        # quad elements are not empty
        if len(l[1][1]) != 0:
            for p_id in range(len(l[1][1])):
                l[1][1][p_id] = [i+n for i in l[1][1][p_id]]
                dom_elem_data.append(d)
        d+=1
    # combines mesh coordinates
    mesh_points = []
    for l in pt_list:
        mesh_points += l

    mesh_elements_tri = []
    mesh_elements_quad = []
    for l in elm_list:
        # tri elements per srf mesh
        if len(l[0][1]) != 0:
            mesh_elements_tri += l[0][1]
        # quad elements per srf mesh
        if len(l[1][1]) != 0:
            mesh_elements_quad += l[1][1]

    mesh_elements = []
    if len(mesh_elements_tri) != 0:
        mesh_elements.append(("triangle", mesh_elements_tri))
    if len(mesh_elements_quad) != 0:
        mesh_elements.append(("quad", mesh_elements_quad))

    return [mesh_points, mesh_elements, dom_elem_data]
#end

def check_mesh_format():
    print('Paraview module is not available. Script uses Paraview cgns writer to write the cgns format.')
    print("Please export Paraview's python path in your environment to be able to export cgns format by:")
    print("export PYTHONPATH='/path/to/paraview/install/lib/python3.10/site-packages:$PATH'")
    print(".dat is exported instead.")
#end

# paraview to export cgns format
def write_mesh_cgns (m_name,data):
    # imports paraview simple from python path to export cgns
    try:
        import paraview.simple
    except ModuleNotFoundError:
        check_mesh_format()
        mesh_dat = m_name.split('.')[0]+'.'+"dat"
        write_mesh_meshio(mesh_dat,data)
        exit()
    
    mesh_vtu = m_name.split('.')[0]+'.'+"vtu"
    write_mesh_meshio(mesh_vtu,data)
    mesh_vtu_load = paraview.simple.OpenDataFile(mesh_vtu)
    paraview.simple.SaveData(m_name,mesh_vtu_load)
    if os.path.isfile(mesh_vtu): os.remove(mesh_vtu)
#end

# meshio to export the mesh
def write_mesh_meshio (m_name, data):
    meshio.write_points_cells(m_name,data[0],data[1])
#end

def write_mesh(mesh,m_name):
    
    # see if extension is available
    try:
        mesh_ext = m_name.split('.')[1]
    except IndexError:
        print("Output mesh extension must be specified. '.dat' is exported!")
        mesh_ext = 'dat'
    
    # combining all srf meshes
    combined_data = combine_domains(mesh)
    output_name = m_name.split('.')[0]

    # export cgns format through paraview; otherwise use meshio to export
    if mesh_ext == "cgns":
        write_mesh_cgns(output_name + '.' + "cgns" ,combined_data)
    else:
        write_mesh_meshio(output_name + '.' + mesh_ext ,combined_data)

    #exporting the mesh interface
    print(f"Interface is exported: {output_name}.{mesh_ext}")
    print(f"Number of points: {mesh_size}")
    print(f"Number of elements: {mesh_size}")
#end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',help='Specify the input JSON file that describes the rotational interface.',type=str,required=True)
    parser.add_argument('-o','--output',help='Specify the output file name for the rotational interface.',type=str,required=True)
    args = parser.parse_args()
    scriptDir = os.getcwd()

    # read interface parameters
    int_params = read_config_parameters(args.input)
    # generate interface mesh
    interfaceMesh = gen_rotational_interface(int_params)
    # writing the interface mesh
    write_mesh(interfaceMesh,args.output)

if __name__ == '__main__':
    main()