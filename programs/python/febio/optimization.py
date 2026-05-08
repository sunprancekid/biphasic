
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
# local
# none

## PARAMETERS
# format of config file
config_file_format = "{0}/{1}/{1}.config.csv"
# format of parameter file
parameter_file_format = "{0}/{1}/{1}.parm.csv"

## METHODS
# none

## CLASSES
class Optimization (object):
    """ handles sets of jobs in which one or more parameters are being optimized.

    ## TODO get the optimization results from each simulation.
    ## TODO save the results in the job directory.
    ## TODO display optimization results.
    ## TODO initialize simulation with job parameters AND optimized parameters.

    Attributes:
    -----------
    None

    Methods:
    --------
    None
    """

    def __init__ (jd, jn):
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


    def get_optimization_results(self):
        """ for each simulation in the job set, parse the optimization results.

        the results are returned as a dataframe, and saved to the job directory.

        Arguments:
        ----------
        None

        Returns:
        --------
        DataFrame
            contains results of optimization from each job set.
        """
        pass

    def generate_optimized_model (self, m, n):
        """ creates optimized model file from the results of an optimization job.

        Arguments:
        ----------
        m : str
        n : int

        Returns:
        --------
        Model
        """
        pass

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
