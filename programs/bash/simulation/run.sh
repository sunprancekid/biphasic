#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.14
## submits jobs in batch
## user can specify running jobs locally, or submitting jobs to a cluster

## TODO
# parse job status from squeue and append to parameter csv
# rename jobs using simint
# merge multiple simulations into one script to reduce listing on squeue (so I look less like an asshole)

## PARAMETERS
# nonzero exit code
declare -i NONZEROEXITCODE=120
# file name
FILENAME="./programs/bash/simulation/run.sh"
# path to parse csv file
PARSE_CSV="./programs/bash/util/parse_csv.sh"
# path to script for slurm submission
SUB_SLURM="./programs/bash/simulation/submit_slurm.sh"

## HOSTNAME AND FEBIO EXECUTABLE INSTRUCTIONS
# host name of mpikg lbox
MPIKG_HOST="lbox181.mpikg.mpg.de"
# febio4 executable for mpikg
MPIKG_EXEC="/scratch/dorsey/FEBio-4.9/build-with-MKL/bin/febio4"
# normal febio4 executable
FEBIO4='febio4'
# host for slurm submissino
SLURM_HOST="hot2.mpikg.mpg.de"


## OPTION PARAMETERS
# boolean for verbose execution
declare -i BOOL_VERBOSE=0
# boolean that determines if the job directory path has been specified
declare -i BOOL_PATH=0
# boolean that determines if the job name has been specified
declare -i BOOL_JOB=0
# boolean that determines if the jobs should be run locally
declare -i BOOL_LOCAL=0
# boolean that determines if the jobs should be run via slurm
declare -i BOOL_SLURM=0
# boolean for running single job
declare -i BOOL_SIMINT=0
# boolean for specifying check file
declare -i BOOL_CHECKFILE=0

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
    echo -e " -v\t\t| verbose script execution."
#     echo -e " -o\t\t| overwrite files and restart all simulations, even if they have already run."
    echo -e " -l\t\t| run job locally ('febio4' must be installed)."
    echo -e " -s\t\t| submit job via slurm (via 'sbatch' - see ${SUB_SLURM})."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MANDATORY: path to job directory."
    echo -e " -j  << ARG >>\t| MANDATORY: job name."
    # echo -e " -t  << ARG >>\t| OPTIONAL:  transfer job files to another location before execution."
    echo -e " -c  << ARG >>\t| OPTIONAL: specify a check file: if the file exists within the simulation subdirectory, the script will skip submitting / runnning this simulation."
    echo -e " -n  << ARG >>\t| OPTIONAL: submit single job corresponding to integer in parameter file."
    echo -e ""
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
    help $NONZEROEXITCODE

}

# formatted verbose message
display_verbose () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: message to display
    VRB_MSG=$1

    ## SCRIPT
    # display message
    echo -e "${FILENAME} :: ${VRB_MSG}."

}

# check that the right parameters have been specified by the user
check () {

    ## PARAMTERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the job path exists
    JOB_PATH=${JOB_PATH}${JOB}/ # update job name
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
            display_error "the parameter file '$PARM_FILE' cannot be foundfebio4."
            help $NONZEROEXITCODE
        fi
    fi
    # the job name has been specified and the parameter file exists

    # if the local boolean has been specified
    if [ $BOOL_LOCAL -eq 1 ]
    then
        # check if the febio4 command exists
        if ! command -v $FEBIO4 >/dev/null 2>&1
        then
            # if it does not, then jobs cannot be run locally
            display_error "the command '${febio4}' could not be found, jobs cannot be run locally"
            help $NONZEROEXITCODE
        fi
    fi
}

