#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institute for Colloids and Interfaces
## 2026.01.28

## MODULES
# used to parse and write information to csv files
PARSE_CSV="./programs/bash/util/parse_csv.sh"

## PARAMETERS
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# filename
FILENAME="/bash/parameter/length-scale.sh"
# file purpose
PURPOSE="generate parameters that correspond to a simulation length scale"
# default header used for parameter files
PARM_HEADER="n,id,path"
# default header used for the config file
CONFIG_HEADER="key,xml,description,units,constant,related,symbolic"

## options
# boolean for directory
declare -i BOOL_DIR=0
# boolean for job name
declare -i BOOL_JOB=0
# boolean for feb model path
declare -i BOOL_FEB=0
# boolean for model name
declare -i BOOL_MODEL=0
# boolean for XML path
declare -i BOOL_XML=0
# default xml
DEFAULT_XML='na'
# boolean corresponding to parameter KEY
declare -i BOOL_KEY=0
# default key
DEFAULT_KEY='Z'
# boolean corresponding to parameter DESCRIPTION
declare -i BOOL_DESCRIPT=0
# default description
DEFAULT_DESCRIPT='length_scale'
# boolean corresponding to parameter UNITS
declare -i BOOL_UNITS=0
# default units
DEFAULT_UNITS='mm'


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
    echo -e "DESCRIPTION: to parametrically adjust the length scale of 'FEB' models, the model files are stored in a model directory which matches the hirearchy: \${FEB}/scale/\${MODEL}/\${SCALE}.feb. Here, \${FEB} and \${MODEL} correspond to the parameters -f and -m, respectively. \${SCALE} refers to the name of the feb model, which is the assigned length scale. The script parses the length scales from the model file names, and then uses that information to generate the corresponding parameters."
    # display script options
    echo -e "\n ## SCRIPT PROTOCOL ##"
    echo -e " -h\t\t| display HELP options, exit 0."
    # echo -e " -v\t\t| VERBOSE execution of script as export single line describing script actions to CLT."
    # echo -e " -V\t\t| VERY VERBOSE execution of script, export script execution to CLT at least step."
    echo -e "\n ## FEB PARAMETER OPTIONS ##"
    echo -e " -d << ARG >>\t| MANDATORY: path to DIRECTORY to which contains directory hirearchy."
    echo -e " -j << ARG >>\t| MANDATORY: named assgined to JOB, contains simulation directories."
    echo -e " -f << ARG >>\t| MANDATORY: path to FEB directory which contains scaled models."
    echo -e " -m << ARG >>\t| MADNATORY: name of scaled MODEL."
    echo -e " -k << ARG >>\t| OPTIONAL: shortcut KEY used to identify parameter (default is ${DEFAULT_KEY})."
    echo -e " -x << ARG >>\t| OPTIONAL: XML path specifiying parameter in '.feb' file (default is ${DEFAULT_XML})."
    echo -e " -u << ARG >>\t| OPTIONAL: UNITS corresponding to parameter, stored in config file (default is ${DEFAULT_UNITS})."
    echo -e " -D << ARG >>\t| OPTIONAL: single string DESCRIBING parameter, store in config file (default is ${DEFAULT_DESCRIPT})."
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

# check that the options arguments are correct
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the path to the directory exists
    if [[ $BOOL_DIR -eq 0 ]]; then
        display_error "must specify job DIRECTORY (option -d)"
    elif [[ ! -d $DIR ]]; then
        # if the path does not exist, thow an error
        display_error "unable to find path '$DIR'"
    fi

    # check if the job exist
    SUBDIR="$DIR/$JOB/"
    if [[ $BOOL_JOB -eq 0 ]]; then
        display_error "must specify JOB name (option -j)"
    elif [[ ! -d $SUBDIR ]]; then
        # if the directory does not exist, make it
        mkdir -p $SUBDIR
    fi

    # check the model directory and name
    if [[ $BOOL_FEB -eq 0 ]]; then
        display_error "must specify path to FEB models (option -f)"
    fi
    if [[ $BOOL_MODEL -eq 0 ]]; then
        display_error "must specify the MODEL name (option -m)"
    fi
    SCALE_DIR=${FEB}scale/${MODEL}/
    if [[ ! -d $SCALE_DIR ]]; then
        # if the directory does not exist, throw an error
        display_error "FEB directory which contains scaling MODELS '${SCALE_DIR}' does not exist. Directory hirearchy must match pattern '\${FEB}/scale/\${MODEL}/'."
    fi

    # check the key
    if [[ $BOOL_KEY -eq 0 ]]; then
        KEY=${DEFAULT_KEY}
    fi

    # check the xml path
    if [[ $BOOL_XML -eq 0 ]]; then
        XML=${DEFAULT_XML}
    fi

    # check the units
    if [[ $BOOL_UNITS -eq 0 ]]; then
        UNITS=$DEFAULT_UNITS
    fi

    # check the description
    if [[ $BOOL_DESCRIPT -eq 0 ]]; then
        DESCRIPT=$DEFAULT_DESCRIPT
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

    # check if the config file exists
    CONFIG_FILE="$SUBDIR$JOB.config.csv"
    if [[ ! -f $CONFIG_FILE ]]; then
        # if the file does not exist, write the header
        echo $CONFIG_HEADER > $CONFIG_FILE
    fi


}

