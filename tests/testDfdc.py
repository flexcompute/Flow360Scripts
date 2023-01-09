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
                                 "centerOfRotation": [0, 0, 0],
                                 "rotationDirectionRule": "leftHand",
                                 "axisOfRotation": [0, 0, 1],
                                 "thickness": 15,
                                 "chordRef": 14,
                                 "nLoadingNodes": 20}

        inputFile = os.path.join(here, 'data/dfdc_xv15_twist0.case')
        betFlow360 = interface.generateXrotorBETJSON(inputFile, betDiskAdditionalInfo)

        # betFlow360['tipGap'] = 'inf'
        # betFlow360['initialBladeDirection'] = [1, 0, 0]
        # flow360BaseJsonFile = os.path.join(here,'flow360_XV15_BET_Template.json')
        # with open(flow360BaseJsonFile) as fh:
        #     flow360Dict = json.load(fh)
        #
        # flow360Dict['BETDisks'] = [betFlow360]
        # # Append the Flow360 data to the Flow360 input JSON
        #
        # # dump the completed Flow360 dictionary to a json file
        # with open('xv15_dfdc_translated_BET.json', 'w') as fh:
        #     json.dump(flow360Dict, fh, indent=4)
        #
        #
        # with open('betFlow360.json', 'w') as fh:
        #     json.dump(betFlow360, fh, indent=4)
        #
        # with open('betFlow360.json', 'w') as fh:
        #     json.dump(betFlow360, fh, indent=4)

        with open(os.path.join(here, 'ref/dfdcTest.json')) as fh:
            refbetFlow360 = json.load(fh)


        self.maxDiff = None
        utils.assertDeepAlmostEqual(self, betFlow360, refbetFlow360, places=14)




if __name__ == '__main__':
    unittest.main()
