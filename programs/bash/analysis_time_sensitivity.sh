#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.08.06

## used to study the effect of numerical step size on results FEM simulation

## PARAMETERS
# filename
FILENAME="analysis_time_sensitivity"
# list of step sizes to test
# n refers to the number numerical steps in one period
N_LIST=( 10 20 40 60 80 120 160 200 240 280 320 )
## FLAG PROTOCOL
# boolean determining if the script should be execute verbosely
declare -i BOOL_VERBOSE=0
## MANDATORY FLAG PARAMETERS
# boolean determining if the path to create directory hirearchy has been specified
# boolean determining if the
## OPTIONAL FLAG PARAMETERS
# default cycle period for simulation
#


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
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: analysis for the effect of numerical step size on results from febio simulations.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " NONE "

    # exit with exit code
    exit $exitcode
}



## OPTIONS
# parse options
while getopts "hf:p:" option; do
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
# loop through each step size
for n in ${N_LIST[@]}; do
    echo $n
done
# generate paths
# determine parameters
# geeration simulation
# save parameters
# submit simulation to slurm
# add analysis options
