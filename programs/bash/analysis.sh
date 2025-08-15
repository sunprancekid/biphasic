#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.15
## extract and compile results from febio simulations

## MODULES
# scripts to load from program repository
# path to parse csv file
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# extract results from custom outfile
EXTRACT="python ./programs/python/extract.py"
# hysteresis analysis
HYSTERESIS="python ./programs/python/hysteresis.py"
# outfile
FEBIO_OUT="febio4.job.out"
# file that contains information for hysteresis in each simulation directory
HYS_OUT="hys.out.csv"

## PARAMATERS
# exit code indicating error
declare -i NONZEROEXITCODE=120
# file name
FILENAME="analysis.sh"
# text explaining the purpose of the script
PURPOSE="extract and compile results from febio simulations"

## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: exit code
    local exitcode=$1

    ## SCRIPT
    # display options
    echo -e "\nFILE: ${FILENAME}\nPURPOSE: ${PURPOSE}\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MANDATORY: path to job directory, contains '.csv' file with job parameters."
    echo -e " -j  << ARG >>\t| MANDATORY: job name, corresponds to a '.csv' file name in \$DIR, which contains job parameters."
    echo -e ""
    # exit
    exit $exitcode

}

# display formatted error message
display_error () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: error message to display
    local err_msg=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${err_msg}.\n"

}

# check that the options specified are correct
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the job path exists
    if [ $BOOL_PATH -eq 0 ]
    then
        # if the job path has not been specified
        display_error "must specify path to simulation directory (option '-d')"
        help $NONZEROEXITCODE
    else
        # the job path has been specified, check that it exists
        if [ ! -d $JOB_PATH ]
        then
            # the path does not exists
            display_error "the path '${JOB_PATH}' does not exist or cannot be found"
        fi
    fi
    # otherwise, the path has been specified and does exist

    # check that the parameter file exists
    if [ $BOOL_JOB -eq 0 ]
    then
        # the job name has not been specified
        display_error "must specify job name (option '-j')"
        help $NONZEROEXITCODE
    else
        # the job name has been specified
        # check that the parameter file exists
        PARM_FILE="${JOB_PATH}${JOB}.csv"
        if [ ! -f $PARM_FILE ]
        then
            # the parameter file does not exist
            display_error "the parameter file '$PARM_FILE' cannot be foundfebio4."
            help $NONZEROEXITCODE
        fi
    fi
    # the job name has been specified and the parameter file exists
}

## OPTIONS
# parse options, if any
while getopts "hd:j:" opt; do
    case $opt in
        h) # display help, exit zero
            help 0 ;;
        d) # path to job directory
            declare -i BOOL_PATH=1
            JOB_PATH=${OPTARG} ;;
        j) # specify job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        ?) # default case for unknown option
            help $NONZEROEXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# initialize file names
# PARM_FILE="${JOB_PATH}${JOB}.csv"
SUM_FILE="${JOB_PATH}${JOB}.sum.csv"

# check options
check

# prase file parameter, perform analysis
# get the number of lines
declare -i N_LINES=$($PARSE_CSV -f $PARM_FILE -l)
# boolean that determines if the header for the summary file has been parsed
declare -i HAS_SUM_HEADER=0

# get the header, parse the results
declare -i HAS_PERIOD_COL=0 # boolean that determines if the column containing the period has been parsed from the header
declare -i PERIOD_COL=0 # integer that determines the column in the csv which contains the cycle period
for c in $(seq 1 $($PARSE_CSV -f $PARM_FILE -l 1 -c))
do
    COL_HEADER=$($PARSE_CSV -f $PARM_FILE -l 1 -c $c)
    if [ "${COL_HEADER}" = "period" ]; then
        declare -i PERIOD_COL=$c
        declare -i HAS_PERIOD_COL=1
    fi
done
# if the period column was not processed, abort
if [ $HAS_PERIOD_COL -eq 0 ]; then
    display_error "unable to parse 'period' column from ${PARM_FILE}, cannot perform hystersis analysis"
fi

# loop through each line, line 1 is the header ..
for n in $(seq 2 $N_LINES)
do
    ## get simulation pathsfebio4
    # the first column is the SUBDIR
    SUBDIR=$($PARSE_CSV -f $PARM_FILE -l $n -c 1)
    # the second column is the SIMID
    SIMID=$($PARSE_CSV -f $PARM_FILE -l $n -c 2)

    ## extract results
    $EXTRACT $JOB_PATH$SUBDIR $FEBIO_OUT

    ## perform analysis as requested
    # for now, just determine hystersis
    # determine the column which contains the period
    $HYSTERESIS $JOB_PATH$SUBDIR $($PARSE_CSV -f $PARM_FILE -l $n -c $PERIOD_COL )

    ## get the information from the save file, append to the parameter file
    # get the header for the summary file, if not already
    if [ $HAS_SUM_HEADER -eq 0 ]; then
        PARM_HEADER=$($PARSE_CSV -f $PARM_FILE -l 1)
        HYS_HEADER=$($PARSE_CSV -f $JOB_PATH$SUBDIR$HYS_OUT -l 1)
        SUM_HEADER="${PARM_HEADER},${HYS_HEADER}"
        echo "$SUM_HEADER" > $SUM_FILE
        declare -i HAS_SUM_HEADER=1
    fi
    # write the hysterseis information to the summary file
    echo "$($PARSE_CSV -f $PARM_FILE -l $n),$($PARSE_CSV -f $JOB_PATH$SUBDIR$HYS_OUT -l 2)" >> $SUM_FILE

done
