#!/bin/bash
set -e


## Matthew A. Dorsey
## 2025.10.01
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## the goal of this script to is parameterize loading simulations

## MODELES
# script used for augmenting feb files
AUGMENT_FEB="python programs/python/febio/parse_feb.py"

## PARAMETERS
# nonzero exit code to run in error
declare -i NONZERO_EXITCODE=120
# name of script
FILENAME="analysis_loading"
# script purpose
PURPOSE="parameterize loading simulations"
# boolean for overwriting simulation directories
declare -i BOOL_OVERWRITE=0
# boolean for feb file
declare -i BOOL_FEBFILE=0
# boolean for simulation directory
declare -i BOOL_DIR=0
# booleaning for log vs. linear scale
declare -i BOOL_LOGSCALE=0

## ANALYSIS PARAMETERS
# header for parameter file
PARM_HEADER="path,id,n,depth,time,"
# job name
JOB="loading"
# minimum loading time to test
MIN_LOADTIME="0.01"
# maximum loading time to test
MAX_LOADTIME="100."
# number of loading times to test
declare -i N_LOAD_TIMES=30
# loading depth (mm)
LOADING_DEPTH="0.025"
# DEPRICATED - loading duration (seconds)
# LOADING_LENGTH="10."
# holding duration (seconds)
HOLDING_LENGTH="1000."
# steps during loading
N_LOAD_STEPS="100"
# steps during hold
N_HOLD_STEPS="1000"

## METHODS
# display script usage, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: exit code
    local exitcode=$1

    ## SCRIPT
    # display options
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # display
    echo -e " ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0."
    echo -e " -v\t\t| execute script verbosely."
    echo -e " -o\t\t| overwrite existing files if they exist."
#     echo -e " -l\t\t| generate holding times on a log scale."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -f  << ARG >>\t| MANDATORY: specify '.feb' file."
    echo -e " -p  << ARG >>\t| MANDATORY: specify path to simulation directory."
    echo -e " -j  << ARG >>\t| OPTIONAL: job name (default is ${JOB})."
    echo -e " -A  << ARG >>\t| OPTIONAL: maximum loading time in seconds (default is ${MIN_LOADTIME})."
    echo -e " -B  << ARG >>\t| OPTIONAL: minimum loading time is seconds (default is ${MAX_LOADTIME})."
    echo -e " -N  << ARG >>\t| OPTIONAL: number of loading times to test (default is ${N_LOAD_TIMES})."
    echo -e " -D  << ARG >>\t| OPTIONAL: loading depth in mm (constant, default is ${LOADING_DEPTH})."
    echo -e " -H  << ARG >>\t| OPTOINAL: holding time in sec (constant, default is ${HOLDING_LENGTH})."
    echo -e " -Y  << ARG >>\t| OPTIONAL: number of numerical steps during loading sequence (constant, default is ${N_LOAD_STEPS})."
    echo -e " -Z  << ARG >>\t| OPTIONAL: number of numerical steps during holding sequence (constant, default is ${N_HOLD_STEPS})."
    echo -e "\n"
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

# check that the information passed to the script is correct
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the feb file was specified and exists
    if [[ $BOOL_FEBFILE -eq 0 ]]; then
        display_error "must specify '.feb' file (option -f)"
    elif [[ ! -f $FEBFILE ]]; then
        display_error "path to '.feb' file ('$FEBFILE') does not exist"
    fi
    # feb file exists

    # check that the path to the simulation directory exists
    if [[ $BOOL_DIR -eq 0 ]]; then
        display_error "must specify directory (option -p)"
    elif [[ ! -d $DIR$JOB ]]; then
        mkdir -p $DIR$JOB
    fi
}

# generate simulation directories and parameters
generate () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # write the header to the parameter file
    local parm_file="$DIR$JOB/$JOB.csv"
    echo $PARM_HEADER > $parm_file

    # loop through each load time to test
    for n in $(seq 0 $(($N_LOAD_TIMES))); do
        # determine the load time from the min and max values
        if [[ $BOOL_LOGSCALE -eq 1 ]]; then
            # calulate on log scale
            local load_time=$( logscale $n )
        else
            # calculate on linear scale
            local load_time=$( linscale $n )
        fi

        # set simid, write to parameter file
        local id="n$n"
        echo "${id}/,${id},$n,$LOADING_DEPTH,$load_time" >> $parm_file

        # copy feb to directory
        mkdir -p $DIR$JOB/$id/
        local feb=$DIR$JOB/$id/$id.feb
        cp $FEBFILE $feb

        # adjust loading parameters
        # assign the depth of loading (stored in the step, rigid body boundary condition)
        $AUGMENT_FEB $feb "Step/step[@id='1']/Rigid/rigid_bc[@name='tip_loading']/value" "-${LOADING_DEPTH}"
        # adjust the loading rate (stored in the load controller)
        $AUGMENT_FEB $feb "LoadData/load_controller[@name='tip_displacement_controller']/math" "t/$load_time"
        # adjust the number of loading steps
        local load_step_size=$( echo "$load_time / $N_LOAD_STEPS"| bc -l )
        $AUGMENT_FEB $feb "Step/step[@id='1']/Control/time_steps" $( echo "10 * (${N_LOAD_STEPS})" | bc -l )
        $AUGMENT_FEB $feb "Step/step[@id='1']/Control/step_size" $( echo "$load_step_size / 10" | bc -l )
        $AUGMENT_FEB $feb "Step/step[@id='1']/Control/time_stepper/dtmin" $( echo "$load_step_size / 100" | bc -l )
        $AUGMENT_FEB $feb "Step/step[@id='1']/Control/time_stepper/dtmax" $load_step_size
        # adjust the holding time and number of steps
        local hold_step_size=$( echo "100 * $load_time / $N_HOLD_STEPS" | bc -l )
