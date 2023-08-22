import os
from flow360.examples import base_test_case
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--localFiles', default = 0, type = int, required = False)
args = parser.parse_args()
local = args.localFiles

base_test_case.here = os.path.dirname(os.path.abspath(__file__))

class S809(base_test_case.BaseTestCase):
    name = "localFiles"
    if local==1:
        class url:
            geometry   = "local://s809.csm"
            surface_json = "local://s809SurfaceMesh.json"
            volume_json = "local://s809VolumeMesh.json"
            case_json = "local://s809Case.json"
            mesh = "local://s809structured.cgns"
    else:
        class url:
            geometry = "https://simcloud-public-1.s3.amazonaws.com/s809/s809.csm"
            surface_json = "local://s809SurfaceMesh.json"
            volume_json = "local://s809VolumeMesh.json"
            case_json = "local://s809Case.json"
            mesh = "https://simcloud-public-1.s3.amazonaws.com/s809/s809structured.cgns"

