
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max Planck Institute for Colloids and Interfaces
## 2026.02.19

## FILENAME: projects/poroelastic/poroelastic_modulation.py
## PURPOSE: sysmteatically vary the poroelastic parameters, extract pressure and stress data

## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from febio.job import Job
from febio.feb.model import Model


## PARAMETERS
# model file
feb_model = 'models/uniax/comp.feb'
# absolute path to remote data
rmt_dir = "/mnt/data/bgfs1/dorsey/biphasic_simulations/"
# number of oscillation cycles
n_cycles = 10
# number of steps per cycle
n_steps = 60
# loading depth (mm), unless otherwise specified
default_loading_depth = 0.005
# relaxation time (s), unless otherwise specified
default_relaxation_time = 10000
# oscillation amplitude (mm), unless otherwise specified
default_oscillation_amplitude = 0.001


## METHODS
# none

## CLASSES
# none


if __name__ == "__main__":

	## ARGUMENTS
	# first argument: job directory
	jd = sys.argv[1]
	# second argument: job id
	jn = sys.argv[2]

	## TODO add model file to job, generate dictionaries and write feb file

	## SCRIPT

	## TODO import base model, add log data
	m = Model(feb_model)
	m.add_element_data_to_logfile_output(elements = [1, 226, 451, 676, 901, 1126, 1351, 1576, 1601, 2026, 2251, 2576, 2701, 2926, 3151, 3376, 3601, 3826, 4051, 4276, 4501, 4726, 4951, 5176, 5401, 5626, 5851, 6076, 6301, 6526], properties = ['p', 'effective stress'], delim = ",", filename = 'elm.dat')
	m.save_model(filename = "models/uniax/comp_ex.feb", overwrite = True)
	exit()
	# create job
	j = Job (jd, jn)

	# generate parameter file
	if not j.has_parameters():
		j.generate_parameters()

	# save
	j.save_config()
	j.save_parameters()

	# generate
	# j.save_model()
	# j.generate_simulations()

