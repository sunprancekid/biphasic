
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
## simulation parameters
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

## figure / plotting parameters
# default subtitle label font size
default_subtitle_label_font_size = 16
# default axis label font size
default_axis_label_font_size = 14
# key used for dissipated energy property
pkey_de = 'de'
# key used for phase shift property
pkey_ps = 'ps'
# key used for lissajou curve property
pkey_lj = 'lj'
# default axis label size
# list of properties, used as keys
prop_dict = [pkey_de, pkey_ps, pkey_lj]
# dictionary used for x-axis labels
xax_prop_label_dict = {pkey_de: "Oscillation Amplitude ($mm$)",
                       pkey_ps: "Oscillation Amplitude ($mm$)",
                       pkey_lj: None}
xax_norm_prop_label_dict = {pkey_de: "Normalized Oscillation Amplitude\n($A^{{*}} = A \\cdot \\L^{{-1}}$)",
                       pkey_ps: None,
                       pkey_lj: None}
# dictionary used for y-axis labels
yax_prop_label_dict = {pkey_de: "Dissipated Energy ($J$)",
                       pkey_ps: "Phase Shift ($^\\circ$)",
                       pkey_lj: None}
yax_norm_prop_label_dict = {pkey_de: "Normalized Dissipated Energy\n($W^{{*}} = W \\cdot L^{{-2}} \\cdot E^{{-1}}$)",
                            pkey_ps: "Normalized Phase Shift\n($\\delta^{{*}} = \\delta \\cdot L^{{-2}}$)",
                            pkey_lj: None}
# scaling integers used for normalizationfile_complex_modulus
p_scale_ell = {pkey_de: 0, pkey_lj: 0, pkey_ps: 0} # property scaling against length scale, key 'L'
p_scale_load = {pkey_de: -2, pkey_lj: 0, pkey_ps: 0} # scaling of property against the loading depth, key 'LD'
# p_scale_amp = {pkey_de: 0, pkey_lj: 0, pkey_ps: 0} # scaling of property against the oscillation amplitude, key 'OA'/
p_scale_emod = {pkey_de: -1, pkey_lj: 0, pkey_ps: 0} # property scaling against the elastic modulus, key 'E'

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
    crit_poro_f = 30. * pow(emod, 1) * pow(perm, 1) * pow(ell, -2)
    crit_poro_t = 2. * math.pi / crit_poro_f
    # initialize job, add model
    j = Job(jd, jn)
    # set constant parameters
    pe.constant_bulk_modulus(j, emod)
    pe.constant_permeability(j, perm)
    pe.constant_length_scale(j, ell)
    dma.set_loading_depth(j, ld)
    dma.set_relaxation_time(j, val_relaxation_time)
    # oscillation time scale is at resonant poroelastic timescale
    dma.set_oscillation_period(j, crit_poro_t, n_cycles = 10, n_steps = 60)
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
def fig_amp_res (jd, jn, prop, norm = False, show = False, save = False):
    """ show results from one amplitude sweep.

    Arguments:
    ----------
    jd : str
        path to directory which contains job
    jn : str
        name of directory which contains results in job directory ('jd')
    prop : str
        key corresponding to property, must be in 'prop_dict'
    norm : bool
        if 'True', normalize results by simulation parameters according to 'scale_dict'
    show : bool
        if 'True', display results in GUI.
    save : boolcenter
        if 'True', save results to csv file.

    Returns:
    --------
    list, list
        x- and y-axis data sets as lists
    """
    ## check that 'prop' exists in 'prop_dict'
    if prop not in prop_dict:
        # error, cannot extract results
        Exception("ERROR :: ammplitude_sweep() :: cannot extract results for 'prop={0}', does not exist in 'prop_dict'.".format(prop))
        return [], []
    ## get constants
    j = Job(jd, jn)
    emod_val = float(j.get_key_value('E', 1))
    ell_val = float(j.get_key_value('L', 1))
    ld_val = float(j.get_key_value('LD', 1))
    # oa_val = float(j.get_key_value('OA'))
    ## accumulate simulation data
    x = []
    y = []
    # TODO plot phase shift scaling
    # TODO plot lissajou curve
    for i in range(1, j.get_sim_num() + 1):
        ## collect hysteresis and oscillation amplitude
        s = j.get_simulation(i) # returns Simulation object

        # the x-axis is the oscillation amplitude applied to the simulation
        if prop == pkey_de or pkey_ps:
            # for hysteresis or phase shift, property is plotted
            # against the oscillation amplitude
            x.append(s.get_key_value('OA'))
            if norm: x[-1] *= math.pow(ld_val, -1) # the distance is normalized by the length scale factor
        elif prop == pkey_lj:
            # for the lissajou curve, force is plotted against displacement
            disp, force = s.show_hysteresis_work(cycle = s.get_number_oscillation_cycles() - 1, show = False, save = False, center = True)
            if not norm: x.append(disp)
            else:
                disp = [d * pow(ld_val, p_scale_ell[prop]) * pow(emod_val, p_scale_emod[prop]) for d in disp]
                x.append(disp)

        if prop == pkey_de:
            # the y-axis is the energy dissipated by the material
            y.append(s.parse_hysteresis_work()[-2]) # use the second to last cycle
            if norm: y[-1] *= math.pow(ld_val, p_scale_load[prop]) * math.pow(emod_val, p_scale_ell[prop]) # reduced by elastic modulus and length scale
        elif prop == pkey_ps:
            # the y-axis is the phase shift
            y.append(s.parse_complex_modulus(overwrite = True)['delta'].to_list()[-2])
            if norm: y[-1] *= math.pow(ld_val, p_scale_load[prop]) * math.pow(emod_val, p_scale_ell[prop]) # reduced by elastic modulus and length scale
        elif prop == pkey_lj:
            pass

    ## show results
    if show:
        f, ax1 = plt.subplots()
        line = ax1.plot(x, y)
        if norm:
            ax1.set_xlabel("Normalized Oscillation Amplitude ($A^{{*}} = A \\cdot \\ell^{{-1}}$)") #, fontsize = )
        else:
            ax1.set_xlabel("Oscillation Amplitude ($mm$)") #, fontsize = )
        if norm:
            ax1.set_ylabel("Normalized Dissipated Energy ($W^{{*}} = W \\cdot \\ell^{{-3}} \\cdot Efloat(j.get_key_value(dma.key_ld, 1))^{{-1}}$)") #, fontsize = )
        else:
            ax1.set_ylabel("Dissipated Energy ($J$)") #, fontsize = )
        # set logscale
        plt.show()
    ## return
    return x, y

