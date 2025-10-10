#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2025.10.06

## FILE: bash/parameter/elasticity.sh
## PURPOSE: generate set of elasticity parameters according to linear or logscale, write to FEB file

## PROGRAMS
# used to parse and write information to csv files
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# used to generate range of values along either a logscale or a linear scale
LINLOGSCALE="./programs/bash/util/math/linlogscale.sh"

## PARAMETERS
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# filename
FILENAME="/bash/parameter/elasticity.sh"
# file purpose
PURPOSE="generate elasticity parameters and write to '.feb' file"
# default header used for parameter files
PARM_HEADER="n,id,path"

## options
# default directory path for storing parameters
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# default job name
JOB="biphasic_job"
# default xml path specifying elasticity in '.feb' file
XML_PATH="Material/material[@id='1']/solid[@type='isotropic elastic']/E"
# default key use to identify the elasticity parameter
KEY="E"
# boolean used to determine if a cosntant value has been specifed
declare -i BOOL_CONSTANT=0
# boolean determining if a minimum value has been specified
declare -i BOOL_MINVAL=0
# boolean for specifying maximum value
declare -i BOOL_MAXVAL=0
# boolean for generating values along a log scale
declare -i BOOL_LOGSCALE=0
# boolean for specifying the number of values that should be generated
declare -i BOOL_NVALS=0



## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # first option: exit code
    local exitcode=$1

    ## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # display script options
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0."
    echo -e " -L \t\t| generate parameters along LOG scale (default is LINEAR)."
    echo -e "\n ## SCRIPT MODIFIABLE PARAEMETERS ## \n"
    echo -e " -d << ARG >>\t| PATH to which contains directory hirearchy (default is ${DIR})."
    echo -e " -j << ARG >>\t| named assgined to JOB, contains simulation directories (default is ${JOB})."
    echo -e " -x << ARG >>\t| XML path specifiying elastic modulus in '.feb' file (default is '${XML_PATH}')."
    echo -e " -k << ARG >>\t| shortcut KEY used to identify elasticity parameter (default is ${KEY})."
    echo -e " -C << ARG >>\t| assign one CONSTANT value to property."
    echo -e " -A << ARG >>\t| MINIMUM value assigned to parameter."
    echo -e " -B << ARG >>\t| MAX value assigned to parameter."
    echo -e " -N << ARG >>\t| NUMBER of unique parameters to generate between A and B."
    echo -e ""

    # exit with exit code
    exit $exitcode

}

# display error message, exit with nonzero exitcode
display_error () {

    # PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # first argument: error message to display
    local err_msg=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${err_msg}.\n"
    help $NONZERO_EXITCODE

}

# check information passed to options before script execution
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the path to the directory exists
    if [[ ! -d $DIR ]]; then
        # if the path does not exist, thow an error
        display_error "unable to find path '$DIR'"
    fi

    # check if the job exist
    SUBDIR="$DIR/$JOB/"
    if [[ ! -d $SUBDIR ]]; then
        # if the directory does not exist, make it
        mkdir -p $SUBDIR
    fi

    # check if the parameter file already exists
    PARM_FILE="$SUBDIR$JOB.parm.csv"
    if [[ ! -f $PARM_FILE ]]; then
        # if the file does not exist, write a default header to the parameter file
        echo "$PARM_HEADER" > $PARM_FILE
    else
        # if the file does exist, check if the key has already been specified for another parameter
        local c=$( $PARSE_CSV -f $PARM_FILE -l 1 -c) # number of columns in file header
        for n in $( seq 1 $c ); do
            # check if KEY already exists in the header
            local head=$( $PARSE_CSV -f $PARM_FILE -l 1 -c $n )
            if [[ "$head" == "$KEY" ]]; then
                display_error "key '$KEY' already has been defined for job '$JOB' in '$DIR'"
            fi
        done
    fi

    # TODO :: add check for specify the scale to generate numbers along
    # e.g. negative numbers cannot be generated on a log scale

}

