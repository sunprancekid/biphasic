#!/bin/bash
set -e 

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.10.14

## MODULES
# material property - permeability
MAT_PERM="./programs/bash/parameter/material/permeability.sh"
# material property - poissons ratio
MAT_PR="./programs/bash/parameter/material/poisson-ratio.sh"
# material property - elastic modulus
MAT_EMOD="./programs/bash/parameter/material/elastic-modulus.sh"
# material property - volume fraction
MAT_VF="./programs/bash/parameter/material/solid-volume-fraction.sh"
# loading - depth of prestress displacement
LOAD_DEPTH="./programs/bash/parameter/loading/depth.sh"
# oscillation - amplitude
OSC_AMP="./programs/bash/parameter/oscillation/amplitude.sh"
# oscillation - period
OSC_PER="./programs/bash/parameter/oscillation/period.sh"

## PARAMETERS
# job name
JOB="osc_emod"

## CONSTANTS
# permiability (mm^4 / N * s)
PERMEABILITY="0.001"
# poissons ratio
POISSON_RATIO="0.1"
# solid volume fraction
VOLUME_FRAC="0.2"
# loading depth (mm)
VAL_LOAD_DEPTH="0.05"
# oscillation amplitude (mm)
VAL_OSCILLATION_AMPLITUDE="0.025"

## ELASTIC MODULUS (logscale)
# minimum elastic modulus to test (MPa)
MIN_EMOD="0.005"
# maximum elastic modulus to test (MPa)
MAX_EMOD="50."
# number of unique elastic modulus values to test
N_EMOD="9"

## OSCILLATION PERIOD (logscale)
# minimum period to test (seconds)
MIN_PERIOD="0.2"
# maximum period to test (seconds)
MAX_PERIOD="20000."
# number of unique period values to test
N_PERIOD="25"

## LOADING - PRESTRESS
# depth of loading 

## METHODS
# none

## OPTIONS
# none

## ARGUMENTS
# none

## SCRIPT
## set constants
# constant volume fraction
$MAT_VF -j $JOB -C $VOLUME_FRAC
# constant poisson ratio
$MAT_PR -j $JOB -C $POISSON_RATIO
# constant permeability
$MAT_PERM -j $JOB -C $PERMEABILITY
# constant loading depth
$LOAD_DEPTH -j $JOB -C $VAL_LOAD_DEPTH
# constant oscillation amplitude 
$OSC_AMP -j $JOB -C $VAL_OSCILLATION_AMPLITUDE

## generate parameters
# elastic modulus
$MAT_EMOD -j $JOB -A $MIN_EMOD -B $MAX_EMOD -N $N_EMOD -L
# oscillation period
$OSC_PER -j $JOB -A $MIN_PERIOD -B $MAX_PERIOD -N $N_PERIOD -L

# TODO :: generate feb files and directories (en masse, from parm file)
# TODO :: submit jobs to HPC cluster (en masse, from parm file)
# TODO :: update jobs status (en mass, from parm file)
# TODO :: parse results (en mass, from parm file)
