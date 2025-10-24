#!/bin/bash
# set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.10.14

## MODULES - JOB MANAGEMENT
# generate directory hirearchy and feb parameterization
GEN="./programs/bash/simulation/generate.sh"
# submit job to linux cluster en masse
RUN="./programs/bash/simulation/run.sh"

## MODULES - FEB PARAMETERIZATION
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

## SCRIPT CONSTANTS
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# filename
FILENAME="programs/bash/jobs/emod_oscillation.sh"
# file purpose
PURPOSE="perform oscillation simulations where the elastic modulus is a variable parameter."

## FEB PARAMETERIZATION CONSTANTS
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

## ELASTIC MODULUS PARAMETERES (logscale)
# minimum elastic modulus to test (MPa)
MIN_EMOD="0.005"
# maximum elastic modulus to test (MPa)
MAX_EMOD="50."
# number of unique elastic modulus values to test
N_EMOD="9"

## OSCILLATION PERIOD PARAMETERS (logscale)
# minimum period to test (seconds)
MIN_PERIOD="0.2"
# maximum period to test (seconds)
MAX_PERIOD="20000."
# number of unique period values to test
N_PERIOD="25"

# OPTION PARAMETERS
# directory which contains jobs
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean for declaring job name
declare -i BOOL_JOB=0
# job name
JOB="osc_emod"
# boolean for file overwriting
declare -i BOOL_OVERWRITE=0
# boolean for parameter and config file writing
declare -i BOOL_PARM=0
# boolean for feb file
declare -i BOOL_FEB=0
# boolean for generating files
declare -i BOOL_GEN=0
# boolean for submitting jobs
declare -i BOOL_RUN=0
# boolean for analyzing jobs
declare -i BOOL_ANAL=0
# boolean for specifying job integer
declare -i BOOL_INT=0

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
    echo -e " -v\t\t| VERBOSE script execution."
    echo -e " -V\t\t| VERY VERBOSE script execution."
    echo -e " -o\t\t| overwrite existing simulation files."
    echo -e " -p\t\t| create PARAMETER and CONFIG files."
    echo -e " -g\t\t| GENERATE FEB files."
    echo -e " -r\t\t| RUN jobs."
    echo -e " -a\t\t| ANALYZE results post-simulation."
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -d  << ARG >>\t| DIRECTORY path to generate jobs (default is ${DIR})"
    echo -e " -j  << ARG >>\t| JOB name (default is ${JOB})"
    echo -e " -f  << ARG >>\t| FEB FILE to use when GENERATING jobs."
    echo -e " -n  << ARG >>\t| perform execution for only one parameter set, integer N."
    echo -e " -c  << ARG >>\t| if CHECKFILE exists in simulation directory, skip operation."

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

# check options before execution
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the main directory exists
    if [[ ! -d $DIR ]]; then
    	# the directory doesnt exist
    	display_error "DIRECTORY '${DIR}' cannot be found"
    fi

    # parameter generation
    if [[ $BOOL_PARM -eq 1 ]]; then
        # check if the directory, and config and parm files already exist
        if [[ -d ${DIR}${JOB} && $BOOL_OVERWRITE -eq 0 ]]; then
        	# the job already exists but overwrite has not been called
        	display_error "the job parameters have already been generated and cannot be overwritten without an overwrite flag (-o)."
      	elif [[ -d ${DIR}${JOB} && $BOOL_OVERWRITE -eq 1 ]]; then
      		display_error "TODO :: implement overwrite routine."
      	fi
    fi

    # directory generation and feb parameterization
    if [[ $BOOL_GEN -eq 1 ]]; then
    	# check that the feb file exists
    	if [[ $BOOL_FEB -eq 0 ]]; then
    		display_error "must specify FEB FILE (-f)"
    	elif [[ ! -f $FEB_FILE ]]; then
    		display_error "specified FEB FILE '${FEB_FILE}' does not exist."
    	fi
    fi
}

