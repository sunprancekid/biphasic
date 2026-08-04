#!/bin/bash
set -E

## Matthew A. Dorsey
## @mad-mpikg
## 2026.06.30
## use file to sync between local and remote computers

## MODULES
# contains syncing instructions
SYNC="sync.sh"
# used to parse information from csv files
PARSE_CSV="parse_csv.sh"

## PARAMETERS
# filename
FILENAME="update.sh"
# script purpose
PURPOSE="use file to sync local and remote directories"
# non zero exit code
declare -i NONZERO_EXITCODE=120
# path to mpikg desktop
MPIKG_DESKTOP="dorsey@ssh.mpikg.mpg.de"

## OPTIONS
# execute script verbosely
declare -i BOOL_VERB=0
# determines if directories should be updated locally
declare -i BOOL_GET=0
# determines if directories should be pushed to remote hosts
declare -i BOOL_SEND=0
# determines if a file containing the sync instructions has been obtains
declare -i BOOL_FILE=0
# determines if a path has been specified
declare -i BOOL_PATH=0
# determines if a specific line number was specified
declare -i BOOL_LINE=0
# path to executables
EX_PATH="./programs/bash/util/"

## SYNC FILE HEADERS
# column / number corresponding to the protocol ('protocol')
COL_PROTOCOL='protocol'
declare -i COL_NUM_PROTOCOL=0
# column number corresponding to the file or directory name ('name')
COL_NAME='name'
declare -i COL_NUM_NAME=0
# column number corresponding to the host ('host')
COL_HOST='host'
declare -i COL_NUM_HOST=0
# column number corresponding to the local directory ('local')
COL_LOCAL='local'
declare -i COL_NUM_LOCAL=0
# column number corresponding to the remote directory ('remote')
COL_REMOTE='remote'
declare -i COL_NUM_REMOTE=0

## MPIKG-LAPTOP
# list of paths to sync with laptop
list_sync=("/mnt/data/bgfs1/dorsey/presentations" "/mnt/data/bgfs1/dorsey/conferences")

## METHODS
# display options, exit
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
    echo -e " -v\t\t| execute script VERBOSELY."
    echo -e " -f\t\t| specify FILE which contains sync instructions"
    echo -e " -s\t\t| SEND: sync remote directory with local directory (local -> remote)."
    echo -e " -g\t\t| GET: sync local directory with remote directory (remote -> local)."
    echo -e " -p\t\t| specify path to executables 'sync.sh' and 'parse_csv.sh' (default is ${EX_PATH})"
    echo -e " -n << ARG >> \t| specify a certain line number in FILE to perform operation for (exclusively)."
    echo -e ""

    # exit with exit code
    exit $exitcode

}