# generate parameter based on the model parameters
gen_parm () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # determine the files that match the hirearchy
    MODELS=( ${SCALE_DIR}*.feb )

    # parse the scaling integers, create a list
    SCALE=( )
    for i in "${!MODELS[@]}"; do
        # get the integer from the file name
        file=$(basename  "${MODELS[i]}")
        scale="${file%.*}"
        # append to array
        SCALE=( "${SCALE[@]}" $scale)
    done
    # printf '%s\n' "${SCALE[@]}"

    # append key to parameter file header
    local head=$( $PARSE_CSV -f $PARM_FILE -l 1 )
    sed -i "s/$head/$head,$KEY/" $PARM_FILE

    ## loop through each integer, append to existing parameters
    local len="${#SCALE[@]}"
    local lines=$( $PARSE_CSV -f $PARM_FILE -l )
    # for constant values, add constant value to find row
    if [[ $len -eq 1 ]]; then
        if [[ $lines -eq 1 ]]; then
            # if there is only one line, no parameters have been written
            echo "0,${KEY}0,${KEY}0/,$CONSTANT_VALUE" >> $PARM_FILE
        else
            # otherwise, loop through all lines and append the constant value
            for n in $( seq 2 $lines ); do
                local l=$( $PARSE_CSV -f $PARM_FILE -l $n )
                sed -i "${n}c${l},${SCALE[0]}" $PARM_FILE
            done
        fi
    else
        # otherwise, multiple parameters will be written
        if [[ $lines -eq 1 ]]; then
            # if there is only one line in the parameter file
            # then only the header has been written and no paraemeters have been generated for the job
            for n in "${!SCALE[@]}"; do
                # append to file
                echo "${n},${KEY}${n},${KEY}${n}/,${SCALE[n]}" >> $PARM_FILE
            done
        else
            # multiple values have already been specified
            # loop through each line in parameter file, and replicate all values
            OLD_PARM_FILE="${PARM_FILE}~"
            cp $PARM_FILE $OLD_PARM_FILE # create copy of the parameter file
            echo $( $PARSE_CSV -f $OLD_PARM_FILE -l 1 ) > $PARM_FILE # copy the header, overwrite the original
            # loop through each new parameter
            declare -i count=1
            for n in $( seq 0 $(($len-1)) ); do
                # loop through each line of the old file
                for l in $( seq 2 $lines ); do
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
                    # append to the new file
                    echo "${count},${simid},${simdir},${parms}${SCALE[n]}" >> $PARM_FILE
                    # update the count
                    ((count++))
                done
            done
            # delete the old file
        fi
    fi

    # write to config file
    echo "$KEY,$XML,$DESCRIPT,$UNITS,0,1,1" >> $CONFIG_FILE

    return

}

## OPTIONS
# parse options
while getopts "hd:j:f:m:k:x:u:D:" opt; do
    case $opt in
        h) # display options exit zero
            help 0 ;;
        d) # specify directory
            declare -i BOOL_DIR=1
            DIR=${OPTARG} ;;
        j) # specify job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        f) # specify path to model directory
            declare -i BOOL_FEB=1
            FEB=${OPTARG} ;;
        m) # specify model name
            declare -i BOOL_MODEL=1
            MODEL=${OPTARG} ;;
        k) # specify key
            declare -i BOOL_KEY=1
            KEY=${OPTARG} ;;
        x) # specify xml path
            declare -i BOOL_XML=1
            XML=${OPTARG} ;;
        u) # specify units
            declare -i BOOL_UNITS=1
            UNITS=${OPTARG} ;;
        D) # specify description
            declare -i BOOL_DESCRIPT=1
            DESCRIPT=${OPTARG} ;;
        ?) # default, display options with nonzero exitcode
            help $NONZERO_EXITCODE
    esac
done

## ARGMENTS
# none

## SCRIPT
# check script arguments
check

# generate parameters
gen_parm
