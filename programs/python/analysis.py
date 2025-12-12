
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
from plot.fit import Line, fit_line
# local
# none

## PARAMETERS
# assumed elastic modulus, unless specified (Pa)
emod_base_val = 500000
# assumed permeability, unless specified (mm^4 / N s)
perm_base_val = 0.001
# assumed beam width, unless specified (mm)
width_base_val = 0.125
# assumed oscillation amplitude, unless specified (mm)
amp_base_val = 0.05

## METHODS
# none

## ARGUMENTS
# first argument: path to job directory
jd = sys.argv[1]
# second argument: job name 
jn = sys.argv[2]

## SCRIPT
# open the file
savedir = "{0}/{1}/results/".format(jd, jn)
df_config = pd.read_csv("{0}/{1}/{1}.config.csv".format(jd, jn))
df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
df_sum = pd.read_csv("{0}/{1}/{1}.sum.csv".format(jd, jn))

# parse the constant and non constant parameters from the config file
non_constant_col = []
constant_col = []
for index, row in df_config.iterrows():
	# skip the oscillation period
	if row['key'] == 'OT': continue
	# sort all other parameters by constant or non-constant
	if row['constant'] == 0:
		# the key is not constant
		non_constant_col.append(row['key'])
	else:
		# the key is constant over the course of the simulations
		constant_col.append(row['key'])

# create normalized values based on model parameters
norm_col_init =['T', 'A', 'OT', 'W', 'EM', 'K', 'OA', 'Z'] # initial parameters
norm_cols = norm_col_init.copy() # columns eventually used with data frame
for k in non_constant_col:
	# for any other tested parameters which aren't in the initial set
	if k not in norm_cols:
		norm_cols.append(k)
df_norm = pd.DataFrame(columns=norm_cols)
for index, row in df_sum.iterrows():
	# ignore data when the time scale is less than 1.
	if row['OT'] < 1.0: continue

	# parse the elastic modulus
	if 'EM' in non_constant_col or 'EM' in constant_col:
		e = df_sum.iloc[index]['EM']
	else:
		e = emod_base_val

	# parse the permeability
	if 'K' in non_constant_col or 'K' in constant_col:
		k = df_sum.iloc[index]['K']
	else:
		k = perm_base_val

	# parse the loading depth
	if 'OA' in non_constant_col or 'OA' in constant_col:
		a = df_sum.iloc[index]['OA']
	else:
		a = amp_base_val

	# parse the beam width
	if 'Z' in non_constant_col or 'Z' in constant_col:
		z = df_sum.iloc[index]['Z']
	else:
		z = width_base_val

	## TODO :: automate determining the final column which/ 1000000000 contains the amplitude (here, 'c9')
	# get the normalizing parameters
	# normalize the oscillation period, normalize the energy
	T = df_sum.iloc[index]['OT'] * (k * e / pow(z, 2))
	A = df_sum.iloc[index]['c9'] / (e * pow(a, 2) * pow(z, 3))
	row = [T, A, df_sum.iloc[index]['OT'], df_sum.iloc[index]['c9'] * 1000000000, e, k, a, z]
	for k in non_constant_col:
		if k not in norm_col_init:
			# append any additional data which has not be included with the initial data set
			row.append(df_sum.loc[index][k])
	df_norm.loc[index] = row