check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    ## check that script options / arguments are correct before execution
    # check that path to the executables
    if [ ! -f ${EX_PATH}${SYNC} ]; then
        # the executable does not exist in the path
        display_error "executable ${SYNC} cannot be found in ${EX_PATH}. update path with option -p."
    else
        # update the executable with the path
        SYNC=${EX_PATH}${SYNC}
    fi
    if [ ! -f ${EX_PATH}${PARSE_CSV} ]; then
        # the executable does not exist in the path
        display_error "executable ${PARSE_CSV} cannot be found in ${EX_PATH}. update path with option -p."
    else
        # update the executable with the path
        PARSE_CSV=${EX_PATH}${PARSE_CSV}
    fi

    # check that the file has been specified and exists
    if [ $BOOL_FILE -eq 0 ]; then
        display_error "file containing sync instructions must be specified with option -f."
    elif [ ! -f ${SYNC_FILE} ]; then
        display_error "file '${SYNC_FILE}' containing sync instructions does not exist or cannot be found."
    fi

    # if a line number was specified, check that it exists in the file
    if [[ $BOOL_LINE -eq 1 ]]; then 
        # check that the line number exists in the file
        declare -i n_lines=$($PARSE_CSV -f $SYNC_FILE -l)
        if [[ $L -gt $n_lines ]]; then
            display_error "argument '${L}' was passed to flag '-n', but file '$SYNC_FILE' contains $n_lines lines"
        elif [[ $L -lt 2 ]]; then
            display_error "argument '${L}' was passed to flag '-n', which is less than the minimum number '2' (the first line is the header)."
        fi
    fi

    # check for the column headers
    declare -i N_COL=$($PARSE_CSV -f $SYNC_FILE -l 1 -c)
    for n in $(seq 1 $N_COL); do
            local head="$($PARSE_CSV -f $SYNC_FILE -l 1 -c $n)"
            if [ "$head" = "$COL_HOST" ]; then
                declare -i COL_NUM_HOST=$n
            elif [ "$head" = "$COL_LOCAL" ]; then
                declare -i COL_NUM_LOCAL=$n
            elif [ "$head" = "$COL_NAME" ]; then
                declare -i COL_NUM_NAME=$n
            elif [ "$head" = "$COL_REMOTE" ]; then
                declare -i COL_NUM_REMOTE=$n
            elif [ "${head}" = "${COL_PROTOCOL}" ]; then
                declare -i COL_NUM_PROTOCOL=$n
            fi
    done

    # check if any columns where unspecified
    if [ $COL_NUM_HOST -eq 0 ]; then
        display_error "column header '${COL_HOST}' does not exist in ${SYNC_FILE}."
    elif [ $COL_NUM_LOCAL -eq 0 ]; then
        display_error "column header '${COL_LOCAL}' does not exist in ${SYNC_FILE}."
    elif [ $COL_NUM_NAME -eq 0 ]; then
        display_error "column header '${COL_NAME}' does not exist in ${SYNC_FILE}."
    elif [ $COL_NUM_PROTOCOL -eq 0 ]; then
        display_error "column header '${COL_PROTOCOL}' does not exist in ${SYNC_FILE}."
    elif [ $COL_NUM_REMOTE -eq 0 ]; then
        display_error "column header '${COL_REMOTE}' does not exist in ${SYNC_FILE}."
    fi
}

display_error () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: error message to display
    local err_msg=$1

    ## SCRIPT
    # display error message
    echo -e "\nERROR :: ${FILENAME} :: ${err_msg}.\n"
    help $NONZERO_EXITCODE

}

# use sync to retrieve
get_sync () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: line in sync file which action should be performed for
    declare -i l=$1

    ## SCRIPT
    # get address
    local host=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_HOST)
    local local=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_LOCAL)
    local remote=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_REMOTE)
    local name=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_NAME)

    # if verbose, inform the user
    if [ $BOOL_VERB -eq 1 ]; then
        echo -e "\nSyncing '${name}' in remote directory '${host}:$remote' with local directory '${local}'.."
    fi

    # execute
    $SYNC -a $host -g -r $remote$name/ -l $local$name/
}

# use git to retrieve
get_git() {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: line in sync file that contains host information
    declare -i l=$1

    ## SCRIPT
    # get the sync info from script
    local host=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_HOST)
    local local=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_LOCAL)
    local remote=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_REMOTE)
    local name=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_NAME)
    # store the current working directory
    local curr_dir=$(echo $PWD)
    # navigate to the git directory
    cd $local$name
    # inform the user, if requested
    if [[ $BOOL_VERB -eq 1 ]]; then
        echo -e "\npulling git repo '${name}' located in directory '${local}'."
    fi
    # pull
    git pull
    # return to the current working directory
    cd $curr_dir
}

# use sync to send
send_sync () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: line in sync file which action should be performed for
    declare -i l=$1

    ## SCRIPT
    # get address
    local host=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_HOST)
    local local=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_LOCAL)
    local remote=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_REMOTE)
    local name=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_NAME)

    # if verbose, inform the user
    if [ $BOOL_VERB -eq 1 ]; then
        echo -e "\nSyncing '${name}' in local directory '${local}' with remote directory '${host}:$remote'.."
    fi

    # execute
    $SYNC -a $host -s -r $remote$name -l $local$name/
}

