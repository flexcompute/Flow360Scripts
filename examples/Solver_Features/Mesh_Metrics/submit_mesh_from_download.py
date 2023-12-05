"""Submits the mesh from mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

mesh_name_list = []

# download meshes to the current directory

URL = "PLACEHOLDER"
MESH_FILENAME = "Unswept_CRM_Poor_Surface.cgns"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)


# submit mesh with poor surface
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="CRM_Poor_Surface_Mesh")
volume_mesh = volume_mesh.submit()
mesh_name_list.append(volume_mesh.name)

with open("mesh_name_list.dat", "w", encoding="utf-8") as f:
    for line in mesh_name_list:
        f.write(f"{line}\n")
