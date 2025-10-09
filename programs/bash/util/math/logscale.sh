#!/bin/bash
set -e

## Matthew Dorsey
## @ mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Insitute for Colloids and Interfacial Sciences
## 2025.10.08

## FILENAME: programs/bash/util/math/logscsale.sh
## PURPOSE: generate range of values linearly along a logscsale

## MODULES
# none

## PARAMETERES
# nonzero exit value
declare -i NONZERO_EXITCODE=120
# file name
FILENAME="progams/bash/util/math/logscale.sh"
# purpose
PURPOSE="generate one value (n) corresponding to range of number (N) between (A) and (B) along either linear or logscale"

## METHODS
# display script used, exit with exitcode
help () {

    ## PARAMETERES
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # first option: exit code
    local exitcode=$1

    ## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # display script options
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0."
    echo -e "\n ## SCRIPT MANDATORY PARAEMETERS ## \n"
    echo -e " -A << ARG >>\t| MANDATORY: MINIMUM value assigned to parameter."
    echo -e " -B << ARG >>\t| MANDATORY: MAX value assigned to parameter."
    echo -e " -L << ARG >>\t| MANDATORY: generate values along LOG scale (default is LINEAR)."
    echo -e " -n << ARG >>\t| MANDATORY: integer representing current NUMBER to generate along scale (script returns value corresponding to n)"
    echo -e " -N << ARG >>\t| integer representing TOTAL NUMBER of unique values to generate between A and B."
    echo -e ""

    # exit with exit code
    exit $exitcode

}

# display error message, call help with nonzero exit code
display_error () {

    ## PARAMETERS
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

# check options passed to script call, before script execution
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    display_error "TODO :: implement check"
}

# generate number along logscale, echo
logscale () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    display_error "TODO :: implement logscale"
}

## OPTIONS
# parse options
while getopts "h" opt; do
    case $opt in
        h) # call help
            help 0 ;;
        ?) # unspecified flag
            help $NONZERO_EXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# check options
check
