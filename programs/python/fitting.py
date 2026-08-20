
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2026.04.17

## FILENAME: projects/pv-fitting.py
## PURPOSE: comparing fit viscoelastic model to poroelastic simulation data.


## MODULES
# native
import sys, os, math
import copy
# conda
import pandas as pd
# local - febio
from febio.job import Job
from febio.sweep import Sweep
from febio.optimization import Optimization as Opt
from febio.simulation import Simulation
from febio.feb.model_file import ModelFile
from febio.feb.optimization_file import OptimizationFile as OptFile
from febio.slurm.submit import gen_slurm_script
from mod_parm.poroelastic_modulation import constant_bulk_modulus, constant_permeability, frequency_sweep
# local - plotting
from plot.figure import Figure
from plot.plot import gen_plot


## PARAMETERS
## SIMULATION PARAMETERS
# default amplitude during oscillation phase
default_oscillation_amplitude = 0.001
# default relxation time between starting the oscillation phase
default_relaxation_time = 10000
# default loading depth during initial loading
default_loading_depth = 0.005
# dictionary used to map length scale to febio model files
dict_feb = {'0.05': "z_0050", '0.08': "z_0080", '0.125': "z_0125", '0.2': "z_0200", '0.5': "z_0500", '1.0': "z_1000"}
# dictionary used for viscoelastic model files
# default feb model for viscoleastic simulations
default_feb_ve = "models/bend/bend_ve.feb"
# default feb model for poroelastic simulations
default_feb_pe = "models/bend/mesh/bend/bend_n15.feb"

## TODO :: depricated
## VISCOELASTIC MODEL
# small gamma - n gamma to test
n_small = 3
# small gamma - lowest gamma value to test
min_small_gamma = 0.1
# small gamma - highest gamma value to test
max_small_gamma = 1.
# large gamma - n  gamma to test
n_large = 3
# large gamma - lowest gamma value to test
min_large_gamma = 500.
# large gamma - highest gamma value to test
max_large_gamma = 5000.

# POROELASTIC MODEL
# permeabilityOptimization
default_perm = 0.0001
# elastic modulus
default_emod = 0.5
# length scale
default_z = 0.125
# sweep
default_n_period = 20

## VISCOELASTIC OPTIMIZATION
# path to objective function in feb file
obj_fun = "fem.rigidbody('Material2').Fz"
# amount by which the object function needs to be reduced to match the specified data
obj_tol = 1.0e-18
# gamma min, max, start, and name
gamma_min = 0.01
gamma_max = 1.
gamma_start = 0.1
gamma_name = "fem.material('Material1').g1"
# tau min, max, start, and name
tau_min = 1.
tau_max = 1000.
tau_start = 10.
tau_name = "fem.material('Material1').t1"
# elastic modulus min, max, start, and name
emod_min = 0.35
emod_max = 0.55
emod_start = 0.45
emod_name = "fem.material('Material1').elastic.E"

## TODO add rigid body file writting and pe and ve files

