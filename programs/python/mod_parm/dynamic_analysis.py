
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2026.10.16

## FILENAME: programs/python/mod_parm/dynamic_analysis.py
## PURPOSE: handles varying / setting parameters associated with DMA

## MODULES
# febio
import math
from febio.job import Job


## PARAMETERS
## LOADING DEPTH
# xml path to loading depth parameter in model files
xml_ld = "Step/step[@id='1']/Rigid/rigid_bc[@name='tip_displacement']/value"
# key use for loading depth id
key_ld = 'LD'
# description for loading depth variable
descrip_ld = 'loading_displacement_depth'
# units for loading depth parameter
units_ld = 'mm'
# default loading depth value when constant
default_ld_set = 0.005

## RELAXATION TIME
# xml path for relaxation time in model files
xml_rt = None
# key used for relaxation time id in config and parameter files
key_rt = "RT"
# description for relaxation time variable
descrip_rt = "loading_hold_time"
# units for relaxation time variables
units_rt = "seconds"

# relaxation step size
# xml path for step size during relaxation phase
xml_rt_ss = "Step/step[@id='1']/Control/step_size"
# key used for relaxation step size
key_rt_ss = f"{key_rt}ss"
# description for variable associated with relaxation phase step size
descrip_rt_ss = 'relaxation_step_size'
# units for relaxation step
units_rt_ss = None

# relaxation length
# xml path for relaxation phase length, in steps
xml_rt_sl = "Step/step[@id='1']/Control/time_steps"
# key used for relaxation length variable
key_rt_sl = f"{key_rt}n"
# description for variable associated with relaxation phase length (steps)
descrip_rt_sl = "relaxation_length"
# units for relaxation length
units_rt_sl = "steps"

## OSCILATION AMPLITUDE
# xml path associated with oscillation amplitude in model file
xml_oa = "Step/step[@id='2']/Rigid/rigid_bc[@name='tip_oscillation']/value"
# key associated with oscillation amplitude variable
key_oa = "OA"
# desciption used for variable
descrip_oa = "oscillation_amplitude"
# units associated with oscillation amplitude value
units_oa = "mm"

## OSCILLATION PERIOD
# xml path associated with oscillation amplitude in model file
xml_ot = None
# key associated with oscillation amplitude variable
key_ot = 'OT'
# string description of variable
descrip_ot = 'oscillation_period'
# units associated with variable
units_ot = 's'

# oscilation symbolic equation
# value used for oscillation equation
val_ot_eq =  f"0.5*sin((2*{math.pi:.8f}/OT)*(t-RT))"
# xml path for oscillation equation
xml_ot_eq = "LoadData/load_controller[@name='tip_oscillation_controller']/math"
# key for oscilation equation variable
key_ot_eq = f"{key_ot}Ma"
# string description of oscillation equation
descrip_ot_eq = "tip_oscillation_equation"
# units associlated with variable
units_ot_eq = None

# number of cycles
# key used for cycle number variable
key_ot_nc = f"{key_ot}NCy"
# description for variable
descrip_ot_nc = "number_oscillation_cycles"

# number of steps in oscillation cycle
# key used for oscillation step number variable
key_ot_ns = "NOSs"
# description for oscillation step number variable
descrip_ot_ns = "steps_per_oscillation_cycle"

# total number of numerical steps in oscillation step
# value used for total step number
val_ot_nt = f"{key_ot_nc} * {key_ot_ns} * 10"
# xml path for variable in model file
xml_ot_nt = "Step/step[@id='2']/Control/step_size"
# key used for total step number
key_ot_nt = "ON"
# string description of variable
descrip_ot_nt = "oscillation_total_numerical_steps"
# units for variable
units_ot_nt = None

# max integration step size during oscillation phase
# value used for max step size
val_ot_mx = f"({key_ot}) / ({key_ot_ns})"
# xml path for max step size
xml_ot_mx = "Step/step[@id='2']/Control/time_stepper[@type='default']/dtmax"
# key used for max step size
key_ot_mx = "OSMx"
# string description of variable
descrip_ot_mx = "oscillation_max_step_size"
# variable units
units_ot_mx = None

# min integration step size during oscillation phase
# value used for min step size
val_ot_mn = f"({key_ot}) / ({key_ot_ns} * 10)"
# xml path for min step size
xml_ot_mn = "Step/step[@id='2']/Control/step_size"
# key used for variable
key_ot_mn = "OSMn"
# string description of variable
descip_ot_mn = "oscillation_initial_step_size"
# variable units
units_ot_mn = None


