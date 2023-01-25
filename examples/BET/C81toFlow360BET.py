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
 $   python3 C81toFlow360BET.py

"""
import json
import os

from BETDisk.BETTranslatorInterface import generateC81BETJSON

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

    # path to the geometry input file(s) you would like to use.
    geometryFilePathList = ['data/c81/Xv15_geometry.csv', 'data/c81/Xv15_geometry.csv']# Each BET disk will get its own geometry and polars definition.
    geometryFilePathList = [os.path.join(here, file) for file in geometryFilePathList]
    # # The number of BET disks defined in your Flow360Json file is the number of elements in your dfdcFilePathList
    numBetDisks = len(geometryFilePathList) # number of disks is number of geometry files defined above.

    # Path to the existing Flow360 run parameters that you would like to append the Betdisk information to.
    # IMPORTANT: you must make sure that the mesh is appropriately refined in the region where the BETdisk will be
    # activated.
    flow360BaseJsonFile = os.path.join(here, 'flow360_XV15_BET_Template.json')

    c81InputDicts = [{} for i in range(numBetDisks)]  # This is where we will store the BET disk information once we have it.

    # for loop to create each disk in turn
    for diskIdx in range(numBetDisks):

        # we need extra information to define a BET disk that is not in the above c81 file.
        # Get it for the BET disk we are doing now.
        betDiskDict = getBetDiskParams(diskIdx)
        geometryFilePath = geometryFilePathList[diskIdx]

        c81InputDicts[diskIdx] = generateC81BETJSON(geometryFilePath, betDiskDict)

    # now we read in the Flow360 input JSON file we will append the BET information to. This will add  numBetDisks
    # to this Flow360 JSON file.
    with open (flow360BaseJsonFile) as fh:
        flow360Dict  = json.load(fh)

    # Append the Flow360 data to the Flow360 input JSON
    flow360Dict['BETDisks'] = c81InputDicts

    # dump the completed Flow360 dictionary to a json file
    outputFilename = 'xv15_c81_translated_BET.json'
    with open('xv15_c81_translated_BET.json', 'w') as fh:
        json.dump(flow360Dict, fh, indent=4)
        print('File saved:', outputFilename)

########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the main() function
    main()
