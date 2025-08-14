#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.14
## submits jobs in batch
## user can specify running jobs locally, or submitting jobs to a cluster

## PARAMETERS
# nonzero exit code
declare -i NONZEROEXITCODE=120
# file name
FILENAME="submit_bash_jobs"
# path to parse csv file
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# path to script for slurm submission
SUB_SLURM="./programs/bash/util/submit_febio_slurm.sh"

## OPTION PARAMETERS
# boolean that determines if the job directory path has been specified
declare -i BOOL_PATH=0
# boolean that determines if the job name has been specified
declare -i BOOL_JOB=0

## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first agrument: exit code
    local exitcode=$1

    ## SCRIPT
    # report options to user
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: submit jobs in batch to a user specified cluster.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
#     echo -e " -o\t\t| overwrite files and restart all simulations, even if they have already run."
#     echo -e " -l\t\t| run job locally ('febio4' must be installed)."
#     echo -e " -s\t\t| submit job via slurm (via 'sbatch' - see util/submit_febio_slurm.sh)."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MANDATORY: path to job directory, contains '.feb' file."
    echo -e " -j  << ARG >>\t| MANDATORY: job name, corresponds to a '.csv' file name in \$DIR, which contains job parameters."
#     echo -e " -f  << ARG >>\t| OPTIONAL: specify a check file: if the file exists within the simulation subdirectory, the script will skip submitting / runnning this simulation."
    # exit
    exit $exitcode

}

# display formatted error message
display_error () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: error message
    ERR_MSG=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${ERR_MSG}.\n"

}

# check that the right parameters have been specified by the user
check () {

    ## PARAMTERS
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
            display_error "the parameter file '$PARM_FILE' cannot be found."
            help $NONZEROEXITCODE
        fi
    fi
    # the job name has been specified and the parameter file exists
}

## OPTIONS
# parse options
while getopts "hd:j:" opt
do
    case $opt in
        h) # display help options and exit zero
            help 0 ;;
        d) # path to job directory
            declare -i BOOL_PATH=1
            JOB_PATH=${OPTARG} ;;
        j) # specify job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        ?) # unknown option
            help $NONZEROEXITCODE
    esac # case backwards ...
done # not do backwards ...


## ARGUMENTS
# none


## TODO
# specify absolute path to bash scripts via enivronment variable or .. (how do expert bash developers do this)

## SCRIPT
# check options specified by user
check

# open csv parameter file, parse options from each row
# get the number of lines
declare -i N_LINES=$($PARSE_CSV -f $PARM_FILE -l)

# loop through each line, line 1 is the header ..
for n in $(seq 2 $N_LINES)
do
    ## get simulation paths
    # the first column is the SUBDIR
    SUBDIR=$($PARSE_CSV -f $PARM_FILE -l $n -c 1)
    # the second column is the SIMID
    SIMID=$($PARSE_CSV -f $PARM_FILE -l $n -c 2)

    echo $SUBDIR $SIMID

    ## run job ..
    # if local, run on current machine with 'febio4'
    # if slurm, generate submission script and run sbatch
done
