
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
from febio.feb.model_file import ModelFile


## PARAMETERS
# base model file
model_file = "models/bend/bend.feb"
# absolute path to remote data
rmt_dir = "/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# number of oscillation cycles
n_cycles = 10
# number of steps per cycle
n_steps = 60
# loading depth (mm), unless otherwise specified
default_loading_depth = 0.005
# relaxation time (s), unless otherwise specified
default_relaxation_time = 10000
# oscillation amplitude (mm), unless otherwise specified
default_oscillation_amplitude = 0.001
# lowest oscillation period to test (s), unless otherwise specified
default_period_low = 10.
# highest oscillation period to test (s), unless otherwise specified
default_period_high = 100000. # one hundred thousand, 1e6
# number of period values to test in between highest and lowest, unless otherwise specified
default_period_n = 40

## MAXWELL MODEL PARAMETERS
# default first elastic modulus
default_E1_val = 1.129
# default second elastic modulus
default_E2_val = 7.014
# default second viscosity
default_n2_val = 335.5

## BULK MODULUS
# default constant bulk modulus
default_bulk = default_E1_val
# lowest bulk modulus to test when varying
default_E_low = 0.1
# highest bulk modulus value to test when varying parameter
default_E_high = 100.
# number of bulk modulus values to test, when varying parameter
default_E_n = 5

## FIRST RELAXATION MODULUS
# default first relaxation modulus constant
default_g_val = (default_E2_val / default_E1_val)
# lowest gamma value to test, when not specified
default_gamma_low = 0.1
# highest gamma value to test, when not specified
default_gamma_high = 100.
# number of gamma values to test, when not specified
default_gamma_n = 7

## FIRST TIME CONSTANT
# default first time constant
default_t_val = (default_n2_val / default_E2_val)
# lowest time constant value to test when varying
default_t_low = 10.
# highest time constant value to test when varying
default_t_high = 1000.
# number of time constant values to test when varying
default_t_n = 5


## METHODS
def vary_bulk_modulus (job, E_low = default_E_low, E_high = default_E_high, E_n = default_E_n):
	""" vary the bulk modulus between two values.

	Parameters:
	-----------
	job : Job
		contains job parameters.
	E_low : float (default is 'default_E_low')
		lowest value to test
	E_high : float (default is 'default_E_high')
		highest value to test
	E_n : int (default is 'default_E_n')
		number of unique E values to test

	Returns:
	--------
	Job
		'job' with additional parameters
	"""
	# vary the bulk modulus
	job.add_variable_parameter(minval = E_low,
		maxval = E_high,
		nval = E_n,
		log = True,
		key = 'E',
		xml = "Material/material[@id='1']/elastic/E",
		units = "MPa",
		description = "bulk_modulus")

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
		key = 'E',
		xml = "Material/material[@id='1']/elastic/E",
		units = "MPa",
		description = "bulk_modulus")

def vary_gamma (job, g_low = default_gamma_low, g_high = default_gamma_high, g_n = default_gamma_n):
	""" add variable gamma to job.

	Parameters:
	-----------
	job : Job
		contains job parameters.
	g_low : float (default is 'default_gamma_low')
		lowest gamma value to test
	g_high : float (default is 'default_gamma_high')
		highest gamma value to test
	g_n : int (default is 'default_gamma_n')
		number of gamma values to test

	Returns:
	Job
		'job' with additional arguments

	"""
	# vary the first relaxation modulus
	job.add_variable_parameter(minval = g_low,
		maxval = g_high,
		nval = g_n,
		log = True,
		key = 'gamma',
		xml = "Material/material[@id='1']/g1",
		units = None,
		description = "gamma_1")

def constant_gamma (job, g_val = default_g_val):
	""" add constant relaxation modulus to job.

	Parameters:
	-----------
	job : Job
		contains job parameters.
	g_val : float (default is 'default_g_val')
		constant relaxation modulus value

	Returns:
	--------
	Job
		'job' with additional parameters
	"""
	# the first relaxation moudlus is constant, use the default value
	job.add_constant_parameter(val = g_val,
		key = 'gamma',
		xml = "Material/material[@id='1']/g1",
		units = None,
		description = "gamma_1")

def vary_tau (job, t_low = default_t_low, t_high = default_t_high, t_n = default_t_n):
	""" add variable set of time constant values to job.

	Arguments:
	----------
	job : Job
		contains job parameters.
	t_low : float (default is 'default_t_low')
		lowest time constant value to test
	t_high : float (default is 'default_t_high')
		highest time constant value to test
	t_n : int (default is 'default_t_n')
		number of unqiue time constants to test

	Returns:
	Job
		'job' with additional parameters.
	"""
	# vary the first time constant
	job.add_variable_parameter(minval = t_low,
		maxval = t_high,
		nval = t_n,
		log = True,
		key = 'tau',
		xml = "Material/material[@id='1']/t1",
		units = 'seconds',
		description = "tau_1")

