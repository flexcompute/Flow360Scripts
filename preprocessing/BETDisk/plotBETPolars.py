"""

This code reads in a given Flow360 BET input JSON file and plots the 2D Cl and CD polars along with the twist and chord
distribution in that file.

The goal is to make sure that the polars and geometry information being given to the Flow360 solver is as expected.

"""


import json
import matplotlib.pyplot as plt
import sys
import os

figSize = [16, 8]
ticks = ['x-', '+--', 'p:', '^-', '>--', '<-', '*:', '-', '1-', '2--','3--','4:']

################################################################################################################
def plotClCd(jsonDict):
    """
    Take a valid Flow360 BET disk JSON dictionary and plot the 2D polar values for the various stations.

    :param jsonDict: Dictionary in the format expected by Flow360
    :return: None (outputs plots in png format)
    """
    nDisks = len(jsonDict['BETDisks'])
    for diskNum in range((nDisks)):
        nStations = len(jsonDict['BETDisks'][diskNum]['sectionalRadiuses'])
        alphas = jsonDict['BETDisks'][diskNum]['alphas']
        nMachs = len(jsonDict['BETDisks'][diskNum]['MachNumbers'])
        #plt.figure(figsize=(32, 16))
          # needed to differentiate the various sections in the final plot.
        for stationIdx in range(nStations):
            plt.figure(figsize=(figSize[0], figSize[1]))
            for machIdx in range(nMachs):
                plt.subplot(1, 2, 1)
                plt.plot(jsonDict['BETDisks'][diskNum]['sectionalPolars'][stationIdx]['dragCoeffs'][machIdx][0],
                         jsonDict['BETDisks'][diskNum]['sectionalPolars'][stationIdx]['liftCoeffs'][machIdx][0], ticks[stationIdx],
                         label='Mach#:%.2f' % (jsonDict['BETDisks'][diskNum]['MachNumbers'][machIdx]))
                plt.subplot(1, 2, 2)
                plt.plot(alphas, jsonDict['BETDisks'][diskNum]['sectionalPolars'][stationIdx]['liftCoeffs'][machIdx][0],
                         ticks[stationIdx], label=' Mach#:%.2f' % (jsonDict['BETDisks'][diskNum]['MachNumbers'][machIdx]))

            plt.subplot(1, 2, 1)
            plt.xlim(0, 0.07)
            plt.ylim(-1, 3)
            plt.xlabel('Cd')
            plt.ylabel('Cl')
            plt.grid('on')
            plt.legend()
            plt.title('CL vs Cd')
            plt.subplot(1, 2, 2)
            plt.xlim(-10, 20)
            plt.ylim(-1, 3)
            plt.xlabel('Alpha')
            plt.ylabel('Cl')
            plt.grid('on')
            plt.legend()
            plt.title('Cl vs Alpha')
            plt.savefig('disk%i_CL_CD_comparetoXrotor_station%i.png' % (diskNum, stationIdx))
            plt.close()

        # Now we plot the CL v alpha and CD vs alpha at larger alphas
        for stationIdx in range(nStations):
            plt.figure(figsize=(figSize[0], figSize[1]))
            for machIdx in range(nMachs):
                plt.subplot(1, 2, 1)
                plt.plot(alphas, jsonDict['BETDisks'][diskNum]['sectionalPolars'][stationIdx]['liftCoeffs'][machIdx][0], ticks[stationIdx],
                         label='CL Mach#:%.2f' % (jsonDict['BETDisks'][diskNum]['MachNumbers'][machIdx]))
                plt.subplot(1, 2, 2)
                plt.plot(alphas, jsonDict['BETDisks'][diskNum]['sectionalPolars'][stationIdx]['dragCoeffs'][machIdx][0], ticks[stationIdx],
                         label='Cd Mach#:%.2f' % (jsonDict['BETDisks'][diskNum]['MachNumbers'][machIdx]))


            plt.subplot(1, 2, 1)
            # plt.xlim(0, 0.07)
            # plt.ylim(-0.6, 1.2)
            plt.xlabel('alpha')
            plt.ylabel('Cl')
            plt.grid('on')
            plt.legend()
            plt.title('CL vs Alpha')
            plt.subplot(1, 2, 2)
            # plt.xlim(-20, 30)
            # plt.ylim(-0.7, 1.3)
            plt.xlabel('Alpha')
            plt.ylabel('Cd')
            plt.grid('on')
            plt.legend()
            plt.title('Cd vs Alpha')
            plt.savefig('disk%i_CL_CDvAlpha_station%i.png' % (diskNum, stationIdx))
            plt.subplot(1, 2, 1)
            plt.xlim(-45, 45)
            plt.subplot(1, 2, 2)
            plt.xlim(-45, 45)
            # plt.ylim(-0.6, 1.2).
            plt.savefig('disk%i_CL_CDvAlphaZoomed_station%i.png' % (diskNum, stationIdx))
            plt.subplot(1, 2, 1)
            plt.xlim(-20, 20)
            plt.subplot(1, 2, 2)
            plt.xlim(-20, 20)
            # plt.ylim(-0.6, 1.2).
            plt.savefig('disk%i_CL_CDvAlphaZoomed2_station%i.png' % (diskNum, stationIdx))
            plt.close()


