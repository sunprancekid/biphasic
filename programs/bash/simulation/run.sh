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
# generate feb files
GENERATE="./programs/bash/simulation/generate.sh"

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
# boolean determining if the xplt file should be removed
declare -i BOOL_XPLT=0
# boolean determing if the feb file should be removed
declare -i BOOL_DEL_FEB=0
# determines if a feb file has been specified
declare -i BOOL_FEB=0
# determines if an optimization file has been specified
declare -i BOOL_OPT=0

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
    echo -e " -x\t\t| delete '.xplt' file after simulation completes."
    echo -e " -y\t\t| delete '.feb' file after simulation completes."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MANDATORY: path to job directory."
    echo -e " -j  << ARG >>\t| MANDATORY: job name."
    # echo -e " -t  << ARG >>\t| OPTIONAL:  transfer job files to another location before execution."
    echo -e " -c  << ARG >>\t| OPTIONAL: specify a check file: if the file exists within the simulation subdirectory, the script will skip submitting / runnning this simulation."
    echo -e " -f  << ARG >>\t| OPTIONAL: specify a FEB file, generate feb file before execution."
    echo -e " -n  << ARG >>\t| OPTIONAL: submit single job corresponding to integer in parameter file."
    echo -e " -o  << ARG >>\t| OPTIONAL: submit febio job with optimization file."
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
    JOB_PATH=${DIR}${JOB}/ # update job name
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

    # if a feb file has been specified, check that it exists
    if [ $BOOL_FEB -eq 1 ]; then
        # check that feb file exists
        if [[ ! -f $FEB_FILE ]]; then
            display_error "unable to find FEB FILE '${FEB_FILE}' (option -f)"
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
        display_verbose "simulation directory '$simdirstack' does not exist. cannot submit simulation '$simid'"
        return
    fi
    # check that the directory contains a feb file
    local feb_list=( ${simdirstack}*.feb )
    declare -i n_feb=$( find ${simdirstack} -name "*.feb" | wc -l )
    if [[ $n_feb -eq 0 ]]; then
        display_verbose "no '.feb' file exist in simulation directory '$simdirstack'. unable to submit '$simid'"
        return
    elif [[ $n_feb -gt 1 ]]; then
        display_verbose "multiple '.feb' files exist in simulation directory '$simdirstack'. unable to submit '$simid'"
        return
    else
        local feb_file=${feb_list[0]}
    fi

    # check if the directory contains an optimization file
    declare -i HAS_OPT=0
    local regex="*.opt"
    # local opt_list=( ${simdirstack}${regex} )
    declare -i n_opt=$( find ${simdirstack} -name ${regex} | wc -l )
    if [[ $n_opt -eq 0 ]]; then
        # the liist length is zero
        # no optimization files exist in the simulation directory
        # check if a global optimization file was specified
        if [[ $BOOL_OPT -eq 1 ]]; then
            # submit the simulation with the global optimization file
            declare -i HAS_OPT=1
            local local_opt=${OPT_FILE} # local opt is global opt
        fi
        # run without optimization
    elif [[ $n_opt -gt 1 ]]; then
        # the list length is greater than one
        # multiple optimization files were detected
        # throw error
        display_verbose "multiple optimization files detected locally in simulation directory '${simdirstack}'. unable to submit simulation '${simid}'."
        return
    else
        # the list length is one
        # one optimization file was detected
        # check that a global optimization was not specified
        if [[ $BOOL_OPT -eq 1 ]]; then
            # the global optimization file was specified but one was detected locally
            # throw an error
            display_verbose "optimization file detected locally in simulation directory '${simdirstack}', but global optimization file was specified '${OPT_FILE}'. unable to submit simulation '${simid}'."
            return
        fi
        # submit the simulation with the local optimization file
        declare -i HAS_OPT=1
        local local_opt=$(find ${simdirstack} -name ${regex})
    fi

    # if there is a check file call, check for the file
    if [[ $BOOL_CHECKFILE -eq 1 ]]; then
        # check for regex
        # if specific check file doesn't eist, check for regex
        declare -i n_check=$( find ${simdirstack} -name $CHECKFILE | wc -l )
        if [[ $n_check -gt 0 ]]; then
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
        SLURM_FLAGS=""
        if [[ $BOOL_XPLT -eq 1 ]]; then
            SLURM_FLAGS="-x "
        fi
        if [[ $BOOL_DEL_FEB -eq 1 ]]; then
            SLURM_FLAGS="${SLURM_FLAGS}-y "
        fi
        if [[ $HAS_OPT -eq 1 ]]; then
            SLURM_FLAGS="${SLURM_FLAGS}-o ${local_opt} "
        fi
        # submit the script from the local directory
        declare -i slurmid="$($SUB_SLURM -d ${simdirstack} -f ${feb_file} -j ${JOB}-${simint} -r $SLURM_FLAGS )"
        # echo "$SUB_SLURM -d ${simdirstack} -f ${simdirstack}${simid}.feb -j ${JOB}-${simint} -r $SLURM_FLAGS"
        echo "${JOB}${simint} (slurm id: ${simid}): $slurmid"
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

    if [[ $BOOL_FEB -eq 1 ]]; then
        # generate the feb file, if requested
        $GENERATE -d $DIR -j $JOB -f $FEB_FILE -n $simint
    fi
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
        if [[ $BOOL_FEB -eq 1 ]]; then
            # generate the feb file, if requested
            $GENERATE -d $DIR -j $JOB -f $FEB_FILE -n $((l-1))
        fi
        # pass line to submit
        submit $l
    done
}

## OPTIONS
# parse options
while getopts "hvlsd:j:c:f:n:xyo:" opt
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
            DIR=${OPTARG} ;;
        j) # specify job name
            declare -i BOOL_JOB=1
            JOB=${OPTARG} ;;
        c) # check file
            declare -i BOOL_CHECKFILE=1
            CHECKFILE=${OPTARG} ;;
        f) # feb file
            declare -i BOOL_FEB=1
            FEB_FILE=${OPTARG} ;;
        n) # specify single job
            declare -i BOOL_SIMINT=1
            declare -i SIMINT=${OPTARG} ;;
        x) # boolean for xplt file removal
            declare -i BOOL_XPLT=1 ;;
        y) # delete feb file post simulation
            declare -i BOOL_DEL_FEB=1 ;;
        o) # include optimization file
            declare -i BOOL_OPT=1
            OPT_FILE=${OPTARG} ;;
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
