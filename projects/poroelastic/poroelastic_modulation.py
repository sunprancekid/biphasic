
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max Planck Institute for Colloids and Interfaces
## 2026.02.19

## FILENAME: projects/poroelastic/poroelastic_modulation.py
## PURPOSE: sysmteatically vary the poroelastic parameters, extract pressure and stress data

## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from febio.job import Job
from febio.feb.model import Model


## PARAMETERS
# model file
feb_model = 'models/uniax/comp.feb'
# absolute path to remote data
rmt_dir = "/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# number of oscillation cycles
n_cycles = 10
# number of steps per cycle
n_steps = 60
# loading depth (mm), unless otherwise specified
default_loading_depth = 0.01
# relaxation time (s), unless otherwise specified
default_relaxation_time = 10000
# oscillation amplitude (mm), unless otherwise specified
default_oscillation_amplitude = 0.005
# lowest oscillation period to test (s), unless otherwise specified
default_period_low = 10.
# highest oscillation period to test (s), unless otherwise specified
default_period_high = 100000. # one hundred thousand, 1e6
# number of period values to test in between highest and lowest, unless otherwise specified
default_period_n = 40
# default constant bulk modulus
default_bulk = 0.01129
# default material permeability
default_perm = 0.01
# maps length scale to specific feb files
scale_dict = { '0.05': 'models/uniax/scale/comp/0.05.feb',
			   '0.08': 'models/uniax/scale/comp/0.08.feb',
			  '0.125': 'models/uniax/scale/comp/0.125.feb',
			   '0.20': 'models/uniax/scale/comp/0.2.feb',
			   '0.50': 'models/uniax/scale/comp/0.5.feb',
			   '1.00': 'models/uniax/scale/comp/1.0.feb'}


## METHODS
def constant_bulk_modulus (job, E_val = default_bulk):
	""" specify constant bulk modulus.

	Paramters:
	----------
	job : Job
		contains job parameters.
	E_val : float (default is 'default_bulk')
		constant bulk modulus value

	Returns:
	--------
	Job
		'job' with additional parameter.
	"""
	# constant bulk modulus
	job.add_constant_parameter(val = E_val,
		key = "E",
		xml = "Material/material[@id='1']/solid/E",
		units = "MPa",
		description = "bulk_modulus")

def constant_permeability(job, K_val = default_perm):
	"""

	Arguments:
	----------
	None

	Returns:
	--------
	None
	"""
	# set the permeability for the job constant
	job.add_constant_parameter(val = K_val,
		key = "K",
		xml = "Material/material[@id='1']/permeability/perm",
		units = "MPa",
		description = "permeability")

def frequency_sweep (job, loading_depth = default_loading_depth, relaxation_time = default_relaxation_time, oscillation_amplitude = default_oscillation_amplitude, period_low = default_period_low, period_high = default_period_high, period_n = default_period_n):
	""" add pre-stress and oscillation frequency to job.

	Parameters:
	-----------
	job : Job
		contains job parameters.
	loading_depth : float (default is 'default_loading_depth')
		depth of prestress (in mm)
	relaxation_time : float (default is 'default_relaxation_time')
		length prestress holding before starting oscillation sequence
	oscillation_amplitude : float (default is 'default_oscillation amplitude')
		oscllation amplitude (in mm)
	period_low : float (default is 'default_period_low')
		lowest oscillatory period to test in frequency sweep
	period_high : float (default is 'default_period_high')
		highest oscillatory period to test in frequency sweep
	period_n : int (default is 'default_period_n')
		number of osillatory values to test between highest and lowest values

	Returns:
	--------
	Job
		job provided to method as argument with additional parameters

	"""
	# add loading routine - constant
	job.add_constant_parameter(val = loading_depth,
		key = 'LD',
		xml = "Step/step[@id='1']/Rigid/rigid_bc[@name='tip_displacement']/value",
		description = "loading_discplacement",
		units = "mm",
		related = False)
	# add oscillation amplitude - constant
	job.add_constant_parameter(val = oscillation_amplitude,
		key = 'OA',
		xml = "Step/step[@id='2']/Rigid/rigid_bc[@name='tip_oscillation']/value",
		units = "mm",
		related = False)
	job.add_constant_parameter(val = 0.1,
		key = 'RTss',
		xml = "Step/step[@id='1']/Control/step_size",
		units = None,
		description = 'loading_step_size',
		related = False)
	job.add_constant_parameter(val = "RT / RTss",
		key = 'RTn',
		xml = "Step/step[@id='1']/Control/time_steps",
		units = None,
		description = 'loading_number_steps',
		related = True)
	# add relaxation time - constant
	## NOTE: this parameter needs to go after the other relaxation parameters due to overlapping keys / replacement dependencies
	job.add_constant_parameter(val = relaxation_time,
		key = 'RT',
		xml = None,
		units = 'seconds',
		description = 'loading-hold-time',
		related = False)
	# add oscillation frequency - variable
	job.add_variable_parameter (minval = period_low,
		maxval = period_high,
		nval = period_n,
		log = True,
		key = "OT",
		xml = None,
		units = "s",
		description = "oscillation_period")
	# oscillation equation
	job.add_constant_parameter (val = "0.5*sin((2*{0}/OT)*(t-RT))".format(3.14159265359),
		key = "OTMa",
		xml = "LoadData/load_controller[@name='tip_oscillation_controller']/math",
		units = None,
		description = "tip_oscillation_equation",
		related = True,
		symbolic = True)
	# number of cycles
	job.add_constant_parameter(val = n_cycles,
		key = "NCy",
		description = "number_oscillation_cycles")
	# number of nsteps per cycle
	job.add_constant_parameter (val = n_steps,
		key = "NOSs",
		description = "number_steps_per_oscillation_cycle")
	# total number of numerical steps
	job.add_constant_parameter (val = "NCy * NOSs * 10",
		key = "ON",
		xml = "Step/step[@id='2']/Control/time_steps",
		units = None,
		description = "oscillation_total_numerical_steps",
		related = True)
	job.add_constant_parameter (val = "(OT) / (NOSs)",
		key = "OSMx",
		xml = "Step/step[@id='2']/Control/time_stepper[@type='default']/dtmax",
		units = None,
		description = "oscillation_max_step",
		related = True)
	job.add_constant_parameter (val = "(OT) / (NOSs * 10)",
		key = "OSMn",
		xml = "Step/step[@id='2']/Control/step_size",
		units = None,
		description = "oscillation_initial_step",
		related = True)

