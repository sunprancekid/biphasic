#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institute for Colloids and Interfacial Sciences
## 2026.01.29

## FILENAME: programs/bash/parameters/loading/relaxation-time.sh
## PURPOSE: parameterize relaxation time of loading

## MODULES
# generates parameters and integrates with feb file
FEB_PARAMETER="./programs/bash/parameter/feb_parameter.sh"

## PARAMETERS - CONSTANTS
# non-zero exit code
declare -i NONZERO_EXITCODE=120
# script filename
FILENAME="programs/bash/parameter/loading/depth.sh"
# script purpouse
PURPOSE="specify or vary the depth of tip prestress associated with FEB loading simulations"

## PARAMETERS - OPTIONS
# boolean determining if the job directoy has been specified
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean determining if the job name has been specified
declare -i BOOL_JOB=0
# default xml path
XML_PATH="na"
# default key
KEY="RT"
# default units
UNITS="seconds"
# default description
DESCRIPTION="loading_hold_time"
# boolean for a constant value
declare -i BOOL_CONSTANT=0
# boolean for min val
declare -i BOOL_MINVAL=0
# boolean for max val
declare -i BOOL_MAXVAL=0
# boolean for number of values
declare -i BOOL_NVALS=0
# boolean for logscale
declare -i BOOL_LOGSCALE=0
# boolean for flagging constant valued parameters as related to other parameters
declare -i BOOL_RELATED=0
# boolean for flagging constant valued parameters as related to one another
declare -i BOOL_SYMBOLIC=0

## PARAMETERS - NUMERICAL STEP SIZE
# default step size
STEP_SIZE='0.1'
# step size xml path
XML_STEP_SIZE="Step/step[@id='1']/Control/step_size"
# step size key
KEY_STEP_SIZE='RTss'
# step size units
UNITS_STEP_SIZE='na'
# step size description
DESCRIPTION_STEP_SIZE='loading_step_size'

## PARAMETERS - NUMERICAL STEPS
# number steps xml path
XML_STEP_NUMBER="Step/step[@id='1']/Control/time_steps"
# numer steps key
KEY_STEP_NUMBER='RTn'
# number steps units
UNITS_STEP_NUMBER='na'
# number steps description
DESCRIPTION_STEP_NUMBER='loading_number_steps'


## METHODS
# display options, exit with exit code
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
    # echo -e " -v\t\t| VERBOSE execution of script as export single line describing script actions to CLT."
    # echo -e " -V\t\t| VERY VERBOSE execution of script, export script execution to CLT at least step."
    echo -e "\n ## LOADING DEPTH PARAMETER OPTIONS ##"
    echo -e " -j << ARG >>\t| MANDATORY: named assgined to JOB, contains simulation directories."
    echo -e " -d << ARG >>\t| path to DIRECTORY to which contains directory hirearchy (default is ${DIR})."
#     echo -e " -x << ARG >>\t| XML path specifiying parameter in '.feb' file (default is ${XML_PATH})."
    echo -e " -k << ARG >>\t| shortcut KEY used to identify parameter (default is ${KEY})."
    echo -e " -u << ARG >>\t| UNITS corresponding to parameter, stored in job config file (default is ${UNITS})."
    echo -e " -D << ARG >>\t| single string DESCRIBING parameter, store in job config file (default is ${DESCRIPTION})."
    echo -e "\n ## GENERATING ONE VALUE ##"
    echo -e " -C << ARG >>\t| assign one CONSTANT value to property."
    echo -e " -R\t\t| flag parameter as being related to other parameters (constant value contains KEY of other parameters)."
#     echo -e " -S\t\t| flag parameter as symbolic (i.e. is a maths equation, which should not be evaulated)."
    echo -e "\n ## GENERATING MULTIPLE VALUES ##"
    echo -e " -L \t\t| generate parameters along LOG scale (default is LINEAR)."
    echo -e " -A << ARG >>\t| MINIMUM value assigned to parameter."
    echo -e " -B << ARG >>\t| MAX value assigned to parameter."
    echo -e " -N << ARG >>\t| NUMBER of unique parameters to generate between A and B."
    echo -e " \n ## SIMULATION LENGTH AND NUMERICAL STEP SIZE ##"
    echo -e " -T << ARG >>\t number of TIME integration step size (default is ${STEP_SIZE})"
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