#         $AUGMENT_FEB $feb "LoadData/load_controller[@name='hold_maxstep_controller']/math" "$hold_step_size + (${hold_step_size} * 10 * t)"
#         $AUGMENT_FEB $feb "Step/step[@id='2']/Control/time_steps" $( echo "10 * (${N_HOLD_STEPS})" | bc -l )
#         $AUGMENT_FEB $feb "Step/step[@id='2']/Control/step_size" $( echo "$hold_step_size / 10" | bc -l )
#         $AUGMENT_FEB $feb "Step/step[@id='2']/Control/time_stepper/dtmin" $( echo "$hold_step_size / 100" | bc -l )
    done
}

# submit simulations to slurm
submit () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    display_error "TODO :: implement 'submit' method."

}

# parse simulation results, perform analysis
analyze () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none
    display_error "TODO :: implement 'analyze' method"

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
     MIN_VAL_LOG10=$( log10 ${MIN_LOADTIME} )
     # maximum number on a log10 scale
     MAX_VAL_LOG10=$( log10 ${MAX_LOADTIME} )

     ## ARGUMENTS
     # integer, ranging from 0 to N_PERIOD_VAL
     declare -i NUM=$1

     ## SCRIPT
     # generate the parameter along scale
     scale=$( echo "(( $NUM ) / ( ${N_LOAD_TIMES} ))" | bc -l )
     scale=$( echo "(${scale} * (${MAX_VAL_LOG10} - ${MIN_VAL_LOG10}) + ${MIN_VAL_LOG10})" | bc -l )
     scale=$( pow10 "$scale" )
     echo $(printf "%8.5f\n" "${scale}")
}

# used to generate parameters along a log scale
linscale() {
    ## PARAMETERS
    # minimum number on a linear scale
    MIN_VAL_LIN="${MIN_LOADTIME}"
    # maximum value along a linear scale
    MAX_VAL_LIN="${MAX_LOADTIME}"

    ## ARGUMENTS
    # integer ranging from 1 to N_PERIOD_VAL
    declare -i NUM=$1

    ## SCRIPT
    # generate the parameter along the linear scale
    scale=$( echo "(($NUM ) / ( ${N_LOAD_TIMES} ))" | bc -l )
    scale=$( echo "(${scale} * (${MAX_VAL_LIN} - ${MIN_VAL_LIN}) + ${MIN_VAL_LIN})" | bc -l )
    echo $(printf "%8.5f\n" "${scale}")
}


## OPTIONS
# parse options
while getopts "holf:p:j:A:B:N:D:H:Y:Z:" opt; do
    case $opt in
        h) # display options, exit zero
            help 0 ;;
        o) # overwrite
            BOOL_OVERWRITE=1 ;;
        l) # generate loading times on a log scale
            declare -i BOOL_LOGSCALE=1 ;;
        f) # feb file
            declare -i BOOL_FEBFILE=1
            FEBFILE=${OPTARG} ;;
        p) # path to simulation directory
            declare -i BOOL_DIR=1
            DIR=${OPTARG} ;;
        j) # update job name
            JOB=${OPTARG} ;;
        A) # minimum loading time to test
            MIN_LOADTIME=${OPTARG} ;;
        B) # maximum loading time to test
            MAX_LOADTIME=${OPTARG} ;;
        N) # number of unique loading times to test
            declare -i N_LOAD_TIMES=${OPTARG} ;;
        D) # loading depth
            LOADING_DEPTH=${OPTARG} ;;
        H) # holding length
            HOLDING_LENGTH=${OPTARG} ;;
        Y) # number of time steps during loading sequence
            N_HOLD_STEPS=${OPTARG} ;;
        Z) # number of time steps during holding sequence
            N_LOAD_STEPS=${OPTARG} ;;
        ?) # declare
            help $NONZERO_EXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# check options
check

# generate simulations
generate

# run simulations
# submit

# parse simulation results
# analyze
