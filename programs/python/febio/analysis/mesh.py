
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2026.01.16

## FILENAME: programs/python/febio/analysis/mesh.py
## PURPOUSE: meshing study post-processing and analysis


## MODULES
# native / conda
import sys, os, math
import statistics as stat
import pandas as pd
# local
from plot.figure import Figure
from plot.plot import gen_plot
from febio.io.plotfile import XPLT


## PARAMETERS
# write analysis process to command line
verbose = True
# show graphs
show = False
# save graphs
save = True


## METHODS
# none


## ARGMENTS
# first argument: directory
jd = sys.argv[1]
# second argument: job
jn = sys.argv[2]


## SCRIPT
# filenames and directories
savedir = "{0}/{1}/results/".format(jd, jn)
df_config = pd.read_csv("{0}/{1}/{1}.config.csv".format(jd, jn))
df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
df_sum = pd.read_csv("{0}/{1}/{1}.sum.csv".format(jd, jn))

# find NM, NE, and OT in config file
# loop through simulations
NE = []
cpu_time = []
hys = []
force_max = []
stress_max = []
for index, row in df_sum.iterrows():

    # parse cpu time, hysteresis, max stress ...
    NE.append(eval(row['NE'].replace('NM',str(row['NM']))))
    hys.append(row['c9'])
    t = row['time_total'].split(':')
    cpu_time.append(int(t[0]) * 60 * 60 + int(t[1]) * 60 + int(t[2]))

    ## extract the maximum force from the febio out files
    df_febout = pd.read_csv("{0}/{1}/{2}febio4.out.csv".format(jd, jn, row['path']))
    force_max.append(df_febout['F_mag'].max())

    ## TODO extract maximum stress from the XPLT file
    if verbose: print("\nFinding max stress element for simulation {0}..".format(row['id']))
    xplt_file = "{0}/{1}/{2}{3}.xplt".format(jd, jn, row['path'], row['id'])
    xplt = XPLT(xplt_file)
    # find that states that correspond to a certain time period
    state = xplt.get_state_at_time(10.)
    # find that element with max strain in that time period
    stress = xplt.get_field_values(field = 'solid stress', state = state)
    max_stress_element = 1
    for e in xplt.get_elements():
        if stress.iloc[0][e] > stress.iloc[0][max_stress_element]:
            # print(e)
            max_stress_element = e

    # use that element to find max stress at all states
    if verbose: print("Parsing maximum stress for element {0} in simulation {1}..".format(max_stress_element, row['id']))
    elem_subset = [max_stress_element]
    stress = xplt.get_field_values(field = 'solid stress', element = elem_subset)
    del xplt
    # find the maximum value
    max_s = 0.
    for e in elem_subset:
        comp_s = stress[e].max()
        if comp_s > max_s:
            max_s = comp_s
    if verbose: print("Max stress is {0}.".format(max_s))
    stress_max.append(max_s)

## ERROR CALCULATIONS
x_err = []
y_err = []
l_err = []

# error in hystersis calculation
hys_err = []
hys_true = hys[-1]
for i in range(len(hys)):
    hys_err.append((abs(hys[i] - hys_true) / hys_true) * 100)
# the final error is by definition 0 so replace it with an average
hys_err[-1] = stat.mean(hys_err[-2:])
for i in range(len(hys_err)):
    x_err.append(NE[i])
    y_err.append(hys_err[i])
    l_err.append("Hystersis")
    if verbose: print("{0} : {1} : {2}".format(x_err[-1], y_err[-1], l_err[-1]))

# error in force calculation
f_true = force_max[-1]
f_err = []
for i in range(len(force_max)):
    f_err.append((abs(force_max[i] - f_true) / f_true) * 100)
# final error is by definitiion 0 so it is replaced with an average of the last two values
f_err[-1] = stat.mean(f_err[-2:])
for i in range(len(f_err)):
    x_err.append(NE[i])
    y_err.append(f_err[i])
    l_err.append("Maximum Force")
    if verbose: print("{0} : {1} : {2}".format(x_err[-1], y_err[-1], l_err[-1]))

# error in stress calculation
s_true = stress_max[-1] # the true value is the final, most detailed simulation
s_err = []
for i in range(len(stress_max)):
    s_err.append((abs(stress_max[i] - s_true) / s_true) * 100)
# final error is by definition zero, so replace with an average
s_err[-1] = stat.mean(s_err[-2:])
for i in range(len(s_err)):
    x_err.append(NE[i])
    y_err.append(s_err[i])
    l_err.append("Maximum Stress")
    if verbose: print("{0} : {1} : {2}".format(x_err[-1], y_err[-1], l_err[-1]))

## PLOT
# plot - clock time against number of elements
df_plot_cpu = pd.DataFrame.from_dict({'NE': NE, 'cpu': cpu_time})
fig = Figure()
fig.load_data(d = df_plot_cpu, xcol = 'NE', ycol = 'cpu')
fig.set_saveas(savedir = savedir, filename = 'cpu')
fig.save_data()
fig.set_xaxis_scale(log = True)
fig.set_yaxis_scale(log = True)
fig.set_yaxis_label('Simulation Clock Time (seconds)')
fig.set_xaxis_label('Number of Meshing Elements')
gen_plot(fig, show = show, save = save)


df_plot_err = pd.DataFrame.from_dict({'x': x_err, 'y': y_err, 'l': l_err})
# plot - calculation error against number of elements
fig = Figure()
fig.load_data(d = df_plot_err, xcol = 'x', ycol = 'y', icol = 'l')
fig.set_saveas(savedir = savedir, filename = 'err')
fig.save_data()
fig.set_xaxis_scale(log = True)
fig.set_yaxis_scale(log = True)
fig.set_yaxis_label('Error in Calculation (%)')
fig.set_xaxis_label('Number of Meshing Elements')
fig.set_cmap('Dark2')
gen_plot(fig, show = show, save = save)
