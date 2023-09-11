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
            mesh = "local://mesh.lb8.ugrid"
            case_json = "local://Flow360.json"
    else:
        class url:
            mesh = "https://simcloud-public-1.s3.amazonaws.com/examples/Solver_Features/Adaptive_CFL/ONERAM6/mesh.lb8.ugrid.bz2"
            case_json = "local://Flow360.json"
