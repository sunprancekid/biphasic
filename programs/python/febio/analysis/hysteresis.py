
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
import xml.etree.ElementTree as ET
# local
from febio.simulation import Simulation


## PARAMETERS
# nonzero exit code for faulty method execution
nonzero_exitcode = 120
# name of csv file containing displacment information
febio_out = "febio4.out.csv"
# name of file used to store work information
hys_out = "hys.out.csv"
# prestress relaxation step size - xml path
xml_relax_step_size = "Step/step[@id='1']/Control/step_size"
# prestress relaxation number of steps - xml path
xml_relax_num_step = "Step/step[@id='1']/Control/time_steps"


## METHODS
# none


## ARGUMENTS
# first argment: path to job directory
jd = sys.argv[1]
# second argument: job directory
jn = sys.argv[2]
# third argument: simulation integer
simint = int(sys.argv[3])


## SCRIPT
# open config, parameter files
df_config = pd.read_csv("{0}/{1}/{1}.config.csv".format(jd, jn))
df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
sim = Simulation(jd, jn, simint)

# estalish the path to the simulation directory
sd = "{0}/{1}/{2}".format(jd, jn,  df_parm.iloc[simint]['path'])
# get the cycle period
period = float(df_parm.iloc[simint]['OT'])
# get the relaxation time
# if sim.has_key('RT'):
#     # if the column header is in the parameter file
#     relax_time = sim.get_key_value('RT')
# else:
# get the relaxation time from the feb file
# step size
steps = int(sim.get_feb_path_value(xml_relax_num_step))
# number of steps
size = float(sim.get_feb_path_value(xml_relax_step_size))
# calculate the relaxation time
relax_time = size * steps

print(relax_time)
exit()


## TODO :: plot the force-displacement data as hysteresis loops

# check if the file exists
if not os.path.exists(sd + febio_out):
    # if the file does not exist, inform the user
    print("ERROR :: hystersis :: unable to find file {}{} ..".format(sd, febio_out))
    exit(nonzero_exitcode)

# open the file, get the time and the work
df = pd.read_csv(sd + febio_out)

# drop the first 10000 seconds of simulation data
df.drop(df[df['t'] <= relax_time].index, inplace = True)
df['t'] = df['t'] - relax_time

# parse data
time = df['t'].to_list()
work = df['dw_fdx'].to_list()
# determine the number of cycles which have occured
n_cyc = math.floor(time[-1] / period)
hys = [0.]
for i in range(len(time)):
    # print(i, time[i], work[i])
    # accumulate the work done in each cycle
    if len(hys) < math.ceil(time[i] / period):
        # here, the system has transitioned from one cycle to the next
        # split the work between the two cycles by averaging between time
        time_prev = time[i - 1]
        time_now = time[i]
        time_period = period * math.ceil(time_prev / period)
        hys[-1] += ((time_period - time_prev) / (time_now - time_prev)) * work[i]
        hys.append(((time_now - time_period) / (time_now - time_prev)) * work[i])
    else:
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

with open(sd + hys_out, 'w') as s_io:
    s_io.writelines("{}\n".format(header))
    s_io.writelines("{}\n".format(cycle))
