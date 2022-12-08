"""
This module is meant as an example of how you would use Xfoil generated polars to create the Flow360 BET disk input file.
Since an Xfoil polar file does not provide all of the required information. We need to enter the remaining information
that the BET disk implementation needs. Things like disk location, thrust axis etc...

This can be done either by reading in a JSON file you have setup with all the information not included in the xfoil polars
or you can hard code them in you translator script.

In this example, all the required values are hard coded in this sample script.


Example
-------
 $   python3 samplexfoilTranslateScript.py

"""
import sys
import json
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from BETTranslatorInterface import generateXfoilBETJSON

here = os.path.dirname(os.path.realpath(__file__))


########################################################################################################################
def getBetDiskParams(diskIdx):

    # Here we could read in the BET disk information from a JSON or other file for example by using something like:
    # betDiskJsonFiles=['betDiskJsonNum1.json', 'betDiskJsonNum2.json'.......]
    # betDiskDict = json.load(open(betDiskJsonFiles[diskIdx], 'r'))

    # For this Example we will assign them manually so you see what it needs to look like:
    # All these parameters are explained in the Flow360 documentation under
    # https://docs.flexcompute.com/projects/flow360/en/latest/solverConfiguration/solverConfiguration.html?highlight=initialBladeDirection#betdisks-list

    location= [10*diskIdx, 0, 0] # small hack to get a different location for each BETdisk.

    betDiskDict = {"centerOfRotation": location,
                 "rotationDirectionRule": "leftHand",
                 "axisOfRotation": [0, 0, 1],
                 "initialBladeDirection": [1,0,0],
                 "thickness": 15,
                 "chordRef": 14,
                 "nLoadingNodes": 20,
                 "omega" : 0.0046,
                 "tipGap": "inf",
                 "numberOfBlades" : 3}

    return betDiskDict

########################################################################################################################
def main():
    # this example will show you how to create a BET disk input JSON file with 2 BET disks.

    # path to the xfoil input file(s) you would like to use.
    geometryFilePathList = ['xv15_geometry_xfoil_translator.csv', 'xv15_geometry_xfoil_translator.csv']  # Each BET disk will get its own geometry and polars definition.
    geometryFilePathList = [os.path.join(here, file) for file in geometryFilePathList]
    # # The number of BET disks defined in your Flow360Json file is the number of elements in your dfdcFilePathList
    numBetDisks = len(geometryFilePathList)  # number of disks is length of the filename list

    # Path to the existing Flow360 run parameters that you would like to append the Betdisk information to.
    # IMPORTANT: you must make sure that the mesh is appropriately refined in the region where the BETdisk will be
    # activated.
    flow360BaseJsonFile = os.path.join(here, '../flow360_XV15_BET_Template.json')

    xfoilInputDicts = [{} for i in range(numBetDisks)]  # This is where we will store the BET disk information once we have it.

    # for loop to create each disk in turn
    for diskIdx in range(numBetDisks):
        # we need extra information to define a BET disk that is not in the above c81 file.
        # Get it for the BET disk we are doing now.
        betDiskDict = getBetDiskParams(diskIdx)
        geometryFilePath = geometryFilePathList[diskIdx]

        xfoilInputDicts[diskIdx] = generateXfoilBETJSON(geometryFilePath, betDiskDict)

    # now we read in the Flow360 input JSON file we will append the BET information to. This will add  numBetDisks
    # to this Flow360 JSON file.
    with open(flow360BaseJsonFile) as fh:
        flow360Dict = json.load(fh)

    flow360Dict['BETDisks'] = xfoilInputDicts
    # Append the Flow360 data to the Flow360 input JSON

    # dump the completed Flow360 dictionary to a json file
    with open('xv15_xfoil_translated_BET.json', 'w') as fh:
        json.dump(flow360Dict, fh, indent=4)
########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the main() function
    main()
