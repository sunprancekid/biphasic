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
PLOT="python ./programs/python/analysis.py"
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

## PARAMETERS
# filename
FILENAME="programs/bash/jobs/mesh.sh"
# purpose
PURPOSE="scaling effect of FEB meshing on model properties and performance"
# directory which contains jobs
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean for declaring job name
declare -i BOOL_JOB=0
# job name
JOB="mesh"
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

## FEB PARAMETERS - CONSTANTS
# permiability (mm^4 / N * s)
PERMEABILITY="0.001"
# poissons ratio
POISSON_RATIO="0.3"
# solid volume fraction
VOLUME_FRAC="0.2"
# loading depth (mm)
VAL_LOAD_DEPTH="0.1"
# oscillation amplitude (mm)
VAL_OSCILLATION_AMPLITUDE="0.05"
# elastic modulus (MPa)
ELASTIC_MODULUS="0.5"
# oscillation period
VAL_OSCILLATION_PERIOD="1000"

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
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -d  << ARG >>\t| DIRECTORY path to generate jobs (default is ${DIR})"
    echo -e " -j  << ARG >>\t| MANDATORY: JOB name, corresponds to feb file."
    echo -e " -f  << ARG >>\t| MANDATORY: FEB directory, contains premade meshing files stored within according to \$FEB/mesh/\$JOB."
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
    # constant elastic modulus
	$MAT_EMOD -d $DIR -j $JOB -C $ELASTIC_MODULUS
    # constant oscillation period
	$OSC_PER -d $DIR -j $JOB -C $VAL_OSCILLATION_PERIOD

	# vary the meshing integer N, calculate NE, append if mesh file exists
	declare -i HAS_START=0
	declare -i N_START=0
	declare -i HAS_END=0
	declare -i N_END=0
	for n in $(seq 1 20); do
        FEB_MESH=${FEB_DIR}mesh/${JOB}/${JOB}_n${n}.feb
        if [[ -f ${FEB_MESH} ]]; then
            # the mesh file exists, record the integer
            if [[ $HAS_START -eq 0 ]]; then
                declare -i N_START=$n
                declare -i HAS_START=1
            fi
        else
            # the meshing integer does not exist
            # check if the start has already been found
            if [[ $HAS_START -eq 1 && $HAS_END -eq 0 ]]; then
                # the meshing file sequence has started, but not ended
                # the last file is the previous integer
                declare -i HAS_END=1
                declare -i N_END=$(($n-1))
            fi
        fi
	done
	# if the end has not been identified yet,
	# the last meshing file is the final integer
	if [[ $HAS_START -eq 1 && $HAS_END -eq 0 ]]; then
        declare -i HAS_END=1
        declare -i N_END=$n
	fi
	# if the start was never identified, through an error
	if [[ $HAS_START -eq 0 ]]; then
        display_error "no meshing files were identified in '${FEB_DIR}/mesh/${JOB}/'."
	fi

	## generate parameters corresponding to the meshing integer N
	## and the number of elements NE
	# number of elements (symbolic relationship) - NE
	$FEB_PARM -d $DIR -j $JOB -x 'na' -k 'NE' -D 'number_meshing_elements' -C '2*(NM)*(NM^2)' -R
	# meshing integer - N
	N_DIFF=$(($N_END-$N_START+1))
	## TODO :: add format integer
	$FEB_PARM -d $DIR -j $JOB -x 'na' -k 'NM' -D 'meshing_integer' -A $N_START -B $N_END -N $N_DIFF

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
	declare -i MESH_COL=0
	for i in $(seq 1 $N_COL); do
        if [ "$($PARSE_CSV -f $PARM_FILE -l 1 -c $i )" = "NM" ]; then
            declare -i MESH_COL=$i
        fi
	done
	# loop through the parameter file
	declare -i N_LINES=$( $PARSE_CSV -f $PARM_FILE -l)
	for i in $(seq 2 $N_LINES); do
        # get the meshing integer
        declare -i SIM_INT=$($PARSE_CSV -f $PARM_FILE -l $i -c 1)
        declare -i MESH_INT=$($PARSE_CSV -f $PARM_FILE -l $i -c $MESH_COL)
        echo $MESH_INT
        FEB_FILE=${FEB_DIR}mesh/${JOB}/${JOB}_n${MESH_INT}.feb
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
	# normal
	return

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
	# none
	return
}


## OPTIONS
# parse options
while getopts "hvVopgrslad:j:f:n:c:" opt; do
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
    f) # feb file specification
        declare -i BOOL_FEB=1
        FEB_DIR=${OPTARG};;
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
