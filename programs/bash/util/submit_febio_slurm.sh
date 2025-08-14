#!/bin/bash
set -e

## Matthew A. Dorsey
## @sunprancekid
## MPIKG - matthew.dorsey@mpikg.mpg.de
## 2025.07.24

## script for submit FEBio jobs to MPIKG cluster via SLURM

## PARAMETERS // CONSTANTS
# non-zero exit code
declare -i NONZEROEXITCODE=120
# location of febio executable
# FEBIO_LOC="/scratch/dorsey/FEBio-4.9/build/bin/febio4"
# name of MPIKG linux cluster for login
CLUSTER="hot2"
## booleans for script parameters
# boolean for replicating jobs
declare -i BOOL_REPLICATE=0
# boolean determining if job directory has been specified
declare -i BOOL_DIR=0
# boolean determining if job name has been specified
declare -i BOOL_JOB=0
# boolean determining if optional argument feb file has been specified
declare -i BOOL_FEB=0


## FUNCTIONS
# output script options to cml terminal
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # exit code
    local exit_code=$1

    ## SCRIPT
    # report usage to user
    echo -e "\nFILE: \t submit_febio_slurm.sh\nPURPOSE: submit febio jobs to MPIKG compute cluster via slurm.\n"
    echo -e "\n ## SCRIPT PROTOCOL ## \n"
    echo -e " -h\t\t| display options, exit 0"
    echo -e " -r\t\t| replicate simulation, otherwise overwrite simulation data if job has already run."
    echo -e "\n ## SCRIPT PARAEMETERS ## \n"
    echo -e " -d  << ARG >>\t| MADATORY: path to job directory, contains '.feb' file."
    echo -e " -j  << ARG >>\t| MADATORY: job name, corresponds to '.feb' file name in \$DIR."
    echo -e " -f  << ARG >>\t| OPTIONAL: '.feb' file name, when it does not correspond to \$JOB."
    echo -e

    exit $exit_code
}

# check that mandatory arguments have been specified
check () {

    ## PARAMETERS
    # boolean determining that the script has passed all initial checks
    declare -i check=0

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check that the directory which has been specified exists
    if [[ $BOOL_DIR -eq 0 ]]; then
        # must specify the directory name
        # inform user and exit nonzero
        echo -e "\nERROR :: Must specify job directory.\n"
        help $NONZEROEXITCODE
    elif [[ ! -d $DIR ]]; then
        # if the directory does not exist
        # inform user and exit nonzero
        echo -e "\nERROR :: path to job directory '${DIR}' does not exist.\n"
        help $NONZEROEXITCODE
    fi
    # the directory has been specified and exists

    # check that feb file exists
    if [[ $BOOL_FEB -eq 1 ]]; then
        # a feb file has been specified by the user
        # check that it exists
        if [[ ! -f "${DIR}${FEB_FILE}" ]]; then
            # the feb file does not exist in the specified directory
            # inform the user and exit nonzero
            echo -e "\nERROR :: model file '${DIR}${FEB_FILE}' cannot be found.\n"
            help $NONZEROEXITCODE
        fi
        # otherwise, the FEB file specified by the user does exist.

        # the user should still provide a job name
        if [[ $BOOL_JOB -eq 0 ]]; then
            # a job name has not been specified
            # inform the user and exit nonzero
            echo -e "\nERROR :: must specify job name."
            help $NONZEROEXITCODE
        fi
    else
        FEB_FILE="${JOB}.feb"
        if [[ $BOOL_JOB -eq 0 ]]; then
            # the job name has not been specified
            # inform the user and exit
            echo -e "\nERROR :: must specify job name.\n"
            help $NONZEROEXITCODE

            ## TODO :: parse job name if not specified by user
        elif [[ ! -f "${DIR}${FEB_FILE}" ]]; then
            # a model file corresponding to the job does not exist in the job directory
            # inform user and exit nonzero
            echo -e "\nERROR :: model file '${DIR}${JOB}.feb' cannot be found.\n"
            help $NONZEROEXITCODE
        fi
    fi
    # the model file exists

}

