
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

# dictonary of additional properties that can be calculated
ADD_PROP_DICT = {
    'total stress': ['fluid pressure', 'solid stress']}

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
    e : int
        number of elements in post model
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
        self.set_elements()
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

    def get_states (self):
        """ returns a list of all states in post model.

        Parameters
        ----------
        None

        Returns
        -------
        List[int]
            integer list of all possible states in post model.
        """
        return list(range(0, self.s))

    def get_state_at_time (self, time = None):
        """ returns state that closest matches time.

        Parameters
        ----------
        time : float
            real number greater than zero

        Returns
        -------
        int
            integer that corresponds to desired state
        """
        # get all time and states points in post model
        init = self.get_field_values('initial position', element = 1)
        state_list = init['state'].tolist()
        time_list = init['time'].tolist()
        # find the state that is closest to the time passed to the method
        idx_time = 0
        err_time = []
        for i in range(1, len(time_list)):
            # print("{0} : ({1} - {2} = {3})".format(i, time_list[i], time, time_list[i] - time))
            if abs(time_list[i] - time) < abs(time_list[idx_time] - time):
                # if the current time is closer than the previous, update the index
                idx_time = i
            else:
                # time is linear. if the index is not being update,
                # the desired time point has been found
                break
        # print("Time {0} corresponds to state {1} when simulation time is {2}.".format(time, state_list[idx_time], time_list[idx_time]))
        return int(state_list[idx_time])

    def get_states_from_time_period (self, min_time = None, max_time = None):
        """ returns a list of states that correspond to a time period within the post model.

        Parameters
        ----------
        min_time : float
            (Optional) real number greater than or equal to zero
        max_time : float
            (Optional) real number less than or equal to the maximum time
        Returns
        -------
        List[int]
            integer list of all states in post model which match the time constraints.
        """
        pass

    ## ELEMENTS ##

    def set_elements (self):
        """ initialize the number of elements in the post model.

        Parameters
        ----------
        None

        Returns
        -------

        """
        # get the element data from the first state
        self.e = len(self.post.Evaluate(self.post.GetDataField('initial position'), TENS_COMP_DICT['EFFECTIVE'], 0).elemData) - 1

    def get_elements (self):
        """ returns a list of all possible elements in post model.

        Parameters
        ----------
        None

        Returns
        -------
        List[int]
            integer list of all possible elements in model
        """
        return list(range(1, self.e + 1))

    def get_elements_from_initial_position (self, x = None, y = None, z = None):
        """ returns elements that match a described initial position.

        Parameters
        ----------
        x : float
            x-coordinate
        y : float
            y-coordinate
        z : float
            z-coordinate

        Returns
        -------
        List[int]
            integer last of elements whose initial position match the coordinates
        """
        pass

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
            string representation of field, must be within self.f
        tensor_component : str
            (optional) used to select MAT3DS via TENS_COMP_DICT, default is 'EFFECTIVE'
        state : int or list(int)
            (optional) integer(s) specifying state(s) to get field values, default is
            all states
        element : int or list(int)
            (optional) integer(s) specifying elements(s) in post model, default is
            all elements

        Returns
        -------
        DataFrame
            contains information pertaining to specified states and elements
        """

        # check 'field'
        add_prop = False
        if field in list(ADD_PROP_DICT.keys()):
            # check if file has the additional properties that need to be calculated for the special property
            for p in (ADD_PROP_DICT[field]):
                if not self.has_field(p):
                    # the post file does not have the field required for the additional property
                    print("ERROR :: XPLT.get_field_values() :: field '{0}' is required to calculate property '{1}', but does not exist in post file.".format(p, field))
                    return
                add_prop = True
        elif not self.has_field(field):
            print("ERROR :: XPLT.get_field_values() :: '{0}' is not a field in post model.".format(field))
            return

        # check 'tensor_component'
        if tensor_component not in TENS_COMP_DICT.keys():
            print("ERROR :: XPLT.get_field_values() :: '{0}' is not a valid tensor component.".format(tensor_component))

        # check 'state'
        if state is None:
            # if state is not specified, return all states
            state = self.get_states()
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
            element = self.get_elements()
        elif not isinstance(element, list) and isinstance(element, int):
            # if element is not a list and is an integer
            if element <= 0 or element > self.e:
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
                if not isinstance(e, int) or e <= 0 or e > self.e:
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

        # get fields from post
        dataFields = []
        if not add_prop:
            dataFields.append(self.post.GetDataField(field))
        else:
            # additional property is true
            for f in ADD_PROP_DICT[field]:
                dataFields.append(self.post.GetDataField(f))

        # loop through states
        for i in range(len(state)):
            # intitialize the row, with the state number
            row = [state[i]]
            # get the time corresponding to the state
            row.append(self.post.State(state[i]).time)
            # loop through elements
            for j in range(len(element)):
                elm_val = 0
                # evalue model at state for each datafield
                for k in range(len(dataFields)):
                    # get the values for field k at state i
                    fieldState = self.post.Evaluate(dataFields[k], TENS_COMP_DICT[tensor_component], state[i])
                    # sum the field value at element j
                    elm_val += fieldState.elemData[element[j]].val
                # append, repeat for each element
                row.append(elm_val)
            # add the row to the data frame, repeat for each state
            df.loc[i] = row

        # return the dataframe
        return df

## ARGUMENTS
# none

## SCRIPT
# none
