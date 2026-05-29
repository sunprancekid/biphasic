
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max-Planck-Institute for Colloids and Interfaces
## 2026.05.27

## FILENAME: programs/python/febio/feb/optimization_file.py
## PURPOSE: handle, generate optimization files for febio


## MODULES
# native, conda
import sys, os
import re # used for regular expression checking
import copy
import xml.etree.ElementTree as ET # handles xml formatting
# local
# none

## PARAMTERS
## default values
# default objective tolerance
default_objective_tolerance = 0.00001
# default f_diff_scale value
default_f_diff_scale = 0.01
# default log_level value
default_log_level = "LOG_FILE_AND_SCREEN"
# default print_level value
default_print_level = "PRINT_VERBOSE"


## METHODS
# collects all paths in element tree
def rec_elm_tree (root, abs_path = None, sl = None):
    """ recursively gets paths of all elements in a tree with attributes.

    Arguments:
    ----------
    root : element
        element with sub-elements
    abs_path : str
        absolute path to root
    sl : List[str]
        string list containing paths in root

    Returns:
    --------
    List[str]
        list of strings containing absolute path of all elemnts in tree.
    """
    if abs_path is None:
        abs_path = " "
    if sl is None:
        sl = []
    for child in root:
        # translate child text to string
        cld_txt = str(child.text)
        if "\t" in cld_txt:
            cld_txt = ""
        # translate child attributes to string
        cld_att = str(child.attrib)
        if not child.attrib:
            cld_att = ""
        nxt_path = ""
        if abs_path == " ":
            nxt_path = abs_path + root.tag
        else:
            nxt_path = abs_path + "/" + root.tag
        sl.append(nxt_path + "/" + child.tag + " " + cld_txt + " " + cld_att)
        subelm_list = root.findall(child.tag + "/")
        if not (subelm_list is None or (isinstance(subelm_list, list) and len(subelm_list) == 0)):
            # sl.append(root.tag + "/" + child.tag + " ... (x{0})".format(len(subelm_list)))
            rec_elm_tree(child, abs_path = nxt_path, sl = sl)
    return sl

# checks if path exists in element tree
def tree_has_path (root, elm_path):
    """ determines if xml path exists in root tree.

    Arguments:
    ----------
    root : Element
        contains element tree
    elm_path : str
        xml path to check for in root tree

    Returns:
    --------
    bool
        'True' if element path exists in root, else 'False'
    """
    if elm_path is None:
        return False
    elm = root.findall(elm_path)
    if elm is None or (isinstance(elm, list) and len(elm) == 0):
        return False
    else:
        return True

# add element to tree
def add_element_to_tree(root, elm_path, tag, value = None, attributes = None):
    """ adds element to tree. if the element already exists, properties are replaced.

    Arguments:
    ----------
    root : Element
        element tree which contains sub-elements
    elm_path : str
        element path which exists in root tree, location where new element is stored
    tag : str
        name of new element in element tree
    value : str
        value which is stored in new element
    attributes : dictYou do not need to try/except while you are popping a key which is unavailable. Here is how you can do this.
        attributes associated with element

    Returns:
    --------
    bool
        'True' if addition operation was successful, else 'False'
    """
    # check that element path exists in root
    if not tree_has_path(root, elm_path): return False
    # check that tag does not exist in element path
    if tree_has_path (root, elm_path + "/" + tag):
        # if it does, replace the values and attributes
        for elm in root.findall(elm_path + "/" + tag):
            # replace the value
            if value is not None:
                elm.text = str(value)
            # remove the previous attributes
            if attributes is not None:
                old_attrib = copy.deepcopy(elm.attrib)
                for a in old_attrib:
                    elm.attrib.pop(a)
                # add new attributes
                for a in attributes:
                    elm.set(a, attributes[a])
        return True
    else:
        # if it does not, add new subelement to tree with attributes and values
        # get element at path
        elm = root.find(elm_path)
        # append subelement
        sub = ET.SubElement(elm, tag, attrib = attributes)
        if value is not None:
            sub.text = value
        return True

## CLASSES
# used for handling optimization files
class OptimizationFile (object):
    """ handles, generates optimization files for febio.

    Attributes:
    -----------
    None

    Methods:
    --------
    __init__():
        initialize object
    __str__():
        return string representation of optimization file xml tree
    load_optimization_file():
        load existing file into object

    """

    def __init__ (self, filepath = None):
        """ initialize optimization file.

        if 'filepath' is specified, the optimization file is loaded from
        the existing format. if not, a blanck optimization file is generated.

        Arguments:
        ----------
        filepath : str
            path to existing optimization file

        Returns:
        --------
        None
        """
        if filepath is not None:
            self.load_optimization_file(filepath)
        else:
            self.reset_optimization_file()

    def __str__(self):
        """ return optimization file as string.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            file state as string.
        """
        # get absolute paths for all elements in tree
        l = rec_elm_tree(self.root)
        # convert list of elements to string
        s = ""
        for i in range(len(l)):
            # append element absolute path
            s += l[i]
            # add newline character if not last string
            if i != len(l) - 1: s += "\n"
        # return string
        return s

    def load_optimization_file (self, filepath):
        """ replace object with existing data from file.

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if file was successfully loaded into object, else 'False'.
        """
        # check that the file exists
        if not os.path.exists(filepath):
            print("ERROR :: OptimizationFile.load_optimization_file() :: path '{0}' does not exist, unable to load.".format(filepath))
            return False
        # parse the element tree
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        return True

    def save_optimization_file (self, directory, filename):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def reset_optimization_file (self):
        """ reset all mandatory fields.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # reset options
        # reset parameters
        # reset objective
        pass

    ## PARAMETERS

    def reset_parameters (self):
        """

        Arguments:
        ----------
        None

        Returns:
        -----------
        None
        """
        pass

    def add_parameters (self, name, min_val, max_val, start_val):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def has_parameters (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    ## OPTIONS

    # objective tolerence
    def set_objective_tolerance (self, value, attributes = None):
        """ assigns objective tolerance to optimization value

        Arguments:
        ----------
        value : float
            objective tolerance value (real number greater than 0)
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        # adjust the value
        add_element_to_tree(self.root, "Options", "obj_tol", value = value, attributes = attributes)

    # reset objective tolerance
    def reset_objective_tolerance (self):
        """ assigns default value to objective tolerance.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_objective_tolerance(default_objective_tolerance)

    # set f_diff_scale
    def set_f_diff_scale (self, value, attributes = None):
        """ change fdiff scale value and attributes.

        Arguments:
        ----------
        value : float
            'f_diff_scale' value (real number greater than 0)
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "f_diff_scale", value = value, attributes = attributes)

    # reset f_diff scale
    def reset_f_diff_scale (self):
        """ assign 'f_diff_scale' parameter default value.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_f_diff_scale(default_f_diff_scale)

    # set log_level field
    def set_log_level (self, value, attributes = None):
        """ sets log level to user specified value.

        Arguments:
        ----------
        value : str
            'log_level' value
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "log_level", value = value, attributes = attributes)

    # reset log level field
    def reset_log_level (self):
        """ sets log level field to default value

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_log_level(default_log_level)

    # set print_level field
    def set_print_level (self, value, attributes = None):
        """

        Arguments:
        ----------
        value : str
            'print_level' value
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "print_level", value = value, attributes = attributes)

    # reset print level field
    def reset_print_level (self):
        """ resets print level to default value.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_log_level(default_print_level)

    ## DATA

    def add_data (self, df):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def get_data (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def set_optimization_function (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def get_optimization_function (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """


## ARGUMENTS
# none


## SCRIPT
# none