# use git to push directory
send_git() {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # first argument: line in sync file that contains host information
    declare -i l=$1

    ## SCRIPT
    # get the sync info from script
    local host=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_HOST)
    local local=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_LOCAL)
    local remote=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_REMOTE)
    local name=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_NAME)
    # store the current working directory
    local curr_dir=$(echo $PWD)
    # navigate to the git directory
    cd $local$name
    # inform the user, if requested
    if [[ $BOOL_VERB -eq 1 ]]; then
        echo -e "\npulling git repo '${name}' located in directory '${local}'."
    fi
    # pull
    git push
    # return to the current working directory
    cd $curr_dir
}

## FLAGS
while getopts "hvgsf:p:n:" opt; do
    case $opt in
        h) # display help options, exit
            help 0;;
        v) # execute script verbosely
            declare -i BOOL_VERB=1 ;;
        g) # get, syn files locally with remote directory
            declare -i BOOL_GET=1 ;;
        s) # send, push local files / directory to remote directory
            declare -i BOOL_SEND=1 ;;
        f) # declare file with sync instructions
            declare -i BOOL_FILE=1
            SYNC_FILE=${OPTARG} ;;
        p) # specify a path to the directory which contains the executables
            declare -i BOOL_PATH=1
            EX_PATH=${OPTARG} ;;
        n) # specify a certain line number to perform the syncing opertion for
            declare -i BOOL_LINE=1
            declare -i L=${OPTARG} ;;
        ?) # display help, exit non-zero
            help $NONZERO_EXITCODE
        esac
done

## ARGUMENTS
# none

## SCRIPT
## check script arguments
check

## update column headers
# have to do this again because of local call in 'check' is not global (for integers)
declare -i N_COL=$($PARSE_CSV -f $SYNC_FILE -l 1 -c)
for i in $(seq 1 $N_COL); do
        head="$($PARSE_CSV -f $SYNC_FILE -l 1 -c $i)"
        if [ $head = $COL_HOST ]; then
            declare -i COL_NUM_HOST=$i
        elif [ $head = $COL_LOCAL ]; then
            declare -i COL_NUM_LOCAL=$i
        elif [ $head = $COL_NAME ]; then
            declare -i COL_NUM_NAME=$i
        elif [ $head = $COL_REMOTE ]; then
            declare -i COL_NUM_REMOTE=$i
        elif [ $head = $COL_PROTOCOL ]; then
            declare -i COL_NUM_PROTOCOL=$i
        fi
done

## loop through each line in the file
# if one specific line was provided
if [[ $BOOL_LINE -eq 1 ]]; then
    # increment only the requested line
    declare -i START_LINE=$L
    declare -i N_LINES=$L
else
    # increment all lines
    declare -i START_LINE=2
    declare -i N_LINES=$($PARSE_CSV -f $SYNC_FILE -l )
fi
for l in $(seq $START_LINE $N_LINES); do
    # determine the protocol
    p=$($PARSE_CSV -f $SYNC_FILE -l $l -c $COL_NUM_PROTOCOL)
    # execute protocol
    if [[ ($BOOL_GET -eq 1) && ( ("${p}" = "sync-bash") || ( "${p}" = "sync-local" ) ) ]]; then
        get_sync $l
    elif [[ ($BOOL_GET -eq 1) && ( ("${p}" = "git") || ("${p}" = "git-pull") ) ]]; then
        get_git $l
    elif [[ ($BOOL_SEND -eq 1) && ("${p}" = "sync-bash") ]]; then
        send_sync $l
    elif [[ ($BOOL_SEND -eq 1) && (${p} = "git") ]]; then
        send_git $l
    fi
done