# create parameters
parameter () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# none

	## SCRIPT
	## set constants
	# constant volume fraction
	$MAT_VF -d $DIR -j $JOB -C $VOLUME_FRAC
	# constant poisson ratio
	$MAT_PR -d $DIR -j $JOB -C $POISSON_RATIO
	# constant permeability
	$MAT_PERM -d $DIR -j $JOB -C $PERMEABILITY
	# constant loading depth
	$LOAD_DEPTH -d $DIR -j $JOB -C $VAL_LOAD_DEPTH
	# constant oscillation amplitude 
	$OSC_AMP -d $DIR -j $JOB -C $VAL_OSCILLATION_AMPLITUDE

	## generate variable parameters
	# elastic modulus
	echo $MAT_EMOD -d $DIR -j $JOB -A $MIN_EMOD -B $MAX_EMOD -N $N_EMOD -L
	# oscillation period
	echo $OSC_PER -d $DIR -j $JOB -A $MIN_PERIOD -B $MAX_PERIOD -N $N_PERIOD -L

}

# generate directories and parameterize feb files
generate () {

	## PARAMETER
	# none

	## ARGUMENT
	# none

	## SCRIPT
	# generate parameters depending on if an integer was specified or not
	if [[ $BOOL_INT -eq 0 ]]; then
		$GEN -d $DIR -j $JOB -f $FEB_FILE
	else
		echo "TODO :: implement single parameter generation"
		$GEN -d $DIR -j $JOB -f $FEB_FILE -n $SIM_INT
		# TODO :: add local option, generate feb in pwd
	fi

}

# run simulations
run () {

	## PARAMETER
	# none

	## ARGUMENT
	# none

	## SCRIPT
	# run single or multiple jobs
	if [[ $BOOL_INT -eq 0 ]]; then
		$RUN -d $DIR -j $JOB -s
	else # integer has been specified
		$RUN -d $DIR -j $JOB -s -n $SIM_INT
	fi


	## TODO :: add these to submission script
	# for batch generation, add columns that contains the job number and the status

}

# run analysis routine
analysis () {

	## PARAMETER
	# none

	## ARGUMENT
	# none

	## SCRIPT
	# run selected analysis routine
	display_error "TODO :: implement analysis routines for ${JOB}"
}

## OPTIONS
# parse options
while getopts "hvVopgrad:j:f:n:c:" opt; do
 case $opt in
    h) # display options, exit 0
        help 0 ;;
    v) # verbose
        declare -i BOOL_VERBOSE=1 ;;
    V) # very verbose
        declare -i BOOL_VERYVERBOSE=1 ;;
    o) # overwrite simulations if they exist
        declare -i BOOL_OVERWRITE=1 ;;
    p) # create parameter and config files
        declare -i BOOL_PARM=1 ;;
    g) # generate FEB files
        declare -i BOOL_GEN=1 ;;
    r) # RUN simulations
        declare -i BOOL_RUN=1 ;;
    a) # analyze simulation results
        declare -i BOOL_ANAL=1 ;;
    d) # specify directory for job
    	DIR=${OPTARG} ;;
    j) # job title
        declare -i BOOL_JOB=1
        JOB=${OPT_ARG};;
    f) # feb file specification
        declare -i BOOL_FEB=1
        FEB_FILE=${OPTARG};;
    n) # integer for specific job number
        declare -e BOOL_INT=1
        SIM_INT=${OPTARG} ;;
    c) # specify check file
        declare -i BOOL_CHECKFILE=1
        CHECKFILE=${OPTARG} ;;
    ?) # default option
        help $NONZERO_EXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# check options passed to script
check

# perform specified operation
if [[ $BOOL_PARM -eq 1 ]]; then
	parameter
fi
if [[ $BOOL_GEN -eq 1 ]]; then
	generate
fi
if [[ $BOOL_RUN	-eq 1 ]]; then
	run
fi
if [[ $BOOL_ANAL -eq 1 ]]; then
	analysis
fi


# TODO :: update jobs status (en mass, from parm file)
# TODO :: parse results (en mass, from parm file)
