#!/bin/bash
# set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.12.05

## MODULES - JOB MANAGEMENT
# generate directory hirearchy and feb parameterization
GEN="./programs/bash/simulation/generate.sh"
# submit job to linux cluster en masse
RUN="./programs/bash/simulation/run.sh"
# contains analysis routines
ANAL="./programs/bash/simulation/analysis.sh"
# show results after analysis has been performed
PLOT="python ./programs/python/febio/analysis/scaling.py"
# instructions for syncing local and remote directories
SYNC="./programs/bash/util/sync.sh"

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
FILENAME="programs/bash/jobs/perm_oscillation.sh"
# file purpose
PURPOSE="perform oscillation simulations where the solid volume fraction is a variable parameter."
# host name for personal computer
PERSONAL_HOST="MacBook-Pro-404.local"
# mpikg login address
MPIKG_HOST="dorsey@ssh.mpikg.mpg.de"

## FEB PARAMETERIZATION CONSTANTS
# permiability (mm^4 / N * s)
PERMEABILITY="0.001"
# elastic modulus (MPa)
ELASTIC_MODULUS="0.5"
# poissons ratio (na)
POISSON_RATIO="0.3"
# loading depth (mm)
VAL_LOAD_DEPTH="0.1"
# oscillation amplitude (mm)
VAL_OSCILLATION_AMPLITUDE="0.05"

## SOLID VOLUME FRACTION PARAMETERES (linear scale)
# minimum permeability to test (na)
MIN_SFRAC="0.2"
# maximum permeability to test (na)
MAX_SFRAC="0.8"
# number of unique permeability values to test
N_SFRAC="4"

## OSCILLATION PERIOD PARAMETERS (logscale)
# minimum period to test (seconds)
MIN_PERIOD="1.0"
# maximum period to test (seconds)
MAX_PERIOD="1000."
# number of unique period values to test
N_PERIOD="30"

# OPTION PARAMETERS
# directory which contains jobs
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean for declaring job name
declare -i BOOL_JOB=0
# job name
JOB="osc_sfrac"
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
# boolean for running jobs on linux cluster
declare -i BOOL_SLURM=0
# boolean for running jobs locally
declare -i BOOL_LOCAL=0
# boolean for analyzing jobs
declare -i BOOL_ANAL=0
# boolean for specifying job integer
declare -i BOOL_INT=0
# boolean for updating job directory
declare -i BOOL_UPDATE=0

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
    echo -e " \t-s\t| SUBMIT JOBS to HPC cluster via slurm."
    echo -e " \t-l\t| run jobs LOCALLY."
    echo -e " -a\t\t| ANALYZE results post-simulation."
    echo -e " -u\t\t| UPDATE local job dir with jobs on cloud cluster."
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

    ## SCRIPT./programs/bash/parameter/material/poisson-ratio.sh -d /mnt/data/bgfs1/dorsey/biphasic_simulations/ -j osc_prat -C
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
	# constant permeability
	$MAT_PERM -d $DIR -j $JOB -C $PERMEABILITY
	# constant poisson ratio
	$MAT_PR -d $DIR -j $JOB -C $POISSON_RATIO
	# constant elastic modulus
	$MAT_EMOD -d $DIR -j $JOB -C $ELASTIC_MODULUS
	# constant loading depth
	$LOAD_DEPTH -d $DIR -j $JOB -C $VAL_LOAD_DEPTH
	# constant oscillation amplitude 
	$OSC_AMP -d $DIR -j $JOB -C $VAL_OSCILLATION_AMPLITUDE

	## generate variable parameters
	# vary volume fraction
	echo $MAT_VF -d $DIR -j $JOB -A $MIN_SFRAC -B $MAX_SFRAC -N $N_SFRAC
	# vary oscillation period
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
	RUN_FLAGS="-d ${DIR} -j ${JOB}"
	# check for job specification
	if [[ $BOOL_INT -eq 1 ]]; then
		RUN_FLAGS="${RUN_FLAGS} -n ${SIM_INT}"
	fi
	# check for running instructions
	if [[ $BOOL_SLURM -eq 1 ]]; then
		RUN_FLAGS="${RUN_FLAGS} -s"
	elif [[ $BOOL_LOCAL -eq 1 ]]; then
		RUN_FLAGS="${RUN_FLAGS} -l"
	else
		display_error "must specify running simulations locally (flag -l) or submitting to slurm cluster (flag -s) to run."
	fi
	# execute
	$RUN $RUN_FLAGS

	## TODO :: add these to submission script
	# for batch generation, add columns that contains the job number and the status

}

# sync local directories with jobs on remote cluster
update () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# none

	## SCRIPT
	# if on person computer, sync with remote MPIKG cluster
	if [[ "${HOSTNAME}" == "${PERSONAL_HOST}" ]]; then
		$SYNC -g -l ${DIR} -r "/mnt/data/bgfs1/dorsey/biphasic_simulations/${JOB}" -a ${MPIKG_HOST}
	else
		# report error
		display_error "no sync instructions listed for ${HOSTNAME}"
	fi

}

# run analysis routine
analysis () {

	## PARAMETER
	# file which contains job analysis
	ANAL_FILE="${DIR}/${JOB}/${JOB}.sum.csv"

	## ARGUMENT
	# none

	## SCRIPT
	# run selected analysis routine
	if [[ ! -f $ANAL_FILE || $BOOL_OVERWRITE -eq 1 ]]; then
		# perform analysis if the analysis file does not already exist,
		# or if overwrite has been called
		$ANAL -d $DIR -j $JOB -H
	fi
	# plot results after analysis
	$PLOT $DIR $JOB
}

## OPTIONS
# parse options
while getopts "hvVopgrslaud:j:f:n:c:" opt; do
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
    s) # submit jobs to SLURM
    	declare -i BOOL_SLURM=1 ;;
    l) # run jobs LOCALLY
    	declare -i BOOL_LOCAL=1 ;;
    a) # analyze simulation results
        declare -i BOOL_ANAL=1 ;;
	u) # update job directories
		declare -i BOOL_UPDATE=1 ;;
    d) # specify directory for job
    	DIR=${OPTARG} ;;
    j) # job title
        declare -i BOOL_JOB=1
        JOB=${OPTARG};;
    f) # feb file specification
        declare -i BOOL_FEB=1
        FEB_FILE=${OPTARG};;
    n) # integer for specific job number
        declare -i BOOL_INT=1
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
if [[ $BOOL_UPDATE -eq 1 ]]; then
	update
fi
if [[ $BOOL_ANAL -eq 1 ]]; then
	analysis
fi


# TODO :: parse results (en mass, from parm file)
