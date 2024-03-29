"""
This module is meant as an example of how you would use the Xrotor => Flow360 BET disk translator function
Since the Xrotor input file does not provide all of the required information. We need to enter the remaining information
that the BET disk implementation needs. Things like disk location, thrust axis etc...

This can be done either by reading in a JSON file you have setup with all the information not included in the Xrotor file
or you can hard code them in you translator script.

In this example, all the required values are hard coded in this sample script.


Example
-------
 $   python3 XrotorToFlow360BET.py

"""
import json
import os

from BETDisk.BETTranslatorInterface import generateXrotorBETJSON

here = os.path.dirname(os.path.realpath(__file__))

########################################################################################################################
def getBetDiskParams(diskIdx):

    # Here we could read in the BET disk information from a JSON or other file for example by using something like:
    # betDiskJsonFiles=['betDiskJsonNum1.json', 'betDiskJsonNum2.json'.......]
    # betDiskDict = json.load(open(betDiskJsonFiles[diskIdx], 'r'))

    # For this Example we will assign them manually so you see what it needs to look like:
    # All these parameters are explained in the Flow360 documentation under
    # https://docs.flexcompute.com/projects/flow360/en/latest/solverConfiguration/solverConfiguration.html?highlight=initialBladeDirection#betdisks-list

    #mesh is in inches so meshUnit needs to be 0.0254 m per in ( i.e. per mesh unit).  Xrotor inputs are in metric system.
    # Here we are using a mesh in inches to show how to convert using the meshUnit variable.
    betDiskDict = [{"meshUnit": 0.0254,
                 "centerOfRotation": [0, 0, 0],
                 "rotationDirectionRule": "leftHand",
                 "axisOfRotation": [0, 0, 1],
                "omega": 0.0046,
                 "thickness": 15,
                 "chordRef": 14,
                 "nLoadingNodes": 20},
                  # Now we define the 2ND betDisk.
                  {"meshUnit": 0.0254,
                   "centerOfRotation": [10, 0, 0],
                   "rotationDirectionRule": "leftHand",
                   "axisOfRotation": [0, 0, 1],
                   "omega": 0.0046,
                   "thickness": 15,
                   "chordRef": 14,
                   "nLoadingNodes": 20}]

    return betDiskDict[diskIdx] # Since we are doing one BETdisk at a time, return only the betDisk information relevant
# to the disk we are currently doing.


########################################################################################################################
def main():

    # this example will show you how to create a BET disk input JSON file with 2 BET disks.

    # path to the Xrotor input file you would like to use.
    xrotorFilePathList = ['data/xrotor/xv15_like_twist0.xrotor','data/xrotor/xv15_like_twist0.xrotor']  # Each BET disk will get its own geometry and polars definition.
    xrotorFilePathList = [os.path.join(here, file) for file in xrotorFilePathList]
    # The number of BET disks defined in your Flow360Json file is the number of elements in your xRotorFilePathList
    numBetDisks = len(xrotorFilePathList)  # number of disks is length of the filename list

    # Path to the existing Flow360 run parameters that you would like to append the Betdisk information to.
    # IMPORTANT: you must make sure that the mesh is appropriately refined in the region where the BETdisk will be
    # activated.
    flow360BaseJsonFile = os.path.join(here, 'flow360_XV15_BET_Template.json')

    xrotorInputDicts = [{} for i in range(numBetDisks)]  # This is where we will store the BET disk information once we have it.

    # for loop to create each disk in turn
    for diskIdx in range(numBetDisks):

        # we need extra information to define a BET disk that is not in the above Xrotor file.
        # Get it for the BET disk we are doing now.
        betdiskParams = getBetDiskParams(diskIdx)
        xrotorFilePath = xrotorFilePathList[diskIdx]

        xrotorInputDicts[diskIdx] = generateXrotorBETJSON(xrotorFilePath, betdiskParams)

    # now we read in the Flow360 input JSON file we will append the BET information to. This will add  numBetDisks
    # to this Flow360 JSON file.
    with open (flow360BaseJsonFile) as fh:
        flow360Dict  = json.load(fh)

    # Append the Flow360 data to the Flow360 input JSON
    flow360Dict['BETDisks'] = xrotorInputDicts

    # dump the completed Flow360 dictionary to a json file
    outputFilename = 'xv15_xrotor_translated_BET.json'
    with open(outputFilename, 'w') as fh:
        json.dump(flow360Dict, fh, indent=4)
        print('File saved:', outputFilename)


########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the main() function
    main()
