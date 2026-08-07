
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institute for Colloids and Interfacial Sciences
## 2026.05.07

## FILENAME: programs/python/febio/optimization.py
## PURPOSE: handles sets of jobs in which one or more parameters are optimized

## MODULES
# native / conda
import sys, os
import math
import pandas as pd
import numpy as np
# local
from febio.io.logfile import extract_febio_opt as opt_io
from febio.job import Job
from febio.feb.optimization_file import OptimizationFile as OptFile
from febio.feb.model_file import ModelFile as ModFile
from plot.figure import Figure # used for generating plots
from plot.plot import gen_plot

## PARAMETERS
# format for directoy containing files
job_directory_format = "{0}{1}/"
# format of config file
config_file_format = "{0}{1}.config.csv"
# format of parameter file
parameter_file_format = "{0}{1}.parm.csv"
# format of summary file name
summary_file_format = "{0}{1}.sum.csv"
# header used for config files
config_header = ['key', 'xml', 'description', 'units', 'constant', 'related', 'symbolic', 'val', 'min_val', 'max_val', 'n_val', 'log']
# header used for summary file
summary_header = ['n', 'id']

## METHODS

## CLASSES
class Optimization (object):
    """ handles sets of jobs in which one or more parameters are being optimized.

    ## TODO display optimization results.
    ## TODO initialize simulation with job parameters AND optimized parameters.

    Attributes:
    -----------
    get_job_id():
    get_summary_file_format():
    has_summary():
    get_summary():
    get_config_file_format():
    has_config():
    load_config():
    get_parameter_file_format():
    has_parameters():
    load_parameters():

    Methods:
    --------
    None
    """

    def __init__ (self, jd, jn):
        """ initialize optimization object.

        Arguments:
        ----------
        jd : str
            path to job directory
        jn : str
            job name, used to store config and parameter files in job directory.

        Returns:
        --------
        Optimization
            initialized optimization object.
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

    def get_optimization_results(self, save = False, overwrite = False):
        """ for each simulation in the job set, parse the optimization results.

        the results are returned as a dataframe, and saved to the job directory.
        if the optimization job failed, the results corresponding to the results 
        are filled with 'nan' to signify the optimized results to no exists
        in that case.

        Arguments:
        ----------
        save : bool (optional, default is 'False')
            saves the optimization results to the job directory as a csv file.
        overwrite : bool (optional, default is 'True')
            if 'True', overwrites the summary file and recalculates results

        Returns:
        --------
        DataFrame
            contains results of optimization from each job set.
        """
        self.df_sum = None
        # check if the summary file already exists
        if (not overwrite) and os.path.exists(self.get_summary_file_format()):
            self.df_sum = pd.read_csv(self.get_summary_file_format())
        else:
            for idx, row in self.df_parm.iterrows():
                # attempt to parse the results and save them as csv
                opt_dir = "{0}{1}/{2}".format(self.jd, self.jn, row['path'])
                success = True # assume the results exists
                if not os.path.exists(opt_dir + 'febio4.opt.csv'):
                    # if the results do not exist, attempt to parse them
                    success = opt_io(d = "{0}{1}/{2}/".format(self.jd, self.jn, row['path']), f = 'febio4.opt.out')

                if success: # if the simulation results file exists
                    ## get the final optimized values from the summary file
                    # append the optimization results to the summary data frame
                    df_opt_res = pd.read_csv(opt_dir + 'febio4.opt.csv')
                    # check if the summary file has already been initialized
                    if self.df_sum is None:
                        # the summary dataframe has not been initialized yet
                        self.df_sum = self.df_parm.copy(deep = True)
                        # if results have period value, calculate frequency
                        if 'OT' in list(self.df_sum.columns.values):
                            self.df_sum['f'] = [2 * math.pi / v for v in self.df_sum['OT'].to_list()]
                        # the optimization column header to the results dataframe
                        for j in list(df_opt_res.columns.values)[1:]:
                            self.df_sum[j] = [np.nan for k in range(len(self.df_sum))]

                    for j in list(df_opt_res.columns.values)[1:]:
                        self.df_sum.loc[idx, j] = df_opt_res.loc[len(df_opt_res) - 1, j]
                else:
                    # if the results do not exist for the simulation, skip
                    continue
            if save:
                self.df_sum.to_csv("{0}{1}/{1}.sum.csv".format(self.jd, self.jn), index = False)

        return self.df_sum

    def show_optimization_results (self, xaxis_key = None, yaxis_key = None, show = True, save = False):
        """ plots optimized parameters.
        
        Arguments:
        ----------
        xaxis_key : str (optional, default is 'n')
        yaxis_key : str or List[str] (optional, default is 'all')
        show : bool
        save : bool

        Returns:
        --------
        List[Figure]
            each optimization parameter as Figure object.
        """
        # get the optimization results
        df = self.get_optimization_results()

        # check the xaxis keey
        if xaxis_key is None:
            xaxis_key = 'n'
        else:
            # check that the xaxis exists in the column list
            if xaxis_key not in list(df.columns.values):
                # the xaxis key must exiss in the optimization results table
                print("ERROR :: Optimization.show_optimization_results() :: 'xaxis_key'({0}) does not exist in optimization results ({1}/opt.sum.csv).".format(xaxis_key, "{0}{1}".format(self.jd, self.jn)))
                return

        # check the yaxis key
        # convert string to list preimpltively
        if isinstance(yaxis_key, str): yaxis_key = [yaxis_key]
        # check yaxis keys based on type
        if yaxis_key is None:
            # if no keys were specified, do for all keys
            yaxis_key = []
            # loop through each column in the results file
            for i in list(df.columns.values):
                # if the header does not exist in the parameter file
                # it is a result from the optimization process
                if i not in list(self.df_parm.columns.values):
                    # add it to the list of yaxis_keys
                    yaxis_key.append(i)
        elif isinstance(yaxis_key, list):
            # check each item in the list for it's type
            # traverse the list in reverse order
            for i in range(len(yaxis_key) - 1, -1, -1):
                # check that the key specified does not exist in optimization job parameters
                if y in list(self.df_parm.columns.values):
                    # the yaxis key is not an optimizable parameter
                    print("ERROR :: Optimization.show_optimization_results() :: 'yaxis_key' ({0}) is not a result of the optimization process, and cannot be specified as a dependent variable when plotting.".format(yaxis_key.pop(i)))
                # check that the specified key exists in the results file
                if (yaxis_key[i] not in list(df.columns.values)) or ((yaxis_key[i] + '_opt') not in list(df.columns.values)):
                    # the string does not match any of the columns in the results file
                    print("ERROR :: Optimization.show_optimization_results() :: 'yaxis_key' ({0}) does not exist in the optimization process.".format(yaxis_key.pop(i)))

            # check that the length of the list is still greater than one
            if (len(yaxis_key) == 0):
                print("ERROR :: Optimization.show_optimization_results() :: all elements were removed from method argument 'yaxis_key'. Unable to continue.")
                return
        else:
            # the key does not match the specified data type
            print("ERROR :: Optimization.show_optimization_results() :: method argument 'yaxis_key' ({0}) should be either type 'str' or 'List[str]'.".format(yaxis_key))
            pass

        for y in yaxis_key:
            # create figure, add data
            fig = Figure()
            fig.append_df (df = df, xcol = xaxis_key, ycol = y)
            # set axis labels
            fig.set_axis_label (akey = 'x', l = xaxis_key)
            fig.set_axis_label (akey = 'y', l = y)
            fig.set_axis_scale (akey = 'x', log = True)
            fig.set_axis_scale (akey = 'y', log = True)
            # set save location
            if save:
                fig.set_saveas(savedir = '{0}{1}/results/'.format(self.jd, self.jn), filename = y)
                fig.save_data()
            gen_plot (fig, show = show, save = save)

    def generate_optimized_model (self, m, n):
        """ creates optimized model file from the results of an optimization job.

        if optimization results do not exist for the specified job ('n'), the
        method returns 'None'.

        Arguments:
        ----------
        n : int
            integer corresponding to specific optimization job
        m : str (optional, if unspecified, model stored with job is used)
            path to model that optimization parameters should be added to

        Returns:
        --------
        Model
            job which includes optimized value from specific optimization set
        """
        # get the base model from the job directory
        if m is None:
            # replace m with the job stored in the file
            m = "{0}{1}/{1}.feb".format(self.jd, self.jn)
        # check if the model exists
        if os.path.exists(m):
            m = ModFile(m)
        else:
            # path does not exist
            print("ERROR :: Optimization.generate_optimized_model() :: path to model file '{0}' does not exist or cannot be found. specify path to model 'm' as type str in method argument.".format(m))

        # check that n exists
        if (n < 1) or (n > self.df_parm['n'].max()):
            # the integer specified is outside of the allowable range
            print("ERROR :: Optimization.generate_optimized_model() :: method argument n '{0}' is outside the allowable range for this optimization job.".format(n))

        # generate model with job parameters
        j = Job(self.jd, self.jn)
        m = j.parameterize_model(m = m, n = n)

        # get the optimization results, add them to the model
        of = OptFile("{0}{1}/{2}{1}-{3}.opt".format(self.jd, self.jn, self.df_parm['path'][n - 1], n))
        for index, row in of.get_parameters().iterrows(): # gets the parameters and paths for each optimizable value
            # add the optimized value to appropriate field in the model
            val = self.df_sum[row['key'] + "_opt"][n - 1]
            if np.isnan(val): return None # row contains nan types, optimization was unsuccessful
            m.update_element_value(elm_path = row['path'], value = self.df_sum[row['key'] + "_opt"][n - 1])

        # return the model to the user
        return m

    ## ITERATIONS

    def get_iterations_single (self, n):
        """ returns the results of a single optimization process.

        Arguments:
        ----------
        n : int
            integer associated with single optimization process within job.

        Returns:
        --------
        DataFrame
            contains each iteration of optimization
        """
        # check that job parameters exist
        if not self.has_parameters():
            # the optimization job does not have any parameters
            # job does not exists
            print("ERROR :: Optimization.get_iterations_single() :: parameters for job '{0}' in directory '{1}' cannot be found.".format(self.jn, self.jd))
            return

        # check that n exists within job
        if n not in self.df_parm['n'].to_list():
            # n does not exist within the job
            print("ERROR :: Optimization.get_iterations_single() :: optimization job number '{0}' does not exist in the job set.".format(n))
            return

        # check that the results exist within the simulation directory
        opt_csv_file = "{0}{1}/{2}febio4.opt.csv".format(self.jd, self.jn, self.df_parm.iloc[n]["path"])
        if not os.path.exists(opt_csv_file):
            # if the optimization file does not exist within the simulation directory,
            # attempt to parse if from the job file (if it exists)
            opt_out_file = "{0}{1}/{2}febio4.opt.out".format(self.jd, self.jn, self.df_parm.iloc[n]["path"])
            if not os.path.exists(opt_out_file):
                # unable to parse results
                print("ERROR :: Optimization.get_iterations_single() :: unable to parse optimization results, 'febio4.opt.out' does not exist in simulation directory ('{0}{1}/{2}').".format(self.jd, self.jn, self.df_parm.iloc[n]["path"]))
                return
            else:
                # parse the optimization file
                success = opt_io(d = "{0}{1}/{2}".format(self.jd, self.jn, self.df_parm.iloc[n]["path"]), f = 'febio4.opt.out')
                print(success)

        # open the opimization file as a data frame, return
        return pd.read_csv(opt_csv_file)

    ## JOBID

    def get_jobid (self):
        """ returns the job path.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            path to job directory used to load optimization results.
        """
        return job_directory_format.format(self.jd, self.jn)

    ## SUMMARY ## 

    def get_summary_file_format (self):
        """ returns the formatted path to the summary file.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            path to the simulation summary file.
        """
        return summary_file_format.format(self.jd, self.jn)

    def has_summary (self):
        """ checks if summary file exists within the simulation directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        return path.os.exists(self.get_summary_file_format())

    def get_summary (self):
        """ return summary of optimization simulations.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        return self.df_sum

    ## CONFIG ##

    def get_config_file_format (self):
        """ returns formatted path to config file.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            path to the simulation config file.
        """
        return config_file_format.format(self.get_jobid(), self.jn)

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
        return (os.path.exists(self.get_config_file_format()))

    def load_config (self):
        """ load config file into Job from simulation directory.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.df_config = pd.read_csv(config_file_format.format(self.get_jobid(), self.jn))
        # check if the config file has all of the headers
        for h in config_header:
            # if the column is not in config file header already
            if h not in list(self.df_config.columns):
                # append an empty list to the column
                self.df_config[h] = ['na' for i in range(len(self.df_config.index))]
                ## TODO :: there is an option to get the information pertaining to each key from the parm file for config files that already exist and use an older version ...

    ## PARAMETERS ##

    def get_parameter_file_format (self):
        """ returns formatted path to config file.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            path to the simulation parameter file.
        """
        return parameter_file_format.format(self.get_jobid(), self.jn)

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
        return (os.path.exists(self.get_parameter_file_format()))

    def load_parameters (self):
        """ loads the parameter file, if it exists.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.df_parm = pd.read_csv(self.get_parameter_file_format())

## ARGUMENTS
# none

## SCRIPT
# none
