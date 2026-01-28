#!/bin/bash
set -e

## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institute for Colloids and Interfaces
## 2026.01.28

## MODULES
# used to parse and write information to csv files
PARSE_CSV="./programs/bash/util/parse_csv.sh"

## PARAMETERS
# nonzero exit code
declare -i NONZERO_EXITCODE=120
# filename
FILENAME="/bash/parameter/length-scale.sh"
# file purpose
PURPOSE="generate parameters that correspond to a simulation length scale"
# default header used for parameter files
PARM_HEADER="n,id,path"
# default header used for the config file
CONFIG_HEADER="key,xml,description,units,constant,related,symbolic"

## FUNCTIONS
# display options, exit
help () {

    ## PARAMETERS
    # none

    ## ARGUMENTS
    # none

    ## SCRIPT
    # first option: exit code
    local exitcode=$1

    ## SCRIPT
    # display script name and purpose
    echo -e "\nFILE: \t ${FILENAME}.sh\nPURPOSE: ${PURPOSE}.\n"
    echo -e "DESCRIPTION: to parametrically adjust the length scale of 'FEB' models, the model files are stored in a model directory which matches the hirearchy: \${FEB}/scale/\${MODEL}/\${SCALE}.feb. Here, \${FEB} and \${MODEL} correspond to the parameters -f and -m, respectively. \${SCALE} refers to the name of the feb model, which is the assigned length scale. The script parses the length scales from the model file names, and then uses that information to generate the corresponding parameters."
    # display script options
    echo -e "\n ## SCRIPT PROTOCOL ##"
    echo -e " -h\t\t| display HELP options, exit 0."
    # echo -e " -v\t\t| VERBOSE execution of script as export single line describing script actions to CLT."
    # echo -e " -V\t\t| VERY VERBOSE execution of script, export script execution to CLT at least step."
    echo -e "\n ## FEB PARAMETER OPTIONS ##"
    echo -e " -d << ARG >>\t| MANDATORY: path to DIRECTORY to which contains directory hirearchy."
    echo -e " -j << ARG >>\t| MANDATORY: named assgined to JOB, contains simulation directories."
    echo -e " -f << ARG >>\t| MANDATORY: path to FEB directory which contains scaled models."
    echo -e " -m << ARG >>\t| MADNATORY: name of scaled MODEL."
    echo -e " -k << ARG >>\t| OPTIONAL: shortcut KEY used to identify parameter (default is ...)."
    echo -e " -x << ARG >>\t| OPTIONAL: XML path specifiying parameter in '.feb' file (default is ...)."
    echo -e " -u << ARG >>\t| OPTIONAL: units corresponding to parameter, stored in config file (default is ...)."
    echo -e " -D << ARG >>\t| OPTIONAL: single string describing parameter, store in config file (default is ...)."
    echo -e ""

    # exit with exit code
    exit $exitcode

}

## OPTIONS
# parse options
while getopts "h" opt; do
    case $opt in
        h) # display options exit zero
            help 0 ;;
        ?) # default, display options with nonzero exitcode
            help $NONZERO_EXITCODE
    esac
done

## ARGMENTS
# none

## SCRIPT
# none