## METHODS
# set constant loading depth
def set_loading_depth(job, val = default_ld_set):
	""" assign constant loading depth to job.

	Arguments:
	----------
	job : Job
		job to add constant parameter to.
	val : float
		constant number

	Returns:
	--------
	bool
		'True' if addition was successful, else 'False'
	"""
	return job.add_constant_parameter(val = val, key = key_ld, xml = xml_ld, units = units_ld, description = descrip_ld, related = False, symbolic = False)

# vary loading depth
def vary_loading_depth(job, minval, maxval, nval, log = False):
	""" assign variable loading depth to job.

	Arguments:
	----------
	job : Job
		job to add variable parameter to.
	maxval : float
		largest value to apply to parameter.
	minval : float
		smallest value to apply to parameter.
	nval : int
		number of total parameters that should be applied.
	log : bool (optional, default is 'False')
		generate variable parameter set on log scale

	Returns:
	--------
	bool
		'True' if addition was succesful, else 'False'.
	"""
	job.add_variable_parameter(minval = minval, maxval = maxval, nval = nval, log = log, key = key_ld, xml = xml_ld, units = units_ld, description = descrip_ld, related = False)

# set constant relaxation time
def set_relaxation_time(job, val):
	""" assign constant relaxation time to job.

	Argumnts:
	---------
	job : Job
		job to assign constant relaxation time to
	val : float
		relaxation time value

	Returns:
	--------
	bool
		'True' if successful, else 'False'
	"""
	# the relaxation time step size controls the maximum size of the time integration
	job.add_constant_parameter(val = 0.1, key = key_rt_ss, xml = xml_rt_ss, units = units_rt_ss, description = descrip_rt_ss, related = False)
	# the relaxation step number defines the number of steps which would be required
	# to be taken to reach to the set relaxation time (next parameter) if each step
	# were the maximum step size (previous parameter)
	job.add_constant_parameter(val = "{0} / {1}".format(key_rt, key_rt_ss), key = key_rt_sl, xml = xml_rt_sl, units = units_rt_sl, description = descrip_rt_sl, related = True)
	## NOTE: this parameter needs to go after the other relaxation parameters
	## because other key values depend on it
	job.add_constant_parameter(val = val, key = key_rt, xml = None, units = units_rt, description = descrip_rt, related = False)

# vary relaxation time
def vary_relaxation_time(job, minval, maxval, nval, log = False):
	""" assign variable relaxation time to job.

	Arguments:
	----------
	job : Job
		job to add variable parameter to.
	maxval : float
		largest value to apply to parameter.
	minval : float
		smallest value to apply to parameter.
	nval : int
		number of total parameters that should be applied.
	log : bool (optional, default is 'False')
		generate variable parameter set on log scale

	Returns:
	--------
	bool
		'True' if successfully added to job, else 'False'
	"""
	# the relaxation time step size controls the maximum size of the time integration
	job.add_constant_parameter(val = 0.1, key = key_rt_ss, xml = xml_rt_ss, units = units_rt_ss, description = descrip_rt_ss, related = False)
	# the relaxation step number defines the number of steps which would be required
	# to be taken to reach to the set relaxation time (next parameter) if each step
	# were the maximum step size (previous parameter)
	job.add_constant_parameter(val = "{0} / {1}".format(key_rt, key_rt_ss), key = key_rt_sl, xml = xml_rt_sl, units = units_rt_sl, description = descrip_rt_sl, related = True)
	## NOTE: this parameter needs to go after the other relaxation parameters
	## because other key values depend on it
	job.add_variable_parameter(minval = minval, maxval = maxval, nval = nval, key = key_rt, xml = None, units = units_rt, description = descrip_rt, related = False, log = log)

# set constant oscillation amplitude
def set_oscillation_amplitude(job, val):
	""" assign constant oscillation amplitude.

	Arguments:
	----------
	job
	val

	Returns:
	--------
	bool
		'True' if constant value was succesfully added to job, else 'False'.
	"""
	job.add_constant_parameter(val = val, key = key_oa, xml = xml_oa, units = units_oa, description = descrip_oa, related = False)

