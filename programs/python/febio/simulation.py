
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
        self.file_log = "{0}/{1}/{2}/{3}.log".format(jd, jn, self.parm['path'], self.parm['id'])
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
        extract_febio_out(d = self.sd, f = '{0}.log'.format(self.parm['id']))
        # get displacement and force
        calculate_displacement (d = self.sd, f = default_outfile,  z = True)
        calculate_force (d = self.sd, f = default_outfile, z = True, y = True, x = True)
        # calculate work
        calculate_work(d = self.sd, f = default_outfile, x_col = 'z', v_col = 'vz', f_col = 'Fz', t_col = 't')

        # operation completed succesfully
        return True

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
        """ get the values for one propery, with optional time and element specification.

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
        rt_idx = 0 # current index for the return dataframe\
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
            print(idx_timelist, rt_idx, idx_propdf)
            idx_propdf += 1
            if idx_propdf == len(self.elm_data[prop]): break
        # return the data frame
        return df_return

    def show_steady_state_property_profile (self, prop = None, ax = None, init = True, ax_norm = None, n_sample = None):
        """"""
        # according to period, determine start and end of second to last cycle
        # pick a few points that are distributed in time along the cycle
        # condense data frame
        # plot
        pass

    ## ANALYSIS - HYSTERESIS ##

    def parse_complex_modulus (self):
        """ Use cyclic loading data to determing the dynamic modulus.

        Parameter:
        ----------
        None

        Returns:
        --------
        None

        """
        ## load module
        ## TODO :: move module above once hysteresis has been completely refactored
        from febio.analysis.hysteresis import calculate_complex_mod

        ## get data# get the relaxation time and oscaillation period
        if self.has_key('OT'):
            period = self.get_key_value('OT')
        else:
            print("ERROR :: Simulation.prase_hystersis_work() :: Unable to parse oscilation period 'OT' from config file.")

        if self.has_key('RT'):
            relax_time = self.get_key_value('RT')
        else:
            # get the relaxation time from the feb file
            # step size
            steps = float(self.get_feb_path_value(xml_relax_num_step))
            # number of steps
            size = float(self.get_feb_path_value(xml_relax_step_size))
            # calculate the relaxation time
            relax_time = size * steps

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

        ## pass to method
        delta, dymod = calculate_complex_mod(period, time, pos, force)

        ## return to user
        return delta, dymod

    def parse_prestress_work (self):
        """ calculate the work performed during the prestress phase

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        """
        ## get relevant the data
        # get the relaxation time
        if self.has_key('RT'):
            relax_time = self.get_key_value('RT')
        else:
            # get the relaxation time from the feb file
            # step size
            steps = float(self.get_feb_path_value(xml_relax_num_step))
            # number of steps
            size = float(self.get_feb_path_value(xml_relax_step_size))
            # calculate the relaxation time
            relax_time = size * steps

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
        if self.has_key('RT'):
            relax_time = self.get_key_value('RT')
        else:
            # get the relaxation time from the feb file
            # step size
            steps = float(self.get_feb_path_value(xml_relax_num_step))
            # number of steps
            size = float(self.get_feb_path_value(xml_relax_step_size))
            # calculate the relaxation time
            relax_time = size * steps

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
        if self.has_key('OT'):
            period = self.get_key_value('OT')
        else:
            print("ERROR :: Simulation.prase_hystersis_work() :: Unable to parse oscilation period 'OT' from config file.")

        if self.has_key('RT'):
            relax_time = self.get_key_value('RT')
        else:
            # get the relaxation time from the feb file
            # step size
            steps = float(self.get_feb_path_value(xml_relax_num_step))
            # number of steps
            size = float(self.get_feb_path_value(xml_relax_step_size))
            # calculate the relaxation time
            relax_time = size * steps

        # get the time and work from the outfile
        if recalculate:
            self.parse_logfile()
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
        if self.has_key('OT'):
            period = self.get_key_value('OT')
        else:
            print("ERROR :: Simulation.prase_hystersis_work() :: Unable to parse oscilation period 'OT' from config file.")

        if self.has_key('RT'):
            relax_time = self.get_key_value('RT')
        else:
            # get the relaxation time from the feb file
            # step size
            steps = float(self.get_feb_path_value(xml_relax_num_step))
            # number of steps
            size = float(self.get_feb_path_value(xml_relax_step_size))
            # calculate the relaxation time
            relax_time = size * steps

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
        # parse the period
        if self.has_key('OT'):
            period = self.get_key_value('OT')
        else:
            print("ERROR :: Simulation.prase_hystersis_work() :: Unable to parse oscilation period 'OT' from config file.")
        # get the hysteresis work
        hys = self.parse_hysteresis_work()

        print(hys)

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
