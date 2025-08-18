
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
import matplotlib.pyplot as plt
# local
# none

## PARAMETERS
# nonzero exit code
nonzero_exitcode=120
# number of points to use in fit
n_fit = 100

## METHODS
# converts linear scale to log scale
def lin2log(x, base = 10.):
    return math.log(x) / math.log(base)

# converts log scale to linear scale
def log2lin (x, base = 10.):
    return math.pow(base, x)

# cauchy distribution function
def cauchy_dist (x, x0, gamma):
    return (1. / math.pi) * (gamma / (np.pow(x - x0, 2) + math.pow(gamma, 2)))


## ARGUMENTS
# first argument: path to file which contains hysteresis information
hys_file = sys.argv[1]

## SCRIPT
# open the file, find the columns which correspond to the period and the work data
df = pd.read_csv(hys_file)
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
for i in range(c):
    # parse the data from the csv
    p = df['period'].to_list()
    w = df['c{}'.format(i)].to_list()
    # convert the period to a logscale
    p_log = []
    for j in range(len(p)):
        p_log.append(lin2log(p[j]))

    # fit the data to cauchy distribution
    init = [ p_log[w.index(max(w))], 0.0000001] # initial values to start with
    popt, pcov = curve_fit(cauchy_dist, p_log, w, p0 = init)
    p_fit = [ ((max(p_log) - min(p_log)) / (n_fit - 1)) * j + min(p_log) for j in range(n_fit)]
    w_fit = [ cauchy_dist(x, *popt) for x in p_fit ]

    print(popt)
    print("The maximum period is {} seconds.".format(log2lin(popt[0])))

    # plot to double check
    fig, ax = plt.subplots()
    plt.plot(p_fit, w_fit, 'k--',   label = "Cauchy Fit"    )
    plt.plot(p_log,     w,  'rx',   label = "Hystersis Data")
    plt.legend(loc = 'upper right')
    plt.show()
    exit()

    # print(popt)
    # exit()
    #
    # print("The maximum period is {} seconds".format(popt[0]))

    for j in range(len(p_fit)):
        print(j, p_fit[j], w_fit[j])

    res = 0.
    for j in range(len(w)):
        res += math.pow(w[j] - cauchy_dist(p_log[j], *popt), 2)

    # find the maximum
    # write to file

