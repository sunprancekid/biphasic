
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
from febio.job import Job, gen_log_scale_range
from febio.sweep import Sweep
from febio.optimization import Optimization as Opt
from febio.simulation import Simulation
from febio.feb.model_file import ModelFile
from febio.feb.optimization_file import OptimizationFile as OptFile
from febio.slurm.submit import gen_slurm_script
from mod_parm.poroelastic_modulation import constant_bulk_modulus, constant_permeability, frequency_sweep
from util.smoothie import log2lin, lin2log
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

# POROELASTIC MODEL
# permeabilityOptimization
default_perm = 0.0001
# elastic modulus
default_emod = 0.5
# length scale
default_z = 0.125
# sweep
default_n_period = 20

## PERMEABILITY MODULATION
# default minimum permeability to test
default_permeability_low = 0.00001
# default maximum permeability to test
default_permeability_high = 0.001
# default number of permerabilities to test
default_permeability_n = 5

## ELASTIC MODULUS MODULTATION
# default minimum elastic modulus to test
default_emod_low = 0.05
# default maximum elastic modulus to test
default_emod_high = 5.
# default number of elastic moduli to test
default_emod_n = 5

## VISCOELASTIC OPTIMIZATION
# path to objective function in feb file
obj_fun = "fem.rigidbody('Material2').Fz"
# amount by which the object function needs to be reduced to match the specified data
obj_tol = 1.0e-18
# gamma min, max, start, and name
gamma_min = 0.0000001
gamma_max = 100.
gamma_start = 0.1
gamma_name = "fem.material('Material1').g1"
gamma_xml = "Material/material[@id='1']/g1"
# tau min, max, start, and name
tau_min = 0.01
tau_max = 100000.
tau_start = 10.
tau_name = "fem.material('Material1').t1"
tau_xml = "Material/material[@id='1']/t1"
# elastic modulus min, max, start, and name
emod_min = 0.35
emod_max = 0.55
emod_start = 0.45
emod_name = "fem.material('Material1').elastic.E"
emod_xml = "Material/material[@id='1']/elastic/E"

## METHODS
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
        # default max freq. is two orders of magnitude 
        # greater than the critical freq.
        max_freq = crit_poro_freq * 100
    elif norm:
        # the max freq provided is reduce, move to real time
        max_freq = max_freq * norm_fac

    # if the min frequency is unspecified in the method call
    if min_freq is None: 
        # default min freq. is two orders of magnitude 
        # less than the critical freq.
        min_freq = crit_poro_freq / 100
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

def vary_fit_perm (jd = None, k_lo = default_permeability_low, k_hi = default_permeability_high, k_n = default_permeability_n, emod = default_emod, z = default_z, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_freq = None, max_freq = None, norm = False):
    """ initialize a series of fitting where the permeability varies.

    Arguments:
    ----------
    jd : str
    k_lo : float
    k_hi : float
    k_n : int
    emod : float
    z : float
    osc_amp : float
    relax_time : float
    load_depth : float
    min_freq : float
    max_freq : float
    norm : bool

    Returns:
    --------
    bool
        'True' if successful, else 'False'
    """

    ## check method arguments
    # jd must be specified
    if jd is None:
        print("ERROR :: fitting.vary_fit_perm() :: job directory 'jd' must be specified.")
        return False
    # check that z exists in the feb dictionary for poroelastic and viscoelastic jobs
    z_str = str(z)
    if z_str not in list(dict_feb.keys()):
        print("ERROR :: fitting.vary_fit_perm() :: length scale value 'z' ('') does not correspond to any values in 'dict_feb'.")
        return False
    #

    # loop through k, initialize fitting jobs
    k_list = gen_log_scale_range(n = k_n, min_val = k_lo, max_val = k_hi)
    for i in range(len(k_list)):
        # establish the permeability value
        k_val = k_list[i]
        # get the viscoelastic and poroelastic models corresponding to the length scale
        pe_feb = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[z_str] + "/bend_pe.feb"
        ve_feb = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[z_str] + "/bend_ve.feb"
        # init fit
        ## TODO add length scale as constant parameter to pe config.
        init_fit(jd = jd, jn = "k_{0}".format(i+1), emod = emod, perm = k_val, z = z, osc_amp = osc_amp, relax_time = relax_time, load_depth = load_depth, min_freq = min_freq, max_freq = max_freq, norm = norm, pe_feb = pe_feb, ve_feb = ve_feb)

