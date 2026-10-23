
## MODULES
# native, conda
import sys, os, math, glob
import matplotlib.pyplot as plt
# febio
import mod_parm.dynamic_analysis as dma
import mod_parm.poroelastic_modulation as pe
from febio.job import Job
from febio.slurm.submit import gen_slurm_script
# figure
from plot.figure import Figure
from plot.plot import gen_plot

## PARAMETERS
# model file
m = pe.bend_scale_dict['0.125']
# permeability
val_perm = 0.0001
# elastic modulus
val_emod = 0.5
# loading depth (mm)
val_loading_depth = 0.01
# relaxation_time (seconds)
val_relaxation_time = 10
# length scale associated with model
val_ell = 0.125
# number of oscillation amplitudes to test
n_osc_amp = 10
# time limit assigned to simulations on slurm
slurm_timelimit = "40:00"

## METHODS
# initialize job
def initialize_amplitude_sweep (jd, jn, m, emod = val_emod, perm = val_perm, ell = val_ell, ld = val_loading_depth, n = n_osc_amp):
    """ generate parameters and save job.

    Arguments:
    jd : str
        job directory
    jn : str
        job name (in directory)
    m : str or ModelFile
        file associated with amplitude sweep experiment
    emod : float
        bulk elastic modulus (MPa)
    perm : float
        permeability (mm^4 / Ns)
    ell : float
        length scale, emperical (mm)
    ld : float
        loading depth (mm)
    n : int
        number of amplitudes to test

    Returns:
    --------
    None
    """
    ## determine resonant timescale from poroelastic properties
    tau_poro = 30. * pow(emod, -1) * pow(perm, -1) * pow(ell, 2)
    # initialize job, add model
    j = Job(jd, jn)
    # set constant parameters
    pe.constant_bulk_modulus(j, emod)
    pe.constant_permeability(j, perm)
    pe.constant_length_scale(j, ell)
    dma.set_loading_depth(j, ld)
    dma.set_relaxation_time(j, val_relaxation_time)
    # oscillation time scale is at resonant poroelastic timescale
    dma.set_oscillation_period(j, 2. * math.pi / tau_poro, n_cycles = 10, n_steps = 60)
    # vary the oscillation amplitude linearly from 0.05 to the loading depth
    dma.vary_oscillation_amplitude(j, minval = 0.01 * ld, maxval = ld, nval = n)
    # generate parameters, initialize files
    j.generate_parameters()
    j.save_config()
    j.save_parameters()
    for i in range(1, j.get_sim_num() + 1):
        jobid = "{0}-p{1}".format(jn, i)
        sd = j.get_simulation(i).get_simulation_path()
        mi = j.parameterize_model(m = m, n = i) # parameterize model
        mi.save_model(saveto = sd, saveas = "{0}.feb".format(jobid))
        gen_slurm_script(filepath = "{0}{1}.slurm.sub".format(sd, jobid), jobid = "{0}".format(jobid), feb_file = "{0}{1}.feb".format(sd, jobid), time_limit = slurm_timelimit, del_xplt = True)

# create testing array
def vary_loading_depth(jd, z, min_ld = None, max_ld = None, n_ld = 5):
    """ vary the loading depth, test range of amplitudes at each loading depth.

    Arguments:
    ----------
    jd : str
        path to job directory
    z : int
        length scale, corresponds to model file in 'pe.scale_dict'
    min_ld : float
        smallest loading depth to test
    max_ld : float
        largest loading depth to test
    n_ld : number of loading depths between largest and smallest to test

    Returns:
    --------
    None
    """
    # based on the z_int
    z_str = str(z)
    if not z_str in list(pe.bend_scale_dict.keys()):
        print("ERROR :: amplitude_sweep.vary_loading_depth() :: method argument 'z' ({0}) must be a key in 'pe.scale_dict'.".format(z_str))

    # find the model file
    m = "/home/mpikg/dorsey/Desktop/biphasic/" + pe.bend_scale_dict[z_str]
    # generate a range of length scales to test
    if min_ld is None: min_ld = z / 10.
    if max_ld is None: max_ld = z / 2.
    ld = [ min_ld + (max_ld - min_ld) * ((i) / (n_ld - 1)) for i in range(n_ld)]
    for i in range(len(ld)):
        initialize_amplitude_sweep(jd = jd, jn = "l{0}".format(i), m = m, ld = ld[i])

