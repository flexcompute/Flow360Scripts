import os, sys
import json

import unittest
import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.BETDisk.BETDisk.BETTranslatorInterface as interface

here = os.path.abspath(os.path.dirname(__file__))


class AdvancedTestSuite(unittest.TestCase):

    def test_xfoil(self):    

        betDiskAdditionalInfo = {"centerOfRotation": [0, 0, 0],
                 "rotationDirectionRule": "leftHand",
                 "axisOfRotation": [0, 0, 1],
                 "initialBladeDirection": [1,0,0],
                 "thickness": 15,
                 "chordRef": 14,
                 "nLoadingNodes": 20,
                 "omega" : 0.0046,
                 "numberOfBlades" : 3}

        inputFile = os.path.join(here, 'data/xfoil/xv15_geometry_xfoil_translatorDisk0.csv')
        betFlow360 = interface.generateXfoilBETJSON(inputFile, betDiskAdditionalInfo)


        with open(os.path.join(here, 'ref/xfoilTest.json')) as fh:
            refbetFlow360 = json.load(fh)

        self.maxDiff = None
        utils.assertDeepAlmostEqual(self, betFlow360, refbetFlow360, places=14)


if __name__ == '__main__':
    unittest.main()
