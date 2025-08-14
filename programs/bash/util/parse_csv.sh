#!/bin/bash
set -e

## Matthew Dorsey
## @sunprancekid
## North Carolina State University
## 2023.05.15
## program used for parseing csv files

## ARGUMENTS
# integer used as exit code when usage error has occured
declare -i NONZERO_EXITCODE=1
# boolean that determines if the program is debugging
declare -i BOOL_DEBUG=0
# boolean that determines if the number of lines should
# be returned to the user
declare -i GET_LINES=0
# boolean that determines if a line number has been specified
declare -i GOT_LINE=0
# boolean that determins if the number of columns should be returned
# to the user
declare -i GET_COL=0
# boolean that determines if the column number has been specified
declare -i GOT_COL=0
# boolean that determines if the filename has been parsed
declare -i GOT_FILENAME=0
# array containing all of the arguments in the script
ARGS=($@)
# number of elements in array containing arguments
N_ARGS=$#

## OPTIONS
# parse options
while [[ $# -gt 0 ]]
do
	# parse each options
	case $1 in
		# turn on debugging mode
		-d)

			# boolean that determines if the debugging
			# is on
			declare -i BOOL_DEBUG=1
			shift # pass argument
			;;
		# parse option corresponding to csv columns
		-c)

			shift # pass argument

			# check if there is an argument after the flag
			if [[ $# -gt 0 ]]
			then
				# parse the argument
				COL_NO=$1
				# determine if it is a flag
				if ! [[ COL_NO == "-"* ]]
				# if the next argument is not a flag
				then
					declare -i COL_NO
					declare -i GOT_COL=1
					shift # pass the argument
					if [[ BOOL_DEBUG -eq 1 ]]
					then
						# inform the user
						echo "Column number $COL_NO specified by user."
					fi
				fi
			fi

			if [[ GOT_COL -eq 0 ]]
			# if the user did not specify a column number
			then
				# the number of columns still needs to be parsed
				declare -i GET_COL=1
			fi
			;;
		# parse the option corresponding to the number of lines
		-l)

			shift # pass the argument

			## check if there is an argument after the flag
			if [[ $# -gt 0 ]]
			then
				# parse the next argument
				LINE_NO=$1
				# determine if it is a flag
				if ! [[ $LINE_NO == "-"* ]]
				# if the next argument is not a flag
				then
					declare -i LINE_NO
					declare -i GOT_LINE=1
					shift # pass the argument
					if [[ BOOL_DEBUG -eq 1 ]]; then
						# inform the user
						echo "Line number $LINE_NO specified by the user."
					fi
				fi
			fi

			if [[ GOT_LINE -eq 0 ]]
			# if the user did not specify a line number
			then
				# the number of lines still needs to be parsed
				declare -i GET_LINES=1
			fi
			;;
		# specify the file name
		-f)

			shift # pass the argument

			## check if there is an argument after the flag
			if [[ $# -gt 0 ]]
			then
				# parse the next argument
				FILENAME=$1
				# determine if it is a flag
				if ! [[ $FILENAME == "-"* ]]
				# if the next argument is not a flag
				then
					declare -i GOT_FILENAME=1
					shift # pass the argument
					if [[ BOOL_DEBUG -eq 1 ]]; then
						# inform the user
						echo "filename is $FILENAME."
					fi
				fi
			fi

		;;
		# default option if parsed letter does not
		# match possible
		\?)
			shift # pass argument
			;;
	esac
done

## ARGUMENTS
# none

## FUNCTIONS
# function that parses the number of lines in a file
# provided the name of the file
get_lines() {

	## PARAMETERS
	# none

	## OPTIONS
	# none

	## ARGUMENTS
	# name of file to parse lines from
	local filename=$1

	## SCRIPT
	# parse the number of lines from the file
	declare -i N_LINES=$(wc -l < $filename)

	# return the numbe of lines in the csv to the user
	echo $N_LINES
}
# function that gets a specific line from a csv file
get_line() {

	## PARAMETERS
	# none

	## OPTIONS
	# none

	## ARGUMENTS
	# name of file to parse lines from
	local filename=$1
	# line number of parse from file
	declare -i line_no=$2

	## SCRIPT
	# parse the line from the file
	line=$( head -n ${line_no} ${filename} | tail -n 1 )

	# return the line
	echo $line
}
# function that determines the number of columns in
# a csv line
get_cols_line(){

	## PARAMETERS
	# none

	## OPTIONS
	# none

	## ARGUMENTS
	# name of file to parse lines from
	local filename=$1
	# line number of parse from file
	declare -i line_no=$2

	## SCRIPT
	# parse the line from the csv file
	local line=$(get_line $filename $line_no)

	# determine the number of times the delimiter occurs in the line
	declare -i n_col=$(echo $line | sed 's/\(.\)/\n\1/g' | sort | uniq -c | grep , | cut -d "," -f 1)

	# the number of columns in the line is one more than
	# the number of delimiters
	((n_col+=1))

	# return the value to the user
	echo $n_col
}
# function that gets a particular element in a line
get_element_col_line(){

	## PARAMETERS
	# none

	## OPTIONS
	# none

	## ARGUMENTS
	# name of file to parse lines from
	local filename=$1
	# line number of parse from file
	declare -i line_no=$2
	# column number to parse from file
	declare -i col_no=$3

	## SCRIPT
	# parse the line from the csv file
	local line=$(get_line $filename $line_no)

	# determine the number of times the delimiter occurs in the line
	element=$(echo $line | cut -d , -f $col_no )

	# return the value to the user
	echo $element
}

## SCRIPT
# check that a file name has been provided and
# that the path to the file is correct
if [[ GOT_FILENAME -eq 0 ]]
# if the script did not parse the file name
then
	# inform the user and exit
	echo -e "\nERROR: Must specify filename when parsing file."
	echo -e "USAGE: ./parse_csv.sh -f FILENAME [...]"
	exit $NONZERO_EXITCODE
elif ! test -f $FILENAME
# if the path to the file does not exist
then
	# inform the user and exit
	echo -e "\nERROR: Path to $FILENAME does not exist."
	exit $NONZERO_EXITCODE
fi

# parse the information about lines
declare -i N_LINES=$(get_lines $FILENAME)
if [[ GET_LINES -eq 1 ]]
# if the number of lines in the file should be returned to the user
then
	# return the number of lines in the file to the user
	echo $N_LINES
	# exit the program
	exit 0
elif [[ GOT_LINE -eq 1 ]]
# if a specific line has been specified by the user
then
	# check that the line number specified by the user is within the
	# bounds of the file
	if [[ (( LINE_NO -gt N_LINES ) || ( LINE_NO -lt 0 )) ]]
	then
		# value provided by the user is too large
		echo -e "\nERROR: Line number specified by user is too large."
		echo -e "USAGE: ./parse_csv.sh -f $FILENAME -l [ 0 < integer <= $N_LINES]"
		exit $NONZERO_EXITCODE
	fi

	# determine the number of data entries in the line
	declare -i N_COLS=$(get_cols_line $FILENAME $LINE_NO)

	if [[ GOT_COL -eq 1 ]]
	# if a column number has been specified
	then
		# check that the column specified by the user is within the limits
		if [[ COL_NO -gt N_COLS ]]
		# if the column number specified by the user is greater than
		# the number of columns in the row
		then
			# inform the user and exit
			echo -e "\nERROR: Column number out of bounds."
			echo -e "USAGE: ./parse_csv.sh -f $FILENAME -l $LINE_NO -c [ 0 < integer <= $N_COLS]"
			exit 0
		fi
		# parse the item corresponding to the column
		ELEMENT=$(get_element_col_line $FILENAME $LINE_NO $COL_NO)

		# return the value to the user
		echo $ELEMENT

	elif [[ GET_COL -eq 1 ]]
	# if a column return has been called but not specified
	then
		# return the number of columns in the line to the user
		echo $N_COLS
	else
		# return the entire line to the user
		echo $(get_line $FILENAME $LINE_NO)
	fi
fi

exit 0
