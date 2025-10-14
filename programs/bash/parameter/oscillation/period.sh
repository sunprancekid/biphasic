#!/bin/bash
set -e 

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2025.10.13

## FILENAME: programs/bash/parameters/oscillation/period.sh
## PURPOSE: specify or vary the period associated with a FEB oscillation simulation

## MODULES
# generates parameters and integrates with feb file
FEB_PARAMETER="./programs/bash/parameter/feb_parameter.sh"

## PARAMETERS - CONSTANTS
# non-zero exit code
declare -i NONZERO_EXITCODE=120
# script filename
FILENAME="programs/bash/parameters/oscillation/period.sh"
# script purpouse
PURPOSE="specify or vary the depth of tip period associated with FEB osclliation simulations"

## PARAMETERS - PERIOD OPTIONS
# boolean determining if the job directoy has been specified
DIR="/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# boolean determining if the job name has been specified
declare -i BOOL_JOB=0
# default xml path
XML_PATH="Step/step[@id='2']/Rigid/rigid_bc[@name='tip_oscillation']/value[@lc='2']"
# default key 
KEY="OT"
# default units
UNITS="s"
# default description
DESCRIPTION="oscillation_period"
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

## PARAMETERS - SIMULATION LENGTH and NUMERICAL STEP SIZE OPTIONS
# number of oscillation cycles
declare -i N_CYCLES=10
# number of numerical time steps during each simulation
declare -i N_STEPS=40
# key for number of numerical steps 
KEY_STEPS="ON"
# description for number of time steps
DESCRIP_STEPS="oscillation_total_numerical_steps"
# xml path for the number of steps
XML_STEPS="Step/step[@id='2']/Control/time_steps"
# key for simulation initial step size
KEY_INIT_STEP="OSMi"
# description for numerical step size
DESCRIP_INIT_STEP="oscillation_initial_step"
# xml path for minimum / initial step size
XML_INIT_STEP="Step/step[@id='2']/Control/step_size"
# key for simulation max step size
KEY_MAX_STEP="OSMa"
# description for the maximum step size
DESCRIP_MAX_STEP="oscillation_max_step"
# xml path for max step size
XML_MAX_STEP="Step/step[@id='2']/Control/time_stepper[@type='default']/dtmax"



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
    echo -e "\n ## OSCILLATION PERIOD PARAMETER OPTIONS ##"
    echo -e " -j << ARG >>\t| MANDATORY: named assgined to JOB, contains simulation directories."
    echo -e " -d << ARG >>\t| path to DIRECTORY to which contains directory hirearchy (default is ${DIR})."
    echo -e " -x << ARG >>\t| XML path specifiying parameter in '.feb' file (default is ${XML_PATH})."
    echo -e " -k << ARG >>\t| shortcut KEY used to identify parameter (default is ${KEY})."
    echo -e " -u << ARG >>\t| UNITS corresponding to parameter, stored in job config file (default is ${UNITS})."
    echo -e " -D << ARG >>\t| single string DESCRIBING parameter, store in job config file (default is ${DESCRIPTION})."
    echo -e "\n ## GENERATING ONE VALUE ##"
    echo -e " -C << ARG >>\t| assign one CONSTANT value to property."
    echo -e "\n ## GENERATING MULTIPLE VALUES ##"
    echo -e " -L \t\t| generate parameters along LOG scale (default is LINEAR)."
    echo -e " -A << ARG >>\t| MINIMUM value assigned to parameter."
    echo -e " -B << ARG >>\t| MAX value assigned to parameter."
    echo -e " -N << ARG >>\t| NUMBER of unique parameters to generate between A and B."
    echo -e " \n ## SIMULATION LENGTH AND NUMERICAL STEP SIZE ##"
    echo -e " -C << ARG >>\t number of oscillation CYCLES (default is ${N_CYCLES})."
    echo -e " -T << ARG >>\t number of TIME integration steps per cycle (default is ${N_STEPS})"
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

# check script parameters
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
gen () {

	# PARAMTERS
	# none

	## ARGUMENTS
	# none

	## SCRIPT
	# execute feb paramterization script
	# write the period 
	if [[ $BOOL_CONSTANT -eq 1 ]]; then
		# append constant value to job
		$FEB_PARAMETER -j $JOB -d $DIR -x $XML_PATH -k $KEY -u $UNITS -D $DESCRIPTION -C $CONSTANT_VALUE
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
	# write the total number of numerical steps (constant)
	declare -i TOTAL_STEPS_MAX=$( echo "$N_CYCLES * $N_STEPS" | bc -l ) # based on max step size
	declare -i TOTAL_STEPS_MIN=$( echo "$TOTAL_STEPS_MAX * 10" | bc -l ) # based on the inital step size
	$FEB_PARAMETER -j $JOB -d $DIR -k $KEY_STEPS -x $XML_STEPS -D $DESCRIP_STEPS -C $( echo "$TOTAL_STEPS_MIN" )
	# write the max step size (dependent on the period - OT)
	$FEB_PARAMETER -j $JOB -d $DIR -x $XML_MAX_STEP -D $DESCRIP_MAX_STEP -k $KEY_MAX_STEP -C "${KEY}/${KEY_STEPS}"
	# write the initial step size (dependent on the period - OT)
	$FEB_PARAMETER -j $JOB -d $DIR -x $XML_INIT_STEP -D $DESCRIP_INIT_STEP -k $KEY_INIT_STEP -C "${KEY}/(${KEY_STEPS}*10)"
}

## OPTIONS
# prase options
while getopts "hd:j:x:k:u:D:C:A:B:N:LC:T:" opt; do
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
        A) # specify a minimum number to generate
            declare -i BOOL_MINVAL=1
            MINVAL=${OPTARG} ;;
        B) # specify a maxmimum number to generate
            declare -i BOOL_MAXVAL=1
            MAXVAL=${OPTARG} ;;
        C) # specify the number of cycles to perform
        	declare -i N_CYCLES=${OPTARG} ;;
        T) # specify the number of numerical time integration steps
        	declare -i N_STEPS=${OPTARG} ;;
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

# generate parameter values
gen