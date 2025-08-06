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
## FLAG PROTOCOL
# execute script verbosely
declare -i BOOL_VERBOSE=0
## MADNATORY SCRIPT PARAMETERS
# boolean that determines if the febio model file has been assigned
declare -i BOOL_FEB_FILE=0
# boolean that determines if the path was specified
declare -i BOOL_SIM_PATH=0
## OPTIONAL SCRIPT PARAMETERS
# none


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
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: generate simulation that adjust the size of the numerical time step in order to determine the effect of time step analysis on the hystersis calculations.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
    echo -e " -v\t\t| execute script verbosely."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use as a default."
    echo -e " -p  << ARG >>\t| MANDATORY: specify the path to copy model file."
    echo -e " -m  << ARG >>\t| MANDATORY: specify max simulation step size."
    echo -e " -l  << ARG >>\t| OPTIONAL:  specify simulation length (default is .. )."
    echo -e " -n  << ARG >>\t| OPTIONAL:  specify starting step size (default is 1 / 100 of max step)."

    # exit with exit code
    exit $exitcode
}


## OPTIONS
# parse options
while getopts "hf:p:" option; do
    case $option in
        h) # call help with nonzero exit code
            help 0 ;;
        v) # execute script verbosely
            declare -i BOOL_VERBOSE=1 ;;
        f) # specify the febio file
            declare -i BOOL_FEB_FILE=1
            FEB_FILE=${OPTARG} ;;
        p) # specify path to save simulation
            declare -i BOOL_SIM_PATH=1
            SIM_PATH=${OPTARG} ;;
        ?) # default for unspecified option
            # call help with nonzero exit code
            help $NONZEROEXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
# given a step size or the number of steps
# assign the total number of interations
# assign the starting step size
# assign the minimum and maximum step size
# assign the loadcurve
