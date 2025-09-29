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
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# default job name
JOB="vfrac_study"
# boolean that determines if the feb file path has been passed to the method
declare -i BOOL_FEBFILE=0
# boolean for overwrite protocol
declare -i BOOL_OVERWRITE=0
# boolean that determines if the script should generate directories
declare -i BOOL_GEN=0
# boolean that determines if the script should analyze and compile results
declare -i BOOL_ANAL=0
# boolean that determines if the script should submit to slurm
declare -i BOOL_SUB=0
# boolean that determines if the script should run locally
## testable parameters
# list of volume fractions to test
PARM_P=( "0.01" "0.1" "1.0" "10." "100." )
# list of elasticity values to test
PARM_E=( "0.005" "0.05" "0.5" "5.0" "50." )
# list of permiability values to test
PARM_K=( "0.00001" "0.0001" "0.001" "0.01" "0.1" )
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

}

# generate simulation parameters
gen () {

    ## PARAMETERS
    # file which contains job parameters
    local parm_file=${JOB}.csv
    # integer used to count the number of unique parameters which are tested
    declare -i count_int=0
    # header used for parameter file
    local parm_header="n,id,dir,E,K,P"

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check if the path to the simulation job directory already exists
    if [[ -p ${DIR}/${JOB} ]]; then
        # if the job already exists, check if overwrite has been called
        if [[ $BOOL_OVERWRITE -eq 1 ]]; then
            # the directory exists and overwrite has been called
            display_error "TODO :: implement method for clearing existing simulations with overwrite flag in 'gen' subroutine"
        else
            # the directory already exists and overwrite has not been called
            display_error "job directory already exists and cannot be overwritten (to overwrite, call -o)"
        fi
    else
        # the job path does not exist, so make it
        mkdir -p ${DIR}/${JOB}
        # initialize the parameter file
        echo $parm_header #> $parm_file
    fi

    # if a parameter file has already been written to the job directory, check for overwrite

    # loop through elastic, permiability constants
    for e in "${PARM_E[@]}"; do
        declare -i e_count=0
        for k in "${PARM_K[@]}"; do
            declare -i k_count=0
            for p in "${PARM_P[@]}"; do
                declare -i p_count=0

                # generate directories
                id="E${e_count}K${k_count}P${p_count}"
                path="E${e_count}/K${k_count}/P${p_count}/"
                echo "${n_count},${id},${path},${e},${k},${p}"
                # write feb file
                # generate max frequency analysis

                # accumulate the void fraction count
                ((p_count++))
                # accumulate the total simulation parameter count
                ((n_count++))
            done
            # accumulate the permeability parameter count
            ((k_count++))
        done
        # accumulate the elasticity parameter count
        ((e_count++))
    done
}

# submit simulations to compute cluster via slurm
sub () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
}

# compile simulation results
anal () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
}

## OPTIONS
# parse option
while getopts "hof:p:j:gas" opt; do
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
        g) # generate simulation files and directories
            declare -i BOOL_GEN=1 ;;
        a) # analyze and compile simulation data
            declare -i BOOL_ANAL=1 ;;
        s) # submit simulations for execution on slurm
            declare -i BOOL_SUB=1 ;;
        ?) # default option, exit nonzero
            help $NONZERO_EXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
# check parameters passed as options to the script
check

# generate simulations
if [[ $BOOL_GEN -eq 1 ]]; then
    gen
fi

# submit simulations
if [[ $BOOL_SUB -eq 1 ]]; then
 sub
fi

# analyze and compile simulations
if [[ $BOOL_SUB -eq 1 ]]; then
    anal
fi