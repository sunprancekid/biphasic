
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## 06.02.2026

## FILENAME: programs/python/febio/job.py
## PURPOSE: contains classes and methods for handling febio simulation

## MODULES
# none

## PARAMETERS
# header used for config files
default_config_header = "key, xml, description, units, constant, related, symbolic"

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
        ## if the paths do not exist,
        self.df_config = None
        self.df_parm = None
        self.df_sum = None

    ## has config file

    ## load config file


    ## add parameter

    ## generate parameters with model

## ARGUMENTS
# none

## SCRIPT
# none
