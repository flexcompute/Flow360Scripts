import os, sys
import json

import unittest
import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import preprocessing.BETDisk.BETDisk.BETTranslatorInterface as interface

here = os.path.abspath(os.path.dirname(__file__))


class AdvancedTestSuite(unittest.TestCase):

    def test_dfdc(self):    


        betDiskAdditionalInfo = {"meshUnit": 1,
                                 "centerOfRotation": [10, 0, 0],
                                 "rotationDirectionRule": "rightHand",
                                 "axisOfRotation": [0, 0, 1],
                                 "thickness": 0.05,
                                 "chordRef": 1,
                                 "nLoadingNodes": 20}

        inputFile = os.path.join(here, 'data/dfdcTest.case')
        betFlow360 = interface.generateXrotorBETJSON(inputFile, betDiskAdditionalInfo)

        betFlow360['tipGap'] = 'inf'
        betFlow360['initialBladeDirection'] = [1, 0, 0]

        with open('betFlow360.json', 'w') as fh:
            json.dump(betFlow360, fh, indent=4)

        with open(os.path.join(here, 'ref/dfdcTest.json')) as fh:
            refbetFlow360 = json.load(fh)


        self.maxDiff = None
        utils.assertDeepAlmostEqual(self, betFlow360, refbetFlow360, places=14)




if __name__ == '__main__':
    unittest.main()