## METHODS
## TODO write linux script, how should job execute ..?
# start fitting job
def init_fit (jd = None, jn = None, emod = default_emod, perm = default_perm, z = default_z, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_freq = None, max_freq = None, norm = False, pe_feb = default_feb_pe, ve_feb = default_feb_ve):
    """ initialize the parameters and model files for fitting routine.

    a fitting routine contains three parts: first, data is generated from a
    poroelasic model for beam bending. The poroelastic model parameters are
    the elastic modulus (emod), the permeability (perm), and the length scale
    (z). the beam bending model has two parameters, which are the loading
    depth (load_depth - the depth the tip displaces the beam during the pre-
    stress phase) and the oscillation amplitude (osc_amp - the amplitude of
    oscillation during the oscillation phase).

    second: stress-strain data is taken from the final complete oscillation
    cycle of the poroelastic simulation. the data is provided to a viso-
    elastic beam bending model ('feb_ve') which has the exact same 
    dimensions. during optimization, the viscoelastic model parameters 
    are adjusted until the viscoelastic model reproduces the exact same
    stress-strain data as the poroelastic model. 

    third: the optimal parameters provided during optimization are validated
    by running one final simulation where the stress-strain data is reproduced.

    This is performed at several time scales to determine the how the optimal
    viscoelastic parameters change with time scale overtime.

    here, two time scales are selected (min_freq and max_freq), which are meant
    to be the boundaries (outer edges) of the range of timescales which will 
    be tested during fitting.
    
    Arguments:
    ----------
    jd : str
        path to location to save simulation directory
    jn : str
        name of simulation set
    emod : float (optional, default is 'default_emod')
        value of elastic modulus used in material model
    perm : float (optional, default is 'default_perm')
        value of permeability using in material model
    z : float (optional, default iis 'default_z')
        value of model length scale (must match length scale of feb model)
    osc_amp : float (optional, default is 'default_oscillation_amplitude')
        amplitude during oscillation phase
    relax_time : float (optional, default is 'default_relaxation_time')
        time between loading and oscillation phase
    load_depth : float (optional, default is 'default_loading_depth')
        depth of initial indentation before relxation and oscillation phases
    min_freq : float (optional)
        minimum oscilation period to test (if unspecified, minimum period is
        two orders of magnitude less than the resonant timescale)
    max_freq : float (optional)
        maximum oscillation period to test (if unspecified, maximum period is
        two orders of magnitude greater than the resonant timescale)
    norm : bool
        if 'True', time scales provided ('min_freq' and 'max_freq') are
        relative to the poroelastic timescale determined by the poroelastic
        model parameters
    pe_feb : str (optional, default is 'default_feb_pe')
        path to base poroelastic model to use for simulation set
    ve_feb : str (optional, default is 'default_feb_ve')
        path to base viscoelastic mode to use for simulation set

    Returns:
    -----------
    None
    """
    ## check arguments

    ## establish timescales 
    # estimate the critical period / frequency according to the poroelastic model parameters
    norm_fac = pow(emod, 1.) * pow(perm, 1.) * pow(z, -2.) # converts reduced time to real time according to poroelastic parameters
    crit_poro_freq = 30. * norm_fac # this is an emperically determined value

    # if frequency is unspecified in method call
    if max_freq is None: 
        # default max freq. is one order of magnitude 
        # greater than the critical freq.
        max_freq = crit_poro_freq * 10
    elif norm:
        # the max freq provided is reduce, move to real time
        max_freq = max_freq * norm_fac

    # if the min frequency is unspecified in the method call
    if min_freq is None: 
        # default min freq. is one order of magnitude 
        # less than the critical freq.
        min_freq = crit_poro_freq / 10
    elif norm:
        # if the minfreq was provided and normalized
        # move to real time
        min_freq = min_freq * norm_fac

    # convert frequency to period
    max_period = 2. * math.pi / min_freq # min_freq -> max_period
    min_period = 2. * math.pi / max_freq # max_freq -> min_period

    # notify the user of the estimate critical frequency
    print("NOTE :: fitting.init_fit() :: according to the poroelastic model parameters (e = {0:.2e} MPa, K = {1:.2e} mm^4/Ns, l = {2:.2e} mm), the resonant time scale will be {3:.2e} seconds or {4:.2e} Hz.".format(emod, perm, z, math.pi * 2. / crit_poro_freq, crit_poro_freq))
    if crit_poro_freq > (2. * math.pi):
        # notify the user if the resonant period is approaching the "speed limit"
        print("WARNING :: fitting.init_fit() :: the resonant frequency is approaching the resonant beam frequency ({0:.2e} seconds / {1:.2e} Hz).".format(0.1, math.pi * 2. * 10))

    ## create poroelastic job
    # set job parameters
    j_pe = Job("{0}{1}".format(jd, jn), 'pe')
    constant_bulk_modulus (job = j_pe, E_val = emod)
    constant_permeability (job = j_pe, K_val = perm)
    # here the loading depth and oscillation amplitude are scaled by the the implicit geometric length scale
    frequency_sweep (job = j_pe, 
        loading_depth = (z / default_z) * load_depth, 
        relaxation_time = relax_time, 
        oscillation_amplitude = (z / default_z) * osc_amp, 
        period_low = min_period, 
        period_high = max_period, 
        period_n = 2) # initially, only two simulations are started
    # generate job parameters
    # save
    j_pe.generate_parameters()
    j_pe.save_config()
    j_pe.save_parameters()
    # j_pe.generate_parameterized_models(m = "{0}{1}/pe/pe.feb", overwrite = True)
    # generate model
    m_pe = ModelFile (pe_feb)
    m_pe.save_model (saveto = "{0}{1}/pe/".format(jd, jn), saveas = "pe.feb".format(jn))

    ## create optimization job
    job_opt = Job("{0}{1}".format(jd, jn), 'opt')
    # write pe parameters to ve job
    # NOTE: here, elastic modulus, gamma and tau are varied during optimization, and therefore do not need to fixed
    frequency_sweep (job = job_opt,
                     loading_depth = (z / default_z) * load_depth,
                     relaxation_time = relax_time,
                     oscillation_amplitude = (z / default_z) * osc_amp,
                     period_low = min_period,
                     period_high = max_period,
                     period_n = 2) 
    # save parameters
    job_opt.generate_parameters()
    job_opt.save_config()
    job_opt.save_parameters()
    # generate model
    m_opt = ModelFile(ve_feb)
    m_opt.save_model(saveto = "{0}{1}/opt/".format(jd, jn), saveas = "opt.feb", overwrite = True)

    ## create viscoelastic job
    # viscoelatic job is exactly the same as the optimization job
    job_ve = copy.deepcopy(job_opt)
    job_ve.jn = 've'
    job_ve.generate_parameters()
    job_ve.save_config()
    job_ve.save_parameters()
    # the viscoelastic model is exactly the same as the optimization model
    m_opt.save_model(saveto = "{0}{1}/ve/".format(jd, jn), saveas = "ve.feb", overwrite = True)