def vary_fit_elastic_modulus (jd = None, e_lo = default_emod_low, e_hi = default_emod_high, e_n = default_emod_n, perm = default_perm, z = default_z, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_freq = None, max_freq = None, norm = False):
    """ initialize a series of fitting experiments where the elastic modulus varies.

    Arguments:
    ----------
    jd : str
        path to directory that contains job.
    e_lo : float
        lowest elastic modulus value to test
    e_hi : float
        highest elastic modulus value to test
    e_n : int
        number of different elastic moduli to test, including the highest and lowest
    perm : float
        constant permeability assigned to the biphasic materil.
    z : float
        length scale to used, correspond to model
    osc_amp : float
        oscillation amplitude assigned after pre-loading
    relax_time : float
        length of time (seconds) the material is allowed to relax
    load_depth : float
        depth of pre-stress loading
    min_freq : float
        lowest frequency to test
    max_freq : float
        highest frequency to test
    norm : bool
        determines if the frequency values passed to method are already normalized

    Returns:
    --------
    bool
        'True' if operation was successful, else 'False'
    """
    ## check method arguments
    # jd must be specified
    if jd is None:
        print("ERROR :: fitting.vary_fit_elastic_modulus() :: job directory 'jd' must be specified.")
        return False
    # check that z exists in the feb dictionary for poroelastic and viscoelastic jobs
    z_str = str(z)
    if z_str not in list(dict_feb.keys()):
        print("ERROR :: fitting.vary_fit_elastic_modulus() :: length scale value 'z' ('') does not correspond to any values in 'dict_feb'.")
        return False
    #

    # loop through k, initialize fitting jobs
    e_list = gen_log_scale_range(n = e_n, min_val = e_lo, max_val = e_hi)
    for i in range(len(e_list)):
        # establish the permeability value
        e_val = e_list[i]
        print(e_val)
        # get the viscoelastic and poroelastic models corresponding to the length scale
        pe_feb = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[z_str] + "/bend_pe.feb"
        ve_feb = "/home/mpikg/dorsey/Desktop/biphasic/models/bend/scale/" + dict_feb[z_str] + "/bend_ve.feb"
        # init fit
        ## TODO add length scale as constant parameter to pe config.
        init_fit(jd = jd, jn = "e_{0}".format(i+1), emod = e_val, perm = perm, z = z, osc_amp = osc_amp, relax_time = relax_time, load_depth = load_depth, min_freq = min_freq, max_freq = max_freq, norm = norm, pe_feb = pe_feb, ve_feb = ve_feb)


def update_fit (jd = None, jn = None, overwrite = True, force = False, z_int = None):
    """ update fit job directories based on their status.
    
    Arguments:
    ----------
    jd : str
        path to location to save simulation directory
    jn : str
        name of simulation set
    overwrite : bool
        boolean that determines if existing files are overwritten
    force : bool
        during optimization, force bulk modulus and gamma to take specific values

    Returns:
    --------
    None
    """
    ## esablish jobs, models
    ## TODO update results for each job
    j_pe = Job ("{0}{1}/".format(jd, jn), 'pe')
    j_op = Opt ("{0}{1}/".format(jd, jn), 'opt')
    j_ve = Job ("{0}{1}/".format(jd, jn), 've')
    m_pe = ModelFile ("{0}{1}/pe/pe.feb".format(jd, jn))
    m_op = ModelFile ("{0}{1}/opt/opt.feb".format(jd, jn))
    m_ve = ModelFile ("{0}{1}/ve/ve.feb".format(jd, jn))

    # used for job naming
    if z_int is None:
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
        n = j_pe.df_parm.iloc[i-1]['n']

        ## update poroelastic routine
        # if method returns false, poroelastic simulation has not completed yet
        if not (update_poroelastic(jd = jd, jn = jn, i = i, overwrite = overwrite, z_int = z_int)): continue

        ## update optimization routine
        if not force:
            # if method results 'False', optimization simulation has not completed yet
            if not (update_optimization(jd = jd, jn = jn, i = i, overwrite = overwrite, z_int = z_int)): continue
        else:
            # parse bulk modulus and relaxation constant from other jobs
            continue

        continue

        ## VISCOELASTIC JOB
        # if the method returns False, viscoelastic simulation has not compeleted yet
        if not (update_viscoelastic(jd = jd, jn = jn, i = i, overwrite = overwrite, z_int = z_int)): continue

        ## ANALYSIS
        # update the results

