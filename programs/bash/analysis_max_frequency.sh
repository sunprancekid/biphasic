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
# header for parameter file
PARM_HEADER="path,simid,period,step_size,n_cycles"

## FLAG PROTOCOL
# boolean that determines if the script should be executed verbosely
declare -i BOOL_VERBOSE=0

## MANDATORY FLAG OPTIONS
# boolean determining if the script should be execute verbosely
declare -i BOOL_VERBOSE=0
## MANDATORY FLAG PARAMETERS
# boolean determining if the path to create directory hirearchy has been specified
declare -i BOOL_SIM_PATH=0
# boolean determining if the '.feb' model file to use
declare -i BOOL_FEB_FILE=0

## OPTIONAL FLAG OPTIONS
# job name
JOB="max_frequency"
# minimum frequency
MIN_PERIOD_VAL="2."
# maximum frequency
MAX_PERIOD_VAL="200."
# number of cycle periods to test
declare -i N_PERIOD_VAL=21
# number of points to sample per loop
declare -i N_CYCLE_STEPS=20
# number of times to cycle
declare -i N_CYCLES=5
# default permeability
PERM="0.001"


## FUNCTIONS
# displace options, exit
help () {

    ## SCRIPT


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
    echo -e " -v\t\t| execute script verbosely."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify the '.feb' file to use, presumed to be stored in 'models/'."
    echo -e " -p  << ARG >>\t| MANDATORY: specify the path to generate directory hirearchy 'time_sensitivity'."
    echo -e " -j  << ARG >>\t| OPTIONAL:  rename the job (default is ${JOB})."
    echo -e " -k  << ARG >>\t| OPTIONAL:  specify the material permeability (default is ${PERM})."
    echo -e " -A  << ARG >>\t| OPTIONAL:  specify the minimum cycle period to test (default is ${MIN_PERIOD_VAL})."
    echo -e " -B  << ARG >>\t| OPTIONAL:  specify the maximum cycle period to test (default is ${MAX_PERIOD_VAL})."
    echo -e " -N  << ARG >>\t| OPTIONAL:  specify the number of unique cycle periods to test on logscale (default is ${N_PERIOD_VAL})."
    echo -e " -t  << ARG >>\t| OPTIONAL:  specify the number of numerical steps to take each cycle, inversely related to the maximum step size of the simulation (default is ${N_CYCLE_STEPS})."
    echo -e " -n  << ARG >>\t| OPTIONAL:  specify the number of simulation cycles (default is ${N_CYCLES})."
    echo -e "\n"

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


# log10 function, echos log10 of first argument passed to method
log10 (){

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # number to perform log10 operation on
    local NUM_LOG=$1

    ## SCRIPT
    # perform log10 operation on number
    echo "l(${NUM_LOG})/l(10)" | bc -l
}

# pow10 function, echos 10 to the power of the first argument passed to method
pow10 () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # number to perform pow10 operation on
    local NUM_POW=$1

    ## SCRIPT
    # perform pow10 operation
    VAL=$( echo "l(10)" | bc -l )
    VAL=$( echo "(${VAL})*(${NUM_POW})" | bc -l )
    echo "e(${VAL})" | bc -l
}

# used to generate parameters along a logscale
logscale () {

     ## PARAMETERS
     # minimum number on a log10 scale
     MIN_VAL_LOG10=$( log10 ${MIN_PERIOD_VAL} )
     # maximum number on a log10 scale
     MAX_VAL_LOG10=$( log10 ${MAX_PERIOD_VAL} )

     ## ARGUMENTS
     # integer, ranging from 0 to N_PERIOD_VAL
     declare -i NUM=$1

     ## SCRIPT
     # generate the parameter along scale
     scale=$( echo "(( $NUM ) / ( ${N_PERIOD_VAL} ))" | bc -l )
     scale=$( echo "(${scale} * (${MAX_VAL_LOG10} - ${MIN_VAL_LOG10}) + ${MIN_VAL_LOG10})" | bc -l )
     scale=$( pow10 "$scale" )
     echo $(printf "%8.5f\n" "${scale}")
}

# used to generate parameters along a log scale
linscale() {
    ## PARAMETERS
    # minimum number on a linear scale
    MIN_VAL_LIN="-${MIN_PERIOD_VAL}"
    # maximum value along a linear scale
    MAX_VAL_LIN=${MAX_PERIOD_VAL}

    ## ARGUMENTS
    # integer ranging from 1 to N_PERIOD_VAL
    declare -i NUM=$1

    ## SCRIPT
    # generate the parameter along the linear scale
    scale=$( echo "(($NUM - 1 ) / ( ${N_PERIOD_VAL} ))" | bc -l )
    scale=$( echo "(${scale} * (${MAX_VAL_LIN} - ${MIN_VAL_LIN}) + ${MIN_VAL_LIN})" | bc -l )
    echo $(printf "%8.5f\n" "${scale}")
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
while getopts "hvf:p:A:B:N:t:n:k:" opt; do
    case $opt in
        h) # get help, exit zero
            help 0 ;;
        v) # execute script verbosely
            declare -i BOOL_VERBOSE=1 ;;
        f) # feb file
            declare -i BOOL_FEB_FILE=1
            FEB_FILE=${OPTARG} ;;
        p) # directory path
            declare -i BOOL_SIM_PATH=1
            SIM_PATH=${OPTARG} ;;
        A) # minimum period val to test
            MIN_PERIOD_VAL=${OPTARG} ;;
        B) # maximum period val to test
            MAX_PERIOD_VAL=${OPTARG} ;;
        N) # number of unique cycle periods to test
            declare -i N_PERIOD_VAL=${OPTARG} ;;
        t) # number of numerical steps in time during one cycle
            declare -i N_CYCLE_STEPS=${OPTARG} ;;
        n) # number of cycles
            declare -i N_CYCLES=$OPTARG ;;
        k) # update the material permiability
            PERM=${OPTARG}
        ?) # unknown option, get help and exit nonzero
            help $NONZEROEXITCODE
    esac
done


## ARGUMENTS
# none

## SCRIPT
# check parameters
check

# start parameter file
PARM_FILE="${SIM_PATH}/${JOB}/${JOB}.csv"
echo $PARM_HEADER > ${PARM_FILE}
# loop through each period val
for n in $(seq 0 $(($N_PERIOD_VAL))); do

    # generate path
    SUBDIR="${SIM_PATH}/${JOB}/k${n}"
    if [ ! -d $SUBDIR ]; then
        # if the path does not exist, make it
        mkdir -p $SUBDIR
    fi

    # copy the model file
    cp models/$FEB_FILE $SUBDIR/k${n}.feb

    # determine the frequency as a period
    PERIOD_VAL=$( logscale $n )
    # determine max numerical step size
    TIMESTEP=$(div $PERIOD_VAL $N_CYCLE_STEPS)
    # determine the simulation length
    LENGTH=$(mul $PERIOD_VAL $N_CYCLES )

    # augment the feb file
    ./programs/bash/augment_feb.sh -f ${SUBDIR}/k${n}.feb -m $TIMESTEP -l $LENGTH -c $PERIOD_VAL -k $PERM
    # copy the simulation parameters to the parameter file
    echo "k${n}/,k${n},${PERIOD_VAL},${TIMESTEP},${N_CYCLES}" >> $PARM_FILE

done