# submit job
submit () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: line corresponding to job in parameter file
    local -i l=$1

    ## SCRIPT
    # get the directory and simid from the parameter file
    local simid=$($PARSE_CSV -f $PARM_FILE -l $l -c 2)
    local simdir=$($PARSE_CSV -f $PARM_FILE -l $l -c 3)
    local simint=$($PARSE_CSV -f $PARM_FILE -l $l -c 1)
    # check that the directory exists
    local simdirstack=$JOB_PATH$simdir
    if [[ ! -d $simdirstack ]]; then
        display_error "simulation directory '$simdirstack' does not exist. cannot submit simulation '$simid'"
    fi
    # check that the directory contains a feb file
    local feb_list=( ${simdirstack}*.feb )
    if [[ ${#feb_list[@]} -eq 0 ]]; then
        display_error "no '.feb' file exist in simulation directory '$simdirstack'. unable to submit simulation '$simid'"
    elif [[ ${#feb_list[@]} -gt 1 ]]; then
        display_error "multiple '.feb' files exist in simulation directory '$simdirstack'. unable to submit simulaiton '$simid'"
    else
        local feb_file=${feb_list[0]}
    fi

    # if there is a check file call, check for the file
    if [[ $BOOL_CHECKFILE -eq 1 ]]; then
        # check for regex
        # if specific check file doesn't eist, check for regex
        local check_list=( ${simdirstack}$checkfile )
        if [[ ${#check_list[@]} -gt 0 ]]; then
            # report if verbose
            if [[ $BOOL_VERBOSE -eq 1 ]]; then
                display_verbose "files found in '${simdirstack}' matching check file '${CHECKFILE}'. skipping .."
            fi
            return
        fi
    fi

    # run 
    if [[ $BOOL_LOCAL -eq 1 ]]; then
        # run locally
        if [[ "$HOSTNAME" == "$MPIKG_HOST" ]]; then
            # run using the local installation at mpikg
            $MPIKG_EXEC $feb_file
            return
        else
            # check that the febio4 command is installed
            if command -v $FEBIO4 >/dev/null 2>&1
            then
                $FEBIO4 $feb_file
                return
            else
                display_error "cannot run simulation '$simid' locally. $FEBIO4 command is not installed on ${HOSTNAME}"
            fi
        fi
    elif [[ $BOOL_SLURM -eq 1 ]]; then
        # submit to slurm
        # check the host is hot2
        if [[ ! "${HOSTNAME}" == "${SLURM_HOST}" ]]; then
            display_error "login into ${SLURM_HOST} before submitting to slurm."
        fi
        # submit the script from the local directory
        $SUB_SLURM -d ${simdirstack} -j ${simid} -i ${simint}
        return
    fi
    # 

}

# submit single job
submit_single () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: integer corresponding to the job in the parameter file
    local -i simint=$1

    ## SCRIPT
    # find the job in the parameter file
    declare -i lines=$($PARSE_CSV -f $PARM_FILE -l )
    for l in $(seq 2 $lines); do
        # find the line corresponding to the integer
        if [[ $simint -eq $($PARSE_CSV -f $PARM_FILE -l $l -c 1) ]]; then
            break
        fi
    done

    # submit the job according the specifications
    submit $l
}

# submit all jobs
submit_batch () {

    ## PARAMETERS 
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # loop through all lines in parameter file and submit
    for l in $(seq 2 $($PARSE_CSV -f $PARM_FILE -l )); do
        # pass line to submit
        submit $l
    done
}

## OPTIONS
# parse options
while getopts "hvlsd:j:c:n:" opt
do
    case $opt in
        h) # display help options and exit zero
            help 0 ;;
        v) # execute verbosly
            declare -i BOOL_VERBOSE=1 ;;
        l) # run febio locally
            declare -i BOOL_LOCAL=1 ;;
        s) # run the jobs via slurm
            declare -i BOOL_SLURM=1 ;;
        d) # path to job directory$SUB_SLURM
            declare -i BOOL_PATH=1
            JOB_PATH=${OPTARG} ;;
        j) # specify job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        c) # check file
            declare -i BOOL_CHECKFILE=1
            CHECKFILE=${OPTARG} ;;
        n) # specify single job
            declare -i BOOL_SIMINT=1
            declare -i SIMINT=${OPTARG} ;;
        ?) # unknown option
            help $NONZEROEXITCODE
    esac 
done 

## ARGUMENTS
# none


## TODO
# specify absolute path to bash scripts via enivronment variable or .. (how do expert bash developers do this)

## SCRIPT
# check options specified by user
check

# submit jobs
if [[ $BOOL_SIMINT -eq 0 ]]; then
    submit_batch
else # bool_simint is 1
    submit_single $SIMINT
fi
