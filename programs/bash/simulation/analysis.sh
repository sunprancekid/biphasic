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
# file name that contains information about simulation CPI performance
CPU_OUT="febio.cpu.csv"

## PARAMATERS
# exit code indicating error
declare -i NONZEROEXITCODE=120
# file name
FILENAME="analysis.sh"
# text explaining the purpose of the script
PURPOSE="extract and compile results from febio simulations"
# boolean for hysteresis analysis
declare -i BOOL_HYS=0
# boolean for extracting job performance on CPU
declare -i BOOL_CPU=0
# boolean for performing relaxation analysis
declare -i BOOL_RELAX=0

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
    echo -e " -H\t\t| perform HYSTERSIS analysis."
    echo -e " -C\t\t| parse the simulation performance on the CPU."
    echo -e " -R\t\t| perform RELAXATION analysis."
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
    JOB_PATH=${JOB_PATH}${JOB}/
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
        PARM_FILE="${JOB_PATH}${JOB}.parm.csv"
        if [ ! -f $PARM_FILE ]
        then
            # the parameter file does not exist
            display_error "the parameter file '$PARM_FILE' cannot be found."
            help $NONZEROEXITCODE
        fi
    fi
    # the job name has been specified and the parameter file exists
}

## OPTIONS
# parse options, if any
while getopts "hHCRd:j:" opt; do
    case $opt in
        h) # display help, exit zero
            help 0 ;;
        H) # perform hystersis analysis
            declare -i BOOL_HYS=1 ;;
        C) # parse simulation performance
            declare -i BOOL_CPU=1 ;;
        R) # perform relaxation analysis
            declare -i BOOL_RELAX=1 ;;
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
SUM_FILE="${JOB_PATH}${JOB}/${JOB}.sum.csv"

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
    if [ "${COL_HEADER}" = "OT" ]; then
        declare -i PERIOD_COL=$c
        declare -i HAS_PERIOD_COL=1
    fi
done

# if hystersis analysis should be performed
if [[ $BOOL_HYS -eq 1 ]]; then
    # check if the simulation parameter includes the period
    if [ $HAS_PERIOD_COL -eq 0 ]; then
        # if it does not, abort
        display_error "unable to parse 'period' column from ${PARM_FILE}, cannot perform hystersis analysis"
    fi
fi


# loop through each line, line 1 is the header ..
for n in $(seq 2 $N_LINES)
do
    ## get simulation pathsfebio4
    # the first column is the SUBDIR
    SUBDIR=$($PARSE_CSV -f $PARM_FILE -l $n -c 3)
    # the second column is the SIMID
    SIMID=$($PARSE_CSV -f $PARM_FILE -l $n -c 2)

    ## extract results
    # parse results from febio.out which automatically includes CPU
    $EXTRACT $JOB_PATH$SUBDIR $FEBIO_OUT
    # perform hystersis analysis if requested
    if [[ $BOOL_HYS -eq 1 ]]; then
        # pass the path to the analysis file and simulation period
        # to the hystersis analysis program
        $HYSTERESIS $JOB_PATH$SUBDIR $($PARSE_CSV -f $PARM_FILE -l $n -c $PERIOD_COL )
    fi


    ## for the first iteration, parse the headers while performing the analysis
    CPU_FILE=$JOB_PATH$SUBDIR$CPU_OUT # path to default CPU file
    HYS_FILE=$JOB_PATH$SUBDIR$HYS_OUT # path to default HYS file
    if [[ $HAS_SUM_HEADER -eq 0 ]]; then
        # parse the header from the summary file
        SUM_HEADER="$($PARSE_CSV -f $PARM_FILE -l 1 )"

        # parse the CPU header if requested
        if [[ $BOOL_CPU -eq 1 ]]; then
            CPU_HEADER="$($PARSE_CSV -f $CPU_FILE -l 1 )"
            SUM_HEADER="${SUM_HEADER},${CPU_HEADER}"
        fi

        # parse the HYS header if requested
        if [[ $BOOL_HYS -eq 1 ]]; then
            HYS_HEADER="$($PARSE_CSV -f $HYS_FILE -l 1 )"
            SUM_HEADER="${SUM_HEADER},${HYS_HEADER}"
        fi

        # write the header to the summary file
        echo "${SUM_HEADER}" > $SUM_FILE
        # the header has been parsed
        declare -i HAS_SUM_HEADER=1
    fi


    ## perform analysis as requested
    # get the simulation parameters
    SIM_PARM="$($PARSE_CSV -f $PARM_FILE -l $n )"
    SIM_DAT="${SIM_PARM}"
    # get the cpu information if requested
    if [[ $BOOL_CPU -eq 1 ]]; then
        CPU_DAT="$($PARSE_CSV -f $CPU_FILE -l 2 )"
        SIM_DAT="${SIM_DAT},${CPU_DAT}"
    fi
    # get the hystersis information if requested
    if [[ $BOOL_HYS -eq 1 ]]; then
        HYS_DAT="$($PARSE_CSV -f $HYS_FILE -l 2 )"
        SIM_DAT="${SIM_DAT},${HYS_DAT}"
    fi
    echo "${SIM_DAT}" >> $SUM_FILE

done
