
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
from febio.simulation import Simulation
from febio.feb.model_file import ModelFile
from febio.analysis.scaling import scale
from plot.figure import Figure
from plot.plot import gen_plot
from plot.fit import Line, fit_line
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
# contains assumed scaling parameters for viscoelastic model
viscoelastic_normalization_dict = {'E': [1, 0], 'gamma': [1, 0], 'tau': [0, 1], 'k': [1, 0]}
# contains assumed scaling parameter for poroelastic model
poroelastic_normalization_dict = {'E': [1, -1], 'K': [0, -1], 'z': [3, 2]}

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

    ## TODO :: job handles creating directories and generates feb files.
    ## TODO :: somehow isolates model parameters from osilation and loading.
        - LD is a special parameter set that can be added via methods
        - OT is a special parameter set that can be added via methods
        - when generating parameters, LD and OT are created last
        - when creating directories, sub-jobs are created in which constant parameters 
            are added (variable in main job) and only parameters dealing with oscillation are
            variedclass Job (object):

        - main job has special config files which point to individual sweeps
    ## TODO :: add parameters to existing jobs without having to re-run everything
    ## TODO :: re-calculate certain values upon request (e.g. if re-running)

    Attributes:
    -----------
    None

    Methods:
    --------
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

    ## SIMULATION ##

    def has_simulation (self, n):
        """ determines if simulation number exists in job.

        Parameters:
        -----------
        n : int
            integer corresponding to simulation in parameter file.

        Returns:
        --------
        bool
            'True' if Job has Simulation, else 'False'
        """
        if self.has_parameters():
            return (n in self.df_parm['n'].tolist())
        else:
            return False

    def get_simulation (self, n):
        """ returns Simulation corrseponding to integer.

        Parameters:
        -----------
        n : int
            integer specifiying simulation in parameter file.

        Returns:
        --------
        Simulation
            simulation object corresponding to integer.
        """
        if self.has_simulation(n):
            return Simulation(self.jd, self.jn, n)
        else:
            return None

    def get_sim_num(self):
        """ returns the integer number of simulations associated with job.

        Arguments:
        ----------
        None

        Returns:
        --------
        int
            number of simulations associated with job.
        """
        return len(self.df_parm['n'].tolist())

    ## CONFIG ##

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

    ## PARAMETERS ##

    def get_key_value (self, key, n):
        """ get key value corresponding to simulation set.

        Arguments:
        ----------
        key : str
            corresponds to parameter in config and parameter files
        n : int
            specific simulation integer in job

        Returns:
        --------
        float or str
            value corresponding to key stored in parameter / config files
        """
        # check that they key exists
        # check that simulation integer is in job
        # get key value
        pass

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
        self.df_parm = pd.read_csv(parameter_file_format.format(self.jd, self.jn))

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
                    # update n, sid, and path
                    # n is the new total number of parameters
                    n = list(range(1, n_parm_total + 1))
                    sidn = [] # new sid list
                    pathn = [] # new path list
                    for i in range(len(sid)):
                        for j in range(n_parm):
                            sidn.append("{0}{1}{2}".format(sid[i],c,j))
                            pathn.append("{0}{1}{2}/".format(path[i],c,j))
                    # replace the old list with the new list
                    sid = sidn
                    path = pathn
                    # update the previous nonconstant parameters
                    for k in list(noncon_dict.keys()):
                        kn = [] # new list for key
                        for i in noncon_dict[k]:
                            for j in range(n_parm):
                                kn.append(i)
                        # print old list with new list
                        noncon_dict[k] = kn
                    # add the new non-constant parameter to the dict
                    v = []
                    for i in range(int(n_parm_total / n_parm)):
                        for j in vals:
                            v.append(j)
                    noncon_dict.update({c: v})

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

    def get_variable_parameter_range (self, key = None, description = None):
        """ looks for key in parameter file, returns range (min and max values).

        if the key does not exist in the job, None types are returns. if the
        key does not exist, but a description is provided, then a description
        is used to find the parameter.

        Arguments:
        ----------
        key : str
            key value associated with parameter.
        description : str
            description associated with parameter.

        Returns:
        --------
        int
            minimum value associated with variable parameter
        int
            maximum value associated with variable parameter
        """
        has_key = False
        has_descrip = False
        # check if the key exists in the config file
        if key in self.df_config['key'].tolist(): has_key = True
        # check if the description exists in the config file
        if description in self.df_config['description'].tolist(): has_descrip = True

        # if neither key or description matches, return None
        if (not has_key) and (not has_descrip): return None

        # otherwise parse the constant value, and return
        if has_key:
            return self.df_config.loc[self.df_config['key'] == key]['min_val'].tolist()[0], self.df_config.loc[self.df_config['key'] == key]['max_val'].tolist()[0]
        elif has_descrip:
            return self.df_config.loc[self.df_config['description'] == description]['min_val'].tolist()[0], self.df_config.loc[self.df_config['description'] == description]['max_val'].tolist()[0]

    def get_variable_parameter_number (self, key = None, description = None):
        """ gets the variable number ('n_val') assigned to a variable parameter.

        Arguments:
        ----------
        key : str
            key value associated with parameter.
        description : str
            description associated with parameter.

        Returns:
        --------
        int
            minimum value associated with variable parameter
        """
        has_key = False
        has_descrip = False
        # check if the key exists in the config file
        if key in self.df_config['key'].tolist(): has_key = True
        # check if the description exists in the config file
        if description in self.df_config['description'].tolist(): has_descrip = True

        # if neither key or description matches, return None
        if (not has_key) and (not has_descrip): return None

        # otherwise parse the constant value, and return
        if has_key:
            return self.df_config.loc[self.df_config['key'] == key]['n_val'].tolist()[0]
        elif has_descrip:
            return self.df_config.loc[self.df_config['description'] == description]['n_val'].tolist()[0]

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

    def get_constant_parameter_value (self, key = None, description = None):
        """ gets the constant value assigned to a parameter.

        Arguments:
        ----------
        key : str
            key value associated with parameter.
        description : str
            description associated with parameter.

        Returns:
        --------
        float or str
            value associated with parameter, either as float or string
        """
        has_key = False
        has_descrip = False
        # check if the key exists in the config file
        if key in self.df_config['key'].tolist(): has_key = True
        # check if the description exists in the config file
        if description in self.df_config['description'].tolist(): has_descrip = True

        # if neither key or description matches, return None
        if (not has_key) and (not has_descrip): return None

        # otherwise parse the constant value, and return
        if has_key:
            return self.df_config.loc[self.df_config['key'] == key]['val'].tolist()[0]
        elif has_descrip:
            return self.df_config.loc[self.df_config['description'] == description]['val'].tolist()[0]

    ## MODEL ##

    def generate_parameterized_models (self, m, overwrite = False):
        """ generates and saves models for each simulation set in job to simulation directory.

        Arguments:
        ----------
        m : str or ModelFile
            if string, path to loadable ModelFile object.
        overwrite : bool
            if 'True' overwrites existing model files in simulation directory.

        Returns:
        --------
        bool
            'True' if operation was successful, else 'False'
        """
        ## NOTE :: parameters and config files must already be generated for this to work.
        # load model
        if isinstance(m, str):
            # the string should be a path to the model
            m = ModelFile(m)
        elif (not isinstance(m, ModelFile)):
            print("ERROR :: Job.generate_parameterized_models() :: method argument 'm' must be either type 'ModelFile' or 'str'.")
            return False

        # check that model has all xml paths specified in config file
        for idx, row in self.df_config.iterrows():
            if (row['xml'] != 'na') and (not m.tree_has_element(row['xml'])):
                print("ERROR :: Job.generate_parameterized_models :: xml path '{0}' for key '{1}' in job config '{2}' does not exist in model file.".format(row['xml'], row['key'], config_file_format.format(self.jd, self.jn)))
                return False

        # loop through each simulation in job
        for i in range(1, self.get_sim_num() + 1):
            # generate model file
            sm = self.parameterize_model(m = m, n = i)
            s = Simulation(self.jd, self.jn, i)
            # if the simulation directory does not exist already, make it
            if not os.path.exists(s.get_simulation_path()): os.makedirs(s.get_simulation_path())
            # save to simulation directory
            sm.save_model(saveto = s.get_simulation_path(), saveas = "{0}-{1}.feb".format(self.jn, i), overwrite = overwrite)
            # exit for debugging
            exit()

        return True

    def parameterize_model (self, m, n):
        """ create model file which is parameterized to fit a specific simulation set.

        Arguments:
        ----------
        m : str or ModelFile
            if string, path to loadable ModelFile
        n : int
            corresponds to specific simulation integer in job

        Returns:
        --------
        ModelFile
            model with parameters adjusted to match simulation set.
        """
        # load model
        if isinstance(m, str):
            # the string should be a path to the model
            m = ModelFile(m)
        elif (not isinstance(m, ModelFile)):
            print("ERROR :: Job.parameterize_model() :: method argument 'm' must be either type 'ModelFile' or 'str'.")
            return False

        # loop through each parameter in config file
        for idx, row in self.df_config.iterrows():
            if row['xml'] == 'na': continue
            ## TODO :: here, it possible to encapsulate this method into a routine that
            ##         that is callable by the object (ergo, reusable)
            if row['constant'] == 1:
                # if the value is constant
                if row['related'] == 0
                    # the value is not related to any other values
                    m.update_element_value(elm_path = row['xml'], value = row['val'])
                else:
                    # the parameter value is dependent on other parameters
                    pass
            else:
                # the value is variable, use key to parse value from parameter file
                m.update_element_value(elm_path = row['xml'], value = self.df_parm[row['key']][i])

        # get dependencies
        # augment
        # return model
        return m

    ## SCALING ANALYSIS ##

    def show_hysteresis(self, n = None, show = True, save = False):
        """ show hystersis loops for multiple simulations in job.

        Arguments:
        -----------
        n : int or List[int]
            one or more integers corresponding to simulaitons in job.
        show : bool
            display figure
        save : bool
            save figure to results directory

        Returns:
        --------
        None
        """
        # if n is a single integer, make it an integer list
        if isinstance(n, int):
            n = [n]

        # initialize the figure
        fig = Figure()
        # loop through each item in the list
        for i in n:
            # check that i is an integer
            if not isinstance(i, int):
                print("ERROR :: Job.show_hysteresis() :: Unable to parse simulaiton '{0}' from Job, not an integer.".format(i))
            # check that i is a simulation in the job
            if not self.has_simulation(i):
                print("ERROR :: Job.show_hysteresis() :: Simulation '{0}' does not exist in job.".format(i))

            # get simulation, get hysteresis data, append to Figure
            s = self.get_simulation(i)
            d, f = s.show_hysteresis(show = False)
            fig.append_lists(xlist = d, ylist = f, label = s.get_simid())

        # plot the figure
        fig.set_xaxis_label("Displacement (mm)")
        fig.set_yaxis_label("Force (N)")
        if save:
            fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = 'simulation-hysteresis')
            fig.save_data()
        gen_plot(fig, show = show, save = save)

    def hysteresis_scaling(self, period = False, recalculate = False, fit = True, show = True, save = False):
        """ determing the scaling of hysteresis with respect to non-constant parameters.

        Parameters:
        -----------
        period : bool
            if 'True', plot scaling as a function of period rather than frequency.
        recalculate : bool
            recalculate hysteresis even if files exist
        fit : bool
            boolean determines if scaling should be fit to power law
        show : bool
            boolean determines if graphs are displayed
        save : bool
            boolean determines if graphs are saved

        Returns:
        --------

        """
        # determine constant and non-constant parameters
        noncon_col = []
        noncon_dict = {}
        con_col = []
        for idx, row in self.df_config.iterrows():
            if row['constant'] == 1:
                con_col.append(row['key'])
            else:
                noncon_col.append(row['key'])
                noncon_dict.update({row['key']: []})

        # get the hystresis values for each simulation, create dataframe
        # df = pd.DataFrame(index = self.get_sim_num(), column = ['id', 'T', 'f'] + noncon_col + )
        hys = []
        f = []
        for idx, row in self.df_parm.iterrows():
            # open the simulation
            s = Simulation(self.jd, self.jn, row['n'])
            # get the hysteresis data
            h = s.parse_hysteresis_work(recalculate, norm = False)
            # append the second to last value
            hys.append(h[-2])
            # append frequency
            f.append(2. * math.pi / row['OT'])
            # append nonconstant value
            for k in list(noncon_dict.keys()):
                noncon_dict[k].append(row[k])

        # for each non-constant column which is not 'OT', plot the frequency data
        df = pd.DataFrame.from_dict(noncon_dict | {'f': f} | {'h': hys})
        for k in noncon_col:
            if k != 'OT':
                # establish save directory if saving
                if not period:
                    xcol = 'f'
                    xaxis = "Cyclic Frequency ($Hz, 2 \\pi \\cdot T^{{-1}}$)"
                else:
                    xcol = 'OT'
                    xaxis = "Cyclic Period ($seoncds, 2 \\pi f$)"
                if save:
                    savedir = "{0}/{1}/results/{2}/".format(self.jd, self.jn, k)
                else:
                    savedir = None
                if k == 'tau':
                    k_str = '\\tau'
                elif k == 'gamma':
                    k_str = '\\gamma'
                else:
                    k_str = k
                # return scale (df, k, fit = fit, save_to = savedir)
                fig = Figure()
                fig.load_data(df, xcol = xcol, ycol = 'h', icol = k)
                fig.add_format("${0}$ ".format(k_str) + "= {:.1e}")
                fig.set_xaxis_label(xaxis)
                fig.set_yaxis_label("Energy Dissipated (J)")
                fig.set_xaxis_scale(log = True)
                # fig.set_yaxis_scale(log = True)
                if save:
                    fig.set_saveas(savedir = savedir, filename = 'sweep')
                gen_plot(fig, show = show, save = save)
                # find the maximum for each hysteresis curve
                n = 0
                df_scale = pd.DataFrame(columns = [k, 'T', 'A'])
                for i in df[k].unique():
                    # get the data set corresponding to the parameter
                    df_temp = df[df[k] == i].reset_index()
                    # find the maximum amplitude and the corresponding period
                    # here, is there a better way to identify the maximum (with curve fitting)
                    mx_idx = df_temp.index[df_temp['h'] == df_temp['h'].max()].to_list()
                    # if the max index is the first or the last
                    if (mx_idx[0] == 0) or (mx_idx[0] == len(df_temp)): continue
                    # append to the data frame and accumulate the next value
                    df_scale.loc[n] = [i, df_temp.iloc[mx_idx[0]][xcol], df_temp.iloc[mx_idx[0]]['h'] ]
                    n = n+1
                # establish axis string describing the parameter
                df_key = self.df_config.loc[self.df_config['key'] == k].reset_index()
                if k == 'k':
                    xax_str = "$k$ ($MPa$)"
                elif k == 'gamma':
                    xax_str = "$\\gamma_{{1}}$"
                elif k == 'tau':
                    xax_str = "$\\tau_{{1}}$ ($s$)"
                else:
                    xax_str = "{1} (${0}$)".format(df_key.iloc[0]['description'].replace('_', ' ').title(), df_key.iloc[0]['units'])
                print(xax_str)
                if not period:
                    yax_str_time = "Resontant Cyclic Frequency ($Hz, 2 \\pi \\cdot T^{{-1}}$)"
                else:
                    yax_str_time = "Resontant Cyclic Period ($seconds, 2 \\pi f$)"
                # plot the resonant period against the model parameter
                if fit:
                    fit_power = fit_line(x = df_scale[k].to_list(), y = df_scale['T'].to_list(), log = True)
                    fit_parms = fit_power.get_parameters()
                    if not period:
                        fit_power.set_label("${0} \\propto f^{{{1:.02f}}}$".format(k_str, fit_parms[0]))
                    else:
                        fit_power.set_label("${0} \\propto T^{{{1:.02f}}}$".format(k_str, fit_parms[0]))
                    fit_power.set_linecolor("k")
                    fit_power.set_linestyle(":")
                else:
                    fit_power = None
                fig = Figure()
                fig.load_data(df_scale, xcol = k, ycol = 'T')
                fig.set_xaxis_label(xax_str)
                fig.set_yaxis_label(yax_str_time)
                fig.set_xaxis_scale(log = True)
                fig.set_yaxis_scale(log = True)
                if save:
                    fig.set_saveas(savedir = savedir, filename = 'Tv{0}'.format(k))
                gen_plot(fig, linewidth = 0, markersize = 8, show = show, save = save, fit = fit_power)
                # plot the resonant amplitude against the model parameter
                if fit:
                    fit_power = fit_line(x = df_scale[k].to_list(), y = df_scale['A'].to_list(), log = True)
                    fit_parms = fit_power.get_parameters()
                    fit_power.set_label("${0} \\propto A^{{{1:.02f}}}$".format(k_str, fit_parms[0]))
                    fit_power.set_linecolor("k")
                    fit_power.set_linestyle(":")
                else:
                    fit_power = None
                fig = Figure()
                fig.load_data(df_scale, xcol = k, ycol = 'A')
                fig.set_xaxis_label(xax_str)
                fig.set_yaxis_label('Resontant Amplitude ($J$)')
                fig.set_xaxis_scale(log = True)
                fig.set_yaxis_scale(log = True)
                if save:
                    fig.set_saveas(savedir = savedir, filename = 'Av{0}'.format(k))
                gen_plot(fig, linewidth = 0, markersize = 8, show = show, save = save, fit = fit_power)

        # plot non-constant parameters against frequency
        pass

    def viscoelastic_normalization (self, norm_dict = viscoelastic_normalization_dict, period = False, recalculate = False, show = True, save = False):
        """ normalize a series of frequency sweeps by the assumed scaling parameters for viscoelasticity.

        Parameters:
        -----------
        norm_dict : Dict[int] (default is 'viscoelastic_normalization_dict')
            contains the assumed scaling parameters.
        period : bool (default is 'False')
            determines if scaling occuers with respect to period or frequency
        recalculate : bool (default is 'False')
            recalculate hysteresis before normalization
        show : bool (default is 'True')
            display normalization plots
        save : bool (default is 'False')
            save normalization plots to 'results' in job dictionary

        Returns:
        --------
        DataFrame
            parameters plus an additional column 'norm' that conatins normalized hysteresis
        """
        # determine constant and non-constant parameters
        noncon_col = []
        noncon_dict = {}
        con_col = []
        for idx, row in self.df_config.iterrows():
            if row['constant'] == 1:
                con_col.append(row['key'])
            else:
                noncon_col.append(row['key'])
                noncon_dict.update({row['key']: []})

        # get the hystresis values for each simulation, create dataframe
        hys = []
        f = []
        for idx, row in self.df_parm.iterrows():
            # open the simulation
            s = Simulation(self.jd, self.jn, row['n'])
            # get the hysteresis data
            h = s.parse_hysteresis_work(recalculate, norm = False)
            # append the second to last value
            hys.append(h[-2])
            # append frequency
            f.append(2. * math.pi / row['OT'])
            # append nonconstant value
            for k in list(noncon_dict.keys()):
                noncon_dict[k].append(row[k])

        ## NORMALIZE
        # determine the normalization values amplitude and timeseries data
        A_norm = 1.
        T_norm = 1.
        f_norm = 1.

        ## TODO use latex for keys when possible
        ## TODO add constants to scaling when possible
        A_norm_base = 1.
        T_norm_base = 1.
        f_norm_base = 1.
        for k in con_col:
            if k in list(norm_dict.keys()):
                # get the constant value
                val = self.get_simulation(1).get_key_value(k)
                # append the constant value to the normalization values
                A_norm_base = A_norm * pow(val,  norm_dict[k][0])
                T_norm_base = T_norm * pow(val,  norm_dict[k][1])
                f_norm_base = f_norm * pow(val, -norm_dict[k][1])

        # normalize the amplitude and time-series data
        df = pd.DataFrame.from_dict(noncon_dict | {'f': f} | {'h': hys})
        df_norm = pd.DataFrame(columns = list(df.columns.values))
        for index, row in df.iterrows():
            row_norm = [] # new row for df_norm
            # initial normalization values
            A_norm = A_norm_base
            T_norm = T_norm_base
            f_norm = f_norm_base
            for c in list(df.columns.values):
                # the order of the columns in the dictionary should be parameters, then properties
                if c in list(norm_dict.keys()):
                    A_norm = A_norm * pow(row[c],  norm_dict[c][0])
                    T_norm = T_norm * pow(row[c],  norm_dict[c][1])
                    f_norm = f_norm * pow(row[c], -norm_dict[c][1])
                    row_norm.append(row[c])
                elif c == 'OT':
                    row_norm.append(row['OT'] / T_norm)
                elif c == 'f':
                    row_norm.append(row['f'] / f_norm)
                elif c == 'h':
                    row_norm.append(row['h'] / A_norm)
                else:
                    row_norm.append(row[c])
            # add to df_norm
            df_norm.loc[index] = row_norm

        ## PLOT
        # normalization strings are used to indicated the normalization in the figure axes
        A_norm_str = ""
        f_norm_str = ""
        T_norm_str = ""
        for c in (list(df.columns.values) + con_col):
            if c in list(norm_dict.keys()):
                ## NOTE :: r helps regularize strings, avoids parsing issue
                c_str = c
                if c_str == "gamma": c_str = "\\gamma"
                if c_str == "tau": c_str = "\\tau"
                if norm_dict[c][0] != 0:
                    A_norm_str += r"{0}".format(c_str) + r"^{{" + r"{0}".format(norm_dict[c][0]) + r"}}"
                if norm_dict[c][1] != 0:
                    T_norm_str += r"{0}".format(c_str) + r"^{{" + r"{0}".format(norm_dict[c][1]) + r"}}"
                    f_norm_str += r"{0}".format(c_str) + r"^{{" + r"{0}".format(-norm_dict[c][1]) + r"}}"

        # set subtitle
        subtitle = ""
        # loop through constant columns,
        for c in con_col:
            # if any exist in the normalization dictionary
            if c in list(norm_dict.keys()):
                if subtitle: # here, empty strings are equivalent to boolean False
                    subtitle += ", "
                # get the constant value
                val = self.get_simulation(1).get_key_value(c)
                c_str = c
                if c_str == "gamma": c_str = "$\\gamma$"
                if c_str == "tau": c_str = "$\\tau$"
                subtitle += "{0} = {1:.1e}".format(c_str, val)

        # loop through non-constant columns, plot
        for k in noncon_col:
            if k != 'OT':
                # plot, return to user
                fig = Figure()
                ycol = "Normalized Energy Loss (J, $W^{{*}} =  W \\cdot " + A_norm_str + "$)"
                if period:
                    xcol = 'OT'
                    xcol_label = "Normalized Oscillation Period (s, $T^{{*}} = T \\cdot " + T_norm_str + "$)"
                else:
                    xcol = 'f'
                    xcol_label = "Normalized Oscilation Frequency (Hz, $f^{{*}} = f \\cdot " + f_norm_str + "$)"
                fig.append_df(df_norm, xcol = xcol, ycol = 'h', icol = k)
                fig.set_axis_label('x', l = xcol_label)
                fig.set_axis_label('y', l = ycol)
                fig.set_axis_scale('x', log = True)
                # fig.set_axis_scale('y', log = True)
                fig.set_subtitle_label(subtitle)
                k_str = k
                if k_str == "gamma": k_str = "$\\gamma$"
                if k_str == "tau": k_str = "$\\tau$"
                fig.add_format("{0}".format(k_str) + " = {:.1e}")
                if save:
                    fig.set_saveas(savedir = "{0}/{1}/results/".format(self.jd, self.jn), filename = "norm-{0}".format(k))
                    fig.save_data()
                gen_plot(fig, show = show, save = save)

## ARGUMENTS
# none

## SCRIPT
# none
