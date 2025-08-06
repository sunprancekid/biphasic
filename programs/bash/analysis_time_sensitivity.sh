#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.08.06

## used to study the effect of numerical step size on results FEM simulation

## PARAMETERS
# nonzero exit code
declare -i NONZEROEXITCODE=120
# filename
FILENAME="analysis_time_sensitivity"
# list of step sizes to test
# n refers to the number numerical steps in one period
N_LIST=( 10 20 40 60 80 120 160 200 240 280 320 )
# header used to store parameters
PARM_HEADER=""
## FLAG PROTOCOL
# boolean determining if the script should be execute verbosely
declare -i BOOL_VERBOSE=0
## MANDATORY FLAG PARAMETERS
# boolean determining if the path to create directory hirearchy has been specified
declare -i BOOL_SIM_PATH=0
# boolean determining if the '.feb' model file to use
declare -i BOOL_FEB_FILE=0
# boolean determining if the
## OPTIONAL FLAG PARAMETERS
# job name
JOB="ts"
# default cycle period for simulation
PERIOD="2."
# default number of cycles
N_CYCLES="5"


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
    echo -e " -h\t\t| display options, exit 0."
    echo -e " -v\t\t| execute script verbosely."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use."
    echo -e " -p  << ARG >>\t| MANDATORY: specify the path to generate directory hirearchy 'time_sensitivity'."
    echo -e " -j  << ARG >>\t| OPTIONAL: rename the job (default is ${JOB})."
    echo -e " -c  << ARG >>\t| OPTIONAL: specify cycle period as float (default is ${PERIOD})."
    echo -e " -n  << ARG >>\t| OPTIONAL: specify number of cycles as integer (default is ${N_CYCLES})"
    echo -e "\n"

    # exit with exit code
    exit $exitcode
}

# check that parameters passed to script are correct
check () {

    ## PARAMETERS
    # none


    ## ARGUMENTS
    # none


    ## SCRIPT
    # check that the model file exists
    if [ $BOOL_FEB_FILE -eq 0 ]; then
        # feb file must be specified
        echo -e "\nERROR :: ${FILENAME} :: must specify '.feb' file.\n"
        help $NONZEROEXITCODE
    fi
    # the feb file exists

    # check that the path exist
    if [ $BOOL_SIM_PATH -eq 0 ]; then
        # the user must specify the directory path
        echo -e "\nERROR :: ${FILENAME} :: must specify path.\n"
        help $NONZEROEXITCODE
    elif [ ! -d $SIM_PATH ]; then
        # if it does not, create it
        mkdir -p "${SIM_PATH}/${JOB}"
    elif [ ! -d "${SIMPATH}/${JOB}" ]; then
        mkdir -p "${SIM_PATH}/${JOB}"
    fi
    # the path has been specified and does exist


}


## OPTIONS
# parse options
while getopts "hf:p:j:c:n:" option; do
    case $option in
        h) # call help with nonzero exit code
            help 0 ;;
        f) # specify '.feb' model file
            declare -i BOOL_FEB_FILE=1
            FEB_FILE=${OPTARG} ;;
        p) # specify path to generate simulation directory
            declare -i BOOL_SIM_PATH=1
            SIM_PATH=${OPTARG} ;;
        j) # rename job
            JOB=${OPTARG} ;;
        c) # cycle period
            PERIOD=${OPTARG} ;;
        n) # number of cycles
            N_CYCLES=${OPTARG} ;;
        ?) # default for unspecified option
            # call help with nonzero exit code
            help $NONZEROEXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
# check that all of the correct parameters exist
check

# loop through each step size
for n in ${N_LIST[@]}; do
    echo $n
    # generate path
    SUBDIR="${SIM_PATH}/${JOB}/n_${n}"
    if [ ! -d $SUBDIR ]; then
        # if the path does not exist, make it
        mkdir -p $SUBDIR
    fi

    # determine simulation parameters based on input
    # set the max step size according to period and number of steps
    # set the simulation length according to period and number of cycles

    # generate simulation files
    # save parameters to csv


done

# submit simulation to slurm
# add analysis options