# add fitting at selected time scale to job
def add_fit_timescales (jd = None, jn = None):
    """ add timescaled to fitting job.
    
    Arguments:
    ----------
    jd : str
        path to directory containing 'fit' job
    jn : str
        name of job in directory

    Returns:
    --------
    bool
        'True' if operation was successful, else 'False'
    """
    # get directories, model files for job
    j_pe = Job ("{0}{1}/".format(jd, jn), 'pe')
    j_op = Opt ("{0}{1}/".format(jd, jn), 'opt')
    j_ve = Job ("{0}{1}/".format(jd, jn), 've')
    m_pe = ModelFile ("{0}{1}/pe/pe.feb".format(jd, jn))
    m_op = ModelFile ("{0}{1}/opt/opt.feb".format(jd, jn))
    m_ve = ModelFile ("{0}{1}/ve/ve.feb".format(jd, jn))

    # get the time scales associated with the poroelastic job
    ts = j_pe.df_parm['OT'].tolist()
    # determine how many new timescales should be added
    if len(ts) == 2:
        n_up = 1 # add one more simulation
    elif len(ts) < 2:
        # error, must have at least two points
        print("ERROR :: fitting.add_fit_timescales() :: fit job '{0}' in '{1}' has less than two timescales, cannot add more.".format(jn, jd))
        return False
    else:
        n_up = (len(ts) - 1) / 2

    ## append new timescales to data frame
    cur_idx = 0 # current index
    prv_idx = 0 # previous index
    df_len = len(j_pe.df_parm.index)
    for idx, row in j_pe.df_parm.iterrows():
        # update time scales
        # skip the first row
        if idx != 0:
            # for each row, the new timescale is half way between the current and previous timescales
            j_pe.df_parm.loc[df_len + idx - 1] = row # copy

            # determine new time scale on log scale (!)
            ts_low = lin2log(j_pe.df_parm.iloc[idx - 1]['OT'])
            ts_high = lin2log(j_pe.df_parm.iloc[idx]['OT'])
            ts_new = log2lin((ts_low + ts_high) / 2)


            # adjust values
            j_pe.df_parm.loc[df_len + idx - 1, 'OT'] = ts_new
            j_pe.df_parm.loc[df_len + idx - 1, 'n'] = j_pe.df_parm['n'].max() + 1
            j_pe.df_parm.loc[df_len + idx - 1, 'id'] = 'OT{0}'.format(j_pe.df_parm.loc[df_len + idx - 1, 'n'])
            j_pe.df_parm.loc[df_len + idx - 1, 'path'] = "job/OT{0}/".format(j_pe.df_parm.loc[df_len + idx - 1, 'n'])

        # update indicies
        cur_idx = idx + 1
        prv_idx = idx

    # save updated data frame to simulation directories
    # sort list
    j_pe.df_parm = j_pe.df_parm.sort_values(by=['OT'])
    # save
    j_pe.save_parameters(overwrite = True)
    j_pe.jn = "opt"
    j_pe.save_parameters(overwrite = True)
    j_pe.jn = "ve"
    j_pe.save_parameters(overwrite = True)

# update optimization while forcing other optimization values to remain constant
def force_viscoelastic_optimization (jd = None, jn = None, overwrite = True, z_int = None, force = False):
    """

    Arguments:
    ----------
    None

    Returns:
    --------
    bool
        'True' if optimization corresponding to simulation has been completed, else 'False'.
    """
    pass

