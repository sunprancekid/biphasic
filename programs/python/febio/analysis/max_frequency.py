
## Matthew Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.15
## from hysterseis data, determine the period at which the work done by cyclical bending is maximum

## PACKAGES
# native / from conda
import sys, os, math
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit # used for curve fitting
from scipy.signal import savgol_filter as sg
import matplotlib.pyplot as plt
# local
# used for filter, fitting, and smoothing data
from util.smoothie import lin2log, log2lin
from util.smoothie import poly_smooth as psmooth

## PARAMETERS
# nonzero exit code
nonzero_exitcode=120
# number of points to use in fit
n_fit = 100
# boolean that determines if the fitting should be plotted
plot = False
# name of file used to store work information
hys_out = "hys.out.csv"
# file that contains maximum frequency predictions
mf_out = "mf.out.csv"

## METHODS
# none


## ARGUMENTS
# first argument: path to directory which contains hysterseis file
hys_path = sys.argv[1]
# second argument: file that contains the hysteresis / cycle information
hys_file = sys.argv[2]


## SCRIPT
# open the file, find the columns which correspond to the period and the work data
df = pd.read_csv(hys_path + hys_file)
head = list(df.columns.values)

# check if the header has columns corresponding to the period
if not "period" in head:
    print("ERROR :: max_frequency :: unable to find column containing cycle period (assumed 'period')")
    exit(nonzero_exitcode)

# determine how many cycles were performed
c = 0
while True:
    if "c{}".format(c) in head:
        c += 1
    else:
        break

## loop through each cycle, fit data to work data
mf = []
for i in range(c):
    # parse the data from the csv
    p = df['period'].to_list()
    w = df['c{}'.format(i)].to_list()
    # convert the period to a logscale
    p_log = []
    for j in range(len(p)):
        p_log.append(lin2log(p[j]))

    p_filter, w_filter = psmooth (x = p_log, y = w, order = 2, window = len(p_log) - 23, n_fit = 90)
    # find the maximum
    mf.append(log2lin(p_filter[w_filter.index(max(w_filter))]))
    print ("For cycle {} the maximum period is {} seconds.".format(i, mf[-1]))

    if plot:
        # plot to double check
        fig, ax = plt.subplots()
        plt.plot(p_filter, w_filter, 'k--', label = "SG Filter")
        plt.plot(p_log, w, 'rx', label = "Hystersis Data")
        plt.legend(loc = 'upper right')
        plt.show()

# export results to a csv
# write header and cycle information
header = ""
cycle = ""
for i in range(len(mf)):
    header += "c{}".format(i)
    cycle += "{}".format(mf[i])
    if i != (len(mf) - 1):
        header += ","
        cycle += ","

with open(hys_path + mf_out, 'w') as s_io:
    s_io.writelines("{}\n".format(header))
    s_io.writelines("{}\n".format(cycle))

