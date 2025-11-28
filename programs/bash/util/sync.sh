#!/bin/bash
set -e

## Matthew Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.10.14

## FILENAME: programs/bash/util/sync.sh
## PURPOSE: use rsync to download or upload files to a remote directory

## PARAMETERS 
# script filename
FILENAME="programs/bash/util/sync.sh"
# script purpose
PURPOSE="use rsync to download or upload files to a remote directory."
# exit code for error
declare -i NONZERO_EXITCODE=120

## PARAMETERS - COMMON HOST
# PATh super computer
PATh_HOST="matthew.dorsey@ap21.facility.path-cc.io"
# Open Science Grid access point
OSG_HOST=""
# mpikg login path
MPIKG_HOST="dorsey@ssh.mpikg.mpg.de"
# remote desktop
UBT_HOST="matthew-dorsey@192.168.2.165 -p 3389"

## PARAMETERS - COMMON PATHS
# absolute path in local directory to simulation files
ABS_PATH="~/professional/NCSU/paper3/data/"
# path to hall NCSU storage when connected
NCSU_PATH="/Volumes/hall/madorse2/paper4/data"
# path to PATh
PATh_PATH="matthew.dorsey@ap1.facility.path-cc.io:paper3/data/"

# PARAMETERS - OPTIONS
# boolean that determines if the local path has been specifed
declare -i BOOL_LOCAL=0
# boolean that determines if the remote path has been specifed
declare -i BOOL_REMOTE=0
# boolean determining if the remote login address has been specified
declare -i BOOL_ADDRESS=0
# boolean determnining if a unique port number has been specified
declare -i BOOL_PORT=0
# boolean determining if the script should execute verbosely
declare -i BOOL_VERBOSE=0
# boolean determining if the script should send files (local -> remote)
declare -i BOOL_SEND=0
# boolean determining if the script should get files (remote -> local)
declare -i BOOL_GET=0
# boolean determining if the script should also zip files before transfer
declare -i BOOL_ZIP=0
# boolean determining if the script should use regular expression to qualify which files are transfered
declare -i BOOL_REGEX=0


## FUNCTIONS
# display help, exit
help () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# first argument: exit code
	local exitcode=$1

	## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    # display script options
    echo -e "\n ## SCRIPT EXECUTION ##"
    echo -e " -h\t\t| display HELP options, exit 0."
    echo -e " -v\t\t| execute VERBOSELY."
    echo -e " -s\t\t| SEND: sync remote directory with local directory."
    echo -e " -g\t\t| GET: sync local directory with remote directory."
    echo -e " -z\t\t| ZIP directory before sending or recieving."
    echo -e "\n ## SCRIPT PARAMETERS ##"
    echo -e " -l  << ARG >>\t| MADNDATORY: LOCAL path."
    echo -e " -r  << ARG >>\t| MADNDATORY: REMOTE path."
    echo -e " -a  << ARG >>\t| MADNDATORY: remote login ADDRESS."
    echo -e " -e  << ARG >>\t| include regular-EXPRESSION to qualify sync / zip operation(s) for files being transfered."
    echo -e " -p  << ARG >>\t| remote host PORT (default is 22)."

    # exit with exit code
    exit $exitcode
}

# display error message and exit
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

# check script arguments before execution
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # check the local path
    if [ $BOOL_LOCAL -eq 0 ]; then
        # must specify local path
        display_error "must specify local path (option -l)"
    else
        # local path has been specified, check that it exists
        if [ ! -d $LOCAL_PATH ]; then
            # if the local path is not a directory, it cannot be transmitted
            display_error "local path '${LOCAL_PATH}' does not exist or cannot be found."
        fi
    fi

    # check the remote path
    if [ $BOOL_REMOTE -eq 0 ]; then
        # must specify remote path
        display_error "must specify remote path (option -r)"
    fi

    # check the remote login address
    if [ $BOOL_ADDRESS -eq 0 ]; then
        # must specify the login address
        display_error "must specify remote login address (option -a)"
    fi
}

## OPTIONS
# parse options
while getopts "hvsgzl:r:a:e:p:" opt; do
 case $opt in
    h) # display options, exit 0
        help 0 ;;
    v) # execute script verbosely
        declare -i BOOL_VERBOSE=1 ;;
    s) # send files (local -> remote)
        declare -i BOOL_SEND=1 ;;
    g) # get files (remote -> local)
        declare -i BOOL_GET=1 ;;
    z) # zip files
        declare -i BOOL_ZIP=1 ;;
    l) # local path
        declare -i BOOL_LOCAL=1
        LOCAL_PATH=${OPTARG} ;;
    r) # remote path
        declare -i BOOL_REMOTE=1
        REMOTE_PATH=${OPTARG} ;;
    a) # remote address 
        declare -i BOOL_ADDRESS=1
        REMOTE_ADDRESS=${OPTARG};;
    e) # specify regular expression
        declare -i BOOL_REGEX=1
        REGEX=${OPTARG} ;;
    p) # port
        declare -i BOOL_PORT=1
        declare -i PORT_NUMBER=${OPTARG} ;;
    ?) # default option
        help $NONZERO_EXITCODE
    esac
done

## ARGUMENTS
# none
# first argument: simulation path (expected format is 'conH/squ2c32/a*/h*')
# SIM_DIR=$1

## SCRIPT
# check script arguments
check

# check that the absolute path exists
if [ ! -d $ABS_PATH$SIM_DIR ]; then
	echo "Path '$ABS_PATH$SIM_DIR' does not exist."
fi

# sync local directory with PATh
echo rsync -Pavz $PATh_PATH$SIM_DIR

# clean and compress simulation files
# sync hall NCSU with local simulation files
echo ./zip.sh -r e* -p conH/squ2c32/a050/h00/ -e -u $NCSU_PATH

# remove compressed directory
echo rm $ABS_PATH$SIM_DIR