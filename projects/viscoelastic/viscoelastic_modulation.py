
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max Planck Institute for Colloids and Interfaces
## 2026.02.19

## FILENAME: projects/viscoelastic/viscoelastic_modulation.py
## PURPOSE: sysmteatically vary the viscoelastic parameters

## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from febio.job import Job


## PARAMETERS
# loading depth (mm)
loading_depth = 0.025
# relaxation time (s)
relaxation_time = 10000
# default first elastic modulus
default_E1_val = 1.129
# default second elastic modulus
default_E2_val = 6.
# default second viscosity
default_n2_val = 478.33


## METHODS
# none


## CLASSES
# none


## ARGUMENTS
# none


## SCRIPT
# create job
j = Job ("projects/", "ve-mod")

## add parameters
# loading depth is constant
j.add_constant_parameter(val = loading_depth, 
	key = 'LD', 
	xml = "Step/step[@id='1']/Rigid/rigid_bc[@name='tip_displacement']/value", 
	description = "loading_discplacement", 
	units = "mm",
	related = False)
# relaxation time is constant
j.add_constant_parameter(val = relaxation_time, 
	key = 'RT', 
	xml = None, 
	units = 'seconds', 
	description = 'loading-hold-time',
	related = False)
j.add_constant_parameter(val = 0.1, 
	key = 'RTss', 
	xml = "Step/step[@id='1']/Control/step_size", 
	units = None, 
	description = 'loading_step_size',
	related = False)
j.add_constant_parameter(val = "RT / RTss", 
	key = 'RTn', 
	xml = "Step/step[@id='1']/Control/time_steps", 
	units = None, 
	description = 'loading_number_steps', 
	related = True)

## establish the materials parameters
# the first elastic modulus varies
j.add_constant_parameter(val = default_E1_val, 
	key = "E1", 
	xml = None, 
	units = 'MPa', 
	description = "emod_1", 
	related = False)
# the second elastic modulus varies
j.add_constant_parameter(val = default_E2_val, 
	key = "E2", 
	xml = None, 
	units = 'MPa', 
	description = "emod_2", 
	related = False)
# the second viscosity varies
j.add_constant_parameter(val = default_n2_val, 
	key = "n2", 
	xml = None, 
	units = 'MPa * seconds', 
	description = "viscocity_2", 
	related = False)

# establish relationships between the each the viscoelastic constants and model parameters
j.add_constant_parameter(val = 'E1', key = 'G', xml = "Material/material[@id='1']/elastic/E", units = "MPa", description = "bulk_modulus", related = True)
j.add_constant_parameter(val = "E2 / E1", key = 'g1', xml = "Material/material[@id='1']/g1", units = None, description = "gamma_1", related = True)
j.add_constant_parameter(val = "n2 / E2", key = 't1', xml = "Material/material[@id='1']/t1", units = 'seconds', description = "tau_1", related = True)