def constant_tau (job, t_val = default_t_val):
	""" add constant time constant to job.

	Arguments:
	----------
	job : Job
		contains job parameters.
	t_val : float (default is 'default_t_val')
		constant time constant value to specify in job.

	Returns:
	--------
	Job
		'job' with additional parameter.
	"""
	# constant time constant
	job.add_constant_parameter(val = t_val,
		key = 'tau',
		xml = "Material/material[@id='1']/t1",
		units = 'seconds',
		description = "tau_1")

def constant_oscillation_parameters (job, loading_depth = default_loading_depth, relaxation_time = default_relaxation_time, oscillation_amplitude = default_oscillation_amplitude, oscillation_period = None):
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
	oscillation_period : float
		oscilation period

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
	## NOTE: this parameter needs to go have the other relaxation parameters due to overlapping keys / replacement dependencies
	job.add_constant_parameter(val = relaxation_time,
		key = 'RT',
		xml = None,
		units = 'seconds',
		description = 'loading-hold-time',
		related = False)
	# add oscillation frequency
	job.add_constant_parameter(val = oscillation_period,
		key = 'OT',
		xml = None,
		units = 'seconds',
		description = "oscillation_period",
		related = False)
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
	## NOTE: this parameter needs to go have the other relaxation parameters due to overlapping keys / replacement dependencies
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

## from fitting