# generate SLURM script
gen_slurm_script () {

    ## PARAMETERS
    # name of file contains slurm submission instructions
    local FILENAME="${SIMID}.slurm.sub"
    # directory that the file is stored in
    local FILEPATH="${SIMDIR}"

    ## ARGUMENTS
    # none

    ## SCRIPT
    # none

#     echo "BASH" > $FILEPATH$FILENAME
#     echo "" >> $FILEPATH$FILENAME
    echo "#!/bin/bash -l" > $FILEPATH$FILENAME
    echo "" >> $FILEPATH$FILENAME
    echo "#SBATCH --partition=cpu2" >> $FILEPATH$FILENAME
    echo "#SBATCH -J ${SIMID}.%j.slurm" >> $FILEPATH$FILENAME
    echo "#SBATCH --nodes=1" >> $FILEPATH$FILENAME  # number of nodes
    echo "#SBATCH --ntasks=1" >> $FILEPATH$FILENAME   # number of processor cores (i.e. tasks)
    echo "#SBATCH --error=${SIMID}.%j.err" >> $FILEPATH$FILENAME
    echo "#SBATCH --output=${SIMID}.%j.out" >> $FILEPATH$FILENAME
    # echo "#SBATCH --mail-type=FAIL" >> $FILEPATH$FILENAME
    # echo "#SBATCH --mail-user=dorsey@ipfdd.de" >> $FILEPATH$FILENAME
    echo "" >> $FILEPATH$FILENAME
    echo "" >> $FILEPATH$FILENAME
    echo " ### MODULES ### " >> $FILEPATH$FILENAME
    echo "module purge" >> $FILEPATH$FILENAME
    echo "module load FEBio/4.9" >> $FILEPATH$FILENAME
    echo "module list" >> $FILEPATH$FILENAME
    echo "" >> $FILEPATH$FILENAME
    echo "### JOB ###" >> $FILEPATH$FILENAME
    echo "echo \"Running ${SIMID} on host \$(hostname) in \$(pwd)\"" >> $FILEPATH$FILENAME
    echo "echo \"Job start time is \$(date).\"" >> $FILEPATH$FILENAME
    echo "srun febio4 ${FEB_FILE} > febio4.job.out 2>&1" >> $FILEPATH$FILENAME #> /dev/null 2>&1
    echo "echo \"Job end time is \$(date).\"" >> $FILEPATH$FILENAME

}

# submit slurm script to cluster
sub_slurm_script () {

    ## PARAMETERS
    # current directory
    local currdir=$(pwd)

    ## ARGUMENTS
    # none

    ## SCRIPT
    # navigate to the job directory
    echo $currdir
    cd $SIMDIR
    echo $pwd

    # log into cluster and submit script
    sbatch ${SIMID}.slurm.sub

    # exit cluster, return to starting directory
    cd $currdir
    echo $pwd

}

## OPTIONS
# parse options
while getopts "hrd:j:f:" option; do
    case $option in
        h) # call help with nonzero exit code
            help 0 ;;
        r) # replicate simulation if simulation data already exists
            declare -i BOOL_REPLICATE=1 ;;
        d) # specify the path to the job directory
            declare -i BOOL_DIR=1
            DIR="${OPTARG}" ;;
        j) # specify the job name
            declare -i BOOL_JOB=1
            JOB="${OPTARG}" ;;
        f) # specifiy the name of the feb file
            declare -i BOOL_FEB=1
            FEB_FILE="${OPTARG}" ;;
        ?) # default for unspecified option
            # call help with nonzero exit code
            help $NONZEROEXITCODE
    esac
done

## ARGUMENTS
# none

## SCRIPT
# check that the necessary arguments have been specified
check

# specify simid and simdir
if [[ $BOOL_REPLICATE -eq 1 ]]; then
    # if replicate has been specified
    echo -e "\nTODO :: specify replicate protocol.\n"
    exit $NONZEROEXITCODE
else
    # otherwise, run the job in $DIR
    SIMID="${JOB}"
    SIMDIR="${DIR}"
fi

# generate slurm script, job directory
gen_slurm_script

# submit slurm script
sub_slurm_script
