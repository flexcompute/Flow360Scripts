import os
import argparse

import interface.reader as reader
import interface.writer as writer
import interface.utilities as utlz
import interface.arbitrary as arb_int

def gen_rotational_interface(params):
    int_dict = params["interface"]

    #setting default in case they are not defined
    int_type = utlz.dict_read_or_default(int_dict['general'],'type','profile')

    if int_type == 'profile':
        int_mesh = arb_int.gen_profile_interface(int_dict)
    else:
        print('Only revolved interfaces with profile input are supported.')
        exit()
    return int_mesh
#end

def main(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',help='Specify the input JSON file that describes the rotational interface.',type=str,required=True)
    parser.add_argument('-o','--output',help='Specify the output file name for the rotational interface.',type=str,required=True)
    if __name__ != "__main__":
        idein = []
        for var, val in kwargs.items():
            if val is not None:
                idein.extend(['--{}'.format(var)])
                idein.extend(['{}'.format(val)])
        args = parser.parse_args(idein)
    else:
        args = parser.parse_args()
    scriptDir = os.getcwd()
    
    # read interface parameters
    int_params = reader.read_config_parameters(args.input)
    # generate interface mesh
    interfaceMesh = gen_rotational_interface(int_params)
    # writing the interface mesh
    writer.write_mesh(interfaceMesh,args.output)
#end

if __name__ == '__main__':
    main()
