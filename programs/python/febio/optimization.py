
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
# none

## METHODS
# none

## CLASSES
class Optimization (object):
    """ handles sets of jobs in which one or more parameters are being optimized.

    ## TODO get the optimization results from each simulation.
    ## TODO save the results in the job directory
    ## TODO display optimization results
    ## TODO initialize simulation with job parameters AND optimized parameters

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
        pass


## ARGUMENTS
# none

## SCRIPT
# none
