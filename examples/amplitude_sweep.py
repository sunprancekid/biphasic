
## MODULES
# native, conda
import sys, os, math
# febio
import mod_parm.dynamic_analysis as dma
import mod_parm.poroelastic_modulation as pe
from febio.job import Job
from febio.slurm.submit import gen_slurm_script

## PARAMETERS
# model file
m = pe.scale_dict['0.125']
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
n_osc_amp = 20
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
        sd = j.get_simulation(i).get_simulation_path()
        mi = j.parameterize_model(m = m, n = i) # parameterize model
        mi.save_model(saveto = sd, saveas = "{0}-{1}.feb".format(jn, i))
        gen_slurm_script(filepath = "{0}{1}-{2}.slurm.sub".format(sd, jn, i), jobid = "{0}-{1}".format(jn, i), feb_file = "{0}{1}-{2}.feb".format(sd, jn, i), time_limit = slurm_timelimit, del_xplt = True)

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
    if not z_str in list(pe.scale_dict.keys()):
        print("ERROR :: amplitude_sweep.vary_loading_depth() :: method argument 'z' ({0}) must be a key in 'pe.scale_dict'.".format(z_str))

    # find the model file
    m = "/home/mpikg/dorsey/Desktop/biphasic/" + pe.bend_scale_dict[z_str]
    # generate a range of length scales to test
    if min_ld is None: min_ld = z / 10.
    if max_ld is None: max_ld = z / 2.
    ld = [ min_ld + (max_ld - min_ld) * ((i) / (n_ld - 1)) for i in range(n_ld)]
    for i in range(len(ld)):
        initialize_amplitude_sweep(jd = jd, jn = "l{0}".format(i), m = m, ld = ld[i])


if __name__ == "__main__":

    ## ARGUMENTS:
    # first argument: job directory
    jd = sys.argv[1]
    # second argument: job name
    jn = sys.argv[2]

    ## SCRIPT
    # initialize job that has amplitude sweep
    initialize_amplitude_sweep(jd, jn, m = "/home/mpikg/dorsey/Desktop/biphasic/" + m)

