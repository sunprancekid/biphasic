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
PARM_HEADER="subdir,subid,n,period,time_step,cycles"
## FLAG PROTOCOL
# boolean determining if the script should be execute verbosely
declare -i BOOL_VERBOSE=0
## MANDATORY FLAG PARAMETERS
# boolean determining if the path to create directory hirearchy has been specified
declare -i BOOL_SIM_PATH=0
# boolean determining if the '.feb' model file to use
declare -i BOOL_FEB_FILE=0
## OPTIONAL FLAG PARAMETERS
# job name
JOB="time_sensitivity"
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
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use, presumed to be stored in 'models/'."
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
    # check that the model file was specified and exists
    if [ $BOOL_FEB_FILE -eq 0 ]; then
        # feb file must be specified
        echo -e "\nERROR :: ${FILENAME} :: must specify '.feb' file.\n"
        help $NONZEROEXITCODE
    elif [ ! -f models/${FEB_FILE} ]; then
        # the feb file does not exist
        echo -e "\nERROR :: ${FILENAME} :: the file 'models/${FEB_FILE}' cannot be found.\n"
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

## TODO :: add to math module
# divide two numbers, return the results
div () {

    ## PARAMETERS
    # none


    ## ARGUMENTS
    # first argument: numerator
    local num=$1
    # second argument: denomenator
    local denom=$2


    ## SCRIPT
    # divide two numbers, return the result
    echo "${num}/${denom}" | bc -l

}

## TODO :: add to math module
# multiply two numbers by each other, return the result
mul () {

    ## PARAMETERS
    # none


    ## ARGUMENTS
    # first argument: first number
    local num1=$1
    # second argument: second number
    local num2=$2


    ## SCRIPT
    # multiply the two numbers by each other
    echo "${num1}*${num2}" | bc -l
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

# start parameter file
PARM_FILE="${SIM_PATH}/${JOB}/${JOB}.csv"
echo $PARM_HEADER > ${PARM_FILE}
# copy the initial model file to the main directory
cp models/$FEB_FILE ${SIM_PATH}/${JOB}/
# loop through each step size
for n in ${N_LIST[@]}; do

    # generate path
    SIMID="n${n}"
    SUBDIR="${SIM_PATH}/${JOB}/n${n}"
    if [ ! -d $SUBDIR ]; then
        # if the path does not exist, make it
        mkdir -p $SUBDIR
    fi

    cp models/$FEB_FILE $SUBDIR/${SIMID}.feb
    # determine simulation parameters based on input
    # set the max step size according to period and number of steps
    TIMESTEP=$(div $PERIOD $n)
    # set the simulation length according to period and number of cycles
    LENGTH=$(mul $PERIOD $N_CYCLES)
    # copy the feb file to the sub directory
    ./programs/bash/augment_feb.sh -f ${SUBDIR}/${SIMID}.feb -m $TIMESTEP -l $LENGTH -c $PERIOD
    # generate simulation files
    # save parameters to csv

    echo "${SIMID}/,${SIMID},${n},${PERIOD},${TIMESTEP},${N_CYCLES}" >> ${PARM_FILE}


done

# submit simulation to slurm
# add analysis options
