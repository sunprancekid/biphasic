#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.08.06

## script for generating simulations which adjust only the numerical time step

## PARAMETERS
# filename
FILENAME="augment_feb"
## FLAG PROTOCOL
# execute script verbosely
declare -i BOOL_VERBOSE=0
## MADNATORY SCRIPT PARAMETERS
# boolean that determines if the febio model file has been assigned
declare -i BOOL_FEB_FILE=0
# boolean that determines if the path was specified
declare -i BOOL_SIM_PATH=0
## OPTIONAL SCRIPT PARAMETERS
# boolean that determines if the period has been specified
declare -i BOOL_PERIOD=0


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
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: augment the '.feb' files in order to parameterize simulation conditions.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
    echo -e " -v\t\t| execute script verbosely."
    echo -e "\n ## SCRIPT PARAMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use as a default."
    echo -e " -p  << ARG >>\t| MANDATORY: specify the path to copy model file."
    echo -e " -m  << ARG >>\t| MANDATORY: specify max simulation step size."
    echo -e " -l  << ARG >>\t| OPTIONAL:  specify simulation length (default is .. )."
    echo -e " -n  << ARG >>\t| OPTIONAL:  specify starting step size (default is 1 / 100 of max step)."
    echo -e " -p  << ARG >>\t| OPTIONAL:  specify the period used for beam bending."
    echo -e "\n"

    # exit with exit code
    exit $exitcode
}


## OPTIONS
# parse options
while getopts "hf:p:m:l:" option; do
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
        m) # specify the maximum simulation step size
            STEP_SIZE=${OPTARG} ;;
        l) # simulation length
            LENGTH=${OPTARG} ;;
        p) # specify cycle period
            declare -i BOOL_PERIOD=0
            PERIOD=${OPTARG} ;;
        ?) # default for unspecified option
            # call help with nonzero exit code
            help $NONZEROEXITCODE
    esac
done


## ARGUMENTS
# none


## SCRIPT
echo $FEB_FILE
# copy the feb file to the path
# given a step size or the number of steps
# assign the maximum step size
sed -i "s/<dtmax>0.1<\/dtmax>/<dtmax>${STEP_SIZE}<\/dtmax>/" $FEB_FILE
# assign the initial step size
MIN_STEP=$( echo "${STEP_SIZE} / 10" | bc -l )
sed -i "s/<step_size>0.01<\/step_size>/<step_size>${MIN_STEP}<\/step_size>/" $FEB_FILE
# assign the total number of interations (based on the minimum)
TIME_STEPS=$( echo "((10 * ${LENGTH}) / ${STEP_SIZE})" | bc -l )
echo $TIME_STEPS
sed -i "s/<time_steps>1000<\/time_steps>/<time_steps>${TIME_STEPS}<\/time_steps>/" $FEB_FILE
# adjust the load curve according to the period
if [ $BOOL_PERIOD -eq 1 ]; then
    return
fi
