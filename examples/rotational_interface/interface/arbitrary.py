import numpy as np

import interface.profile as prf
import interface.mesh as mesher
import interface.utilities as utlz

def set_index_diff(n_zones):
    global index_diff_oc,index_diff_cc,index_diff_co,index_diff_oo
    # open and closed
    index_diff_oc = [0,0,1,2,2,3]
    # closed and closed
    index_diff_cc = [0,1,2,3,4,5]
    # closed and open
    index_diff_co = [0,1,2,2,3,4]
    # open and open
    index_diff_oo = [0,0,1,1,1,2]
    if n_zones == 4:
        index_diff_oc[3]-=1
        index_diff_co[3]+=1
#end

def gen_profile_mesh(profile_dict,params,m_edge,ref_f):
    interface_top = mesher.gen_interface_mesh(profile_dict,params,m_edge,ref_f,"top",180)
    interface_bottom = mesher.gen_interface_mesh(profile_dict,params,m_edge,ref_f,"bottom",180)
    interface_mesh_points = interface_top[0] + interface_bottom[0]
    interface_mesh_elements = interface_top[1] + interface_bottom[1]
    interface_mesh_index = interface_top[2][:-2] + interface_bottom[2][:-2]
    mesh_size = interface_top[3] + interface_bottom[3]
    mesh_b_points = interface_top[4][0] + interface_bottom[4][0]
    mesh_b_shared = interface_top[4][1]

    # combining srf mesh indices 
    index_list = np.cumsum(interface_mesh_index)
    num_zones = len(interface_mesh_index)
    set_index_diff(num_zones)
    index_combined = []
    for i in range(0,len(index_list),2): index_combined.append(index_list[i])
    # index diff for domain combination
    if not interface_top[2][-1] and not interface_top[2][-2]:
        index_combined = list(np.array(index_combined)+np.array(index_diff_oo[:num_zones]))
    elif not interface_top[2][-1] and interface_top[2][-2]:
        index_combined = list(np.array(index_combined)+np.array(index_diff_co[:num_zones]))
    elif interface_top[2][-1] and not interface_top[2][-2]:
        index_combined = list(np.array(index_combined)+np.array(index_diff_oc[:num_zones]))
    else:
        index_combined = list(np.array(index_combined)+np.array(index_diff_cc[:num_zones]))
    return [interface_mesh_points,interface_mesh_elements,index_combined,mesh_size,[mesh_b_points,mesh_b_shared]]
#end

# generates the interface mesh based on input profile
def gen_profile_interface(params):
    # input file
    profile_file = params['general']['inputProfile']
    general_ref_factor = utlz.cal_refinement_factor(params['properties'])
    general_spacing = params['properties']['maxEdgeLength']
    
    # segment spacings
    spacing_input = utlz.dict_read_or_default(params,'spacing',None)
    segment_dict = prf.gen_segment_dict(profile_file,general_spacing,spacing_input,general_ref_factor)
    profile_dict = prf.gen_profile_dict(segment_dict)
    profile_mesh = gen_profile_mesh(profile_dict,params,general_spacing,general_ref_factor)
    return profile_mesh
#end