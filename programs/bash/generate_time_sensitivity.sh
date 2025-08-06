#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.08.06

## script for generating simulations which adjust only the numerical time step

## PARAMETERS
# filename
FILENAME="generate_time_sensitivity"


## FUNCTIONS
# displace options
help () {

    # PARAMETERS
    # none


    ## ARGUMENTS
    # first argument: exit code
    local exitcode=$1


    ## SCRIPT
    # display useage
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: submit febio jobs to MPIKG compute cluster via slurm.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"

    # exit with exit code
    exit $exitcode
}


## OPTIONS
# parse options
while getopts "h" option; do
    case $option in
        h) # call help with nonzero exit code
            help 0 ;;
        ?) # default for unspecified option
            # call help with nonzero exit code
            help $NONZEROEXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
# none
