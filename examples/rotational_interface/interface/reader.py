import json
import numpy as np

#read json configuration file
def read_config_parameters(configF):
    with open(configF,'r') as jconfig:
        config_data = jconfig.read()
    config = json.loads(config_data)
    return config
#end

def read_interface_profile(p_file):
    f = open(p_file,'r')
    lines = f.readlines()
    # profile segment dict
    segments = {}
    # temp coords in each segment
    temp_coords = []
    # for bearks between segments
    isBreak = False
    # is a segment is self-intersecting
    isExist = False
    # segmentId in the dict
    iSeg = 0
    # loop over lines
    for i in range(len(lines)):
        # fetch coordinates as an array
        coord = np.array(lines[i].strip().split(), float)
        # detect breaks between segments
        if len(coord) == 0: isBreak = True
        # if there is a break go to the next segment - empty temp coordinates
        if isBreak: 
            segments[iSeg]= temp_coords
            temp_coords = []
            isBreak = False
            iSeg += 1
        # if not check if it is self intersecting
        else:
            for p in range(len(temp_coords)): 
                if (coord == temp_coords[p]).all(): isExist = True
            # if self-intersect print and exit
            if isExist:
                print('There is a self-intersecting segment in the profile. Aborted!')
                exit()
            # if not self-intersect append to temp
            else:
                temp_coords.append(coord)

    # add the temp coordinates for the last segment
    segments[iSeg]= temp_coords
    
    # check if segments are connected
    for segId in list(segments.keys())[:-1]:
        end_coord = segments[segId][-1]
        if not (end_coord == segments[segId+1][0]).all():
            print('Segments are disconnected in the interface profile. Aborted!')
            exit()
    return segments
#end

