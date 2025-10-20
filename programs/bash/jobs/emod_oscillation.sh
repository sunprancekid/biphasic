#!/bin/bash
# set -e

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
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# filename
FILENAME="programs/bash/jobs/emod_oscillation.sh"
# file purpose
PURPOSE="perform oscillation simulations where the elastic modulus is a variable parameter."
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

## METHODS
# display options, exit with exit code
help () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# first argument: exit code
    local exitcode=$1

	## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # display script options
    echo -e "\n ## SCRIPT EXECUTION ##"
    echo -e " -h\t\t| display HELP options, exit 0."
    echo -e " -p\t\t| create PARAMETER and CONFIG files."
    echo -e " -g\t\t| GENERATE FEB files."
    echo -e " -s\t\t| SUBMIT jobs to cluster."
    echo -e " -a\t\t| ANALYZE results post-simulation."
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -j  << ARG >>\t| JOB name (default is ${JOB})"
    echo -e " -f  << ARG >>\t| FEB FILE to use when GENERATING jobs."
    echo -e " -n  << ARG >>\t| perform execution for only one parameter set, integer N."

    # exit with exit code
    exit $exitcode
}

# display error message, exit with nonzero exitcode
display_error () {

    # PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # first argument: error message to display
    local err_msg=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${err_msg}.\n"
    help $NONZERO_EXITCODE

}

## OPTIONS
# parse options
while getopts "hpgsaj:f:n:" opt; do
 case $opt in
    h) # display options, exit 0
        help 0 ;;
    ?) # default option
        help $NONZERO_EXITCODE

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
echo $MAT_EMOD -j $JOB -A $MIN_EMOD -B $MAX_EMOD -N $N_EMOD -L
# oscillation period
echo $OSC_PER -j $JOB -A $MIN_PERIOD -B $MAX_PERIOD -N $N_PERIOD -L

# TODO :: generate feb files and directories (en masse, from parm file)
# TODO :: submit jobs to HPC cluster (en masse, from parm file)
# TODO :: update jobs status (en mass, from parm file)
# TODO :: parse results (en mass, from parm file)
