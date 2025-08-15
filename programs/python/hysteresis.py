
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## determine the work performed by cyclical beam bending, plot hystersis


## PACKAGES
# native / from conda
import sys, os, math
import pandas as pd
import numpy as np
# local
# none


## PARAMETERS
# nonzero exit code for faulty method execution
nonzero_exitcode = 120
# name of csv file containing displacment information
febio_out = "febio4.out.csv"
# name of file used to store work information
hys_out = "hys.out.csv"


## METHODS
# none


## ARGUMENTS
# first argment: path to directory containing febio output and displacement information
path = sys.argv[1]
# second argument: cycle period (in seconds)
period = float(sys.argv[2])


## SCRIPT
## TODO :: plot the force-displacement data as hysteresis loops

# check if the file exists
if not os.path.exists(path + febio_out):
    # if the file does not exist, inform the user
    print("ERROR :: hystersis :: unable to find file {}{} ..".format(path, febio_out))
    exit(nonzero_exitcode)

# open the file, get the time and the work
df = pd.read_csv(path + febio_out)
time = df['t'].to_list()
work = df['dw_fvdt'].to_list()
# determine the number of cycles which have occured
n_cyc = math.floor(time[-1] / period)
hys = [0.]
for i in range(len(time)):
    # accumulate the work done in each cycle
    if len(hys) < math.ceil(time[i] / period):
        hys.append(0.)
    hys[-1] += work[i]

# export the file as a csv
# write header and cycle information
header = ""
cycle = ""
for i in range(len(hys)):
    header += "c{}".format(i)
    cycle += "{}".format(hys[i])
    if i != (len(hys) - 1):
        header += ","
        cycle += ","

# print("\n{}\n{}\n".format(header,cycle))

with open(path + hys_out, 'w') as s_io:
    s_io.writelines("{}\n".format(header))
    s_io.writelines("{}\n".format(cycle))
