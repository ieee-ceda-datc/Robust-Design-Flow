#!/bin/python
'''
Input: Provide the run dir full path
'''
import os
import sys
import re

liberty_file = sys.argv[1]
scale_factor = float(sys.argv[2])

flag = os.path.exists(liberty_file)

if flag:
    with open(liberty_file) as f:
        contents = f.read().splitlines()
    f.close()

    for line in contents:
        items = line.split()
        if (len(items) == 2):
            if (items[0] == 'capacitance:' or items[0] == 'fall_capacitance:' or items[0] == 'rise_capacitance:'):
                capValue = items[1].split(';')
                newCap = round(float(capValue[0]) * scale_factor, 6)
                print(f"		{items[0]}		: {newCap};")
            else:
                print(f"{line}")
                pass
        else:
            print(f"{line}")
            pass

