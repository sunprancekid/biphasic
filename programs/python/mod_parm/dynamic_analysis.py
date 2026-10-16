
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
xml_rt = ""
# key used for loading depth id in config and parameter files
key_rt = ""
# description for relaxation time variable
descrip_rt = ""
# units for relaxation time variables
units_rt = ""

## OSCILATION AMPLITUDE

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
    pass

# vary relaxation time
def vary_relaxation_time():
    pass

# set constant oscillation amplitude
def set_oscillation_amplitude():
    pass

# vary oscillation amplitude
def vary_oscillation_amplitude():
    pass

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
