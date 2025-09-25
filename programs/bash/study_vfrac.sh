#!/bin/bash
set -e

## Matthew Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.09.25

## perform max frequency analysis as a function of the volume fraction


## PARAMETERS
## callable subscripts
# used to parse information from csv files
# used for generate and submit slurm scripts
## script execution
# nonzero exit code for errors
declare -i NONZERO_EXITCODE=120
# script filename
FILENAME="study_vfrac"
# script purpose
PURPOSE="perform max frequency analysis as a function of volume fraction, permeability, and elasticity."
# default directory path
DIR="./"
# default job name
JOB="vfrac_study"
# boolean that determines if the feb file path has been passed to the method
declare -i BOOL_FEBFILE=0
# boolean for overwrite protocol
declare -i BOOL_OVERWRITE=0
# boolean that determines if the script should generate directories
# boolean that determines if the script should analyze and compile results
# boolean that determines if the script should submit to slurm
# boolean that determines if the script should run locally
## testable parameters
# list of volume fractions to test
# list of elasticity values to test
# list of permiability values to test
# maximum time scale to test
# minimum timescale to test
# number of timescales to test


## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first option: exit code
    local exitcode=$1

    ## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # discription
    # echo -e "\nDESCRIPTION: \n"
    # display script options
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0."
    echo -e " -o\t\t| overwrite existing simulation directories, if they exist; otherwise abort."
    echo -e " -g\t\t| generate simulation directories."
    echo -e " -s\t\t| submit simulations to slurm."
    echo -e " -a\t\t| analyze and compile simulation results."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f << ARG >>\t| MANDATORY: path to feb file to use as base model (typically stored in 'models')."
    echo -e " -p << ARG >>\t| path to which contains directory hirearchy (default is ${DIR})."
    echo -e " -j << ARG >>\t| named assgined to job, contains simulation directories (default is ${JOB})."
    echo -e ""

    # exit with exit code
    exit $exitcode

    }

# display formatted error message, exit nonzero
display_error () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: error message to display
    local err_msg=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${err_msg}.\n"
    help $NONZERO_EXITCODE

}

# check that the correct parameters were specified before executing
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the feb file has been specified
    if [[ $BOOL_FEBFILE -eq 0 ]]; then
        # report error and exit
        display_error "feb file must be specified (-f)"
    # check that the feb file exists
    elif [[ ! -f $FEBFILE ]]; then
        # report error and exit
        display_error "unable to feb file '${FEBFILE}'"
    fi

    # check that the directory path exists
    if [[ ! -p $DIR ]]; then
        # if it does not exist, create it
        mkdir -p $DIR
    fi

    # check if the job already exists
    if [[ -p ${DIR}/${JOB} && $BOOL_OVERWRITE -eq 0 ]]; then
        # if the job already exists and overwrite has not been called
        display_error "job directory already exists and cannot be overwritten (to overwrite, call -o)"
    elif [[ ! -p ${DIR}/${JOB} ]]; then
        # if the job path does not exist, make it
        mkdir -p ${DIR}/${JOB}
    fi

}

# generate simulation parameters

# submit simulations to compute cluster via slurm

# compile simulation results

## OPTIONS
# parse option
while getopts "hof:p:j:" opt; do
    case $opt in
        h) # display help, exit zero
            help 0 ;;
        o) # set overwrite protocol
            declare -i BOOL_OVERWRITE=1 ;;
        f) # set the path to the feb file
            declare -i BOOL_FEBFILE=1
            FEBFILE=${OPTARG} ;;
        p) # set the path to generate the simulation directories
            DIR=${OPTARG} ;;
        j) # set the job name
            JOB=${OPTARG} ;;
        ?) # default option, exit nonzero
            help $NONZERO_EXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
# check parameters passed as options to the script
check
