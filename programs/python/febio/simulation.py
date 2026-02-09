
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 06.02.2026

## FILENAME: programs/python/febio/simulation.py
## PURPOSE: contains classes and methods for handling febio simulation

## MODULES
# native / conda
import sys, os
import pandas as pd
import xml.etree.ElementTree as ET
# local
from febio.io.logfile import extract_febio_out, calculate_displacement, calculate_force, calculate_work

## PARAMETERS
# default outfile
default_outfile = 'febio4.out.csv'

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

    def parse_prestress_work (self):
        pass

    def parse_hystersis_work (self):
        pass

    def show_hystersis (self):
        pass

## ARGUMENTS
# none

## SCRIPT
# none
