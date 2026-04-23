
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2026.04.17

## FILENAME: projects/pv-fitting.py
## PURPOSE: comparing fit viscoelastic model to poroelastic simulation data.


## MODULES
# native / conda
import sys, os
# local
from febio.job import Job
from febio.feb.model import Model


## PARAMETERS
## SIMULATION PARAMETERS
# default amplitude during oscillation phase
default_oscillation_amplitude = 0.005
# default relxation time between starting the oscillation phase
default_relaxation_time = 10000
# default loading depth during initial loading
default_loading_depth = 0.01
# default feb model for viscoleastic simulations
default_feb_ve = "models/bend/bend_ve.feb"
# default feb model for poroelastic simulations
default_feb_pe = "models/bend/bend.feb"

## VISCOELASTIC MODEL
# small gamma - n gamma to test
n_small = 3
# small gamma - lowest gamma value to test
min_small_gamma = 0.1
# small gamma - highest gamma value to test
max_small_gamma = 1.
# large gamma - n  gamma to test
n_large = 3
# large gamma - lowest gamma value to test
min_large_gamma = 500.
# large gamma - highest gamma value to test
max_large_gamma = 5000.

# POROELASTIC MODEL
# permeability
perm = 0.01
# elastic modulus
emod = 0.5
# length scale
z = 0.125


## METHODS
# generate viscoelastic simulation using parameters, base feb file
def gen_ve_sweep (emod = None, tau_1 = None, gamma_1 = None, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_period = None, max_period = None, n_period = None, jd = None, jn = None, feb_file = default_feb_ve):
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
    from viscoelastic.viscoelastic_modulation import constant_bulk_modulus, constant_tau, constant_gamma, frequency_sweep

    # check parameters
    # create job, assign parameters
    j = Job(jd, jn)
    constant_bulk_modulus(job = j, E_val = emod)
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

# generate poroelastic frequency sweep using parameters, base feb file
def gen_pe_sweep (emod = emod, perm = perm, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_period = None, max_period = None, n_period = None, jd = None, jn = None, feb_file = default_feb_pe):
    """

    Arguments:
    ----------
    emod : float
        value of elastic modulus used in material model
    perm : float
        value of permeability using in material model
    osc_amp : float
        amplitude during oscillation phase
    relax_time : float
        time between loading and oscillation phase
    load_depth : float
        depth of initial indentation before relxation and oscillation phases
    min_period : float
        minimum oscilation period to test
    max_period : float
        maximum oscillation period to test
    n_period : int
        number of unique period values between minimum and maximum to test
    jd : str
        path to location to save simulation directory
    jn : str
        name of simulation set
    feb_file : str
        path to base poroelastic model to use for simulation set

    Returns:
    --------
    None
    """

    # load modules
    # NOTE :: these methods have the same names as those for viscoleasticity, so they are loaded locally rather than globally
    from poroelastic.poroelastic_modulation import constant_bulk_modulus, constant_permeability, frequency_sweep

    # set job parameters
    j = Job(jd, jn)
    constant_bulk_modulus (job = j, E_val = emod)
    constant_permeability (job = j, K_val = perm)
    frequency_sweep (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, period_low = min_period, period_high = max_period, period_n = n_period)

    # load model
    m = Model (feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/".format(jd, jn), saveas = "{0}.feb".format(jn))


## ARGUMENTS
# first argument: simulation directory
jd = sys.argv[1]
# second argument: simulation set name
jn = sys.argv[2]


## SCRIPT

## POROELASTICITY
# set the poroelastic model parameters, the time and energy scales are then known
poro_tau = pow(z, 2.) / (emod * perm)
poro_amp = emod * pow(z, 3.)
# generate the poroelasticity simulation
gen_pe_sweep (min_period = poro_tau / 100., max_period = poro_tau * 100, n_period = 40, jd = "{0}{1}/".format(jd, jn), jn = "pe")

## VISCOELASTICITY
# pick the viscoelastic model parameters (both large and small)
# vary gamma betweem three values which are sufficiently "small"
for i in range(n_small):
    # establish the viscoelasticity parameters
    g_val = min_small_gamma + ((i) / (n_small - 1)) * (max_small_gamma - min_small_gamma)
    t_val = poro_tau
    e_val = poro_amp / (pow(z, 3.) * emod)
    # generate simulation
    gen_ve_sweep (emod = e_val, tau_1 = t_val, gamma_1 = g_val, jd = "{0}{1}/".format(jd, jn), jn = "g-lo-{0}".format(i), min_period = poro_tau / 100., max_period = poro_tau * 100., n_period = 40)

# vary gamma between three values which are sufficiently "large"
# use gamma to determine emod
for i in range(n_large):
    # establish viscoelasticity parameters
    g_val = min_large_gamma + ((i) / (n_large - 1)) * (max_large_gamma - min_large_gamma)
    t_val = poro_tau / g_val
    e_val = poro_amp / pow(z, 3.)
    # generate simulation
    gen_ve_sweep (emod = emod, tau_1 = t_val, gamma_1 = g_val, jd = "{0}{1}/".format(jd, jn), jn = "g-hi-{0}".format(i), min_period = poro_tau / 100., max_period = poro_tau * 100., n_period = 40)

# (run simulations)
# compare the following:
# - prestress relaxation
# - frequency sweep
# - phase shift
# - dynamic modulus
# - loss modulus 
# - storage modulus
# - hysteresis curve
