import os
from flow360.examples import base_test_case
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--localFiles', default = 0, type = int, required = False)
args = parser.parse_args()
local = args.localFiles

base_test_case.here = os.path.dirname(os.path.abspath(__file__))

class XV15(base_test_case.BaseTestCase):
    name = "localFiles"
    if local==1:
        class url:
            mesh = "local://xv15_airplane_pitch26.cgns"
            case_json = "local://Flow360.json"
    else:
        class url:
            mesh = "PLACEHOLDER"
            case_json = "PLACEHOLDER"