## CLASSES
# none


if __name__ == "__main__":

	## ARGUMENTS
	# first argument: job directory
	jd = sys.argv[1]
	# second argument: job id
	jn = sys.argv[2]

	## TODO add model file to job, generate dictionaries and write feb file

	## SCRIPT
	# data frames for scaling job
	df_parm = None
	df_config = None
	# for each key in the scale_dict
	z_int = 0
	for z, i in zip(list(scale_dict.keys()), range(len(scale_dict.keys()))):
		## load model, update saving parameters
		m = Model(scale_dict[z])
		m.add_element_data_to_logfile_output(elements = [1, 226, 451, 676, 901, 1126, 1351, 1576, 1601, 2026, 2251, 2576, 2701, 2926, 3151, 3376, 3601, 3826, 4051, 4276, 4501, 4726, 4951, 5176, 5401, 5626, 5851, 6076, 6301, 6526], properties = ['p', 'effective stress', 'z'], delim = ",", filename = 'elm.dat')
		## TODO write model to directory

		## establish the job, parameters
		j = Job ("{0}{1}/".format(jd, jn), 'z{0}'.format(i))
		constant_bulk_modulus(job = j)
		constant_permeability(job = j)
		# vary the time scale according to the anticipated maximum
		ts = 100 * pow(float(z), 2.) / (default_bulk * default_perm) # for beam compression, the normalized peak occurs at 100.
		if ts < 10.: continue # if the time scale is too low, skip and continue
		ts_period_low = ts / 100 # the lowest value to test is two orders of magnitude less than the anticipated maximum
		if ts_period_low < 1.: ts_period_low = 1. # the lowest value to test is 1.
		ts_period_high = ts * 100

		## here, the loading depth oscilation amplitude, etc. depend on the length scale
		loading_depth = default_loading_depth * (float(z) / 0.125)
		oscillation_amplitude = default_oscillation_amplitude * (float(z) / 0.125)
		frequency_sweep(job = j, period_low = ts_period_low, period_high = ts_period_high, loading_depth = loading_depth, oscillation_amplitude = oscillation_amplitude)

		## save job, model
		# save model to the directory
		m.save_model(saveto = "{0}{1}/z{2}/".format(jd, jn, i), saveas = "{0}-z{1}.feb".format(jn, i))
		# generate parmeters
		if not j.has_parameters():
			j.generate_parameters()
		# save config, parameter files
		j.save_config()
		j.save_parameters()

		## write sweep to job file
		# copy the sweep parameter file
		df_parm_tmp = pd.read_csv("{0}{1}/z{2}/z{2}.parm.csv".format(jd, jn, i))
		# add scaling integer as parameter, update path
		df_parm_tmp['z'] = [z for j in range(len(df_parm_tmp))]
		for index, row in df_parm_tmp.iterrows():
			if df_parm is not None:
				df_parm_tmp.loc[index, 'n'] = int(df_parm.loc[len(df_parm) - 1, 'n']) + index + 1
			df_parm_tmp.loc[index, 'path'] = "z{0}/{1}".format(i, df_parm_tmp.loc[index, 'path'])
			df_parm_tmp.loc[index, 'id'] = "{1}".format(i, df_parm_tmp.loc[index, 'id'])
		# update job parameter
		if df_parm is None:
			df_parm = df_parm_tmp
		else:
			df_parm = pd.concat([df_parm, df_parm_tmp], ignore_index = True, sort = False)

		if df_config is None:
			df_config = pd.read_csv("{0}{1}/z{2}/z{2}.config.csv".format(jd, jn, i))

	# write parameter file, update config
	df_parm.to_csv("{0}{1}/{1}.parm.csv".format(jd, jn), index = False)
	df_config.loc[-1] = ['z', 'na', 'mm', 'scaling_value', '0', '0', '0', 'na', list(scale_dict.keys())[0], list(scale_dict.keys())[-1], 'na', 'na']
	df_config.index = df_config.index + 1
	df_config = df_config.sort_index()
	df_config.to_csv("{0}{1}/{1}.config.csv".format(jd, jn), index = False)