def update_fit (jd = None, jn = None, overwrite = True):
    """ update fit job directories based on their status.
    
    Arguments:
    ----------
    jd : str
        path to location to save simulation directory
    jn : str
        name of simulation set
    overwrite : bool
        boolean that determines if existing files are overwritten

    Parameters:
    -----------
    None
    """
    ## esablish jobs, models
    ## TODO update results for each job
    j_pe = Job ("{0}{1}".format(jd, jn), 'pe')
    j_op = Opt ("{0}{1}".format(jd, jn), 'opt')
    j_ve = Job ("{0}{1}".format(jd, jn), 've')
    m_pe = ModelFile ("{0}{1}/pe/pe.feb".format(jd, jn))
    m_op = ModelFile ("{0}{1}/opt/opt.feb".format(jd, jn))
    m_ve = ModelFile ("{0}{1}/ve/ve.feb".format(jd, jn))

    # used for job naming
    z_int = 0
    for l in list(dict_feb.keys()):
        if jn == dict_feb[l]:
            z_int = list(dict_feb.keys()).index(l) + 1

    ## check the progression of each job through the fitting routines
    # use poroelastic job hirearchy as Ansatz for 'opt' and 've' jobs
    for i in range(1, j_pe.get_sim_num() + 1):
        # establish job directories
        dir_pe = "{0}{1}/pe/{2}".format(jd, jn, j_pe.df_parm.iloc[i-1]['path'])
        dir_op = "{0}{1}/opt/{2}".format(jd, jn, j_pe.df_parm.iloc[i-1]['path'])
        dir_ve = "{0}{1}/ve/{2}".format(jd, jn, j_pe.df_parm.iloc[i-1]['path'])

        # POROELASTIC JOB
        # check if the job directory exists
        if not os.path.exists(dir_pe):
            # if it does not exist, make the directory
            os.makedirs(dir_pe)
            # parameterize model, save to simulation directory
            j_pe.parameterize_model(m = m_pe, n = i).save_model(saveto = dir_pe, saveas = "pe-{0}.feb".format(i), overwrite = overwrite)
            # write slurm file
            jobid = "p{0}".format(i)
            if z_int > 0: jobid = "z{0}-p{1}".format(z_int, i)
            gen_slurm_script (filepath = "{0}pe-{1}.slurm.sub".format(dir_pe, i),
                jobid = jobid,
                feb_file = "{0}pe-{1}.feb".format(j_pe.get_simulation(i).get_simulation_path(), i), 
                time_limit = "30:00", # twenty minute time limit
                del_feb = True, 
                del_xplt = True)
            continue # move to the next integer
        else:
            # the simulation directory exists, is the simulation done?
            if not os.path.exists(dir_pe + "febio4.job.out"): continue
            elif not os.path.exists(dir_pe + "febio4.out.csv"):
                # in this case, the outfile exists by the csv file does not
                # attempt to parse the results from the logfile
                success = j_pe.get_simulation(i).parse_logfile()
                if not success: continue # simulation not completed yet
                # results where written and ready for optimization phase

        ## OPTIMIZATIONS JOB
        # check if the directory exists
        if not os.path.exists(dir_op):
            # if the  does not, make the directory
            os.makedirs(dir_op)

            # set job id
            jobid = "o{0}".format(i)
            if z_int > 0: jobid = "z{0}-o{1}".format(z_int, i)
            
            # get the simulation stress-strain data from the poroelastic file
            s_pe = j_pe.get_simulation(i)
            f_d = s_pe.get_displacement_force_lag()
            f_d['f'] = -1 * f_d['f'] # transform force to negative value
            
            # generate the feb file
            j_ve.parameterize_model(m = m_op, n = i).save_model(saveto = dir_op, saveas = "{0}.feb".format(jobid), overwrite = overwrite)

            # generate optimization file
            o = OptFile()
            # add optimizable parameters
            ## HERE check for neighbors which are finished already
            o.add_parameters(min_val = gamma_min, max_val = gamma_max, start_val = gamma_start, name = gamma_name) # relaxation constant
            o.add_parameters(min_val = tau_min, max_val = tau_max, start_val = tau_start, name = tau_name) # time constant
            # in the case of elasticity, the bounds should be outside the average value
            o.add_parameters(min_val = emod_min, max_val = emod_max, start_val = emod_start, name = emod_name) # bulk elastic modulus
            o.set_optimization_function(name = obj_fun) # optimization function
            o.set_objective_tolerance(value = obj_tol) # objective tolerance
            o.add_data_list(x_list = f_d['t'].tolist(), y_list = f_d['f'].to_list()) # add optimization data (from poroelastic simulation)
            o.save_optimization_file(filepath = "{0}{1}.opt".format(dir_op, jobid)) # write the optimization file to the simulation directory

            # write slurm file
            gen_slurm_script (filepath = "{0}{1}.slurm.sub".format(dir_op, jobid),
                jobid = jobid,
                feb_file = "{0}{1}.feb".format(dir_op, jobid), 
                opt_file =  "{0}{1}.opt".format(dir_op, jobid),
                time_limit = "2-00:00:00", # two day time limit
                del_feb = True)
            # move to the next integer
            continue
        else:
            # the job directory does exist, check if optimization is finished
            # attempt to generate optimized model
            m_o = j_op.generate_optimized_model (m = m_ve, n = i)
            # if the method returns None type, optimization is not done
            if m_o is None: continue

        ## VISCOELASTIC JOB
        # does the directory exist?
        # if not, make the directory
        # generate the file file
        # generate the slurm submission file
        # if the directory exists, is the job done?
        # if it does exist, is the job done?
        # if it is, move on to ANALYSIS

        ## ANALYSIS
        # update the results

    pass

