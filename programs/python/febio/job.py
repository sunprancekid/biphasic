
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 06.02.2026

## FILENAME: programs/python/febio/job.py
## PURPOSE: contains classes and methods for handling febio simulation

## MODULES
# native / conda
import os, sys, math
import pandas as pd
# local
# none

## PARAMETERS
# format of config file
config_file_format = "{0}/{1}/{1}.config.csv"
# header used for config files
config_header = ['key', 'xml', 'description', 'units', 'constant', 'related', 'symbolic', 'val', 'min_val', 'max_val', 'n_val', 'log']

## METHODS
# none

## CLASSES
# job class
class Job (object):

    """ handles simulations en batch.

    Attributes:
    -----------
    None

    Methods
    -------
    None
    """

    def __init__ (self, jd, jn):
        """ initialize the job name and directory. load configuration files if they exists.

        Parameters:
        -----------
        jd : str
            path to the job directory
        jn : str
            job name in job directory

        Returns:
        --------
        Job
            initialized Job object.
        """
        ## assign the job name and directory
        self.jd = jd
        self.jn = jn
        ## load the config file
        if self.has_config():
            self.load_config()
        else:
            # create an empty config
            self.df_config = pd.DataFrame(columns = config_header)
        ## if the paths do not exist,

    def has_config(self):
        """ check if config file exists in job directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        bool
            'True' if file exists in job directory, else 'False'.
        """
        return (os.path.exists(config_file_format.format(self.jd, self.jn)))

    def load_config (self):
        """ load config file into Job from simulation directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.df_config = pd.read_csv(config_file_format.format(self.jd, self.jn))
        # check if the config file has all of the headers
        for h in config_header:
            # if the column is not in config file header already
            if h not in list(self.df_config.columns):
                # append an empty list to the column 
                self.df_config[h] = ['na' for i in range(len(self.df_config.index))] 
                ## TODO :: there is an option to get the information pertaining to each key from the parm file for config files that already exist and use an older version ... 

    def save_config (self, overwrite = False):
        """ save the config file to the job directory.

        Parameters:
        -----------
        overwrite : bool (default 'False')
            if the config file exists, will not overwrite unless 'True'

        Returns:
        --------
        None
        """
        if not self.has_config() or overwrite:
            if not os.path.exists("{0}/{1}".format(self.jd, self.jn)):
                os.makedirs("{0}/{1}".format(self.jd, self.jn))
            self.df_config.to_csv(config_file_format.format(self.jd, self.jn), index = False)
        else:
            print("ERROR :: Job.save_config() :: Config file '{0}' already exists. Unable to write without 'overwrite'.".format(config_file_format.format(self.jd, self.jn)))

    def add_parameters (self):
        """ adds parameters to config.

        Parameters:
        -----------
        p : Parameter
            parameter object

        Returns:
        --------
        None
        """
        pass
        ## TODO create parameter object

    def add_constant_parameter (self, val = None, key = None, xml = None, units = None, description = None, related = False, symbolic = False):
        """ add constant parameter to config file.

        Parameters:
        -----------
        val : float, int, or str
            value or equation as str
        key : str
            id representing parameter, used as column header in parameter file
        xml : str or None
            (optional) xml path to parameter in feb file
        units : str
            (optional) units assigned to parameter
        description : str
            (optional) short description of parameter
        related : bool
            if 'True', 'val' uses other parameter's 'key's and must be evaluated.
        symbolic : bool
            if 'True', 'val' uses other parameter's 'key's but should not be evaluated.

        Returns:
        --------
        bool 
            'True' if operation was successful, else 'False'.
        """

        # check method arguments
        if val is None:
            print("ERROR :: Job.add_constant_parameter() :: 'val' must be assigned as 'float', 'int', or 'str'.")
            return False
        if key is None:
            print("ERROR :: Job.add_constant_parameter() :: 'key' representing parameter must be assigned.")
            return False

        # replace None types with 'na'
        if xml is None:
            xml = 'na'
        if units is None:
            units = 'na'
        if description is None:
            description = 'na'

        # reassign booleans
        if related:
            related = 1
        else:
            related = 0
        if symbolic:
            symbolic = 1
        else:
            symbolic = 0

        # create array, add to config file
        parm = {config_header[0]: key,
                config_header[1]: xml,
                config_header[2]: units,
                config_header[3]: description,
                config_header[4]: 1,
                config_header[5]: related,
                config_header[6]: symbolic,
                config_header[7]: val}
        self.df_config.loc[len(self.df_config.index)] = parm



    ## generate parameters with model

## ARGUMENTS
# none

## SCRIPT
# none
