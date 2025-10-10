#!/bin/bash
set -e 

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2025.10.10

## FILENAME: programs/bash/parameters/oscillation/amplitude.sh
## PURPOSE: specify or vary the amplitude associated with a FEB oscillation simulation

## MODULES
# generates parameters and integrates with feb file
FEB_PARAMETER="./programs/bash/parameters/feb_parameter.sh"

## PARAMETERS - CONSTANTS
# non-zero exit code
declare -i NONZERO_EXITCODE=120
# script filename
FILENAME="programs/bash/parameters/loading/depth.sh"
# script purpouse
PURPOSE="specify or vary the depth of tip prestress associated with FEB loading simulations"

## PARAMETERS - OPTIONS
# none

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

## OPTIONS
# prase options
while getopts "h" opt; do
	case $opt in
		h) # display options
			help 0 ;; 
		?) # default
			help $NONZERO_EXITCODE
	esac
done

## ARGUMENTS
# none

## SCRIPT
# none