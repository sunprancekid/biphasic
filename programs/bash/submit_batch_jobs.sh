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

## MANDATORY OPTION PARAMETERS
# none

## OPTIONAL OPTION PARAMETERS
# none

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
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MADATORY: path to job directory, contains '.feb' file."
    echo -e " -j  << ARG >>\t| MADATORY: job name, corresponds to a '.csv' file name in \$DIR, which contains job parameters."
    # exit
    exit $exitcode

}

# check that the right parameters have been specified by the user
check () {

    ## PARAMTERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check options
    echo "TODO :: check options .."

}

#     echo -e " -f  << ARG >>\t| OPTIONAL: '.feb' file name, when it does not correspond to \$JOB."

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


## SCRIPT
# check options specified by user
check

# open csv parameter file, parse options from each row