# add optimization routine
def update_optimization (jd = None, jn = None, i = None, overwrite = True, z_int = None, emod_val = None, gamma_val = None, tau_val = None):
    """ update optimization portion of fitting routine.

    Arguments:
    ----------
    jd : str
        path to directory with contains the job
    jn : str
        name of job in directory 'jd'
    i : int
        integer corresponding to index number in parameter file
    overwrite : bool
        overwrite existing files if they are incomplete
    z_int : int (optional)
        correspond to index in 'dict_feb'
    emod_val : float or None (optional)
        optional value to assign bulk modulus ddo not have access to Scholar Profiles. Souring optimization.
    gamma_val : float or None (optional)
        optional value to assign the relaxation constant during optimization.
    tau_val : float or None (optional)
        optional value to assign the time constant during optimization.

    Returns:
    --------
    bool
        'True' if job has been completed successfully; else 'False'.
    """
    ## establish job and model file
    j_pe = Job ("{0}{1}/".format(jd, jn), 'pe')
    j_op = Opt ("{0}{1}/".format(jd, jn), 'opt')
    j_ve = Job ("{0}{1}/".format(jd, jn), 've')
    m_op = ModelFile ("{0}{1}/opt/opt.feb".format(jd, jn))
    m_ve = ModelFile ("{0}{1}/ve/ve.feb".format(jd, jn))

    ## check arguments
    # check job paths
    if not (j_op.has_parameters()):
        print("ERROR :: fitting.update_poroelastic() :: job 'op' does not exist in '{0}{1}'.".format(jd, jn))
        return False
    # check nz_int
    if not (j_pe.has_simulation(i)):
        print("ERROR :: fitting.update_poroelastic() :: simulation integer 'i={0}' does not exist in job '{1}{2}/pe/'.".format(i, jd, jn))
        return False

    ## check the directory
    # establish simulation directory
    dir_op = "{0}{1}/opt/{2}".format(jd, jn, j_op.df_parm.iloc[i-1]['path'])
    n = j_op.df_parm.iloc[i-1]['n']
    jobid = "o{0}".format(n)
    if not (z_int is None): jobid = "z{0}-o{1}".format(z_int, n)
    # if the directory does not eixst
    if not os.path.exists(dir_op):
        # if the  does not, make the directory
        os.makedirs(dir_op)

        # set job id
        # jobid = "o{0}".format(n)
        # if z_int > 0: jobid = "z{0}-o{1}".format(z_int, n)

        # get the simulation stress-strain data from the poroelastic file
        s_pe = j_pe.get_simulation(i)
        f_d = s_pe.get_displacement_force_lag()
        f_d['f'] = -1 * f_d['f'] # transform force to negative value

        ## generate the model file
        m = j_ve.parameterize_model(m = m_op, n = n)
        # if a bulk modulus was specified, specify it in the model file
        if emod_val is not None: m.update_element_value(elm_path = emod_xml, value = emod_val, format = "{0:.4e}")
        # if a realxation constant was specified, specify it in the model file
        if gamma_val is not None: m.update_element_value(elm_path = gamma_xml, value = gamma_val, format = "{0:.4e}")
        # if a time constant was specified, specify it in the model file
        if tau_val is not None: m.update_element_value(elm_path = tau_xml, value = tau_val, format = "{0:.4e}")
        m.save_model(saveto = dir_op, saveas = "{0}.feb".format(jobid), overwrite = overwrite)

        ## GENERATE OPTIMIZATION FILE
        o = OptFile()
        # add optimizable parameters
        ## tau and gamma can depend on previous simulations
        df_res = j_op.get_optimization_results()
        if df_res is not None:
            # get the simulation results to the left, fast
            # as time increases, we expect gamma to increase (high), tau to decrease (low) and emod to be constant
            j = 0
            g_l = None
            t_l = None
            e_l = None
            while g_l is None:
                j += 1 # increment j
                i_l = i - j # decrement the left integer
                if i_l < 1:
                    # decrimined beyond simulation bounds, use defaults
                    g_l = gamma_max
                    t_l = tau_min
                    e_l = emod_min
                else:
                    # attempt to parse simulation data
                    n_l = j_op.df_parm.iloc[i_l - 1]['n']
                    g_l = j_op.get_optimized_parameter_value(n = n_l, o_key = 'g1_opt')
                    t_l = j_op.get_optimized_parameter_value(n = n_l, o_key = 't1_opt')
                    e_l = j_op.get_optimized_parameter_value(n = n_l, o_key = 'E_opt')

            # get the results to the right, slow
            # as the timescale decreases, we expect gamma to decrease (low), tau in increase (high), and emod to be constant
            j = 0
            g_r = None
            t_r = None
            e_r = None
            while g_r is None:
                j += 1 # increment j
                i_r = i + j
                if i_r > j_pe.get_sim_num():
                    # increment beyond simulation bounds, use defaults
                    g_r = gamma_min
                    t_r = tau_max
                    e_r = emod_max
                else:
                    # attempt to parse the simulation data
                    n_r = j_op.df_parm.iloc[i_r - 1]['n']
                    g_r = j_op.get_optimized_parameter_value(n = n_r, o_key = 'g1_opt')
                    t_r = j_op.get_optimized_parameter_value(n = n_r, o_key = 't1_opt')
                    e_r = j_op.get_optimized_parameter_value(n = n_r, o_key = 'E_opt')

            if j_pe.get_sim_num() > 2:
                # if the number of simulations is greater than two, use an average for the elastic modulus
                n_e = 0 # number of elastic modulus values counted
                a_e = 0. # accumulation of elastic modulus values
                for j in range(j_pe.get_sim_num()):
                    # n_e += 1
                    n_tmp = j_op.df_parm.iloc[j - 1]['n'] # i -> n
                    v_e = j_op.get_optimized_parameter_value(n = n_tmp, o_key = 'E_opt') # n -> E_opt
                    if v_e is not None:
                        a_e += v_e
                        n_e += 1
                # if n_e is greater than two, use the second standard deviation to set the bounds
                if n_e > 2:
                    avg = a_e / n_e
                    var = 0.
                    for j in range(j_pe.get_sim_num()):
                        n_tmp = j_op.df_parm.iloc[j - 1]['n'] # i -> n
                        v_e = j_op.get_optimized_parameter_value(n = n_tmp, o_key = 'E_opt') # n -> E_opt
                        if v_e is not None: var += math.pow(v_e - avg, 2)
                    # the bounds are two standard deviations outside of the average
                    e_l = avg - 2 * math.sqrt(var / (n_e - 1))
                    e_r = avg + 2 * math.sqrt(var / (n_e - 1))
            else:
                print("err")
                exit()

        else:
            # optimization simulations have not been completed yet and therefore cannot
            # use default ranges to initialize the optimization parameters
            g_r = gamma_min
            g_l = gamma_max
            t_r = tau_min
            t_l = tau_max
            e_r = emod_min
            e_l = emod_max


        ## append the values to the optimization file
        # relaxation constant
        if g_r < g_l:
            o.add_parameters(min_val = g_r, max_val = g_l, start_val = (g_r + g_l) / 2., name = gamma_name, scale = g_r) # relaxation constant
        else: # g_l < g_r
            o.add_parameters (min_val = g_l, max_val = g_r, start_val = (g_r + g_l) / 2., name = gamma_name, scale = g_l)
        # time constant
        if t_r < t_l:
            o.add_parameters(min_val = t_r, max_val = t_l, start_val = (t_r + t_l) / 2., name = tau_name, scale = t_r) # time constant
        else: # t_l < t_r
            o.add_parameters(min_val = t_l, max_val = t_r, start_val = (t_r + t_l) / 2., name = tau_name, scale = t_l)
        # elastic modulus
        if e_r < e_l:
            o.add_parameters(min_val = e_r, max_val = e_l, start_val = (e_r + e_l) / 2., name = emod_name, scale = e_r)
        else: # e_l < e_r
            o.add_parameters(min_val = e_l, max_val = e_r, start_val = (e_r + e_l) / 2., name = emod_name, scale = e_l)

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
        # the optimization job has not completed yet
        return False
    else:
        # the job directory does exist, check if optimization is finished
        # update results
        j_op.get_optimization_results(save = True, overwrite = True)
        # attempt to generate optimized model
        m_o = j_op.generate_optimized_model (m = m_ve, n = i)
        # if the method returns None type, optimization is not done
        if m_o is None: return False
        # from here, the optimizatoin results can be parse from the job.

    return True