# generate parameters as specifed
gen () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # append key to parameter file header
    local head=$( $PARSE_CSV -f $PARM_FILE -l 1 )
    sed -i "s/$head/$head,$KEY/" $PARM_FILE
    # for constant values, add constant value to find row
    local lines=$( $PARSE_CSV -f $PARM_FILE -l )
    if [[ $BOOL_CONSTANT -eq 1 ]]; then
        if [[ $lines -eq 1 ]]; then
            # if there is only one line, no parameters have been written
            echo "0,${KEY}0,${KEY}0/,$CONSTANT_VALUE" >> $PARM_FILE
        else
            # otherwise, loop through all lines and append the constant value
            for n in $( seq 2 $lines ); do
                local l=$($PARSE_CSV -f $PARM_FILE -l $n )
                sed -i "${n}c${l},${CONSTANT_VALUE}" $PARM_FILE
            done
        fi
    else
        # otherwise, multiple parameters will be written
        if [[ $lines -eq 1 ]]; then
            # if there is only one line in the parameter file
            # then only the header has been written and no paraemeters have been generated for the job
            for n in $( seq 1 $( echo "$NVALS" | bc -l ) ); do
                # generate parameters, append to file
                if [[ $BOOL_LOGSCALE -eq 1 ]]; then
                    # generate along a log scale
                    VAL=$( $LINLOGSCALE -A $MINVAL -B $MAXVAL -N $NVALS -I $n -L )
                else
                    # generate along a lin scale
                    VAL=$( $LINLOGSCALE -A $MINVAL -B $MAXVAL -N $NVALS -I $n )
                fi
                # append to file
                echo "${n},${KEY}${n},${KEY}${n}/,$VAL" >> $PARM_FILE
            done
        else
            # multiple values have already been specified
            # loop through each line in parameter file, and replicate all values
            OLD_PARM_FILE="${PARM_FILE}~"
            cp $PARM_FILE $OLD_PARM_FILE # create copy of the parameter file
            echo $( $PARSE_CSV -f $OLD_PARM_FILE -l 1 ) > $PARM_FILE # copy the header, overwrite the original
            # loop through each new parameter
            declare -i count=1
            for n in $( seq 1 $( echo "NVALS" | bc -l )); do
                # loop through each line of the old file
                for l in $(seq 2 $lines ); do
                    # update the id
                    local simid="$( $PARSE_CSV -f $OLD_PARM_FILE -l $l -c 2 )${KEY}${n}"
                    # update the directory
                    local simdir="$( $PARSE_CSV -f $OLD_PARM_FILE -l $l -c 3)${KEY}${n}/"
                    # parse the parameters
                    local columns=$( $PARSE_CSV -f $OLD_PARM_FILE -l $l -c )
                    local parms=""
                    for c in $( seq 4 $columns ); do
                        parms="${parms}$( $PARSE_CSV -f $OLD_PARM_FILE -l $l -c $c ),"
                    done
                    # determine the new value
                    if [[ $BOOL_LOGSCALE -eq 1 ]]; then
                        # generate along a log scale
                        VAL=$( $LINLOGSCALE -A $MINVAL -B $MAXVAL -N $NVALS -I $n -L )
                    else
                        # generate along a lin scale
                        VAL=$( $LINLOGSCALE -A $MINVAL -B $MAXVAL -N $NVALS -I $n )
                    fi
                    # append to the new file
                    echo "${count},${simid},${simdir},${parms}${VAL}" >> $PARM_FILE
                    # update the count
                    ((count++))
                done
            done
            # delete the old file
        fi
    fi
}

## OPTIONS
# parse options
while getopts "hd:j:x:k:C:A:B:LN:" opt; do
    case $opt in
        h) # display options exit zero
            help 0 ;;
        d) # path to simulation directory
            DIR=${OPTATG} ;;
        j) # job name
            JOB=${OPTARG} ;;
        x) # xml path
            XML_PATH=${OPTARG} ;;
        k) # key used for parameter
            KEY=${OPTARG} ;;
        C) # specify constant value
            declare -i BOOL_CONSTANT=1
            CONSTANT_VALUE=${OPTARG} ;;
        A) # specify a minimum number to generate
            declare -i BOOL_MINVAL=1
            MINVAL=${OPTARG} ;;
        B) # specify a maxmimum number to generate
            declare -i BOOL_MAXVAL=1
            MAXVAL=${OPTARG} ;;
        L) # generate values along a logarithmic scale
            declare -i BOOL_LOGSCALE=1 ;;
        N) # specify the number of values to generate
            declare -i BOOL_NVALS=1
            declare -i NVALS=${OPTARG} ;;
        ?) # default, display options with nonzero exitcode
            help $NONZERO_EXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# check that the correct information was specified
check

# generate parameters
gen

