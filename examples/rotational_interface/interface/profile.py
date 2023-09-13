import numpy as np
from scipy.interpolate import make_interp_spline

import interface.reader as reader
import interface.utilities as utlz
import interface.transform as trsf

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

# defines a b-spline or linear pieceweise for lines and curves and returns their mesh
def apply_distribution(points,dist,seg_type):
    distance = utlz.get_cumulative_distance(points)
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
    # adding the third zero dimension to 2d points and converting them to array
    points_3d = np.append(np.array(points),np.zeros([len(points),1]),1)
    # length of the segment
    seg_length = utlz.get_cumulative_distance(points_3d)[-1]
    # starting and ending points of a segment
    start_p = points_3d[0]
    end_p = points_3d[-1]
    # translate the start to origin
    points_t = trsf.translatePoints(points_3d,-start_p[0],-start_p[1],0)
    # calculate the theta between the start and end
    theta = np.rad2deg(np.arctan2((end_p[1]-start_p[1]),(end_p[0]-start_p[0])))
    # rotate the points to have horizontal line between start and the end
    points_rt = trsf.rotatePointZ(points_t,-np.deg2rad(theta))
    # scale factor to have distance of 1 between the start and the end
    scale_one = 1/points_rt[-1][0]
    points_srt = trsf.scalePoints(points_rt,scale_one)
    # linear distribution between 0 and 1
    line_dist = gen_line_distribution(seg_length,dist,iseg)
    # apply the distribution to the curve
    line_mesh = apply_distribution(points_srt,line_dist,seg_type)
    # undo scaling
    points_rt = trsf.scalePoints(line_mesh,1/scale_one)
    # undo rotation
    points_t = trsf.rotatePointZ(points_rt,np.deg2rad(theta))
    # undo translate
    mesh_points = trsf.translatePoints(points_t,start_p[0],start_p[1],0)
    return mesh_points
#end

# returns types of segments
def define_segment_type(seg_points):
    isLine = utlz.check_line(np.array(seg_points))
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
    profile_segments = reader.read_interface_profile(p_file)
    # number of segments
    num_segments = len(profile_segments.keys())
    # profile spacing dict
    profile_spacing = {}
    for iseg in range(num_segments):
        # tries to fetch spacing per segment
        try:
            seg_stretch = spc_in[f'{iseg}']['stretching']
            profile_spacing[iseg] = [spc_in[f'{iseg}']['cellType'],seg_stretch]
        except:
            # applies the general spacing when not provided
            print(f'General spacing is applied. Spacing is not defined for segment {iseg}!')
            profile_spacing[iseg] = ["tri", [gen_spc,1.0,gen_spc,1.0,gen_spc]]
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
    start_x = seg_dict[0][1][0][0]
    end_x = seg_dict[num_seg-1][1][-1][0]
    for iseg in range(num_seg):
        x_min_box.append(seg_dict[iseg][2][0])
        x_max_box.append(seg_dict[iseg][2][1])
        y_min_box.append(seg_dict[iseg][2][2])
        y_max_box.append(seg_dict[iseg][2][3])
    p_x_min = min(x_min_box)
    p_x_max = max(x_max_box)
    p_y_min = min(y_min_box)
    p_y_max = max(y_max_box)
    delta_seg = num_seg // 3
    i_front = y_max_box.index(p_y_max)
    i_rest = num_seg - i_front - 1
    i_back = i_front + i_rest // 4
    i_mid = num_seg // 2 - 1
    i_25 = i_mid // 2 - 1
    i_75 = i_mid + i_25
    if delta_seg == 1:
        profile_dict[0] = ["front",seg_dict[0]]
        profile_dict[1] = ["side",seg_dict[1]]
        profile_dict[2] = ["back",seg_dict[2]]
    elif delta_seg>1:
        for iseg in range(num_seg):
            if iseg <= i_front:
                profile_dict[iseg] = ["front",seg_dict[iseg]]
            elif iseg <= i_back:
                profile_dict[iseg] = ["side",seg_dict[iseg]]
            else:
                profile_dict[iseg] = ["back",seg_dict[iseg]]
    else:
        print("For profile interface type there must be at least three segments. Aborted!")
        exit()
    return profile_dict
#end