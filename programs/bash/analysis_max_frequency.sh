#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.08.06

## adjust the osciliation frequency of beam bending and determine the work done


## PARAMETERS
# nonzero exit code
declare -i NONZEROEXITCODE=120
# filename
FILENAME="analysis_max_frequency"
## FLAG PROTOCOL
# none
## MANDATORY FLAG OPTIONS
# none
## OPTIONAL FLAG OPTIONS
# job name
JOB="max_frequency"
# minimum frequency
MIN_FREQ="2."
# maximum frequency
MAX_FREQ="200."
# test points
declare -i N_TEST=20


## FUNCTIONS
# displace options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: exit code
    local exit_code=$1

    ## SCRIPT
    # display options
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: analysis for the effect of bending frequency on material hysteresis.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use, presumed to be stored in 'models/'."
    echo -e " -p  << ARG >>\t| MANDATORY: specify the path to generate directory hirearchy 'time_sensitivity'."
    echo -e " -j  << ARG >>\t| OPTIONAL:  rename the job (default is ${JOB})."
    echo -e " -A  << ARG >>\t| OPTIONAL:  specify the initial frequency (default is ${MIN_FREQ})."
    echo -e " -B  << ARG >>\t| OPTIONAL:  specify the maximum frequency (default is ${MAX_FREQ})."
    echo -e " -N  << ARG >>\t| OPTIONAL:  specify the number of points to test (default is ${N_TEST})."

    # exit
    exit $exit_code

}

# check that all mandatory parameters have been provided
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    return

}


## OPTIONS
# none


## ARGUMENTS
# none

## SCRIPT
# check parameters
# generate simulations