def fig_load_res (jd, jn, norm = False, show = True, save = False):
    """ analyze the results from loading depth sweeps.

    Arguments:
    ----------
    jd : str
        path to job directory which contains the loadinellg sweep.
    jn : str
        name job in job directory ('jd').
    norm : bool
        display results normalized by relevant model parameters.pkey_de: 0, pkey_lj: 0, pkey_ps: 0
    show : bool
        display results.
    save : bool
        save results.

    Returns:
    --------
    None
    """
    # for all properties
    for pkey in prop_dict:
        if pkey != pkey_de and pkey != pkey_ps: continue
        # loop through loading experiments existing in job directory
        i = 0
        fig = Figure()
        while True:
            # check if the directory exists
            ld = "{0}/{1}/l{2}/".format(jd, jn, i)
            if not os.path.exists(ld): break
            # if it does, parse the results append to existing data
            j = Job("{0}/{1}/".format(jd, jn), "l{0}".format(i))
            x, y = fig_amp_res(jd = "{0}/{1}/".format(jd, jn), jn = "l{0}".format(i), prop = pkey, norm = norm, show = False, save = False)
            if norm: label = "$L/\\ell = {0:.2f}$".format(float(j.get_key_value(dma.key_ld, 1))/float(j.get_key_value('L', 1)))
            else: label = "$L = {0:.3e}$".format(float(j.get_key_value(dma.key_ld, 1)))
            fig.append_lists(xlist = x, ylist = y, label = label)
            i += 1 # increment and repeat
        # set axis formatting
        # set xaxis label
        if norm: fig.set_axis_label(akey = 'x', l = xax_norm_prop_label_dict[pkey], s = default_axis_label_font_size)
        else: fig.set_axis_label(akey = 'x', l = xax_prop_label_dict[pkey], s = default_axis_label_font_size)
        # set yaxis label
        if norm: fig.set_axis_label(akey = 'y', l = yax_norm_prop_label_dict[pkey], s = default_axis_label_font_size)
        else: fig.set_axis_label(akey = 'y', l = yax_prop_label_dict[pkey], s = default_axis_label_font_size)
        if show: gen_plot(fig, save = False)
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