# vary oscillation amplitude
def vary_oscillation_amplitude(job, maxval, minval, nval, log = False):
	""" assign variable oscillation amplitude to job.


	Arguments:
	----------
	job : Job
		job to add variable parameter to.
	maxval : float
		largest value to apply to parameter.
	minval : float
		smallest value to apply to parameter.
	nval : int
		number of total parameters that should be applied.
	log : bool (optional, default is 'False')
		generate variable parameter set on log scale

	Returns:
	--------
	bool
		'True' if successfully added to job, else 'False'
	"""
	job.add_variable_parameter(minval = minval, maxval = maxval, nval = nval, key = key_oa, xml = xml_oa, units = units_oa, description = descrip_oa, related = False, log = log)

# set constant oscillation period
def set_oscillation_period(job, val, n_cycles, n_steps):
	""" set constant oscillation period.

	Arguments:
	----------
	job : Job
		job to add variable parameter to
	val : float
		oscillation period
	n_cycles : float
		total number of oscillation cycles which are performed
	n_steps : float
		number of intergrate time steps each oscillation cycle

	Returns:
	--------
	bool
		'True' if constant value was successfully added to job, else 'False'
	"""
	# constant time scale parameters
	job.add_constant_parameter (val = val, key = key_ot, xml = xml_ot, units = units_ot, description = descrip_ot)
	# oscillation equation - equation used to control the tip discplacement wrt time
	job.add_constant_parameter (val = val_ot_eq, key = key_ot_eq, xml = xml_ot_eq, units = units_ot_eq, description = descrip_ot_eq, related = True, symbolic = True)
	# number of oscillation cycles which are performed
	job.add_constant_parameter(val = n_cycles, key = key_ot_nc, description = descrip_ot_nc)
	# number of nsteps per cycle
	job.add_constant_parameter (val = n_steps, key = key_ot_ns, description = descrip_ot_ns)
	# total number of numerical steps in oscillation step
	job.add_constant_parameter (val = val_ot_nt, key = key_ot_nt , xml = xml_ot_nt, units = units_ot_nt, description = descrip_ot_nt, related = True)
	# max time integration step size, assumed average step size when determining simulation length
	job.add_constant_parameter (val = val_ot_mx, key = key_ot_mx, xml = xml_ot_mx, units = units_ot_mx, description = descrip_ot_mx, related = True)
	# min time integration step size for oscillation step, initial step size
	return job.add_constant_parameter (val = val_ot_mn, key = key_ot_mn, xml = xml_ot_mn, units = units_ot_mn, description = descip_ot_mn, related = True)

# vary oscillation amplitude
def vary_oscillation_period(job, maxval, minval, nval, log = False):
	""" assign variable oscillation period to job.


	Arguments:
	----------
	job : Job
		job to add variable parameter to.
	maxval : float
		largest value to apply to parameter.
	minval : float
		smallest value to apply to parameter.
	nval : int
		number of total parameters that should be applied.
	log : bool (optional, default is 'False')
		generate variable parameter set on log scale

	Returns:
	--------
	bool
		'True' if successfully added to job, else 'False'
	"""
	# constant time scale parameters
	job.add_variable_parameter (minval = minval, maxval = maxval, nval = nval, key = key_ot, xml = xml_ot, units = units_ot, description = descrip_ot, log = log)
	# oscillation equation - equation used to control the tip discplacement wrt time
	job.add_constant_parameter (val = val_ot_eq, key = key_ot_eq, xml = xml_ot_eq, units = units_ot_eq, description = descrip_ot_eq, related = True, symbolic = True)
	# number of oscillation cycles which are performed
	job.add_constant_parameter(val = n_cycles, key = key_ot_nc, description = descrip_ot_nc)
	# number of nsteps per cycle
	job.add_constant_parameter (val = n_steps, key = key_ot_ns, description = descrip_ot_ns)
	# total number of numerical steps in oscillation step
	job.add_constant_parameter (val = val_ot_nt, key = key_ot_nt , xml = xml_ot_nt, units = units_ot_nt, description = descrip_ot_nt, related = True)
	# max time integration step size, assumed average step size when determining simulation length
	job.add_constant_parameter (val = val_ot_mx, key = key_ot_mx, xml = xml_ot_mx, units = units_ot_mx, description = descrip_ot_mx, related = True)
	# min time integration step size for oscillation step, initial step size
	return job.add_constant_parameter (val = val_ot_mn, key = key_ot_mn, xml = xml_ot_mn, units = units_ot_mn, description = descip_ot_mn, related = True)

# set constant oscillation frequency
def set_oscillation_frequency():
	pass

# vary oscillation frequency
def vary_oscillation_frequency():
	pass