# generate viscoelastic simulation using parameters, base feb file
def gen_ve_frequency_sweep (emod = None, tau_1 = None, gamma_1 = None, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_period = None, max_period = None, n_period = None, jd = None, jn = None, feb_file = default_feb_ve):
    """

    Arguments:
    ----------
    emod : float
        value of elastic modulus parameter for material model
    tau_1 : float
        value of time constant for material model
    gamma_1 : float
        value of relaxation modulus parameter for material model
    osc_amp : float
        value of oscillation amplitude parameter for simulation
    relax_time : float
        value of relaxation time (time between loading and oscillation) for simulation
    load_depth : float
        value of loading depth during loading phase during simulation
    min_period : float
        minimum oscillation frequency which is tested
    max_period : float
        maximum oscillation frequency which is tested
    n_period : int
        number of simulation frequencies between minimum and maximum which are tested
    jd : str
        path to location to initialize the job directory
    jn : str
        name assigned to job
    feb_file : str
        path to base febio model

    Returns:
    --------
    None
    """

    # import methods from viscoleastic mod file
    # NOTE :: these methods have the same name as those in the proelastic mod file, so they are loaded locally (not globally)
    # from viscoelastic_modulation import constant_bulk_modulus, constant_tau, constant_gamma, frequency_sweep

    # check parameters
    # create job, assign parameters
    j = Job (jd, jn)
    constant_bulk_modulus (job = j, E_val = emod)
    constant_gamma (job = j, g_val = gamma_1)
    constant_tau (job = j, t_val = tau_1)
    frequency_sweep (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, period_low = min_period, period_high = max_period, period_n = n_period)

    # append model
    m = Model(feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/".format(jd, jn), saveas = "{0}.feb".format(jn))

def gen_ve_gamma_sweep (emod = None, tau_1 = None, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, oscillation_period = None, min_gamma = None, max_gamma = None, n_gamma = None, jd = None, jn = None, feb_file = None):
    """ generate viscoelastic simulations at fixed time scales that vary in their parameter gamma.

    Arguments:
    ----------
    emod : float
        value of elastic modulus parameter for material model
    tau_1 : float
        value of time constant for material model
    osc_amp : float
        value of oscillation amplitude parameter for simulation
    relax_time : float
        value of relaxation time (time between loading and oscillation) for simulation
    load_depth : float
        value of loading depth during loading phase during simulation
    oscillation_period : float
        timescale of periodic oscillation during simulation
    min_gamma : float
        minimum gamma value which are tested
    max_gamma : float
        maximum gamma value which are tested
    n_gamma : int
        number of gamma values between minimum and maximum which are tested
    jd : str
        path to location to initialize the job directory
    jn : str
        name assigned to job
    feb_file : str
        path to base febio model

    Returns:
    --------
    None
    """
    # import methods from viscoleastic mod file
    # NOTE :: these methods have the same name as those in the proelastic mod file, so they are loaded locally (not globally)
    # from viscoelastic_modulation import constant_bulk_modulus, constant_tau, vary_gamma, constant_oscillation_parameters

    # check parameters
    # create job, assign parameters
    j = Job(jd, jn)
    constant_bulk_modulus(job = j, E_val = emod)
    constant_tau (job = j, t_val = tau_1)
    constant_oscillation_parameters (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, oscillation_period = oscillation_period)
    vary_gamma (job = j, g_low = min_gamma, g_high = max_gamma, g_n = n_gamma)

    # append model
    m = Model(feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/".format(jd, jn), saveas = "{0}.feb".format(jn))

def gen_ve_emod_tau_sweep ():
    """ vary elastic modulus and time scale parameters while gamma remains fixed.

    Arguments:
    ----------
    None

    Returns:
    --------
    None
    """
    pass

# analysis low gamma data
def analysis_gamma_low (jd = None, jn = None, show = True, save = False):
    """ analyze the data

    Arguments:
    ----------
    jd : str
        path to job directory
    jn : str
        job name
    show : bool
        determines if graphs should be shown
    save : bool
        determines if graphs should be saved

    Returns
    -------
    None
    """
    ## open simulation jobs
    # check for the poroelastic simulation
    simdir = "{0}{1}/".format(jd, jn)
    if not os.path.exists(simdir + "pe"):
        print("ERROR :: analysis_gamma_low() :: unable to find poroelastic data in ''.".format())
    sweep_pe = Sweep(simdir, "pe")

    # check for viscoelastic simulation data
    sweep_ve = []
    i = 0
    while True:
        if os.path.exists(simdir + "g-lo-{0}".format(i)):
            sweep_ve.append(Sweep(simdir, "g-lo-{0}".format(i)))
            i += 1
        else:
            break
    # for i in range(len(sweep_ve)):
    #     sweep_ve[i].show_phase_shift()

    ## compare poroelasticity and viscoelasticity simulations
    # frequency sweep
    data = sweep_pe.get_hysteresis_work()
    pe_label = "PE ($E$ = {0:.1e}, \n$K$ = {1:.1e}, $Z$ = {2:.1e})".format(sweep_pe.get_simulation(0).get_key_value('E'), sweep_pe.get_simulation(0).get_key_value('K'), 0.125)
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_hysteresis_work()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Measured Energy Loss ($J$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)

    # phase shift
    data = sweep_pe.get_phase_shift()
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_phase_shift()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Phase Shift (degrees, $^{{\\circ}}$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)

    # dynamic modulus
    data = sweep_pe.get_dynamic_modulus()
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_dynamic_modulus()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Dynamic Modulus ($Pa$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)


## CLASSES
# none


if __name__ == "__main__":

	## ARGUMENTS
	# first argument: job directory
	jd = sys.argv[1]
	# second argument: job id
	jn = sys.argv[2]


	## TODO import base model, add log data
	## TODO add model file to job, generate dictionaries and write feb file

	## SCRIPT
	# create job
	j = Job (jd, jn)

	## add parameters
	# loading depth is constant
	if not j.has_config():

		## BULK MODULUS
		if 'k' in sys.argv:
			# vary the bulk modulus
			vary_bulk_modulus(job = j, E_low = default_E_low, E_high = default_E_high, E_n = default_E_n)
		else:
			# the bulk modulus is constant
			constant_bulk_modulus(job = j, E_val = default_bulk)

		## FIRST RELAXATION MODULUS
		if 'g1' in sys.argv:
			# vary gamma within full range
			vary_gamma (job = j, g_low = 0.1, g_high = 1000., g_n = default_gamma_n)
		elif 'g1-lo' in sys.argv:
			# vary gamma below transition regime
			vary_gamma(job = j, g_low = 0.001, g_high = 1., g_n = 5)
		elif 'g1-hi' in sys.argv:
			# vary gamma above transition regime
			vary_gamma(job = j, g_low = 10., g_high = 10000., g_n = 5)
		else:
			# constant gamma
			constant_gamma(job = j, g_val = default_g_val)

		## FIRST TIME CONSTANT
		if 't1' in sys.argv:
			# vary the first time constant
			vary_tau (job = j, t_low = default_t_low, t_high = default_t_high, t_n = default_t_n)
		else:
			# constant tau
			constant_tau (job = j, t_val = default_t_val)

		# create the frequency sweep
		frequency_sweep(job = j) # use default values

	# generate parameter file
	if not j.has_parameters():
		j.generate_parameters()

	# save
	j.save_config()
	j.save_parameters()
