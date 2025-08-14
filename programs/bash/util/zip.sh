#!/bin/bash
set -e

## Matthew Dorsey
## @sunprancekid
## 2025.08.01
## program for zipping simulation up simulation files and shipping them off to the cloud

## PARAMETERS
# nonzero exit code
NONZEROEXITCODE=120
# boolean determining if the script should exit verbosely
declare -i BOOL_VERBOSE=0
# boolean that determines if script should be execture
declare -i BOOL_EXECUTE=0
# boolean determining if specified directory should be uploaded to cloud
declare -i BOOL_UPLOAD=0
# boolean that determines if local should be sync with cloud first
declare -i BOOL_DOWNLOAD=0
# regular expression which formats the sub-directory hirearchy
REGEX=h*/e*

# directories to zip (and remove)
ZIPDIR=( "/r00/anneal" "/r00/out" )
# ZIPDIR=( "/anneal" "/out" )
# directories to delete
RMDIR=( "/r01" "/r02" "/r00/anal" "/r00/sub" )
# RMDIR=( "/anal" "/sub" )
# remove these file types
RMFILE=( "/r00/*.py" "/r00/*.sh" "/r00/*.spl" "/r00/*.txt" "/.DS_Store" "/r00/.DS_Store")
# RMFILE=( "/*.py" "/*.sh" "/*.spl" "/*.txt" "/.DS_Store" )

## FUNCTIONS
# report options and script usage, exit
help () {

	## PARAMETERS
	# none

	## ARGUMENTS
	# exitcode
	EXITCODE=$1

	## SCRIPT
	# report script used to cml
	# exit
	exit $EXITCODE
}
# zip
# delete without zipping

## OPTIONS
# parse options
# -v verbose execution
# -z unzips everything
# -d downloads from specified directory
# -s upload / sync with specified directory
# -r change ragex
while getopts "evp:r:u:d:" opt; do
	case $opt in
		v) # verbose directory
			declare -i BOOL_VERBOSE=1 ;;
		e) # execute script
			declare -i BOOL_EXECUTE=1 ;;
		u) # upload directory
			declare -i BOOL_UPLOAD=1
			UPLOAD_DIR=${OPTARG} ;;
		p) # path to main directory
			DIR=${OPTARG} ;;
		r) # change the regular expression
			REGEX=${OPTARG} ;;
		d) # download
			declare -i BOOL_DOWNLOAD=1
			DOWNLOAD_DIR=${OPTARG} ;;
		?) # unspecified option
			# call help, exit nonzero
			help $NONZEROEXITCODE
	esac
done


## ARGUMENTS
# none

## SCRIPT
# none

## PSEUDOCODE
# download from cloud before zipping

# create list of sub directories which match regular expression
SUBDIRS=( ${DIR}${REGEX} )
for sd in ${SUBDIRS[@]}; do
	# sync local with cloud
	if [ $BOOL_DOWNLOAD -eq 1 ]; then
		echo -e "\n\nSyncing ${sd} with ${DOWNLOAD_DIR} ...\n"
		rsync -Pavz ${DOWNLOAD_DIR}$sd/ $sd
	fi

	# clean
	echo -e "\n\nCleaning and compressing.. $sd\n"
	# delete program files (.f90, .sh)
	for fregex_rm in ${RMFILE[@]}; do
		# find files that match regular expression
		f_list=( ${sd}$fregex_rm )
		for f in ${f_list[@]}; do
			# remove the file if it exists
			if [ -f $f ]; then
				# if verbose, inform the user
				if [ $BOOL_VERBOSE -eq 1 ]; then
					echo "Removing file: $f"
				fi
				# if execute has been called, remove the file
				if [ $BOOL_EXECUTE -eq 1 ]; then
					rm $f
				fi
			else
				# if the file does not exist, inform user
				echo "Unable to find files $f. Cannot remove!"
			fi
		done
	done

	# loop through remove directories
	for dir_rm in ${RMDIR[@]}; do
		# remove the directory if it exists
		if [ $BOOL_VERBOSE -eq 1 -a -d ${sd}${dir_rm} ]; then
			# if verbose, inform user
			if [ $BOOL_VERBOSE -eq 1 ]; then
				echo "Removing directory: ${sd}${dir_rm}"
			fi
			# if execute, remove the directory
			if [ $BOOL_EXECUTE -eq 1 ]; then
				rm -r $sd$dir_rm
			fi
		else
			# if unable to find the directory, inform the user
			echo "Unable to find directory $sd$dir_rm. Cannot remove!"
		fi
	done

	# archive files
	for z in ${ZIPDIR[@]}; do
		# zip the files if they exist
		if [ $BOOL_VERBOSE -eq 1 -a -d $sd$z ]; then
			# if verbose, inform the user
			if [ $BOOL_VERBOSE -eq 1 ]; then
				echo "Compressing: $sd$z"
			fi
			# if execute, zip the directory, and remove it
			if [ $BOOL_EXECUTE -eq 1 ]; then
				zip -r $sd$z.zip $sd$z
				rm -r $sd$z
			fi
		else
			# if the directories do not exist, inform the user
			echo "Unable to find directory $sd$z. Cannot compress!"
		fi
	done

	# sync files with cloud
	if [ $BOOL_UPLOAD -eq 1 ]; then
		# check that the specified path exists
		if [ ! -d $UPLOAD_DIR ]; then
			# if it does not, inform the used and exit
			echo "Upload directory $UPLOAD_DIR does not exist.."
			echo $NONZEROEXITCODE
		fi

		# if verbose, inform user
		if [ $BOOL_VERBOSE -eq 1 ]; then
			echo -e "\nSyncing local ($sd) with cloud ($UPLOAD_DIR)."
		fi
		# if execute, sync directory
		if [ $BOOL_EXECUTE -eq 1 ]; then
			# if the directory does not exist, inform the user
			if [ ! -d $UPLOAD_DIR$sd ]; then
				mkdir -p $UPLOAD_DIR$sd
			fi
			# sync the directory
			rsync -Pavz $sd/ $UPLOAD_DIR$sd
		fi
	fi

	# remove if requested
done