# open the summary file, loop through all unique parameters
for k in non_constant_col:
	if k != 'OT': # ignore the oscillation period
		# plot normalized data
		fig = Figure()
		fig.load_data(df_norm, xcol = 'T', ycol = 'A', icol = k)
		fig.add_format("${0}$ ".format(k) + "= {:.1e}")
		fig.set_xaxis_label("Normalized Cycle Period ($T^{{*}} = T \\cdot (E \\cdot K \\cdot Z^{{-2}}$))")
		fig.set_yaxis_label("Normalized Energy Dissipated ($A^{{*}} = A \\cdot (E^{{-1}} \\cdot Z^{{-3}})$)")
		fig.set_xaxis_scale(log = True)
		# fig.set_yaxis_scale(log = True)
		fig.set_saveas(savedir = savedir, filename = 'sweep_norm')
		gen_plot(fig, show = False, save = True)

		# plot un-normalized data
		fig = Figure()
		fig.load_data(df_norm, xcol = 'OT', ycol = 'W', icol = k)
		fig.add_format("${0}$ ".format(k) + "= {:.1e}")
		fig.set_xaxis_label("Cyclic Period ($s$)")
		fig.set_yaxis_label("Dissipated Energy per Cycle ($pJ$)")
		fig.set_cmap('Set2')
		fig.set_xaxis_scale(log = True)
		fig.set_saveas(savedir = savedir, filename = 'sweep')
		gen_plot(fig, show = False, save = True)
		# exit()

		# from each unique parameter
		# plot frequency sweep, save to results
		n = 0
		df_parm = pd.DataFrame(columns = [k, 'T', 'A'])
		for i in df_norm[k].unique():
			# collect the resonant amplitude and period
			df_temp = df_norm[df_norm[k] == i].reset_index()
			# here, is there a better way to identify the maximum (with curve fitting)
			mx_idx = df_temp.index[df_temp['W'] == df_temp['W'].max()].to_list()
			df_parm.loc[n] = [i, df_temp.iloc[mx_idx[0]]['OT'], df_temp.iloc[mx_idx[0]]['W'] ]
			n = n+1
			continue
			# plot, save the frequency sweep
			fig = Figure()
			fig.load_data(df_temp, xcol = 'OT', ycol = 'c9')
			fig.set_title_label("{0}".format(jn))
			fig.set_subtitle_label("{0}".format(i))
			fig.set_xaxis_label("Cyclic Period ($s$)")
			fig.set_yaxis_label("Dissipated Energy per Cycle ($kJ$)")
			fig.set_cmap('Set2')
			fig.set_xaxis_scale(log = True)
			gen_plot(fig, show = True, save = False)
			# exit()

		# fit power law to resonant period
		# TODO :: move the plot variables above the figure (for plot, as well as scatter)
		# TODO :: adjust plot dimensions as method argument
		# TODO :: add power fit (rather than just a"{0}/{1}/{1}.config.csv" linear fit on a log scale)
		# TODO :: include R^2 value with fit label (automatically)
		fit = fit_line(x = df_parm[k].to_list(), y = df_parm['T'].to_list(), log = True)
		fit_parms = fit.get_parameters()
		fit.set_label("${0} \\propto T^{{{1:.02f}}}$".format(k, fit_parms[0]))
		fit.set_linecolor("k")
		fit.set_linestyle(":")

		# plot the resontant frequency against the model parameter with fit
		# TODO :: combine both figures with secondary y-axis
		df_key = df_config.loc[df_config['key'] == k].reset_index()
		fig = Figure()
		xax_str = "{0} (${1}$)".format(df_key.iloc[0]['description'].replace('_', ' ').title(), df_key.iloc[0]['units'])
		fig.load_data(df_parm, xcol = k, ycol = 'T')
		fig.set_xaxis_label(xax_str)
		fig.set_yaxis_label('Resontant Period ($s$)')
		fig.set_xaxis_scale(log = True)
		fig.set_yaxis_scale(log = True)
		fig.set_saveas(savedir = savedir, filename = 'Tv{0}'.format(k))
		gen_plot(fig, linewidth = 0, markersize = 8, show = False, save = True, fit = fit)

		# fit power law to resonant amplitude
		fit = fit_line(x = df_parm[k].to_list(), y = df_parm['A'].to_list(), log = True)
		fit_parms = fit.get_parameters()
		fit.set_label("${0} \\propto A^{{{1:.02f}}}$".format(k, fit_parms[0]))
		fit.set_linecolor("k")
		fit.set_linestyle(":")

		# plot the resonant amplitude against the model parameter with fit
		fig = Figure()
		fig.load_data(df_parm, xcol = k, ycol = 'A')
		fig.set_xaxis_label(xax_str)
		fig.set_yaxis_label('Resonant Amplitude ($pJ$)')
		fig.set_xaxis_scale(log = True)
		# TODO :: adjust yaxis scale to handle constant values with log value (potentially through a variance calcuation?)
		fig.set_yaxis_scale(log = True)
		fig.set_saveas(savedir = savedir, filename = 'Av{0}'.format(k))
		gen_plot(fig, linewidth = 0, markersize = 8, show = False, save = True, fit = fit)

		# save the data frame
		if not os.path.exists("{0}/{1}/results".format(jd, jn)):
			os.makedirs("{0}/{1}/results".format(jd, jn))
		df_norm.to_csv("{0}/{1}/results/normalized.csv".format(jd, jn), index = False)

