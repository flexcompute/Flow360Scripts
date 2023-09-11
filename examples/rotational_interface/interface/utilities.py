import numpy as np

# returns the value if defined or default if not
def dict_read_or_default (dictionary, entryName, defaultValue):
    try:
        return dictionary[entryName]
    except:
        return defaultValue
#end

# cumulative distance for points on a curve line
def get_cumulative_distance(points):
    return np.cumsum( np.sqrt(np.sum( np.diff(points, axis=0)**2, axis=1 )) )
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

# checks consecutive mesh distance
def check_consecutive_mesh_distance(ringId,ref_distance,consecutive_dist):
    # diff between ref consecutive distance and consecutive mesh distance
    consecutive_dist_tol = []
    # checking the consecutive distance between mesh nodes
    for dis in consecutive_dist:
        consecutive_dist_tol.append(abs(dis - ref_distance))
    # when min consecutive distance is greater than 1 - equivalent of 1e-12 based on scale factor
    if min(consecutive_dist_tol) > 1:
        print(f"Distance between two consecutive nodes exceeds at {ringId} radial ring. Min Tol: {min(consecutive_dist_tol)}")
#end

def cal_ring_max_edge(r,n_slice,r_dim):
    # circumference of the current ring
    ring_circum = 2 * np.pi * r
    # circumferential edge length for the current ring
    return (ring_circum / n_slice) / (r_dim)
#end

# calculate a list of ring numbers over which shrinking happens
def get_shrink_list(start_dim,end_dim,r_delta,i_ring,n_rings):
    # number of times it must be shrunk
    shrink_num = int(np.floor((end_dim - start_dim) / r_delta))
    if shrink_num >= 0 or n_rings < 1:
        return [False,[0]]
    else:
        # shrink freq
        shrink_freq = int(np.floor((n_rings - i_ring) / shrink_num ))
        # lists of shrinking ring ids
        shrink_ring_ids = [i for i in range(n_rings,i_ring,shrink_freq)]
        if len(shrink_ring_ids) !=0:
            # when number of shrink times doesn't match
            if len(shrink_ring_ids) < abs(shrink_num):
                delta_s = shrink_num - len(shrink_ring_ids)
                shrink_id_new = len(shrink_ring_ids) // 2
                shrink_list_new = shrink_ring_ids[0:shrink_id_new]
                shrink_freq_update = int(np.floor((shrink_list_new[0] - shrink_list_new[-1]) / (len(shrink_list_new)+delta_s) ))
                shrink_ring_ids_new = [i for i in range(shrink_list_new[0],shrink_list_new[-1],shrink_freq_update)]
                shrink_ring_ids = shrink_ring_ids_new + shrink_ring_ids[shrink_id_new:]
            return [True,shrink_ring_ids]
        else:
            return [False,[0]]
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
def cal_starting_elements(ref,m_edge,s_point,e_point,f_center,b_center,n_slice):
    # n_slice = interface_slices
    # scaling the starting and ending point coordinates
    # s_point_coords = [coord*scale_factor for coord in s_point]
    # e_point_coords = [coord*scale_factor for coord in e_point]
    s_point_coords = s_point
    e_point_coords = e_point
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
        f_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri_added) * (1/n_slice)))
    else:
        min_tri = cal_min_initial_tri(s_point_coords,f_center,n_slice,m_edge,max_tri_added,min_tri_added)
        f_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri) * (1/n_slice)))
    # initial number of edges calculation for back
    if b_starts_center:
        b_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri_added) * (1/n_slice)))
    else:
        min_tri = cal_min_initial_tri(e_point_coords,b_center,n_slice,m_edge,max_tri_added,min_tri_added)
        b_num_initial_edges = int(np.floor((ref * max_tri_added + min_tri) * (1/n_slice)))
    return [f_num_initial_edges,b_num_initial_edges, f_starts_center, b_starts_center]
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