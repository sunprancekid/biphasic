
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
import pandas as pd
import xml.etree.ElementTree as ET
# local
from febio.io.logfile import extract_febio_out, calculate_displacement, calculate_force, calculate_work
from plot.figure import Figure
from plot.plot import gen_bar_chart, gen_plot

## PARAMETERS
# default outfile
default_outfile = 'febio4.out.csv'
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
        # open parameter file, get parameters
        # open feb file, extract feb information (if needed)
        # check febio.out files, xplt files ...

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