# add fitting at selected time scale to job
def add_fit_timescale ():
    """ add timescale to fitting job.
    
    Arguments:
    ----------
    None

    Parameters:
    -----------
    None
    """
    # assume time scale exists between two points which have already run 
    # generate an optization file which contains the correct bounds
    pass

def update_step_two (jd = None, jn = None):
    """ iteratively implements optimization and feb files.

    Arguments:
    ----------
    None

    Returns:
    --------
    None
    """
    # check that the path to optimization exists
    # check what has been completed so far
    # first: run only the ends
    # second: fill 
    pass

# first step in fitting sequence
def step_one (jd = None, jn = None, emod = default_emod, perm = default_perm, z = default_z, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, n_frequency = default_n_period, min_frequency = None, max_frequency = None, feb_file = default_feb_pe, norm = False):
    """ first step in fitting sequence.

    during the first step, the a poroelastic model is generated, and the resonant
    properties are determined over a range of time scales.

    Arguments:
    ----------
    jd : str
        path to location to save simulation directory
    jn : str
        name of simulation set
    emod : float (optional, default is 'default_emod')
        value of elastic modulus used in material model
    perm : float (optional, default is 'default_perm')
        value of permeability using in material model
    z : float (optional, default iis 'default_z')
        value of model length scale (must match length scale of feb model)
    osc_amp : float (optional, default is 'default_oscillation_amplitude')
        amplitude during oscillation phase
    relax_time : float (optional, default is 'default_relaxation_time')
        time between loading and oscillation phase
    load_depth : float (optional, default is 'default_loading_depth')
        depth of initial indentation before relxation and oscillation phases
    n_freqyebct : int (optional, default is 'default_n_period')
        number of unique frequency values to test
    min_frequency : float (optional)
        minimum oscilation period to test (if unspecified, minimum period is
        two orders of magnitude less than the resonant timescale)
    max_frequency : float (optional)
        maximum oscillation period to test (if unspecified, maximum period is
        two orders of magnitude greater than the resonant timescale)
    feb_file : str (optional, default is 'default_feb_pe')
        path to base poroelastic model to use for simulation set
    norm : bool
        if 'True', time scales are selected relative to normalized poroelastic
        timescale

    Returns:
    --------
    None
    """
    ## determine timescales
    # estimate the critical period / frequency according to the poroelastic model parameters
    norm_fac = pow(emod, 1.) * pow(perm, 1.) * pow(z, -2.) # converts reduced time to real time according to poroelastic parameters
    crit_poro_freq = 30. * norm_fac # this is an emperically determined value

    # if frequency is unspecified in method call
    if max_frequency is None: 
        # default max freq. is one order of magnitude 
        # greater than the critical freq.
        max_frequency = crit_poro_freq * 10
    elif norm:
        # the max freq provided is reduce, move to real time
        max_frequency = max_frequency * norm_fac

    # if the min frequency is unspecified in the method call
    if min_frequency is None: 
        # default min freq. is one order of magnitude 
        # less than the critical freq.
        min_frequency = crit_poro_freq / 10
    elif norm:
        # if the minfreq was provided and normalized
        # move to real time
        min_frequency = min_frequency * norm_fac

    # convert frequency to period
    max_period = 2. * math.pi / min_frequency # min_frequency -> max_period
    min_period = 2. * math.pi / max_frequency # max_frequency -> min_period

    # notify the user of the estimate critical frequency
    print("NOTE :: fitting.step_one() :: according to the poroelastic model parameters (e = {0:.2e} MPa, K = {1:.2e} mm^4/Ns, l = {2:.2e} mm), the resonant time scale will be {4:.2e} seconds or {5:.2e} Hz.".format(emod, perm, z, math.pi * 2. / crit_poro_freq, crit_poro_freq))
    if crit_poro_freq > (2. * math.pi):
        # notify the user if the resonant period is approaching the "speed limit"
        print("WARNING :: fitting.step_one() :: the resonant frequency is approaching the resonant beam frequency ({0:.2e} seconds / {1:.2e} Hz).".format(0.1, math.pi * 2. * 10))

    # load modules
    # NOTE :: these methods have the same names as those for viscoleasticity, so they are loaded locally rather than globally
    from poroelastic_modulation import constant_bulk_modulus, constant_permeability, frequency_sweep

    # set job parameters
    j = Job("{0}{1}".format(jd, jn), 'pe')
    constant_bulk_modulus (job = j, E_val = emod)
    constant_permeability (job = j, K_val = perm)
    # here the loading depth and oscillation amplitude are scaled by the the implicit geometric length scale
    frequency_sweep (job = j, loading_depth = (z / default_z) * load_depth, relaxation_time = relax_time, oscillation_amplitude = (z / default_z) * osc_amp, period_low = min_period, period_high = max_period, period_n = n_period)

    # load model
    m = ModelFile (feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/pe/".format(jd, jn), saveas = "pe.feb".format(jn))
    j.generate_parameterized_models(m = "{0}{1}/pe/pe.feb", overwrite = True)

# second step in fitting sequence
def step_two (jd = None, jn = None, feb_file = default_feb_ve):
    """ second step in fitting sequence, once first step is finished.

    during the second step, a viscoelastic model is fit to the poroelastic
    stress-strain data at each time scale.

    Arguments:
    ----------
    jd : str
        path to directory which will contain job
    jn : str
        name of job in job directory
    feb_file : str
        path to viscoelastic model

    Results:
    --------
    None
    """
    # check that the poroelastic simulations exist, loop through each one
    if not os.path.exists("{0}/{1}/pe".format(jd, jn)):
        print("ERROR :: fitting.step_two() :: Unable to find set of previous poroelastic simulations (''). Unable to perform next step of viscoelastic fitting..")
        return

    # import methods from viscoleastic mod file
    # NOTE :: these methods have the same name as those in the proelastic mod file, so they are loaded locally (not globally)
    # from viscoelastic_modulation import constant_bulk_modulus, constant_tau, constant_gamma, frequency_sweep

    # create viscoelastic job and model, save parameters
    job_ve = Job("{0}{1}".format(jd, jn), 'opt')
    # NOTE: it is important that parameters are exactly the same as the poroelastic model.
    job_pe = Job("{0}{1}".format(jd, jn), 'pe')
    # write pe parameters to ve job
    # NOTE: here, elastic modulus, gamma and tau are varied during optimization, and therefore do not need to fixed
    min_period, max_period = job_pe.get_variable_parameter_range(key = 'OT')
    frequency_sweep (job = job_ve,
                     loading_depth = job_pe.get_constant_parameter_value(key = 'LD'),
                     relaxation_time = job_pe.get_constant_parameter_value(key = 'RT'),
                     oscillation_amplitude = job_pe.get_constant_parameter_value(key = 'OA'),
                     period_low = min_period,
                     period_high = max_period,
                     period_n = job_pe.get_variable_parameter_number(key = 'OT'))

    m_ve = ModelFile(feb_file)
    job_ve.generate_parameters()
    job_ve.save_config()
    job_ve.save_parameters()
    m_ve.save_model(saveto = "{0}{1}/opt/".format(jd, jn), saveas = "opt.feb", overwrite = True)

    # generate simulation specific models# write the stress-strain data to the simulation file just for viewing
    job_ve.generate_parameterized_models(m = "{0}{1}/opt/opt.feb".format(jd, jn), overwrite = True)

    # loop through each poroelastic simulation, generation viscoelastic optimization
    for i in range(1, job_pe.get_sim_num() + 1):
        # check the that simulation finished
        # open each simulation, save the final stress-strain, hysteresis data
        s_pe = job_pe.get_simulation(i)
        s_ve = job_ve.get_simulation(i)
        if not os.path.exists(s_ve.get_simulation_path()): os.makedirs(s_ve.get_simulation_path())
        f_d = s_pe.get_displacement_force_lag ()
        # save force displacement lag to simulation directory
        s_pe.show_displacement_force_lag (norm = True, save = True, show = False)
        f_d['f'] = -1 * f_d['f'] # transform force to negative value

        ## generate optimization job, add mandatory defaults
        o = OptFile()
        # add optimization parameters
        o.add_parameters(min_val = gamma_min, max_val = gamma_max, start_val = gamma_start, name = gamma_name)
        o.add_parameters(min_val = tau_min, max_val = tau_max, start_val = tau_start, name = tau_name)
        o.add_parameters(min_val = emod_min, max_val = emod_max, start_val = emod_start, name = emod_name)
        # add optimization function
        o.set_optimization_function(name = obj_fun)
        # set the objective function tolerance
        o.set_objective_tolerance(value = obj_tol)
        # add optimization data (from poroelastic simulation)
        o.add_data_list(x_list = f_d['t'].tolist(), y_list = f_d['f'].to_list())
        # append cyclic data to optimization file to the viscoelastic job with the poroelastic data
        # here, the parameters for the poroelastic and viscoelastic jobs should be exactly the same
        o.save_optimization_file(filepath = "{0}opt-{2}.opt".format(s_ve.get_simulation_path(), jn, i))

# third step in fitting sequence
def step_three (jd = None, jn = None, feb_file = default_feb_ve, overwrite = False):
    """ third step is fitting sequence, once the second step is finished.

    during the third step, the optimal viscoelastic parameters are parsed
    from each optimization model. the optimized model is rerun to confirm
    the validity of the optimized parameters relative to the poroelastic
    model.

    Arguments:
    ----------
    jd : str
        path to directory which will contain job
    jn : str
        name of job in job directory
    feb_file : str
        path to viscoelastic model
    overwrite : bool (optional, default is 'False')
        overwrite existing results, if requested

    Results:
    --------
    None
    """
    # check that the previous step was completed
    if not os.path.exists("{0}{1}/opt".format(jd, jn)):
        # through error, exit
        print("ERROR :: step_three() :: directory '' does not exist, step two has not yet been completed.")
        return

    # open optimization jobs, parse results
    job_ve = Job("{0}{1}".format(jd, jn), "opt") # used for generating parameters
    o = Opt("{0}{1}/".format(jd, jn), "opt") # used get th results from optimization
    m = ModelFile(feb_file)
    df_opt_res = o.get_optimization_results(save = True, overwrite = overwrite)

    # re-write the same parameters from the optimization job a new directory
    job_ve.jn = "ve" # rename the job
    job_ve.generate_parameters()
    job_ve.save_config()
    job_ve.save_parameters()
    m.save_model(saveto = "{0}{1}/ve/".format(jd, jn), saveas = "ve.feb")

    # loop through each set of optimization runs,
    # generated optimized model and write to the new viscoelasticity job directory.
    for idx, row in df_opt_res.iterrows():
        # generate and save the visco elastic model with optimized parameters from step two
        # here, the parameters, directories for 'job_ve' and 'o' are the same
        m_opt = o.generate_optimized_model(m = feb_file, n = row['n'])
        if m_opt is None: 
            os.makedirs("{0}{1}/ve/{2}".format(jd, jn, row['path'])) # make path
            continue # skip if method returns 'None' type
        m_opt.save_model(saveto = "{0}{1}/ve/{2}".format(jd, jn, row['path']), saveas = "ve-{0}.feb".format(row['n']), overwrite = overwrite)

# fourth step in fitting sequence
def step_four (jd, jn, show = True, save = False):
    """ fourth step in fitting sequence, once the third step is finished.

    during the fourth step, the optimizal parameters for the viscoelastic
    fitting are plotted against the timescale. The properties of the
    simulated material (e.g. loss modulus) are compared for the poroelastic
    model and the optimized viscoelastic model.

    Arguments:
    ----------
    jd : str
        path to the job directory
    jn : str
        name of job in job directory
    show : bool
        if 'True', displays all images to UI.
    save : bool
        if 'True', saves all images and data to job directory.

    Results:
    --------
    None
    """
    # get the results for the viscoelastic and poroelastic jobs
    sp = Sweep("{0}{1}/".format(jd, jn), "pe")
    sv = Sweep("{0}{1}/".format(jd, jn), "ve")
    savedir = "{0}{1}/results/".format(jd, jn)

    # get the number of cycles that were performed
    n_cyc = sp.get_simulation(1).get_number_oscillation_cycles()
    # reduce the number of cycles by two
    n_cyc -= 2

    ## poro and viscoelastic labels
    label_pe = "Poroelastic Data"
    label_ve = "Viscoelastic Fit"

    ## TODO plot the optimized parameters against frequency
    # open the optimization job
    o = Opt(jd = "{0}{1}/".format(jd, jn), jn = "opt")
    o.get_optimization_results(save = True, overwrite = True)
    o.show_optimization_results(save = save, show = show, xaxis_key = 'OT')

    ## between poroelasticity and viscoelasticity, compare the following properties
    # resonant amplitude (-dW)
    fig = Figure()
    fig.append_df(df = sp.get_hysteresis_work(), xcol = 'f', ycol = n_cyc, label = label_pe)
    fig.append_df(df = sv.get_hysteresis_work(), xcol = 'f', ycol = n_cyc, label = label_ve)
    fig.set_axis_scale(akey = 'x', log = True)
    fig.set_axis_label(akey = 'x', l = "Frequency (Hz, $2 \\pi T^{{-1}}$)")
    fig.set_axis_label(akey = 'y', l = "Dissipated Energy (J)")
    fig.set_saveas(savedir = savedir, filename = "sweep")
    if save: fig.save_data()
    gen_plot(fig, save = save, show = show)

    # phase shift (delta)
    fig = Figure()
    fig.append_df(df = sp.get_phase_shift(), xcol = 'f', ycol = n_cyc, label = label_pe)
    fig.append_df(df = sv.get_phase_shift(), xcol = 'f', ycol = n_cyc, label = label_ve)
    fig.set_axis_scale(akey = 'x', log = True)
    fig.set_axis_label(akey = 'x', l = "Frequency (Hz, $2 \\pi T^{{-1}}$)")
    fig.set_axis_label(akey = 'y', l = "Phase lag (degrees, $^{{\\circ}}$)")
    fig.set_saveas(savedir = savedir, filename = "phase-lag")
    if save: fig.save_data()
    gen_plot(fig, save = save, show = show)

    # dynamic modulus (G*)
    fig = Figure()
    fig.append_df(df = sp.get_dynamic_modulus(), xcol = 'f', ycol = n_cyc, label = label_pe)
    fig.append_df(df = sv.get_dynamic_modulus(), xcol = 'f', ycol = n_cyc, label = label_ve)
    fig.set_axis_scale(akey = 'x', log = True)
    fig.set_axis_label(akey = 'x', l = "Frequency (Hz, $2 \\pi T^{{-1}}$)")
    fig.set_axis_label(akey = 'y', l = "Dynamic Modulus ($Pa$)")
    fig.set_saveas(savedir = savedir, filename = "dynamic-modulus")
    if save: fig.save_data()
    gen_plot(fig, save = save, show = show)

    # loss modulus (G'')
    fig = Figure()
    fig.append_df(df = sp.get_loss_modulus(), xcol = 'f', ycol = n_cyc, label = label_pe)
    fig.append_df(df = sv.get_loss_modulus(), xcol = 'f', ycol = n_cyc, label = label_ve)
    fig.set_axis_scale(akey = 'x', log = True)
    fig.set_axis_label(akey = 'x', l = "Frequency (Hz, $2 \\pi T^{{-1}}$)")
    fig.set_axis_label(akey = 'y', l = "Loss Modulus ($Pa$)")
    fig.set_saveas(savedir = savedir, filename = "loss-modulus")
    if save: fig.save_data()
    gen_plot(fig, save = save, show = show)

    # storage modulus (G')
    fig = Figure()
    fig.append_df(df = sp.get_storage_modulus(), xcol = 'f', ycol = n_cyc, label = label_pe)
    fig.append_df(df = sv.get_storage_modulus(), xcol = 'f', ycol = n_cyc, label = label_ve)
    fig.set_axis_scale(akey = 'x', log = True)
    fig.set_axis_label(akey = 'x', l = "Frequency (Hz, $2 \\pi T^{{-1}}$)")
    fig.set_axis_label(akey = 'y', l = "Storage Modulus ($Pa$)")
    fig.set_saveas(savedir = savedir, filename = "storage-modulus")
    if save: fig.save_data()
    gen_plot(fig, save = save, show = show)

    ## for each oscillatiory simulation
    # compare the viscoleastic / poroelastic model stress curves ..
    for i in range(1, sv.get_sim_num() + 1):
        sim_ve = sv.get_simulation(i)
        sim_pe = sp.get_simulation(i)

        # TODO can I adjust the markers so that the fitting is more obvious?
        # in time
        fig = Figure()
        # append data
        # NOTE in theory, the poroelastic and viscoelastic strain curves are exactly the same
        fig.append_df(df = sim_pe.get_displacement_force_lag(cycle = n_cyc), xcol = 't', ycol = 'f', label = label_pe)
        fig.append_df(df = sim_ve.get_displacement_force_lag(cycle = n_cyc), xcol = 't', ycol = 'f', label = label_ve)
        # set markers
        fig.set_marker(ival = label_pe, marker = 'o')
        fig.set_marker(ival = label_ve, marker = 'x')
        # add title
        fig.set_title_label(l = "$f = {0:.2e} Hz$, $T = {1:.2e} s$".format(sim_ve.get_oscillation_phase_frequency(), sim_ve.get_oscillation_phase_period()))
        fig.set_subtitle_label(l = "({0})".format(sim_ve.get_key_value('id')))
        # set axis labels
        fig.set_axis_label(akey = 'x', l = "Simulation Time (seconds)")
        fig.set_axis_label(akey = 'y', l = "Force against Tip (mN)") # TODO double check these units
        # save data
        if save:
            fig.set_saveas(savedir = savedir + "cycles/", filename = "{0}-stress".format(sim_ve.get_key_value('id')))
            fig.save_data()
            # show figure
            gen_plot(fig, show = False, save = save)

        # hysteresis loop
        fig = Figure()
        # append data
        fig.append_df(df = sim_pe.get_displacement_force_lag(cycle = n_cyc), xcol = 'x', ycol = 'f', label = label_pe)
        fig.append_df(df = sim_ve.get_displacement_force_lag(cycle = n_cyc), xcol = 'x', ycol = 'f', label = label_ve)
        # set markers
        fig.set_marker(ival = label_ve, marker = 'x')
        fig.set_marker(ival = label_pe, marker = 'o')
        # add title
        fig.set_title_label(l = "$f = {0:.2e} Hz$, $T = {1:.2e} s$".format(sim_ve.get_oscillation_phase_frequency(), sim_ve.get_oscillation_phase_period()))
        fig.set_subtitle_label(l = "({0})".format(sim_ve.get_key_value('id')))
        # set axis labels
        fig.set_axis_label(akey = 'x', l = "Tip Displacement (mm)")
        fig.set_axis_label(akey = 'y', l = "Force against Tip (mN)") # TODO double check these units
        # save data
        if save:
            fig.set_saveas(savedir = savedir + "cycles/", filename = "{0}-lj".format(sim_ve.get_key_value('id')))
            fig.save_data()
            # show figure
            gen_plot(fig, show = False, save = save)

if __name__ == "__main__":

    ## ARGUMENTS
    # first argument: path to directory that contains fitting simulations
    dir_path = sys.argv[1]

    ## SCRIPT
    # loop through each length scale directory
    for l in list(dict_feb.keys()):
        # location of model files for corresponding length scale
        feb_pe = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[l] + "/bend_pe.feb"
        feb_ve = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[l] + "/bend_ve.feb"

        # does the simulation directory exist for the length scale?
        if not os.path.exists(dir_path + dict_feb[l]):
            # if not make the directory and generate the simulation file structure
            init_fit (jd = dir_path, jn = dict_feb[l], z = float(l), pe_feb = feb_pe, ve_feb = feb_ve)

        # update the directory
        update_fit (jd = dir_path, jn = dict_feb[l])
