#!/bin/bash
set -e

## Matthew Dorsey
## @mad-mpikg
## matthew.dorsey@mpikp.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.10.15

## FILENAME: programs/bash/simulation/generate.sh
## PURPOSE: use parameter and config files to generate simulation directories and parameterized 'feb' files

## MODULES
# used to parse and write information to csv files
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# used to augment feb files
AUGMENT_FEB="python programs/python/febio/augment_feb_batch.py"

## CONSTANTS
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# file name
FILENAME="programs/bash/simulation/generate.sh"
# file purpose
PURPOSE="use parameter and config files to generate simulation directories and parameterized '.feb' files."

## PARAMETERS
# boolean used for job
declare -i BOOL_JOB=0
# boolean used for feb files
declare -i BOOL_FEB=0
# boolean for job number
declare -i BOOL_NUMBER=0
# default directory path for storing parameters
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"

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
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -j  << ARG >>\t| MANDATORY: JOB name."
    echo -e " -f  << ARG >>\t| MANDATORY: path to FEB FILE which is used a base for parameterization."
    echo -e " -d  << ARG >>\t| DIRECTORY which contains job (default is ${DIR})."
    echo -e " -n  << ARG >>\t| generate single parameter set associated with integer NUMBER in JOB."
    echo -e ""

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

# check script parameters
check () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# none

	## SCRIPT
	# check that the job has been specified
	if [[ $BOOL_JOB -eq 0 ]]; then
        display_error "must specify the JOB (option -j)"
	fi
	# check that the feb file has been specified
	if [[ $BOOL_FEB -eq 0 ]]; then
        display_error "must specify the FEB FILE (option -f)"
	fi
	# check that the directory exists
	if [[ ! -d $DIR ]]; then
        display_error "the DIRECTORY '${DIR}' cannot be found (option -d)"
	fi
	# check that the job exists
	SUBDIR=${DIR}${JOB}
	if [[ ! -d $SUBDIR ]]; then
        display_error "the JOB '${JOB}' does not exist within DIRECTORY '${DIR}'"
	fi
	# check that feb file exists
	if [[ ! -f $FEB ]]; then
        display_error "unable to find FEB FILE '${FEB}' (option -f)"
	fi
	# check that config and parameter files exist
	PARM_FILE="$SUBDIR/$JOB.parm.csv"
	CONFIG_FILE="$SUBDIR/$JOB.config.csv"
	if [[ ! -f ${PARM_FILE} ]]; then
        display_error "JOB '${JOB}' parameter file '${PARM_FILE}' has not been generated yet"]
	elif [[ ! -f ${CONFIG_FILE} ]]; then
        display_error "JOB '${JOB}' configuration file '${CONFIG_FILE}' has not been generated yet"
	fi
}

# generate simulations en gen_batch
gen_batch () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # open the parameter file
    declare -i LINES=$( $PARSE_CSV -f $PARM_FILE -l )
    # loop through each line
    for l in $( seq 2 $LINES); do
        # generate directory
        local simid=$( $PARSE_CSV -f $PARM_FILE -l $l -c 2 )
        local simdir=$SUBDIR/$( $PARSE_CSV -f $PARM_FILE -l $l -c 3 )
        if [[ ! -d $simdir ]]; then
            mkdir -p $simdir
        fi
        # copy feb to simulation directory
        cp $FEB $simdir$simid.feb
        # augment feb locally (python call)
        $AUGMENT_FEB $FEB $DIR $JOB $((${l}-1))
    done
}

# generate single simulation
gen_single () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: interger corresponding to job number in parameter file
    local n=$1

    ## SCRIPT
    # check that the integer passed to the method exists
    declare -i N_LINES=$($PARSE_CSV -f $PARM_FILE -l )
    if [[ $n -gt $(($N_LINES-1)) ]]; then
        # the simulation integer is to great
        display_error "the integer passed to the program '$n' does not exist within '${JOB}'."
    fi
    # get the simulation information from the parameter file
    local simid=$($PARSE_CSV -f $PARM_FILE -l $((n+1)) -c 2)
    local simdir=$($PARSE_CSV -f $PARM_FILE -l $((n+1)) -c 3)
    if [[ ! -d $simdir ]]; then
        mkdir -p $simdir
    fi
    # copy feb to simulation directory
    cp $FEB $simdir$simid.feb
    # augment feb locally (python call)
    $AUGMENT_FEB $FEB $DIR $JOB $n
}

# OPTIONS
# parse options
while getopts "hj:f:d:n:" opt; do
	case $opt in
		h) # display options
			help 0 ;;
        j) # job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        f) # feb file
            declare -i BOOL_FEB=1
            FEB=${OPTARG} ;;
        d) # directory
            DIR=${OPTARG} ;;
        n) # integer number
            declare -i BOOL_NUMBER=1
            declare -i NUMBER=${OPTARG} ;;
        ?) # default, display options with nonzero exitcode
            help $NONZERO_EXITCODE
	esac
done

## SCRIPT
# check script inputs
check

# generate directories and feb files
if [[ $BOOL_NUMBER -eq 0 ]]; then
    gen_batch
else
    gen_single $NUMBER
fi
