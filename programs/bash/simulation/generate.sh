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
	# check that the directory exists
	# check that the job exists
	# check that feb file exists
	display_error "TODO :: implement check"
}

# generate simulations en gen_batch
gen_batch () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    display_error "TODO :: implement batch job generation"
}

# generate single simulation
gen_single () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: interger corresponding to job number in parameter file
    local n=$1

    ## SCRIPT
    # none
    display_error "TODO :: implement single job generation"
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
            declare -i BOOL_NUMBER=0
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
