
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 06.02.2026

## FILENAME: programs/python/febio/simulation.py
## PURPOSE: contains classes and methods for handling febio simulation

## MODULES
# native / conda
import sys, os, math
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
# local
from febio.io.logfile import extract_febio_out, calculate_displacement, calculate_force, calculate_work, parse_element_data
from plot.figure import Figure
from plot.plot import gen_bar_chart, gen_plot

## PARAMETERS
# default outfile
default_outfile = 'febio4.out.csv'
# default file containing element data
default_elm_dat = 'elm.dat'
# prestress relaxation step size - xml path
xml_relax_step_size = "Step/step[@id='1']/Control/step_size"
# prestress relaxation number of steps - xml path
xml_relax_num_step = "Step/step[@id='1']/Control/time_steps"
# default color map used for steady state property profile graphs
# default_prop_profile_colormap = 'seismic'
default_prop_profile_colormap = 'berlin'
# default_prop_profile_colormap = 'bwr'
# name of complex modulus file
file_complex_modulus = "complex-modulus.csv"

## METHODS
# none

## CLASSES
# simulation class
class Simulation (object):

    """ handles febio simulation data.

    Attributes:
    -----------
    None

    Methods
    -------
    None
    """

    def __init__ (self, jd, jn, si):

        """ initialize simulation path using job directory.

        Parameter:
        ----------
        jd : str
            path to job directory
        jn : str
            job name
        si : int
            integer corresponding to the simulation number in the job

        Returns:
        --------
        None
        """
        ## TODO save simulation data to files within directories, to avoid recalculating things
        ## TODO seperate complex modulus to phase shift and dynamic modulus
        ## TODO add save statement requirements for files
        # get the row corresponding to the simulation from the parameter file
        df_parm = pd.read_csv("{0}/{1}/{1}.parm.csv".format(jd, jn))
        # parameters corresponding to simulation in job
        self.parm = df_parm.iloc[si - 1]
        # paths
        self.sd = "{0}/{1}/{2}".format(jd, jn, self.parm['path'])
        # files
        self.file_feb = "{0}/{1}/{2}/{3}.feb".format(jd, jn, self.parm['path'], self.parm['id'])
        self.file_out = "{0}/{1}/{2}/febio4.out.csv".format(jd, jn, self.parm['path'], self.parm['id'])
        self.file_xplt = "{0}/{1}/{2}/{3}.xplt".format(jd, jn, self.parm['path'], self.parm['id'])
        self.file_log = "{0}/{1}/{2}/febio4.job.out".format(jd, jn, self.parm['path'])
        self.file_elm_dat = "{0}/{1}/{2}/{3}".format(jd, jn, self.parm['path'], default_elm_dat)
        # contains simulation data
        self.elm_data = {}

    def get_simid (self):
        """ returns the id assigned to the simulation.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        return self.parm['id']

    def has_key (self, k):
        """ check if key exists as job parameter.

        Paramters:
        ----------
        k : str
            header in parameter file column

        Returns:
        --------
        bool
            bool determining if key exist in job parameter file
        """
        return (k in self.parm)

    def get_key_value (self, k):
        """ get key value for simulation from job parameters.

        Parameters:
        -----------
        k : str
            header in parameter file

        Returns:
        --------
        str
            value stored in parameter file
        """
        return self.parm[k]

    def get_simulation_path (self):
        """ returns path to simulation directory.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            path to simulation directory from 'jd'
        """
        return self.sd

    ## FEBFILE ##

    def feb_has_path (self, xml_path):
        """ determines if xml path exists in feb file.

        Parameters
        ----------
        xlm_path : str
            string in xml format

        Returns
        -------
        bool
            True if path exists in feb file, otherwise false.
        """
        tree = ET.parse(self.file_feb)
        root = tree.getroot()
        elm = root.findall(xml_path)
        return (len(elm) > 0)

    def get_feb_path_value (self, xml_path):
        """ get value stored in feb file from xml path.

        Parameters
        ----------
        xml_path : str
            string in xml format

        Returns
        -------
        str
            value stored in xml path as string
        """
        tree = ET.parse(self.file_feb)
        root = tree.getroot()
        elm = root.findall(xml_path)
        return elm[0].text

    ## OUTFILE ##

    def has_outfile (self):
        """ check if outfile exists in simulation directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        bool
            True if outfile exists in directory, else False.
        """
        return os.path.exists(self.file_out)

    def get_outfile(self):
        """ gets outfile information stored in csv.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        if not self.has_outfile():
            self.parse_logfile()

        return pd.read_csv(self.file_out)

    ## LOGFILE ##

    def has_logfile (self):
        """ check if the logfile exists in the simulation directory

        Parameters:
        -----------
        None

        Returns:
        --------
        bool
            True if the file exists in the simulation directory, else False.
        """
        return (os.path.exists(self.logfile))

    def parse_logfile (self, logfile = None, outfile = None):
        """ extract rigid body information from the logfile, write to outfile.

        Parameters:
        ----------
        logfile : str (optional)
            path to logfile (default is used if unspecified)
        outfile : str (optional)
            path to outfile (default is used if unspecified)

        Returns:
        --------
        bool
            True if operation was successful, else False.
        """
        # if a logfile was not sepecified, use the default
        if logfile is None:
            logfile = self.file_log
        # if an outfile was not specified, use the default
        if outfile is None:
            outfile = self.file_out

        # check if the logfile exists
        if not os.path.exists(logfile):
            print("ERROR :: Simulation.parse_logfile :: Unable able to parse logfile '{0}'. Path does not exist.".format(logfile))
            return False

        # parse the logfile, write to outfile
        extract_febio_out(d = self.sd, f = 'febio4.job.out')
        # get displacement and force
        calculate_displacement (d = self.sd, f = default_outfile,  z = True)
        calculate_force (d = self.sd, f = default_outfile, z = True, y = True, x = True)
        # calculate work
        calculate_work(d = self.sd, f = default_outfile, x_col = 'z', v_col = 'vz', f_col = 'Fz', t_col = 't')

        # operation completed succesfully
        return True

    ## SIMULATION PROPERTY - OSCILLATION ## 

    def has_oscillation_phase (self):
        """ determines if simulation has oscillation phase.

        The oscillation phase is determined by the config key 'OT',
        which contains the oscillation period. If the period key does
        not exist in the config file, then the simulation does not have
        an oscillation phase during the simulation. 

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if 'OT' exists in the config file, else 'False'.
        """
        return self.has_key('OT')

    def get_oscillation_phase_period (self):
        """ returns the oscillation phase period, if it exists.

        Arguments:
        ----------
        None

        Returns:
        --------
        float
            time assigned to simulation oscillation phase in simulation seconds.
        """
        if self.has_oscillation_phase():
            return self.get_key_value('OT')
        else:
            print("ERROR :: Simulation.get_oscillation_phase_period() :: simulation does not have a oscillation phase.")
            return None

    def get_oscillation_phase_frequency(self):
        """ returns the oscilation frequency, if it exists.

        Arguments:
        ----------
        None

        Returns:
        --------
        float
            frequency assigned to simulation oscillation phase in simulation seconds.
        """
        return 2 * math.pi / self.get_oscillation_phase_period()

    def get_number_oscillation_cycles (self):
        """ returns the number of cycles in the oscillation phase.

        The number of cycles is determined by the total simulation
        length. First the relaxation time is removed (if there is 
        a relaxation phase), then the remaining simulation length is
        divided by the oscillation period.

        Arguments:
        ----------
        None

        Returns:
        --------
        int
            number of complete cycles
        """
        # establish simulation period and relaxation time
        if not self.has_oscillation_phase():
            print("ERROR :: Simulation.get_number_oscillation_cycles() :: simulation does not have oscillation phase.")
        period = self.get_oscillation_phase_period()
        # get the simulation length
        time = max(self.get_outfile()['t'].to_list())
        time = time - self.get_relaxation_phase_length()
        # determine the number of cycles
        err = []
        n_cyc = 1
        while True:
            err.append(time - n_cyc * period)
            if len(err) > 1:
                # is the error decreasing?
                if abs(err[-1]) > abs(err[-2]):
                    # error increased from the previous calculation
                    # the previous integer was the closest to the period
                    n_cyc -= 1
                    break
                else:
                    n_cyc += 1
            else:
                n_cyc += 1
        return n_cyc

    ## SIMULATION PROPERTY - RELAXATION PEROID ##

    def has_relaxation_phase (self):
        """ determines if the simulation had a relaxation phase.

        The relaxation phase is determined by the existance of a key
        for the relaxation time ('RT) in the simulation config file.

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if the relaxation key exists, else 'False'.
        """
        return self.has_key('RT') or (self.feb_has_path(xml_relax_num_step) and self.feb_has_path(xml_relax_step_size))

    def get_relaxation_phase_length (self):
        """returns the length of the relaxation phase.

        For most simulations, the relaxation phase is stored in the 
        config file with the relaxation key. For depricated version, a
        relaxation value was not parameterized and instead stored within 
        the model file (hard coded).

        Arguments:
        ----------
        None

        Returns:
        --------
        float
            length of relxation phase in simulation seconds.
        """
        if self.has_relaxation_phase():
            if self.has_relaxation_phase():
                return self.get_key_value('RT')
            else:
                # get the relaxation time from the feb file
                # step size
                steps = float(self.get_feb_path_value(xml_relax_num_step))
                # number of steps
                size = float(self.get_feb_path_value(xml_relax_step_size))
                # calculate the relaxation time
                return size * steps
        else:
            return 0.

    ## ANALYSIS - ELEMENT DATA ##

    def has_element_data(self):
        """ check if element data exists for simulation.

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if default element data file exists in simulation directory.
        """
        return (os.path.exists(self.file_elm_dat))

    def parse_element_data(self, overwrite = True):
        """ parse element data from file.

        Arguments:
        ----------
        overwrite : bool
            overwrite existing data stored in object.

        Returns:
        --------
        None
        """
        if (not self.elm_data) or (overwrite):
            self.elm_data = parse_element_data(self.file_elm_dat)

    def get_element_data(self, overwrite = True):
        """ returns the element data associated with the simulation.

        Arguments:
        ----------
        overwrite : bool
            overwrite existing data stored in object.

        Returns:
        --------
        Dict[DataFrame]
            dictionary which contains frames containing element data across simulation time for each property.
        """
        if not self.has_element_data(): return None
        self.parse_element_data(overwrite)
        return self.elm_data

    def element_data_has_property(self, prop):
        """check if property exists within element data.

        Arguments:
        ----------
        prop : str
            propery to check for in element data keys list.

        Returns:
        --------
        bool
            'True' if property exists in element data, else 'False'.
        """
        return (prop in list(self.elm_data.keys()))

    def get_properties_in_element_data(self):
        """ returns list of properties stored within element data.

        Arguments:
        ----------
        None

        Returns:
        --------
        List[str]
            list of all properties stored within element data, if any.
        """
        return list(self.elm_data.keys())

    def element_data_has_element(self, elm, prop = None):
        """ checks if element exists within elements that have element data.

        Arguments:
        ----------
        elm : int
            integer corresponding to element number
        prop : str (optional)
            specify propery data set to get element data for (in case of inconsistent data)

        Returns:
        --------
        bool
            'True' if element exists within list, else 'False'
        """
        return (elm in self.get_elements_in_element_data(prop))

    def get_elements_in_element_data(self, prop = None):
        """ returns elements which has element data.

        Arguments:
        ----------
        prop : str (optional)
            specify propery data set to get element data for (in case of inconsistent data)

        Returns:
        --------
        List[int]
        """
        if prop is None: prop = self.get_properties_in_element_data()[0]
        if (self.elm_data):
            vals = list(self.elm_data[prop].columns.values)
            vals.pop(0) # remove the column header for steps
            vals.pop(0) # remove the column header for time
            return vals
        else:
            return []

    def get_time_in_element_data(self, prop = None):
        """ returns the time points associated with stored element property data.

        Arguments:
        ----------
        prop : str (optional)
            specify property corresponding to time point data to retrieve

        Returns:
        --------
        List[float]
            all time points in element data.
        """
        # check if the simulation has element data
        if not (self.elm_data):
            if self.has_element_data():
                self.parse_element_data()
            else:
                print("ERROR :: Simulation.get_time_in_element_data() :: Simulaton does not have element data.")
                return []
        # check method arguments
        if prop is None: 
            prop = self.get_properties_in_element_data()[0]
        elif not self.element_data_has_property(prop):
            print("ERROR :: Simulation.get_time_in_element_data() :: simulation element data does not contain property '{0}'.".format(prop))
            return []
        # get data
        if (self.elm_data):
            time = self.elm_data[prop]['Time'].tolist()
            for i in range(len(time)):
                if not isinstance(time[i], float):
                    time[i] = float(time[i])
            return time
        else:
            return []

    def element_data_has_time (self, t):
        """ checks if floating point number exists within time series data.
        
        Arguments:
        ----------
        t : float 
            floating point number greater than zero

        Returns:
        --------
        bool
            'True' if time point exists within element data, else 'False'.
        """
        time = self.get_time_in_element_data()
        if (time):
            # check the time point is greater than the min and max values
            return (t <= max(time)) and (t >= min(time))
        else:
            # the list is empty
            return False

    def get_property_values (self, prop = None, elm = None, time = None):
        """ get the values for one propery, at a specified simulation time and element.

        Arguments:
        ----------
        prop : str
            property that exists within element data.
        elm : int or List[int] (optional, default is all elements)
            subset of elements to return property data for.
        time : float or List[float] (optional, default is all time points)
            subset of time points to return propery data for.

        Returns:
        --------
        DataFrame
            ...
        """
        # if the element data for the simulation has not already been loaded
        if not (self.elm_data):
            # check if the simulation has element data already
            if not self.has_element_data():
                print("ERROR :: Simulation.get_property_values() :: Simulation does not have element data.")
                return None
            # otherwise, load the data
            self.parse_element_data()

        # check the property passed to the method
        if prop is None:
            print("ERROR :: Simulation.get_property_values() :: must specify method argument 'prop'.")
            return None
        elif not isinstance(prop, str):
            print("ERROR :: Simulation.get_property_values() :: method argument 'prop' should be type 'str'.")
            return None
        elif not self.element_data_has_property(prop):
            print("ERROR :: Simulation.get_property_values() :: property '{0}' does not exist with element propery data.".format(prop))
            return None

        # check the specified elements
        if isinstance(elm, list):
            # check all items in list
            for i in range(len(elm) - 1, -1, -1):
                # transverse list in reverse order
                # check elm is an integer
                if not isinstance(elm[i], int):
                    # remove from list
                    print("ERROR :: Simulation.get_property_values() :: element in list 'elm' ({0}, {1}) is not type integer, removing.".format(i, elm[i]))
                # check if elm is in the list of accepted integer
                if not self.element_data_has_element(elm[i]):
                    # if not, remove from the list
                    print("ERROR :: Simulation.get_property_values() :: element in method argument list 'elm' ({0}, {1}) does not exist in element data for property '{2}', removing from list.".format(i, elm[i], prop))
            # check that there are still items in the list
            if len(elm) == 0:
                print("ERROR :: Simulation.get_property_values() :: element list 'elm' is empty.")
                return None
        elif isinstance(elm, int):
            # turn int into list int
            elm = [elm]
        elif elm is None:
            # if unspecified, elm is all elements corresponding to property
            elm = self.get_elements_in_element_data(prop)
        else:
            # elm should either be int or list int
            print("ERROR :: Simulation.get_property_values() :: method argument 'elm' must be either type 'int' or 'List[int]'.")
            return None

        # check the specified time points
        ## TODO :: check items in time list
        if isinstance(time, list):
            # check all points in the list
            for i in range(len(time) - 1, -1, -1):
                # transverse the list in reverse order
                # check that each item is a floating point number or an integer
                if not (isinstance(time[i], float) or isinstance(time[i], int)):
                    # the time point is not a floating point number or an integer
                    print("ERROR :: Simulation.get_property_values() :: time point in method argument list 'time' ({0}, {1}) is not of type 'int' or 'float', removing.".format(i , time.pop(i)))
                    continue
                # if it is an integer, cast as floating point number
                if isinstance(time[i], int):
                    time[i] = float(time[i])
                # check that the time point is within allowable range
                if not self.element_data_has_time(time[i]):
                    print("ERROR :: Simulation.get_property_values() :: time point in method argumet list 'time' ({0}, {1}) is outside the range of time points stored in the element data.".format(i, time.pop(i)))
                    continue
            if len(time) == 0:
                print("ERROR :: Simulation.get_property_values() :: argument method time list 'time' is empty.")
                return None
        else:
            ## TODO check that the time is within in the range
            if isinstance(time, float):
                # turn float into list float
                time = [time]
            elif isinstance(time, int):
                # turn int into list float
                time = [float(time)]
            elif time is None:
                # use all time points in list
                # TODO :: all items in list need to be type cast as flatoing point
                time = self.get_time_in_element_data(prop)
            else:
                # time should be either float or list float
                print("ERROR :: Simulation.get_property_values() :: method argment 'time' must be either type 'float' or 'List[float]'.")
                return None

        ## go through each point in element property list, append to df_return if meets criteria
        # NOTE :: this algorithm assumes that data in 'time' are ordered
        df_return = pd.DataFrame(columns = (['Time'] + elm)) # empty data frame
        # find the data that corresponds to the time point
        idx_timelist = 0 # current inedex in time list
        rt_idx = 0 # current index for the return dataframe
        idx_propdf = 1
        while True:
            # check if the current row in the property data frame meets the criteria
        # for i in range(1, len(self.elm_data[prop])):
            if abs(float(self.elm_data[prop].loc[idx_propdf, 'Time']) - time[idx_timelist]) > abs(float(self.elm_data[prop].loc[idx_propdf - 1, 'Time']) - time[idx_timelist]):
                # here, the previous time has lower error than the current time
                # the previous time point should be added to the return data frame
                # first, check to see if the algo is attemping to add a time point that is already in the list
                # print(df_return.head)
                if len(df_return) != 0:
                    print(df_return.loc[rt_idx - 1, 'Time'], self.elm_data[prop].loc[idx_propdf - 1, 'Time'])
                if (len(df_return) != 0) and (df_return.loc[rt_idx - 1, 'Time'] == self.elm_data[prop].loc[idx_propdf - 1, 'Time']):
                    # here, the time points in 'time' are too close together,
                    # and the same data points from 'elm_data[prop]' will be added to the return
                    # matrix a second time. So skip time point in 'time'
                    # NOTE :: switching to while loop will help solve this bug
                    idx_timelist += 1
                    if idx_timelist == len(time): break
                # append the current time point
                df_return.loc[rt_idx] = [np.nan for i in range(len(elm) + 1)]
                # return df_return
                df_return.loc[rt_idx, 'Time'] = float(self.elm_data[prop].loc[idx_propdf - 1, 'Time'])
                for e in elm:
                    df_return.loc[rt_idx, e] = self.elm_data[prop].loc[idx_propdf - 1, e]
                # increment indicies
                idx_timelist += 1
                rt_idx += 1
                # idx_propdf += 1
                # if idx_propdf == len(self.elm_data[prop]): break
                if idx_timelist == len(time): break
            # print(idx_timelist, rt_idx, idx_propdf)
            idx_propdf += 1
            if idx_propdf == len(self.elm_data[prop]): break
        # return the data frame
        return df_return

    def get_steady_state_property_values (self, prop = None, elm = None, reduced_time = None, cycle = None):
        """ get the property value for one or more elements at a specified point in time along oscillation profile.

        Arguments:
        ----------
        prop : str
            string desciribing property which is stored in element data file.
        elm : int or List[int]
            one or more elements containing property data (if unspecified, data for all elements are returned).
        reduced_time : float between zero and one
            time point along reduced simulation oscillation profile.
        cycle : int
            specific cycle number to return data for (if unspecified, second to last cycle is returned).

        Returns:
        --------
        DataFrame
            contains property values for specified (or all) elements at time point in simulation oscillation cycle.
        """
        ## CHECK ARGUMENTS AND OBJECT STATE
        # check element data
        if not (self.elm_data):
            # check if the simulation has element data already
            if not self.has_element_data():
                print("ERROR :: Simulation.get_steady_state_property_values() :: Simulation does not have element data.")
                return None
            # otherwise, load the data
            self.parse_element_data()

        # check property in element data
        if prop is None:
            print("ERROR :: Simulation.get_steady_state_property_values() :: must specify method argument 'prop'.")
            return None
        elif not isinstance(prop, str):
            print("ERROR :: Simulation.get_steady_state_property_values() :: method argument 'prop' should be type 'str'.")
            return None
        elif not self.element_data_has_property(prop):
            print("ERROR :: Simulation.get_steady_state_property_values() :: property '{0}' does not exist with element propery data.".format(prop))
            return None

        # check elements in element data
        if isinstance(elm, list):
            # check all items in list
            for i in range(len(elm) - 1, -1, -1):
                # transverse list in reverse order
                # check elm is an integer
                if not isinstance(elm[i], int):
                    # remove from list
                    print("ERROR :: Simulation.get_steady_state_property_values() :: element in list 'elm' ({0}, {1}) is not type integer, removing.".format(i, elm[i]))
                # check if elm is in the list of accepted integer
                if not self.element_data_has_element(elm[i]):
                    # if not, remove from the list
                    print("ERROR :: Simulation.get_steady_state_property_values() :: element in method argument list 'elm' ({0}, {1}) does not exist in element data for property '{2}', removing from list.".format(i, elm[i], prop))
            # check that there are still items in the list
            if len(elm) == 0:
                print("ERROR :: Simulation.get_steady_state_property_values() :: element list 'elm' is empty.")
                return None
        elif isinstance(elm, int):
            # turn int into list int
            elm = [elm]
        elif elm is None:
            # if unspecified, elm is all elements corresponding to property
            elm = self.get_elements_in_element_data(prop)
        else:
            # elm should either be int or list int
            print("ERROR :: Simulation.get_steady_state_property_values() :: method argument 'elm' must be either type 'int' or 'List[int]'.")
            return None

        # check reduced time
        if reduced_time is None:
            print("ERROR :: Simulation.get_steady_state_property_values() :: method argument 'reduced_time' must be specified as type 'float' between 0. and 1., inclusive.")
        elif isinstance(reduced_time, float) and ((reduced_time < 0.) or (reduced_time > 1.)):
            print("ERROR :: Simulation.get_steady_state_property_values() :: method argument 'reduced_time' must be specified as type 'float' between 0. and 1., inclusive.")

        # check cycle
        if cycle is None:
            cycle = self.get_number_oscillation_cycles()
            if cycle > 5:
                cycle -= 2
            elif cycle > 2:
                cycle -= 1
        elif isinstance(cycle, int) and (cycle <= 0):
            print("ERROR :: Simulation.get_steady_state_property_values() :: method argument 'cycle' must be specified as type 'int' 1 or greater.")

        ## GET DATA, RETURN
        # get period, relaxation time from simulation
        period = self.get_oscillation_phase_period()
        relax_time = self.get_relaxation_phase_length()

        # use cycle, reduced time to determine the simulation time point
        t = relax_time + period * (cycle - 1 + reduced_time)
        return self.get_property_values(prop = prop, elm = elm, time = t)

    def show_steady_state_property_profile (self, prop = None, ax = None, init = True, ax_norm = None, n_sample = 4, cmap = default_prop_profile_colormap):
        """ display a particular property values against one spatial coordinate across oscillation period.

        Arguments:
        ----------
        prop : str
            property that exists in simulation element data.
        ax : str
            one of three spatial coordinates ('x', 'y', or 'z') that also exist in property data.
        init : bool
            use the initialial spatial coordinates (t = 0), rather than those changing with time.
        ax_norm : float
            normalize the axis length by the maximum value occuring in the data series.
        n_sample : int (default is '5')
            number of points to sample along period frequency
        cmap : str
            string representing accepted matplotlib color map, used when generating figure

        Returns:
        --------
        None
        """

        # check that the element data has been loaded
        if not (self.elm_data):
            # check if the simulation has element data already
            if not self.has_element_data():
                print("ERROR :: Simulation.show_steady_state_property_profile() :: Simulation does not have element data.")
                return None
            # otherwise, load the data
            self.parse_element_data()

        # check that the property exists
        if prop is None:
            # must specify property values
            print("ERROR :: Simulation.show_steady_state_property_profile() :: must specify method argument 'prop'.")
            return None
        elif not isinstance(prop, str):
            # prop must be strng
            print("ERROR :: Simulation.show_steady_state_property_profile() :: method argument 'prop' should be type 'str'.")
            return None
        elif not self.element_data_has_property(prop):
            print("ERROR :: Simulation.show_steady_state_property_profile() :: property '{0}' does not exist with element propery data ({1}).".format(prop, self.get_properties_in_element_data))
            return None

        # check that the axis is right and also exists in the element data
        if ax is None or ax not in ['x', 'y', 'z']:
            # must specify coordinates
            print("ERROR :: Simulation.show_steady_state_property_profile() :: must specify axis coordinate frame 'ax' as either 'x', 'y', or 'z'.")
            return None
        elif ax not in self.get_properties_in_element_data():
            # axis data not in save element data
            print("ERROR :: Simulation.show_steady_state_property_profile() :: axis coordinate data '{0}' does not exist in element data.".format(ax))
            return None

        # check n_sample
        if n_sample is None or not isinstance(n_sample, int) or n_sample <= 2:
            # n_sample has not been provided correctly
            print("ERROR :: Simulation.show_steady_state_property_profile() :: must specify 'n_sample' as integer greater than 2.")
            return None

        # get the oscillation period and relaxation time
        period = self.get_oscillation_phase_period()
        relax_time = self.get_relaxation_phase_length()


        ## get the times corresponding to the start and end of the second to last cycle
        # get all time, drop relaxation time
        time = self.get_time_in_element_data()
        # reduce or drop time
        for i in range(len(time) - 1, -1, -1):
            # transverse list in reverse order
            if time[i] >= relax_time:
                time[i] = time[i] - relax_time
            else:
                time.pop(i)
        # determine the number of cycles
        err = []
        n_cyc = 1
        while True:
            err.append(time[-1] - n_cyc * period)
            if len(err) > 1:
                # is the error decreasing?
                if abs(err[-1]) > abs(err[-2]):
                    # error increased from the previous calculation
                    # the previous integer was the closest to the period
                    n_cyc -= 1
                    break
                else:
                    n_cyc += 1
        n_cyc -= 2 # use the second to last cycle
        t_start = period * n_cyc
        t_end = period * (n_cyc + 1)

        ## get data
        # pick a few points that are distributed in time along the cycle
        t = [ t_start + ((i) / (n_sample)) * (t_end - t_start) for i in range (1, n_sample + 1)]
        for i in range(len(t)):
            t[i] = t[i] + relax_time
        # get the property and axis data corresponding to the time points
        p = self.get_property_values(prop = prop, time = t)
        if init:
            # use the coordinates at time zero
            z = self.get_property_values(prop = ax, time = 0)
        else:
            z = self.get_property_values(prop = ax, time = t)

        # condense data frame, plot
        df_plot = pd.DataFrame()
        for i in range(len(p)):
            # establish index used for ax
            j = i
            if init:
                j = 0
            # append the data set to plot df
            label = (i + 1) / (n_sample)
            df_plot = pd.concat([df_plot, pd.DataFrame.from_dict({'prop': p.loc[i,1:].values.flatten().tolist(), 'ax_coor': z.loc[j,1:].values.flatten().tolist(), 'time': [label for k in range(len(self.get_elements_in_element_data()))]})])


        ## plot
        # estbalish labels
        xaxis_label = ""
        if ax == 'x':
            xaxis_label = "X-Axis Position (mm)"
        elif ax == 'y':
            xaxis_label = "Y-Axis Position (mm)"
        elif ax == 'z':
            xaxis_label = "Z-Axis Position (mm)"
        if init:
            xaxis_label = "Initial {0}".format(xaxis_label)
        yaxis_label = ""
        if prop == 'p':
            yaxis_label = "Fluid Pressure (MPa)"
        elif prop == 'effective stress':
            yaxis_label = "Effective Solid Stress (MPa)"
        else:
            yaxis_label = prop
        # generate and show figure
        fig = Figure()
        fig.append_df(df_plot, ycol = 'prop', xcol = 'ax_coor', icol = 'time')
        fig.set_cmap(cmap)
        fig.set_subtitle_label("T = {0:.2f}".format(period))
        fig.set_axis_label('x', xaxis_label)
        fig.set_axis_label('y', yaxis_label)
        fig.add_format("t / T = {:.2f}")
        gen_plot(fig, show = True, save = False)

    ## ANALYSIS - HYSTERESIS ##

    def parse_complex_modulus (self, overwrite = True):
        """ Use cyclic loading data to determing the complex modulus properties.

        complex modulus properties include phase shift (delta), storage modulus (G'), 
        loss modulus (G''), and dynamic modulus (G*).

        Data is stored in a local file corresponding to the simulation. If the
        file already exists locally, then the data is loaded from the file
        rather than calculated from the raw simulation data. If overwrite
        is specified, then the complex modulus data is recalculated regardless
        of if the local file exists or not.

        Parameter:
        ----------
        overwrite : bool
            determines if previously calculated complex modulus should be overwritten.

        Returns:
        --------
        DataFrame
            contains complex modulus properties for each oscillation cycle

        """
        ## load module
        ## TODO :: move module above once hysteresis has been completely refactored
        from febio.analysis.hysteresis import calculate_complex_mod

        ## TODO load from local file, if it already exists
        ## if not, calculate the data and save it to a local file

        if (not overwrite) and os.path.exists("{0}/{1}".format(self.sd, file_complex_modulus)):
            # load the file if overwrite has not been specified, and
            # and the file exists
            df = pd.read_csv("{0}/{1}".format(self.sd, file_complex_modulus))
        else:
            # overwrite has been specified or the file does not exist
            ## get data
            # get the relaxation time and oscaillation period
            period = self.get_oscillation_phase_period()
            relax_time = self.get_relaxation_phase_length()

            # get the time and work from the outfile
            time = self.get_outfile()['t'].to_list()
            pos = self.get_outfile()['disp'].to_list()
            force = self.get_outfile()['F_mag'].to_list()
            # drop the relaxation time from the work and time
            # reduce time
            for i in range(len(time) - 1, -1, -1):
                # transverse list in reverse order
                if time[i] >= relax_time:
                    time[i] = time[i] - relax_time
                else:
                    time.pop(i)
                    pos.pop(i)
                    force.pop(i)

            ## pass data to method
            df = calculate_complex_mod(period, time, pos, force)

            ## save data to local file
            df.to_csv("{0}/{1}".format(self.sd, file_complex_modulus), index  = False)

        # return to user
        return df

    def get_displacement_force_lag (self, cycle = None, norm = False, t_start = None, t_end = None):
        """ get the displacement and force corresponding to a certain cycle of a simulation.

        Arguments:
        ----------
        cycle : int (optinal, default is second to last cycle)
            cycle number
        norm : bool (optional, default is 'False')
            if 'True', normalize stress / strain values so that they are on a relative scale
        t_start : float (optional)
            specify the time point at which the stress / strain data should start
        t_end : float (optional)
            specify the time point at which the stress / strain data should end

        Returns:
        --------
        DataFrame
            contains displacement, force data, columns headers are 't', 'x', 'f'
        """
        # get the period, relaxation time from the simulation key
        period = self.get_oscillation_phase_period()
        relax_time = self.get_relaxation_phase_length()

        # determine the cycle number
        if cycle is None or not isinstance(cycle, int) or (cycle < 1):
            cycle = self.get_number_oscillation_cycles()
            # decriment according to total
            if cycle > 3:
                cycle -= 2
            elif cycle > 2:
                cycle -= 1

        # according to the cycle number, get the starting and stopping times for the cycle
        if t_start is None: t_start = relax_time + period * (cycle - 1)
        if t_end is None: t_end   = relax_time + period * (cycle)
        # parse the displacement and force data
        time = self.get_outfile()['t'].to_list()
        pos = self.get_outfile()['disp'].to_list()
        force = self.get_outfile()['Fz'].to_list() # NOTE z component of force
        # get the displacement and force data corresponding to the cycle
        f_plot = []
        p_plot = []
        t_plot = []
        for i in range(len(time)):
            if (time[i] <= t_end) and (time[i] >= t_start):
                t_plot.append(time[i])
                p_plot.append(-pos[i]) # NOTE negative position
                f_plot.append(-force[i]) # NOTE negative force
        # normalize data if requested
        if norm:
            # normalize the position, force data if requested
            max_force = max(f_plot)
            min_force = min(f_plot)
            max_position = max(p_plot)
            min_position = min(p_plot)
            for i in range(len(f_plot)):
                f_plot[i] = (f_plot[i] - min_force) / (max_force - min_force)
                p_plot[i] = (p_plot[i] - min_position) / (max_position - min_position)

        # create dataframe and return
        df = pd.DataFrame.from_dict({'t': t_plot, 'x': p_plot, 'f': f_plot})
        return df

    def show_displacement_force_lag (self, cycle = None, norm = False, show = True, save = False):
        """ display the stress-strain lag for a give cycle.

        Arguments:
        ----------
        cycle : int (optional, default is 'None')
            oscillation cycle number, must be one or greater.
        norm : bool (optional, default is 'False')
            if True, normalize the stress / strain values so that they are on a relative scale.
        show : bool (optional, default is 'True')
            if True, display figure with strss-strain data against time.
        save : bool (optional, default is 'False')
            if True, figure and dataset are saved to simulation folder.

        Returns:
        -------
        Figure
            object containing data, figure formatting.
        """
        ## CHECK ARGUMENTS
        # determine the cycle number
        if cycle is None or not isinstance(cycle, int) or (cycle < 1):
            cycle = self.get_number_oscillation_cycles()
            # decriment according to total
            if cycle > 3:
                cycle -= 2
            elif cycle > 2:
                cycle -= 1

        ## GET DATA
        df = self.get_displacement_force_lag(cycle = cycle, norm = norm)
        # establish labels
        if norm:
            df_unnorm = self.get_displacement_force_lag(cycle = cycle, norm = False)
            f_label = "Normalized Force \n($F_{{max}}$ = {:.1e}, $F_{{min}}$ = {:.1e})".format(df_unnorm['f'].max(), df_unnorm['f'].min())
            p_label = "Normalized Position \n($x_{{max}}$ = {:.1e}, $x_{{min}}$ = {:.1e})".format(df_unnorm['x'].max(), df_unnorm['x'].min())
        else:
            f_label = "Force"
            p_label = "Position"

        ## PLOT
        fig = Figure()
        fig.append_df (df = df, xcol = 't', ycol = 'f', label = f_label)
        fig.append_df (df = df, xcol = 't', ycol = 'x', label = p_label)
        fig.set_axis_label('x', "Simulation Time (seconds)")
        fig.set_axis_label('y', "Force / Position")
        if save:
            fig.set_saveas(savedir = self.sd, filename = "force-displacement-c{0}".format(cycle))
            fig.save_data()
        gen_plot(fig, show = show, save = save)

        # return figure
        return fig

    def parse_prestress_work (self):
        """ calculate the work performed during the prestress phase

        Parameters:
        -----------
        None4

        Returns:
        --------
        None

        """
        ## get relevant the data
        # get the relaxation time
        relax_time = self.get_relaxation_phase_length()

        # get the time and work performed
        time = self.get_outfile()['t'].to_list()
        work = self.get_outfile()['dw_fdx'].to_list()

        # drop any data after the relaxation time ends, accumulate the rest
        work_prestress = 0
        for i in range(len(time) - 1, -1, -1):
            if time[i] >= relax_time:
                time.pop(i)
                work.pop(i)
            else:
                work_prestress += work[i]

        # return the prestress work
        return work_prestress

    def show_prestress_work (self, show = True, save = False, savedir = None, filename = None):
        """ plot the work performed during prestress

        Paramters:
        ----------
        cycle : List[int] (optional, default all cycles)
            list of integers that represnt subset of cycles to display
        show : bool (optional, default True)
            display graph before saving
        save : bool (optional, default False)
            True if file should be saved, else False
        savedir : str or None (optional, default None)
            path to save directory (simulation directory is used if None)
        filename : str or None (optional, default is None)
            save file as ('hys' is used if None)

        Returns:
        --------
        List[float]
            time data for prestress phase
        List[float]
            displacement data for prestress phase
        List[float]
            force data for prestress phase

        """
        ## get the relevant data
        # get the relaxation time
        relax_time = self.get_relaxation_phase_length()

        # get the time and work performed
        time = self.get_outfile()['t'].to_list()
        force = self.get_outfile()['F_mag'].to_list()
        displacement = self.get_outfile()['disp'].to_list()
        work = self.parse_prestress_work()

        # drop any data after the relaxation time ends
        for i in range(len(time) -1, -1, -1):
            if time[i] >= relax_time or time[i] < 0.01:
                time.pop(i)
                force.pop(i)
                displacement.pop(i)

        # plot the data
        df = pd.DataFrame.from_dict({'disp': displacement, 'force': force, 'time': time})
        fig = Figure()
        fig.load_data(df, xcol = 'time', ycol = 'force')
        fig.set_xaxis_min(0.1)
        fig.set_xaxis_scale(log = True)
        fig.set_axis_scale('y', log = True)
        fig.set_subtitle_label("$W_{{prestress}} = {0:.2E}$".format(work))
        fig.set_xaxis_label("Time (s)")
        fig.set_yaxis_label("Force (N)")
        gen_plot(fig)

        # return data
        return time, displacement, force

    def parse_hysteresis_work (self, recalculate = False, norm = False):
        """ from the outfile, determing the hyesteresis performed during each cycle.

        Parameters:
        -----------
        norm : bool
            normalize hysteresis values by the pre-stress work
        recalculate : bool
            recalculate hysteresis even if files already exist

        Returns:
        --------
        List[float]
            work performed by each cycle which was fully completed.
        """
        # load the module
        ## TODO :: move this back above to the modules section once hystersis has been completely refactored
        ##          (right now it throughs a cyclical reference error)
        from febio.analysis.hysteresis import calculate_hysteresis_work

        ## TODO :: if the hystersis file already exists in the directory, just load the data from there

        # get the relaxation time and oscaillation period
        period = self.get_oscillation_phase_period()
        relax_time = self.get_relaxation_phase_length()

        # get the time and work from the outfile
        if recalculate or (not self.has_outfile()):
            self.parse_logfile()
        # else:
            # if 've' in self.sd:
            #     print(self.file_out)
            #     print(self.has_outfile())
            #     exit()
        time = self.get_outfile()['t'].to_list()
        work = self.get_outfile()['dw_fdx'].to_list()
        # drop the relaxation time from the work and time
        # reduce time
        for i in range(len(time) - 1, -1, -1):
            # transverse list in reverse order
            if time[i] >= relax_time:
                time[i] = time[i] - relax_time
            else:
                time.pop(i)
                work.pop(i)

        ## calculate work, return
        hys = calculate_hysteresis_work(period, time, work)
        if norm:
            psw = self.parse_prestress_work()
            for i in range(len(hys)):
                hys[i] = hys[i] / psw
        return (hys)

    def show_hysteresis (self, cycle = None, show = True, save = False, savedir = None, filename = None):
        """ show force displacement curve for cyclic loading.

        Paramters:
        ----------
        cycle : List[int] (optional, default all cycles)
            list of integers that represnt subset of cycles to display
        show : bool (optional, default True)
            display graph before saving
        save : bool (optional, default False)
            True if file should be saved, else False
        savedir : str or None (optional, default None)
            path to save directory (simulation directory is used if None)
        filename : str or None (optional, default is None)
            save file as ('hys' is used if None)

        Returns:
        --------
        List[float]
            displacement data for cyclic loading (or subset thereof)
        List[float]
            force data for cyclic loading (or subset thereof)

        """

        ## get the relevant data
        # get the period and the relaxation time
        period = self.get_oscillation_phase_period()
        relax_time = self.get_relaxation_phase_length()

        # get the time and work from the outfile
        time = self.get_outfile()['t'].to_list()
        disp = self.get_outfile()['disp'].to_list()
        force = self.get_outfile()['F_mag'].to_list()

        # drop the relaxation time from the work and time
        # reduce time
        for i in range(len(time) - 1, -1, -1):
            # transverse list in reverse order
            if time[i] >= relax_time:
                time[i] = time[i] - relax_time
                disp[i] = -disp[i]
            else:
                time.pop(i)
                disp.pop(i)
                force.pop(i)

        ## TODO :: if cycle_list is specified, use period to find the subset of cyclic loading data

        ## plot the data
        if show:
            df = pd.DataFrame.from_dict({'disp': disp, 'force': force})
            fig = Figure()
            fig.load_data(df, xcol = 'disp', ycol = 'force')
            fig.set_xaxis_label("Displacement (mm)")
            fig.set_yaxis_label("Force (N)")
            fig.set_subtitle_label("T = {0:.2f}".format(period))
            gen_plot(fig)

        return disp, force

    def show_hysteresis_work (self, show = True, save = False, savedir = None, filename = None):
        """ graph the work performed each hysteresis cycle.

        Paramters:
        ----------
        show : bool (optional, default True)
            display graph before saving
        save : bool (optional, default False)
            True if file should be saved, else False
        savedir : str or None (optional, default None)
            path to save directory (simulation directory is used if None)
        filename : str or None (optional, default is None)
            save file as ('hys' is used if None)

        Returns:
        --------
        List[float]
            list of work performed by cyclic loading each cycle
        """
        # get the hysteresis work
        hys = self.parse_hysteresis_work()

        # display and save
        df = pd.DataFrame.from_dict({'cycle': list(range(len(hys))), 'hys': hys})
        fig = Figure()
        fig.load_data(d = df, xcol = 'cycle', ycol = 'hys')
        fig.set_xaxis_label("Cycle Number")
        fig.set_yaxis_label("Energy Dissipated (J)")
        fig.set_cmap('Dark2')
        gen_bar_chart(fig, show = True, save = False)

        # return data
        return hys

## ARGUMENTS
# none

## SCRIPT
# none
