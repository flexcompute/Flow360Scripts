import os, sys
import json

import unittest
import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import preprocessing.BETDisk.BETDisk.BETTranslatorInterface as interface

here = os.path.abspath(os.path.dirname(__file__))


class AdvancedTestSuite(unittest.TestCase):

    def test_c81(self):    


        betDiskAdditionalInfo = {"gridUnit": 1,
                                 "centerOfRotation": [0, 0, 0],
                                 "rotationDirectionRule": "leftHand",
                                 "axisOfRotation": [0, 0, 1],
                                 "thickness": 15,
                                 "chordRef": 14,
                                 "nLoadingNodes": 20}

        inputFile = os.path.join(here, 'data/Xv15_c81_section1Polars.csv')
        betFlow360 = interface.generateC81BETJSON(inputFile, betDiskAdditionalInfo['axisOfRotation'],
                                    betDiskAdditionalInfo['centerOfRotation'],
                                    betDiskAdditionalInfo['rotationDirectionRule'],
                                    diskThickness=betDiskAdditionalInfo['thickness'],
                                    gridUnit=betDiskAdditionalInfo['gridUnit'],
                                    chordRef=betDiskAdditionalInfo['chordRef'],
                                    nLoadingNodes=betDiskAdditionalInfo['nLoadingNodes'])



        with open(os.path.join(here, 'ref/c81Test.json')) as fh:
            refbetFlow360 = json.load(fh)


        utils.assertDeepAlmostEqual(self, betFlow360, refbetFlow360, places=14)



if __name__ == '__main__':
    unittest.main()
