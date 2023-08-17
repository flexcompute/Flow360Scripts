import os
from flow360.examples import base_test_case
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--localFiles', default = 0, type = int, required = False)
args = parser.parse_args()
local = args.localFiles

base_test_case.here = os.path.dirname(os.path.abspath(__file__))

class ONERAM6(base_test_case.BaseTestCase):
    name = "localFiles"
    if local==1:
        class url:
            geometry   = "local://om6wing.csm"
            surface_json = "local://om6SurfaceMesh.json"
            volume_json = "local://om6VolumeMesh.json"
            case_json = "local://om6Case.json"
    else:
        class url:
            geometry   = "https://simcloud-public-1.s3.amazonaws.com/om6QuickStartAutoMesh/om6wing.csm"
            surface_json = "https://simcloud-public-1.s3.amazonaws.com/om6QuickStartAutoMesh/om6SurfaceMesh.json"
            volume_json = "https://simcloud-public-1.s3.amazonaws.com/om6QuickStartAutoMesh/om6VolumeMesh.json"
            case_json = "https://simcloud-public-1.s3.amazonaws.com/om6QuickStartAutoMesh/om6Case.json"

