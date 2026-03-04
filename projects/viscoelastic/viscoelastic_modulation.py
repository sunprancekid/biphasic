
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max Planck Institute for Colloids and Interfaces
## 2026.02.19

## FILENAME: projects/viscoelastic/viscoelastic_modulation.py
## PURPOSE: sysmteatically vary the viscoelastic parameters

## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from febio.job import Job


## PARAMETERS
# absolute path to remote data
rmt_dir = "/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# number of oscillation cycles
n_cycles = 11
# number of steps per cycle
n_steps = 60
# loading depth (mm)
loading_depth = 0.025
# oscillation amplitude (mm)
oscillation_amplitude = 0.01
# relaxation time (s)
relaxation_time = 10000
# default first elastic modulus
default_E1_val = 1.129
# default second elastic modulus
default_E2_val = 7.014
# default second viscosity
default_n2_val = 3355
# default bulk modulus
default_bulk = default_E1_val
# default first relaxation modulus constant
default_g1_val = (default_E2_val / default_E1_val)
# default first time constant
default_t1_val = (default_n2_val / default_E2_val)


## METHODS
# none


## CLASSES
# none


## ARGUMENTS
# first argument: job directory
jd = sys.argv[1]
# second argument: job id
jn = sys.argv[2]


## SCRIPT
# create job
j = Job (jd, jn)

## add parameters
# loading depth is constant
if not j.has_config():
	j.add_constant_parameter(val = loading_depth,
		key = 'LD',
		xml = "Step/step[@id='1']/Rigid/rigid_bc[@name='tip_displacement']/value",
		description = "loading_discplacement",
		units = "mm",
		related = False)
	# oscillation amplitude is constant
	j.add_constant_parameter(val = oscillation_amplitude,
		key = 'OA',
		xml = "Step/step[@id='2']/Rigid/rigid_bc[@name='tip_oscillation']/value",
		units = "mm",
		related = False)
	j.add_constant_parameter(val = 0.1,
		key = 'RTss',
		xml = "Step/step[@id='1']/Control/step_size",
		units = None,
		description = 'loading_step_size',
		related = False)
	j.add_constant_parameter(val = "RT / RTss",
		key = 'RTn',
		xml = "Step/step[@id='1']/Control/time_steps",
		units = None,
		description = 'loading_number_steps',
		related = True)
	# relaxation time is constant
	j.add_constant_parameter(val = relaxation_time,
		key = 'RT',
		xml = None,
		units = 'seconds',
		description = 'loading-hold-time',
		related = False)

	## establish the materials parameters
	# the first elastic modulus varies
	# j.add_constant_parameter(val = default_E1_val,
	# 	key = "E1",
	# 	xml = None,
	# 	units = 'MPa',
	# 	description = "emod_1",
	# 	related = False)
	# # the second elastic modulus varies
	# j.add_constant_parameter(val = default_E2_val,
	# 	key = "E2",
	# 	xml = None,
	# 	units = 'MPa',
	# 	description = "emod_2",
	# 	related = False)
	# # the second viscosity varies
	# j.add_constant_parameter(val = default_n2_val,
	# 	key = "n2",
	# 	xml = None,
	# 	units = 'MPa * seconds',
	# 	description = "viscocity_2",
	# 	related = False)

	# establish relationships between the each the viscoelastic constants and model parameters
	if 'k' in sys.argv:
		# vary the bulk modulus
		j.add_variable_parameter(minval = 0.1,
			maxval = 100.,
			nval = 5,
			log = True,
			key = 'E',
			xml = "Material/material[@id='1']/elastic/E",
			units = "MPa",
			description = "bulk_modulus")
	else:
		# the bulk modulus is constant, use the default value
		j.add_constant_parameter(val = default_bulk,
			key = 'E',
			xml = "Material/material[@id='1']/elastic/E",
			units = "MPa",
			description = "bulk_modulus")

	if 'g1' in sys.argv:
		# vary the first relaxation modulus
		j.add_variable_parameter(minval = 0.1,
			maxval = 100.,
			nval = 5,
			log = True,
			key = 'gamma',
			xml = "Material/material[@id='1']/g1",
			units = None,
			description = "gamma_1")
	else:
		# the first relaxation moudlus is constant, use the default value
		j.add_constant_parameter(val = default_g1_val,
			key = 'gamma',
			xml = "Material/material[@id='1']/g1",
			units = None,
			description = "gamma_1")

	if 't1' in sys.argv:
		print("Varying the first timescale")
		# vary the first time constant
		j.add_variable_parameter(minval = 1.,
			maxval = 1000.,
			nval = 5,
			log = True,
			key = 'tau',
			xml = "Material/material[@id='1']/t1",
			units = 'seconds',
			description = "tau_1")
	else:
		# the first time constant is constant, use the default value
		j.add_constant_parameter(val = default_t1_val,
			key = 'tau',
			xml = "Material/material[@id='1']/t1",
			units = 'seconds',
			description = "tau_1")

	# create the frequency sweep
	## TODO :: change to 'add_sweep'
	j.add_variable_parameter (minval = 100.,
		maxval = 1000000.,
		nval = 40,
		log = True,
		key = "OT",
		xml = None,
		units = "s",
		description = "oscillation_period")
	# oscillation equation
	j.add_constant_parameter (val = "0.5*sin((2*{0}/OT)*(t-RT))".format(3.14159265359),
		key = "OTMa",
		xml = "LoadData/load_controller[@name='tip_oscillation_controller']/math",
		units = None,
		description = "tip_oscillation_equation",
		related = True,
		symbolic = True)
	# number of cycles
	j.add_constant_parameter(val = n_cycles,
		key = "NCy",
		description = "number_oscillation_cycles")
	# number of nsteps per cycle
	j.add_constant_parameter (val = n_steps,
		key = "NOSs",
		description = "number_steps_per_oscillation_cycle")
	# total number of numerical steps
	j.add_constant_parameter (val = "NCy * NOSs * 10",
		key = "ON",
		xml = "Step/step[@id='2']/Control/time_steps",
		units = None,
		description = "oscillation_total_numerical_steps",
		related = True)
	j.add_constant_parameter (val = "(OT) / (NOSs)",
		key = "OSMx",
		xml = "Step/step[@id='2']/Control/time_stepper[@type='default']/dtmax",
		units = None,
		description = "oscillation_max_step",
		related = True)
	j.add_constant_parameter (val = "(OT) / (NOSs * 10)",
		key = "OSMn",
		xml = "Step/step[@id='2']/Control/step_size",
		units = None,
		description = "oscillation_initial_step",
		related = True)

# generate parameter file
if not j.has_parameters():
	j.generate_parameters()

# save
j.save_config()
j.save_parameters()
