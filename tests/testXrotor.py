import os, sys
import json

import unittest
import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import preprocessing.BETDisk.BETDisk.BETTranslatorInterface as interface

here = os.path.abspath(os.path.dirname(__file__))


class AdvancedTestSuite(unittest.TestCase):

    def test_xrotor(self):    


        betDiskAdditionalInfo = {"gridUnit": 1,
                                 "centerOfRotation": [0, 0, 0],
                                 "rotationDirectionRule": "leftHand",
                                 "axisOfRotation": [0, 0, 1],
                                 "thickness": 15,
                                 "chordRef": 14,
                                 "nLoadingNodes": 20}

        inputFile = os.path.join(here, 'data/xv15_like_twist0.xrotor')
        betFlow360 = interface.generateXrotorBETJSON(inputFile, betDiskAdditionalInfo['axisOfRotation'],
                                    betDiskAdditionalInfo['centerOfRotation'],
                                    betDiskAdditionalInfo['rotationDirectionRule'],
                                    diskThickness=betDiskAdditionalInfo['thickness'],
                                    gridUnit=betDiskAdditionalInfo['gridUnit'],
                                    chordRef=betDiskAdditionalInfo['chordRef'],
                                    nLoadingNodes=betDiskAdditionalInfo['nLoadingNodes'])

        with open('betFlow360.json', 'w') as fh:
            json.dump(betFlow360, fh, indent=4)

        with open(os.path.join(here, 'ref/xrotorTest.json')) as fh:
            refbetFlow360 = json.load(fh)

        self.maxDiff = None
        utils.assertDeepAlmostEqual(self, betFlow360, refbetFlow360, places=14)



if __name__ == '__main__':
    unittest.main()
