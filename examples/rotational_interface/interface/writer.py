import numpy as np
import meshio

import interface.utilities as utilz

# writes the cgns format
def write_mesh_cgns(filename, c_data):
    # from pycgns
    import CGNS.MAP
    import CGNS.PAT.cgnslib as CGL
    import CGNS.PAT.cgnskeywords as CK

    num_points = len(c_data[0])
    num_elem_type = len(c_data[1])
    
    if num_elem_type == 2:
        num_elem = len(c_data[1][0][1])+len(c_data[1][1][1])
        tri_status = True
        quad_status = True
    else:
        num_elem = len(c_data[1][0][1])
        if c_data[1][0][0] == 'triangle':
            tri_status = True
            quad_status = False
        elif c_data[1][0][0] == 'quad':
            quad_status = True
            tri_status = False
    
    # tree - base - zone and grid coordinates
    T = CGL.newCGNSTree(version=3.2)
    B = CGL.newCGNSBase(T, 'Base',2,3)
    zone_dim = np.array([[num_points,num_elem,0]])
    Z = CGL.newZone(B, 'Zone_1',zone_dim,CK.Unstructured_s)
    gc = CGL.newGridCoordinates(Z,CK.GridCoordinates_s)

    # grid coordinate arrays
    x_array = np.array([pt[0] for pt in c_data[0]])
    y_array = np.array([pt[1] for pt in c_data[0]])
    z_array = np.array([pt[2] for pt in c_data[0]])
    
    CGL.newDataArray(gc,CK.CoordinateX_s,x_array)
    CGL.newDataArray(gc,CK.CoordinateY_s,y_array)
    CGL.newDataArray(gc,CK.CoordinateZ_s,z_array)

    # connectivities
    if tri_status:
        tri_conn = np.array(c_data[1][0][1])
        tri_range = tri_conn.shape[0]
        tri_array = tri_conn.reshape(tri_range*3) + 1
        tri_start = 1 + tri_conn[0][0]
        tri_end = tri_start + tri_range - 1
        tri_rng_array = np.array([tri_start,tri_end])
        CGL.newElements(Z,'Elem_Triangles',CK.TRI_3,tri_rng_array,tri_array)
    if quad_status:
        quad_conn = np.array(c_data[1][1][1])
        quad_range = quad_conn.shape[0]
        quad_array = quad_conn.reshape(quad_range*4) + 1
        quad_start = tri_end + quad_conn[0][0]
        quad_end = quad_start + quad_range - 1
        quad_rng_array = np.array([quad_start,quad_end])
        CGL.newElements(Z,'Elem_Quads',CK.QUAD_4,quad_rng_array,quad_array)

    # zone_bc for boundary condition
    elm_array = np.array([[i+1 for i in range(num_elem)]])
    int_BC = CGNS.PAT.cgnslib.newBoundary(Z,'interface',elm_array,'BCWall',pttype='PointList')
    CGNS.PAT.cgnslib.newGridLocation(int_BC, value='EdgeCenter')

    # writing the cgns mesh
    CGNS.MAP.save(filename+'.cgns',T)
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
    combined_data = utilz.combine_domains(mesh)
    output_name = m_name.split('.')[0]

    # writes the cgns mesh via pycgns or uses meshio for other formats
    if mesh_ext == "cgns":
        write_mesh_cgns(output_name,combined_data)
    else:
        write_mesh_meshio(output_name + '.' + mesh_ext ,combined_data)

    mesh_points = len(combined_data[0]) - mesh[-1][0] + mesh[-1][1] + 6
    
    #exporting the mesh interface
    print(f"Interface is exported: {output_name}.{mesh_ext}")
    print(f"Number of elements: {mesh[-2]}")
    print(f'Number of mesh points: {mesh_points}')
#end