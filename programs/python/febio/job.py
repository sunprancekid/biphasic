
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
config_header = ['key', 'xml', 'description', 'units', 'constant', 'related', 'symbolic']

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


    ## add parameter

    ## generate parameters with model

## ARGUMENTS
# none

## SCRIPT
# none