################################################################################################################
def plotTwistChord(jsonDict):
    """
    Take a valid Flow360 BET disk JSON dictionary and plot the twist and chord of the propeller vs radius for the
    various stations.

    :param jsonDict: Dictionary in the format expected by Flow360
    :return: None (outputs plots in png format)
    """
    nDisks = len(jsonDict['BETDisks'])
    plt.figure(figsize=(32, 16))
    for diskNum in range((nDisks)):
        twists=[]
        radius=[]
        twistList=jsonDict['BETDisks'][diskNum]['twists']
        for i in range(len(twistList)):
            twists.append(twistList[i]['twist'])
            radius.append(twistList[i]['radius'])
        plt.plot(radius,twists,label='Disk %i'%diskNum)
    plt.xlabel('radius')
    plt.ylabel('Twist')
    plt.grid('on')
    plt.legend()
    plt.title('Twist vs Propeller Radius')
    plt.savefig('TwistVRadius.png')
    plt.close()

    # now we plot the chords vs radius
    plt.figure(figsize=(32, 16))
    for diskNum in range((nDisks)):
        chords=[]
        radius=[]
        chordList=jsonDict['BETDisks'][diskNum]['chords']
        for i in range(len(chordList)):
            chords.append(chordList[i]['chord'])
            radius.append(chordList[i]['radius'])
        plt.plot(radius,chords,label='Disk %i'%diskNum)
    plt.xlabel('radius')
    plt.ylabel('chords')
    plt.grid('on')
    plt.legend()
    plt.title('Chord vs Propeller Radius')
    plt.savefig('ChordVRadius.png')
    plt.close()
################################################################################################################
def main():
    # load in the files
    if len(sys.argv) == 2:  # assume we passed it the json file names
        JsonFile = sys.argv[1]
    elif len(sys.argv) == 1:  # assume we need to enter the Flow360 file name
        JsonFile = 'xv15_xrotor_translated_BET.json'#input('Please enter the path of the Flow360 json input file you would like to use:')
    else:
        print('wrong number of arguments passed, expecting none or 2, got: ', len(sys.argv) - 1)
        print('QUITTING')
        quit()

    if not os.path.isfile(JsonFile):
        print('xotor json input file %s does not exist.' % JsonFile)
        print('QUITTING')
        quit()

    jsonDict = json.load(open(JsonFile, 'r'))

    plotClCd(jsonDict)
    plotTwistChord(jsonDict)


################################################################################################################
if __name__ == '__main__':
    main()
