"""
This module is meant as an example of how you would use the Xrotor => Flow360 BET disk translator function

EXAMPLE useage:
    python3 sampleXrotorTranslateScript.py

"""

import BETTranslatorInterface as interf
import json


########################################################################################################################
def getBetDiskParams(diskIdx):

    # Here we could read in the BET disk information from a JSON or other file for example by using something like:
    # betDiskJsonFiles=['betDiskJsonNum1.json', 'betDiskJsonNum2.json'.......]
    # betDiskDict = json.load(open(betDiskJsonFiles[diskIdx], 'r'))

    # For this Example we will assign them manually so you see what it needs to look like:
    # All these parameters are explained in the Flow360 documentation under
    # https://docs.flexcompute.com/projects/flow360/en/latest/solverConfiguration/solverConfiguration.html?highlight=initialBladeDirection#betdisks-list
    betDiskDict = [{"gridUnit": 1,
                 "centerOfRotation": [0, 0, 0],
                 "rotationDirectionRule": "leftHand",
                 "axisOfRotation": [0, 0, 1],
                 "thickness": 15,
                 "chordRef": 14,
                 "nLoadingNodes": 20},
                  # Now we define the 2ND betDisk.
                  {"gridUnit": 1,
                   "centerOfRotation": [10, 0, 0],
                   "rotationDirectionRule": "rightHand",
                   "axisOfRotation": [0, 0, 1],
                   "thickness": 0.05,
                   "chordRef": 1,
                   "nLoadingNodes": 20}]

    return betDiskDict[diskIdx]


########################################################################################################################
def main():

    # this example will show you how to create a BET disk input JSON file with 2 BET disks.

    # path to the Xrotor input file you would like to use.
    xrotorFilePathList = ['xv15_like_twist0.xrotor', 'ecruzer.prop']  # Each BET disk will get its own geometry and polars definition.
    # The number of BET disks defined in your Flow360Json file is the number of elements in your dfdcFilePathList
    numBetDisks = len(xrotorFilePathList)  # number of disks is length of the filename list


    # Path to the existing Flow360 run parameters that you would like to append the Betdisk information to.
    # IMPORTANT: you must make sure that the mesh is appropriately refined in the region where the BETdisk will be
    # activated.
    flow360BaseJsonFile = 'flow360_XV15_BET_Template.json'

    xrotorInputDicts = [{} for i in range(numBetDisks)]  # This is where we will store the BET disk information once we have it.

    # for loop to create each disk in turn
    for diskIdx in range(numBetDisks):

        # we need extra information to define a BET disk that is not in the above Xrotor file.
        # Get it for the BET disk we are doing now.
        betdiskParams = getBetDiskParams(diskIdx)
        xrotorFilePath = xrotorFilePathList[diskIdx]

        xrotorInputDicts[diskIdx] = interf.generateXrotorBETJSON(xrotorFilePath, betdiskParams['axisOfRotation'],
                                    betdiskParams['centerOfRotation'],
                                    betdiskParams['rotationDirectionRule'],
                                    diskThickness=betdiskParams['thickness'],
                                    gridUnit=betdiskParams['gridUnit'],
                                    chordRef=betdiskParams['chordRef'],
                                    nLoadingNodes=betdiskParams['nLoadingNodes'])

    # now we read in the Flow360 input JSON file we will append the BET information to. This will add  numBetDisks
    # to this Flow360 JSON file.
    flow360Dict = json.load(open(flow360BaseJsonFile, 'r'))
    flow360Dict['BETDisks'] = xrotorInputDicts
    # Append the Flow360 data to the Flow360 input JSON

    # dump the completed Flow360 dictionary to a json file
    json.dump(flow360Dict, open('xv15_xrotor_translated_BET.json', 'w'), indent=4)


########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the main() function
    main()
