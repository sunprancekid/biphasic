
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2026.10.16

## FILENAME: programs/python/mod_parm/dynamic_analysis.py
## PURPOSE: handles varying / setting parameters associated with DMA

## MODULES
# none


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
def vary_loading_depth(job, minval, maxval, nval):
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

    Returns:
    --------
    bool
        'True' if addition was succesful, else 'False'.
    """
    job.add_variable_parameter(minval = minval, maxval = maxval, nval =nval, log = False, key = key_ld, xml = xml_ld, units = units_ld, description = descrip_ld, related = False)

# set constant relaxation time
def set_relaxation_time():
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
def vary_relaxation_time(job, minval, maxval, nval):
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
	job.add_variable_parameter(minval = minval, maxval = maxval, nval = nval, key = key_rt, xml = None, units = units_rt, description = descrip_rt, related = False)

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
def vary_oscillation_amplitude(job, maxval, minval, nval):
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

    Returns:
    --------
    bool
        'True' if successfully added to job, else 'False'
    """
	job.add_variable_parameter(minval = minval, maxval = maxval, nval = nval, key = key_oa, xml = xml_oa, units = units_oa, description = descrip_oa, related = False)

# set constant oscillation period
def set_oscillation_period():
    pass

# vary oscillation amplitude
def vary_oscillation_period():
    pass

# set constant oscillation frequency
def set_oscillation_frequency():
    pass

# vary oscillation frequency
def vary_oscillation_frequency():
    pass
