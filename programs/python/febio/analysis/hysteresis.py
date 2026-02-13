
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
from scipy.optimize import curve_fit, Bounds
# local
from plot.figure import Figure
from plot.plot import gen_bar_chart, gen_plot


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
## TODO seperate methods to make them more modular
## TODO extract max stress and strain as properties
## TODO return stress strain curves if requested
# cosine function
def cos_shift (t, delta):
    """ used to fit normalized amplitude data.

    Parameters:
    -----------
    t : float
        time data, x-axis
    delta : float (between -pi and pi)
        function phase shift

    Returns:
    --------
    float
        (1 / 2) * (cos (t + delta) + 1)
    """
    return 0.5 * (np.cos((2 * math.pi * t) - delta) + 1.)

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
    # determine the number of cycles that were performed
    err = []
    n_cyc = 1
    while True:
        err.append(time[-1] - n_cyc * period)
        if len(err) > 1:
            # is the error decreasing?
            if abs(err[-1]) > abs(err[-2]):
                # error increased from the previous calculation
                # the previous integer was the closest to the period
                n_cyc -= 1
                break
            else:
                n_cyc += 1
    # accumulate work for each cycle
    hys = [0.]
    # n = 0
    for i in range(len(time)):
        # if the current time is greater than the total simulation length
        if time[i] > period * n_cyc: break
        # accumulate the work done in each cycle
        if len(hys) < math.ceil(time[i] / period):
            if i > len(time) - num_prev_hys:
                ## TODO integrate force data to end using gap in time data
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

# calculate the complex modulus
def calculate_complex_mod (period, time, pos, force):
    """ calculate the complex modulus for each cycle in cyclic pertibation.

    Parameters:
    -----------
    period : float
        oscilation period in seconds.
    time : List[float]
        time at each point in the simulation.
    pos : List[float]
        position of rigid body, corresponing to time data
    force : List[float]
        reaction force on rigid body, corresponding to time data

    Return:
    -------
    List[float]
        dynamic loss modulus of each cycle.
    """
    ## get the stress strain information for each cycle, find the max
    # determine the number of cycles that were performed
    err = []
    n_cyc = 1
    while True:
        err.append(time[-1] - n_cyc * period)
        if len(err) > 1:
            # is the error decreasing?
            if abs(err[-1]) > abs(err[-2]):
                # error increased from the previous calculation
                # the previous integer was the closest to the period
                n_cyc -= 1
                break
            else:
                n_cyc += 1

    # loop through all points, accumulate stress and strain for each cycle
    dm = []
    t = [[] for i in range(n_cyc)]
    stress = [[] for i in range(n_cyc)]
    strain = [[] for i in range(n_cyc)]
    for i in range(len(time)):
        # accumulate stress strain data
        n = math.floor(time[i] / period)
        if n < n_cyc:
            t[n].append(time[i])
            stress[n].append(-pos[i])
            strain[n].append(force[i])

    ## initialize arrays
    # complex modulus properties
    delta = []
    dymod = []
    # min and max stress / strain for normalization
    max_strain = [[] for i in range(n_cyc)]
    min_strain = [[] for i in range(n_cyc)]
    max_stress = [[] for i in range(n_cyc)]
    min_stress = [[] for i in range(n_cyc)]
    # accumulate data for plotting
    x = []
    y = []
    l = []
    sub_int = n_cyc - 1
    ## loop through all cycles
    for i in range(n_cyc):

        ## get max and min stress / strain for cycle
        max_strain[i] = max(strain[i])
        min_strain[i] = min(strain[i])
        max_stress[i] = max(stress[i])
        min_stress[i] = min(stress[i])

        ## normalize each data point
        for j in range(len(stress[i])):
            t[i][j] = t[i][j] / period # reduce the time scale by the period
            # reduce the stress / strain by the max and minimum values
            stress[i][j] = (stress[i][j] - min_stress[i]) / (max_stress[i] - min_stress[i])
            strain[i][j] = (strain[i][j] - min_strain[i]) / (max_strain[i] - min_strain[i])

        ## determine the phase shift for the normalized strain data
        x_fit = t[i]
        y_fit = strain[i]
        popt, pcov = curve_fit(f = cos_shift, xdata =  x_fit, ydata = y_fit, bounds = Bounds(0., 2. * math.pi))
        delta_strain = popt[0]

        ## determine the phase shift for the normalized stress data
        x_fit = t[i]
        y_fit = stress[i]
        popt, pcov = curve_fit(f = cos_shift, xdata =  x_fit, ydata = y_fit, bounds = Bounds(0., 2. * math.pi))
        delta_stress = popt[0]

        ## NOTE right now the dynamic modulus displays behavior opposite
        ## to what one expects from literature (one expects the dynamic mod
        ## to be highest at fast cycles and lowest at slow cycles). 
        ## TODO Double check definitions
        # calculate the difference in phase shift between stress and strain, convert from radians to degrees
        delta.append((delta_stress - delta_strain) * (180. / (2. * math.pi)))
        # dynamic modulus is related to the phase shift according to:
        # max_stress / max_strain * cos(delta)
        dymod.append((max_stress[i] / max_strain[i]) * math.cos(delta[-1] * (2. * math.pi) / 180.))

        if i == sub_int:
            # append data to plot data frame if specified
            for j in range(len(stress[i])):
                # append strain
                x.append(t[i][j])
                y.append(strain[i][j])
                l.append('$\\varepsilon_{{norm}}$')
                # append stress
                x.append(t[i][j])
                y.append(stress[i][j])
                l.append('$\\sigma_{{norm}}$')

    df = pd.DataFrame.from_dict({'x': x, 'y': y, 'l': l})
    fig = Figure()
    fig.load_data(df, xcol = 'x', ycol = 'y', icol = 'l')
    fig.set_subtitle_label("$\\delta = {0:.4f}, Y' = {1:.2f}$".format(delta[sub_int], dymod[sub_int]))
    gen_plot(fig, show = False, save = False)

    return delta, dymod

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
