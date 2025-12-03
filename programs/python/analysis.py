
## Matthew A. Dorsey
## @mad-mpikg
## 2025.11.28
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences

## FILENAME: programs/python/plot.py
## PURPOSE: visualize results post analysis

## PACKAGES
# conda / native
import sys, os
import pandas as pd
import numpy as np
# import matplotlib as mplt
from plot.figure import Figure
from plot.plot import gen_plot
# local
# none

## PARAMETERES
# none

## METHODS
# none

## ARGUMENTS
# first argument: path to job directory
jd = sys.argv[1]
# second argument: job name 
jn = sys.argv[2]

## SCRIPT
# open the file
df_config = pd.read_csv("{0}/{1}/{1}.config.csv".format(jd, jn))
df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
df_sum = pd.read_csv("{0}/{1}/{1}.sum.csv".format(jd, jn))

# get the non-constant parameters from the config file
non_constant_col = []
for index, row in df_config.iterrows():
	if row['constant'] == 0:
		non_constant_col.append(row['key'])

# create normalized values based on model parameters
df_norm = pd.DataFrame(columns=['OT', 'E', 'K'])
for index, row in df_sum.iterrows():
	# ignore data when the time scale is less than 1.
	if row['OT'] < 1.0: continue
	# get the normalizing parameters
	e = df_sum.iloc[index]['EM']
	k = df_sum.iloc[index]['K']
	# normalize the oscillation period, normalize the energy
	T = df_sum.iloc[index]['OT'] * (k * e)
	E = df_sum.iloc[index]['c9'] / (e)
	df_norm.loc[index] = [T, df_sum.iloc[index]['c9'], df_sum.iloc[index]['K']]
	# print(df_norm.iloc[index]['OT'])
	# print(k, e)


# open the summary file, loop through all unique parameters
for k in non_constant_col:
	if k != 'OT': # ignore the oscillation period
		# plot normalized data
		fig = Figure()
		fig.load_data(df_norm, xcol = 'OT', ycol = 'E', icol = 'K')
		fig.add_format("$K$ = {:.1e}")
		fig.set_xaxis_label("Normalized Cycle Period ($T^{{*}} = T \\cdot (E \\cdot K \\cdot W^{{-2}}$))")
		fig.set_yaxis_label("Normalized Energy Dissipated ($W^{{*}} = W \\cdot E^{{-1}}$)")
		fig.set_xaxis_scale(log = True)
		# fig.set_yaxis_scale(log = True)
		gen_plot(fig, show = True, save = False)
		exit()

		# plot un-normalized data
		fig = Figure()
		fig.load_data(df_sum, xcol = 'OT', ycol = 'c9', icol = k)
		fig.set_title_label("{0}".format(jn))
		fig.set_xaxis_label("Cyclic Period ($s$)")
		fig.set_yaxis_label("Dissipated Energy per Cycle ($kJ$)")
		fig.set_cmap('Set2')
		fig.set_xaxis_scale(log = True)
		gen_plot(fig, show = True, save = False)
		exit()
		# plot normalized data
		# plot work and period against model parameter, fit
		# plot each unique frequency sweep, save to results
		for i in df_sum[k].unique():
			fig = Figure()
			fig.load_data(df_sum[df_sum[k] == i], xcol = 'OT', ycol = 'c9')
			fig.set_title_label("{0}".format(jn))
			fig.set_subtitle_label("{0}".format(i))
			fig.set_xaxis_label("Cyclic Period ($s$)")
			fig.set_yaxis_label("Dissipated Energy per Cycle ($kJ$)")
			fig.set_cmap('Set2')
			fig.set_xaxis_scale(log = True)
			gen_plot(fig, show = True, save = False)
			# exit()
