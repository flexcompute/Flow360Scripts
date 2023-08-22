import os
from flow360.examples import base_test_case
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--localFiles', default = 0, type = int, required = False)
args = parser.parse_args()
local = args.localFiles

base_test_case.here = os.path.dirname(os.path.abspath(__file__))

class XV15_1st(base_test_case.BaseTestCase):
    name = "localFiles"
    if local==1:
        class url:
            case_json = "local://XV15_quick_start_flow360_1st.json"
            mesh = "local://XV15_Hover_ascent_coarse.cgns"
    else:
        class url:
            case_json = "local://XV15_quick_start_flow360_1st.json"
            mesh = "https://simcloud-public-1.s3.amazonaws.com/xv15/XV15_Hover_ascent_coarse.cgns"

class XV15_2nd(base_test_case.BaseTestCase):
    name = "localFiles"
    if local==1:
        class url:
            case_json = "local://XV15_quick_start_flow360_2nd.json"
    else:
        class url:
            case_json = "https://simcloud-public-1.s3.amazonaws.com/xv15/XV15_quick_start_flow360_2nd.json"

