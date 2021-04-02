import sys 
import getopt
import re

def convert_bristol(pws_array):
    bristol = []
    num_gates, num_wires, niv, nov = 0, 0, 0, 0

    pass


if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Missing input file")
        sys.exit(-1)
    if sys.argv[1][-3:] != 'pws':
        print("Not PWS file")
        sys.exit(-1)
    
    ### Read Bristol
    pws = sys.argv[1]
    with open(pws, 'r') as in_f: 
        in_lines = in_f.readlines()
    for i in range(len(in_lines)):
        if in_lines[i][-1] == "\n":
            in_lines[i] = in_lines[i][:-1]
    print(in_lines)


    # with open("%s.txt" % pws[:-4], 'w') as f: 
    #     print('hello')