# update poroelastic jobs in fit job
def update_poroelastic (jd = None, jn = None, i = None, overwrite = True, z_int = None):
    """ update the poroelastic portion of the fit jobs

    Parameters:
    -----------
    jd : str
        path to directory with contains the job
    jn : str
        name of job in directory 'jd'
    i : int
        integer corresponding to index number in parameter file
    overwrite : bool
        overwrite existing files if they are incomplete
    z_int : int (optional)
        correspond to index in 'dict_feb'

    Returns:
    --------
    bool
        'True' if job has been completed successfully; else 'False'.
    """
    ## establish job and model file
    j_pe = Job ("{0}{1}/".format(jd, jn), 'pe')
    m_pe = ModelFile ("{0}{1}/pe/pe.feb".format(jd, jn))

    ## check arguments
    # check job paths
    if not (j_pe.has_parameters()):
        print("ERROR :: fitting.update_poroelastic() :: job 'pe' does not exist in '{0}{1}'.".format(jd, jn))
        return False
    # check n
    if not (j_pe.has_simulation(i)):
        print("ERROR :: fitting.update_poroelastic() :: simulation integer 'i={0}' does not exist in job '{1}{2}/pe/'.".format(i, jd, jn))
        return False

    ## check the directory
    # establish simulation directory
    dir_pe = "{0}{1}/pe/{2}".format(jd, jn, j_pe.df_parm.iloc[i-1]['path'])
    n = j_pe.df_parm.iloc[i-1]['n']
    jobid = "p{0}".format(n)
    if not (z_int is None): jobid = "z{0}-p{1}".format(z_int, n)
    # if the directory does not eixst
    if not os.path.exists(dir_pe):
        ## establish the simulation
        # if it does not exist, make the directory
        os.makedirs(dir_pe)
        # parameterize model, save to simulation directory
        j_pe.parameterize_model(m = m_pe, n = n).save_model(saveto = dir_pe, saveas = "{0}.feb".format(jobid), overwrite = overwrite)
        # write slurm file
        gen_slurm_script (filepath = "{0}{1}.slurm.sub".format(dir_pe, jobid),
            jobid = jobid,
            feb_file = "{0}{1}.feb".format(j_pe.get_simulation(i).get_simulation_path(), jobid),
            time_limit = "30:00", # twenty minute time limit
            del_feb = True,
            del_xplt = True)
        return False # job not completed yet
    else: # if the simulation directory exists
        ## has the simulation completed?
        if not os.path.exists(dir_pe + "febio4.job.out"): return False
        elif not os.path.exists(dir_pe + "febio4.out.csv"):
            # in this case, the outfile exists by the csv file does not
            # attempt to parse the results from the logfile
            success = j_pe.get_simulation(i).parse_logfile()
            if not success: return False # simulation not completed yet
            # past here, results were written and ready for optimization phase

    return True

