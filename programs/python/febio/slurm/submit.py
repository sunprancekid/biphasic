
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
def gen_slurm_script (filepath = None, jobid = None, feb_file = None, opt_file = None, time_limit = None, overwrite = False, del_feb = False, del_xplt = None):
	""" generates slurm submission script.

	Arguments:
	----------
	filepath : str
		path location of script
	jobid : str
		name of job on compute cluster
	feb_file : str 
		path to febio file
	opt_file : str (optional)
		for optimization jobs, path to optimization file
	time_limit : str
		string description of time limit assigned to job (e.g. 1-12:00:00)
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
	## check arguments
	# check the file path
	if filepath is None:
		print ("ERROR :: submit.gen_slurm_script() :: method argument 'filepath' must be specified in method call.")
		return
	elif (os.path.exists(filepath)) and (not overwrite):
		# the file exists already but overwrite is not allowed
		print ("ERROR :: submit.gen_slurm_script() :: method argument 'filepath' ({0}) exists already but 'overwrite' was not specified; cannot overwrite existing file.".format(filepath))
		return
	# check the febfile
	if feb_file is None:
		# throw error 
		print("ERROR :: submit.gen_slurm_script() :: method argument 'feb_file' must be specified during method call.")
		return

	## write file contents to list
	# create list if file contents
	f_list = []
	f_list.append("#!/bin/bash -l")
	f_list.append("")
	f_list.append("#SBATCH --partition=cpu2")
	if jobid is not None: f_list.append("#SBATCH -J {0}".format(jobid))
	f_list.append("#SBATCH --nodes=1")
	f_list.append("#SBATCH --ntasks=1")
	# f_list.append("#SBATCH --cpus-per-task=16")
	if jobid is not None: f_list.append("#SBATCH --error={0}.%j.err".format(jobid))
	else: f_list.append("#SBATCH --error=%j.err")
	if jobid is not None: f_list.append("#SBATCH --error={0}.%j.out".format(jobid))
	else: f_list.append("#SBATCH --error={0}.%j.out".format(jobid))
	if time_limit is not None: f_list.append("#SBATCH --time={0}".format(time_limit))
	f_list.append("#SBATCH --partition=m128")
	f_list.append("#SBATCH --cpus-per-task=20")
	f_list.append("")
	f_list.append("### MODULES ### ")
	f_list.append("module purge")
	f_list.append("module load FEBio/4.9")
	f_list.append("module list")
	f_list.append(" ")
	f_list.append("### JOB ### ")
	f_list.append("echo \"Running {0} on host $(hostname) in $(pwd)\"".format(jobid))
	f_list.append("echo \"Job start time is $(date).\"")
	# if optimization run optimization with file
	if opt_file is None:
		# optimization file not specified, run febio simulation
		f_list.append("srun febio4 {0} > febio4.job.out 2>&1".format(feb_file))
	else:
		# optimization file was specified, run febio with optimization
		f_list.append("srun febio4 -i {0} -s {1} > febio4.opt.out 2>&1".format(feb_file, opt_file))
	# otherwise, run normal febio simulation
	f_list.append("echo \"Job end time is $(date).\"")
	if del_feb: f_list.append("rm *.feb")
	if del_xplt: f_list.append("rm *.xplt")

	# write file
	with open(filepath, 'w') as file:
		for l in f_list:
			file.write(l + "\n")

## CLASSES
# none

## ARGUMENTS
# none

## SCRIPT
# none
