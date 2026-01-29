#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2026.01.14

## MODULES
# used to parse and write information to csv files
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# generate directory hirearchy and feb parameterization
GEN="./programs/bash/simulation/generate.sh"
# submit job to linux cluster en masseHOSTNAME
RUN="./programs/bash/simulation/run.sh"
# contains analysis routines
ANAL="./programs/bash/simulation/analysis.sh"
# show results after analysis has been performed
PLOT="python ./programs/python/febio/analysis/scaling.py"
# instructions for syncing local and remote directories
SYNC="./programs/bash/util/sync.sh"

## MODULES - FEB PARAMETERIZATION
# custom FEB parameter
FEB_PARM="./programs/bash/parameter/feb_parameter.sh"
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
# length scale
LENGTH_SCALE="./programs/bash/parameter/length-scale.sh"

## PARAMETERS
# filename
FILENAME="programs/bash/jobs/scale.sh"
# purpose
PURPOSE="scaling effect of model length scale on simulation results"
# directory which contains jobs
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean for declaring job name
declare -i BOOL_JOB=0
# job name
JOB="scale"
# boolean for file overwriting
declare -i BOOL_OVERWRITE=0
# boolean for parameter and config file writing
declare -i BOOL_PARM=0
# boolean for feb directory
declare -i BOOL_FEB=0
# boolean for feb model name
declare -i BOOL_MODEL=0
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
# boolean for deleting xplt files
declare -i BOOL_XPLT=0

## FEB PARAMETERS - CONSTANTS
# permiability (mm^4 / N * s)
PERMEABILITY="0.0001"
# poissons ratio
POISSON_RATIO="0.3"
# solid volume fraction
VOLUME_FRAC="0.2"
# elastic modulus (MPa)
ELASTIC_MODULUS="0.5"
# reference scale (mm)
REF_SCALE="0.125"
# loading depth (mm)
VAL_LOAD_DEPTH="0.01"
# oscillation amplitude (mm)
VAL_OSCILLATION_AMPLITUDE="0.005"

## OSCILLATION PERIOD PARAMETERS (logscale)
# minimum period to test (seconds)
MIN_PERIOD="10."
# maximum period to test (seconds)
MAX_PERIOD="100000."
# number of unique period values to test
N_PERIOD="40"

## METHODS
# display options, exit
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
#     echo -e " -v\t\t| VERBOSE script execution."
#     echo -e " -V\t\t| VERY VERBOSE script execution."
#     echo -e " -o\t\t| overwrite existing simulation files."
    echo -e " -p\t\t| create PARAMETER and CONFIG files."
    echo -e " -g\t\t| GENERATE FEB files."
    echo -e " -r\t\t| RUN jobs."
    echo -e " \t-s\t| SUBMIT JOBS to HPC cluster via slurm."
    echo -e " \t-l\t| run jobs LOCALLY."
    echo -e " -a\t\t| ANALYZE results post-simulation."
    echo -e " \t-x\t| delete XPLT files if the exist."
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -d  << ARG >>\t| DIRECTORY path to generate jobs (default is ${DIR})"
    echo -e " -j  << ARG >>\t| MANDATORY: JOB name, corresponds to feb file."
    echo -e " -f  << ARG >>\t| MANDATORY: FEB directory, contains premade meshing files stored within according to \$FEB/scale/\$MODEL/."
    echo -e " -m  << ARG >>\t| MANDATORY: MODEL name, located in FEB directory."
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
        	display_error "the job parameters have already been generated in '${DIR}${JOB}' and cannot be overwritten without an overwrite flag (-o)."
      	elif [[ -d ${DIR}${JOB} && $BOOL_OVERWRITE -eq 1 ]]; then
      		display_error "TODO :: implement overwrite routine."
      	fi
    fi

    # directory generation and feb parameterization
    if [[ $BOOL_GEN -eq 1 ]]; then
        # check that the feb file exists
        if [[ $BOOL_FEB -eq 0 ]]; then
            display_error "must specify FEB FILE (-f)"
        elif [[ ! -d $FEB_DIR ]]; then
            display_error "specified FEB FILE '${FEB_FILE}' does not exist."
        fi
    fi

    # check the model directory and name
    if [[ $BOOL_FEB -eq 0 ]]; then
        display_error "must specify path to FEB models (option -f)"
    fi
    if [[ $BOOL_MODEL -eq 0 ]]; then
        display_error "must specify the MODEL name (option -m)"
    fi
    SCALE_DIR=${FEB_DIR}scale/${MODEL}/
    if [[ ! -d $SCALE_DIR ]]; then
        # if the directory does not exist, throw an error
        display_error "FEB directory which contains scaling MODELS '${SCALE_DIR}' does not exist. Directory hirearchy must match pattern '\${FEB}/scale/\${MODEL}/'."
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
    # constant elastic modulus
	$MAT_EMOD -d $DIR -j $JOB -C $ELASTIC_MODULUS

	## set dependents
	# constant loading depth (is proportional to the length scale)
	$LOAD_DEPTH -d $DIR -j $JOB -C "($VAL_LOAD_DEPTH)*(Z/${REF_SCALE})" -R
	# constant oscillation amplitude (is proportional to the length scale)
	$OSC_AMP -d $DIR -j $JOB -C "($VAL_OSCILLATION_AMPLITUDE)*(Z/${REF_SCALE})" -R

	## set variables
	# model length scale
	$LENGTH_SCALE -d $DIR -j $JOB -f ${FEB_DIR} -m ${MODEL}
	# oscillation frequency sweep
	$OSC_PER -d $DIR -j $JOB -A $MIN_PERIOD -B $MAX_PERIOD -N $N_PERIOD -L

}