# update viscoelastic jobs in fit job
def update_viscoelastic (jd = None, jn = None, n = None, overwrite = True, z_int = None):
    """ update the specific viscoelastic job.

    Parameters:
    -----------
    jd : str
        path to directory with contains the job
    jn : str
        name of job in directory 'jd'
    n : int
        integer corresponding to 'n' column in parameter file
    overwrite : bool
        overwrite existing files if they are incomplete
    z_int : int (optional)
        correspond to index in 'dict_feb'

    Returns:
    --------
    bool
        'True' if job has been completed successfully; else 'False'.
    """
    ## establish job and model file
    j_ve = Job ("{0}{1}/".format(jd, jn), 've')
    j_op = Opt ("{0}{1}/".format(jd, jn), 'opt')
    m_ve = ModelFile ("{0}{1}/ve/ve.feb".format(jd, jn))

    ## check arguments
    # check job paths
    if not (j_ve.has_parameters()):
        print("ERROR :: fitting.update_viscoelastic() :: job 've' does not exist in '{0}{1}'.".format(jd, jn))
        return False
    # check n
    if not (j_ve.has_simulation(i)):
        print("ERROR :: fitting.update_viscoelastic() :: simulation integer 'i={0}' does not exist in job '{1}{2}/ve/'.".format(i, jd, jn))
        return False

    ## check the directory
    # establish simulation directory
    dir_ve = "{0}{1}/ve/{2}".format(jd, jn, j_ve.df_parm.iloc[i-1]['path'])
    n = j_ve.df_parm.iloc[i-1]['n']
    jobid = "v{0}".format(n)
    if not (z_int is None): jobid = "z{0}-v{1}".format(z_int, n)
    # if the directory does not eixst
    if not os.path.exists (dir_ve):
        ## generate simulation
        # create the directory
        os.makedirs(dir_ve)

        ## generate the model file with optimized parameters
        m_o = j_op.generate_optimized_model(m = m_ve, n = i)
        m_o.save_model(saveto = dir_ve, saveas = "{0}.feb".format(jobid), overwrite = overwrite)

        ## generate the slurm file
        gen_slurm_script (filepath = "{0}{1}.slurm.sub".format(dir_ve, jobid),
            jobid = jobid,
            feb_file = "{0}{1}.feb".format(j_ve.get_simulation(i).get_simulation_path(), jobid),
            time_limit = "15:00", # fifteen minute time limit
            del_feb = True,
            del_xplt = True)
        return False # continue to next int
    else: # if the simulation directory exists
        ## has the simulation completed?
        if not os.path.exists(dir_ve + "febio4.job.out"): return False
        elif not os.path.exists(dir_ve + "febio4.out.csv"):
            # in this case, the outfile exists but the csv file does not
            # attempt to parse the results from the logfile
            success = j_ve.get_simulation(i).parse_logfile()
            if not success: return False # simulation not completed yet
            # past here, results were written and ready for analysis or further use

    return True

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
