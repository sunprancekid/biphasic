
## Matthew A Dorsey
## @mad-mpikg
## Max-Planck-Institute for Colloids and Interfaces
## 2026.08.17
## used to create scripts used during slurm submission

## MODULES
# native
import sys, os

## PARAMETERS
# none

## METHODS
# generates slurm script
def gen_slurm_script (filepath = None, jobid = None, overwrite = False, del_feb = False, del_xplt = None):
	""" generates slurm submission script.

	Arguments:
	----------
	filepath : str
		path location of script
	jobid : str
		name of job on compute cluster
	overwrite : bool
		if 'True', overwrite existing files even if they exists
	def_feb : bool
		if 'True', job deletes any files that match'*.feb' upon completion
	del_xplt : bool
		if 'True', job deletes any files that match '*.xplt' upon completion

	Returns:
	--------
	None
	"""
	# create list if file contents
	f_list = []
	f_list.append("#/bin/bash -l")
	f_list.append("")
	f_list.append("#SBATCH --partition=cpu2")
	if jobid is not None: f_list.append("#BATCH -J {0}".format(jobid))
	f_list.append("#SBATCH --nodes=1")
	f_list.append("#SBATCH --ntasks=1")
	f_list.append("#SBATCH --cpus-per-task=16")
	if jobid is not None: f_list.append("#SBATCH --error={0}.%j.err")
	if jobid is not None: f_list.append("#SBATCH --error={0}.%j.out")

	# check that the file exists
	# check if overwrite was specified
	# create file
	f = open(filepath, 'w')
	f.write ("")
	pass

## CLASSES
# none

## ARGUMENTS
# none

## SCRIPT
# none
