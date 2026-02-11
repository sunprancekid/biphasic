
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
# number of final time points to include with hystersis calculation
num_prev_hys = 30


## METHODS
# determine the work performed by each cycle in a hystersis loop
def calculate_hysteresis_work(period, time, work):
    """ calculate the work performed by oscillation.

    Parameters:
    -----------
    period : float
        oscilation period in seconds.
    time : List[float]
        time at each point in the simulation.
    work : List[float]
        change in work performed by rigid body at each point in the simulation.

    Return:
    -------
    List[float]
        work performed at each cycle
    """
    # determine the number of cycles which have occured
    hys = [0.]
    # loop through all point except the last one
    for i in range(len(time)):
        # print(i, time[i], work[i])
        # accumulate the work done in each cycle
        if len(hys) < math.ceil(time[i] / period):
            if i > len(time) - num_prev_hys:
                # if one the final time points,
                # integrate without splitting
                hys[-1] += work[i]
            else:
                # otherwise, the system has transitioned from one cycle to the next
                # split the work between the two cycles by averaging between time
                time_prev = time[i - 1]
                time_now = time[i]
                time_period = period * math.ceil(time_prev / period)
                hys[-1] += ((time_period - time_prev) / (time_now - time_prev)) * work[i]
                hys.append(((time_now - time_period) / (time_now - time_prev)) * work[i])
        else:
            hys[-1] += work[i]

    return hys

# determine the prework performed by the simulation during the relaxation phase

# calculate the dyanmic modulus
def calculate_dynamic_mod (period, time, work):
    """ calculate the dynamic loss modulus after each cycle.

    Parameters:
    -----------
    period : float
        oscilation period in seconds.
    time : List[float]
        time at each point in the simulation.
    work : List[float]
        change in work performed by rigid body at each point in the simulation.

    Return:
    -------
    List[float]
        dynamic loss modulus of each cycle.
    """
    return []

# calculate the loss modulus / phase shift


if __name__ == '__main__':
    ## ARGUMENTS
    # first argment: path to job directory
    jd = sys.argv[1]
    # second argument: job directory
    jn = sys.argv[2]
    # third argument: simulation integer
    simint = int(sys.argv[3])


    ## SCRIPT
    # open config, parameter files
    from febio.simulation import Simulation
    df_config = pd.read_csv("{0}/{1}/{1}.config.csv".format(jd, jn))
    df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
    sim = Simulation(jd, jn, simint)

    # estalish the path to the simulation directory
    sd = sim.sd

    # calulate hysteresis
    hys = sim.parse_hysteresis_work()

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
