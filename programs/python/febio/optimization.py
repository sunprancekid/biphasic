
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
import pandas as pd
import numpy as np
# local
from febio.io.logfile import extract_febio_opt as opt_io
from febio.job import Job
from febio.feb.optimization_file import OptimizationFile as OptFile
from febio.feb.model_file import ModelFile as ModFile

## PARAMETERS
# format of config file
config_file_format = "{0}/{1}/{1}.config.csv"
# format of parameter file
parameter_file_format = "{0}/{1}/{1}.parm.csv"
# format of summary file name
summary_file_format = "{0}/{1}/{1}.sum.csv"
# header used for config files
config_header = ['key', 'xml', 'description', 'units', 'constant', 'related', 'symbolic', 'val', 'min_val', 'max_val', 'n_val', 'log']
# header used for summary file
summary_header = ['n', 'id']

## METHODS
# none

## CLASSES
class Optimization (object):
    """ handles sets of jobs in which one or more parameters are being optimized.

    ## TODO display optimization results.
    ## TODO initialize simulation with job parameters AND optimized parameters.

    Attributes:
    -----------
    None

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
        df_sum = None
        # check if the summary file already exists
        if (not overwrite) and os.path.exists(summary_file_format.format(self.jd, self.jn)):
            df_sum = pd.read_csv(summary_file_format.format(self.jd, self.jn))
        else:
            for idx, row in self.df_parm.iterrows():
                # attempt to parse the results and save them as csv
                opt_dir = "{0}{1}/{2}".format(self.jd, self.jn, row['path'])
                print(opt_dir)
                if not os.path.exists(opt_dir + 'febio4.opt.csv'):
                    success = opt_io(d = "{0}{1}/{2}/".format(self.jd, self.jn, row['path']), f = 'febio4.opt.out')
                    print(success)
                    if not success: continue
                # append the optimization results to the summary data frame
                df_opt_res = pd.read_csv(opt_dir + 'febio4.opt.csv')
                if df_sum is None:
                    # the summary dataframe has not been initialized yet
                    df_sum = self.df_parm.copy(deep = True)
                    for j in list(df_opt_res.columns.values)[1:]:
                        df_sum[j] = [np.nan for k in range(len(df_sum))]
                for j in list(df_opt_res.columns.values)[1:]:
                    df_sum.loc[idx, j] = df_opt_res.loc[len(df_opt_res) - 1, j]
            if save:
                df_sum.to_csv("{0}{1}/{1}.sum.csv".format(self.jd, self.jn))

        return df_sum

    def show_optimization_results (self, show = True, save = False):
        """ plots optimized parameters.
        
        Arguments:
        ----------
        show : bool
        save : bool
        xaxis_key : str (optional, default is 'n')
        yaxis_key : str (optional, default is 'all')

        Returns:
        --------
        List[Figure]
            each optimization parameter as Figure object.
        """
        # get the optimization results
        df = self.get_optimization_results()
        # check the xaxis key
        # check the yaxis key
        if yaxis_key is None:
            # if no keys were specified, do for all keys
            # yaxis_key = self.get_optimization_parameters()
            pass
        elif isinstance(yaxis_key, str):
            # check that the key that was specified exists in optimization job
            pass
        elif isinstance(yaxis_key, list):
            # check that each key in the list exists in the optimization job
            pass
        else:
            # the key does not match the specified data type
            pass

        for y in yaxis_key:
            # create figure
            fig = Figure()
            # 
            pass 

    def generate_optimized_model (self, m, n):
        """ creates optimized model file from the results of an optimization job.

        Arguments:
        ----------
        n : int
            integer corresponding to specific optimization job
        m : str (optional, if unspecified, model stored with job is used)
            path to model that optimization parameters should be added to

        Returns:
        --------
        Model
            job which includes specific job para
            # print(m.tree_has_element(row['path']))
            # m.update_element_value(elm_path = row['path'], value = df_opt[row['key'] + "_opt"][len(df_opt) - 1])
            # print(df_opt[row['key'] + "_opt"][len(df_opt) - 1])
            # print(row['key'])meters and optimal parameters from optimization job
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
        for index, row in of.get_parameters().iterrows():
            # get the parameter optimial parameter from result file
            df_opt = pd.read_csv("{0}{1}/{2}febio4.opt.csv".format(self.jd, self.jn, self.df_parm['path'][n - 1]))

        # return the model to the user
        return m

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

    ## PARAMETERS ##

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

## ARGUMENTS
# none

## SCRIPT
# none
