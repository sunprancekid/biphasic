
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
# none


## METHODS
# none


## ARGUMENTS
# none


## SCRIPT
# set the poroelastic model parameters, the time and energy scales are then known
# pick the viscoelastic model parameters (both large and small)
# (run simulations)
# compare the following:
# - prestress relaxation
# - frequency sweep
# - phase shift
# - dynamic modulus
# - loss modulus 
# - storage modulus
# - hysteresis curve