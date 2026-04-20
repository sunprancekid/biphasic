
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


## PARAMETERS
# POROELASTIC MODEL
# permeability
perm = 0.01
# elastic modulus
emod = 0.5
# length scale
z = 0.125


## METHODS
# generate viscoelastic simulation using parameters, base feb file
def gen_ve_sweep (emod = None, tau_1 = None, gamma_1 = None, osc_amp = None, relax_time = None, load_depth = None, min_freq = None, max_freq = None, n_freq = None, simdir = None, job = None, feb_file = None):
    """

    Arguments:
    ----------
    None

    Returns:
    --------
    None
    """
    pass

# generate poroelastic frequency sweep using parameters, base feb file
def gen_pe_sweep (emod = None, perm = None, osc_amp = None, relax_time = None, load_depth - None, min_freq = None, max_freq = None, n_freq = None, simdir = None, job = None, feb_file = None):
    """

    Arguments:
    ----------
    None

    Returns:
    --------
    None
    """
    pass


## ARGUMENTS
# none


## SCRIPT
# set the poroelastic model parameters, the time and energy scales are then known
poro_tau = pow(z, 2.) / (emod * perm)
poro_amp = emod * pow(z, 3.)

# pick the viscoelastic model parameters (both large and small)
# vary gamma betweem three values which are sufficiently "large"
# use gamma to determine tau_1

# vary gamma between three values which are sufficiently "small"
# use gamma to determine emod

# (run simulations)
# compare the following:
# - prestress relaxation
# - frequency sweep
# - phase shift
# - dynamic modulus
# - loss modulus 
# - storage modulus
# - hysteresis curve
