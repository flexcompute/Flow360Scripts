import os
from flow360.examples import base_test_case
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--localFiles', default=0, type=int, required=False)
args = parser.parse_args()
local = args.localFiles

base_test_case.here = os.path.dirname(os.path.abspath(__file__))

class WallResolved(base_test_case.BaseTestCase):
    name = "localFiles"

    if local == 1:
        class url:
            mesh = "local://Windsor_Wall_Resolved_1e-06.b8.ugrid"
            case_json = "local://Flow360.json"
    else:   
        class url:
            mesh = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Resolved_1e-06.b8.ugrid"
            case_json = "local://Flow360.json"

class WallModel(base_test_case.BaseTestCase):
    name = "localFiles"

    if local == 1:
        class url:
            mesh = "local://Windsor_Wall_Model_5e-04.b8.ugrid"
    else:
        class url:
            mesh = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Model_5e-04.b8.ugrid"
