
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
from util.smoothie import log2lin, lin2log

## PARAMETERS
# format of config file
config_file_format = "{0}/{1}/{1}.config.csv"
# header used for config files
config_header = ['key', 'xml', 'description', 'units', 'constant', 'related', 'symbolic', 'val', 'min_val', 'max_val', 'n_val', 'log']
# format of parameter file
parameter_file_format = "{0}/{1}/{1}.parm.csv"
# header used for parameter file
parameter_header = ['n', 'id', 'path']

## METHODS
def gen_linear_scale_range (n, min_val, max_val):
    """ generate n, linearly seperated values.

    Parameters:
    -----------
    n : int
        total number of values to generate
    min_val : float
        lowest value in linear series
    max_val : float
        largest value in linear series

    Returns:
    --------
    List[float]
        list of n values which are linearly spaced.
    """
    if not isinstance(n, int):
        n = int(n)
    if not isinstance(min_val, float):
        min_val = float(min_val)
    if not isinstance (max_val, float):
        max_val = float(max_val)
    val = []
    for i in range(n):
        val.append(min_val + ((i) / (n - 1)) * (max_val - min_val))
    return val

def gen_log_scale_range (n, min_val, max_val):
    """ generate n, linearly seperated values.

    Parameters:
    -----------
    n : int
        total number of values to generate
    min_val : float
        lowest value in logarithmic series
    max_val : float
        highest value in logarithmic series

    Returns:
    List[float]
        list of n values which a logarithmically spaced.
    """
    # check the arguments
    if not isinstance(n, int):
        n = int(n)
    if not isinstance(min_val, float):
        min_val = float(min_val)
    if not isinstance(max_val, float):
        max_val = float(max_val)
    # convert min and max values to logscale
    min_val = lin2log(min_val)
    max_val = lin2log(max_val)
    # generate range
    val = []
    for i in range(n):
        tmp = min_val + ((i) / (n - 1)) * (max_val - min_val)
        val.append(log2lin(tmp))
    return val

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
        # assign the job name and directory
        self.jd = jd
        self.jn = jn
        # load the config file
        if self.has_config():
            self.load_config()
        else:
            # create an empty config
            self.df_config = pd.DataFrame(columns = config_header)
        # load the parameter file if it exists
        if self.has_parameters():
            self.load_parameters()
        else:
            self.df_parm = None

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

    def has_parameters (self):
        """ check if the parameter file exists within the job directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        bool 
            'True' if the parameter file exists, else 'False'.
        """
        return (os.path.exists(parameter_file_format.format(self.jd, self.jn)))

    def load_parameters (self):
        """ loads the parameter file, if it exists.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        pass

    def generate_parameters (self, overwrite = False):
        """ using config file, generate the job parameters.

        Parameters:
        -----------
        overwrite : bool (default 'False')
            if 'False', parameter file will not be overwritten if it exists.

        Returns:
        --------
        None
        """
        # check if the parameter file already exists
        if self.df_parm is not None and not overwrite:
            # parameters have already been generated / loaded and overwrite has not been called
            print("ERROR :: Job.generate_parameters() :: must specifiy 'overwrite' to overwrite existing parameters.")
            return

        # find the non-constant parameters, determine how many unique parameters exist
        nonconstant_col = []
        constant_col = []
        constant_col
        for idx, row in self.df_config.iterrows():
            # check if the column is non constant
            if row['constant'] == 0:
                nonconstant_col.append(row['key'])
            else:
                constant_col.append(row['key'])

        ## generate parameters
        # initialize lists for n ,id and path
        n = [1]
        sid = ['job']
        path = ['job/']

        # define the constant values
        con_dict = {} # dictionary for constant values
        if len(constant_col) > 0:
            for c in constant_col:
                # get the constant value from the config file
                idx = self.df_config.index[self.df_config['key'] == c]
                val = self.df_config.iloc[idx[0]]['val']
                con_dict.update({c: [val]})

        # define nonconstant values
        noncon_dict = {}
        if len(nonconstant_col) > 0:
            # for each of the non-constant columns
            n_parm_total = 1
            for c in nonconstant_col:
                # get the total number of parameters, range, etc.
                idx = self.df_config.index[self.df_config['key'] == c].tolist()
                n_parm = int(self.df_config.iloc[idx[0]]['n_val'])
                n_parm_total = n_parm * n_parm_total
                # generate values
                vals = []
                if self.df_config.iloc[idx[0]]['log'] == 1:
                    # generate parameters along a log scale
                    vals = gen_log_scale_range(n = self.df_config.iloc[idx[0]]['n_val'],
                                           min_val = self.df_config.iloc[idx[0]]['min_val'],
                                           max_val = self.df_config.iloc[idx[0]]['max_val'])
                else:
                    # generate parameters along a linear scale
                    vals = gen_linear_scale_range(n = self.df_config.iloc[idx[0]]['n_val'],
                                           min_val = self.df_config.iloc[idx[0]]['min_val'],
                                           max_val = self.df_config.iloc[idx[0]]['max_val'])
                # update non-constant parameters
                if len(noncon_dict) == 0:
                    # append the new column to the empty dictionary
                    noncon_dict.update({c: vals})
                    # update the n, sid, and path
                    n = list(range(1, len(vals) + 1))
                    sid = []
                    path = []
                    for i in n:
                        sid.append("{0}{1}".format(c, i))
                        path.append("job/{0}{1}/".format(c, i))
                else:
                    print("TODO :: Job.generate_parameters() :: implement 'generate_parameters' for multiple non-consants.")
                    exit()

            # update constant parameters
            if len(con_dict) > 0:
                # duplicate all of the constant parameters by the total parameters
                for k in list(con_dict.keys()):
                    nl = [] # new list
                    for i in con_dict[k]:
                        for j in range(n_parm_total):
                            nl.append(i)
                    con_dict[k] = nl # replace old list with new list

        # generate the new parameters dataframe
        self.df_parm = pd.DataFrame.from_dict({'n': n, 'id': sid, 'path': path} | con_dict | noncon_dict)

    def save_parameters (self, overwrite = False):
        """ save the parameters to the job directory

        Parameters:
        -----------
        overwrite : bool
            if 'True', overwrites existing parameter file.

        Return:
        -------
        None
        """
        if not self.has_parameters() or overwrite:
            if not os.path.exists("{0}/{1}".format(self.jd, self.jn)):
                os.makedirs("{0}/{1}".format(self.jd, self.jn))
            self.df_parm.to_csv(parameter_file_format.format(self.jd, self.jn), index = False)
        else:
            print("ERROR :: Job.save_config() :: Config file '{0}' already exists. Unable to write without 'overwrite'.".format(config_file_format.format(self.jd, self.jn)))

    def add_variable_parameter (self, minval = None, maxval = None, nval = None, log = False, key = None, xml = None, units = None, description = None, related = False):
        """ add variable parameter set to config file.

        Parameters:
        -----------
        minval : float, int, or str
            lowest value range of variable set.
        maxval : float, int, or str
            largest value in range of variable set.
        nval : int
            number of values to generate.
        key : str
            id representing parameter, used as column header in parameter file
        log : bool (default 'False')
            determines if values should be generated along a linear log scale
        xml : str (optional, default 'None')
            xml path to parameter in feb file
        units : str (optional, default 'None')
            units assigned to parameter
        description : str
            (optional) short description of parameter
        related : bool (default 'False')
            if 'True', 'val' uses other parameter's 'key's and must be evaluated.

        Returns:
        --------
        bool
            'True' if operation is successful, else 'False'.
        """
        # check method arguments
        if minval is None:
            print("ERROR :: Job.add_variable_parameter() :: 'minval' must be assigned as 'float', 'int', or 'str'.")
            return False
        if maxval is None:
            print("ERROR :: Job.add_variable_parameter() :: 'minval' must be assigned as 'float', 'int', or 'str'.")
            return False
        if nval is None:
            print("ERROR :: Job.add_variable_parameter() :: 'nval' must be assigned as 'int' greater than 1.")
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
        if log:
            log = 1
        else:
            log = 0

        # create array, add to config file
        parm = {config_header[0]: key,
                config_header[1]: xml,
                config_header[2]: units,
                config_header[3]: description,
                config_header[4]: 0,
                config_header[5]: related,
                config_header[6]: 0,
                config_header[7]: 'na',
                config_header[8]: minval,
                config_header[9]: maxval,
                config_header[10]: nval,
                config_header[11]: log}
        self.df_config.loc[len(self.df_config.index)] = parm

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
                config_header[7]: val,
                config_header[8]: 'na',
                config_header[9]: 'na',
                config_header[10]: 'na',
                config_header[11]: 'na'}
        self.df_config.loc[len(self.df_config.index)] = parm


## ARGUMENTS
# none

## SCRIPT
# none