# generate results
def fig_amp_res (jd, jn, norm = False, show = False, save = False):
    """ show results from one amplitude sweep.

    Arguments:
    ----------
    jd : str
    jn : str
    show : bool
    save : bool

    Returns:
    --------
    Figure
        contains data and plotting instructions.
    """
    ## get constants
    j = Job(jd, jn)
    emod_val = float(j.get_key_value('E', 1))
    ell_val = float(j.get_key_value('L', 1))
    ld_val = float(j.get_key_value('LD', 1))
    # oa_val = float(j.get_key_value('OA'))
    ## accumulate simulation data
    x = []
    y_hys = []
    # TODO plot phase shift scaling
    # TODO plot lissajou curve
    for i in range(1, j.get_sim_num() + 1):
        ## collect hysteresis and oscillation amplitude
        s = j.get_simulation(i) # returns Simulation object

        # the x-axis is the oscillation amplitude applied to the simulation
        x.append(s.get_key_value('OA'))
        # if norm: x[-1] *= math.pow(ell_val, -1) # the distance is normalized by the length scale factor
        if norm: x[-1] *= math.pow(ld_val, -1) # the distance is normalized by the length scale factor

        # the y-axis is the energy dissipated by the material
        y_hys.append(-s.parse_hysteresis_work()[0]) # use the second to last cycle
        if norm: y_hys[-1] *= math.pow(ld_val, -2) * math.pow(emod_val, -1) # reduced by elastic modulus and length scale

    ## show results
    if show:
        f, ax1 = plt.subplots()
        line = ax1.plot(x, y_hys)
        if norm:
            ax1.set_xlabel("Normalized Oscillation Amplitude ($A^{{*}} = A \\cdot \\ell^{{-1}}$)") #, fontsize = )
        else:
            ax1.set_xlabel("Oscillation Amplitude ($mm$)") #, fontsize = )
        if norm:
            ax1.set_ylabel("Normalized Dissipated Energy ($W^{{*}} = W \\cdot \\ell^{{-3}} \\cdot E^{{-1}}$)") #, fontsize = )
        else:
            ax1.set_ylabel("Dissipated Energy ($J$)") #, fontsize = )
        # set logscale
        plt.show()
    ## return
    return x, y_hys

def fig_load_res (jd, jn, norm = False, show = True, save = False):
    """ analyze the results from loading depth sweeps.

    Arguments:
    ----------
    jd : str
        path to job directory which contains the loading sweep.
    jn : str
        name job in job directory ('jd').
    norm : bool
        display results normalized by relevant model parameters.
    show : bool
        display results.
    save : bool
        save results.

    Returns:
    --------
    None
    """
    # loop through loading experiments existing in job directory
    i = 0
    fig = Figure()
    while True:
        # check if the directory exists
        ld = "{0}/{1}/l{2}/".format(jd, jn, i)
        if not os.path.exists(ld): break
        # if it does, parse the results append to existing data
        j = Job("{0}/{1}/".format(jd, jn), "l{0}".format(i))
        x, y = fig_amp_res(jd = "{0}/{1}/".format(jd, jn), jn = "l{0}".format(i), norm = norm, show = False, save = False)
        fig.append_lists(xlist = x, ylist = y, label = "$L = {0:.3e} $".format(float(j.get_key_value(dma.key_ld, 1))))
        i += 1 # increment and repeat
    # set axis formatting
    fig.set_axis_label(akey = 'x', l = "Oscillation Amplitude ($mm$)")
    fig.set_axis_label(akey = 'y', l = "Dissipated Energy ($J$)")
    gen_plot(fig)
    # get the results for each loading experiment
    # merge results and plot
    pass


if __name__ == "__main__":

    ## ARGUMENTS:
    # first argument: job directory
    jd = sys.argv[1]
    # second argument: job name
    jn = sys.argv[2]

    ## SCRIPT
    # initialize job that has amplitude sweep
    initialize_amplitude_sweep(jd, jn, m = "/home/mpikg/dorsey/Desktop/biphasic/" + m)

