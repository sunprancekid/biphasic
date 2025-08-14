#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.14
## submits jobs in batch
## user can specify running jobs locally, or submitting jobs to a cluster

## PARAMETERS
# nonzero exit code
declare -i NONZEROEXITCODE=120


## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first agrument: exit code
    local exitcode=$1

    ## SCRIPT
    # display options
    echo -e "TODO :: add options"
    # exit
    exit $exitcode

}

# check that the right parameters have been specified by the user
check () {

    ## PARAMTERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check options
    echo "TODO :: check options .."

}


## OPTIONS
# none


## ARGUMENTS
# none


## SCRIPT
# none
