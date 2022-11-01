"""
This module is meant as an example of how you would use C81 polars to create the Flow360 BET disk input file.
Since a C81 input file does not provide all of the required information. We need to enter the remaining information
that the BET disk implementation needs. Things like disk location, thrust axis etc...


AS explained in https://ntrs.nasa.gov/citations/20090040076, the C81 airfoil performance table is a text file that lists
coefficients of lift, drag, and pitching moment of an airfoil as functions of angle of attack for a range of Mach numbers.
here is more on the .c81 format https://etda.libraries.psu.edu/files/final_submissions/15396
https://cibinjoseph.github.io/C81-Interface/page/index.html


This can be done either by reading in a JSON file you have setup with all the information not included in the C81 polars
or you can hard code them in you translator script.

In this example, all the required values are hard coded in this sample script.


Example
-------
 $   python3 sampleC81TranslateScript.py

"""
import sys
import json
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from BETTranslatorInterface import generateC81BETJSON

here = os.path.dirname(os.path.realpath(__file__))


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

    return betDiskDict[diskIdx] # Since we are doing one BETdisk at a time, return only the betDisk information relevant
# to the disk we are currently doing.

########################################################################################################################
def main():
    # this example will show you how to create a BET disk input JSON file with 2 BET disks.

    # path to the C81 input file(s) you would like to use.
    c81FilePathList = ['Xv15_c81_section1Polars.csv', 'Xv15_c81_section2Polars.csv']  # Each BET disk will get its own geometry and polars definition.
    c81FilePathList = [os.path.join(here, file) for file in c81FilePathList]
    # # The number of BET disks defined in your Flow360Json file is the number of elements in your dfdcFilePathList
    numBetDisks = 1 # TEMPORARY HARD CODED len(c81FilePathList)  # number of disks is length of the filename list

    # Path to the existing Flow360 run parameters that you would like to append the Betdisk information to.
    # IMPORTANT: you must make sure that the mesh is appropriately refined in the region where the BETdisk will be
    # activated.
    flow360BaseJsonFile = os.path.join(here, '../flow360_XV15_BET_Template.json')

    c81InputDicts = [{} for i in range(numBetDisks)]  # This is where we will store the BET disk information once we have it.

    # for loop to create each disk in turn
    for diskIdx in range(numBetDisks):

        # we need extra information to define a BET disk that is not in the above c81 file.
        # Get it for the BET disk we are doing now.
        betdiskParams = getBetDiskParams(diskIdx)
        c81FilePath = c81FilePathList[diskIdx]

        c81InputDicts[diskIdx] = generateC81BETJSON(c81FilePath, betdiskParams['axisOfRotation'],
                                    betdiskParams['centerOfRotation'],
                                    betdiskParams['rotationDirectionRule'],
                                    diskThickness=betdiskParams['thickness'],
                                    gridUnit=betdiskParams['gridUnit'],
                                    chordRef=betdiskParams['chordRef'],
                                    nLoadingNodes=betdiskParams['nLoadingNodes'])

    # now we read in the Flow360 input JSON file we will append the BET information to. This will add  numBetDisks
    # to this Flow360 JSON file.
    with open (flow360BaseJsonFile) as fh:
        flow360Dict  = json.load(fh)

    flow360Dict['BETDisks'] = c81InputDicts
    # Append the Flow360 data to the Flow360 input JSON

    # dump the completed Flow360 dictionary to a json file
    with open('xv15_c81_translated_BET.json', 'w') as fh:
        json.dump(flow360Dict, fh, indent=4)
########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the main() function
    main()