# generate directories and parameterize feb files
generate () {

	## PARAMETER
	# job parameter file
	PARM_FILE=${DIR}${JOB}/${JOB}.parm.csv

	## ARGUMENT
	# none

	## SCRIPT
	# identify the head column that contains NM parameter
	declare -i N_COL=$( $PARSE_CSV -f $PARM_FILE -l 1 -c)
	declare -i SCALE_COL=0
	for i in $(seq 1 $N_COL); do
        if [ "$($PARSE_CSV -f $PARM_FILE -l 1 -c $i )" = "Z" ]; then
            declare -i SCALE_COL=$i
        fi
	done
	# loop through the parameter file
	declare -i N_LINES=$( $PARSE_CSV -f $PARM_FILE -l)
	for i in $(seq 2 $N_LINES); do
        # get the scaling value
        declare -i SIM_INT=$($PARSE_CSV -f $PARM_FILE -l $i -c 1)
        SCALE_VAL=$($PARSE_CSV -f $PARM_FILE -l $i -c $SCALE_COL)
        FEB_FILE=${FEB_DIR}scale/${MODEL}/${SCALE_VAL}.feb
        # generate the feb file iteratively
        $GEN -d $DIR -j $JOB -f $FEB_FILE -n $SIM_INT
	done

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
	# check if xplt deletion has been specified
	if [[ $BOOL_XPLT -eq 1 ]]; then
		RUN_FLAGS="${RUN_FLAGS} -x"
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

}

# sync local directories with jobs on remote cluster
update () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# none

	## SCRIPT
	# none
	return

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
		$ANAL -d $DIR -j $JOB -H -C
	fi
	# plot results after analysis
# 	$PLOT $DIR $JOB
}


## OPTIONS
# parse options
while getopts "hvVopgrslad:j:f:m:n:c:x" opt; do
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
    d) # specify directory for job
    	DIR=${OPTARG} ;;
    j) # job title
        declare -i BOOL_JOB=1
        JOB=${OPTARG};;
    f) # feb directory specification
        declare -i BOOL_FEB=1
        FEB_DIR=${OPTARG};;
    m) # feb model name
        declare -i BOOL_MODEL=1
        MODEL=${OPTARG} ;;
    n) # integer for specific job number
        declare -i BOOL_INT=1
        SIM_INT=${OPTARG} ;;
    c) # specify check file
        declare -i BOOL_CHECKFILE=1
        CHECKFILE=${OPTARG} ;;
    x) # delete xplt files
    	declare -i BOOL_XPLT=1 ;;
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
