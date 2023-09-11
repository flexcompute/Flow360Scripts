import numpy as np

import interface.profile as prf
import interface.mesh as mesher

def gen_profile_mesh(profile_dict,params):
    interface_top = mesher.gen_interface_mesh(profile_dict,params,"top",180)
    interface_bottom = mesher.gen_interface_mesh(profile_dict,params,"bottom",180)
    interface_mesh_points = interface_top[0] + interface_bottom[0]
    interface_mesh_elements = interface_top[1] + interface_bottom[1]
    interface_mesh_index = interface_top[2][:-1] + interface_bottom[2][:-1]
    
    # meshio.write_points_cells(f"ft.dat",interface_top[0][0],interface_top[1][0])
    # meshio.write_points_cells(f"fb.dat",interface_top[0][1],interface_top[1][1])
    # meshio.write_points_cells(f"st.dat",interface_top[0][2],interface_top[1][2])
    # meshio.write_points_cells(f"sb.dat",interface_bottom[0][0],interface_bottom[1][0])
    # meshio.write_points_cells(f"bt.dat",interface_bottom[0][1],interface_bottom[1][1])
    # meshio.write_points_cells(f"bb.dat",interface_bottom[0][2],interface_bottom[1][2])

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
    segment_dict = prf.gen_segment_dict(profile_file,general_spacing,spacing_input)
    profile_dict = prf.gen_profile_dict(segment_dict)
    profile_mesh = gen_profile_mesh(profile_dict,params)
    return profile_mesh
#end