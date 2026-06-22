
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
from plot.figure import Figure
from plot.plot import gen_plot


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
    list_sim : List[][str]
      md list of paths to simulations that exist within sweep set
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
        ## TODO  add cycle specification, file saving and loading
        ## TODO check dynamic modulus
        ## TODO modularize accessing properties from simulations (lots of repeats)
        ## TODO add max / min stress / strain as properties
        # initialize lists
        self.list_sim = [[] for i in range(4)]
        self.parm_sim = []
        # if jd and jn were specified
        if jd is not None and jn is not None:
            self.add_sim_batch(jd, jn)

    ## REDUNDENT ##
    # in theory, these should be included with JOB
    def get_simulation(self, n):
        """ return simulation associated with integer.

        Arguments:
        ----------
        n : int
            corresponding to simulation number in job file

        Returns:
        --------
        Simulation
            initialized simulation object
        """
        return Simulation(self.jd, self.jn, n)

    def has_simulation(self, n):
        """ check if simulation integer exists within the simulation list.

        Arguments:
        ----------
        n : int
            simulation integer to check for within Sweep

        Returns:
        --------
        bool
            'True' if the simulation exists within the object, else 'False'.
        """
        return (n < self.get_sim_num())

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
        return len(self.list_sim[col_jd])

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
        self.jd = jd
        self.jn = jn
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

    def get_maximum_timescale (self, period = False):
        """ returns the largest frequency in the sweep (or smallest period).

        Arguments:
        ----------
        period : bool
            return time scale are oscillation period rather than frequency.

        Returns:
        --------
        float
            value corresponding to timescale (either frequency or period, as specified)
        """
        pass

    ## ANALYSIS - HYSTERESIS WORK ##

    def get_hysteresis_work (self, cycles = None):
        """ returns the hysteresis work for all simulations.

        for all simulation within the set, the hysteresis work is 
        determined for the 

        Parameters:
        -----------
        cycles : int or List[int]
            subset of cycles numbers to be selected

        Returns:
        --------
        df
            DataFrame containg hysteresis work and simulation parameters

        """
        # initialize arrays
        max_cycle = 0
        ot = []
        hys = [[] for i in range(self.get_sim_num())]
        # loop through all simulations
        for i in range(self.get_sim_num()):
            # initialize the simulation
            sim = Simulation(self.list_sim[col_jd][i], \
                    self.list_sim[col_jn][i], \
                    self.list_sim[col_si][i])
            # get the hysteresis data
            if sim.has_key('OT'):
                ot.append(sim.get_key_value('OT'))
                hys[i] = sim.parse_hysteresis_work()
                if len(hys[i]) > max_cycle:
                    max_cycle = len(hys[i])
            # remove the simulation
            del sim
        # add to the dataframe
        col_header = ['T', 'f']
        for i in range(max_cycle):
            col_header.append(i)
        df = pd.DataFrame(index=range(self.get_sim_num()),columns=col_header)
        for i in range(self.get_sim_num()):
            df.loc[i, 'T'] = ot[i]
            df.loc[i, 'f'] = 2. * math.pi / ot[i]
            for j in range(len(hys[i])):
                df.loc[i,j] = hys[i][j]
        # return the data frame to the user
        return df

    def show_hysteresis_work (self, period = False, save = False):
        """ plot hysteresis work for second to last cycle.

        Parameters:
        -----------
        period : bool (default 'False')
            if 'True', displays hysteresis work against period.
        save : bool (default 'False')
            if 'True', saves display to job directory

        Returns:
        --------
        None

        """
        # get work for simulations within set
        df_hys = self.get_hysteresis_work()
        # determine how cycles were performed
        c = list(df_hys.columns.values)
        i = 0
        while True:
            i += 1
            if i in c:
                continue
            else:
                i -= 2
                break
        # display the results
        fig = Figure()
        if period:
            fig.load_data(df_hys, xcol = 'T', ycol = i)
        else:
            fig.load_data(df_hys, xcol = 'f', ycol = i)
        fig.set_xaxis_scale(log = True)
        if period:
            fig.set_xaxis_label("Period ($s$)")
        else:
            fig.set_xaxis_label("Frequency (Hz, $2 \\pi T^{{-1}}$)")
        fig.set_yaxis_label("Dissipated Energy (J)")
        if save:
            fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = 'hysteresis_work')
            fig.save_data()
        gen_plot(fig, show = True, save = save)

    def get_resonant_simulation_int (self):
        """ returns the simulation number at which the sweep has an amplitude maximum.

        Parameters:
        -----------
        None

        Returns:
        --------
        int
            integer corresponding to simulation with greatest amplitude within sweep
        """
        # get the hysterseis work
        h = self.get_hysteresis_work()
        # get second to last cycle
        c = len(h.columns.values) - 4
        m_idx = 0 # index corresponding to simulation with greatest amplitude
        # search through all simulations, find index with greatest dissipated energy
        for i in range(1, len(h)):
            if h[c][i] > h[c][i - 1]:
                m_idx = i
        # NOTE here some jobs index from 1 and some from zero, would be good to check this.
        return m_idx + 1

    ## ANALYSIS - STORAGE MODULUS ##

    ## TODO add recalculate option

    def get_storage_modulus (self, cycles = None):
        """ returns the storage modulus for all simulations.

        Parameters:
        -----------
        cycles : int or List[int]
            subset of cycles to get work for

        Returns:
        --------
        df
            contains storage modulus as well as simulation properties at specified cycle.
        """
        # initialize arrays
        max_cycle = 0
        ot = []
        hys = [[] for i in range(self.get_sim_num())]
        # loop through all simulations
        for i in range(self.get_sim_num()):
            # initialize the simulation
            sim = Simulation(self.list_sim[col_jd][i], \
                    self.list_sim[col_jn][i], \
                    self.list_sim[col_si][i])
            # get the hysteresis data
            if sim.has_key('OT'):
                ot.append(sim.get_key_value('OT'))
                hys[i] = sim.parse_complex_modulus()['store-mod'].to_list()
                if len(hys[i]) > max_cycle:
                    max_cycle = len(hys[i])
            # remove the simulation
            del sim
        # add to the dataframe
        col_header = ['T', 'f']
        for i in range(max_cycle):
            col_header.append(i)
        df = pd.DataFrame(index=range(self.get_sim_num()),columns=col_header)
        for i in range(self.get_sim_num()):
            df.loc[i, 'T'] = ot[i]
            df.loc[i, 'f'] = 2. * math.pi / ot[i]
            for j in range(len(hys[i])):
                df.loc[i,j] = hys[i][j]
        # return the data frame to the user
        return df

    def show_storage_modulus (self):
        pass

    ## ANALYSIS - LOSS MODULUS ##

    def get_loss_modulus (self, cycles = None):
        """ returns the loss modulus for all simulations.

        Parameters:
        -----------
        cycles : int or List[int]
            subset of cycles to get work for

        Returns:
        --------
        df
            contains loss modulus as well as simulation properties at specified cycle.
        """
        # initialize arrays
        max_cycle = 0
        ot = []
        hys = [[] for i in range(self.get_sim_num())]
        # loop through all simulations
        for i in range(self.get_sim_num()):
            # initialize the simulation
            sim = Simulation(self.list_sim[col_jd][i], \
                    self.list_sim[col_jn][i], \
                    self.list_sim[col_si][i])
            # get the hysteresis data
            if sim.has_key('OT'):
                ot.append(sim.get_key_value('OT'))
                hys[i] = sim.parse_complex_modulus()['loss-mod'].to_list()
                if len(hys[i]) > max_cycle:
                    max_cycle = len(hys[i])
            # remove the simulation
            del sim
        # add to the dataframe
        col_header = ['T', 'f']
        for i in range(max_cycle):
            col_header.append(i)
        df = pd.DataFrame(index=range(self.get_sim_num()),columns=col_header)
        for i in range(self.get_sim_num()):
            df.loc[i, 'T'] = ot[i]
            df.loc[i, 'f'] = 2. * math.pi / ot[i]
            for j in range(len(hys[i])):
                df.loc[i,j] = hys[i][j]
        # return the data frame to the user
        return df

    def show_loss_modulus (self):
        pass

    ## ANALYSIS - PHASE SHIFT ##

    def get_phase_shift (self, cycles = None):
        """ returns the phase shift (deg) in dynamic response for all simulations.

        Parameters:
        -----------
        cycles : int or List[int]
            subset of cycles to get work for

        Returns:
        --------
        df
            contains phase shift as well as simulation properties

        """
        # initialize arrays
        max_cycle = 0
        ot = []
        hys = [[] for i in range(self.get_sim_num())]
        # loop through all simulations
        for i in range(self.get_sim_num()):
            # initialize the simulation
            sim = Simulation(self.list_sim[col_jd][i], \
                    self.list_sim[col_jn][i], \
                    self.list_sim[col_si][i])
            # get the hysteresis data
            if sim.has_key('OT'):
                ot.append(sim.get_key_value('OT'))
                hys[i] = sim.parse_complex_modulus()['delta'].to_list()
                if len(hys[i]) > max_cycle:
                    max_cycle = len(hys[i])
            # remove the simulation
            del sim
        # add to the dataframe
        col_header = ['T', 'f']
        for i in range(max_cycle):
            col_header.append(i)
        df = pd.DataFrame(index=range(self.get_sim_num()),columns=col_header)
        for i in range(self.get_sim_num()):
            df.loc[i, 'T'] = ot[i]
            df.loc[i, 'f'] = 2. * math.pi / ot[i]
            for j in range(len(hys[i])):
                df.loc[i,j] = hys[i][j]
        # return the data frame to the user
        return df

    def show_phase_shift (self, period = False, save = False):
        """ displays the phase shift (deg) for all simulations against frequency.

        Parameters:
        -----------
        period : bool
            if 'True', display phase shift against cycle period.
        save : bool (default 'False')
            if 'True', saves display to job directory.

        Returns:
        --------
        None

        """
        # get work for simulations within set
        df = self.get_phase_shift()
        # determine how cycles were performed
        c = list(df.columns.values)
        i = 0
        while True:
            i += 1
            if i in c:
                continue
            else:
                i -= 2
                break
        # display the results
        fig = Figure()
        if period:
            fig.load_data(df, xcol = 'T', ycol = i)
        else:
            fig.load_data(df, xcol = 'f', ycol = i)
        fig.set_xaxis_scale(log = True)
        if period:
            fig.set_xaxis_label("Period ($s)")
        else:
            fig.set_xaxis_label("Frequency (Hz, $2 \\pi T^{{-1}}$)")
        fig.set_yaxis_label("Phase lag (degrees, $^{{\\circ}}$)")
        fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = 'phase_shift')
        gen_plot(fig, show = True, save = save)

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
        # initialize arrays
        max_cycle = 0
        ot = []
        hys = [[] for i in range(self.get_sim_num())]
        # loop through all simulations
        for i in range(self.get_sim_num()):
            # initialize the simulation
            sim = Simulation(self.list_sim[col_jd][i], \
                    self.list_sim[col_jn][i], \
                    self.list_sim[col_si][i])
            # get the hysteresis data
            if sim.has_key('OT'):
                ot.append(sim.get_key_value('OT'))
                hys[i] = sim.parse_complex_modulus()['dynamic-mod'].to_list()
                if len(hys[i]) > max_cycle:
                    max_cycle = len(hys[i])
            # remove the simulation
            del sim
        # add to the dataframe
        col_header = ['T', 'f']
        for i in range(max_cycle):
            col_header.append(i)
        df = pd.DataFrame(index=range(self.get_sim_num()),columns=col_header)
        for i in range(self.get_sim_num()):
            df.loc[i, 'T'] = ot[i]
            df.loc[i, 'f'] = 2. * math.pi / ot[i]
            for j in range(len(hys[i])):
                df.loc[i,j] = hys[i][j]
        # return the data frame to the user
        return df

    def show_dynamic_modulus (self, period = False, save = False):
        """ displays the dynamic modulus for all simulations against frequency.

        Parameters:
        -----------
        period : bool
            if 'True', dynamic modulus is shown against period.
        save : bool (default 'False')
            if 'True', saves display to job directory.

        Returns:
        --------
        None

        """
        # get work for simulations within set
        df = self.get_dynamic_modulus()
        # determine how cycles were performed
        c = list(df.columns.values)
        i = 0
        while True:
            i += 1
            if i in c:
                continue
            else:
                i -= 2
                break
        # display the results
        fig = Figure()
        if period:
            fig.load_data(df, xcol='T', ycol = i)
        else:
            fig.load_data(df, xcol = 'f', ycol = i)
        fig.set_xaxis_scale(log = True)
        if period:
            fig.set_xaxis_scale("Cycle Perid ($s$)")
        else:
            fig.set_xaxis_label("Frequency (Hz, $2 \\pi T^{{-1}}$)")
        fig.set_yaxis_label("Dynamic Modulus ($Pa$)")
        fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = 'dynamic_modulus')
        gen_plot(fig, show = True, save = save)

    ## ANALYSIS - ELEMENT VALUES ##

    def get_steady_state_element_property_values (self, sim = None, prop = None, elm = None, reduced_time = None, cycle = None):
        """ returns the steady state element values for all simulations at a certain time point.

        Parameters:
        -----------
        sim : int or List[int]
            subset of simulations within Sweep object, identified by their integer number
        prop : str
            element property contained in simulation data.
        elm : int or List[int]
            elmements which contain property values in property data.
        reduced_time : float between 0. and 1.
            time point along periodic simulation oscillation, where 0. corresponds to the beginning and 1. to the end.
        cycle : int (optional)
            specify a specific cycle number to extract steady state data from.

        Returns:
        --------
        DataFrame
            contains simulation number, element number, property value, and simulation period
        """
        # if any simulations were specified
        if sim is None:
            sim = [i for i in range(self.get_sim_num())]
        elif isinstance(sim, int):
            # if the simulation specified is just one integer
            # repackage as a list
            sim = [sim]
        elif isinstance(sim, list):
            # check each item in the list
            for i in range(len(sim) -1, -1, -1):
                # remove items that are not integers, or that are not in the simulation list
                if (not isinstance(sim[i], int)):
                    print("ERROR :: Simulation.get_steady_state_element_property_values() :: item number '{0}' in method argument 'sim' ('{1}') is not of type 'int', removing from list.".format(i, sim.pop(i)))
                elif (not self.has_simulation(sim[i])):
                    print("ERROR :: Simulation.get_steady_state_element_property_values() :: item number '{0}' in method argument 'sim' corresponds to an integer that does not exist within the object.".format(i, sim.pop(i)))
            # check if there are any items in the list
            if (len(sim) == 0):
                print("ERROR :: Simulation.get_steady_state_element_property_values() :: method argument 'sim' is an empty list.")
                return None

        df = pd.DataFrame.from_dict({})
        # iterate through simulations
        for i in sim:
            s = self.get_simulation(i)
            period = s.get_oscillation_phase_period() # simulation oscillation period
            temp_df = s.get_steady_state_property_values (prop = prop, elm = elm, reduced_time = reduced_time, cycle = cycle)
            # transform data frame
            prop_list = []
            elements = []
            for j in list(temp_df.columns.values):
                if j != 'Time':
                    elements.append(j)
                    prop_list.append(temp_df.iloc[0][j])
            temp_df = pd.DataFrame.from_dict({'sim': [i for k in range(len(prop_list))], 'elm': elements, prop: prop_list, 'period': [period for k in range(len(prop_list))]})
            # append data frame and repeat
            if i == 0:
                df = temp_df
            else:
                df = pd.concat([df, temp_df], ignore_index = True)
        return df

    def show_steady_state_element_property_profile (self, sim = None, prop = None, elm = None, ax = None, reduced_time = 0.75, show = True, save = False):
        """ display the steady steady profile for a property at a certain time point.

        Parameters:
        -----------
        sim : int or List[int]
            subset of simulations within Sweep object, identified by their integer number
        prop : str
            element property contained in simulation data.
        ax : str
            one of three spatial coordinates ('x', 'y', or 'z') that also exist in element property data.
        elm : int or List[int]
            elmements which contain property values in property data.
        reduced_time : float between 0. and 1.
            time point along periodic simulation oscillation, where 0. corresponds to the beginning and 1. to the end.
        cycle : int (optional)
            specify a specific cycle number to extract steady state data from.


        Returns:
        --------
        Figure
            Figure object containing data and formatting.
        """
        ## check method arguments
        # check if any simulations were specified
        if sim is None:
            # get simulations centering around the resonant simulation
            res_int = self.get_resonant_simulation_int()
            max_int = self.get_sim_num() - 1
            mid_low = math.floor((res_int - 1) / 2)
            mid_high = math.ceil(res_int + (max_int - res_int) / 2)
            sim = [1, mid_low, self.get_resonant_simulation_int(), mid_high, self.get_sim_num() - 1]
            # find some simulation which are at timescales greater than and lower than the resonant time scale
        elif isinstance(sim, int):
            # if the simulation specified is just one integer
            # repackage as a list
            sim = [sim]
        elif isinstance(sim, list):
            # check each item in the list
            for i in range(len(sim) -1, -1, -1):
                # remove items that are not integers, or that are not in the simulation list
                if (not isinstance(sim[i], int)):
                    print("ERROR :: Simulation.show_steady_state_element_property_profile() :: item number '{0}' in method argument 'sim' ('{1}') is not of type 'int', removing from list.".format(i, sim.pop(i)))
                elif (not self.has_simulation(sim[i])):
                    print("ERROR :: Simulation.show_steady_state_element_property_profile() :: item number '{0}' in method argument 'sim' corresponds to an integer that does not exist within the object.".format(i, sim.pop(i)))
            # check if there are any items in the list
            if (len(sim) == 0):
                print("ERROR :: Simulation.show_steady_state_element_property_profile() :: method argument 'sim' is an empty list.")
                return None

        # check the axis that was specified
        if ax is None or ax not in ['z', 'y', 'x']:
            ## error
            print("ERROR :: Simulation.show_steady_state_element_property_profile() :: method argument 'ax' not specified or not specified as an allowable axis.")
            return None
            ## TODO check for axis in element property data

        # get data, generate figure
        fig = Figure()
        df_prop = self.get_steady_state_element_property_values(sim = sim, prop = prop, elm = elm, reduced_time = reduced_time)
        df_ax = self.get_steady_state_element_property_values(sim = sim, prop = ax, elm = elm, reduced_time = reduced_time)
        for i in df_prop['period'].unique():
            x_dat, y_dat = [], []
            df_prop_tmp = df_prop.loc[df_prop['period'] == i]
            df_ax_tmp = df_ax.loc[df_ax['period'] == i]
            for idx, row in df_prop_tmp.iterrows():
                x_dat.append(df_ax_tmp[ax][idx])
                y_dat.append(df_prop_tmp[prop][idx])
            fig.append_lists(xlist = x_dat, ylist = y_dat, label = "f = {:.2e}".format(2 * math.pi / i))
        # add formatting, show the figure
        fig.set_axis_label('x', ax)
        fig.set_axis_label('y', prop)
        fig.set_subtitle_label("$T_{{res}}$ = {:.2e}".format(self.get_simulation(self.get_resonant_simulation_int()).get_key_value('OT')))
        if save:
            fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = "{0}-{1}".format(prop.replace(" ", "-"), ax))
        gen_plot(fig, show = show, save = save)
        # return the figure with the data
        return fig


## ARGUMENTS
# none


## SCRIPT
# none
