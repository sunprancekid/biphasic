
## Matthew A. Dorsey
## @mad-mpikg
## 2025.12.11
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institute for Colloids and Interfacial Sciences

## FILENAME: programs/python/febio/plotfile.py
## PURPOSE: contains classes to extract data from '.xplt' simulation files
## VERSION: python 3.10

## MODULES
# native / conda
import sys, os
import pandas as pd
# local
from fbs import post

## PARAMETERS
# dictionary which relates tensor component to MAT3DS data structure
TENS_COMP_DICT = {
    'EFFECTIVE': post.MAT3DS.EFFECTIVE,
    'XX': post.MAT3DS.XX,
    'YY': post.MAT3DS.YY,
    'ZZ': post.MAT3DS.ZZ}

## METHODS
# none

## CLASSES
# handles data extraction from xplt files
class XPLT (object):

    """ Used to parse information from febio 'xplt' files via fbs module.

    Attributes
    ----------
    postModel : postModel
        fbs postModel object
    manager : DataManager
        fbs data manager, stores the attributes (name and type) of the different data fields.
    s : int
        number of states in post model
    f : list(str)
        list of strings corresponding to fields contained within post model

    Methods
    -------
    None


    """

    def __init__ (self, filename):
        # check that the file exists
        if not os.path.exists(filename):
            print("ERROR :: XPLT :: '{0}' does not exist or cannot be found.".format(filename))
        # use the xplt file to initialize the data manager and post model
        self.post = post.ReadPlotFile(filename)
        self.manager = self.post.GetDataManager()
        self.set_states()
        # self.e = self.get_elements() # TODO parse number of elements from 0th state
        self.set_fields()

    ## STATES ##

    def set_states (self):
        """ initialize the number of states in the post model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.s = self.post.States()

    ## FIELDS ##

    def set_fields(self):
        """ initialize fields in post model.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.f = []
        for i in range(self.manager.DataFields()):
            f = self.manager.DataField(i)
            self.f.append(f.name)

    def get_fields (self):
        """ returns fields stored in

        Parameters
        ----------
        None

        Returns
        -------
        list(str)
            list of string object describing each field
        """
        return self.f

    def has_field(self, field):
        """ checks if xplt file contains a certain data field.

        Parameters
        ----------
        field : str
            string representation of field to check for

        Returns
        -------
        bool
            True if xplt file contains field, else false

        """

        # check if field is in data manager
        return field in self.f

    def get_field_values (self, field, tensor_component = 'EFFECTIVE', state = None, element = None):
        """ get field values corresponding to element(s) at specified state(s).

        Parameters
        ----------
        field : str
            string representation of field
        tensor_component : str
            (optional) used to select MAT3DS via TENS_COMP_DICT, default is 'EFFECTIVE'
        state : int or list(int)
            (optional) integer(s) specifying state(s) to get field values
        element : int or list(int)
            (optional) integer(s) specifying elements(s) in post model

        Returns
        -------
        DataFrame
            contains information pertaining to specified states and elements
        """

        # check 'field'
        if not self.has_field(field):
            print("ERROR :: XPLT.get_field_values() :: '{0}' is not a field in post model.".format(field))
            return

        # check 'tensor_component'
        if tensor_component not in TENS_COMP_DICT.keys():
            print("ERROR :: XPLT.get_field_values() :: '{0}' is not a valid tensor component.".format(tensor_component))

        # check 'state'
        if state is None:
            # if state is not specified, return all states
            state = range(0, self.s)
        elif not isinstance(state, list) and isinstance(state, int):
            # if state is not a list and is a integer
            if state >= self.s or state < 0:
                # state provided to method does not exist in post model
                print("ERROR :: XPLT.get_field_values() :: 'state' number {0} does not exist in model.".format(state))
                return
            else:
                # turn state into a list
                state = [state] # turn state into a list
        elif isinstance(state, list):
            # if state is a list, check each state is an integer within the accepted list
            for i,s in reversed(list(enumerate(state))): # transverse list in reverse order
                if not isinstance(s, int) or s >= self.s or s < 0:
                    print("ERROR :: XPLT.get_field_values() :: state number {0} in list does not exist in post model, removing.".format(state.pop(i)))
            # check that the list is non-zero
            if len(state) <= 0:
                print("ERROR :: XPLT.get_field_values() :: 'state' list is empty.")
        else:
            # state is not accepted type
            print("ERROR :: XPLT.get_field_values() :: 'state' must be int or list of integers.")
            return

        # check 'element'
        if element is None:
            # TODO :: if element is none, return for all elements
            print("ERROR :: XPLT.get_field_values() :: 'element' cannot be 'None' type.")
            return
        elif not isinstance(element, list) and isinstance(element, int):
            # if element is not a list and is an integer
            # TODO :: check element against list of elements stored in object
            if element <= 0:
                # element provided to method does not exist in post model
                print("ERROR :: XPLT.get_field_values() :: 'element' number {0} does not exist in model.".format(element))
                return
            else:
                # format element as list
                element = [element]
        elif isinstance(element, list):
            # element is a list
            # check whether each element within the list is accepted
            for i, e in reversed(list(enumerate(element))):
                if not isinstance(e, int) or e <= 0:
                    print("ERROR :: XPLT.get_field_values() :: 'element' {0} at index {1} not accepted type, removing from list.".format(element.pop(i), i))
            # check that the element list is greater than 0
            if len(element) == 0:
                print("ERROR :: XPLT.get_field_values() :: 'element' list is empty.")
                return
        else:
            # element is not the accepted type
            print("ERROR :: XPLT.get_field_values() :: 'element' must be 'int' or 'int' list.")
            return

        # initialize pandas data frame
        df = pd.DataFrame(columns = (['state', 'time'] + element))

        # loop through states
        dataField = self.post.GetDataField(field)
        for i in range(len(state)):
            # intitialize the row, with the state number
            row = [state[i]]
            # get the time corresponding to the state
            row.append(self.post.State(state[i]).time)
            # evalue model at state
            fieldState = self.post.Evaluate(dataField, TENS_COMP_DICT[tensor_component], state[i])
            # loop through elements
            for j in range(len(element)):
                # parse field data corresponding to element at specified state, append to df row
                row.append(fieldState.elemData[element[j]].val)
            # add the row to the data frame
            df.loc[i] = row

        # return the dataframe
        return df

## ARGUMENTS
# none

## SCRIPT
# none