# check parameters passed to script
check () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
	# check that the job name was specified
	if [[ $BOOL_JOB -eq 0 ]]; then
		display_error "must specify job name (option -j)"
	fi

	# if a constant value was not specified
	if [[ $BOOL_CONSTANT -eq 0 ]]; then
		# check that the parameters for multiple value generate were specified
		if [[ $BOOL_MINVAL -eq 0 ]]; then
			display_error "for multiple values, must specify minimum in range (option -A)"
		elif [[ $BOOL_MAXVAL -eq 0 ]]; then
			display_error "for multiple values, must specify maxmimum in range (option -B)"
		elif [[ $BOOL_NVALS -eq 0 ]]; then
			display_error "for multiple values, must specify the total number of values to generate (option -N)"
		fi
	fi

}

# generate parameters
gen_parm () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    ## constant values
    # write the loading step size
    $FEB_PARAMETER -j $JOB -d $DIR -x $XML_STEP_SIZE -k $KEY_STEP_SIZE -u $UNITS_STEP_SIZE -D $DESCRIPTION_STEP_SIZE -C $STEP_SIZE
    # the number of steps during the loading phase is the loading time times the step size
    $FEB_PARAMETER -j $JOB -d $DIR -x $XML_STEP_NUMBER -k $KEY_STEP_NUMBER -u $UNITS_STEP_NUMBER -D $DESCRIPTION_STEP_NUMBER -C "${KEY} / ${KEY_STEP_SIZE}" -R -i # format as integer

    ## constant / variable values
    # write the loading time
	# execute feb paramterization script
	if [[ $BOOL_CONSTANT -eq 1 ]]; then
		if [[ $BOOL_RELATED -eq 1 ]]; then
			$FEB_PARAMETER -j $JOB -d $DIR -x $XML_PATH -k $KEY -u $UNITS -D $DESCRIPTION -C $CONSTANT_VALUE -R
		else
			$FEB_PARAMETER -j $JOB -d $DIR -x $XML_PATH -k $KEY -u $UNITS -D $DESCRIPTION -C $CONSTANT_VALUE
		fi
	else
		# generate multiple values and append to job
		if [[ $BOOL_LOGSCALE -eq 1 ]]; then
			# generate values on logscale
			$FEB_PARAMETER -j $JOB -d $DIR -x $XML_PATH -k $KEY -u $UNITS -D $DESCRIPTION -A $MINVAL -B $MAXVAL -N $NVALS -L
		else
			# generate values on linear scale
			$FEB_PARAMETER -j $JOB -d $DIR -x $XML_PATH -k $KEY -u $UNITS -D $DESCRIPTION -A $MINVAL -B $MAXVAL -N $NVALS
		fi
	fi

    return
}



## OPTIONS
# prase options
while getopts "hd:j:x:k:u:D:C:RA:B:N:L" opt; do
	case $opt in
		h) # display options
			help 0 ;;
		d) # define the directory
			DIR=${OPTARG} ;;
		j) # define job name
			declare -i BOOL_JOB=1
			JOB=${OPTARG} ;;
		x) # set the xml path
			XML_PATH=${OPTARG} ;;
		k) # set the key
			KEY=${OPTARG} ;;
		u) # reset the units
			UNITS=${OPTARG} ;;
		D) # set the description
			DESCRIPTION=${OPTARG} ;;
        C) # specify constant value
            declare -i BOOL_CONSTANT=1
            CONSTANT_VALUE=${OPTARG} ;;
        R) # relationship
        	declare -i BOOL_RELATED=1 ;;
        A) # specify a minimum number to generate
            declare -i BOOL_MINVAL=1
            MINVAL=${OPTARG} ;;
        B) # specify a maxmimum number to generate
            declare -i BOOL_MAXVAL=1
            MAXVAL=${OPTARG} ;;
        L) # generate values along a logarithmic scale
            declare -i BOOL_LOGSCALE=1 ;;
        N) # specify the number of values to generate
            declare -i BOOL_NVALS=1
            declare -i NVALS=${OPTARG} ;;
        ?) # default, display options with nonzero exitcode
            help $NONZERO_EXITCODE
	esac
done


## ARGUMENTS
# none


## SCRIPT
# check script parameters
check

# generate parameters
gen_parm
