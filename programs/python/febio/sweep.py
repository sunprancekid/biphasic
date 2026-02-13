
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institut for Colloids and Interfacial Sciences
## 2026.02.12

## FILENAME: programs/python/febio/sweep.py
## PURPOSE: handles simulation sets with variable oscilation frequency

## MODULES
# native / conda
import sys, os, math
import pandas as pd
# local
from febio.simulation import Simulation


## PARAMETERS
# integer corresponding to column in 'list_sim' containing simulation job directory
col_jd = 0
# integer corresponding to column in 'list_sim' containing simulation job name
col_jn = 1
# integer corresponding to column in 'list_sim' containing simulation integer
col_si = 2
# integer corresponding to column in 'list_sim' containing simulation oscillation period
col_ot = 3


## METHODS
# none


## CLASSES
class Sweep (object):
    """ handles simulation sets with variable oscillation frequency.

    Attributes:
    -----------
    list_sim : List[n_sim][]
      list of paths to simulations that exist within sweep set
    parm_sim : dict
        simulation parameters stored in dictionary
    check_paths : bool
        internal boolean that determines if paths should be checked while parsing simulations

    Methods:
    --------
    None
    """
    def  __init__ (self, jd = None, jn = None):
        """ Initialize object attributes. Attempt to load jobs if provided.

        Parameters:
        -----------
        jd : str
            path to job directory
        jn : job name
            job name, corresponds to parameter and config files

        Returns:
        --------
        Simulation
            initialized Simulation object.

        """
        # initialize lists
        self.list_sim = [[] for i in range(4)]
        self.parm_sim = []
        # if jd and jn were specified
        if jd is not None and jn is not None:
            self.add_sim_batch(jd, jn)

    ## SIMULATIONS ##

    def get_sim_num (self):
        """ returns number of simulations stored within object.

        Paramters:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def add_sim (self, jd, jn, si):
        """ append simulation to list.

        Attempts to add simulation to list_sim. Checks simulation parameters
        against parameters for simulations already in list. If all other
        simulation parameters other than the osciliation time are the same,
        then the simulation is included with the others. Otherwise, the
        simulation cannot be added. The boolean returned by the method
        determines if the appending operation was successful.

        Parameters:
        -----------
        jd : str
            path to job directory
        jn : str
            job name
        si : int
            integer corresponding to simulation in job

        Return:
        -------
        bool
            True if addition was successful, else False.
        """
        # check that the job paths and files exist
        file_parm = "{0}/{1}/{1}.parm.csv".format(jd, jn)
        file_config = "{0}/{1}/{1}.config.csv".format(jd, jn)
        if self.check_paths:
            if jd is not None:
                # attempt to locate the directory
                if not os.path.exists("{0}".format(jd)):
                    print("ERROR :: Sweep.add_sim() :: job directory '{0}' does not exist.".format(jd))
                    return True
            else:
                print("ERROR :: Sweep.add_sim() :: must specify job directory path as 'jd'.")
                return False
            if jn is not None:
                # attempt to locate the directory
                if not os.path.exists("{0}/{1}/".format(jd, jn)):
                    print("ERROR :: Sweep.add_sim() :: Unable to locate job '{0}' in directory '{1}'.".format(jn, jd))
                    return False
            else:
                print("ERROR :: Sweep.add_sim() :: must specify job name 'jn' in job directory, matching pattern ${{jd}}/{{jn}}.")
                return False
            # attempt to open the parameter and config files
            if not os.path.exists(file_parm):
                print("ERROR :: Sweep.add_sim() :: Unable to locate parameter file '{0}'.".format(file_parm))
                return False
            if not os.path.exists(file_config):
                print("ERROR :: Sweep.add_sim() :: Unable to locate the configuration file '{0}'.".format(file_config))
                return False
        # get the simulation parameters, check that the simulation integer exists
        df_parm = pd.read_csv(file_parm)
        n_match = len(df_parm.loc[df_parm['n'] == si])
        if n_match == 1:
            # append the simulation to the list
            ## TODO :: check that the simulation parameters match the parameters of simulations that already exist within the set
            self.list_sim[col_jd].append(jd)
            self.list_sim[col_jn].append(jn)
            self.list_sim[col_si].append(si)
        elif n_match == 0:
            # no matches were found
            print("ERROR :: Sweep.add_sim() :: Simulation number '{0}' does not exist within '{}'.".format(si, file_parm))
            return False
        else:
            # multiple matches were found
            print("ERROR :: Sweep.add_sim() :: Multipule simulations with integer '{0}' exist within '{1}'.".format(si, file_parm))

    def add_sim_batch (self, jd = None, jn = None):
        """ add simulation batch to object.

        Parameters:
        -----------
        jd : str
            path to job directory
        jn : job name
            job name, corresponds to parameter and config files

        Returns:
        --------
        bool
            True if operation was successful, otherwise False

        """
        # check that the job name and directory are valid paths
        if jd is not None:
            # attempt to locate the directory
            if not os.path.exists("{0}".format(jd)):
                print("ERROR :: Sweep.add_sim_batch() :: job directory '{0}' does not exist.".format(jd))
                return True
        else:
            print("ERROR :: Sweep.add_sim_batch() :: must specify job directory path as 'jd'.")
            return False
        if jn is not None:
            # attempt to locate the directory
            if not os.path.exists("{0}/{1}/".format(jd, jn)):
                print("ERROR :: Sweep.add_sim_batch() :: Unable to locate job '{0}' in directory '{1}'.".format(jn, jd))
                return False
        else:
            print("ERROR :: Sweep.add_sim_batch() :: must specify job name 'jn' in job directory, matching pattern ${{jd}}/{{jn}}.")
            return False
        # attempt to open the parameter and config files
        file_parm = "{0}/{1}/{1}.parm.csv".format(jd, jn)
        if not os.path.exists(file_parm):
            print("ERROR :: Sweep.add_sim_batch() :: Unable to locate parameter file '{0}'.".format(file_parm))
            return False
        file_config = "{0}/{1}/{1}.config.csv".format(jd, jn)
        if not os.path.exists(file_config):
            print("ERROR :: Sweep.add_sim_batch() :: Unable to locate the configuration file '{0}'.".format(file_config))
            return False
        # paths are all correct, turn off path check while appending simulations
        self.check_paths = False
        # get the total number of simulations in the batch
        df_parm = pd.read_csv(file_parm)
        n_sim = df_parm.loc[df_parm['n'].idxmax()]['n']
        # loop through simulations, parse parameters
        for n in range(1, n_sim + 1):
            self.add_sim(jd, jn, n)
        # turn off path check
        self.check_paths = True

    ## ANALYSIS - HYSTERESIS WORK ##

    def get_hysteresis_work (self):
        """ returns the hysteresis work for all simulations.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass

    def show_work (self):
        """ plot hysteresis work.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass


    ## ANALYSIS - PHASE SHIFT ##

    def get_phase_shift (self):
        """ returns the phase shift (deg) in dynamic response for all simulations.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass

    def show_phase_shift (self):
        """ displays the phase shift (deg) for all simulations against frequency.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass


    ## ANALYSIS - DYNAMIC MODULUS ##

    def get_dynamic_modulus (self):
        """ returns the dynamic modulus (Pa) for all simulations and all cycles.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass

    def show_dynamic_modulus (self):
        """ displays the dynamic modulus for all simulations against frequency.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        pass


## ARGUMENTS
# none


## SCRIPT
# none
