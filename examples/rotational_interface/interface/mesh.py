import numpy as np
import math

import interface.utilities as utlz
import interface.transform as trsf

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
    consecutive_dist = []
    for i in range(len(c_ring_point)-1):
        consecutive_dist.append(math.dist(c_ring_point[i+1],c_ring_point[i]))
        # # the reference distance from the first element to check tolerance
        # if i == 0: ref_distance = consecutive_dist[-1]
    return consecutive_dist
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

# generates the rotational interface mesh
def gen_interface_face_mesh(side,f_center,f_status,f_dist,f_start_ring,n_fixed,m_edge,shrink,i_tri):

    global mesh_tri_elements, mesh_quad_elements
    # global consecutive_dist

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
        print('Number of layers with fixed circumferential distribution cannot exceed the number of rings. Fixed layers are set to 1!')
        n_fixed =1

    # calculating shrink parameters
    shrink_list = utlz.get_shrink_list(dim_ring,1+dim_ring_delta,dim_ring_delta,1,num_rings-n_fixed)
    # looping over concentric rings
    for i_ring in range(1,num_rings):
        # per ring properties
        # radius of the mesh ring
        y_i = face_points[i_ring][1]
        ring_radius = abs(y_i - f_center[1])
        edge_length_ring = utlz.cal_ring_max_edge(ring_radius,num_slice,dim_ring)

        if shrink and shrink_list[0]:
            # shrinking and growing in back face
            if i_ring in shrink_list[1]:
                if dim_ring - dim_ring_delta > 1:
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
        consecutive_dist = get_ring_connection(i_ring,dim_ring_delta,f_status,mesh_points_index,\
                                           mesh_points,face_cellType[i_ring])
        ref_distance = consecutive_dist[-1]
        # checking consecutive distance within scale of e+12 not exceeds 1
        utlz.check_consecutive_mesh_distance(i_ring,ref_distance,consecutive_dist)
    
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
    else:
        connectivity.append(("triangle", []))
    # when there quads adds them to connectivity
    if len(mesh_quad_elements) !=0:
            connectivity.append(("quad", mesh_quad_elements))
    else:
        connectivity.append(("quad", []))
    mesh_size_boundaries[3] = len(mesh_points[i_ring])
    index_range = [list_index[0],list_index[-1]]
    points_list = [list_points]
    elements_list = [connectivity]
    ring_dict = [mesh_points,mesh_points_index]

    return [points_list,elements_list,ring_dict,index_range]
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
    center_interface_position = utlz.dict_read_or_default(interface_properties,"center",[0,0,0])
    axis_interface = utlz.dict_read_or_default(interface_properties,"axis",[1,0,0])
    angles_interface = trsf.rotationalAngles(axis_interface)
    max_edge_length = utlz.dict_read_or_default(interface_properties,"maxEdgeLength",0.1)
    ring_ref_factor = utlz.dict_read_or_default(interface_properties,"refinementFactor",0)
    f_fixed_layers = utlz.dict_read_or_default(interface_properties,"frontFixedDistributionLayers",1)
    b_fixed_layers = utlz.dict_read_or_default(interface_properties,"backFixedDistributionLayers",1)

    # scaling interface parameters
    center_interface = [0.5 * abs(last_seg_point[0]-first_seg_point[0]) + first_seg_point[0],0,0]
    center_interface = [coord * scale_factor for coord in center_interface]
    center_interface_position = [coord * scale_factor for coord in center_interface_position]
    first_seg_point = [coord * scale_factor for coord in first_seg_point]
    last_seg_point = [coord * scale_factor for coord in last_seg_point]
    interface_length = interface_length * scale_factor
    max_edge_length = max_edge_length * scale_factor

    # center of front and back mesh faces
    front_center = [center_interface[0] - interface_length * 0.5, center_interface[1], center_interface[2]]
    back_center = [center_interface[0] + interface_length * 0.5, center_interface[1], center_interface[2]]

    # calculating first ring number of elements and face status
    f_init_tri,b_init_tri, f_center, b_center = utlz.cal_starting_elements(ring_ref_factor,max_edge_length,\
                                                                      first_seg_point,last_seg_point,front_center,back_center,interface_slices)
    
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
    front_mesh_transform = trsf.transformMesh(front_mesh,angles_interface,center_interface,center_interface_position)
    #transforming side face mesh according to axis
    side_mesh_transform = trsf.transformMesh(side_mesh,angles_interface,center_interface,center_interface_position)
    #transforming side face mesh according to axis
    back_mesh_transform = trsf.transformMesh(back_mesh,angles_interface,center_interface,center_interface_position)
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

