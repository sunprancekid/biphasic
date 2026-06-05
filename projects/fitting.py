
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 2026.04.17

## FILENAME: projects/pv-fitting.py
## PURPOSE: comparing fit viscoelastic model to poroelastic simulation data.


## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from febio.job import Job
from febio.sweep import Sweep
from febio.feb.model_file import ModelFile
from febio.feb.optimization_file import OptimizationFile as OptFile
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
# permeability
default_perm = 0.001
# elastic modulus
default_emod = 0.5
# length scale
default_z = 0.125
# sweep
default_n_period = 40

## VISCOELASTIC OPTIMIZATION
# path to objective function in feb file
obj_fun = "fem.rigidbody('Material2').Fz"
# gamma min, max, start, and name
gamma_min = 0.001
gamma_max = 100.
gamma_start = 1.
gamma_name = "fem.material('Material1').g1"
# tau min, max, start, and name
tau_min = 0.001
tau_max = 100.
tau_start = 1.
tau_name = "fem.material('Material1').t1"
# elastic modulus min, max, start, and name
emod_min = 0.001
emod_max = 100.
emod_start = 1.
emod_name = "fem.material('Material1').elastic.E"


## METHODS
# generate viscoelastic simulation using parameters, base feb file
def gen_ve_frequency_sweep (emod = None, tau_1 = None, gamma_1 = None, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, min_period = None, max_period = None, n_period = None, jd = None, jn = None, feb_file = default_feb_ve):
    """

    Arguments:
    ----------
    emod : float
        value of elastic modulus parameter for material model
    tau_1 : float
        value of time constant for material model
    gamma_1 : float
        value of relaxation modulus parameter for material model
    osc_amp : float
        value of oscillation amplitude parameter for simulation
    relax_time : float
        value of relaxation time (time between loading and oscillation) for simulation
    load_depth : float
        value of loading depth during loading phase during simulation
    min_period : float
        minimum oscillation frequency which is tested
    max_period : float
        maximum oscillation frequency which is tested
    n_period : int
        number of simulation frequencies between minimum and maximum which are tested
    jd : str
        path to location to initialize the job directory
    jn : str
        name assigned to job
    feb_file : str
        path to base febio model

    Returns:
    --------
    None
    """

    # import methods from viscoleastic mod file
    # NOTE :: these methods have the same name as those in the proelastic mod file, so they are loaded locally (not globally)
    from viscoelastic_modulation import constant_bulk_modulus, constant_tau, constant_gamma, frequency_sweep

    # check parameters
    # create job, assign parameters
    j = Job (jd, jn)
    constant_bulk_modulus (job = j, E_val = emod)
    constant_gamma (job = j, g_val = gamma_1)
    constant_tau (job = j, t_val = tau_1)
    frequency_sweep (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, period_low = min_period, period_high = max_period, period_n = n_period)

    # append model
    m = Model(feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/".format(jd, jn), saveas = "{0}.feb".format(jn))

def gen_ve_gamma_sweep (emod = None, tau_1 = None, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, oscillation_period = None, min_gamma = None, max_gamma = None, n_gamma = None, jd = None, jn = None, feb_file = None):
    """ generate viscoelastic simulations at fixed time scales that vary in their parameter gamma.

    Arguments:
    ----------
    emod : float
        value of elastic modulus parameter for material model
    tau_1 : float
        value of time constant for material model
    osc_amp : float
        value of oscillation amplitude parameter for simulation
    relax_time : float
        value of relaxation time (time between loading and oscillation) for simulation
    load_depth : float
        value of loading depth during loading phase during simulation
    oscillation_period : float
        timescale of periodic oscillation during simulation
    min_gamma : float
        minimum gamma value which are tested
    max_gamma : float
        maximum gamma value which are tested
    n_gamma : int
        number of gamma values between minimum and maximum which are tested
    jd : str
        path to location to initialize the job directory
    jn : str
        name assigned to job
    feb_file : str
        path to base febio model

    Returns:
    --------
    None
    """
    # import methods from viscoleastic mod file
    # NOTE :: these methods have the same name as those in the proelastic mod file, so they are loaded locally (not globally)
    from viscoelastic_modulation import constant_bulk_modulus, constant_tau, vary_gamma, constant_oscillation_parameters

    # check parameters
    # create job, assign parameters
    j = Job(jd, jn)
    constant_bulk_modulus(job = j, E_val = emod)
    constant_tau (job = j, t_val = tau_1)
    constant_oscillation_parameters (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, oscillation_period = oscillation_period)
    vary_gamma (job = j, g_low = min_gamma, g_high = max_gamma, g_n = n_gamma)

    # append model
    m = Model(feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/".format(jd, jn), saveas = "{0}.feb".format(jn))

def gen_ve_emod_tau_sweep ():
    """ vary elastic modulus and time scale parameters while gamma remains fixed.

    Arguments:
    ----------
    None

    Returns:
    --------
    None
    """
    pass

# analysis low gamma data
def analysis_gamma_low (jd = None, jn = None, show = True, save = False):
    """ analyze the data

    Arguments:
    ----------
    jd : str
        path to job directory
    jn : str
        job name
    show : bool
        determines if graphs should be shown
    save : bool
        determines if graphs should be saved

    Returns
    -------
    None
    """
    ## open simulation jobs
    # check for the poroelastic simulation
    simdir = "{0}{1}/".format(jd, jn)
    if not os.path.exists(simdir + "pe"):
        print("ERROR :: analysis_gamma_low() :: unable to find poroelastic data in ''.".format())
    sweep_pe = Sweep(simdir, "pe")

    # check for viscoelastic simulation data
    sweep_ve = []
    i = 0
    while True:
        if os.path.exists(simdir + "g-lo-{0}".format(i)):
            sweep_ve.append(Sweep(simdir, "g-lo-{0}".format(i)))
            i += 1
        else:
            break
    # for i in range(len(sweep_ve)):
    #     sweep_ve[i].show_phase_shift()

    ## compare poroelasticity and viscoelasticity simulations
    # frequency sweep
    data = sweep_pe.get_hysteresis_work()
    pe_label = "PE ($E$ = {0:.1e}, \n$K$ = {1:.1e}, $Z$ = {2:.1e})".format(sweep_pe.get_simulation(0).get_key_value('E'), sweep_pe.get_simulation(0).get_key_value('K'), 0.125)
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_hysteresis_work()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Measured Energy Loss ($J$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)

    # phase shift
    data = sweep_pe.get_phase_shift()
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_phase_shift()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Phase Shift (degrees, $^{{\\circ}}$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)

    # dynamic modulus
    data = sweep_pe.get_dynamic_modulus()
    data['label'] = [pe_label for i in range(len(data))]
    for i in range(len(sweep_ve)):
        d_ve = sweep_ve[i].get_dynamic_modulus()
        ve_label = "VE-{0} ($k$ = {1:.1e}, \n$\\gamma$ = {2:.1e}, $\\tau$ = {3:.1e})".format(i, sweep_ve[i].get_simulation(0).get_key_value('E'), sweep_ve[i].get_simulation(0).get_key_value('gamma'), sweep_ve[i].get_simulation(0).get_key_value('tau'))
        d_ve['label'] = [ve_label.format(i) for j in range(len(d_ve))]
        data = pd.concat([data, d_ve], ignore_index = True)
    fig = Figure()
    fig.append_df(data, xcol = 'f', ycol = 8, icol = 'label')
    fig.set_axis_scale('x', log = True)
    # fig.set_axis_scale('y', log = True)
    fig.set_axis_label('x', "Oscillation Frequency ($Hz$)")
    fig.set_axis_label('y', "Dynamic Modulus ($Pa$)")
    # fig.set_axis_minimum_value('y', data[8].min())
    # fig.set_axis_maximum_value('y', data[8].max())
    gen_plot(fig, show = show, save = save)

# first step in fitting sequence
def step_one (jd = None, jn = None, emod = default_emod, perm = default_perm, z = default_z, osc_amp = default_oscillation_amplitude, relax_time = default_relaxation_time, load_depth = default_loading_depth, n_period = default_n_period, min_period = None, max_period = None, feb_file = default_feb_pe):
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
    n_period : int (optional, default is 'default_n_period')
        number of unique period values between minimum and maximum to test
    min_period : float (optional)
        minimum oscilation period to test (if unspecified, minimum period is
        two orders of magnitude less than the resonant timescale)
    max_period : float (optional)
        maximum oscillation period to test (if unspecified, maximum period is
        two orders of magnitude greater than the resonant timescale)
    feb_file : str (optional, default is 'default_feb_pe')
        path to base poroelastic model to use for simulation set

    Returns:
    --------
    None
    """
    # based on the poroelastic model, determine the time scales
    poro_tau = pow(z, 2.) / (emod * perm)
    poro_amp = emod * pow(z, 3.)

    # use time scales to set minimum, maximum period
    if min_period is None: min_period = poro_tau / 100
    if max_period is None: max_period = poro_tau * 100

    # load modules
    # NOTE :: these methods have the same names as those for viscoleasticity, so they are loaded locally rather than globally
    from poroelastic_modulation import constant_bulk_modulus, constant_permeability, frequency_sweep

    # set job parameters
    j = Job("{0}{1}".format(jd, jn), 'pe')
    constant_bulk_modulus (job = j, E_val = emod)
    constant_permeability (job = j, K_val = perm)
    frequency_sweep (job = j, loading_depth = load_depth, relaxation_time = relax_time, oscillation_amplitude = osc_amp, period_low = min_period, period_high = max_period, period_n = n_period)

    # load model
    m = ModelFile (feb_file)

    # save
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    m.save_model (saveto = "{0}{1}/pe/".format(jd, jn), saveas = "pe.feb".format(jn))

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
    from viscoelastic_modulation import constant_bulk_modulus, constant_tau, constant_gamma, frequency_sweep

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
    job_ve.generate_parameterized_models(m = "{0}{1}/opt/opt.feb".format(jd, jn))

    # loop through each poroelastic simulation, generation viscoelastic optimization
    for i in range(1, job_pe.get_sim_num() + 1):
        # check the that simulation finished
        # open each simulation, save the final stress-strain, hysteresis data
        s_pe = job_pe.get_simulation(i)
        s_ve = job_ve.get_simulation(i)
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
        # add optimization data (from poroelastic simulation)
        o.add_data_list(x_list = f_d['t'].tolist(), y_list = f_d['f'].to_list())
        # append cyclic data to optimization file to the viscoelastic job with the poroelastic data
        # here, the parameters for the poroelastic and viscoelastic jobs should be exactly the same
        o.save_optimization_file(filepath = "{0}opt-{2}.opt".format(s_ve.get_simulation_path(), jn, i))

# third step in fitting sequence
def step_three ():
    """ third step is fitting sequence, once the second step is finished.

    during the third step, the optimal viscoelastic parameters are parsed
    from each optimization model. the optimized model is rerun to confirm
    the validity of the parameters.

    Arguments:
    ----------
    None

    Results:
    --------
    None
    """
    pass

# fourth step in fitting sequence
def step_four ():
    """ fourth step in fitting sequence, once the third step is finished.

    during the fourth step, the optimizal parameters for the viscoelastic
    fitting are plotted against the timescale. The properties of the
    simulated material (e.g. loss modulus) are compared for the poroelastic
    model and the optimized viscoelastic model.

    Arguments:
    ----------
    None

    Results:
    --------
    None
    """
    pass

if __name__ == "__main__":

    ## ARGUMENTS
    # first argument: simulation directory
    jd = sys.argv[1]
    # second argument: simulation set name
    jn = sys.argv[2]


    ## SCRIPT

    ## POROELASTICITY
    # generate the poroelasticity simulation
    step_one (jd = "{0}{1}/".format(jd, jn), jn = "pe")

    ## VISCOELASTICITY
    # pick the viscoelastic model parameters (both large and small)
    # vary gamma betweem three values which are sufficiently "small"
    # for i in range(n_small):
    #     # establish the viscoelasticity parameters
    #     g_val = min_small_gamma + ((i) / (n_small - 1)) * (max_small_gamma - min_small_gamma)
    #     t_val = poro_tau
    #     e_val = poro_amp / (pow(z, 3.) * emod)
    #     # generate simulation
    #     gen_ve_frequency_sweep (emod = e_val, tau_1 = t_val, gamma_1 = g_val, jd = "{0}{1}/".format(jd, jn), jn = "g-lo-{0}".format(i), min_period = poro_tau / 100., max_period = poro_tau * 100., n_period = 40)
    #
    # # vary gamma between three values which are sufficiently "large"
    # # use gamma to determine emod
    # for i in range(n_large):
    #     # establish viscoelasticity parameters
    #     g_val = min_large_gamma + ((i) / (n_large - 1)) * (max_large_gamma - min_large_gamma)
    #     t_val = poro_tau / g_val
    #     e_val = poro_amp / pow(z, 3.)
    #     # generate simulation
    #     gen_ve_sweep (emod = emod, tau_1 = t_val, gamma_1 = g_val, jd = "{0}{1}/".format(jd, jn), jn = "g-hi-{0}".format(i), min_period = poro_tau / 100., max_period = poro_tau * 100., n_period = 40)

    # (run simulations)
    # compare the following:
    # - prestress relaxation
    # - frequency sweep
    # - phase shift
    # - dynamic modulus
    # - loss modulus
    # - storage modulus
    # - hysteresis curve
