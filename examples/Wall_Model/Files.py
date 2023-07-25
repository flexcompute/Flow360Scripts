from flow360.examples.base_test_case import BaseTestCase

class WallResolved(BaseTestCase):
    name = "wall_resolved"
   
    class url:
        mesh = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Resolved_1e-06.b8.ugrid"
        case_json = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/JSON/Flow360.json"

class WallModel(BaseTestCase):
    name = "wall_model"

    class url:
        mesh = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Model_5e-04.b8.ugrid"

